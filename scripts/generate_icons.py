#!/usr/bin/env python3
"""Generate clean, anti-aliased macOS (.icns) and Windows/Web (.ico) icons for Float.

Zero third-party dependencies: renders supersampled RGBA pixels in pure Python
using signed-distance-field (SDF) geometry and writes PNG, ICNS, and ICO files.
"""

from __future__ import annotations

import math
import struct
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ICNS_OUT = ROOT / "Float.app" / "Contents" / "Resources" / "AppIcon.icns"
ICO_OUT = ROOT / "float.ico"


def _clamp(v: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return lo if v < lo else (hi if v > hi else v)


def _smoothstep(edge0: float, edge1: float, x: float) -> float:
    t = _clamp((x - edge0) / (edge1 - edge0))
    return t * t * (3.0 - 2.0 * t)


def _mix(a: tuple[float, float, float], b: tuple[float, float, float], t: float) -> tuple[float, float, float]:
    return (
        a[0] + (b[0] - a[0]) * t,
        a[1] + (b[1] - a[1]) * t,
        a[2] + (b[2] - a[2]) * t,
    )


def _blend_over(
    dst: tuple[float, float, float, float],
    src_rgb: tuple[float, float, float],
    src_a: float,
) -> tuple[float, float, float, float]:
    if src_a <= 0.0:
        return dst
    sa = _clamp(src_a)
    da = dst[3]
    out_a = sa + da * (1.0 - sa)
    if out_a <= 1e-6:
        return (0.0, 0.0, 0.0, 0.0)
    r = (src_rgb[0] * sa + dst[0] * da * (1.0 - sa)) / out_a
    g = (src_rgb[1] * sa + dst[1] * da * (1.0 - sa)) / out_a
    b = (src_rgb[2] * sa + dst[2] * da * (1.0 - sa)) / out_a
    return (r, g, b, out_a)


def _sd_rounded_box(px: float, py: float, cx: float, cy: float, hx: float, hy: float, r: float) -> float:
    dx = abs(px - cx) - hx + r
    dy = abs(py - cy) - hy + r
    ox = max(dx, 0.0)
    oy = max(dy, 0.0)
    return math.hypot(ox, oy) + min(max(dx, dy), 0.0) - r


def _sd_squircle(px: float, py: float, half: float, power: float = 4.6) -> float:
    """Approximate macOS continuous superellipse (squircle) signed distance."""
    nx = abs(px) / half
    ny = abs(py) / half
    val = (nx ** power + ny ** power) ** (1.0 / power)
    return (val - 1.0) * half


def _sample_icon(u: float, v: float, aa: float, mac_margin: bool = True) -> tuple[int, int, int, int]:
    """Sample normalized coordinates u, v in [-1, 1] and return RGBA bytes."""
    # macOS Big Sur+ icon grid uses ~82% canvas for the squircle so it matches system icons
    half = 0.82 if mac_margin else 0.94
    d_body = _sd_squircle(u, v, half, power=4.6)
    alpha_body = 1.0 - _smoothstep(-aa, aa, d_body)
    if alpha_body <= 0.001:
        return (0, 0, 0, 0)

    # Background gradient: warm obsidian top -> deep charcoal bottom with subtle terracotta radial glow
    t_vert = _clamp((v + half) / (2.0 * half))
    bg_top = (36.0, 34.0, 32.0)
    bg_bot = (17.0, 16.0, 15.0)
    rgb = _mix(bg_top, bg_bot, t_vert)

    # Subtle warm terracotta radial glow in bottom-right
    glow_dist = math.hypot(u - 0.28, v - 0.30)
    glow = math.exp(-glow_dist * glow_dist * 3.2) * 0.28
    rgb = _mix(rgb, (217.0, 119.0, 87.0), glow)

    # Subtle inner top-edge rim highlight for tactile glass-card depth
    rim = (1.0 - _smoothstep(0.0, aa * 3.5, abs(d_body + aa * 1.4))) * _clamp(0.45 - v * 0.6)
    if rim > 0.0:
        rgb = _mix(rgb, (255.0, 250.0, 245.0), rim * 0.28)

    col = (rgb[0], rgb[1], rgb[2], alpha_body)

    # Crisp geometric Float "F" emblem + terracotta speed-ribbon accent
    scale = half / 0.82
    sx = u / scale
    sy = v / scale
    s_aa = aa / scale

    # Vertical stem of 'F'
    d_stem = _sd_rounded_box(sx, sy, -0.20, 0.00, 0.115, 0.42, 0.055)
    # Top bar of 'F'
    d_top = _sd_rounded_box(sx, sy, 0.06, -0.305, 0.34, 0.115, 0.055)
    # Middle bar of 'F'
    d_mid = _sd_rounded_box(sx, sy, 0.00, 0.015, 0.24, 0.105, 0.052)

    d_letter = min(d_stem, d_top, d_mid)
    a_letter = 1.0 - _smoothstep(-s_aa, s_aa, d_letter)
    # Subtle warm alabaster gradient on the 'F'
    letter_rgb = _mix((255.0, 254.0, 250.0), (236.0, 232.0, 222.0), _clamp((sy + 0.42) / 0.84))
    col = _blend_over(col, letter_rgb, a_letter)

    # Terracotta pill/dot accent in bottom-right of the emblem (representing fleet motion / wheel / signal)
    d_dot = _sd_rounded_box(sx, sy, 0.23, 0.305, 0.14, 0.105, 0.105)
    a_dot = 1.0 - _smoothstep(-s_aa, s_aa, d_dot)
    dot_rgb = _mix((232.0, 134.0, 99.0), (204.0, 96.0, 62.0), _clamp((sy - 0.2) / 0.22))
    col = _blend_over(col, dot_rgb, a_dot)

    # Un-premultiply? col is already straight RGB with combined alpha_body outer mask
    final_a = _clamp(col[3]) * alpha_body
    return (
        int(_clamp(col[0] / 255.0) * 255.0 + 0.5),
        int(_clamp(col[1] / 255.0) * 255.0 + 0.5),
        int(_clamp(col[2] / 255.0) * 255.0 + 0.5),
        int(_clamp(final_a) * 255.0 + 0.5),
    )


def render_png(size: int, mac_margin: bool = True) -> bytes:
    """Render an RGBA PNG of ``size x size`` pixels with 2x2 supersampling."""
    aa = 2.2 / size
    raw_rows = bytearray()
    sub_offsets = (-0.25, 0.25)
    for y in range(size):
        raw_rows.append(0)  # PNG filter type 0 (None)
        for x in range(size):
            r_sum = g_sum = b_sum = a_sum = 0
            for oy in sub_offsets:
                v = ((y + 0.5 + oy) / size) * 2.0 - 1.0
                for ox in sub_offsets:
                    u = ((x + 0.5 + ox) / size) * 2.0 - 1.0
                    r, g, b, a = _sample_icon(u, v, aa, mac_margin=mac_margin)
                    r_sum += r * a
                    g_sum += g * a
                    b_sum += b * a
                    a_sum += a
            a_avg = a_sum / 4.0
            if a_avg > 0.5:
                r_out = int(min(255, round(r_sum / a_sum)))
                g_out = int(min(255, round(g_sum / a_sum)))
                b_out = int(min(255, round(b_sum / a_sum)))
                a_out = int(min(255, round(a_avg)))
            else:
                r_out = g_out = b_out = a_out = 0
            raw_rows.extend((r_out, g_out, b_out, a_out))

    def _chunk(tag: bytes, payload: bytes) -> bytes:
        crc = zlib.crc32(tag + payload) & 0xFFFFFFFF
        return struct.pack(">I", len(payload)) + tag + payload + struct.pack(">I", crc)

    ihdr = struct.pack(">IIBBBBB", size, size, 8, 6, 0, 0, 0)
    idat = zlib.compress(bytes(raw_rows), level=9)
    return b"\x89PNG\r\n\x1a\n" + _chunk(b"IHDR", ihdr) + _chunk(b"IDAT", idat) + _chunk(b"IEND", b"")


def write_icns(path: Path) -> None:
    """Write a complete macOS .icns with standard and Retina @2x PNG chunks."""
    # (chunk_type, pixel_size)
    specs = [
        (b"icp4", 16),
        (b"icp5", 32),
        (b"icp6", 64),
        (b"ic07", 128),
        (b"ic11", 64),   # 32x32@2x
        (b"ic12", 128),  # 64x64@2x
        (b"ic08", 256),
        (b"ic13", 512),  # 256x256@2x
        (b"ic09", 512),
        (b"ic14", 1024), # 512x512@2x
        (b"ic10", 1024),
    ]
    cache: dict[int, bytes] = {}
    chunks = bytearray()
    for tag, px in specs:
        if px not in cache:
            cache[px] = render_png(px, mac_margin=True)
        png = cache[px]
        chunks.extend(tag)
        chunks.extend(struct.pack(">I", 8 + len(png)))
        chunks.extend(png)

    total_len = 8 + len(chunks)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"icns" + struct.pack(">I", total_len) + bytes(chunks))


def write_ico(path: Path) -> None:
    """Write a multi-resolution Windows/Browser .ico using PNG-encoded frames."""
    sizes = [16, 32, 48, 64, 128, 256]
    pngs = [render_png(s, mac_margin=False) for s in sizes]
    header = struct.pack("<HHH", 0, 1, len(sizes))
    offset = 6 + 16 * len(sizes)
    dir_entries = bytearray()
    for s, png in zip(sizes, pngs):
        dim = 0 if s >= 256 else s
        dir_entries.extend(struct.pack("<BBBBHHII", dim, dim, 0, 0, 1, 32, len(png), offset))
        offset += len(png)
    path.write_bytes(header + bytes(dir_entries) + b"".join(pngs))


def main() -> None:
    write_icns(ICNS_OUT)
    write_ico(ICO_OUT)
    print(f"Generated {ICNS_OUT} ({ICNS_OUT.stat().st_size} bytes)")
    print(f"Generated {ICO_OUT} ({ICO_OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    main()

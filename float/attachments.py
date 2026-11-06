"""Turn an uploaded file (base64 from the browser) into plain text for the model.

PDF: uses ``pypdf`` when installed (best for multi-page agreements, policies and invoices); otherwise a
small stdlib reader that handles simple text PDFs. DOCX, XLSX and plain text
use only the standard library.
"""

from __future__ import annotations

import base64
import binascii
import io
import re
import zlib
import zipfile
from typing import Any
from xml.etree import ElementTree

MAX_CHARS = 120_000


class AttachmentError(Exception):
    pass


def _pdf_pypdf(data: bytes) -> str | None:
    try:
        from pypdf import PdfReader
    except ImportError:
        return None
    try:
        reader = PdfReader(io.BytesIO(data))
        if reader.is_encrypted:
            reader.decrypt("")
        return "\n\n".join((page.extract_text() or "") for page in reader.pages)
    except Exception as exc:
        raise AttachmentError(f"That PDF could not be opened ({type(exc).__name__}).") from None


def _unescape(raw: bytes) -> str:
    raw = re.sub(rb"\\([nrtbf()\\])", lambda m: {b"n": b"\n", b"r": b"\r", b"t": b"\t", b"b": b"", b"f": b""}.get(m.group(1), m.group(1)), raw)
    raw = re.sub(rb"\\([0-7]{1,3})", lambda m: bytes([int(m.group(1), 8) & 255]), raw)
    return raw.decode("latin-1")


def _pdf_basic(data: bytes) -> str:
    out: list[str] = []
    for m in re.finditer(rb"stream\r?\n(.*?)\r?\nendstream", data, re.S):
        body = m.group(1)
        try:
            body = zlib.decompress(body)
        except zlib.error:
            pass
        if b"BT" not in body:
            continue
        for block in re.findall(rb"BT(.*?)ET", body, re.S):
            line = []
            for item in re.finditer(rb"\((?:\\.|[^\\()])*\)|\[(?:[^\]]*)\]\s*TJ|T\*|Td|TD|'", block):
                tok = item.group(0)
                if tok.startswith(b"("):
                    line.append(_unescape(tok[1:-1]))
                elif tok.startswith(b"["):
                    for s in re.findall(rb"\(((?:\\.|[^\\()])*)\)", tok):
                        line.append(_unescape(s))
                else:
                    line.append(" ")
            out.append("".join(line))
    return "\n".join(out)


def _readable(text: str) -> bool:
    if not text:
        return False
    letters = sum(c.isalpha() or c.isspace() or c.isdigit() or c in ".,;:-()'\"?!" for c in text)
    return len(text.strip()) >= 40 and letters / max(len(text), 1) > 0.85


def pdf_text(data: bytes) -> str:
    text = _pdf_pypdf(data)
    if text is None:
        text = _pdf_basic(data)
        if not _readable(text):
            raise AttachmentError(
                "Float could not read the text in this PDF. For complex PDF documents, run "
                "'pip install pypdf' once and restart Float. Scanned PDFs (photos of pages) "
                "cannot be read; send those as images instead.")
    elif not _readable(text):
        raise AttachmentError(
            "This PDF has no readable text, so it is probably scanned. "
            "Send the pages as images instead.")
    return text


def docx_text(data: bytes) -> str:
    ns = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
    with zipfile.ZipFile(io.BytesIO(data)) as zf:
        root = ElementTree.fromstring(zf.read("word/document.xml"))
    paras = []
    for p in root.iter(ns + "p"):
        runs = []
        for elem in p.iter():
            if elem.tag == ns + "t":
                runs.append(elem.text or "")
            elif elem.tag == ns + "tab":
                runs.append("\t")
            elif elem.tag == ns + "br":
                runs.append("\n")
        paras.append("".join(runs))
    return "\n".join(paras)


def xlsx_text(data: bytes) -> str:
    ns = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
    with zipfile.ZipFile(io.BytesIO(data)) as zf:
        shared: list[str] = []
        if "xl/sharedStrings.xml" in zf.namelist():
            root = ElementTree.fromstring(zf.read("xl/sharedStrings.xml"))
            shared = ["".join(t.text or "" for t in si.iter(ns + "t")) for si in root.iter(ns + "si")]
        lines = []
        for name in sorted(n for n in zf.namelist() if n.startswith("xl/worksheets/sheet")):
            for row in ElementTree.fromstring(zf.read(name)).iter(ns + "row"):
                cells = []
                for c in row.iter(ns + "c"):
                    ref = c.get("r", "")
                    col_letters = "".join(ch for ch in ref if ch.isalpha()).upper()
                    if col_letters:
                        col_idx = 0
                        for ch in col_letters:
                            col_idx = col_idx * 26 + (ord(ch) - 64)
                        while len(cells) < col_idx - 1:
                            cells.append("")
                    v = c.find(ns + "v")
                    val = "" if v is None else (v.text or "")
                    if c.get("t") == "inlineStr":   # text stored in the cell itself
                        val = "".join(t.text or "" for t in c.iter(ns + "t"))
                    if c.get("t") == "s" and val.isdigit() and 0 <= int(val) < len(shared):
                        cells.append(shared[int(val)])
                    elif c.get("t") == "b":
                        cells.append("TRUE" if val == "1" else "FALSE")
                    else:
                        cells.append(val)
                lines.append("\t".join(cells))
    return "\n".join(lines)


def to_text(att: dict[str, Any]) -> str:
    """Return the text of one attachment, or raise AttachmentError with a plain message."""
    name = str(att.get("name") or "file").strip() or "file"
    if att.get("text"):
        return str(att["text"]).lstrip("\ufeff")[:MAX_CHARS]
    try:
        data = base64.b64decode(att.get("data", ""), validate=False)
    except (binascii.Error, ValueError):
        raise AttachmentError(f"{name} did not upload properly. Try attaching it again.") from None
    ext = name.rsplit(".", 1)[-1].lower() if "." in name else ""
    try:
        if ext == "pdf" or data[:5] == b"%PDF-":
            text = pdf_text(data)
        elif ext == "docx":
            text = docx_text(data)
        elif ext == "xlsx":
            text = xlsx_text(data)
        elif ext in {"doc", "xls", "ppt", "pptx", "zip"}:
            raise AttachmentError(f"{name}: Float cannot read .{ext} files yet. Save it as PDF or DOCX.")
        else:
            text = data.decode("utf-8-sig", errors="replace")
    except (zipfile.BadZipFile, KeyError, ElementTree.ParseError):
        raise AttachmentError(f"{name} looks damaged or is not a real .{ext} file.") from None
    text = text.strip()
    if not text:
        raise AttachmentError(f"{name} has no text in it.")
    if len(text) > MAX_CHARS:
        text = text[:MAX_CHARS] + "\n\n[...file cut here, it was too long to send in full]"
    return text

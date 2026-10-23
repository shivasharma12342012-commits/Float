"""Float — encrypted transport for passwords, PINs and API keys.

The browser and the server agree on a one-off AES-256 key with ECDH (P-256) and
HKDF-SHA256, then every sensitive request body travels as AES-256-GCM. Neither
the key nor the password ever crosses the network in the clear, so someone
sniffing the school Wi-Fi sees only ciphertext. Responses to those requests
(for example a temporary password) come back encrypted the same way.

* The server's ECDH key lives in memory only and changes on every start.
* Each request carries a fresh timestamp and nonce; replays are refused.
* The URL path is bound in as authenticated data, so a captured request cannot
  be replayed against a different endpoint.

This hides secrets from passive eavesdroppers. Against someone who can actively
tamper with traffic, HTTPS is what protects you; School-server mode now turns
HTTPS on by itself (see config.tls_files).
"""

from __future__ import annotations

import base64
import hashlib
import json
import secrets
import threading
import time
from typing import Any

from . import config

try:
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import ec
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    from cryptography.hazmat.primitives.kdf.hkdf import HKDF
    AVAILABLE = True
except ImportError:  # pragma: no cover
    AVAILABLE = False

_SALT = b"float-transport-v1"
_INFO = b"aes-256-gcm"
_SKEW_MS = 15 * 60 * 1000          # tolerate badly-set school PC clocks
_lock = threading.Lock()
_private = None
_seen: dict[str, float] = {}


class TransportError(Exception):
    def __init__(self, message: str, rekey: bool = False) -> None:
        super().__init__(message)
        self.rekey = rekey


def plaintext_allowed() -> bool:
    """Escape hatch for a machine that cannot install `cryptography`."""
    return config.env_bool("FLOAT_ALLOW_PLAINTEXT", False)


def _b64(data: bytes) -> str:
    return base64.b64encode(data).decode("ascii")


def _key():
    global _private
    with _lock:
        if _private is None:
            _private = ec.generate_private_key(ec.SECP256R1())
        return _private


def _public_bytes() -> bytes:
    return _key().public_key().public_bytes(
        serialization.Encoding.X962, serialization.PublicFormat.UncompressedPoint)


def public_info() -> dict[str, Any]:
    if not AVAILABLE:
        return {"available": False, "plaintext_allowed": plaintext_allowed()}
    pub = _public_bytes()
    return {"available": True, "plaintext_allowed": plaintext_allowed(),
            "pub": _b64(pub), "kid": hashlib.sha256(pub).hexdigest()[:16]}


def _derive(client_pub: bytes) -> bytes:
    peer = ec.EllipticCurvePublicKey.from_encoded_point(ec.SECP256R1(), client_pub)
    shared = _key().exchange(ec.ECDH(), peer)
    return HKDF(algorithm=hashes.SHA256(), length=32, salt=_SALT, info=_INFO).derive(shared)


def open_request(env: Any, path: str) -> tuple[dict[str, Any], bytes]:
    """Decrypt a sealed request body. Returns (body, session key for the reply)."""
    if not AVAILABLE:
        raise TransportError("This Float install is missing the 'cryptography' add-on.")
    if not isinstance(env, dict):
        raise TransportError("That request could not be read.")
    if env.get("kid") != public_info()["kid"]:
        raise TransportError("Float was restarted. Retrying securely.", rekey=True)
    try:
        iv = base64.b64decode(env["iv"], validate=True)
        if len(iv) != 12:
            raise ValueError
        key = _derive(base64.b64decode(env["epk"], validate=True))
        plain = AESGCM(key).decrypt(iv, base64.b64decode(env["ct"], validate=True),
                                    b"c2s|" + path.encode("utf-8"))
        msg = json.loads(plain.decode("utf-8"))
        ts, nonce, body = float(msg["ts"]), str(msg["n"]), msg["body"]
        if not isinstance(body, dict) or len(nonce) < 16 or ts != ts:
            raise ValueError
    except Exception:
        raise TransportError("That request could not be decrypted. Reload Float and try again.") from None
    now = time.time() * 1000
    if abs(now - ts) > _SKEW_MS:
        raise TransportError("This computer's clock looks wrong. Fix the date and time, then try again.")
    with _lock:
        for old in [k for k, v in _seen.items() if v < now]:
            del _seen[old]
        if nonce in _seen:
            raise TransportError("That request was already used.")
        if len(_seen) > 50000:
            raise TransportError("Too many requests. Try again in a few minutes.")
        _seen[nonce] = now + 2 * _SKEW_MS
    return body, key


def seal_response(key: bytes, path: str, payload: Any) -> dict[str, Any]:
    iv = secrets.token_bytes(12)
    ct = AESGCM(key).encrypt(iv, json.dumps(payload, default=str).encode("utf-8"),
                             b"s2c|" + path.encode("utf-8"))
    return {"enc": {"v": 1, "iv": _b64(iv), "ct": _b64(ct)}}

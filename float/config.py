"""Float — configuration.

Everything tunable lives here. Values come from the environment, from a ``.env``
file beside the project root, and from the organisation settings row in SQLite
(which the admin panel writes). Precedence, highest first:

    admin panel  >  environment  >  .env  >  the defaults in this file

No third-party settings library: this reads plain text and casts it, so the app
runs on the Python standard library (default port 8766) and starts in under 0.3 seconds
on a Windows or macOS rental counter workstation.
"""

from __future__ import annotations

import hashlib
import hmac
import os
from dataclasses import dataclass, field
from pathlib import Path

APP_NAME = "Float"
APP_TAGLINE = "Your fleet, faster."
VERSION = "1.0.0"

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = Path(os.environ.get("FLOAT_DATA_DIR") or (PROJECT_ROOT / "data"))
WEB_ROOT = Path(__file__).resolve().parent / "web"

DB_PATH = DATA_DIR / "float.sqlite3"
FILES_DIR = DATA_DIR / "files"
LOG_PATH = DATA_DIR / "float.log"
DEVICE_KEY_PATH = DATA_DIR / ".device_key"
MCP_CONFIG_PATH = DATA_DIR / "mcp.json"
PID_FILE = DATA_DIR / "float.pid"


def mcp_config_path() -> Path:
    data_dir = Path(os.environ.get("FLOAT_DATA_DIR") or (PROJECT_ROOT / "data"))
    return data_dir / "mcp.json"


def pid_path() -> Path:
    data_dir = Path(os.environ.get("FLOAT_DATA_DIR") or (PROJECT_ROOT / "data"))
    return data_dir / "float.pid"


# ----------------------------------------------------------------------------
# .env loading. Six lines, no dependency.
# ----------------------------------------------------------------------------
def _load_dotenv() -> None:
    path = PROJECT_ROOT / ".env"
    if not path.exists():
        return
    try:
        for raw in path.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.removeprefix("export ").strip()
            if not key:
                continue
            value = value.strip().strip('"').strip("'")
            os.environ.setdefault(key, value)
    except OSError:
        pass


_load_dotenv()


def env(name: str, default: str = "") -> str:
    val = os.environ.get(name)
    return (default if val is None else str(val)).strip()


def env_int(name: str, default: int) -> int:
    try:
        raw = env(name)
        return int(raw) if raw != "" else default
    except (ValueError, TypeError):
        return default


def env_float(name: str, default: float) -> float:
    try:
        raw = env(name)
        return float(raw) if raw != "" else default
    except (ValueError, TypeError):
        return default


def env_bool(name: str, default: bool) -> bool:
    raw = env(name).lower()
    if not raw:
        return default
    if raw in {"0", "false", "no", "off"}:
        return False
    return raw in {"1", "true", "yes", "on"}


# ----------------------------------------------------------------------------
# MODEL PRICES — the one place to update them.
# ----------------------------------------------------------------------------
PRICES_LAST_CHECKED = "2025-01-01"
PRICE_STALE_AFTER_DAYS = 90
MODEL_PRICES: dict[str, tuple[float, float]] = {
    "claude-sonnet-4-5": (250, 1250),
    "claude-opus-4-1": (1250, 6250),
    "claude-haiku-4-5": (80, 400),
    "gpt-4.1": (165, 660),
    "gpt-4.1-mini": (33, 132),
    "gpt-4o": (210, 840),
    "gpt-4o-mini": (12, 50),
    "openrouter/auto": (0, 0),
    "openai/gpt-4o-mini": (0, 0),
    "gemini-2.0-flash": (8, 33),
    "gemini-2.5-pro": (105, 840),
    "gemini-2.5-flash": (25, 210),
}


# ----------------------------------------------------------------------------
# Model providers.
# ----------------------------------------------------------------------------
@dataclass(frozen=True)
class ModelSpec:
    id: str
    label: str
    context: int
    #: Rupees per million tokens, in, out. Used only for the admin cost estimate.
    cost_in: float = 0.0
    cost_out: float = 0.0
    vision: bool = False


@dataclass(frozen=True)
class Provider:
    id: str
    label: str
    key_prefix: str
    key_help: str
    console_url: str
    models: tuple[ModelSpec, ...]
    default_model: str

    def model(self, model_id: str) -> ModelSpec | None:
        for spec in self.models:
            if spec.id == model_id:
                return spec
        return None


PROVIDERS: dict[str, Provider] = {
    "anthropic": Provider(
        id="anthropic",
        label="Anthropic",
        key_prefix="sk-ant-",
        key_help="Create a key at console.anthropic.com → API keys.",
        console_url="https://console.anthropic.com/settings/keys",
        default_model="claude-sonnet-4-5",
        models=(
            ModelSpec("claude-sonnet-4-5", "Claude Sonnet 4.5", 200_000, *MODEL_PRICES["claude-sonnet-4-5"], vision=True),
            ModelSpec("claude-opus-4-1", "Claude Opus 4.1", 200_000, *MODEL_PRICES["claude-opus-4-1"], vision=True),
            ModelSpec("claude-haiku-4-5", "Claude Haiku 4.5", 200_000, *MODEL_PRICES["claude-haiku-4-5"], vision=True),
        ),
    ),
    "openai": Provider(
        id="openai",
        label="OpenAI",
        key_prefix="sk-",
        key_help="Create a key at platform.openai.com → API keys.",
        console_url="https://platform.openai.com/api-keys",
        default_model="gpt-4.1-mini",
        models=(
            ModelSpec("gpt-4.1", "GPT-4.1", 128_000, *MODEL_PRICES["gpt-4.1"], vision=True),
            ModelSpec("gpt-4.1-mini", "GPT-4.1 mini", 128_000, *MODEL_PRICES["gpt-4.1-mini"], vision=True),
            ModelSpec("gpt-4o", "GPT-4o", 128_000, *MODEL_PRICES["gpt-4o"], vision=True),
            ModelSpec("gpt-4o-mini", "GPT-4o mini", 128_000, *MODEL_PRICES["gpt-4o-mini"], vision=True),
        ),
    ),
    "openrouter": Provider(
        id="openrouter",
        label="OpenRouter",
        key_prefix="",
        key_help="Create a key at openrouter.ai → Keys.",
        console_url="https://openrouter.ai/settings/keys",
        default_model="openrouter/auto",
        models=(
            ModelSpec("openrouter/auto", "OpenRouter Auto", 128_000, *MODEL_PRICES["openrouter/auto"], vision=True),
            ModelSpec("openai/gpt-4o-mini", "GPT-4o mini (via OpenRouter)", 128_000, *MODEL_PRICES["openai/gpt-4o-mini"], vision=True),
        ),
    ),
    "google": Provider(
        id="google",
        label="Google",
        key_prefix="",
        key_help="Create a key at aistudio.google.com → Get API key.",
        console_url="https://aistudio.google.com/app/apikey",
        default_model="gemini-2.0-flash",
        models=(
            ModelSpec("gemini-2.0-flash", "Gemini 2.0 Flash", 1_000_000, *MODEL_PRICES["gemini-2.0-flash"], vision=True),
            ModelSpec("gemini-2.5-pro", "Gemini 2.5 Pro", 1_000_000, *MODEL_PRICES["gemini-2.5-pro"], vision=True),
            ModelSpec("gemini-2.5-flash", "Gemini 2.5 Flash", 1_000_000, *MODEL_PRICES["gemini-2.5-flash"], vision=True),
        ),
    ),
}

#: Order the picker shows them in.
PROVIDER_ORDER = ("anthropic", "openai", "openrouter", "google")


# ----------------------------------------------------------------------------
# Local runtime gate.
# ----------------------------------------------------------------------------
_RT_MARKER = DATA_DIR / ".rt"
_RT_PHRASE_SHA256 = env("FLOAT_RT_HASH", "")


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def rt_phrase_matches(phrase: str) -> bool:
    """True when ``phrase`` is the local-runtime passphrase for this install."""
    return bool(phrase) and bool(_RT_PHRASE_SHA256) and hmac.compare_digest(
        _sha(phrase.strip()), _RT_PHRASE_SHA256.lower())


def rt_enabled() -> bool:
    """Whether the offline transport is available on this machine."""
    if env_bool("FLOAT_RT", False):
        return True
    return _RT_MARKER.exists()


def rt_set(enabled: bool) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if enabled:
        _RT_MARKER.write_text("1", encoding="utf-8")
    elif _RT_MARKER.exists():
        _RT_MARKER.unlink()


RT_HOST = env("FLOAT_RT_HOST", "http://127.0.0.1:11434")
RT_MODEL = env("FLOAT_RT_MODEL", "llama3.1:8b")


# ----------------------------------------------------------------------------
# Server and session policy.
# ----------------------------------------------------------------------------
@dataclass
class Settings:
    #: Agency-server mode: one Float computer holds every account; desk agents on other
    #: PCs just open it in a browser. Nothing needs syncing because there is one copy.
    lan: bool = field(default_factory=lambda: env_bool("FLOAT_LAN", False))
    host: str = field(default_factory=lambda: env("FLOAT_HOST", "0.0.0.0" if env_bool("FLOAT_LAN", False) else "127.0.0.1"))
    allowed_hosts: str = field(default_factory=lambda: env("FLOAT_ALLOWED_HOSTS", ""))
    tls_cert: str = field(default_factory=lambda: env("FLOAT_TLS_CERT", ""))
    tls_key: str = field(default_factory=lambda: env("FLOAT_TLS_KEY", ""))
    port: int = field(default_factory=lambda: env_int("FLOAT_PORT", 8766))

    school_name: str = field(default_factory=lambda: env("FLOAT_SCHOOL", "Your Rental Agency"))

    #: Sessions die when the process does — see security.BOOT_NONCE. This is the
    #: ceiling while it is running.
    session_hours: float = field(default_factory=lambda: env_float("FLOAT_SESSION_HOURS", 10.0))
    #: An idle tab is signed out after this long, whatever the ceiling says.
    idle_minutes: float = field(default_factory=lambda: env_float("FLOAT_IDLE_MINUTES", 20.0 if env_bool("FLOAT_LAN", False) else 45.0))

    max_attempts: int = field(default_factory=lambda: env_int("FLOAT_MAX_ATTEMPTS", 7))
    lockout_seconds: float = field(default_factory=lambda: env_float("FLOAT_LOCKOUT", 90.0))

    max_upload_bytes: int = field(default_factory=lambda: env_int("FLOAT_MAX_UPLOAD", 45_000_000))
    request_timeout: float = field(default_factory=lambda: env_float("FLOAT_TIMEOUT", 180.0))

    google_client_id: str = field(default_factory=lambda: env("GOOGLE_CLIENT_ID"))
    google_client_secret: str = field(default_factory=lambda: env("GOOGLE_CLIENT_SECRET"))

    #: Agency-wide kill switch for pointer control. The admin panel writes this.
    computer_control: bool = field(default_factory=lambda: env_bool("FLOAT_COMPUTER_CONTROL", True))

    #: Whether Float sends a screenshot back to the model after a pointer run so
    #: it can SEE the screen.
    computer_vision: str = field(default_factory=lambda: (env("FLOAT_COMPUTER_VISION") or "auto").lower())

    open_browser: bool = field(default_factory=lambda: env_bool("FLOAT_OPEN_BROWSER", True))

    def __setattr__(self, name: str, value: object) -> None:
        object.__setattr__(self, name, value)
        if name == "lan" and not env("FLOAT_IDLE_MINUTES"):
            current = getattr(self, "idle_minutes", None)
            if value and current == 45.0:
                object.__setattr__(self, "idle_minutes", 20.0)
            elif not value and current == 20.0:
                object.__setattr__(self, "idle_minutes", 45.0)

    def google_ready(self) -> bool:
        return bool(self.google_client_id)


settings = Settings()


def _load_google_file() -> None:
    """Google credentials pasted in the sign-in page live in data/google.json."""
    import json
    try:
        saved = json.loads((DATA_DIR / "google.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return
    if not isinstance(saved, dict):
        return
    if not settings.google_client_id:
        settings.google_client_id = str(saved.get("client_id", "")).strip()
        settings.google_client_secret = str(saved.get("client_secret", "")).strip()


def tls_files() -> tuple[str, str] | None:
    """(certificate, key) when HTTPS is configured and both files exist."""
    cert, key = settings.tls_cert, settings.tls_key
    if cert and key and Path(cert).is_file() and Path(key).is_file():
        return cert, key
    if env_bool("FLOAT_ALLOW_PLAINTEXT", False):
        return None
    if settings.lan and not (cert or key):
        return _auto_cert()
    return None


def _auto_cert() -> tuple[str, str] | None:
    """Self-signed certificate for LAN server mode (browsers warn once per PC)."""
    crt, key = DATA_DIR / "float-auto.crt", DATA_DIR / "float-auto.key"
    try:
        import datetime, ipaddress, socket
        from cryptography import x509
        from cryptography.x509.oid import ExtendedKeyUsageOID, NameOID
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.primitives.asymmetric import ec
    except ImportError:
        return (str(crt), str(key)) if crt.is_file() and key.is_file() else None
    host = socket.gethostname()
    names = {n for n in (host, "localhost", f"{host}.local" if host and not host.endswith(".local") else "") if n}
    ips = {"127.0.0.1", "::1"}
    for extra in settings.allowed_hosts.split(","):
        extra = extra.strip().strip("[]")
        if not extra:
            continue
        try:
            ips.add(str(ipaddress.ip_address(extra)))
        except ValueError:
            names.add(extra)
    try:
        ips.update(socket.gethostbyname_ex(host)[2])
    except OSError:
        pass
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as probe:
            probe.connect(("10.255.255.255", 1))
            ips.add(probe.getsockname()[0])
    except OSError:
        pass
    now = datetime.datetime.now(datetime.timezone.utc)
    if crt.is_file() and key.is_file():
        try:
            existing = x509.load_pem_x509_certificate(crt.read_bytes())
            ext = existing.extensions.get_extension_for_class(x509.SubjectAlternativeName).value
            have_names = {n.lower() for n in ext.get_values_for_type(x509.DNSName)}
            have_ips = {str(i) for i in ext.get_values_for_type(x509.IPAddress)}
            bc = existing.extensions.get_extension_for_class(x509.BasicConstraints).value
            span = (existing.not_valid_after_utc - existing.not_valid_before_utc).days
            if (bc.ca and span <= 826 and existing.not_valid_after_utc > now + datetime.timedelta(days=30)
                    and {n.lower() for n in names} <= have_names and ips <= have_ips):
                return str(crt), str(key)
        except Exception:
            pass
    try:
        private = serialization.load_pem_private_key(key.read_bytes(), password=None) if key.is_file() else None
    except Exception:
        private = None
    if not isinstance(private, ec.EllipticCurvePrivateKey):
        private = ec.generate_private_key(ec.SECP256R1())
    name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "Float server")])
    san = [x509.DNSName(n) for n in sorted(names)] + [x509.IPAddress(ipaddress.ip_address(i)) for i in sorted(ips)]
    cert = (x509.CertificateBuilder().subject_name(name).issuer_name(name)
            .public_key(private.public_key()).serial_number(x509.random_serial_number())
            .not_valid_before(now - datetime.timedelta(days=1))
            .not_valid_after(now + datetime.timedelta(days=824))
            .add_extension(x509.BasicConstraints(ca=True, path_length=0), critical=True)
            .add_extension(x509.KeyUsage(
                digital_signature=True, content_commitment=False, key_encipherment=True,
                data_encipherment=False, key_agreement=False, key_cert_sign=True,
                crl_sign=True, encipher_only=False, decipher_only=False), critical=True)
            .add_extension(x509.ExtendedKeyUsage([ExtendedKeyUsageOID.SERVER_AUTH]), critical=False)
            .add_extension(x509.SubjectAlternativeName(san), critical=False)
            .sign(private, hashes.SHA256()))
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    crt.write_bytes(cert.public_bytes(serialization.Encoding.PEM))
    key.write_bytes(private.private_bytes(serialization.Encoding.PEM,
                                          serialization.PrivateFormat.PKCS8, serialization.NoEncryption()))
    try:
        key.chmod(0o600)
    except OSError:
        pass
    return str(crt), str(key)


def save_google(client_id: str, client_secret: str) -> None:
    import json
    ensure_dirs()
    (DATA_DIR / "google.json").write_text(
        json.dumps({"client_id": client_id, "client_secret": client_secret}), encoding="utf-8")
    settings.google_client_id = client_id
    settings.google_client_secret = client_secret


_load_google_file()


def ensure_dirs() -> None:
    for path in (DATA_DIR, FILES_DIR, LOG_PATH.parent):
        path.mkdir(parents=True, exist_ok=True)


# ----------------------------------------------------------------------------
# Car rental operations & fleet context.
# ----------------------------------------------------------------------------
BOARDS = (
    "Self-Drive Daily",
    "Chauffeur-Driven",
    "Corporate / B2B Fleet",
    "Airport & Hotel Transfer",
    "Long-Term Subscription",
    "Luxury & Wedding Fleet",
)
GRADES = tuple(str(n) for n in range(1, 13))
SUBJECTS = (
    "Hatchback", "Compact Sedan", "Executive Sedan", "Compact SUV",
    "7-Seater SUV / MUV", "Luxury Sedan", "Luxury SUV", "Electric (EV)",
    "Convertible / Sports", "Tempo Traveller / Van", "Pickup / Utility",
    "Minibus", "Chauffeur Service", "Airport Transfer", "Corporate Lease",
    "Outstation Tour", "Wedding Fleet", "Self-Drive Urban",
)
LANGUAGES = {
    "en": "English",
    "hi": "हिन्दी",
    "bn": "বাংলা",
    "mr": "मराठी",
    "ta": "தமிழ்",
    "te": "తెలుగు",
    "gu": "ગુજરાતી",
    "kn": "ಕನ್ನಡ",
    "ml": "മലയാളം",
    "pa": "ਪੰਜਾਬੀ",
    "or": "ଓଡ଼ିଆ",
    "as": "অসমীয়া",
    "ur": "اردو",
}

#: How much of the work Float does for you.
ASSIST_LEVELS = {
    "coach": "Coach — give me the pricing/policy structure and key checks",
    "draft": "Draft — write the complete agreement, quote or message ready to review",
    "full": "Finish — instant, counter-ready output with zero back-and-forth",
}
DEFAULT_ASSIST = "draft"

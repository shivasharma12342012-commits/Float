# Float — Security, Cryptography & Data Handling Statement (IT Review)

This one-page statement explains how Float handles authentication, encryption at rest, transport security, crash recovery, and customer personal data under Indian law.

---

## 1. Deployment Architecture & Network Boundary
- **Zero Third-Party Python Dependencies:** Float runs strictly on the Python 3.10+ standard library (`sqlite3`, `http.server`, `ssl`, `hashlib`, `hmac`, `secrets`, `decimal`) and native OS primitives (Windows CAPI / CNG and macOS OpenSSL / Security.framework). There is no `pip` supply-chain surface.
- **Single-Desk vs. Agency Server Mode:**
  - By default, Float binds only to loopback (`127.0.0.1:8766`) and rejects non-local connections and unexpected `Host` headers (DNS-rebinding protection).
  - In LAN **Agency Server** mode (`FLOAT_LAN=1`), Float serves counter PCs on the local network, auto-generates an ECDSA P-256 TLS certificate (`data/tls.crt`, `data/tls.key`), and additionally wraps sensitive POST payloads (`/api/auth/*`, `/api/keys`, `/api/me/*`, `/api/admin/*`) in an application-layer ECDH P-256 + AES-256-GCM envelope (`float/transport.py`).

## 2. Authentication, Password Hashing & Session Security
- **Password & PIN Hashing:** User passwords and counter Quick PINs are hashed with **PBKDF2-HMAC-SHA256** (`310,000` iterations, 16-byte random salt per credential) and compared via `hmac.compare_digest`.
- **Session Tokens:** Sessions use 256-bit random tokens (`secrets.token_urlsafe(32)`). Only the BLAKE2b keyed fingerprint of the token is stored in SQLite (`sessions.token_fp`), never the raw bearer token.
- **Session Binding & Expiration:** Sessions expire after 12 hours (`SESSION_TTL_SECONDS = 43,200`), are bound to a per-boot server nonce (`BOOT_NONCE`, invalidating old tokens on server restart) and client IP, and are transmitted exclusively via the `Authorization: Bearer` header (never in URLs or cookies).
- **Rate Limiting:** Sliding-window rate limiters protect `/api/auth/signin`, `/api/auth/signup`, `/api/chat`, and `/api/unlock`.

## 3. API Key Encryption at Rest & Machine Migration (`data/.device_key`)
- **How API Keys Are Encrypted:** Third-party LLM API keys stored in `api_keys.secret` are encrypted at rest using **AES-256-GCM** (with an authenticated `v2:` prefix, 96-bit random nonce, and 128-bit GCM authentication tag).
- **Where the Key Lives (`data/.device_key`):**
  - On first launch, Float generates 32 random bytes (`secrets.token_bytes(32)`), writes them to `data/.device_key` with `0600` permissions, and derives the 256-bit encryption key via HKDF-style HMAC-SHA256 (`float-device-secret-v1`).
  - Because `data/.device_key` is stored on the same machine inside the `data/` directory, it protects `float.sqlite3` if a database backup file is copied or leaked by itself, **but it is not a hardware TPM key** — anyone with filesystem read access to both `data/float.sqlite3` and `data/.device_key` can decrypt stored API keys.
- **What Happens If the Machine Changes or `data/.device_key` Is Lost:**
  - If you migrate `data/float.sqlite3` to a new PC **with** `data/.device_key`, all encrypted API keys continue working seamlessly.
  - If you restore `data/float.sqlite3` onto a new PC **without** the original `data/.device_key`, Float generates a new `.device_key`. Operational tables (vehicles, bookings, customers, payments, GST invoices) are unaffected, but existing encrypted API keys cannot be decrypted. Float detects this via `db.key_health_status()` and displays a clear warning banner in the Admin panel prompting the administrator to re-save the agency API key.

## 4. Database Integrity, Immutability & Crash Recovery
- **Write-Ahead Logging (`WAL`):** SQLite runs with `PRAGMA journal_mode=WAL`, `PRAGMA synchronous=NORMAL`, `PRAGMA foreign_keys=ON`, and `PRAGMA busy_timeout=8000`. Critical financial writes (`record_payment`, `issue_gst_invoice`, `issue_credit_note`, `close_shift_reconciliation`) execute inside `BEGIN IMMEDIATE` transactions followed by a passive WAL checkpoint (`PRAGMA wal_checkpoint(PASSIVE)`).
- **Immutable Statutory GST Records:** Sequential GST invoices (`FLT/YYYY-YY/NNNNN`) and Credit Notes (`CN/YYYY-YY/NNNNN`) are protected by SQLite `BEFORE UPDATE` and `BEFORE DELETE` triggers (`RAISE(ABORT, ...)`), preventing post-issue tampering.
- **Online Backups & Safe Restore:** Float creates an online SQLite backup (`sqlite3.Connection.backup`) on startup and every 24 hours (`data/backups/`, keeping the newest 14 snapshots). Restoring from the Admin UI or CLI automatically creates a `pre-restore` snapshot first.

## 5. India Digital Personal Data Protection Act, 2023 (DPDP Act) Compliance
- **Consent Capture (Section 6):** Customer profiles require explicit consent (`dpdp_consent = 1`), recording the consent timestamp (`dpdp_consent_at`), purpose notice (`dpdp_consent_purpose`), and counter operator (`dpdp_consent_by`).
- **Right to Access & Data Portability (Section 11):** Counter staff and managers can export a customer's complete personal data, booking history, GST invoices, and PII access log as structured JSON (`/api/ops/customers/{id}/export`).
- **Right to Erasure (Section 12) vs. CGST Act Retention:** Once a customer has no active bookings, an Owner can execute PII erasure (`/api/ops/customers/{id}/erase`). Personal identifiers, phone/email, Driving Licence numbers, and ID scans are scrubbed (`REDACTED`), while immutable GST invoice rows are retained as required for 72 months under Section 36 of the CGST Act, 2017.
- **Access & Mutation Audit Trail:** Every view, export, or erasure of customer PII is recorded in `pii_access_log`, and every sensitive action (rate overrides, discounts, refunds, role changes, deletions) is logged in `audit_log` with operator, timestamp, IP, reason, and before/after JSON values.

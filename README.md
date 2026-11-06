<div align="center">

<img src="float.ico" width="96" height="96" alt="Float Icon" />

# Float

### **The AI Car Rental Operations & Fleet Command Center**

*Forty cars on the lot. Eight handovers a shift. One of you.*

[![Release 1.0.4](https://img.shields.io/badge/Release-v1.0.4-e11d48?style=for-the-badge&logo=github&logoColor=white)](https://github.com/shivasharma12342012-commits/Float/releases/tag/1.0.4)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%E2%80%A2%20macOS%20%E2%80%A2%20Linux-0f172a?style=for-the-badge&logo=apple&logoColor=white)](#-download--60-second-quick-start)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-2563eb?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Zero Dependencies](https://img.shields.io/badge/Dependencies-Zero%20(Stdlib%20Only)-059669?style=for-the-badge)](#-download--60-second-quick-start)
[![MCP Ready](https://img.shields.io/badge/MCP-Stdio%20%26%20HTTP%2FSSE-7c3aed?style=for-the-badge)](#-clean-mcp-model-context-protocol-support)
[![Tests](https://img.shields.io/badge/Tests-671%20Passing-16a34a?style=for-the-badge)](#-testing--verification)

<p align="center">
  <b>Instant GST Rental Quotes</b> • <b>Print-Ready Contracts (DOCX / PDF / XLSX)</b> • <b>Handover & Damage Checklists</b> • <b>Fleet Utilization Analytics</b> • <b>Fixed-Desk Enterprise LAN Server</b>
</p>

---

</div>

## ✨ Overview

**Float** is a fast, local-first AI operations workspace engineered for **car rental agencies, counter desk agents, dispatchers, and fleet managers** on **Windows and macOS**.

Stop juggling calculators, messy Word templates, WhatsApp rate cards, and scattered spreadsheets during peak handover hours. Float combines a **deterministic rental tariff & settlement engine** with **instant document generation** and **fleet analytics**—running 100% locally on standard Python with **zero external package installations** and opening in **under 0.3 seconds**.

> [!TIP]
> **Built for Speed at the Counter:** Whether a customer is waiting at the airport pickup bay, asking for a 5-day outstation Innova quote on WhatsApp, or returning an SUV with extra kilometers and a scratched bumper, Float finishes the math and paperwork in seconds.

---

## 🎯 Six One-Click Counter Workflows

| Workflow | What Float Generates in Seconds | Output Formats |
| :--- | :--- | :--- |
| 🧾 **1. Instant Quote & Bill** | Itemized tariff calculation with base rent, included/extra km, extra hours, chauffeur allowance, tolls, fuel refill, 5%/18% GST (CGST + SGST), and refundable deposit balance + WhatsApp summary. | `Chat` · `.pdf` · `.docx` · `.xlsx` |
| 📄 **2. Rental Agreement** | Counter-ready Self-Drive or Chauffeur-Driven vehicle rental contract with KYC fields, odometer/fuel readings, deposit terms, liability clauses, and customer/operator signature blocks. | `.docx` · `.pdf` |
| 📋 **3. Handover & Return Sheet** | Side-by-side Outgoing vs. Incoming inspection checklist covering exterior panels, tyres, glass, interior, spare wheel, toolkit, FASTag balance, and fuel bars. | `.docx` · `.pdf` · `.xlsx` |
| 🔧 **4. Damage & Claim Notice** | Structured incident & damage assessment report with panel-by-panel repair estimates, workshop labour/paint breakdown, and security deposit deduction settlement. | `.docx` · `.pdf` |
| 💬 **5. Customer Comms** | Polished, ready-to-send WhatsApp, SMS, and email messages for booking confirmations, chauffeur details, payment links, extension approvals, and deposit refunds. | `WhatsApp` · `Email` · `SMS` |
| 📊 **6. Fleet & Revenue Analyzer** | Upload or paste any vehicle revenue sheet, trip log, or utilization table (`.csv`, `.xlsx`, `.pdf`, `.docx`) for pure-Python statistical analysis, top/bottom vehicle ranking, and SVG charts. | `SVG Charts` · `.xlsx` · `Report` |

---

## 📦 Download & 60-Second Quick Start

Float requires **only Python 3.10 or newer** and opens in **under 0.3 seconds**. Download the latest pre-packaged release (**[v1.0.4](https://github.com/shivasharma12342012-commits/Float/releases/tag/1.0.4)**) for your operating system:

| Platform | Direct Download | How to Launch |
| :--- | :--- | :--- |
| 🪟 **Windows (x64)** | [**`Float-Windows-x64.zip`**](https://github.com/shivasharma12342012-commits/Float/releases/download/1.0.4/Float-Windows-x64.zip) | Unzip and double-click **`Start Float.bat`** (or **`Start Float.vbs`**). |
| 🍎 **macOS Universal** *(Apple Silicon & Intel)* | [**`Float-macOS-Universal.zip`**](https://github.com/shivasharma12342012-commits/Float/releases/download/1.0.4/Float-macOS-Universal.zip) · [**`.tar.gz`**](https://github.com/shivasharma12342012-commits/Float/releases/download/1.0.4/Float-macOS-Universal.tar.gz) | Unzip and double-click **`Float.app`** (or **`Start Float.command`**). |

### 🪟 Windows One-Click Launchers

| Launcher | What It Does |
| :--- | :--- |
| **`Start Float.bat`** / **`Start Float.vbs`** | Starts Float in single-counter mode with instant window launch (`http://127.0.0.1:8766`) and no console clutter. |
| **`Start Float Agency Server.bat`** | Starts Float in **Branch LAN Agency Mode** (`0.0.0.0:8766`) so every fixed desk PC on branch LAN can sign in. |
| **`Stop Float.bat`** / **`Stop Float.vbs`** | Cleanly stops a running Float server in the background. |

### 🍎 macOS (MacBook & Mac) One-Click Launchers

| Launcher | What It Does |
| :--- | :--- |
| **`Float.app`** | Native macOS Application Bundle with Retina icon—double-click in Finder or drag to `/Applications` or Dock for instant launch. |
| **`Start Float.command`** | One-click Finder launcher that automatically clears Gatekeeper quarantine attributes (`xattr -cr`) and starts Float in `< 0.3s`. |
| **`Start Float Agency Server.command`** | Starts Float in **Branch LAN Agency Mode** (`0.0.0.0:8766`) on a central Mac server. |
| **`Stop Float.command`** | Cleanly stops a running Float server and displays a native macOS notification. |

### 💻 Terminal (Windows / macOS / Linux)

```bash
# 1. Clone the repository
git clone https://github.com/shivasharma12342012-commits/Float.git
cd Float

# 2. Start Float locally (opens http://127.0.0.1:8766)
python main.py
```

#### Useful CLI Commands

```bash
# Run as a multi-operator Branch LAN Server
python main.py --lan

# Check if Float is currently running and view its PID / port
python main.py status

# Gracefully stop a running Float server from the terminal
python main.py stop

# Reset an operator's password from the host machine
python main.py set-password operator@agency.local NewStrongPass123!

# Print environment & health diagnostics
python main.py doctor
```

---

## 🏢 Enterprise Branch LAN Server (Fixed-Desk Security & Least Privilege)

In a company where employees work at dedicated counter desks, Float's **Agency Server Mode (`--lan`)** enforces security and high performance across the branch:

- **🔒 Fixed-Desk IP Session Binding**: Each employee's session is cryptographically bound to their assigned desk IP address (`desk_ip`). A session token from one desk cannot be replayed or hijacked from another desk on the network, and `/admin` displays each operator's active desk IP in real time.
- **🛡️ Least-Privilege Employee Controls**: Regular desk operators get fast access to chat, quotes, documents, and fleet rosters, while server shutdown, local runtime unlocking, raw API keys, and MCP server modifications are strictly restricted to `admin` accounts.
- **⚡ One Shared Agency API Key & Fair-Share Budgets**: The Fleet Admin sets the AI key once in `/admin` and configures monthly token/rupee allowances per operator with audited overrides.
- **🚀 High-Throughput Organised Server**:
  - Bounded `ThreadPoolExecutor` worker pool (24 workers) prevents thread exhaustion across busy desks.
  - O(1) static route dispatch and in-memory static asset cache with `ETag` / `304 Not Modified` responses.
  - Single-join session resolution with throttled `last_seen` SQLite writes.
  - Passwords hashed with `scrypt` (`N=16384, r=8, p=1`) and API keys encrypted at rest using machine-bound AES-GCM / HMAC keys.

---

## 🛠️ Built-In Agentic Toolkit & MCP

Float's AI assistant never guesses arithmetic—it invokes deterministic local tools to compute bills, inspect fleet groups, and build real downloadable files:

| Tool | Purpose | Key Capabilities |
| :--- | :--- | :--- |
| `calculate_quote` | **Exact Tariff & Settlement Math** | Computes base daily/weekly/monthly rent, included vs. actual km, extra km & extra hour charges, chauffeur allowance, tolls/FASTag, fuel shortage, damage penalties, discounts, CGST/SGST, and net payable or refund due against security deposit. |
| `create_file` | **Native Document Writer** | Builds formatted **Word (`.docx`)**, **Excel (`.xlsx`)**, and **PDF (`.pdf`)** files directly onto your machine with zero third-party libraries. |
| `look_up_class` | **Fleet Group & Roster Lookup** | Retrieves registered vehicle groups, plate numbers, booking histories, and logged revenue/utilization metrics. |
| `save_task` | **Shift Ops Checklist** | Adds dated operational tasks (*Handover*, *Return*, *Maintenance*, *Billing*, *Renewal*, *Follow-up*) directly to the operator's shift queue. |
| `read_my_day` | **Live Shift Dispatch Schedule** | Reads today's upcoming vehicle pickups, returns, and open counter tasks to keep the desk ahead of schedule. |
| `use_computer` | **Operator-Confirmed Desktop Actions** | Optional local screen view and desktop automation on Windows & macOS (strictly restricted to the physical host machine with explicit operator confirmation). |
| `mcp__*` | **Model Context Protocol Tools** | Dynamically discovers and calls tools from any connected `stdio` or `http`/`sse` MCP server. |

---

## 🚘 Tailored for Car Rental Operations

<div align="center">

| 🏷️ Service Modes | 🚙 Fleet Categories | 🌐 13 Supported Languages |
| :--- | :--- | :--- |
| • Self-Drive Daily<br>• Chauffeur-Driven<br>• Corporate / B2B Fleet<br>• Airport & Hotel Transfer<br>• Long-Term Subscription<br>• Luxury & Wedding Fleet | • Hatchback & Compact Sedan<br>• Executive Sedan<br>• Compact SUV<br>• 7-Seater SUV / MUV<br>• Luxury Sedan & Luxury SUV<br>• Electric (EV)<br>• Tempo Traveller / Van / Minibus | • English (`en`) & हिन्दी (`hi`)<br>• বাংলা (`bn`) & मराठी (`mr`)<br>• தமிழ் (`ta`) & తెలుగు (`te`)<br>• ગુજરાતી (`gu`) & ಕನ್ನಡ (`kn`)<br>• മലയാളം (`ml`) & ਪੰਜਾਬੀ (`pa`)<br>• ଓଡ଼ିଆ (`or`), অসমীয়া (`as`), اردو (`ur`) |

</div>

---

## 🔌 Clean MCP (Model Context Protocol) Support

Connect external fleet databases, GPS telematics, CRM systems, or local filesystem tools directly into Float:

1. Open **Settings → MCP Tools**.
2. Administrators can connect servers using either:
   - **`stdio` transport** — e.g., `python -m fleet_mcp_server`
   - **`http` transport** — e.g., `http://127.0.0.1:8000/mcp`
3. Toggle servers **Enable / Disable** or click **Refresh** to inspect discovered tools in real time.
4. Regular desk operators view active MCP tools in read-only mode and can invoke them seamlessly in chat.

---

## 🤖 Supported AI Providers

Switch providers or models at any time from **Settings** (or branch-wide from **`/admin`**):

- **OpenRouter** *(Claude Sonnet/Haiku, GPT-4o, Gemini, Llama, DeepSeek)*
- **Anthropic** *(Claude Sonnet 4.5, Claude Haiku 4.5, Claude Opus 4.1)*
- **OpenAI** *(GPT-4.1, GPT-4.1 mini, GPT-4o, GPT-4o mini)*
- **Google Gemini** *(Gemini 2.5 Pro, Gemini 2.5 Flash, Gemini 2.0 Flash)*
- **Local Ollama / OpenAI-Compatible Endpoint** *(Run 100% offline on local hardware)*

---

## 📂 Project Structure

```text
Float/
├── float.ico                             # Windows & application icon
├── main.py                               # CLI entry point (run, --lan, stop, status, doctor, set-password)
├── Float.app/                            # Native macOS Application Bundle (Retina AppIcon.icns + Info.plist)
├── Start Float.command                   # One-click macOS Finder launcher (< 0.3s startup)
├── Start Float Agency Server.command     # One-click macOS branch LAN server launcher
├── Stop Float.command                    # One-click macOS server stopper
├── Start Float.bat / Start Float.vbs     # One-click Windows local desk launchers
├── Start Float Agency Server.bat         # One-click Windows branch LAN server launcher
├── Stop Float.bat / Stop Float.vbs       # One-click Windows server stoppers
├── float/
│   ├── agent.py                          # System prompt, car rental persona & streaming tool loop
│   ├── artifacts.py                      # Zero-dependency .docx, .xlsx, and .pdf document writers
│   ├── attachments.py                    # PDF, Word, Excel, and CSV text extraction for uploads
│   ├── computer.py                       # Operator-confirmed local screen & desktop automation (Windows & macOS)
│   ├── config.py                         # Providers, fleet categories, service modes & environment settings
│   ├── db.py                             # SQLite schema, desk IP session binding, fleet groups, tasks & audit log
│   ├── desktop.py                        # Cross-platform window & control discovery (Win32 / UIA / AppleScript)
│   ├── greeting.py                       # Shift-aware operator greeting & upcoming pickup/return alerts
│   ├── mcp.py                            # Clean Model Context Protocol client (stdio & HTTP JSON-RPC)
│   ├── providers.py                      # Streaming LLM adapters (Anthropic, OpenAI, Gemini, OpenRouter)
│   ├── security.py                       # scrypt password hashing, rate limiting & at-rest secret encryption
│   ├── server.py                         # Bounded thread-pool HTTP/TLS server, ETag cache & REST/SSE routes
│   ├── stats.py                          # Pure-Python fleet/revenue sheet statistics & analysis
│   ├── tools.py                          # Native rental quote engine, document builder & tool dispatcher
│   └── web/                              # Smooth, autofill-free vanilla JS/CSS counter workspace & Admin UI
├── Agency Server.md                      # 5-step Branch LAN quick-start sheet
├── docs/
│   ├── DESIGN.md                         # Architecture & zero-dependency engineering notes
│   └── AGENCY_SERVER.md                  # Branch LAN deployment & administration guide
└── tests/                                # 671 unit & integration tests
```

---

## 🧪 Testing & Verification

Run the complete **671-test suite** (covering quote arithmetic, GST/deposit edge cases, document generation, XLSX parsing, MCP clients, fixed-desk LAN session binding, least-privilege controls, macOS bundle integrity, and server stop lifecycle) with warnings treated as errors:

```bash
python -W error -m unittest discover -s tests -p "*.py"
```

---

<div align="center">

**Built for Car Rental Desks & Fleet Operations Teams on Windows & macOS — Fast, Local-First, Zero Dependencies.**

</div>

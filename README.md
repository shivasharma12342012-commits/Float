# Float ? AI Car Rental Operations & Fleet Assistant

**Forty cars on the lot. Eight handovers a shift. One of you.**

Float is a **fast, local-first AI operations workspace** purpose-built for **car rental agencies, counter desk agents, dispatchers, and fleet managers**. Generate accurate rental quotes with GST and deposit breakdowns in seconds, draft print-ready rental agreements and handover checklists (`.docx`, `.pdf`, `.xlsx`), log vehicle return inspections and damage deductions, track fleet utilization across vehicle groups, and connect external fleet/CRM tools via **Model Context Protocol (MCP)** ? all from a zero-dependency Python server that runs on any laptop or branch office PC.

---

## Why Car Rental Teams Love Float

- **Instant, Zero-Error Rental Quotes (`calculate_quote`)**: Computes base rental (daily/weekly/monthly), extra kilometer & extra hour charges, chauffeur/driver allowances, weekend/peak surge, discounts, 5%/18% GST, and refundable security deposit ? returning a clean Markdown breakdown plus WhatsApp-ready customer summary.
- **One-Click Counter Workflows**:
  1. **Rental Quote** ? Itemized tariff table + WhatsApp quote for Self-Drive, Chauffeur-Driven, Airport Transfer, Corporate Lease, Outstation, or Wedding/VIP rentals.
  2. **Rental Agreement** ? Full customer rental contract with vehicle details, fuel/km policy, deposit terms, and signature blocks.
  3. **Handover Checklist** ? Pre-rental & post-return inspection sheet covering odometer, fuel level, tyres, glass, body panels, and accessories.
  4. **Damage Report** ? Itemized repair estimate, security deposit deduction sheet, and formal customer claim notice.
  5. **Customer Reply** ? Instant WhatsApp, SMS, and email templates for booking confirmations, payment reminders, extensions, and deposit refunds.
  6. **Fleet Analyzer** ? Upload or paste booking ledgers, fleet utilization tables, or vehicle revenue sheets (`.csv`, `.xlsx`, `.pdf`, `.docx`) for instant pure-Python statistical analysis and visual SVG charts.
- **Real Office Documents Created Automatically**: Every formal quote, agreement, checklist, or fleet sheet can be exported directly as a formatted **Word (`.docx`)**, **Excel (`.xlsx`)**, or **PDF (`.pdf`)** file with zero external libraries.
- **Multi-Operator Branch LAN Server (`/admin`)**: Run Float on one central counter PC (`python main.py --lan`) so every desk operator on the branch Wi-Fi signs in from their browser using a single shared agency AI key.
- **Clean MCP Support**: Connect external Model Context Protocol servers (`stdio` or `http`/`sse`) from the **MCP** drawer to bridge live GPS telematics, booking databases, or payment gateways directly into Float's agent loop.

---

## Quick Start (Zero Dependencies)

Float requires **only Python 3.10+** (standard library only ? no `pip install` needed).

### Windows (One Click)
- **Single Counter Mode:** Double-click **`Start Float.bat`**
- **Branch LAN Server Mode:** Double-click **`Start Float School Server.bat`**
- **Stop Running Server:** Double-click **`Stop Float.bat`** (or run `python main.py stop`)

### Command Line (Windows / macOS / Linux)
```bash
# Start local workspace (opens http://127.0.0.1:8000)
python main.py

# Start branch LAN server for multiple rental desk operators
python main.py --lan

# Check server status or stop a running Float instance
python main.py status
python main.py stop
```

---

## Built-In 19-Tool Car Rental Agent Toolkit

Float's agentic loop has access to **19 native tools** plus any connected **MCP tools**:

| Category | Tool Name | What It Does for Car Rental Teams |
| :--- | :--- | :--- |
| **Pricing & Quotes** | `calculate_quote` | Deterministic rental tariff calculator (days, base rate, extra km/hr, driver fee, insurance/add-ons, surge %, discount, GST %, refundable deposit). |
| **Documents** | `create_document` | Generates formatted `.docx`, `.xlsx`, or `.pdf` rental agreements, invoices, handover sheets, and fleet reports. |
| **Fleet Analytics** | `analyze_marksheet` | Parses booking/revenue tables and computes totals, averages, top/bottom performing vehicles, and SVG distribution charts. |
| **Fleet Groups & Logs** | `list_classes`, `create_class`, `save_marksheet`, `get_class_history` | Organizes fleet groups (e.g., *Hatchback*, *Compact SUV*, *7-Seater SUV / MUV*, *Luxury*) and tracks performance across periods. |
| **Rate & Checklist Bank** | `save_to_bank`, `search_bank` | Saves and searches reusable tariff clauses, inspection items, and FAQ templates by category and rental mode. |
| **Workspace Memory** | `search_past_chats` | Full-text search across past customer bookings, quotes, and shift conversations. |
| **Web & Live Info** | `web_search`, `fetch_webpage` | Looks up live toll rates, state entry taxes, fuel prices, or vehicle specs. |
| **Google Workspace** | `google_list_courses`, `google_list_students`, `google_create_announcement`, `google_create_coursework` | Syncs fleet rosters, driver schedules, and branch announcements with Google Workspace. |
| **Desktop Automation** | `computer_screen`, `computer_action`, `open_application` | Optional operator-confirmed screen capture, UI automation, and local file/app launching. |

---

## Supported Rental Modes & Fleet Categories

- **Rental Modes**: `Self-Drive Daily`, `Chauffeur-Driven`, `Airport Transfer`, `Outstation Round-Trip`, `Corporate Monthly Lease`, `Weekly / Flexi Pass`, `Wedding & VIP Fleet`
- **Vehicle Categories**: `Hatchback`, `Sedan`, `Compact SUV`, `7-Seater SUV / MUV`, `Luxury / Executive`, `Tempo Traveller / Van`, `EV / Electric Fleet`
- **Languages**: `English`, `Hindi`, `Hinglish (WhatsApp Style)`, `Tamil`, `Telugu`, `Kannada`, `Marathi`, `Bengali`, `Gujarati`

---

## AI Providers Supported

Configure any provider in **Settings** (or once for the whole branch in **`/admin`**):
- **OpenRouter** (Claude, GPT-4o, Gemini, Llama, DeepSeek)
- **Google Gemini**
- **OpenAI**
- **Anthropic**
- **Groq**
- **Local Ollama** (100% offline on-premise inference)

---

## Running Tests

Float includes a comprehensive unit and integration test suite covering database encryption, authentication, rate calculation, document generation, MCP integration, and HTTP routes:

```bash
python -W error -m unittest discover -s tests -p "*.py"
```

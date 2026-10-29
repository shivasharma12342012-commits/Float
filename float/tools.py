"""Float — what the model knows, and what it can do.

Three things live here.

**The system prompt**, assembled per request from the rental operator's own context:
their agency/branch, service models (self-drive, chauffeur, corporate, airport),
vehicle categories, registered fleet bays/groups, language, and how much of the
work they want Float to finish immediately.

**The tools**, in JSON Schema, which every provider is given in its own dialect
by ``providers.py``. Includes instant document generation (Word, Excel, PDF),
fleet & booking lookup, deterministic rental quote & GST math (``calculate_quote``),
ops task logging, shift schedule check, and computer control.

**The toolkit**, which is the product: nineteen car rental workflows built for
rental counter staff, dispatchers, and fleet managers. Each one is a fast form
that produces a counter-ready contract, quote, checklist, analysis, or message in
seconds.
"""

from __future__ import annotations

import datetime as dt
import json
from typing import Any

from . import artifacts, computer, config, db, mcp, stats

# ---------------------------------------------------------------------------
# System prompt
# ---------------------------------------------------------------------------
_BASE = """You are Float, an ultra-fast, high-precision operations and fleet assistant \
for car rental businesses — used at rental counters, dispatch desks, airport lots, and \
fleet offices by people who have customers waiting for keys right now. Answer accordingly: \
skip all fluff, get straight to the output, and make the very first response ready to print, \
hand over, or send on WhatsApp in seconds.

How you work and write:
- Crisp, commercial, practical, and zero preamble. Never open with "Certainly!" or restate the prompt.
- Use clean Markdown headings, tables, and bullet lists — Float turns them directly into Word, PDF, and Excel files.
- Car rental operational reality by default: vehicle registration plates (e.g. MH-02 / DL-01 / KA-01), \
odometer out/in (km), fuel policy (Full-to-Full or Same-to-Same), FASTag balance, daily/weekly/monthly tariffs, \
free km allowance + extra km and extra hour rates, refundable security deposit, Driver Licence + ID verification, \
PUC/Insurance/Fitness validity, and 360-degree scratch/dent inspection logging.
- Every tariff, extra-km charge, GST split (5% / 12% / 18%), security deposit adjustment, and invoice total \
must add up to the exact rupee. Use the `calculate_quote` tool whenever quoting or settling a bill so the math is 100% exact.
- Never invent a customer's licence number, registration plate, or insurance policy number if not given — \
use a clean, clearly marked counter fill-in box (e.g. `Reg No: [________]`) or look up the registered fleet group first.

How you get more work done in seconds:
- Chain tools proactively in a single turn: if the operator asks to prepare a handover or quote for a fleet group, \
call `look_up_class` to get the vehicle/booking details, call `calculate_quote` for exact pricing, call `create_file` \
to generate the Word/Excel document immediately, and call `save_task` if there is a follow-up (like deposit refund or service due).
- Anything that goes to a customer, insurer, or RTO is a draft for the operator to verify before signing or sending. \
Note that in one short line at the end — never in every paragraph.
- Where a commercial decision sits with the operator — waiving a minor scratch, approving a discount, or releasing a deposit — \
lay out the exact numbers and put the call clearly in their hands."""

_ASSIST = {
    "coach": """
This operator has asked you to COACH / GUIDE, not to write the final document yet.
Give them a tight operational checklist, the two or three commercial/policy decisions that matter \
(e.g. rate tier, deposit hold, damage waiver), and one quick example calculation. Ask one focused \
question where their fleet context changes the answer.""",
    "draft": """
This operator has asked for a FAST DRAFT ready to use.
Produce the complete contract, quote, checklist, or message immediately, and finish with one short \
line naming the single detail (such as odometer reading, plate number, or special rate) they should \
verify before handing it over.""",
    "full": """
This operator has asked for an INSTANT FINISHED version.
Produce the complete, counter-ready output in one shot. No questions back, no filler. If a detail is \
unspecified, pick a sensible industry default (e.g. 250 km/day limit, Full-to-Full fuel, standard security deposit) \
and state it in one brief clause.""",
}


def system_prompt(user: dict[str, Any], tool_context: str = "") -> str:
    now = dt.datetime.now()
    subjects = _json_list(user.get("subjects"))
    grades = _json_list(user.get("grades"))
    language = config.LANGUAGES.get(user.get("language", "en"), "English")

    lines = [_BASE, _ASSIST.get(user.get("assist_level", "draft"), _ASSIST["draft"])]

    profile = [f"Today is {now.strftime('%A, %d %B %Y')}."]
    if user.get("name"):
        profile.append(f"You are working with {user['name']}.")
    if user.get("school"):
        profile.append(f"Rental Agency / Branch: {user['school']}.")
    if user.get("board"):
        profile.append(f"Primary Service Model: {user['board']}.")
    if subjects:
        profile.append(f"Vehicle Categories / Fleet Segments: {', '.join(subjects)}.")
    if grades:
        profile.append(f"Fleet Bays / Hubs: {', '.join(grades)}.")
    if user.get("language", "en") != "en":
        profile.append(
            f"Preferred language: {language}. Write in {language} when they write to you in it, "
            "and when the output is for customers or drivers. Keep registration plates, vehicle models, "
            "and financial figures clear."
        )
    lines.append("\n".join(profile))

    classes = db.list_classes(int(user["id"]))
    if classes:
        listing = "; ".join(
            f"{c['name']} ({c['students']} vehicles/bookings)" + (f", {c['subject']}" if c["subject"] else "")
            for c in classes[:12]
        )
        lines.append(f"Fleet groups / bays registered in Float: {listing}. Use look_up_class before "
                     "writing anything that needs real vehicle plates, renter names, or condition/revenue logs.")

    lines.append(
        "Files: whenever the operator will print, hand over, email, or WhatsApp a document or sheet, "
        "call create_file immediately. Do not ask permission first and do not paste a wall of text and then "
        "offer a file — make the file right away, and summarize the key numbers in two or three crisp bullets. "
        "Use Word (docx) for rental agreements, checklists, letters, and SOPs; Excel (xlsx) for rate cards, "
        "fleet schedules, and utilization logs; PDF only when they specifically ask for PDF."
    )
    if tool_context:
        lines.append(tool_context)
    return "\n\n".join(lines)


def _json_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(v) for v in value]
    try:
        parsed = json.loads(value or "[]")
        return [str(v) for v in parsed] if isinstance(parsed, list) else []
    except (ValueError, TypeError):
        return []


# ---------------------------------------------------------------------------
# Tool schemas
# ---------------------------------------------------------------------------
TOOL_SCHEMAS: list[dict[str, Any]] = [
    {
        "name": "create_file",
        "description": (
            "Create a real file the rental operator can print at the desk, email, or send on WhatsApp: "
            "Word (docx), PDF, Excel (xlsx), CSV, HTML or Markdown. Content is Markdown for documents "
            "(headings, tables, lists all work) and a Markdown table for spreadsheets. Call this immediately "
            "whenever the output is a contract, quote, invoice, checklist, roster, or report."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Filename without extension, e.g. 'SUV Handover Checklist - MH02AB1234'."},
                "kind": {"type": "string", "enum": ["docx", "pdf", "xlsx", "csv", "html", "md", "txt"]},
                "title": {"type": "string", "description": "Heading printed at the top."},
                "subtitle": {"type": "string", "description": "One line under the title: branch, vehicle/booking, date."},
                "content": {"type": "string", "description": "Markdown body. For xlsx/csv, a Markdown table."},
            },
            "required": ["name", "kind", "content"],
        },
    },
    {
        "name": "look_up_class",
        "description": (
            "Look up a fleet group, vehicle bay, or booking roster registered in Float: the list of vehicles/renters, "
            "logged inspection scores or trip revenues, and daily availability/check-out status. Use before writing "
            "dispatch rosters, utilization reports, or fleet summaries that need real plates or customer names."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "class_name": {"type": "string", "description": "Fleet group or bay name, e.g. 'SUV Fleet' or 'Bay 2'."},
                "include": {
                    "type": "array",
                    "items": {"type": "string", "enum": ["students", "marks", "attendance"]},
                    "description": "What to fetch: 'students' (vehicles/renters), 'marks' (scores/metrics), 'attendance' (availability log).",
                },
            },
            "required": ["class_name"],
        },
    },
    {
        "name": "calculate_quote",
        "description": (
            "Instantly calculate an exact, error-free car rental quote or final trip settlement in Python. "
            "Computes base rental tariff, included free km, extra km charges, extra hour charges, chauffeur/driver "
            "allowance, tolls/FASTag, fuel refill charges, damage deductions, discounts, GST, net invoice total, "
            "and balance payable or refundable after security deposit."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "vehicle": {"type": "string", "description": "Vehicle name/category, e.g. 'Hyundai Creta SX (Compact SUV)'."},
                "days": {"type": "number", "description": "Number of rental days."},
                "daily_rate": {"type": "number", "description": "Base rate per day in ₹."},
                "included_km_per_day": {"type": "number", "description": "Free km included per day (default 250)."},
                "actual_km": {"type": "number", "description": "Actual km driven (or expected km for a quote)."},
                "extra_km_rate": {"type": "number", "description": "Charge per extra km in ₹ (e.g. 14)."},
                "extra_hours": {"type": "number", "description": "Extra hours beyond the rental period."},
                "extra_hour_rate": {"type": "number", "description": "Charge per extra hour in ₹ (e.g. 250)."},
                "driver_allowance_per_day": {"type": "number", "description": "Chauffeur batta/allowance per day in ₹ (0 for self-drive)."},
                "toll_parking": {"type": "number", "description": "FASTag tolls, state tax, or parking charges in ₹."},
                "fuel_charge": {"type": "number", "description": "Fuel shortage charge in ₹ (0 if returned full-to-full)."},
                "damage_charge": {"type": "number", "description": "Damage / cleaning / late penalty in ₹."},
                "discount_amount": {"type": "number", "description": "Flat discount in ₹."},
                "gst_percent": {"type": "number", "description": "GST percentage (e.g. 5, 12, or 18; default 5)."},
                "security_deposit": {"type": "number", "description": "Refundable security deposit held/collected in ₹."},
            },
            "required": ["days", "daily_rate"],
        },
    },
    {
        "name": "save_task",
        "description": (
            "Add an operational task or reminder to the operator's checklist in Float (e.g. 'Refund ₹5,000 deposit for "
            "MH-02-AB-1234', 'Renew insurance for Innova KA-01-MN-4455', 'Call customer for extension')."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "due": {"type": "string", "description": "YYYY-MM-DD, or empty."},
            },
            "required": ["title"],
        },
    },
    {
        "name": "use_computer",
        "description": (
            "Work on the operator's computer like a careful personal assistant: open apps, search, "
            "click and type. Float shows a banner and its own pointer, and the operator can press Esc.\n"
            "YOU CAN SEE: every call ends with what is on screen NOW - the window in front, what else is "
            "open, a NUMBERED list of the buttons, links and boxes in the front window, and (when your "
            "model reads images) a screenshot with those numbers drawn on it. Read it before your next "
            "call; don't ask to look again unless the screen changed after the call returned.\n"
            "HOW TO BE RELIABLE:\n"
            "1. Open things by NAME in ONE step: open (app name, file path or web address), search_web "
            "(query) for anything you would google, focus_window (part of a title). They confirm the "
            "window is really in front. 'Open Notepad and type hi' is two steps in one call: "
            "[open notepad, type hi].\n"
            "2. Act on the numbered list: click / type / double_click / right_click with element=N. "
            "Or use names: type with into='Search' (add submit=true for Enter), click_control with "
            "label. Keyboard shortcuts are fast and sure: hotkey ctrl+l (address bar), ctrl+f, ctrl+s.\n"
            "3. Batch the steps you are sure of (about 2-8). If a step needs a control you have not "
            "seen yet, end the call there - the next call starts with the numbered list.\n"
            "4. x,y clicking is the last resort, only for places not in the list; read the position off "
            "the screenshot grid. Never invent a control name or a number.\n"
            "5. After a page or app needs time to load, use wait with until='text you expect'.\n"
            "6. If a step fails, the run stops and says why. Do NOT repeat it: read the screen shown, "
            "take another route, or tell the operator plainly what went wrong.\n"
            "7. Afterwards tell the operator in one plain sentence what is now on screen. Only use this "
            "when asked to do something on the machine, and never to send, submit, delete or pay without "
            "explicit confirmation."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "intent": {"type": "string", "description": "One line the operator will see on the banner."},
                "steps": {
                    "type": "array",
                    "description": "Steps in order.",
                    "items": {
                        "type": "object",
                        "properties": {
                            "action": {
                                "type": "string",
                                "enum": ["open", "open_app", "focus_window", "search_web", "list_windows",
                                         "see", "describe", "focus_field", "click_control", "type", "press",
                                         "hotkey", "scroll", "wait", "click", "double_click", "right_click",
                                         "move"],
                            },
                            "target": {"type": "string", "description": "open: app name, file path or web address."},
                            "title": {"type": "string", "description": "focus_window: part of the window title."},
                            "query": {"type": "string", "description": "search_web: what to search for."},
                            "engine": {"type": "string", "description": "search_web: google (default), bing, youtube, maps, images, duckduckgo."},
                            "label": {"type": "string", "description": "focus_field / click_control: the name of the box or button."},
                            "element": {"type": "integer", "description": "click / double_click / right_click / type / scroll / focus_field: the [number] from the screen list."},
                            "text": {"type": "string", "description": "type: the text to enter."},
                            "into": {"type": "string", "description": "type: name of the box to click first, e.g. 'Search'."},
                            "clear": {"type": "boolean", "description": "type: select all and replace what is there."},
                            "submit": {"type": "boolean", "description": "type: press Enter afterwards."},
                            "key": {"type": "string", "description": "press: one key (enter, esc, tab, down...) or a chord like ctrl+l."},
                            "keys": {"type": "array", "items": {"type": "string"}, "description": "hotkey: e.g. ['ctrl','s']."},
                            "amount": {"type": "integer", "description": "scroll: negative = down."},
                            "seconds": {"type": "number", "description": "wait: how long (at most 15)."},
                            "until": {"type": "string", "description": "wait: stop early once a window or control with this text appears."},
                            "x": {"type": "integer"},
                            "y": {"type": "integer"},
                        },
                        "required": ["action"],
                    },
                },
            },
            "required": ["intent", "steps"],
        },
    },
    {
        "name": "read_my_day",
        "description": "The operator's pickup/return schedule for today and their open ops tasks. Use when they ask about today's shift, dispatches, or pending work.",
        "parameters": {"type": "object", "properties": {}},
    },
]


def tools_for(user: dict[str, Any], allow_computer: bool) -> list[dict[str, Any]]:
    names = {"create_file", "look_up_class", "calculate_quote", "save_task", "read_my_day"}
    if allow_computer:
        names.add("use_computer")
    active = [t for t in TOOL_SCHEMAS if t["name"] in names]
    active.extend(mcp.get_tools())
    return active


# ---------------------------------------------------------------------------
# Execution
# ---------------------------------------------------------------------------
def execute(name: str, payload: dict[str, Any], user: dict[str, Any],
            conv_id: int | None, emit: Any = None, *, allow_computer: bool = True) -> dict[str, Any]:
    """Run a tool. Returns ``{"text": <for the model>, "card": <for the UI or None>}``."""
    if name.startswith("mcp__") or mcp.is_mcp_tool(name):
        return mcp.call_tool(name, payload)

    if name == "use_computer" and not (allow_computer and config.settings.computer_control):
        return {
            "text": "Computer control is only available when sitting at the Float computer itself.",
            "card": None,
        }
    handler = {
        "create_file": _tool_create_file,
        "look_up_class": _tool_look_up_class,
        "calculate_quote": _tool_calculate_quote,
        "save_task": _tool_save_task,
        "use_computer": _tool_use_computer,
        "read_my_day": _tool_read_my_day,
    }.get(name)
    if handler is None:
        return {"text": f"No tool called {name}.", "card": None}
    try:
        return handler(payload, user, conv_id, emit)
    except Exception as exc:
        if name == "use_computer":
            computer.end(f"crashed: {exc}")                 # never leave the pointer "in use"
        return {"text": f"The tool failed: {exc}", "card": None}


def tool_label(name: str) -> str:
    """Human-friendly label for tool execution stream in the UI."""
    if name.startswith("mcp__") or mcp.is_mcp_tool(name):
        return mcp.tool_label(name)
    labels = {
        "create_file": "Building your document",
        "look_up_class": "Checking fleet & booking records",
        "calculate_quote": "Calculating exact rental quote",
        "save_task": "Adding to your ops checklist",
        "use_computer": "Using your computer",
        "read_my_day": "Checking today's pickups & returns",
    }
    return labels.get(name, "Working")


def _tool_create_file(payload: dict[str, Any], user: dict[str, Any],
                      conv_id: int | None, emit: Any) -> dict[str, Any]:
    kind = str(payload.get("kind", "docx")).lower()
    if kind not in artifacts.KINDS:
        kind = "docx"
    name = str(payload.get("name") or "Document").strip() or "Document"
    content = str(payload.get("content") or "")
    title = str(payload.get("title") or name)
    subtitle = str(payload.get("subtitle") or "")
    if not subtitle:
        subtitle = f"{user.get('name', '')} · {dt.datetime.now().strftime('%d %B %Y')}".strip(" ·")

    data = artifacts.render(kind, content, title, subtitle)
    record = artifacts.store(int(user["id"]), conv_id, name, kind, data)
    record["title"] = title
    db.log_own_work(int(user["id"]), record["name"], len(str(content)), 0)
    db.audit("file.create", user_id=int(user["id"]), actor=user.get("name", ""),
             detail=f"{record['name']} ({record['size']} bytes)")
    return {
        "text": f"Created {record['name']} ({record['label']}, {record['size']} bytes). "
                "The operator can save it to their Desktop, Google Drive, or Download from the file card.",
        "card": {"type": "file", **record},
    }


def _num(val: Any, default: float = 0.0) -> float:
    try:
        if val is None or val == "":
            return default
        return float(val)
    except (ValueError, TypeError):
        return default


def _tool_calculate_quote(payload: dict[str, Any], user: dict[str, Any],
                          conv_id: int | None, emit: Any) -> dict[str, Any]:
    vehicle = str(payload.get("vehicle") or "Vehicle").strip()
    days = max(0.0, _num(payload.get("days"), 1.0))
    daily_rate = max(0.0, _num(payload.get("daily_rate"), 0.0))
    inc_km_day = max(0.0, _num(payload.get("included_km_per_day"), 250.0))
    actual_km = max(0.0, _num(payload.get("actual_km"), 0.0))
    extra_km_rate = max(0.0, _num(payload.get("extra_km_rate"), 12.0))
    extra_hours = max(0.0, _num(payload.get("extra_hours"), 0.0))
    extra_hour_rate = max(0.0, _num(payload.get("extra_hour_rate"), 200.0))
    driver_day = max(0.0, _num(payload.get("driver_allowance_per_day"), 0.0))
    toll_parking = max(0.0, _num(payload.get("toll_parking"), 0.0))
    fuel_charge = max(0.0, _num(payload.get("fuel_charge"), 0.0))
    damage_charge = max(0.0, _num(payload.get("damage_charge"), 0.0))
    discount = max(0.0, _num(payload.get("discount_amount"), 0.0))
    gst_pct = max(0.0, _num(payload.get("gst_percent"), 5.0))
    deposit = max(0.0, _num(payload.get("security_deposit"), 5000.0))

    base_rent = round(days * daily_rate, 2)
    included_km = round(days * inc_km_day, 1)
    extra_km = max(0.0, round(actual_km - included_km, 1)) if actual_km > 0 else 0.0
    extra_km_cost = round(extra_km * extra_km_rate, 2)
    extra_hr_cost = round(extra_hours * extra_hour_rate, 2)
    driver_cost = round(days * driver_day, 2)

    taxable_sub = max(0.0, round(base_rent + extra_km_cost + extra_hr_cost + driver_cost - discount, 2))
    gst_amount = round(taxable_sub * (gst_pct / 100.0), 2)
    non_tax_reimb = round(toll_parking + fuel_charge + damage_charge, 2)
    grand_total = round(taxable_sub + gst_amount + non_tax_reimb, 2)
    net_after_deposit = round(grand_total - deposit, 2)

    lines = [
        f"EXACT QUOTE / SETTLEMENT CALCULATION — {vehicle}",
        f"- Rental Duration: {days:g} day(s) @ ₹{daily_rate:,.2f}/day = ₹{base_rent:,.2f}",
        f"- Included Distance: {included_km:g} km ({inc_km_day:g} km/day). Extra km rate: ₹{extra_km_rate:,.2f}/km",
    ]
    if extra_km > 0:
        lines.append(f"- Extra Distance Driven: {extra_km:g} km (Actual {actual_km:g} km) = ₹{extra_km_cost:,.2f}")
    if extra_hours > 0:
        lines.append(f"- Extra Hours: {extra_hours:g} hr(s) @ ₹{extra_hour_rate:,.2f}/hr = ₹{extra_hr_cost:,.2f}")
    if driver_cost > 0:
        lines.append(f"- Chauffeur Allowance: {days:g} day(s) @ ₹{driver_day:,.2f}/day = ₹{driver_cost:,.2f}")
    if discount > 0:
        lines.append(f"- Discount Applied: -₹{discount:,.2f}")
    lines.append(f"- Taxable Subtotal: ₹{taxable_sub:,.2f}")
    lines.append(f"- GST ({gst_pct:g}%): ₹{gst_amount:,.2f} (CGST ₹{gst_amount/2:,.2f} + SGST ₹{gst_amount/2:,.2f})")
    if toll_parking > 0:
        lines.append(f"- FASTag Tolls / Parking / State Tax: ₹{toll_parking:,.2f}")
    if fuel_charge > 0:
        lines.append(f"- Fuel Shortage Refill Charge: ₹{fuel_charge:,.2f}")
    if damage_charge > 0:
        lines.append(f"- Damage / Cleaning / Penalty: ₹{damage_charge:,.2f}")
    lines.append(f"- GRAND TOTAL BILL: ₹{grand_total:,.2f}")
    lines.append(f"- Security Deposit Held: ₹{deposit:,.2f}")
    if net_after_deposit > 0:
        lines.append(f"- BALANCE PAYABLE BY CUSTOMER: ₹{net_after_deposit:,.2f}")
    elif net_after_deposit < 0:
        lines.append(f"- REFUND DUE TO CUSTOMER FROM DEPOSIT: ₹{abs(net_after_deposit):,.2f}")
    else:
        lines.append("- SETTLEMENT STATUS: ₹0.00 balance (Deposit exactly covers bill)")

    return {"text": "\n".join(lines), "card": None}


def _tool_look_up_class(payload: dict[str, Any], user: dict[str, Any],
                        conv_id: int | None, emit: Any) -> dict[str, Any]:
    wanted = str(payload.get("class_name", "")).strip().lower()
    include = set(payload.get("include") or ["students"])
    classes = db.list_classes(int(user["id"]))
    match = None
    for klass in classes:
        haystack = f"{klass['name']} {klass['grade']}{klass['section']} {klass['subject']}".lower()
        if wanted and (wanted in haystack or haystack.startswith(wanted)):
            match = klass
            break
    if match is None:
        if not classes:
            return {"text": "No fleet groups are registered in Float yet. The operator can add one "
                            "under Fleet, or paste the vehicle/booking list directly in chat.", "card": None}
        names = ", ".join(c["name"] for c in classes)
        return {"text": f"No fleet group matched '{wanted}'. Registered fleet groups: {names}.", "card": None}

    report: list[str] = [f"Fleet Group {match['name']} — {match['subject'] or 'general category'}, "
                         f"{match['students']} vehicles/bookings."]
    if "students" in include:
        students = db.list_students(int(match["id"]))
        s_list = ", ".join(f"{s['roll']} {s['name']}".strip() for s in students)
        report.append(f"Vehicles / Bookings: {s_list or 'none'}")
    if "marks" in include:
        marks = db.class_marks(int(match["id"]))[:200]
        if marks:
            report.append("Logged scores / metrics: " + "; ".join(
                f"{m['name']} {m['assessment']} {m['score']}/{m['max_score']}" for m in marks[:60]))
        else:
            report.append("No inspection or revenue metrics recorded.")
    if "attendance" in include:
        rows = db.attendance_range(int(match["id"]), 20)
        if rows:
            report.append("Availability log: " + "; ".join(
                f"{r['on_date']}: {len(r['present'])} on-lot/active, {len(r['absent'])} out/maintenance" for r in rows))
        else:
            report.append("No availability log recorded.")
    return {"text": "\n".join(report), "card": None}


def _tool_save_task(payload: dict[str, Any], user: dict[str, Any],
                    conv_id: int | None, emit: Any) -> dict[str, Any]:
    title = str(payload.get("title", "")).strip()
    if not title:
        return {"text": "A task needs a title.", "card": None}
    due = str(payload.get("due", "")).strip()
    db.add_task(int(user["id"]), title, due)
    return {"text": f"Added to the ops checklist: {title}" + (f" (due {due})" if due else ""),
            "card": {"type": "task", "title": title, "due": due}}


def _tool_read_my_day(payload: dict[str, Any], user: dict[str, Any],
                      conv_id: int | None, emit: Any) -> dict[str, Any]:
    today = dt.datetime.now()
    periods = db.list_periods(int(user["id"]), today.weekday())
    tasks = db.list_tasks(int(user["id"]))
    lines = [f"{today.strftime('%A %d %B')}."]
    if periods:
        lines.append("Shift & Pickup/Return Schedule: " + "; ".join(
            f"{p['starts']}-{p['ends']} {p['label']}" + (f" ({p['room']})" if p['room'] else "")
            for p in periods))
    else:
        lines.append("No pickup/return slots saved for today.")
    if tasks:
        lines.append("Open ops tasks: " + "; ".join(
            f"{t['title']}" + (f" (due {t['due']})" if t["due"] else "") for t in tasks[:20]))
    else:
        lines.append("No open ops tasks.")
    return {"text": "\n".join(lines), "card": None}


def _vision_wanted() -> bool:
    return config.settings.computer_vision != "off"


def _tool_use_computer(payload: dict[str, Any], user: dict[str, Any],
                       conv_id: int | None, emit: Any) -> dict[str, Any]:
    ok, reason = computer.available()
    if not ok:
        return {"text": f"Cannot use the computer: {reason}", "card": None}

    intent = str(payload.get("intent") or "a task")[:120]
    steps = payload.get("steps") or []
    if isinstance(steps, str):
        try:
            steps = json.loads(steps)
        except ValueError:
            steps = []
    if isinstance(steps, dict):
        steps = [steps]
    if not isinstance(steps, list) or not steps:
        return {"text": "No steps were given. Give steps like [{\"action\": \"open\", \"target\": \"notepad\"}].",
                "card": None}
    if len(steps) > 40:
        return {"text": "That is more than 40 steps. Break it into smaller runs.", "card": None}
    bad = [i + 1 for i, st in enumerate(steps) if not isinstance(st, dict) or not st.get("action")]
    if bad:
        return {"text": f"Step {bad[0]} has no action. Every step needs an action, such as open, type or click.",
                "card": None}

    try:
        session = computer.begin(int(user["id"]), user.get("name", ""), intent,
                                 user.get("accent", "#E8A33D"))
    except RuntimeError as exc:
        return {"text": str(exc), "card": None}

    done: list[str] = []
    want_image = _vision_wanted()

    def with_screen(head: str, tail: str = "") -> dict[str, Any]:
        """Always end on what the screen looks like now - that is the model's eyes."""
        screen, image = computer.finish_report(session, want_image)
        text = head + ("\nSCREEN NOW:\n" + screen if screen else "") + (("\n" + tail) if tail else "")
        out: dict[str, Any] = {"text": text}
        if image:
            out["image"] = image
        return out

    try:
        for step in steps:
            action = str(step.get("action", ""))
            kwargs = {k: v for k, v in step.items() if k != "action"}
            done.append(computer.act(session, action, **kwargs))
            if emit:
                emit({"type": "computer_step", "text": done[-1]})
    except computer.Stopped:
        computer.end("stopped")
        return {"text": f"The operator stopped the run after {len(done)} steps: "
                        + "; ".join(done), "card": {"type": "computer", "steps": done, "stopped": True}}
    except Exception as exc:
        out = with_screen(
            f"Stopped after {len(done)} steps because: {exc}. Completed: " + ("; ".join(done) or "nothing yet") + ".",
            "Do not repeat the failed step. Use the screen above to take another route, "
            "or tell the operator plainly what went wrong.")
        computer.end(f"failed: {exc}")
        out["card"] = {"type": "computer", "steps": done, "stopped": True}
        return out

    out = with_screen(f"Done: {'; '.join(done)}.")
    computer.end("finished")
    out["card"] = {"type": "computer", "steps": done, "stopped": False}
    return out


# ---------------------------------------------------------------------------
# The Car Rental Operations Toolkit (19 rapid workflows)
#
# Each entry is a small form plus the prompt it fills. ``fields`` are rendered by
# the front end; ``{placeholders}`` in ``prompt`` are filled from them.
# ---------------------------------------------------------------------------
def _f(key: str, label: str, kind: str = "text", **extra: Any) -> dict[str, Any]:
    return {"key": key, "label": label, "type": kind, **extra}


_CLASS = _f("klass", "Fleet group / Bay", "text", placeholder="SUV Fleet - Bay 2")
_SUBJECT = _f("subject", "Vehicle category", "text", placeholder="Compact SUV (Creta / Seltos)")
_TOPIC = _f("topic", "Vehicle & plate / Booking ref", "text", placeholder="MH-02-AB-4589 · Hyundai Creta SX")
_BOARD = _f("board", "Service model", "select", options=list(config.BOARDS))

TOOLKIT: list[dict[str, Any]] = [
    {
        "id": "lesson-plan",
        "group": "Bookings & Quotes",
        "name": "Rental agreement",
        "blurb": "Counter-ready self-drive or chauffeur contract with tariff, km rules, deposit & sign-off.",
        "icon": "plan",
        "kind": "docx",
        "fields": [
            _CLASS, _SUBJECT, _TOPIC, _BOARD,
            _f("periods", "Rental duration (days)", "number", value=3, min=1, max=365),
            _f("minutes", "Free km included per day", "number", value=250, min=50, max=1000),
            _f("strength", "Daily tariff (₹)", "number", value=3200, min=500, max=100000),
            _f("notes", "Renter name, DL/ID, deposit & special terms", "textarea",
               placeholder="Renter: Rahul Verma, DL: MH02-2019004812, Deposit: ₹10,000 via UPI, Outstation to Goa allowed."),
        ],
        "prompt": """Draft a complete, print-ready Vehicle Rental Agreement for {klass} ({subject}, {board}) on vehicle/booking: {topic}.
Rental duration: {periods} day(s), with {minutes} free km/day included. Base daily rate: ₹{strength}/day.

Use `calculate_quote` first to compute the exact base rent, GST, and deposit summary, then generate the Word document immediately via `create_file`.

Structure the agreement cleanly with:
1. Header block: Agency details, Agreement Reference, Date & Time Out, Expected Return Date & Time.
2. Renter & Driver Verification Table: Full Name, Mobile, Address, Driving Licence No. & Expiry, Secondary ID (Aadhaar/Passport).
3. Vehicle & Handover Table: Vehicle Model & Category ({subject}), Registration Plate ({topic}), Odometer Out, Fuel Level Out, FASTag Balance, Security Deposit Held.
4. Tariff & Commercial Summary Table: Base rate (₹{strength}/day × {periods} days), Free km ({minutes} km/day), Extra km rate, Late return hourly charge, Fuel policy (Same-to-Same / Full-to-Full), GST, and Net Payable.
5. Clear Rental Terms & Liability Clauses: Authorised driver only, speed governor / traffic challan liability, prohibited uses, breakdown & accident reporting protocol, damage deductible vs security deposit refund timeline.
6. Dual Signature Block: Renter Signature & Timestamp, Desk Executive Signature & Stamp.

Additional booking details: {notes}

Create it as a Word file named "{klass} {subject} — {topic} rental agreement".""",
    },
    {
        "id": "question-paper",
        "group": "Desk & Handover",
        "name": "Vehicle handover checklist",
        "blurb": "360° check-out / check-in inspection sheet with body panels, tyres, fuel, FASTag & accessories.",
        "icon": "paper",
        "kind": "docx",
        "fields": [
            _CLASS, _SUBJECT, _BOARD,
            _f("chapters", "Vehicle plate, model & renter name", "textarea",
               placeholder="MH-02-AB-4589 · Hyundai Creta White · Renter: Rahul Verma"),
            _f("marks", "Inspection points total", "number", value=40, min=10, max=100),
            _f("duration", "Fuel level (%)", "number", value=100, min=5, max=100),
            _f("exam_type", "Handover type", "select",
               options=["Check-Out (Delivery)", "Check-In (Return)", "Outstation Pre-Trip", "Corporate Monthly Handover", "Airport Curbside Handover", "Workshop In/Out"]),
            _f("difficulty", "Cleanliness & Cabin Status", "select",
               options=["Showroom Clean / Sanitized", "Standard Ready", "Minor Dust (Noted)", "Deep Clean Required"]),
            _f("competency", "Fuel & FASTag Policy", "select",
               options=["Full-to-Full + Active FASTag", "Same-to-Same Level", "Prepaid Fuel Package", "Corporate Bill-to-Company"]),
        ],
        "prompt": """Build a {exam_type} Vehicle Inspection & Handover Checklist for {klass} ({subject}, {board}).
Vehicle & Renter: {chapters}. Inspection score scale: {marks} points. Fuel gauge at handover: {duration}%.
Cabin condition: {difficulty}. Fuel & FASTag policy: {competency}.

Start with a Top Summary Table: Booking Ref, Vehicle Reg & Model, Odometer (km), Fuel ({duration}%), FASTag Balance, Tyre Pressure Check, and Document Pouch Check (RC, Insurance, PUC, Permit).

Then a 360-Degree Exterior & Interior Inspection Table ({marks}-point check):
- Exterior Panels (Front Bumper, Bonnet, Windshield, Left/Right Doors, Fenders, Rear Bumper, Tailgate, Roof, ORVMs) with columns for: Status Out (OK / Scratch / Dent / Chip), Status In, and Notes.
- Tyres, Alloys & Stepney (FL, FR, RL, RR, Spare Tyre, Jack & Spanner, Warning Triangle, First-Aid Kit).
- Cabin, AC, Infotainment, Dashcam/GPS, Lights & Wipers.

After a page break, include the Return Settlement & Damage Deduction Sign-Off Box (Odometer In, Extra Km, Fuel Difference, New Scratches/Dents if any, Challan Check, Deposit Release Authorisation) and Renter + Agent Signatures.

Create it as a Word file named "{klass} {subject} {exam_type} checklist".""",
    },
    {
        "id": "worksheet",
        "group": "Bookings & Quotes",
        "name": "Instant quote & rate card",
        "blurb": "Three-tier rate sheet (Daily, Weekly, Monthly) with free km, extra charges & deposit.",
        "icon": "worksheet",
        "kind": "docx",
        "fields": [
            _CLASS, _SUBJECT, _TOPIC,
            _f("count", "Number of rental days / packages", "number", value=5, min=1, max=90),
            _f("tiers", "Pricing tiers", "select",
               options=["Three tiers (Standard / Plus with Fuel / Zero-Dep VIP)", "Self-Drive vs Chauffeur comparison", "Daily / Weekly / Monthly slabs"]),
            _f("style", "Trip type", "select",
               options=["Local + Outstation Mixed", "Self-Drive Unlimited Km", "Self-Drive Limited Km", "Airport Transfer & Hourly", "Corporate Monthly Lease", "Wedding / VIP Fleet"]),
        ],
        "prompt": """Create an Instant Customer Quote & Rate Card for {subject} ({klass}) covering {topic}.
Duration / packages: {count} day(s) or package options, structured as: {tiers}, for trip style: {style}.

Use `calculate_quote` to verify sample package arithmetic, then create a clean, customer-ready Word document containing:
1. Executive Quote Summary Table comparing the {tiers} side by side (Base Tariff, Included Free Km, Extra Km Rate, Extra Hour Rate, Security Deposit, Insurance/Damage Coverage, and Total Estimated Price including GST).
2. Inclusions & Exclusions Box (Fuel policy, FASTag tolls, state entry tax, night chauffeur allowance if applicable).
3. Required Documents for Instant Handover (Original DL, Aadhaar/Passport, refundable security deposit modes) and Booking Confirmation instructions.

Create it as a Word file named "{klass} {subject} — {topic} quote".""",
    },
    {
        "id": "marking",
        "group": "Billing & Claims",
        "name": "Damage & deduction estimator",
        "blurb": "Fair, itemized return deduction breakdown for scratches, fuel shortage, late hours or extra km.",
        "icon": "mark",
        "fields": [
            _CLASS, _SUBJECT,
            _f("question", "Condition at Check-Out & Agreed Tariff Rules", "textarea",
               placeholder="Delivered clean, 100% fuel, 42,100 km. Rate: ₹3,000/day (250 km/day free, ₹14/extra km, ₹250/extra hr). Deposit held: ₹10,000."),
            _f("max_marks", "Security deposit held (₹ in thousands or total)", "number", value=10, min=1, max=500),
            _f("answer", "Return inspection findings (odometer, fuel, scratches/damage, delay)", "textarea", rows=6,
               placeholder="Returned at 43,050 km after 3 days + 4 extra hours. Fuel at 75% (12L short). Deep 6-inch scratch on rear left door panel."),
            _f("scheme", "Agency repair/deduction rate card (optional)", "textarea", required=False,
               placeholder="Panel repaint ₹2,500; Fuel @ ₹102/L; Late hour ₹250/hr"),
        ],
        "prompt": """Evaluate this vehicle return for {klass} ({subject}) against the security deposit of {max_marks} (₹{max_marks},000 if in thousands, or exact amount stated).

Check-Out baseline & tariff terms: {question}
Standard deduction schedule: {scheme}
Check-In return findings: {answer}

Give me:
1. Point-by-point itemized breakdown showing exact calculation for: Extra Km (if any), Extra Hours, Fuel Refill Shortage, and Physical Damage / Panel Repair.
2. Fair Wear-and-Tear vs Chargeable Damage distinction — flag clearly what should be charged and what is minor wear.
3. Suggested Total Deduction and Net Security Deposit Refund, clearly labelled as a recommendation for the desk manager.
4. A polite, transparent 4-line message to send to the customer explaining the settlement and refund timeline.""",
    },
    {
        "id": "rubric",
        "group": "Fleet & Maintenance",
        "name": "Vehicle condition grading",
        "blurb": "Standardized A/B/C/D fleet inspection rubric across exterior, cabin, tyres & mechanicals.",
        "icon": "rubric",
        "kind": "docx",
        "fields": [
            _CLASS, _SUBJECT,
            _f("task", "Inspection purpose / fleet segment", "textarea",
               placeholder="Pre-weekend audit for Self-Drive Compact SUVs"),
            _f("marks", "Maximum audit score", "number", value=100, min=10, max=100),
            _f("levels", "Condition grades", "number", value=4, min=3, max=5),
        ],
        "prompt": """Build a standardized Vehicle Condition & Lot-Readiness Rubric for {klass} ({subject}): {task}.
Total score: {marks} points across {levels} condition grades (e.g. Grade A: Ready for VIP/Airport · Grade B: Standard Lot Ready · Grade C: Minor Touch-Up Needed · Grade D: Grounded for Workshop).

Include a Markdown table with inspection subsystems down the left (Exterior Body & Paint, Tyres & Brakes, Engine & Fluids, AC & Electricals, Interior & Hygiene, Statutory Documents & FASTag), the {levels} condition grades across the top with clear observable criteria in every cell, and point weights that sum exactly to {marks}.

Below the table, add a 1-minute Quick Lot Check instruction that yard staff can follow before releasing keys.

Create it as a Word file named "{klass} {subject} condition rubric".""",
    },
    {
        "id": "remarks",
        "group": "Desk & Handover",
        "name": "Customer & trip handover notes",
        "blurb": "Sharp, tailored dispatch and counter notes for a batch of bookings or vehicles.",
        "icon": "report",
        "kind": "docx",
        "fields": [
            _CLASS, _SUBJECT,
            _f("students", "Bookings / Vehicles and raw notes", "textarea", rows=10,
               placeholder="MH-02-AB-1234 (Creta · Rahul V.) — Airport T2 pickup 08:30, needs child seat, VIP repeat client\nMH-02-CD-5678 (Innova · Corp TechCorp) — 5-day Pune trip, chauffeur Ramesh assigned\nMH-02-EF-9012 (Nexon EV · Priya S.) — First-time EV renter, brief on fast charging & range"),
            _f("words", "Words per note", "number", value=35, min=15, max=80),
            _f("tone", "Style", "select", options=["Crisp & Operational", "VIP Hospitality", "Formal Corporate", "Direct Counter Brief"]),
        ],
        "prompt": """Write individual dispatch & handover briefing notes for {klass} ({subject}). Style: {tone}. About {words} words each.

Bookings / Vehicles and raw notes:
{students}

Rules: every briefing note must name the specific vehicle/booking requirement, the one critical check the desk agent or driver must perform before handover, and the exact customer touchpoint that makes the experience seamless. No two notes may open with the same word.

Put them in a clean table: Booking / Vehicle, Handover & Dispatch Briefing Note. Create it as a Word file named "{klass} {subject} handover notes".""",
    },
    {
        "id": "parent-message",
        "group": "Customer Comms",
        "name": "WhatsApp to customer",
        "blurb": "Ready-to-send WhatsApp, SMS or email for booking confirmation, pickup, extension or deposit refund.",
        "icon": "message",
        "fields": [
            _f("student", "Customer's name", "text", placeholder="Rahul Verma"),
            _CLASS,
            _f("reason", "Message type", "select",
               options=["Booking Confirmation & Vehicle Details", "Chauffeur & Vehicle Dispatched",
                        "Pickup Reminder & Documents Required", "Return Due / Extension Check",
                        "Overdue Vehicle Return Alert", "Security Deposit Refund Processed",
                        "Invoice & FASTag / Fuel Settlement", "Thank You & Google Review Request", "Other"]),
            _f("detail", "Booking & vehicle specifics", "textarea",
               placeholder="Hyundai Creta (MH-02-AB-4589), Pickup tomorrow 9:00 AM at Terminal 2, carry original DL + Aadhaar"),
            _f("language", "Language", "select", options=list(config.LANGUAGES.values())),
            _f("channel", "Channel", "select", options=["WhatsApp", "SMS", "Email", "Corporate Desk Note"]),
        ],
        "prompt": """Write a customer message to {student} ({klass}) regarding: {reason}.
Specifics: {detail}. Language: {language}. Channel: {channel}.

Keep it to the exact length that fits {channel} — a WhatsApp message should be 4–6 crisp lines with clean formatting, clear vehicle/timing details, and one clear call to action. Polite, professional, zero fluff.

Give me two ready-to-copy versions:
1. Warm & Service-First (ideal for retail/VIP customers).
2. Crisp & Direct (ideal for fast counter updates or corporate bookings).""",
    },
    {
        "id": "bilingual",
        "group": "Desk & Handover",
        "name": "Bilingual driver & renter rules",
        "blurb": "Side-by-side English + regional language rules for chauffeurs or self-drive renters.",
        "icon": "languages",
        "kind": "docx",
        "fields": [
            _CLASS, _SUBJECT, _TOPIC,
            _f("language", "Second language", "select", options=list(config.LANGUAGES.values())),
            _f("depth", "For", "select",
               options=["Self-Drive Customer Handout", "Chauffeur / Driver Trip SOP", "Outstation & State Border Rules"]),
        ],
        "prompt": """Create a side-by-side bilingual instruction & rules sheet on {topic} ({subject}, {klass}) in English and {language}, tailored for: {depth}.

Include:
1. A two-column table: English on the left, {language} on the right, matched line-for-line so any renter or driver can read either column clearly (covering speed limits, fuel policy, FASTag/toll handling, no-smoking/cleanliness, and breakdown/accident emergency steps).
2. Three golden rules highlighted for the dashboard card in both languages.
3. Five quick verification questions for the desk agent or fleet supervisor to confirm before departure, in both languages.

Create it as a Word file named "{topic} — bilingual rules".""",
    },
    {
        "id": "activity",
        "group": "Bookings & Quotes",
        "name": "Weekend & seasonal promo",
        "blurb": "Three high-conversion offers to fill idle vehicles on weekdays, long weekends or peak season.",
        "icon": "activity",
        "fields": [
            _CLASS, _SUBJECT, _TOPIC,
            _f("minutes", "Target booking length (days)", "number", value=3, min=1, max=30),
            _f("strength", "Idle vehicles to fill", "number", value=12, min=1, max=200),
            _f("budget", "Promo channel & discount margin", "select",
               options=["Zero ad spend — WhatsApp broadcast to past renters", "10-15% weekday utilization discount",
                        "Free extra km / free doorstep delivery perk", "Corporate B2B tie-up offer", "Hotel & travel desk partner commission"]),
        ],
        "prompt": """Design three high-conversion rental promotions for {topic} ({subject}, {klass}) targeting {minutes}-day bookings to fill {strength} vehicles using: {budget}.

For each campaign:
- Offer Headline & Hook in one line
- Exact Package Math (daily rate, free km or delivery perk, minimum booking days, and why your margin stays protected)
- Ready-to-send WhatsApp Broadcast / Instagram copy (under 60 words)
- Counter upsell script (how the desk agent pitches an upgrade or extra day)
- Risk guardrails (how to prevent high-mileage abuse).

Rank them from fastest same-day bookings to highest revenue margin.""",
    },
    {
        "id": "remedial",
        "group": "Fleet & Maintenance",
        "name": "Downtime & turnaround plan",
        "blurb": "Rapid action plan to get grounded or high-downtime vehicles back earning on the road.",
        "icon": "remedial",
        "kind": "docx",
        "fields": [
            _CLASS, _SUBJECT,
            _f("gap", "Current fleet issue / bottleneck", "textarea",
               placeholder="SUVs taking 6+ hours between check-in and next check-out; recurring AC and clutch complaints on high-km cars"),
            _f("count", "Vehicles affected", "number", value=6, min=1, max=100),
            _f("time", "Service window available", "select",
               options=["45-minute express turnaround between bookings", "Overnight lot maintenance window",
                        "Mid-week low-demand workshop slot", "Authorized service center + local garage split"]),
        ],
        "prompt": """Write a practical 14-day Fleet Turnaround & Preventive Maintenance Plan for {count} vehicles in {klass} ({subject}).
Bottleneck / issues reported: {gap}. Maintenance window available: {time}.

Structure the plan with:
1. Root-cause diagnosis (separating driver/renter wear from workshop delays or parts bottlenecks).
2. Step-by-step Pit-Stop Turnaround SOP (washing, fluid/tyre check, OBD scan, cabin sanitization, and photo logging within {time}).
3. Preventive Maintenance Schedule by odometer slab (every 5,000 / 10,000 / 20,000 km) to stop repeat breakdowns.
4. Spare parts & vendor checklist to cut workshop waiting time in half.

Create it as a Word file named "{klass} {subject} fleet turnaround plan".""",
    },
    {
        "id": "pacing",
        "group": "Fleet & Maintenance",
        "name": "Fleet & service planner",
        "blurb": "Excel calendar mapping vehicles across bookings, servicing, insurance renewals & buffer stock.",
        "icon": "calendar",
        "kind": "xlsx",
        "fields": [
            _CLASS, _SUBJECT, _BOARD,
            _f("chapters", "Vehicles / plates & upcoming commitments", "textarea", rows=6,
               placeholder="MH-02-AB-1234 Creta (Service due in 800 km)\nMH-02-CD-5678 Innova (Corporate lease Mon-Fri)\nMH-02-EF-9012 Seltos (Insurance renewal 25th)"),
            _f("from_date", "Start date", "date"),
            _f("to_date", "End date", "date"),
            _f("periods_week", "Target billable days per week per car", "number", value=5, min=1, max=7),
            _f("blocked", "Blackout / workshop / renewal dates", "textarea", required=False,
               placeholder="15-16th Workshop service batch; 24-26th Festival peak (100% fleet locked)"),
        ],
        "prompt": """Build a Fleet Availability, Dispatch & Maintenance Schedule for {klass} ({subject}, {board}) from {from_date} to {to_date}, targeting {periods_week} billable days/week per vehicle.

Vehicles & commitments:
{chapters}

Workshop / blackout dates: {blocked}

Allocate each vehicle across active rental days, preventive maintenance windows, and statutory renewals while keeping at least 10-12% reserve/buffer capacity for breakdowns or VIP extensions.

Provide a clean Markdown table (for Excel export): Week / Date Window, Vehicle Plate & Model, Assigned Booking / Service Status, Billable Days, Maintenance / Renewal Action, and Standby Buffer Status. Flag clearly if demand exceeds available fleet.

Create it as an Excel file named "{klass} {subject} fleet schedule".""",
    },
    {
        "id": "analysis",
        "group": "Billing & Claims",
        "name": "Fleet revenue & utilization analysis",
        "blurb": "Paste vehicle earnings, utilization days or inspection scores; get instant profit & fleet insights.",
        "icon": "analysis",
        "fields": [
            _CLASS, _SUBJECT,
            _f("data", "Paste vehicle metrics (Name/Plate, Days Rented, Revenue, Inspection Score)", "textarea", rows=10,
               placeholder="Vehicle, Utilization(30), RevenueScore(100), Condition(10)\nCreta-1234, 26, 92, 9\nInnova-5678, 28, 96, 8\nSwift-9012, 14, 48, 6"),
            _f("topics", "What each column measures", "textarea", required=False,
               placeholder="Q1 Days rented out of 30, Q2 Revenue target %, Q3 Vehicle condition score"),
        ],
        "prompt": """Analyse these fleet performance and utilization figures for {klass} ({subject}).

{data}

Float has already calculated the exact summary statistics in Python above. Use those numbers exactly as given and do NOT recalculate averages, spreads, or percentages.

Metric definitions: {topics}

Give me:
1. Fleet average performance and spread across the group.
2. Which metric/category the fleet underperformed on most, and the operational reason (pricing, downtime, or seasonal demand).
3. Underperforming vehicles (more than 1 SD below average) listed by name/plate, with a specific action for each (reprice, workshop overhaul, or rotate to corporate lease).
4. High-earning / high-utilization vehicles that need preventive maintenance priority so they don't burn out.
5. One crisp paragraph on how to lift fleet utilization and net rev-per-car next week.""",
    },
    {
        "id": "notice",
        "group": "Customer Comms",
        "name": "Branch & driver notice",
        "blurb": "Official rental agency circular or SOP notice for drivers, counter staff or corporate clients.",
        "icon": "notice",
        "kind": "docx",
        "fields": [
            _f("about", "What the notice is about", "textarea",
               placeholder="Mandatory 360-degree video recording + FASTag balance check before every self-drive handover"),
            _f("audience", "For", "select",
               options=["All Chauffeurs & Drivers", "Rental Desk & Yard Staff", "Corporate Fleet Clients", "Self-Drive Customers", "All Branches"]),
            _f("tone", "Tone", "select", options=["Formal SOP", "Friendly Operational", "Urgent Compliance"]),
            _f("from_who", "Issued by", "text", placeholder="Fleet Operations Manager"),
        ],
        "prompt": """Write an official rental agency operational notice/circular for {audience} regarding: {about}. Tone: {tone}. Issued by: {from_who}.

Format cleanly with: Agency Header, "OPERATIONAL NOTICE / CIRCULAR", Reference No., Date, Subject Line, numbered action points stating clearly what must be done at the counter/lot and from when, and signature block.

Create it as a Word file.""",
    },
    {
        "id": "letter",
        "group": "Billing & Claims",
        "name": "Insurance, RTO or vendor letter",
        "blurb": "Formal letter for insurance claims, RTO permits/NOC, corporate billing or police intimation.",
        "icon": "letter",
        "kind": "docx",
        "fields": [
            _f("purpose", "Letter type", "select",
               options=["Motor Insurance Own-Damage Claim Intimation", "RTO Tourist Permit / Fitness / NOC Request",
                        "Corporate Overdue Invoice Demand", "Police Station Incident / Missing Vehicle Intimation",
                        "Authorized Workshop Repair & Estimate Approval", "Corporate Fleet Empanelment Letter", "Other"]),
            _f("detail", "Vehicle plate, policy/invoice ref, dates & facts", "textarea",
               placeholder="Vehicle MH-02-AB-4589, Policy #OG-26-1902-1805, minor rear bumper impact on NH-48 on 14 Oct, estimate ₹14,500"),
            _f("from_who", "Your name, designation & agency name", "text",
               placeholder="Vikram Khanna, Fleet Manager — Apex Car Rentals"),
        ],
        "prompt": """Write a formal official business letter. Purpose: {purpose}.
Specific details: {detail}. From: {from_who}.

Use standard commercial/official format: To block, Date, Reference/Policy/Vehicle Registration Number in the Subject line, clear factual paragraphs stating the exact request, enclosures/documents attached list (RC, DL, Rental Agreement, FIR/Photos if applicable), and authorised signatory block.

Create it as a Word file.""",
    },
    {
        "id": "slides",
        "group": "Bookings & Quotes",
        "name": "Corporate fleet pitch deck",
        "blurb": "Slide-by-slide B2B proposal for companies, hotels or events needing monthly cars & transfers.",
        "icon": "slides",
        "kind": "docx",
        "fields": [
            _CLASS, _SUBJECT, _TOPIC,
            _f("count", "Number of slides", "number", value=8, min=4, max=20),
        ],
        "prompt": """Create a {count}-slide B2B Corporate Fleet & Mobility Pitch Deck for {topic} ({subject}, {klass}).

For each slide provide:
- Slide Title
- At most 4 punchy, metric-backed bullet points (fleet reliability, average vehicle age, 24x7 replacement vehicle SLA, GPS/panic-button safety, GST-compliant consolidated monthly billing)
- Presenter talking points (2–3 crisp sentences)
- Suggested visual or rate comparison table to show on screen.

Slide 1 opens with the client's mobility pain point & cost-saving hook; the final slide is a clear pilot proposal & SLA sign-off.

Create it as a Word file named "{topic} corporate pitch deck" with one section per slide.""",
    },
    {
        "id": "seating",
        "group": "Desk & Handover",
        "name": "Driver & vehicle dispatch roster",
        "blurb": "Assign vehicles and chauffeurs to shifts, airport runs or outstation trips cleanly.",
        "icon": "seating",
        "fields": [
            _CLASS,
            _f("students", "Vehicles / Drivers (or leave blank to pull from your registered Fleet group)", "textarea", required=False,
               placeholder="MH-02-AB-1234 Creta · Ramesh\nMH-02-CD-5678 Innova · Suresh\nMH-02-EF-9012 Dzire · Mahesh"),
            _f("size", "Vehicles per shift / bay pod", "number", value=4, min=1, max=15),
            _f("basis", "Dispatch rule", "select",
               options=["Balance odometer km across fleet", "Airport Morning / Evening Shift Split",
                        "Match VIP Chauffeurs to Luxury/Corporate", "Keep backup standby vehicle per pod", "Outstation vs Local City Split"]),
        ],
        "prompt": """Build a Driver & Vehicle Dispatch Roster in pods/shifts of {size} for {klass}, optimised by: {basis}.
Vehicles / Drivers provided: {students}

If no list was given, call `look_up_class` for {klass} first.

Present the dispatch roster as a clean table: Pod / Shift Slot, Vehicle & Plate, Assigned Driver / Renter, Primary Duty (Airport / Local / Outstation / Standby), and Pre-Dispatch Check. Add one operational note on which vehicle is designated as the instant replacement standby.""",
    },
    {
        "id": "doubt",
        "group": "Customer Comms",
        "name": "Resolve a rental dispute",
        "blurb": "Fair policy breakdown + calm counter script for scratch disputes, fuel, tolls or late returns.",
        "icon": "doubt",
        "fields": [
            _CLASS, _SUBJECT,
            _f("question", "What the customer is disputing", "textarea", rows=5,
               placeholder="Customer says the front bumper scratch was already there at night pickup and refuses to pay ₹2,500 deduction from deposit."),
            _f("level", "Customer profile", "select",
               options=["First-time retail renter (upset at counter)", "High-value repeat / VIP customer", "Corporate account admin / travel desk"]),
        ],
        "prompt": """A {subject} ({klass}) customer is disputing: {question}
Customer profile: {level}.

Give me:
1. Immediate 3-step verification check for the desk agent (check-out timestamped photos/video, signed handover sheet, FASTag/GPS log).
2. Fair commercial resolution options (Option A: full policy enforcement if proof is solid; Option B: 50% goodwill split / polish-only charge; Option C: VIP waiver with future booking credit) — with the exact rupee impact of each.
3. Word-for-word calm counter script the desk agent can say right now to de-escalate without losing authority.
4. A 3-line written settlement confirmation to send on WhatsApp once agreed.""",
    },
    {
        "id": "assembly",
        "group": "Desk & Handover",
        "name": "Morning shift briefing",
        "blurb": "2-minute counter & yard team huddle covering today's pickups, returns and priorities.",
        "icon": "assembly",
        "fields": [
            _f("occasion", "Today's focus / peak event", "text",
               placeholder="Long weekend rush — 18 self-drive check-outs + 6 airport VIP arrivals"),
            _f("speaker", "Led by", "select",
               options=["Branch / Station Manager", "Lead Dispatch Executive", "Fleet Yard Supervisor"]),
            _CLASS,
            _f("minutes", "Briefing length (minutes)", "number", value=2, min=1, max=10),
        ],
        "prompt": """Write a {minutes}-minute morning shift huddle briefing for {occasion}, delivered by the {speaker} to the {klass} counter, yard, and driver team.

Keep sentences punchy and action-oriented:
1. Today's numbers & peak pickup/return windows.
2. Top 3 non-negotiables on the lot today (360° handover photos, fuel & FASTag check, zero-delay VIP arrivals).
3. One specific recognition or safety reminder for the team.

Mark natural pauses for team confirmation.""",
    },
    {
        "id": "hpc",
        "group": "Fleet & Maintenance",
        "name": "Vehicle health & audit report",
        "blurb": "360° multi-domain vehicle dossier covering mechanicals, body/cabin, unit economics & compliance.",
        "icon": "holistic",
        "kind": "docx",
        "fields": [
            _CLASS,
            _f("student", "Vehicle plate & model", "text", placeholder="MH-02-AB-4589 · Hyundai Creta SX (48,200 km)"),
            _f("observations", "Service logs, condition notes & earnings history", "textarea", rows=6,
               placeholder="48,200 km on odo. Front tyres at 35% tread. Earned ₹78,000 last month (24 days billed). Minor AC cooling lag in peak afternoon. Insurance valid till Dec."),
            _f("domains", "Audit scope", "select",
               options=["Mechanical + Exterior/Cabin + Unit Economics + Compliance", "Mechanical & Safety Only",
                        "Revenue, Cost-per-Km & Hold/Sell Decision"]),
        ],
        "prompt": """Write a comprehensive Vehicle Health, Compliance & Unit Economics Audit Report for {student} ({klass}), covering: {domains}.

Logged observations & history: {observations}

For each audit domain:
- Clear factual assessment based on the logged observations (never invent service history not provided).
- Immediate workshop or compliance action required before the next long trip, with estimated cost/downtime.
- Fleet Manager Recommendation: Keep in Prime Self-Drive Fleet, Reassign to Local/City Tier, Send for Preventive Overhaul, or Flag for Resale/Replacement.

Create it as a Word file named "{student} — vehicle health report".""",
    },
]

TOOLKIT_GROUPS = [
    "Bookings & Quotes",
    "Desk & Handover",
    "Fleet & Maintenance",
    "Billing & Claims",
    "Customer Comms",
]

_TOOLKIT_ALIASES = {
    "rental-agreement": "lesson-plan",
    "lesson_plan": "lesson-plan",
    "handover-checklist": "question-paper",
    "question_paper": "question-paper",
    "rate-card": "worksheet",
    "instant-quote": "worksheet",
    "damage-assessment": "marking",
    "inspection-standard": "rubric",
    "booking-notes": "remarks",
    "customer-message": "parent-message",
    "parent_message": "parent-message",
    "driver-briefing": "bilingual",
    "promo-campaign": "activity",
    "fleet-recovery": "remedial",
    "fleet-schedule": "pacing",
    "fleet-analytics": "analysis",
    "ops-circular": "notice",
    "official-letter": "letter",
    "corporate-pitch": "slides",
    "dispatch-roster": "seating",
    "policy-advisor": "doubt",
    "shift-huddle": "assembly",
    "vehicle-health": "hpc",
}


def toolkit_entry(entry_id: str) -> dict[str, Any] | None:
    norm = _TOOLKIT_ALIASES.get(entry_id, entry_id)
    for entry in TOOLKIT:
        if entry["id"] == norm:
            return entry
    return None


def fill_prompt(entry: dict[str, Any], values: dict[str, Any]) -> str:
    prompt = entry["prompt"]
    if entry["id"] == "analysis":
        # Numbers come from Python, not the model. MarksError carries a plain message.
        values = dict(values)
        values["data"] = stats.analyse(str(values.get("data", "")))
    for field in entry["fields"]:
        key = field["key"]
        raw = values.get(key, "")
        text = str(raw).strip() or ("not specified" if field.get("required") is not False else "—")
        prompt = prompt.replace("{" + key + "}", text)
    # Any placeholder the form did not cover.
    for key, value in values.items():
        prompt = prompt.replace("{" + str(key) + "}", str(value))
    return prompt

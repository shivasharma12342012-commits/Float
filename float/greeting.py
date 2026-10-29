"""Float — the line the rental operator sees first.

A greeting is worth writing properly because it is the first thing the rental desk
or fleet manager reads on every shift. Three rules it follows:

*It is built from their shift, not from a generic list.* The time, the weekday,
what pickup or return slot is coming up in the next hour, and what ops tasks are
still open. "Good morning" is not operational; "Airport SUV Pickup starts in 20
minutes — Bay 2" is.

*It costs nothing.* No model call, no network. It is assembled locally in about a
millisecond, so the window is useful before anything has loaded.

*It says one thing.* A greeting, then at most one operational fact, then at most
one nudge.
"""

from __future__ import annotations

import datetime as dt
import random
from typing import Any

from . import db

SALUTATIONS = {
    "en": {"morning": "Good morning", "afternoon": "Good afternoon", "evening": "Good evening"},
    "hi": {"morning": "सुप्रभात", "afternoon": "नमस्कार", "evening": "शुभ संध्या"},
    "bn": {"morning": "শুভ সকাল", "afternoon": "নমস্কার", "evening": "শুভ সন্ধ্যা"},
    "mr": {"morning": "शुभ सकाळ", "afternoon": "नमस्कार", "evening": "शुभ संध्याकाळ"},
    "ta": {"morning": "காலை வணக்கம்", "afternoon": "வணக்கம்", "evening": "மாலை வணக்கம்"},
    "te": {"morning": "శుభోదయం", "afternoon": "నమస్కారం", "evening": "శుభ సాయంత్రం"},
    "gu": {"morning": "સુપ્રભાત", "afternoon": "નમસ્તે", "evening": "શુભ સંધ્યા"},
    "kn": {"morning": "ಶುಭೋದಯ", "afternoon": "ನಮಸ್ಕಾರ", "evening": "ಶುಭ ಸಂಜೆ"},
    "ml": {"morning": "സുപ്രഭാതം", "afternoon": "നമസ്കാരം", "evening": "ശുഭ സായാഹ്നം"},
    "pa": {"morning": "ਸ਼ੁਭ ਸਵੇਰ", "afternoon": "ਸਤ ਸ੍ਰੀ ਅਕਾਲ", "evening": "ਸ਼ੁਭ ਸ਼ਾਮ"},
    "or": {"morning": "ଶୁଭ ସକାଳ", "afternoon": "ନମସ୍କାର", "evening": "ଶୁଭ ସନ୍ଧ୍ୟା"},
    "as": {"morning": "শুভ ৰাতিপুৱা", "afternoon": "নমস্কাৰ", "evening": "শুভ সন্ধিয়া"},
    "ur": {"morning": "صبح بخیر", "afternoon": "السلام علیکم", "evening": "شام بخیر"},
}


LINES = {
    "morning": (
        "Keys on the hook, {name}. Ready for today's pickups?",
        "Lot is ready, {name}. Let's roll.",
        "Coffee and Float time, {name}?",
        "Bright and early at the desk, {name}.",
        "First handovers coming up, {name}.",
        "Let's keep the fleet moving today, {name}.",
        "Morning, {name}. Which vehicles are heading out first?",
    ),
    "afternoon": (
        "Midday turnaround time, {name}?",
        "Peak counter hours, {name}. Need a fast quote or agreement?",
        "Fleet moving smoothly, {name}?",
        "Take a breath, {name}. What's checking in next?",
        "Afternoon shift, {name}. Ready for the next handover?",
        "Halfway through today's dispatches, {name}.",
    ),
    "evening": (
        "Evening returns rolling in, {name}?",
        "Closing out today's trips or lining up tomorrow, {name}?",
        "Winding down the counter, {name}?",
        "Let's lock in tomorrow's fleet schedule tonight, {name}.",
        "Good evening, {name}. One last booking or invoice?",
    ),
    "night": (
        "Night desk or late airport transfer, {name}?",
        "Still on shift, {name}? Let's get it done in seconds.",
        "Late-night fleet check, {name}?",
    ),
}

DAY_LINES = {
    0: ("Monday rush, {name}. Corporate and airport fleet ready.",),
    4: ("It's Friday, {name}. Weekend self-drive rush is here.",),
    5: ("Saturday peak on the lot, {name}. Let's move keys fast.",),
    6: ("Sunday returns and turnaround, {name}. Smooth handovers ahead.",),
}

WEEKDAYS = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")

OPENERS = (
    "What do you need — a quote, contract, checklist, or message?",
    "Which vehicle or booking are we handling?",
    "What's first on the desk today?",
    "Tell me what you need done in seconds.",
)


def _part_of_day(hour: int) -> str:
    if hour >= 22 or hour < 4:
        return "night"
    if hour < 12:
        return "morning"
    if hour < 17:
        return "afternoon"
    return "evening"


def _first_name(name: str) -> str:
    name = (name or "").strip()
    if not name:
        return ""
    parts = [p for p in name.replace(".", " ").split() if p]
    honorifics = {"mr", "mrs", "ms", "miss", "dr", "prof", "shri", "smt", "sir", "madam"}
    if not parts:
        return ""
    for part in parts:
        if part.lower().strip(".") not in honorifics:
            return part
    return parts[-1]


def _parse_clock(value: str) -> dt.time | None:
    if not value or not str(value).strip():
        return None
    for fmt in ("%H:%M", "%I:%M %p", "%I:%M%p", "%H.%M"):
        try:
            return dt.datetime.strptime(value.strip(), fmt).time()
        except ValueError:
            continue
    return None


def next_period(user_id: int, now: dt.datetime | None = None) -> dict[str, Any] | None:
    """The operator's next scheduled pickup/return slot today, if there is one."""
    now = now or dt.datetime.now()
    weekday = now.weekday()
    rows = db.list_periods(user_id, weekday)
    best: tuple[int, dict[str, Any]] | None = None
    for row in rows:
        start = _parse_clock(row["starts"])
        if start is None:
            continue
        starts_at = dt.datetime.combine(now.date(), start)
        minutes = int((starts_at - now).total_seconds() // 60)
        if -5 <= minutes <= 180 and (best is None or minutes < best[0]):
            best = (minutes, {**row, "in_minutes": minutes})
    return best[1] if best else None


def build(user: dict[str, Any], now: dt.datetime | None = None) -> dict[str, Any]:
    """Return ``{headline, detail, opener, period, tone}``."""
    now = now or dt.datetime.now()
    name = _first_name(user.get("name", ""))
    language = user.get("language", "en")
    part = _part_of_day(now.hour)
    if language in SALUTATIONS and language != "en":
        salutation = SALUTATIONS[language].get(part, SALUTATIONS[language]["evening"])
        headline = f"{salutation}, {name}." if name else f"{salutation}."
    else:
        pool = LINES[part] + DAY_LINES.get(now.weekday(), ())
        line = random.choice(pool)
        if name:
            headline = line.replace("{name}", name)
        else:
            headline = line.replace(", {name}", "").replace(" {name}", "").replace("{name}", "")

    detail = ""
    tone = "calm"
    period = next_period(int(user["id"]), now)

    if period:
        label = period.get("label") or "your next handover"
        minutes = period["in_minutes"]
        room = f" at {period['room']}" if period.get("room") else ""
        if minutes <= 0:
            detail = f"{label}{room} is due now."
            tone = "urgent"
        elif minutes <= 30:
            detail = f"{label}{room} in {minutes} minute{'s' if minutes != 1 else ''}."
            tone = "urgent"
        else:
            detail = f"Next slot: {label}{room} at {period['starts']}."

    if not detail:
        open_tasks = db.list_tasks(int(user["id"]))
        today = now.date().isoformat()
        due_today = [t for t in open_tasks if t["due"] and t["due"] <= today]
        if due_today:
            first = due_today[0]["title"]
            extra = len(due_today) - 1
            detail = f"Due today: {first}" + (f", and {extra} more." if extra else ".")
            tone = "urgent" if len(due_today) > 2 else "calm"
        elif open_tasks:
            detail = f"{len(open_tasks)} ops task{'s' if len(open_tasks) != 1 else ''} on your checklist."
        elif now.weekday() == 4 and now.hour >= 14:
            detail = "Friday afternoon — weekend fleet dispatches and check-outs ahead."
        elif now.weekday() >= 5:
            detail = f"It's {WEEKDAYS[now.weekday()]} — peak weekend fleet operations."
        elif user.get("sign_ins", 0) <= 1:
            detail = "Welcome to Float. Tell me about your fleet or ask for an instant quote, contract, or checklist."

    return {
        "headline": headline,
        "detail": detail,
        "opener": random.choice(OPENERS),
        "period": period,
        "tone": tone,
        "date": now.strftime("%A, %d %B"),
        "clock": now.strftime("%H:%M"),
    }


def week_reflection(user_id: int) -> str | None:
    """Friday's note about the operator's week."""
    now = dt.datetime.now()
    if now.weekday() != 4:
        return None
    summary = db.own_work_summary(user_id, days=7)
    if not summary["n"]:
        return None
    share = summary["own_share"]
    if share >= 50:
        return f"This week, {share}% of your agreements and messages were tailored in your own words. Sharp operations."
    if share >= 20:
        return f"This week you customised {share}% of your fleet drafts. Double-check any standard contracts before weekend dispatch."
    return "Most of this week's drafts went out close to standard template. Worth a quick review of rates and terms before weekend rush."

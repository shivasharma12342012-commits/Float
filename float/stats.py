"""Float — class statistics, calculated in Python (never by the AI).

The teacher pastes marks like::

    Name, Q1(5), Q2(5), Q3(10), Q4(10)
    Aarav, 4, 2, 7, 3
    Diya, 5, 5, 9, 8
    Kabir, AB, AB, AB, AB

``analyse`` parses that, computes with the ``statistics`` module, and returns
a block of text of exact numbers to put in the prompt. If the marks cannot be
understood it raises ``MarksError`` with a plain-language message instead of
guessing.
"""

from __future__ import annotations

import re
import statistics
from dataclasses import dataclass, field

ABSENT_WORDS = {"ab", "abs", "absent", "a", "-", "--", "na", "n/a", "x"}
_MAX_RE = re.compile(r"^(.*?)[\(\[]\s*(\d+(?:\.\d+)?)\s*[\)\]]\s*$")


class MarksError(ValueError):
    """The marks could not be parsed. The message is safe to show a teacher."""


@dataclass
class Student:
    name: str
    scores: list  # float | None per question (None = absent)
    total: float | None = None
    status: str = "ok"  # ok | absent | incomplete


@dataclass
class Analysis:
    questions: list
    maxes: list
    students: list
    problems: list = field(default_factory=list)


def _split(line: str) -> list:
    for sep in ("\t", "|", ";", ","):
        if sep in line:
            return [c.strip() for c in line.split(sep)]
    return line.split()


def _num(cell: str):
    try:
        v = float(str(cell).strip())
    except (ValueError, TypeError):
        return None
    return v if v == v and v not in (float("inf"), float("-inf")) else None


def _fmt(x: float) -> str:
    return f"{x:.2f}".rstrip("0").rstrip(".") if x == x else "n/a"


def parse(text: str) -> Analysis:
    lines = [ln for ln in (text or "").replace("\r", "").split("\n") if ln.strip()]
    if not lines:
        raise MarksError("No marks were entered. Paste one row per student, like: Aarav, 4, 2, 7, 3")
    rows = [_split(ln) for ln in lines]

    header = None
    if not any(_num(c) is not None for c in rows[0][1:]):
        header, rows = rows[0], rows[1:]
    if not rows:
        raise MarksError("I found a heading row but no students under it.")

    width = max(len(r) for r in rows) - 1
    if width < 1:
        raise MarksError("Each row needs a name and then at least one mark, separated by commas.")
    questions, maxes = [], []
    for i in range(width):
        label, mx = f"Q{i + 1}", None
        if header and i + 1 < len(header) and header[i + 1]:
            m = _MAX_RE.match(header[i + 1])
            label, mx = (m.group(1).strip() or label, float(m.group(2))) if m else (header[i + 1], None)
        questions.append(label)
        maxes.append(mx)

    out = Analysis(questions, maxes, [])
    for n, r in enumerate(rows, start=1):
        name, cells = (r[0] or f"Student {n}"), r[1:]
        if len(cells) != width:
            out.problems.append(f"{name}: has {len(cells)} marks but {width} were expected")
            continue
        scores, bad = [], None
        for q, c in enumerate(cells):
            if c.lower() in ABSENT_WORDS or c == "":
                scores.append(None)
                continue
            v = _num(c)
            if v is None:
                bad = f"{name}: '{c}' under {questions[q]} is not a number"
                break
            if v < 0 or (maxes[q] is not None and v > maxes[q]):
                bad = f"{name}: {_fmt(v)} under {questions[q]} is outside 0–{_fmt(maxes[q]) if maxes[q] else '?'}"
                break
            scores.append(v)
        if bad:
            out.problems.append(bad)
            continue
        s = Student(name, scores)
        if all(x is None for x in scores):
            s.status = "absent"
        elif any(x is None for x in scores):
            s.status = "incomplete"
        else:
            s.total = sum(scores)
        out.students.append(s)
    return out


def compute(a: Analysis) -> dict:
    scored = [s for s in a.students if s.status == "ok"]
    if not scored:
        raise MarksError("None of the rows had a complete set of marks I could use. " + "; ".join(a.problems[:5]))
    totals = [s.total for s in scored]
    mean = statistics.fmean(totals)
    sd = statistics.pstdev(totals)  # the class is the whole group, so population SD
    res = {"n": len(scored), "mean": mean, "median": statistics.median(totals),
           "high": max(totals), "low": min(totals), "sd": sd,
           "max_total": sum(a.maxes) if all(m is not None for m in a.maxes) else None}
    # Strictly more than one SD below the mean. If everyone scored alike (sd = 0) nobody is flagged.
    res["below"] = [s for s in scored if sd > 0 and s.total < mean - sd]
    res["threshold"] = mean - sd
    qs = []
    for i, label in enumerate(a.questions):
        got = [s.scores[i] for s in a.students if s.scores[i] is not None]
        mx = a.maxes[i]
        qs.append({"label": label, "max": mx, "n": len(got),
                   "avg": statistics.fmean(got) if got else None,
                   "pct": (100 * statistics.fmean(got) / mx) if got and mx else None})
    res["questions"] = qs
    ranked = [q for q in qs if q["pct"] is not None]
    res["hardest"] = min(ranked, key=lambda q: q["pct"]) if ranked else None
    res["easiest"] = max(ranked, key=lambda q: q["pct"]) if ranked else None
    res["careless"] = []
    if (res["hardest"] and res["easiest"] and res["hardest"] is not res["easiest"]
            and res["hardest"].get("max") and res["easiest"].get("max")):
        hi, ei = a.questions.index(res["hardest"]["label"]), a.questions.index(res["easiest"]["label"])
        for s in scored:
            if (s.scores[hi] / res["hardest"]["max"] >= 0.7) and (s.scores[ei] / res["easiest"]["max"] <= 0.5):
                res["careless"].append(s)
    return res


def analyse(text: str) -> str:
    """Parse + compute, and return the exact-figures block for the prompt."""
    a = parse(text)
    r = compute(a)
    L = ["CLASS FIGURES (calculated by Float in Python — exact; use them as given and do NOT recalculate):"]
    tot = f" out of {_fmt(r['max_total'])}" if r["max_total"] else ""
    L.append(f"- Students counted: {r['n']}")
    L.append(f"- Class average: {_fmt(r['mean'])}{tot}")
    L.append(f"- Median: {_fmt(r['median'])}")
    L.append(f"- Highest: {_fmt(r['high'])} · Lowest: {_fmt(r['low'])}")
    L.append(f"- Standard deviation (population): {_fmt(r['sd'])}")
    if r["sd"] == 0:
        L.append("- Everyone scored the same total, so the spread is zero and nobody is below one standard deviation.")
    elif len(a.students) and r["n"] == 1:
        L.append("- Only one student, so spread comparisons mean nothing.")
    L.append("- Per question (class average as % of marks available):")
    for q in r["questions"]:
        pct = f"{_fmt(q['pct'])}%" if q["pct"] is not None else "n/a (no maximum given in the heading)"
        L.append(f"    {q['label']}: {pct} ({q['n']} answered)")
    if r["hardest"]:
        L.append(f"- Worst question: {r['hardest']['label']} at {_fmt(r['hardest']['pct'])}%. "
                 f"Best: {r['easiest']['label']} at {_fmt(r['easiest']['pct'])}%.")
    if r["below"]:
        L.append(f"- More than one SD below the mean (total under {_fmt(r['threshold'])}): "
                 + "; ".join(f"{s.name} ({_fmt(s.total)})" for s in r["below"]))
    else:
        L.append("- Students more than one SD below the mean: none.")
    if r["careless"]:
        L.append("- Scored 70%+ on the worst question but 50% or less on the best: "
                 + ", ".join(s.name for s in r["careless"]))
    ab = [s.name for s in a.students if s.status == "absent"]
    inc = [s.name for s in a.students if s.status == "incomplete"]
    if ab:
        L.append("- Absent (left out of every figure above, not counted as zero): " + ", ".join(ab))
    if inc:
        L.append("- Missing some questions (left out of the totals): " + ", ".join(inc))
    if a.problems:
        L.append("- Rows Float could not use (tell the teacher): " + "; ".join(a.problems))
    L.append("")
    L.append("Each student's marks (" + ", ".join(a.questions) + "):")
    for s in a.students:
        cells = ", ".join("AB" if x is None else _fmt(x) for x in s.scores)
        L.append(f"  {s.name}: {cells}" + (f" = {_fmt(s.total)}" if s.total is not None else f" [{s.status}]"))
    return "\n".join(L)

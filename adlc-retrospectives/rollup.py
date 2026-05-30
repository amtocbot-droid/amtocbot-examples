"""Quarterly retrospective rollup: count contributing-factor tags across the
postmortem corpus and surface recurring factors (>= 3 incidents in quarter).

Companion code for the AmtocSoft post
"Postmortem Retrospective Cadence: Quarterly Cross-Incident Review,
Recurring Contributing Factors".

Tags are validated against a closed vocabulary (tags.md); an unknown tag is
a hard error so the corpus can't silently fragment. Pure standard library.
"""

from __future__ import annotations

import re
import sys
from collections import Counter
from datetime import date, timedelta
from pathlib import Path

BASE = Path(__file__).parent
PM_DIR = BASE / "postmortems" / "incidents"
TAG_FILE = BASE / "postmortems" / "tags.md"
TAG_RE = re.compile(r"^- contributing-factor-tag:\s*(?P<tag>[a-z0-9-]+)\s*$", re.M)
DATE_RE = re.compile(r"^date:\s*(?P<d>\d{4}-\d{2}-\d{2})\s*$", re.M)
RECURRENCE_THRESHOLD = 3


def load_known_tags() -> set[str]:
    text = TAG_FILE.read_text()
    return {m.group("tag") for m in re.finditer(r"^- `(?P<tag>[a-z0-9-]+)`", text, re.M)}


def quarter_bounds(today: date) -> tuple[date, date]:
    q_start_month = ((today.month - 1) // 3) * 3 + 1
    q_start = date(today.year, q_start_month, 1)
    q_end = (q_start + timedelta(days=95)).replace(day=1) - timedelta(days=1)
    return q_start, q_end


def rollup(today: date) -> list[tuple[str, int, list[str]]]:
    q_start, q_end = quarter_bounds(today)
    known = load_known_tags()
    counts: Counter[str] = Counter()
    sources: dict[str, list[str]] = {}
    for pm in sorted(PM_DIR.glob("*.md")):
        text = pm.read_text()
        d_match = DATE_RE.search(text)
        if not d_match:
            continue
        d = date.fromisoformat(d_match.group("d"))
        if not (q_start <= d <= q_end):
            continue
        for tm in TAG_RE.finditer(text):
            tag = tm.group("tag")
            if tag not in known:
                raise ValueError(f"{pm.name}: unknown tag '{tag}' (add to {TAG_FILE})")
            counts[tag] += 1
            sources.setdefault(tag, []).append(pm.name)
    return [(tag, n, sources[tag]) for tag, n in counts.most_common()
            if n >= RECURRENCE_THRESHOLD]


if __name__ == "__main__":
    today = date(2026, 5, 30)
    q_start, q_end = quarter_bounds(today)
    print(f"Recurring contributing factors {q_start} .. {q_end}:")
    rows = rollup(today)
    for tag, n, src in rows:
        print(f"  {tag:<22} x{n}   {', '.join(src)}")
    if not rows:
        print("  (none crossed the recurrence threshold)")
    sys.exit(0)

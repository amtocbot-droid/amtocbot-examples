"""Runbook linter: enforce the sixty-second-triage structure.

Companion code for the AmtocSoft post
"ADLC On-Call Runbook Structure: Sixty-Second Triage, Entry, Three-Stage Map".

Every runbook must have five sections in a fixed order, a short human
headline (no metric names), and a deterministic rollback gate (no
aspirational language like "consider" / "maybe"). The post runs these as
pytest; here they're plain asserts so the example needs no dependencies.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

RUNBOOKS = Path(__file__).parent / "runbooks"
REQUIRED_SECTIONS = ["HEADLINE", "FIRST CHECK", "SECOND CHECK",
                     "ROLLBACK GATE", "ESCALATE"]
ASPIRATIONAL = re.compile(r"\b(consider|maybe|might want to|could)\b", re.I)


def runbook_files() -> list[Path]:
    return sorted(RUNBOOKS.rglob("*.md"))


def check_sections_present_and_ordered(text: str) -> None:
    positions = [text.find(f"**{s}:**") for s in REQUIRED_SECTIONS]
    assert all(p >= 0 for p in positions), "missing a required section"
    assert positions == sorted(positions), "sections out of order"


def check_headline_short_and_human(text: str) -> None:
    m = re.search(r"\*\*HEADLINE:\*\*\s*(.+)", text)
    assert m, "no headline"
    words = m.group(1).strip().split()
    assert len(words) <= 15, "headline too long"
    assert not re.search(r"\bagent_\w+", m.group(1)), "metric name in headline"


def check_rollback_deterministic(text: str) -> None:
    m = re.search(r"\*\*ROLLBACK GATE:\*\*([\s\S]+?)\*\*ESCALATE", text)
    assert m, "no rollback gate"
    assert not ASPIRATIONAL.search(m.group(1)), "aspirational language in rollback"


def lint_all() -> int:
    files = runbook_files()
    assert files, "no runbook files found"
    for rb in files:
        text = rb.read_text()
        check_sections_present_and_ordered(text)
        check_headline_short_and_human(text)
        check_rollback_deterministic(text)
        print(f"ok  {rb.name}")
    return len(files)


if __name__ == "__main__":
    n = lint_all()
    print(f"\n{n} runbook(s) pass the structure lint.")
    sys.exit(0)

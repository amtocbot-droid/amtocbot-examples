"""Postmortem compliance linter: required fields, follow-ups with artefacts,
and follow-up due dates within SLA.

Companion code for the AmtocSoft post
"ADLC Postmortem Template: From Runbook Miss to Runbook Fix".

The post runs these as pytest with a yaml frontmatter parser; this version
parses frontmatter with the standard library so it has zero dependencies.
"""

from __future__ import annotations

import re
import sys
from datetime import date, timedelta
from pathlib import Path

PM_DIR = Path(__file__).parent / "postmortems"

REQUIRED_FIELDS = [
    "## Timeline", "## Detection", "## Response",
    "## Contributing Factors", "## Follow-ups", "## Prevention Measures Shipped",
]

FOLLOWUP_RE = re.compile(
    r"^- \[(?P<status>[ x])\] (?P<action>[^|]+?) "
    r"\| owner: @(?P<owner>\S+) "
    r"\| due: (?P<due>\d{4}-\d{2}-\d{2}) "
    r"\| (?:PR|ticket): (?P<artefact>\S+)$",
    re.MULTILINE,
)
CONTRIB_RE = re.compile(r"^- (?P<text>.+?) — .+", re.MULTILINE)
SLA_DAYS = 14


def frontmatter(text: str) -> dict:
    m = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    fm = {}
    if m:
        for line in m.group(1).splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                fm[k.strip()] = v.strip()
    return fm


def section(text: str, header: str) -> str:
    idx = text.find(header)
    if idx < 0:
        return ""
    rest = text[idx + len(header):]
    nxt = re.search(r"^## ", rest, re.MULTILINE)
    return rest[:nxt.start()] if nxt else rest


def check_required_fields(text: str) -> None:
    last = -1
    for header in REQUIRED_FIELDS:
        idx = text.find(header)
        assert idx > last, f"missing or out-of-order: {header}"
        last = idx


def check_followups_have_artefacts(text: str) -> None:
    matches = list(FOLLOWUP_RE.finditer(section(text, "## Follow-ups")))
    assert matches, "no well-formed follow-ups found"
    for m in matches:
        a = m.group("artefact")
        assert a.startswith(("#", "PR", "TICKET-")), \
            f"follow-up missing artefact: {m.group('action').strip()}"


def check_followups_within_sla(text: str) -> None:
    incident = date.fromisoformat(frontmatter(text)["incident_date"])
    for m in FOLLOWUP_RE.finditer(section(text, "## Follow-ups")):
        due = date.fromisoformat(m.group("due"))
        assert due - incident <= timedelta(days=SLA_DAYS), \
            f"follow-up due date beyond {SLA_DAYS}-day SLA: {m.group('action').strip()}"


def lint_all() -> int:
    files = sorted(PM_DIR.glob("*.md"))
    assert files, "no postmortems found"
    for pm in files:
        text = pm.read_text()
        check_required_fields(text)
        check_followups_have_artefacts(text)
        check_followups_within_sla(text)
        print(f"ok  {pm.name}")
    return len(files)


if __name__ == "__main__":
    n = lint_all()
    print(f"\n{n} postmortem(s) pass compliance lint.")
    sys.exit(0)

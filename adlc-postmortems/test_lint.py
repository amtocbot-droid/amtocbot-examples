"""Tests. Run: python3 test_lint.py"""

from __future__ import annotations

from lint import (
    lint_all, frontmatter, section, check_required_fields,
    check_followups_have_artefacts, check_followups_within_sla,
)

PM_DIR = __import__("lint").PM_DIR
GOOD = (PM_DIR / "PM-2026-03-12-tool-timeout.md").read_text()


def test_real_postmortem_passes():
    assert lint_all() >= 1


def test_frontmatter_parsed():
    assert frontmatter(GOOD)["incident_date"] == "2026-03-12"


def test_section_extraction():
    assert "lookup_order" in section(GOOD, "## Timeline")


def test_missing_field_rejected():
    bad = GOOD.replace("## Detection", "## Detektion")
    try:
        check_required_fields(bad)
    except AssertionError:
        return
    raise AssertionError("should reject missing field")


def test_followup_without_artefact_rejected():
    bad = GOOD.replace("| PR: #4821", "| PR: soon")
    try:
        check_followups_have_artefacts(bad)
    except AssertionError:
        return
    raise AssertionError("should reject follow-up without real artefact")


def test_followup_past_sla_rejected():
    bad = GOOD.replace("due: 2026-03-14", "due: 2026-09-14")
    try:
        check_followups_within_sla(bad)
    except AssertionError:
        return
    raise AssertionError("should reject follow-up past SLA")


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"ok  {name}")
    print("\nall tests passed")

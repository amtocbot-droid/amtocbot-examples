"""Tests for the run summarizer. Run: python test_summarize.py"""

from __future__ import annotations

from summarize_runs import fmt_duration, load_runs, parse_duration, summarize


def test_parse_duration_minutes_seconds():
    assert parse_duration("8m12s") == 492
    assert parse_duration("10m05s") == 605


def test_parse_duration_plain_seconds():
    assert parse_duration("90s") == 90


def test_fmt_duration_roundtrips():
    assert fmt_duration(492) == "8m12s"
    assert fmt_duration(605) == "10m05s"


def test_summarize_ranks_by_corrections_then_time():
    runs = load_runs([
        "results/claude-code.json",
        "results/cursor.json",
        "results/copilot.json",
        "results/windsurf.json",
    ])
    out = summarize(runs)
    lines = out.splitlines()[1:]  # drop header
    order = [ln.split()[0] + " " + ln.split()[1] for ln in lines]
    # Claude Code (0 corrections) ranks first; Windsurf (2) last.
    assert order[0].startswith("Claude")
    assert order[-1].startswith("Windsurf")


def test_copilot_after_cursor_on_tie_by_time():
    # Cursor and Copilot both have 1 correction; Cursor is faster, ranks first.
    runs = load_runs(["results/cursor.json", "results/copilot.json"])
    out = summarize(runs)
    body = out.splitlines()[1:]
    assert body[0].startswith("Cursor")
    assert body[1].startswith("Copilot")


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"ok  {name}")
    print("\nall tests passed")

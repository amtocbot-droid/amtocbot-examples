"""Tests. Run: python3 test_lint_runbooks.py"""

from __future__ import annotations

from lint_runbooks import (
    lint_all, check_sections_present_and_ordered, check_headline_short_and_human,
    check_rollback_deterministic,
)

GOOD = ("**HEADLINE:** Short human line.\n**FIRST CHECK:** a\n"
        "**SECOND CHECK:** b\n**ROLLBACK GATE:** revert now if X.\n"
        "**ESCALATE:** page team.")


def test_real_runbooks_pass():
    assert lint_all() >= 2


def test_out_of_order_rejected():
    bad = ("**FIRST CHECK:** a\n**HEADLINE:** x\n**SECOND CHECK:** b\n"
           "**ROLLBACK GATE:** revert\n**ESCALATE:** page")
    try:
        check_sections_present_and_ordered(bad)
    except AssertionError:
        return
    raise AssertionError("should have rejected out-of-order sections")


def test_aspirational_rollback_rejected():
    bad = GOOD.replace("revert now if X.", "consider reverting maybe.")
    try:
        check_rollback_deterministic(bad)
    except AssertionError:
        return
    raise AssertionError("should have rejected aspirational rollback")


def test_long_headline_rejected():
    bad = "**HEADLINE:** " + " ".join(["word"] * 20) + "\n"
    try:
        check_headline_short_and_human(bad)
    except AssertionError:
        return
    raise AssertionError("should have rejected long headline")


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"ok  {name}")
    print("\nall tests passed")

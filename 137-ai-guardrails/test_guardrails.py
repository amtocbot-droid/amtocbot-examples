"""Tests. Run: python3 test_guardrails.py"""

from __future__ import annotations

from guardrails import (
    fix_pii, gibberish_score, validate_input, check_grounding, ValidationError,
    GuardConfig,
)


def test_pii_redacted():
    assert fix_pii("call 415-555-0142 or a@b.com") == "call <PHONE> or <EMAIL>"


def test_gibberish_high_for_mash():
    assert gibberish_score("zxcvbn qwrtp bcdfg") > 0.8


def test_gibberish_low_for_prose():
    assert gibberish_score("the quick brown fox jumps over the lazy dog") < 0.3


def test_input_too_short_rejected():
    try:
        validate_input("hi")
    except ValidationError:
        return
    raise AssertionError("short input should be rejected")


def test_input_pii_fixed_on_pass():
    out = validate_input("please email me at a@b.com about my account today")
    assert "<EMAIL>" in out


def test_grounding_supported():
    ctx = "The cat sat on the mat in the kitchen."
    assert check_grounding(ctx, "The cat sat on the mat.")["verdict"] == "SUPPORTED"


def test_grounding_unsupported():
    ctx = "The cat sat on the mat."
    r = check_grounding(ctx, "The dog flew to the moon yesterday.")
    assert r["verdict"] == "UNSUPPORTED"


def test_grounding_partial():
    ctx = "The cat sat on the mat in the kitchen."
    r = check_grounding(ctx, "The cat sat on the mat. The dog flew to mars.")
    assert r["verdict"] == "PARTIAL"


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"ok  {name}")
    print("\nall tests passed")

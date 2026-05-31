"""Tests. Run: python3 test_judge.py"""

from __future__ import annotations

from judge import judge_pair, cohens_kappa, _raw_verdict


def test_clear_winner_wins():
    q = "how do I reset my password"
    good = "Go to settings and reset your password."
    bad = "Passwords are a security topic with much history and nuance here."
    assert judge_pair(q, good, bad) == "A"
    assert judge_pair(q, bad, good) == "B"


def test_true_tie_is_tie():
    q = "how do I reset my password"
    a = "Go to settings and reset your password."
    b = "Open settings, then reset your password."
    assert judge_pair(q, a, b) == "TIE"


def test_position_bias_visible_in_raw_verdict():
    q = "reset password"
    a = "go to settings reset password"
    b = "open settings reset password"
    # raw verdict can be swayed by order; mitigated verdict should not be
    raw_ab = _raw_verdict(q, a, b)
    raw_ba = _raw_verdict(q, b, a)
    if raw_ab != "TIE" or raw_ba != "TIE":
        assert judge_pair(q, a, b) == "TIE"


def test_kappa_perfect_agreement():
    assert cohens_kappa(["A", "B", "TIE"], ["A", "B", "TIE"]) == 1.0


def test_kappa_below_one_on_disagreement():
    k = cohens_kappa(["A", "B", "A", "B"], ["A", "B", "B", "A"])
    assert k < 1.0


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"ok  {name}")
    print("\nall tests passed")

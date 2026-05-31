"""Tests. Run: python3 test_oversight.py"""

from __future__ import annotations

from oversight import (
    DecisionTrace, RiskClass, classify_risk, route_decision, ReviewQueue,
    Verdict, REFUSAL,
)


def test_low_confidence_is_high_risk():
    assert classify_risk(DecisionTrace("d", confidence_score=0.5)) == RiskClass.HIGH


def test_mid_confidence_is_elevated():
    assert classify_risk(DecisionTrace("d", confidence_score=0.72)) == RiskClass.ELEVATED


def test_high_confidence_is_standard():
    assert classify_risk(DecisionTrace("d", confidence_score=0.95)) == RiskClass.STANDARD


def test_explicit_high_overrides():
    assert classify_risk(DecisionTrace("d", risk_class="high",
                                       confidence_score=0.99)) == RiskClass.HIGH


def test_high_fails_closed_without_approval():
    q = ReviewQueue()
    out = route_decision(DecisionTrace("d", confidence_score=0.4), "x", q,
                         sample=lambda: 1.0)
    assert out == REFUSAL and q.blocking


def test_high_delivers_with_approval():
    q = ReviewQueue()
    q.set_verdict("d", Verdict(approved=True))
    out = route_decision(DecisionTrace("d", confidence_score=0.4), "x", q,
                         sample=lambda: 1.0)
    assert out == "x"


def test_elevated_queues_async():
    q = ReviewQueue()
    route_decision(DecisionTrace("d", confidence_score=0.72), "x", q, sample=lambda: 1.0)
    assert q.async_queue and q.async_queue[0][1] == 24


def test_standard_samples_for_review():
    q = ReviewQueue()
    route_decision(DecisionTrace("d", confidence_score=0.95), "x", q, sample=lambda: 0.01)
    assert q.async_queue and q.async_queue[0][1] == 72


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"ok  {name}")
    print("\nall tests passed")

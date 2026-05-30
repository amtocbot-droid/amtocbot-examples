"""Tests. Run: python3 test_eval_contracts.py"""

from __future__ import annotations

from eval_contracts import (
    kl_divergence, customer_support_contract, avg_quality,
    tool_call_distribution, refusal_rate,
)
from run import BASELINE, CANDIDATE


def test_kl_zero_for_identical():
    p = {"a": 0.5, "b": 0.5}
    assert kl_divergence(p, p) < 1e-9


def test_kl_positive_for_divergent():
    assert kl_divergence({"a": 0.9, "b": 0.1}, {"a": 0.1, "b": 0.9}) > 0.5


def test_metrics_basic():
    traces = [{"quality": 1.0, "refused": False, "tool_calls": [{"tool": "x"}]},
              {"quality": 0.0, "refused": True, "tool_calls": []}]
    assert avg_quality(traces) == 0.5
    assert refusal_rate(traces) == 0.5
    assert tool_call_distribution(traces) == {"x": 1.0}


def test_identical_candidate_passes():
    c = customer_support_contract(BASELINE)
    assert c.passed(BASELINE) is True


def test_tool_dist_regression_fails():
    c = customer_support_contract(BASELINE)
    results = {r["name"]: r for r in c.evaluate(CANDIDATE)}
    assert results["tool-call-dist-kl"]["passed"] is False
    assert c.passed(CANDIDATE) is False


def test_quality_invariant_tolerates_small_drop():
    c = customer_support_contract(BASELINE)
    # drop every quality by ~1% -> within the 2% tolerance
    cand = [{**t, "quality": t["quality"] * 0.99} for t in BASELINE]
    results = {r["name"]: r for r in c.evaluate(cand)}
    assert results["avg-quality-delta"]["passed"] is True


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"ok  {name}")
    print("\nall tests passed")

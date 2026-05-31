"""Tests. Run: python3 test_tracing.py"""

from __future__ import annotations

from tracing import Span, call_cost, traced_llm_call, MODEL_COST


def test_cost_matches_pricing_table():
    c = call_cost("gpt-4o", 1000, 1000)
    assert abs(c - (0.0025 + 0.010)) < 1e-9


def test_mini_is_cheaper_than_4o():
    assert call_cost("gpt-4o-mini", 1000, 1000) < call_cost("gpt-4o", 1000, 1000)


def test_span_tree_walk_visits_all():
    root = Span("agent_run")
    a = root.child("node:a")
    traced_llm_call(a, "gpt-4o", "a", 100, 50, 200)
    assert len(list(root.walk())) == 3


def test_cost_rolls_up():
    root = Span("agent_run")
    n = root.child("node:n")
    traced_llm_call(n, "gpt-4o", "n", 1000, 1000, 100)
    traced_llm_call(n, "gpt-4o-mini", "n", 1000, 1000, 100)
    expected = call_cost("gpt-4o", 1000, 1000) + call_cost("gpt-4o-mini", 1000, 1000)
    assert abs(root.total_cost() - round(call_cost("gpt-4o",1000,1000),6)
               - round(call_cost("gpt-4o-mini",1000,1000),6)) < 1e-6


def test_tokens_roll_up():
    root = Span("agent_run")
    traced_llm_call(root, "gpt-4o", "x", 300, 200, 100)
    assert root.total_tokens() == 500


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"ok  {name}")
    print("\nall tests passed")

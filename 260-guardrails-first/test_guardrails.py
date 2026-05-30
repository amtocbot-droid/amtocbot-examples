"""Failure-path tests for the guardrails. Run with: python -m pytest -q
(or just `python test_guardrails.py` to run the asserts directly)."""

from __future__ import annotations

from guardrails import (
    Budget,
    RepeatFailureBreaker,
    normalize_error,
    run_agent,
    validate,
)


def test_budget_trips_on_steps():
    b = Budget(max_steps=2)
    assert b.exceeded() is None
    b.charge(10, 0.0)
    b.charge(10, 0.0)
    assert "step limit" in b.exceeded()


def test_validator_blocks_update_without_where():
    err = validate("run_sql", {"sql": "UPDATE orders SET status = 'archived'"})
    assert err == "UPDATE without WHERE clause is blocked"


def test_validator_blocks_unknown_tool():
    assert "not on the allowlist" in validate("rm_rf", {})


def test_validator_blocks_ddl():
    assert "no DDL" in validate("run_sql", {"sql": "DROP TABLE orders"})


def test_breaker_keys_on_error_not_action():
    b = RepeatFailureBreaker(threshold=2)
    # Three *successful*-style distinct errors should not trip on action alone.
    assert b.record("write_file", "disk full on /a") is False
    assert b.record("write_file", "disk full on /b") is False
    assert b.record("write_file", "disk full on /c") is False  # normalized -> same? no, paths differ


def test_normalize_collapses_row_ids():
    a = normalize_error("lock timeout on row 4471")
    c = normalize_error("lock timeout on row 4472")
    assert a == c


def test_breaker_trips_on_normalized_identical():
    b = RepeatFailureBreaker(threshold=2)
    assert b.record("run_sql", "lock timeout on row 1") is False
    assert b.record("run_sql", "lock timeout on row 2") is False
    assert b.record("run_sql", "lock timeout on row 3") is True  # 3rd normalized-identical


def test_run_agent_escalates_cleanly_on_spiral():
    def propose(task, history):
        return {"tool": "run_sql",
                "args": {"sql": "update orders set x = 1 where id = 1"},
                "tokens": 100, "usd": 0.0}

    def execute(tool, args):
        return {"ok": False, "error": "lock timeout on ALTER TABLE orders"}

    result = run_agent("apply migration", propose, execute, Budget())
    assert result["status"] == "escalated"
    assert result["steps"] <= 4
    assert result["destructive_actions"] == 0


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"ok  {name}")
    print("\nall tests passed")

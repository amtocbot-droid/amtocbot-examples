"""Reproduce the 3am migration runaway from the post, with and without
guardrails, and show that the guardrailed run halts cleanly.

    $ python simulate_3am_migration.py
"""

from __future__ import annotations

from guardrails import Budget, run_agent


def make_locked_migration_agent():
    """A model that keeps proposing the same ALTER TABLE, which always fails
    with an identical lock-timeout. This is the 3am scenario."""

    def propose(task: str, history: list[dict]) -> dict:
        return {
            "tool": "run_sql",
            "args": {"sql": "update orders set migrated = true where id < 1000"},
            "tokens": 7_100,
            "usd": 0.05,
        }

    def execute(tool: str, args: dict) -> dict:
        # The lock never clears in this simulation.
        return {"ok": False, "error": "lock timeout on ALTER TABLE orders"}

    return propose, execute


def main() -> None:
    propose, execute = make_locked_migration_agent()
    budget = Budget(max_steps=25)
    result = run_agent("apply pending migration", propose, execute, budget)

    print("status:           ", result["status"])
    print("reason:           ", result["reason"])
    print("steps taken:      ", result["steps"])
    print("destructive acts: ", result["destructive_actions"])
    print("tokens spent:     ", budget.tokens)
    print(f"cost:              ${budget.usd:.2f}")
    print()
    print("Without the breaker this loops to the 25-step / token / cost ceiling.")
    print("With it, the run halts after 3 identical failures in a few seconds.")

    assert result["status"] == "escalated"
    assert result["steps"] <= 4, "breaker should halt within a few steps"
    assert result["destructive_actions"] == 0
    print("\nOK: halted cleanly with zero destructive actions.")


if __name__ == "__main__":
    main()

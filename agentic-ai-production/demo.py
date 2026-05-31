"""Drive a few tool outcomes through typed results, and watch the token
budget gate a runaway loop.

    $ python3 demo.py
"""

from __future__ import annotations

from tools import get_order_status, TokenBudget


def main() -> None:
    responses = {
        "ok": (200, {"status": "shipped"}),
        "rl": (429, None),
        "boom": (503, None),
        "missing": (404, None),
    }
    for label, resp in responses.items():
        r = get_order_status(label, http=lambda oid, _r=resp: _r)
        print(f"{label:<8} status={r.status:<7} type={r.error_type} "
              f"retry_safe={r.retry_safe}")

    assert get_order_status("ok", http=lambda o: (200, {})).status == "success"
    assert get_order_status("rl", http=lambda o: (429, None)).retry_safe is True
    assert get_order_status("missing", http=lambda o: (404, None)).retry_safe is False

    print("\ntoken budget:")
    budget = TokenBudget(total_budget=10_000, warning_threshold=0.75)
    for step in range(1, 6):
        budget.consume(2_000)
        verdict = budget.check(2_000)
        print(f"  step {step}: used={budget.used} -> {verdict}")
        if verdict == "EXCEEDED":
            print("  halting loop before overspend")
            break
    assert budget.check(2_000) == "EXCEEDED"
    print("\nOK: typed tool results + budget gate keep the loop bounded.")


if __name__ == "__main__":
    main()

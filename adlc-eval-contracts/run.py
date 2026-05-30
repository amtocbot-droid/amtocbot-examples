"""Run the customer_support eval contract against a candidate trace set and
print the pass/fail table from the post.

    $ python3 run.py
"""

from __future__ import annotations

from eval_contracts import customer_support_contract

# A small synthetic baseline: balanced tool use, high quality, low refusal.
BASELINE = (
    [{"quality": 0.90, "refused": False,
      "tool_calls": [{"tool": "search"}, {"tool": "lookup_order"}]}] * 40
    + [{"quality": 0.88, "refused": False, "tool_calls": [{"tool": "search"}]}] * 40
    + [{"quality": 0.85, "refused": True, "tool_calls": [{"tool": "escalate"}]}] * 20
)

# Candidate regresses: tool distribution skews toward escalate (KL breach),
# quality barely moves, refusal rate steady.
CANDIDATE = (
    [{"quality": 0.89, "refused": False, "tool_calls": [{"tool": "search"}]}] * 30
    + [{"quality": 0.88, "refused": False, "tool_calls": [{"tool": "escalate"}]}] * 50
    + [{"quality": 0.86, "refused": True, "tool_calls": [{"tool": "escalate"}]}] * 20
)


def main() -> None:
    contract = customer_support_contract(BASELINE)
    results = contract.evaluate(CANDIDATE)
    print(f"contract={contract.name}  version={contract.version}")
    overall = "PASS"
    for r in results:
        status = "PASS" if r["passed"] else "FAIL"
        if not r["passed"]:
            overall = "FAIL"
        print(f"  {r['name']:<22}{status}   delta={r['delta']:.3f}   "
              f"tolerance={r['tolerance']}")
    print(f"result={overall}  "
          f"{'promotion blocked' if overall == 'FAIL' else 'promotion allowed'}")
    return overall


if __name__ == "__main__":
    main()

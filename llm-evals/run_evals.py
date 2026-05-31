"""Run all three eval layers against a small golden set.

    $ python3 run_evals.py
"""

from __future__ import annotations

from evals import (
    eval_ticket_classification, pass_rate, semantic_similarity, judge_response,
)

GOLDEN_RESPONSES = [
    '{"label": "billing", "confidence": 0.97}',
    '{"label": "technical", "confidence": 0.81}',
    '{"label": "account", "confidence": 0.6}',
    '{"label": "made_up_label", "confidence": 0.9}',   # invalid label
    'not json at all',                                  # invalid format
]


def main() -> None:
    print("Layer 1 — format check")
    rate = pass_rate(GOLDEN_RESPONSES)
    print(f"  classification format pass rate: {rate:.1%}")
    assert abs(rate - 0.6) < 1e-9  # 3 of 5 valid

    print("\nLayer 2 — semantic similarity")
    sim = semantic_similarity(
        "The subscription renews on the 15th of each month",
        "Your subscription billing date is the 15th")
    print(f"  similarity: {sim:.3f}")
    assert sim > 0.3

    print("\nLayer 3 — LLM-as-judge rubric")
    weak = judge_response("How do I change my billing date?",
                          "Your billing date is the 15th of each month.")
    strong = judge_response("How do I change my billing date?",
                            "Go to Settings > Billing and click Change date.")
    print(f"  weak answer:   {weak}")
    print(f"  strong answer: {strong}")
    assert strong["helpfulness"] > weak["helpfulness"]
    print("\nOK: format gate, similarity, and judge all wired up.")


if __name__ == "__main__":
    main()

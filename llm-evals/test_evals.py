"""Tests. Run: python3 test_evals.py"""

from __future__ import annotations

from evals import (
    eval_ticket_classification, pass_rate, semantic_similarity, judge_response,
)


def test_valid_classification_passes():
    assert eval_ticket_classification('{"label": "billing", "confidence": 0.9}')


def test_invalid_label_fails():
    assert not eval_ticket_classification('{"label": "nope", "confidence": 0.9}')


def test_confidence_out_of_range_fails():
    assert not eval_ticket_classification('{"label": "billing", "confidence": 1.5}')


def test_non_json_fails():
    assert not eval_ticket_classification("garbage")


def test_pass_rate_counts():
    assert pass_rate(['{"label": "billing", "confidence": 0.9}', "bad"]) == 0.5


def test_similarity_high_for_paraphrase():
    s = semantic_similarity("the cat sat on the mat", "the cat sat on a mat")
    assert s > 0.5


def test_similarity_low_for_unrelated():
    s = semantic_similarity("quantum chromodynamics lecture", "billing date change")
    assert s < 0.3


def test_judge_prefers_actionable_answer():
    weak = judge_response("how do I change billing date",
                          "your billing date is the 15th")
    strong = judge_response("how do I change billing date",
                            "go to settings and change the date")
    assert strong["helpfulness"] > weak["helpfulness"]


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"ok  {name}")
    print("\nall tests passed")

"""
Layer 3: Semantic quality tests using LLM-as-judge.
Marked 'llm_judge' — run only on merge to main, not every commit.
Requires OPENAI_API_KEY.
"""
import json
import pytest
from pathlib import Path
from tests.judge import judge_classification

GOLDEN_DIR = Path(__file__).parent / "eval/golden/ticket_classifier"
MIN_AVG_SCORE = 0.80


@pytest.mark.llm_judge
def test_semantic_quality_above_threshold():
    """Average judge score across golden set must stay above MIN_AVG_SCORE."""
    scores = []
    failures = []

    for golden_path in sorted(GOLDEN_DIR.glob("*.json")):
        golden = json.loads(golden_path.read_text())
        classification = {k: v for k, v in golden.items() if not k.startswith("_")}

        verdict = judge_classification(
            ticket=golden["_test_input"],
            classification=classification,
        )
        scores.append(verdict["score"])

        if verdict["score"] < MIN_AVG_SCORE:
            failures.append(
                f"{golden_path.stem}: score={verdict['score']:.2f} — {verdict['explanation']}"
            )

    avg = sum(scores) / len(scores) if scores else 0.0
    print(f"\nJudge scores: {[f'{s:.2f}' for s in scores]}")
    print(f"Average: {avg:.2f} (threshold: {MIN_AVG_SCORE})")

    assert avg >= MIN_AVG_SCORE, (
        f"Average judge score {avg:.2f} below threshold {MIN_AVG_SCORE}.\n"
        "Low-scoring cases:\n" + "\n".join(failures)
    )

"""
Layer 2: Regression tests — compare golden set to baseline.
Baseline = previous prompt version's golden set.
Run: cp -r tests/eval/golden/ tests/eval/baseline/ before updating prompt.
"""
import json
import pytest
from pathlib import Path

GOLDEN_DIR  = Path(__file__).parent / "eval/golden/ticket_classifier"
BASELINE_DIR = Path(__file__).parent / "eval/baseline/ticket_classifier"


@pytest.mark.skipif(
    not BASELINE_DIR.exists() or not any(BASELINE_DIR.iterdir()),
    reason="No baseline to compare — run after first prompt update"
)
def test_category_unchanged_from_baseline():
    """Categories must not silently change between prompt versions."""
    failures = []
    for golden_path in GOLDEN_DIR.glob("*.json"):
        baseline_path = BASELINE_DIR / golden_path.name
        if not baseline_path.exists():
            continue

        golden   = json.loads(golden_path.read_text())
        baseline = json.loads(baseline_path.read_text())

        if golden["category"] != baseline["category"]:
            failures.append(
                f"{golden_path.stem}: "
                f"'{baseline['category']}' → '{golden['category']}'"
            )

    assert not failures, (
        "Category changed between prompt versions:\n" + "\n".join(failures)
        + "\nIf intentional, update the baseline and regenerate goldens."
    )


@pytest.mark.skipif(
    not BASELINE_DIR.exists() or not any(BASELINE_DIR.iterdir()),
    reason="No baseline to compare"
)
def test_priority_delta_at_most_1():
    """Priority may shift by at most 1 point between prompt versions."""
    failures = []
    for golden_path in GOLDEN_DIR.glob("*.json"):
        baseline_path = BASELINE_DIR / golden_path.name
        if not baseline_path.exists():
            continue

        golden   = json.loads(golden_path.read_text())
        baseline = json.loads(baseline_path.read_text())

        delta = abs(golden["priority"] - baseline["priority"])
        if delta > 1:
            failures.append(
                f"{golden_path.stem}: "
                f"priority {baseline['priority']} → {golden['priority']} (delta={delta})"
            )

    assert not failures, "Priority shifted by >1:\n" + "\n".join(failures)

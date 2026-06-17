"""
Layer 1: Deterministic structure tests.
Loads golden JSON fixtures — no API calls, no network, runs in milliseconds.
"""
import json
import pytest
from pathlib import Path

GOLDEN_DIR = Path(__file__).parent / "eval/golden/ticket_classifier"

VALID_CATEGORIES = {"billing", "technical", "account", "feature_request", "other"}


@pytest.fixture
def golden_responses():
    return {
        path.stem: json.loads(path.read_text())
        for path in GOLDEN_DIR.glob("*.json")
    }


def test_all_golden_responses_have_required_fields(golden_responses):
    required = {"category", "priority", "summary", "confidence"}
    for name, response in golden_responses.items():
        missing = required - set(response.keys())
        assert not missing, f"{name}: missing fields {missing}"


def test_category_is_valid_enum(golden_responses):
    for name, response in golden_responses.items():
        assert response["category"] in VALID_CATEGORIES, (
            f"{name}: invalid category '{response['category']}'"
        )


def test_priority_is_integer_1_to_5(golden_responses):
    for name, response in golden_responses.items():
        p = response["priority"]
        assert isinstance(p, int) and 1 <= p <= 5, (
            f"{name}: priority '{p}' out of range [1, 5]"
        )


def test_summary_under_200_chars(golden_responses):
    for name, response in golden_responses.items():
        s = response["summary"]
        assert len(s) <= 200, f"{name}: summary too long ({len(s)} chars)"


def test_confidence_is_float_0_to_1(golden_responses):
    for name, response in golden_responses.items():
        c = response["confidence"]
        assert isinstance(c, float) and 0.0 <= c <= 1.0, (
            f"{name}: confidence '{c}' out of [0.0, 1.0]"
        )

"""
Generate (or regenerate) the golden fixture set.
Run manually when you intentionally update a prompt.
NEVER run automatically in CI.

Usage:
    export OPENAI_API_KEY=sk-...
    python scripts/generate_golden_set.py
"""
import json
import os
from pathlib import Path
from openai import OpenAI

client = OpenAI()
GOLDEN_DIR = Path(__file__).parent.parent / "tests/eval/golden/ticket_classifier"
GOLDEN_DIR.mkdir(parents=True, exist_ok=True)

SYSTEM_PROMPT = """Classify the support ticket. Return JSON with:
- "category": one of "billing" | "technical" | "account" | "feature_request" | "other"
- "priority": integer 1 (lowest) to 5 (highest)
- "summary": one sentence, ≤200 chars, capturing all key specifics
- "confidence": float 0.0-1.0"""

TEST_CASES = [
    {"id": "billing_simple",     "input": "My invoice has wrong charges this month"},
    {"id": "technical_crash",    "input": "App crashes every time I open the settings screen on iOS 17"},
    {"id": "account_locked",     "input": "I can't log in, says account suspended but I didn't do anything"},
    {"id": "feature_dark_mode",  "input": "Please add dark mode, the white background hurts my eyes at night"},
    {"id": "priority_urgent",    "input": "URGENT: All our users are getting 500 errors on checkout. Revenue stopped."},
]


def classify(ticket_text: str) -> dict:
    resp = client.chat.completions.create(
        model="gpt-4o-mini-2024-07-18",
        temperature=0.1,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": ticket_text},
        ],
    )
    return json.loads(resp.choices[0].message.content)


for case in TEST_CASES:
    result = classify(case["input"])
    result["_test_input"] = case["input"]
    result["_test_id"]    = case["id"]

    out = GOLDEN_DIR / f"{case['id']}.json"
    out.write_text(json.dumps(result, indent=2) + "\n")
    print(f"Generated: {case['id']} → category={result['category']}, priority={result['priority']}")

print(f"\nGolden set written to {GOLDEN_DIR}")
print("Commit these files. To set as baseline: cp -r tests/eval/golden/ tests/eval/baseline/")

"""
Layer 3: LLM-as-judge implementation.
Uses a stronger model to evaluate classification quality against explicit criteria.
"""
import json
import os
from openai import OpenAI

client = OpenAI()

JUDGE_PROMPT = """You are an evaluation judge for a ticket classification system.

You will receive:
1. A support ticket (the input)
2. A classification result (JSON)

Evaluate whether the classification is correct and complete.

Return JSON with:
- "correct": true/false — is the category appropriate for this ticket?
- "priority_reasonable": true/false — is the priority level appropriate?
- "summary_accurate": true/false — does the summary accurately capture the ticket?
- "summary_complete": true/false — does the summary include all key specifics (numbers, error codes, platform names) from the ticket?
- "explanation": one sentence explaining your verdict
- "score": float 0.0-1.0 (1.0 = perfect on all dimensions)

Be strict: a score below 0.8 means something is genuinely wrong."""


def judge_classification(ticket: str, classification: dict) -> dict:
    """Evaluate a classification result using gpt-4o as judge."""
    response = client.chat.completions.create(
        model="gpt-4o-2024-11-20",
        temperature=0.0,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": JUDGE_PROMPT},
            {
                "role": "user",
                "content": json.dumps(
                    {"ticket": ticket, "classification": classification}, indent=2
                ),
            },
        ],
    )
    return json.loads(response.choices[0].message.content)

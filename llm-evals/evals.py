"""Three layers of production LLM evaluation: deterministic format checks,
semantic similarity to a reference, and LLM-as-judge rubric scoring.

Companion code for the AmtocSoft post
"LLM Evaluation in Production".

The post uses a real model for the judge and sentence-transformers for
similarity. Here the judge is a transparent rule-based scorer and similarity
uses a hashing embedding, so the harness runs with no dependencies. The
`eval_ticket_classification` format check is verbatim from the post.
"""

from __future__ import annotations

import hashlib
import json
import math

VALID_LABELS = {"billing", "technical", "account", "feature_request", "other"}


# --------------------------------------------------------------------------
# Layer 1: deterministic format check (verbatim from the post).
# --------------------------------------------------------------------------
def eval_ticket_classification(response: str) -> bool:
    """Verify the response is valid classification JSON with a confidence."""
    try:
        data = json.loads(response)
        return (
            data.get("label") in VALID_LABELS
            and isinstance(data.get("confidence"), float)
            and 0.0 <= data["confidence"] <= 1.0
        )
    except (json.JSONDecodeError, KeyError):
        return False


def pass_rate(responses: list[str]) -> float:
    results = [eval_ticket_classification(r) for r in responses]
    return sum(results) / len(results) if results else 0.0


# --------------------------------------------------------------------------
# Layer 2: semantic similarity (hashing-embedding stand-in for embeddings).
# --------------------------------------------------------------------------
def _embed(text: str, dim: int = 128) -> list[float]:
    vec = [0.0] * dim
    for tok in text.lower().split():
        vec[int(hashlib.sha256(tok.encode()).hexdigest(), 16) % dim] += 1.0
    norm = math.sqrt(sum(x * x for x in vec)) or 1.0
    return [x / norm for x in vec]


def semantic_similarity(response: str, reference: str) -> float:
    a, b = _embed(response), _embed(reference)
    return float(sum(x * y for x, y in zip(a, b)))


# --------------------------------------------------------------------------
# Layer 3: LLM-as-judge rubric (rule-based stand-in for the model call).
# --------------------------------------------------------------------------
def judge_response(question: str, response: str) -> dict:
    """Score accuracy/helpfulness/tone 1-5. A real deployment calls a strong
    model with GRADING_PROMPT; this deterministic proxy keeps the example
    runnable and the scoring logic inspectable."""
    q_tokens = set(question.lower().split())
    r_tokens = set(response.lower().split())
    overlap = len(q_tokens & r_tokens) / (len(q_tokens) or 1)
    # Helpfulness: does it look like it acts (verbs like "go to", "click")?
    acts = any(w in response.lower() for w in
               ("go to", "click", "open", "navigate", "set", "change", "select"))
    accuracy = 5 if overlap > 0.3 else (4 if overlap > 0.1 else 2)
    helpfulness = 4 if acts else 2
    tone = 5 if not any(w in response.lower() for w in ("idiot", "stupid")) else 1
    reasoning = ("addresses the question and gives a concrete action"
                 if acts else "states a fact but doesn't tell the user how to act")
    return {"accuracy": accuracy, "helpfulness": helpfulness, "tone": tone,
            "reasoning": reasoning}

"""Input/output guardrails for production LLM apps: PII redaction, length
and gibberish checks on input, and a grounding check on output.

Companion code for the AmtocSoft post
"AI Guardrails in Production".

The post uses the `guardrails-ai` library and an LLM grounding judge. This
reimplements the same validators with the standard library: PII fixing,
length bounds, a simple gibberish heuristic, and a rule-based grounding
check (every factual claim's key terms must appear in the context).
"""

from __future__ import annotations

import re
from dataclasses import dataclass

EMAIL = re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b")
PHONE = re.compile(r"\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b")


class ValidationError(Exception):
    pass


@dataclass
class GuardConfig:
    min_len: int = 10
    max_len: int = 2000
    gibberish_threshold: float = 0.8


def fix_pii(text: str) -> str:
    """Redact PII rather than reject (OnFailAction.FIX in the post)."""
    text = EMAIL.sub("<EMAIL>", text)
    text = PHONE.sub("<PHONE>", text)
    return text


def gibberish_score(text: str) -> float:
    """Fraction of 'words' that look like noise (no vowels, or very long).
    0.0 = clean prose, 1.0 = keyboard mash."""
    words = text.split()
    if not words:
        return 1.0
    bad = 0
    for w in words:
        letters = [c for c in w.lower() if c.isalpha()]
        if not letters:
            continue
        vowel_ratio = sum(c in "aeiou" for c in letters) / len(letters)
        if vowel_ratio < 0.1 or len(w) > 25:
            bad += 1
    return bad / len(words)


def validate_input(text: str, cfg: GuardConfig = GuardConfig()) -> str:
    """Returns the (possibly PII-fixed) input or raises ValidationError."""
    if not (cfg.min_len <= len(text) <= cfg.max_len):
        raise ValidationError(
            f"length {len(text)} outside [{cfg.min_len}, {cfg.max_len}]")
    if gibberish_score(text) >= cfg.gibberish_threshold:
        raise ValidationError("input looks like gibberish")
    return fix_pii(text)


def check_grounding(context: str, response: str) -> dict:
    """Rule-based grounding: every sentence's content words must be present
    in the context. Returns VERDICT + unsupported claims."""
    ctx_words = set(re.findall(r"[a-z]{4,}", context.lower()))
    sentences = [s.strip() for s in re.split(r"[.!?]", response) if s.strip()]
    unsupported = []
    for s in sentences:
        content = set(re.findall(r"[a-z]{4,}", s.lower()))
        if not content:
            continue
        covered = len(content & ctx_words) / len(content)
        if covered < 0.5:
            unsupported.append(s)
    if not unsupported:
        verdict = "SUPPORTED"
    elif len(unsupported) == len(sentences):
        verdict = "UNSUPPORTED"
    else:
        verdict = "PARTIAL"
    return {"verdict": verdict, "unsupported_claims": unsupported}

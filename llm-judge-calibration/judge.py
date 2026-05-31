"""LLM-as-judge with position-bias mitigation and human-rater calibration.

Companion code for the AmtocSoft post
"LLM-as-a-Judge in Production: Eval Bias Correction, Human-Rater Calibration".

Two failure modes the post addresses:

1. **Position bias** — judges favour whichever response came first. Mitigation:
   run each pair twice with the order swapped; only count a win if it holds
   in both orderings, else call it a TIE.
2. **Judge/human disagreement** — measure it with Cohen's kappa before you
   trust the judge as a gate.

The real judge is an LLM; here it's a deterministic scorer so the example
runs with no dependencies and the bias-correction logic is inspectable.
"""

from __future__ import annotations

from collections import Counter

Verdict = str  # "A" | "B" | "TIE"


def _rubric_score(question: str, response: str) -> float:
    """Stand-in for the LLM judge: rewards on-topic, concise, action-bearing
    answers; penalises padding. Deterministic so tests are stable."""
    q = set(question.lower().split())
    r_tokens = response.lower().split()
    overlap = len(q & set(r_tokens)) / (len(q) or 1)
    acts = any(w in response.lower() for w in
               ("go to", "click", "set", "use", "run", "call", "open"))
    length_penalty = max(0.0, (len(r_tokens) - 40) / 100)  # >40 words starts to hurt
    return overlap + (0.5 if acts else 0.0) - length_penalty


def _raw_verdict(question: str, first: str, second: str, bias: float = 0.05) -> Verdict:
    """One judging pass. `bias` models the judge's preference for whatever is
    shown FIRST — the very bias we then correct for."""
    s1 = _rubric_score(question, first) + bias
    s2 = _rubric_score(question, second)
    if abs(s1 - s2) < 0.1:
        return "TIE"
    return "first" if s1 > s2 else "second"


def judge_pair(question: str, resp_a: str, resp_b: str) -> Verdict:
    """Position-bias-mitigated verdict: judge A-then-B and B-then-A; a win
    only counts if it survives the swap, otherwise TIE."""
    v1 = _raw_verdict(question, resp_a, resp_b)   # A first
    v2 = _raw_verdict(question, resp_b, resp_a)   # B first
    winner1 = {"first": "A", "second": "B", "TIE": "TIE"}[v1]
    winner2 = {"first": "B", "second": "A", "TIE": "TIE"}[v2]
    if winner1 == winner2 and winner1 != "TIE":
        return winner1
    return "TIE"


def cohens_kappa(judge: list[str], human: list[str]) -> float:
    """Cohen's kappa between judge and human labels over the same items."""
    assert len(judge) == len(human) and judge
    n = len(judge)
    po = sum(1 for a, b in zip(judge, human) if a == b) / n
    labels = set(judge) | set(human)
    jc, hc = Counter(judge), Counter(human)
    pe = sum((jc[l] / n) * (hc[l] / n) for l in labels)
    return 1.0 if pe == 1.0 else (po - pe) / (1 - pe)

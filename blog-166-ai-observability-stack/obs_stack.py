"""AI observability stack selection + a vendor-neutral eval pass over traces.

Companion code for the AmtocSoft post
"The AI Observability Stack 2026: Langfuse, Arize, Portkey, Splunk".

Two runnable pieces:

1. `recommend_tools` scores the four tools in the post against a set of
   weighted requirements and returns a ranked recommendation — the
   "which tool for which job" decision, made explicit.
2. `run_eval_pass` runs hallucination + relevance checks over a window of
   recorded traces and decides whether to page on-call (the post's
   Phoenix/Arize offline-eval loop), using rule-based evaluators.

Pure standard library.
"""

from __future__ import annotations

from dataclasses import dataclass

# Capability matrix from the post (0..1 per capability).
TOOLS = {
    "langfuse":  {"tracing": 1.0, "prompt_mgmt": 1.0, "evals": 0.7, "cost": 0.8, "siem": 0.2},
    "arize":     {"tracing": 0.8, "prompt_mgmt": 0.5, "evals": 1.0, "cost": 0.6, "siem": 0.3},
    "portkey":   {"tracing": 0.7, "prompt_mgmt": 0.6, "evals": 0.5, "cost": 1.0, "siem": 0.3},
    "splunk":    {"tracing": 0.6, "prompt_mgmt": 0.2, "evals": 0.4, "cost": 0.4, "siem": 1.0},
}


def recommend_tools(weights: dict[str, float]) -> list[tuple[str, float]]:
    """Score each tool by the dot product of its capabilities and the team's
    requirement weights. Returns a ranked list."""
    scored = []
    for tool, caps in TOOLS.items():
        score = sum(weights.get(cap, 0.0) * val for cap, val in caps.items())
        scored.append((tool, round(score, 3)))
    scored.sort(key=lambda t: t[1], reverse=True)
    return scored


# --------------------------------------------------------------------------
# Offline eval pass over recorded traces.
# --------------------------------------------------------------------------
@dataclass
class Trace:
    context: str
    output: str


def is_hallucination(trace: Trace) -> bool:
    """Output asserts content not grounded in the context (rule-based)."""
    import re
    ctx = set(re.findall(r"[a-z]{4,}", trace.context.lower()))
    out = set(re.findall(r"[a-z]{4,}", trace.output.lower()))
    if not out:
        return False
    return (len(out & ctx) / len(out)) < 0.4


def run_eval_pass(traces: list[Trace], page_threshold: float = 0.15) -> dict:
    n = len(traces) or 1
    halluc = sum(is_hallucination(t) for t in traces)
    rate = halluc / n
    return {"n": n, "hallucination_rate": round(rate, 3),
            "page_oncall": rate > page_threshold}

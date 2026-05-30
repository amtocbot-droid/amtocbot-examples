"""The three memory patterns from the post: semantic (user facts), episodic
(threaded events with summary/raw depth), and procedural (a skill registry
with an LLM-as-router selector).

Companion code for the AmtocSoft post
"AI Agent Memory Patterns: Semantic, Episodic, Procedural".

The post backs semantic memory with pgvector and routes skills with an LLM.
Here, embeddings are a deterministic hash and the skill router is a
transparent keyword scorer, so the example runs with no dependencies.
"""

from __future__ import annotations

import hashlib
import math
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime


def embed(text: str, dim: int = 64) -> list[float]:
    vec = [0.0] * dim
    for tok in text.lower().split():
        vec[int(hashlib.sha256(tok.encode()).hexdigest(), 16) % dim] += 1.0
    norm = math.sqrt(sum(x * x for x in vec)) or 1.0
    return [x / norm for x in vec]


def cosine(a, b):
    return sum(x * y for x, y in zip(a, b))


# --------------------------------------------------------------------------
# Semantic memory: durable user facts, retrieved by similarity.
# --------------------------------------------------------------------------
class SemanticMemory:
    def __init__(self):
        self._facts: list[dict] = []

    def write_user_fact(self, user_id: str, fact_text: str, fact_type: str) -> None:
        self._facts.append({"user_id": user_id, "text": fact_text,
                            "type": fact_type, "emb": embed(fact_text)})

    def read_user_facts(self, user_id: str, query: str, k: int = 5) -> list[dict]:
        q = embed(query)
        rel = [f for f in self._facts if f["user_id"] == user_id]
        rel.sort(key=lambda f: cosine(q, f["emb"]), reverse=True)
        return [{"text": f["text"], "type": f["type"],
                 "similarity": round(cosine(q, f["emb"]), 3)} for f in rel[:k]]


# --------------------------------------------------------------------------
# Episodic memory: threaded events; read at summary or raw depth.
# --------------------------------------------------------------------------
class EpisodicMemory:
    def __init__(self):
        self._events: dict[str, list[dict]] = defaultdict(list)
        self._summaries: dict[str, str] = {}

    def write_event(self, thread_id: str, event_type: str, content: str) -> None:
        self._events[thread_id].append({"type": event_type, "content": content})

    def summarize_thread(self, thread_id: str) -> str:
        # Production calls an LLM; here we synthesize a deterministic summary.
        events = self._events[thread_id]
        summary = f"{len(events)} events: " + "; ".join(
            e["content"][:40] for e in events[:3])
        self._summaries[thread_id] = summary
        return summary

    def read(self, thread_id: str, depth: str = "summary") -> dict:
        out = {"summary": self._summaries.get(thread_id)
               or self.summarize_thread(thread_id)}
        if depth == "raw":
            out["raw_events"] = self._events[thread_id]
        return out


# --------------------------------------------------------------------------
# Procedural memory: a skill registry + LLM-as-router skill selection.
# --------------------------------------------------------------------------
SKILL_REGISTRY = {
    "refund_request": {
        "trigger": "refund charge dispute money back",
        "tools_required": ["billing.lookup", "refund.initiate", "audit.log"],
        "escalation": "if amount > $500 escalate to human"},
    "outage_status": {
        "trigger": "service down slow errors outage",
        "tools_required": ["status.check", "incident.list"],
        "escalation": "if no incident found and user persistent, escalate"},
    "tier_upgrade": {
        "trigger": "upgrade more features hitting limits plan",
        "tools_required": ["billing.tiers", "billing.upgrade"],
        "escalation": "always confirm before charging"},
}


def select_skill(query: str, registry: dict = SKILL_REGISTRY) -> str:
    """Transparent stand-in for the LLM router: pick the skill whose trigger
    tokens overlap the query most; 'none' if nothing matches."""
    q = set(query.lower().split())
    best, best_score = "none", 0
    for name, skill in registry.items():
        score = len(q & set(skill["trigger"].split()))
        if score > best_score:
            best, best_score = name, score
    return best

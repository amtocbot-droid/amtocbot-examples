"""Three-tier agent memory: working (in-context), episodic (vector store),
semantic (structured facts), with a query router that decides which tiers
to hit.

Companion code for the AmtocSoft post
"Context Window Limits and the Memory Myth".

The post backs episodic memory with Chroma and routes with a Haiku
classifier. To keep this runnable with no dependencies, episodic memory is
an in-memory store with a deterministic hashing embedding, and the router is
a transparent keyword classifier (swap in an LLM call in production).
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass, field
from typing import Optional


def embed(text: str, dim: int = 64) -> list[float]:
    vec = [0.0] * dim
    for tok in text.lower().split():
        vec[int(hashlib.sha256(tok.encode()).hexdigest(), 16) % dim] += 1.0
    norm = math.sqrt(sum(x * x for x in vec)) or 1.0
    return [x / norm for x in vec]


def cosine(a, b):
    return sum(x * y for x, y in zip(a, b))


@dataclass
class WorkingMemory:
    """Tier 1: in-context state, cleared each session."""
    messages: list = field(default_factory=list)
    active_task: Optional[dict] = None
    retrieved_context: list = field(default_factory=list)

    def to_context_string(self, max_chunks: int = 5) -> str:
        parts = []
        if self.active_task:
            parts.append(f"Current task: {json.dumps(self.active_task)}")
        if self.retrieved_context:
            parts.append("Retrieved context:")
            for chunk in self.retrieved_context[:max_chunks]:
                parts.append(f"  - {chunk['content'][:500]}")
        return "\n".join(parts)


class EpisodicMemory:
    """Tier 2: vector store for past episodes and documents."""

    def __init__(self):
        self._docs: list[dict] = []

    def write(self, content: str, metadata: dict) -> str:
        doc_id = hashlib.sha256(content.encode()).hexdigest()[:16]
        self._docs.append({"id": doc_id, "content": content,
                           "metadata": metadata, "emb": embed(content)})
        return doc_id

    def retrieve(self, query: str, n_results: int = 3) -> list[dict]:
        q = embed(query)
        ranked = sorted(self._docs, key=lambda d: cosine(q, d["emb"]), reverse=True)
        return [{"content": d["content"], "source": "episodic"} for d in ranked[:n_results]]


class SemanticMemory:
    """Tier 3: structured facts keyed by name."""

    def __init__(self):
        self._facts: dict[str, dict] = {}

    def put(self, key: str, value: dict) -> None:
        self._facts[key] = value

    def get(self, key: str) -> Optional[dict]:
        return self._facts.get(key)


# Transparent keyword router. Production swaps this for an LLM classifier.
ROUTER_RULES = {
    "episodic": ["last time", "previously", "yesterday", "earlier", "history",
                 "document", "conversation", "remember when"],
    "semantic": ["my name", "my account", "preference", "profile", "tier",
                 "email", "settings"],
}


def route_query(query: str, working: WorkingMemory) -> dict:
    q = query.lower()
    tiers = ["working"]
    for tier, kws in ROUTER_RULES.items():
        if any(kw in q for kw in kws):
            tiers.append(tier)
    if tiers == ["working"]:
        # default: also consult episodic when working memory is thin
        if not working.retrieved_context:
            tiers.append("episodic")
    return {"tiers": tiers, "reason": "keyword routing"}


def retrieve_for_query(query: str, working: WorkingMemory,
                       episodic: EpisodicMemory, semantic: SemanticMemory) -> list[dict]:
    routing = route_query(query, working)
    out: list[dict] = []
    if "episodic" in routing["tiers"]:
        out.extend(episodic.retrieve(query, n_results=3))
    if "semantic" in routing["tiers"]:
        profile = semantic.get("user_profile")
        if profile:
            out.append({"content": json.dumps(profile), "source": "semantic"})
    return out

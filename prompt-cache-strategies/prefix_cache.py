"""Stable-prefix prompt builder + cache hit-rate accounting.

Companion code for the AmtocSoft post
"LLM Prompt Cache Strategies: Anthropic, OpenAI, Self-Hosted, Hit-Rate
Optimisation".

Two builders from the post:

- `build_prompt_broken` interpolates the current time and tenant id INTO the
  cached system prompt, so the cache key changes on every call and every
  tenant — hit rate collapses.
- `build_prompt_stable` keeps the rules + tool defs as one byte-stable block
  and pushes all volatile content (time, tenant, user) into the uncached
  user turn.

Plus `cache_stats`, the hit-rate / savings computation the post logs per call.
Pure standard library.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass

RULES_PROMPT = "Follow these rules carefully:\n1. Be accurate.\n2. Cite sources."
TOOLS = [
    {"name": "search", "args": {"q": "string"}},
    {"name": "fetch", "args": {"url": "string"}},
]

# Stable: tool defs serialized deterministically; no volatile content.
SYSTEM_PROMPT_TEMPLATE = (
    "You are an assistant. " + RULES_PROMPT + "\n\nTool definitions:\n"
    + json.dumps(TOOLS, indent=2, sort_keys=True, separators=(",", ": "))
)


def build_prompt_broken(tenant_id: str, user_id: str, message: str, now: str) -> list[dict]:
    """Anti-pattern: volatile values baked into the cached system prompt."""
    return [
        {"role": "system", "content": (
            f"You are an assistant for {tenant_id}. The current time is {now}. "
            + RULES_PROMPT + "\n\nTool definitions:\n" + json.dumps(TOOLS))},
        {"role": "user", "content": f"[{user_id}] {message}"},
    ]


def build_prompt_stable(tenant_id: str, user_id: str, message: str, now: str) -> list[dict]:
    """Byte-stable cached prefix; volatile content lives in the user turn."""
    return [
        {"role": "system", "content": [
            {"type": "text", "text": SYSTEM_PROMPT_TEMPLATE,
             "cache_control": {"type": "ephemeral"}},
        ]},
        {"role": "user", "content": f"[{tenant_id}/{user_id}] [{now}] {message}"},
    ]


def cache_key(messages: list[dict]) -> str:
    """The cacheable prefix is everything up to the first non-cached block.
    Here: the system content marked cache_control, else the whole system msg."""
    sys = messages[0]["content"]
    if isinstance(sys, list):
        prefix = "".join(b["text"] for b in sys if "cache_control" in b)
    else:
        prefix = sys
    return hashlib.sha256(prefix.encode()).hexdigest()


@dataclass
class Usage:
    input_tokens: int
    cache_read_input_tokens: int = 0
    cache_creation_input_tokens: int = 0


def cache_stats(usage: Usage) -> dict:
    """Hit rate + cost savings vs no-cache (write=125%, read=10%)."""
    total = (usage.input_tokens + usage.cache_read_input_tokens
             + usage.cache_creation_input_tokens)
    if total == 0:
        return {"hit_rate": 0.0, "savings": 0.0}
    hit_rate = usage.cache_read_input_tokens / total
    effective = (usage.input_tokens
                 + usage.cache_creation_input_tokens * 1.25
                 + usage.cache_read_input_tokens * 0.10)
    savings = 1 - effective / total
    return {"hit_rate": hit_rate, "savings": savings}


if __name__ == "__main__":
    u = Usage(input_tokens=50, cache_read_input_tokens=41_247,
              cache_creation_input_tokens=0)
    s = cache_stats(u)
    print(f"Cache hit rate: {s['hit_rate']:.1%}")
    print(f"Cost savings vs no-cache: {s['savings']:.1%}")

"""Route LLM tasks between a local small language model and a cloud fallback,
plus the memory-fit math from the post.

Companion code for the AmtocSoft post "SLMs On-Device: Pick, Quantize, and
Ship a Small Language Model". Pure standard library; the Ollama call is
optional and isolated so the routing logic is testable offline.
"""

from __future__ import annotations

import json
import urllib.request

OLLAMA_URL = "http://localhost:11434/api/generate"


# --------------------------------------------------------------------------
# Memory math: will this model + context fit the hardware?
# --------------------------------------------------------------------------
def fits_in_memory(params_b: float, bytes_per_weight: float,
                   context_tokens: int, total_ram_gb: float,
                   reserve_gb: float = 4.0) -> tuple[bool, float]:
    weights_gb = params_b * bytes_per_weight              # 7 * 0.6 ~= 4.4
    kv_cache_gb = context_tokens * 0.000005 * params_b    # rough, model-dependent
    needed = weights_gb + kv_cache_gb + reserve_gb
    return needed <= total_ram_gb, round(needed, 1)


# --------------------------------------------------------------------------
# Difficulty heuristic: which tasks should escalate to the cloud?
# --------------------------------------------------------------------------
HARD_CUES = ("prove", "step by step", "analyze the tradeoffs", "write code")


def is_hard(task: str) -> bool:
    if len(task) > 6000:
        return True
    return any(cue in task.lower() for cue in HARD_CUES)


# --------------------------------------------------------------------------
# Local inference via Ollama (network-isolated so tests don't need it)
# --------------------------------------------------------------------------
def local_generate(prompt: str, model: str = "phi4-mini") -> str:
    payload = json.dumps({"model": model, "prompt": prompt, "stream": False}).encode()
    req = urllib.request.Request(OLLAMA_URL, data=payload,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())["response"].strip()


def route(task: str, cloud_fallback, local_fn=local_generate) -> dict:
    """Return {'engine': 'local'|'cloud', 'output': str}. local_fn is injectable
    so the routing decision can be tested without a running Ollama."""
    if is_hard(task):
        return {"engine": "cloud", "output": cloud_fallback(task)}
    return {"engine": "local", "output": local_fn(task)}

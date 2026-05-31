"""Safe model rollouts: shadow-mode logging and sticky-by-user traffic splits.

Companion code for the AmtocSoft post
"Production LLM Canary Deployments: Shadow Mode, Traffic Splits, Safe Model
Rollouts".

Two primitives from the post:

- `route_decision` — sticky-by-user bucketing so the same user always lands
  in the same bucket for a given rollout percentage.
- `shadow_route` — return the old model's answer to the user while logging
  both old and new for offline diffing (the new model never blocks the user).

The post is async over real models; this uses injected model callables so it
runs standalone. Pure standard library (asyncio).
"""

from __future__ import annotations

import asyncio
import hashlib


def route_decision(user_id: str, percent_new: float) -> str:
    """Sticky-by-user routing. Same user_id maps to the same bucket for a
    given percent, so a user doesn't flip models request to request."""
    h = int(hashlib.sha256(user_id.encode()).hexdigest()[:8], 16)
    bucket = (h % 10000) / 100.0  # 0.00 .. 99.99
    return "model-new" if bucket < percent_new else "model-old"


async def shadow_route(prompt: str, user_id: str, call_model, shadow_log,
                       timeout: float = 30.0) -> dict:
    """Serve the OLD model to the user; run NEW in the background and log a
    diff. Returns immediately with the old response."""
    old_resp = await call_model("model-old", prompt)
    new_task = asyncio.create_task(call_model("model-new", prompt))
    asyncio.create_task(_log_shadow(user_id, prompt, old_resp, new_task,
                                    shadow_log, timeout))
    return {"response": old_resp["text"], "model": "model-old"}


async def _log_shadow(user_id, prompt, old_resp, new_task, shadow_log, timeout):
    try:
        new_resp = await asyncio.wait_for(new_task, timeout=timeout)
    except asyncio.TimeoutError:
        new_resp = {"text": None, "error": "timeout"}
    await shadow_log({
        "user_id": user_id,
        "prompt_hash": hashlib.sha256(prompt.encode()).hexdigest()[:16],
        "old_text": old_resp["text"],
        "new_text": new_resp.get("text"),
        "new_error": new_resp.get("error"),
        "diverged": old_resp["text"] != new_resp.get("text"),
    })

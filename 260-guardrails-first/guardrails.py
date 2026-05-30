"""Guardrails-first agent scaffolding.

Companion code for the AmtocSoft post "Guardrails-First: Making AI Agents
Reliable at 3am". Four cheap layers wrap a fallible model and turn every
failure mode from unbounded into bounded:

    1. Budget        - hard ceiling on steps / tokens / time / cost
    2. Validation    - tool allowlist + typed argument checks
    3. Circuit break - trip on repeated identical failure
    4. Recovery      - typed policy: retry / re-propose / escalate

Pure standard library. No external dependencies.
"""

from __future__ import annotations

import hashlib
import re
import time
from dataclasses import dataclass, field
from typing import Callable


# --------------------------------------------------------------------------
# Layer 1: Budget
# --------------------------------------------------------------------------
@dataclass
class Budget:
    max_steps: int = 25
    max_tokens: int = 200_000
    max_seconds: float = 300.0
    max_usd: float = 1.50
    started_at: float = field(default_factory=time.monotonic)
    steps: int = 0
    tokens: int = 0
    usd: float = 0.0

    def charge(self, tokens: int, usd: float) -> None:
        self.steps += 1
        self.tokens += tokens
        self.usd += usd

    def exceeded(self) -> str | None:
        if self.steps >= self.max_steps:
            return f"step limit {self.max_steps} reached"
        if self.tokens >= self.max_tokens:
            return f"token limit {self.max_tokens} reached"
        if time.monotonic() - self.started_at >= self.max_seconds:
            return f"time limit {self.max_seconds}s reached"
        if self.usd >= self.max_usd:
            return f"cost limit ${self.max_usd} reached"
        return None


# --------------------------------------------------------------------------
# Layer 3: Repeat-failure circuit breaker
# --------------------------------------------------------------------------
def normalize_error(error: str) -> str:
    """Collapse cosmetic variation (ids, timestamps, row numbers) so that
    'lock timeout on row 4471' and 'lock timeout on row 4472' hash alike."""
    error = re.sub(r"\b[0-9a-f]{8}-[0-9a-f-]{27,}\b", "<uuid>", error)
    error = re.sub(r"\b\d{4}-\d{2}-\d{2}[t ][\d:.]+\b", "<ts>", error)
    error = re.sub(r"\d+", "N", error)
    return error.strip().lower()


class RepeatFailureBreaker:
    def __init__(self, threshold: int = 2):
        self.threshold = threshold
        self.counts: dict[str, int] = {}

    def signature(self, action: str, error: str) -> str:
        raw = f"{action}|{normalize_error(error)}".encode()
        return hashlib.sha256(raw).hexdigest()[:4]

    def record(self, action: str, error: str) -> bool:
        """Return True if the breaker should trip."""
        sig = self.signature(action, error)
        self.counts[sig] = self.counts.get(sig, 0) + 1
        return self.counts[sig] > self.threshold


# --------------------------------------------------------------------------
# Layer 2: Action validation (allowlist + typed checks)
# --------------------------------------------------------------------------
ALLOWED_TABLES = {"orders", "customers", "line_items"}


def validate_run_sql(args: dict) -> str | None:
    sql = args.get("sql", "").strip().lower()
    if not sql.startswith(("select", "update", "insert")):
        return "only SELECT/UPDATE/INSERT permitted, no DDL or DROP"
    if not any(t in sql for t in ALLOWED_TABLES):
        return f"query must target an allowed table: {sorted(ALLOWED_TABLES)}"
    if sql.startswith("update") and "where" not in sql:
        return "UPDATE without WHERE clause is blocked"
    return None


VALIDATORS: dict[str, Callable[[dict], str | None]] = {
    "run_sql": validate_run_sql,
}


def validate(tool: str, args: dict) -> str | None:
    if tool not in VALIDATORS:
        return f"tool '{tool}' is not on the allowlist"
    return VALIDATORS[tool](args)


# --------------------------------------------------------------------------
# Layer 4 + loop: budget + validate + breaker + escalation
# --------------------------------------------------------------------------
def escalate(task: str, history: list[dict], reason: str) -> dict:
    destructive = sum(1 for h in history if h.get("result", {}).get("destructive"))
    return {
        "status": "escalated",
        "task": task,
        "reason": reason,
        "steps": len(history),
        "destructive_actions": destructive,
        "handoff": history[-3:],
    }


def run_agent(task: str, propose, execute, budget: Budget) -> dict:
    """Run the agent loop with all four guardrail layers.

    propose(task, history) -> {"tool", "args", "tokens", "usd"}   (model call)
    execute(tool, args)     -> {"ok": bool, "error"?: str, "task_done"?: bool}
    """
    breaker = RepeatFailureBreaker(threshold=2)
    history: list[dict] = []

    while True:
        halt = budget.exceeded()
        if halt:
            return escalate(task, history, reason=halt)

        step = propose(task, history)
        budget.charge(step["tokens"], step["usd"])

        err = validate(step["tool"], step["args"])
        if err:
            history.append({"rejected": step, "error": err})
            if breaker.record(step["tool"], err):
                return escalate(task, history, reason=f"repeated invalid: {err}")
            continue

        result = execute(step["tool"], step["args"])
        if not result["ok"]:
            history.append({"action": step, "error": result["error"]})
            if breaker.record(step["tool"], result["error"]):
                return escalate(task, history, reason=f"repeated failure: {result['error']}")
            continue

        history.append({"action": step, "result": result})
        if result.get("task_done"):
            return {"status": "done", "steps": budget.steps, "history": history}

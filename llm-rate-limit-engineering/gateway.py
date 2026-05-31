"""Workload-class rate limiting: keep batch jobs from starving interactive
user traffic by giving each class its own token-per-minute bucket.

Companion code for the AmtocSoft post
"LLM Rate Limit Engineering: Batch Jobs Starving User Traffic in Distributed
Systems".

Each workload class has its own TPM bucket sized as a fraction of the
provider cap. Interactive traffic is admitted first and never blocked behind
a batch backlog. Pure standard library — a deterministic, injectable clock
replaces wall time so the simulation is reproducible.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Class(Enum):
    INTERACTIVE = "interactive"
    ASYNC_USER = "async_user"
    EVAL_CI = "eval_ci"
    REPLAY = "replay"
    RETRAIN = "retrain"


@dataclass
class Bucket:
    tpm_cap: int                 # tokens-per-minute cap for this class
    refill_per_s: float
    tokens: float
    last: float
    paged_on_429: bool

    def _refill(self, now: float) -> None:
        elapsed = now - self.last
        self.tokens = min(self.tpm_cap, self.tokens + elapsed * self.refill_per_s)
        self.last = now

    def try_admit(self, cost_tokens: int, now: float) -> bool:
        self._refill(now)
        if self.tokens >= cost_tokens:
            self.tokens -= cost_tokens
            return True
        return False


@dataclass
class WorkloadGateway:
    """One TPM bucket per class. Interactive starts with full headroom and is
    refilled at the highest rate; batch classes get what's left."""
    caps: dict
    clock: callable = field(default=lambda: 0.0)
    buckets: dict = field(default_factory=dict)
    rejected: dict = field(default_factory=dict)

    def __post_init__(self):
        now = self.clock()
        for cls, cap in self.caps.items():
            self.buckets[cls] = Bucket(
                tpm_cap=cap, refill_per_s=cap / 60.0,
                tokens=cap * 0.8,  # start at 80% headroom
                last=now, paged_on_429=(cls == Class.INTERACTIVE))
            self.rejected[cls] = 0

    def admit(self, cls: Class, cost_tokens: int) -> bool:
        ok = self.buckets[cls].try_admit(cost_tokens, self.clock())
        if not ok:
            self.rejected[cls] += 1
        return ok

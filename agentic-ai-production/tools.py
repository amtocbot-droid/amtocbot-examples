"""Production-grade tool results and a token budget — the two lessons the
post's early adopters learned the hard way.

Companion code for the AmtocSoft post
"Agentic AI in Production: Lessons From Early Adopters".

A naive tool returns `response.json()["status"]` and explodes on the first
non-200. A production tool returns a typed `ToolResult` the agent loop can
reason about (retry vs give up). And a `TokenBudget` stops a runaway loop
before it burns the month's spend.

The post uses pydantic + requests; this uses a stdlib dataclass and a fake
HTTP client so it runs with no dependencies.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class ToolResult:
    status: str                       # "success" | "error"
    data: Any = None
    error_type: Optional[str] = None  # "transient" | "permanent" | "rate_limit"
    retry_safe: bool = False
    message: str = ""


def classify_http(status_code: int, body: Any) -> ToolResult:
    """Turn an HTTP status into a typed result the agent can act on."""
    if status_code == 200:
        return ToolResult(status="success", data=body)
    if status_code == 429:
        return ToolResult(status="error", error_type="rate_limit",
                          retry_safe=True, message="Rate limit hit. Retry after 60s.")
    if status_code >= 500:
        return ToolResult(status="error", error_type="transient",
                          retry_safe=True, message=f"Server error {status_code}.")
    if status_code == 404:
        return ToolResult(status="error", error_type="permanent",
                          retry_safe=False, message="Not found.")
    return ToolResult(status="error", error_type="permanent",
                      retry_safe=False, message=f"Unexpected status {status_code}.")


def get_order_status(order_id: str, http) -> ToolResult:
    """http is any callable (order_id) -> (status_code, body). Injected so the
    example needs no network."""
    try:
        code, body = http(order_id)
    except TimeoutError:
        return ToolResult(status="error", error_type="transient",
                          retry_safe=True, message="Request timed out.")
    return classify_http(code, body)


class TokenBudget:
    def __init__(self, total_budget: int, warning_threshold: float = 0.75):
        self.total = total_budget
        self.warning_threshold = warning_threshold
        self.used = 0

    def check(self, estimated_tokens: int) -> str:
        ratio = (self.used + estimated_tokens) / self.total
        if ratio > 1.0:
            return "EXCEEDED"
        if ratio > self.warning_threshold:
            return "WARNING"
        return "OK"

    def consume(self, tokens_used: int) -> None:
        self.used += tokens_used

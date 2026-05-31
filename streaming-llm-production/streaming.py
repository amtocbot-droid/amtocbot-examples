"""Production streaming concerns: backpressure, cancellation, and a
partial-response audit record.

Companion code for the AmtocSoft post
"Streaming LLM Responses in Production: Backpressure, Cancellation,
Partial-Response Audit".

The post streams from Anthropic over FastAPI with anyio backpressure. This
models the same control flow with asyncio and a fake token source so it runs
standalone: a bounded queue applies backpressure, client disconnect cancels
the stream, and whatever was emitted is written to an audit log with the
correct finish_reason. Pure standard library (asyncio).
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass


@dataclass
class AuditRecord:
    audit_id: str
    partial_response: str
    finish_reason: str   # "stop" | "client_disconnect" | "cancelled"
    tokens_emitted: int


class FakeModelStream:
    """Yields tokens with an await point, like a real SSE token stream."""

    def __init__(self, tokens: list[str]):
        self.tokens = tokens

    async def __aiter__(self):
        for t in self.tokens:
            await asyncio.sleep(0)  # cooperative yield point
            yield t


async def stream_response(audit_id: str, tokens: list[str], is_disconnected,
                          on_chunk, max_buffer: int = 4) -> AuditRecord:
    """Stream tokens with backpressure (bounded queue) and disconnect-aware
    cancellation, returning the audit record for whatever was emitted.

    is_disconnected() -> bool   client liveness check (injected)
    on_chunk(str)               sink for the emitted SSE chunk (injected)
    """
    queue: asyncio.Queue = asyncio.Queue(maxsize=max_buffer)
    emitted: list[str] = []
    finish_reason = "stop"
    SENTINEL = object()

    async def producer():
        nonlocal finish_reason
        async for tok in FakeModelStream(tokens):
            if is_disconnected():
                finish_reason = "client_disconnect"
                break
            await queue.put(tok)   # blocks when buffer full -> backpressure
        await queue.put(SENTINEL)

    async def consumer():
        nonlocal finish_reason
        while True:
            tok = await queue.get()
            if tok is SENTINEL:
                break
            if is_disconnected():
                finish_reason = "client_disconnect"
                break
            emitted.append(tok)
            on_chunk(tok)

    prod = asyncio.create_task(producer())
    try:
        await consumer()
    except asyncio.CancelledError:
        finish_reason = "cancelled"
        raise
    finally:
        prod.cancel()

    return AuditRecord(audit_id, "".join(emitted), finish_reason, len(emitted))

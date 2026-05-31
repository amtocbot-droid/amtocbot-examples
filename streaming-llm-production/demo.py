"""Stream to completion, then stream with a mid-flight client disconnect, and
show the audit record for each.

    $ python3 demo.py
"""

from __future__ import annotations

import asyncio

from streaming import stream_response

TOKENS = ["Hel", "lo ", "wor", "ld ", "this ", "is ", "a ", "stream."]


async def main() -> None:
    chunks: list[str] = []
    rec = await stream_response("a1", TOKENS, is_disconnected=lambda: False,
                                on_chunk=chunks.append)
    print(f"complete: reason={rec.finish_reason} tokens={rec.tokens_emitted}")
    print(f"  body: {rec.partial_response!r}")
    assert rec.finish_reason == "stop" and rec.tokens_emitted == len(TOKENS)

    # Disconnect after 3 chunks.
    seen = {"n": 0}

    def disconnected():
        seen["n"] += 1
        return seen["n"] > 3

    chunks2: list[str] = []
    rec2 = await stream_response("a2", TOKENS, is_disconnected=disconnected,
                                 on_chunk=chunks2.append)
    print(f"\ndisconnected: reason={rec2.finish_reason} tokens={rec2.tokens_emitted}")
    print(f"  partial body audited: {rec2.partial_response!r}")
    assert rec2.finish_reason == "client_disconnect"
    assert rec2.tokens_emitted < len(TOKENS)
    print("\nOK: backpressure + disconnect handled; partial response audited.")


if __name__ == "__main__":
    asyncio.run(main())

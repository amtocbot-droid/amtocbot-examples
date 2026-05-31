"""Tests. Run: python3 test_streaming.py"""

from __future__ import annotations

import asyncio

from streaming import stream_response

TOKENS = ["a", "b", "c", "d", "e"]


def run(coro):
    return asyncio.run(coro)


def test_full_stream_completes():
    rec = run(stream_response("x", TOKENS, lambda: False, lambda c: None))
    assert rec.finish_reason == "stop"
    assert rec.partial_response == "abcde"
    assert rec.tokens_emitted == 5


def test_disconnect_audits_partial():
    seen = {"n": 0}

    def disc():
        seen["n"] += 1
        return seen["n"] > 2

    rec = run(stream_response("x", TOKENS, disc, lambda c: None))
    assert rec.finish_reason == "client_disconnect"
    assert rec.tokens_emitted < 5


def test_chunks_match_emitted():
    chunks = []
    rec = run(stream_response("x", TOKENS, lambda: False, chunks.append))
    assert "".join(chunks) == rec.partial_response


def test_empty_stream():
    rec = run(stream_response("x", [], lambda: False, lambda c: None))
    assert rec.tokens_emitted == 0 and rec.finish_reason == "stop"


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"ok  {name}")
    print("\nall tests passed")

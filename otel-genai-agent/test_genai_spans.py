"""Tests. Run: python3 test_genai_spans.py"""

from __future__ import annotations

from genai_spans import (
    InMemoryTracer, Span, call_llm, validate_chat_span,
    GEN_AI_SYSTEM, GEN_AI_REQUEST_MODEL, GEN_AI_USAGE_OUTPUT_TOKENS,
    GEN_AI_TOOL_NAME,
)


def test_chat_span_is_conformant():
    t = InMemoryTracer()
    call_llm(t, [{"role": "user", "content": "x"}])
    assert validate_chat_span(t.spans[0]) == []


def test_span_records_request_model():
    t = InMemoryTracer()
    call_llm(t, [], model="claude-sonnet-4-6", system="anthropic")
    span = t.spans[0]
    assert span.attributes[GEN_AI_REQUEST_MODEL] == "claude-sonnet-4-6"
    assert span.attributes[GEN_AI_SYSTEM] == "anthropic"


def test_tool_attributes_set_when_tool_used():
    t = InMemoryTracer()
    call_llm(t, [], tool={"name": "search", "id": "c1"})
    assert t.spans[0].attributes[GEN_AI_TOOL_NAME] == "search"


def test_validator_flags_missing_attributes():
    incomplete = Span("chat x", {GEN_AI_SYSTEM: "openai"})
    missing = validate_chat_span(incomplete)
    assert GEN_AI_REQUEST_MODEL in missing
    assert GEN_AI_USAGE_OUTPUT_TOKENS in missing


def test_usage_tokens_recorded():
    t = InMemoryTracer()
    usage = call_llm(t, [])
    assert usage["input_tokens"] > 0 and usage["output_tokens"] > 0


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"ok  {name}")
    print("\nall tests passed")

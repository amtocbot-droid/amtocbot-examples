"""Emit a chat span and a tool span, then validate they're conformant.

    $ python3 demo.py
"""

from __future__ import annotations

from genai_spans import (
    InMemoryTracer, call_llm, validate_chat_span,
    GEN_AI_USAGE_INPUT_TOKENS, GEN_AI_TOOL_NAME,
)


def main() -> None:
    tracer = InMemoryTracer()
    call_llm(tracer, [{"role": "user", "content": "hi"}], conversation_id="c1")
    call_llm(tracer, [{"role": "user", "content": "look up order"}],
             tool={"name": "get_order", "id": "call_1"}, conversation_id="c1")

    for span in tracer.spans:
        missing = validate_chat_span(span)
        status = "conformant" if not missing else f"MISSING {missing}"
        print(f"{span.name:<28} {status}")
        print(f"  input_tokens={span.attributes[GEN_AI_USAGE_INPUT_TOKENS]}")
        if GEN_AI_TOOL_NAME in span.attributes:
            print(f"  tool={span.attributes[GEN_AI_TOOL_NAME]}")

    assert all(not validate_chat_span(s) for s in tracer.spans)
    print("\nOK: every span carries the required gen_ai.* attributes.")


if __name__ == "__main__":
    main()

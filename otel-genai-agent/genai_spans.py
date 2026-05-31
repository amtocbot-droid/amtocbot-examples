"""Emit OpenTelemetry GenAI-convention spans for LLM calls — without pulling
in the OTel SDK.

Companion code for the AmtocSoft post
"OpenTelemetry GenAI Conventions: LLM Span Attributes".

The post wires the real OTel SDK + OTLP exporter. The portable part is
*which attributes to set* and *what a conformant span looks like*. This
module provides the GenAI semantic-convention attribute keys, a tiny
in-memory tracer that records spans, and a validator that checks a span
carries the required gen_ai.* attributes. Pure standard library.
"""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass, field

# GenAI semantic-convention attribute keys (semconv).
GEN_AI_SYSTEM = "gen_ai.system"
GEN_AI_OPERATION_NAME = "gen_ai.operation.name"
GEN_AI_REQUEST_MODEL = "gen_ai.request.model"
GEN_AI_RESPONSE_MODEL = "gen_ai.response.model"
GEN_AI_USAGE_INPUT_TOKENS = "gen_ai.usage.input_tokens"
GEN_AI_USAGE_OUTPUT_TOKENS = "gen_ai.usage.output_tokens"
GEN_AI_RESPONSE_FINISH_REASONS = "gen_ai.response.finish_reasons"
GEN_AI_RESPONSE_ID = "gen_ai.response.id"
GEN_AI_TOOL_NAME = "gen_ai.tool.name"
GEN_AI_TOOL_CALL_ID = "gen_ai.tool.call.id"

# Minimum set a chat span must carry to be useful for cost/quality dashboards.
REQUIRED_FOR_CHAT = [
    GEN_AI_SYSTEM, GEN_AI_OPERATION_NAME, GEN_AI_REQUEST_MODEL,
    GEN_AI_USAGE_INPUT_TOKENS, GEN_AI_USAGE_OUTPUT_TOKENS,
]


@dataclass
class Span:
    name: str
    attributes: dict = field(default_factory=dict)

    def set_attribute(self, key: str, value) -> None:
        self.attributes[key] = value


class InMemoryTracer:
    def __init__(self):
        self.spans: list[Span] = []

    @contextmanager
    def start_as_current_span(self, name: str, attributes: dict | None = None):
        span = Span(name, dict(attributes or {}))
        try:
            yield span
        finally:
            self.spans.append(span)


def call_llm(tracer: InMemoryTracer, messages, model="gpt-4o-2024-11-20",
             system="openai", tool=None, conversation_id=None) -> dict:
    """Mock LLM call that emits a GenAI-conformant span. Returns a fake usage
    payload (no network)."""
    with tracer.start_as_current_span(
        f"chat {model}",
        attributes={
            GEN_AI_SYSTEM: system,
            GEN_AI_OPERATION_NAME: "chat",
            GEN_AI_REQUEST_MODEL: model,
            "gen_ai.conversation.id": conversation_id,
        },
    ) as span:
        # Pretend we called the model; fill response-side attributes.
        usage = {"input_tokens": 1200, "output_tokens": 256,
                 "finish_reason": "stop", "id": "resp_abc"}
        span.set_attribute(GEN_AI_RESPONSE_MODEL, model)
        span.set_attribute(GEN_AI_USAGE_INPUT_TOKENS, usage["input_tokens"])
        span.set_attribute(GEN_AI_USAGE_OUTPUT_TOKENS, usage["output_tokens"])
        span.set_attribute(GEN_AI_RESPONSE_FINISH_REASONS, [usage["finish_reason"]])
        span.set_attribute(GEN_AI_RESPONSE_ID, usage["id"])
        if tool:
            span.set_attribute(GEN_AI_TOOL_NAME, tool["name"])
            span.set_attribute(GEN_AI_TOOL_CALL_ID, tool["id"])
        return usage


def validate_chat_span(span: Span) -> list[str]:
    """Return missing required attributes ([] = conformant)."""
    return [k for k in REQUIRED_FOR_CHAT if k not in span.attributes]

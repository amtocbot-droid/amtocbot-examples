"""Observable AI agents: a nested span tree for an agent run, with per-call
token and cost attributes.

Companion code for the AmtocSoft post
"Observable AI Agents with OpenTelemetry".

The post wires the real OTel SDK + OTLP exporter. The reusable part is the
*shape* of the trace (agent_run > node > llm_call/tool_call) and the cost
calculation from the model pricing table. This builds that span tree in
memory so you can see and assert on it. Pure standard library.
"""

from __future__ import annotations

from dataclasses import dataclass, field

# Pricing per 1K tokens ($), as of the post (April 2026).
MODEL_COST = {
    "gpt-4o": {"input": 0.0025, "output": 0.010},
    "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
    "claude-sonnet-4-6": {"input": 0.003, "output": 0.015},
}


def call_cost(model: str, prompt_tokens: int, completion_tokens: int) -> float:
    p = MODEL_COST[model]
    return p["input"] * prompt_tokens / 1000 + p["output"] * completion_tokens / 1000


@dataclass
class Span:
    name: str
    attributes: dict = field(default_factory=dict)
    children: list = field(default_factory=list)

    def child(self, name: str, **attrs) -> "Span":
        s = Span(name, dict(attrs))
        self.children.append(s)
        return s

    def walk(self):
        yield self
        for c in self.children:
            yield from c.walk()

    def total_cost(self) -> float:
        return sum(s.attributes.get("llm.cost_usd", 0.0) for s in self.walk())

    def total_tokens(self) -> int:
        return sum(s.attributes.get("llm.prompt_tokens", 0)
                   + s.attributes.get("llm.completion_tokens", 0)
                   for s in self.walk())


def traced_llm_call(parent: Span, model: str, node_name: str,
                    prompt_tokens: int, completion_tokens: int,
                    latency_ms: int) -> Span:
    cost = call_cost(model, prompt_tokens, completion_tokens)
    return parent.child(
        f"llm_call:{model}",
        **{"llm.model": model, "agent.node": node_name,
           "llm.prompt_tokens": prompt_tokens,
           "llm.completion_tokens": completion_tokens,
           "llm.latency_ms": latency_ms, "llm.cost_usd": round(cost, 6)})


def render(span: Span, indent: int = 0) -> str:
    line = "  " * indent + span.name
    cost = span.attributes.get("llm.cost_usd")
    if cost is not None:
        line += f"  (${cost:.5f})"
    out = [line]
    for c in span.children:
        out.append(render(c, indent + 1))
    return "\n".join(out)

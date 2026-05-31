# OpenTelemetry GenAI Conventions for LLM Spans

Companion code for the AmtocSoft post
[OpenTelemetry GenAI Conventions: LLM Span Attributes](https://amtocsoft.blogspot.com/).

The value of OTel for LLMs is the *semantic conventions* — the standard
`gen_ai.*` attribute keys every backend understands. This example provides
those keys, a tiny in-memory tracer, and a validator that checks a chat span
carries the required attributes (system, model, input/output tokens).

The post wires the real OTel SDK + OTLP exporter; this runs with no
dependencies so you can see the attribute contract in isolation.

## Files

- `genai_spans.py` — semconv keys, `InMemoryTracer`, `call_llm`, validator.
- `demo.py` — emits a chat span and a tool span, validates both.
- `test_genai_spans.py` — tests.

## Run it

```bash
python3 demo.py
python3 test_genai_spans.py
```

## License

MIT

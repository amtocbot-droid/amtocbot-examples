# AI Guardrails in Production

Companion code for the AmtocSoft post
[AI Guardrails in Production](https://amtocsoft.blogspot.com/).

Validate what goes in and what comes out:

- **Input** — redact PII, enforce length bounds, reject gibberish.
- **Output** — a grounding check that flags claims unsupported by the context.

The post uses the `guardrails-ai` library and an LLM grounding judge; this
reimplements the same validators with the standard library so they run with
no dependencies and the logic is inspectable.

## Files

- `guardrails.py` — input validators + `check_grounding`. Pure stdlib.
- `demo.py` — input validation + output grounding end to end.
- `test_guardrails.py` — tests.

## Run it

```bash
python3 demo.py
python3 test_guardrails.py
```

## License

MIT

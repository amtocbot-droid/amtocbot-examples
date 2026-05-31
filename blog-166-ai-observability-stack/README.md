# The AI Observability Stack 2026

Companion code for the AmtocSoft post
[The AI Observability Stack 2026: Langfuse, Arize, Portkey, Splunk](https://amtocsoft.blogspot.com/).

Two runnable pieces from the post:

1. **Tool selection** — score Langfuse / Arize / Portkey / Splunk against
   your weighted requirements and get a ranked recommendation.
2. **Offline eval pass** — run hallucination checks over a window of recorded
   traces and decide whether to page on-call.

The eval uses rule-based evaluators (the post uses Phoenix/Arize + an LLM
judge) so it runs with no dependencies.

## Files

- `obs_stack.py` — `recommend_tools`, `run_eval_pass`. Pure stdlib.
- `demo.py` — recommendations for two teams + an eval pass that pages.
- `test_obs_stack.py` — tests.

## Run it

```bash
python3 demo.py
python3 test_obs_stack.py
```

## License

MIT

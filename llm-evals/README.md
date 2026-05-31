# LLM Evaluation in Production

Companion code for the AmtocSoft post
[LLM Evaluation in Production](https://amtocsoft.blogspot.com/).

Three layers of evaluation, cheapest first:

1. **Format checks** — deterministic, fast, catch the dumb failures.
2. **Semantic similarity** — does the answer mean the same as the reference?
3. **LLM-as-judge** — rubric scoring for accuracy / helpfulness / tone.

The post uses a real judge model and sentence-transformers; this version
uses a transparent rule-based judge and a hashing embedding so it runs with
no dependencies. The `eval_ticket_classification` check is verbatim.

## Files

- `evals.py` — the three layers. Pure stdlib.
- `run_evals.py` — runs all three against a golden set.
- `test_evals.py` — tests.

## Run it

```bash
python3 run_evals.py
python3 test_evals.py
```

## License

MIT

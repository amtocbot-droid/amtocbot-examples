# LLM Evals in CI

Working code companion for [LLM Evals in CI: How to Test AI Output Without Flakiness](https://amtocsoft.blogspot.com/2026/06/llm-evals-ci-testing.html).

## What's here

| File | Purpose |
|------|---------|
| `tests/test_structure.py` | Layer 1: deterministic structure tests against golden files |
| `tests/test_regression.py` | Layer 2: golden-set regression tests |
| `tests/judge.py` | Layer 3: LLM-as-judge implementation |
| `tests/test_semantic.py` | Layer 3: pytest test using the judge |
| `scripts/generate_golden_set.py` | Script to generate/regenerate the golden fixture set |
| `tests/eval/golden/` | Sample golden response fixtures for a ticket classifier |
| `.github/workflows/llm-evals.yml` | GitHub Actions config wiring all three layers |

## Quickstart

```bash
# Layer 1 + 2: no API keys needed
pip install pytest
pytest tests/test_structure.py tests/test_regression.py -v

# Layer 3: requires OPENAI_API_KEY
export OPENAI_API_KEY=sk-...
pytest tests/test_semantic.py -m llm_judge -v

# Regenerate golden set (run when you update a prompt intentionally)
export OPENAI_API_KEY=sk-...
python scripts/generate_golden_set.py
```

## The three-layer strategy

```
Layer 4: Human review (periodic)
Layer 3: LLM-as-judge — semantic quality, pennies/run, on merge to main
Layer 2: Golden regression — catches category drift, free, every commit
Layer 1: Structure tests — schema validation, free, every commit
```

Layers 1 and 2 never hit the API. Ship them today.

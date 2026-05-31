# Context Engineering as Infrastructure: The 2026 Field Guide

Companion code for the AmtocSoft post
[Context Engineering as Infrastructure](https://amtocsoft.blogspot.com/).

A small, real context assembler that treats the model's input window as
infrastructure: curate, rank, fit a token budget, and log provenance.

| Stage | What it does |
|-------|--------------|
| `blended_score` | Score chunks on similarity + recency + authority, not cosine alone |
| `dedupe` | Drop near-identical chunks via shingled Jaccard similarity |
| `assemble` | Greedily fill a token budget, apply a relevance floor, position the best chunk nearest the question, and record everything dropped |

## Files

- `context_pipeline.py` — the pipeline. Pure standard library.
- `demo_assemble.py` — reproduces the stale-chunk bug from the post being caught by the relevance floor and budget log.
- `test_context_pipeline.py` — unit tests for scoring, dedupe, budget, and floor.

## Run it

```bash
python3 demo_assemble.py             # stale changelog dropped, policy positioned last
python3 test_context_pipeline.py     # run the tests
```

## License

MIT

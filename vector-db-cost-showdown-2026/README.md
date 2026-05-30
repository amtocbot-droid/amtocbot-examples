# Vector Database Cost Showdown 2026

Companion code for the AmtocSoft post
[Vector Database Cost Showdown 2026: pgvector, Pinecone, Weaviate, Qdrant](https://amtocsoft.blogspot.com/).

Two things the post argues, made runnable:

1. **Cost is dominated by RAM-to-hold-the-index, not by the engine logo.**
   `cost_model.py` factors the showdown into a single model — change the
   workload, re-run the comparison for your own corpus.
2. **Recall must be measured against brute-force ground truth.**
   `recall_benchmark.py` reproduces the Recall@20 spot-check methodology
   (exact cosine ground truth vs an HNSW-style greedy graph index).

## Files

- `cost_model.py` — monthly TCO model for the four engines. Pure stdlib.
- `recall_benchmark.py` — Recall@k of an approximate index vs brute force.
- `test_showdown.py` — tests for both.

## Run it

```bash
python3 cost_model.py          # the showdown table
python3 recall_benchmark.py    # Recall@20 ~ 99% on the toy corpus
python3 test_showdown.py       # tests
```

## License

MIT

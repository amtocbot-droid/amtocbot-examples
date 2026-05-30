# AI Memory Systems: Building Agents That Remember

Companion code for the AmtocSoft post
[AI Memory Systems: Building Agents That Remember](https://amtocsoft.blogspot.com/).

A runnable agent memory store: store/retrieve with the post's
similarity + recency + frequency scoring, plus the contradiction-detection
scan. The post uses pgvector and an embedding API; this version swaps in a
deterministic hashing embedding and an in-memory list so it runs with no
dependencies. `compute_memory_score` is the formula verbatim from the post.

## Files

- `memory_store.py` — the store, scoring, and contradiction scan. Pure stdlib.
- `demo.py` — store memories, retrieve, detect a contradiction.
- `test_memory_store.py` — tests.

## Run it

```bash
python3 demo.py
python3 test_memory_store.py
```

## License

MIT

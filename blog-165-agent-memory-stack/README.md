# AI Agent Memory Patterns: Semantic, Episodic, Procedural

Companion code for the AmtocSoft post
[AI Agent Memory Patterns: Semantic, Episodic, Procedural](https://amtocsoft.blogspot.com/).

Three distinct memory patterns, each with its own read/write shape:

- **Semantic** — durable user facts, retrieved by similarity.
- **Episodic** — threaded events, read at `summary` or `raw` depth.
- **Procedural** — a skill registry with an LLM-as-router selector.

The post uses pgvector + an LLM router; this version uses an in-memory
store with a hashing embedding and a transparent keyword router so it runs
with no dependencies.

## Files

- `memory_stack.py` — the three patterns. Pure stdlib.
- `demo.py` — exercises all three.
- `test_memory_stack.py` — tests.

## Run it

```bash
python3 demo.py
python3 test_memory_stack.py
```

## License

MIT

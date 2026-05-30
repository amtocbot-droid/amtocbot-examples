# Tiered Memory Agent

Companion code for the AmtocSoft post
[Context Window Limits and the Memory Myth](https://amtocsoft.blogspot.com/).

A bigger context window is not a memory system. This example shows the
three-tier alternative: **working** memory (in-context), **episodic** memory
(vector store), and **semantic** memory (structured facts), with a router
that decides which tiers a query needs.

The post uses Chroma and a Haiku router; this version uses an in-memory
store with a hashing embedding and a transparent keyword router so it runs
with no dependencies.

## Files

- `memory_tiers.py` — the three tiers + query router. Pure stdlib.
- `demo.py` — routes three queries to the right tiers.
- `test_memory_tiers.py` — tests.

## Run it

```bash
python3 demo.py
python3 test_memory_tiers.py
```

## License

MIT

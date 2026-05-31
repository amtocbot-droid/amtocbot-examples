# Zero-Downtime Embedding Model Migration

Companion code for the AmtocSoft post
[Embedding Model Migration: Production Reindex of a RAG Corpus With Zero Downtime](https://amtocsoft.blogspot.com/).

Swapping embedding models means re-embedding the whole corpus without taking
search down. The pattern: a **blue/green** index pair, **dual-write** every
live update to both, and an **idempotent, resumable backfill** that fills
GREEN from BLUE — then cut over only once GREEN mirrors every current row.

The post uses asyncpg + OpenAI; this models the migration over two in-memory
indexes with a deterministic fake embedder so the logic runs standalone.

## Files

- `migration.py` — blue/green indexes, dual-write, backfill, cutover gate.
- `demo.py` — seed → batched resumable backfill → mid-flight update → cutover.
- `test_migration.py` — tests.

## Run it

```bash
python3 demo.py
python3 test_migration.py
```

## License

MIT

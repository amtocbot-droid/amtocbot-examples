# LLM Prompt Cache Strategies

Companion code for the AmtocSoft post
[LLM Prompt Cache Strategies: Anthropic, OpenAI, Self-Hosted, Hit-Rate Optimisation](https://amtocsoft.blogspot.com/).

The hit rate is the whole game. These scripts show the one mistake that
tanks it — volatile content (time, tenant id) inside the cached prefix —
and the byte-stable builder that fixes it.

## Files

- `prefix_cache.py` — broken vs stable prompt builders + `cache_stats`.
- `simulate_hit_rate.py` — fleet-wide hit rate for each builder.
- `test_prefix_cache.py` — tests.

## Run it

```bash
python3 prefix_cache.py          # per-call hit rate / savings log line
python3 simulate_hit_rate.py     # broken 0% vs stable ~99%
python3 test_prefix_cache.py
```

## License

MIT

# Prompt Caching for LLM Cost Optimization

Companion code for the AmtocSoft post
[Prompt Caching for LLM Cost Optimization](https://amtocsoft.blogspot.com/).

A large shared prefix (a contract, a system prompt, tool defs) re-sent on
every call is the single biggest line item you can cut. These scripts make
the economics and the #1 gotcha concrete.

## Files

- `estimate_cost.py` — the monthly cost CLI from the post.
- `cache_sim.py` — shows how a timestamp in the cached prefix drops the hit
  rate to 0%, and how normalizing the prefix fixes it.
- `test_caching.py` — tests, including the post's $810 / $729 headline.

## Run it

```bash
python3 estimate_cost.py --tokens 40000 --calls 15 --sessions 90
python3 cache_sim.py
python3 test_caching.py
```

## License

MIT

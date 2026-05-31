# MCP Marketplace: Lessons From the 2014 API Gold Rush

Companion code for the AmtocSoft post
[MCP Marketplace: Lessons From the 2014 API Gold Rush](https://amtocsoft.blogspot.com/).

The post is an analysis piece. Its concrete, testable takeaway is a
checklist: the API listings that *survived* the 2014 gold rush had
versioning, scoped auth, documented rate limits, a deprecation policy, a
changelog, and working examples. This turns those survivors' traits into a
runnable MCP listing-quality scorer.

## Files

- `listing_quality.py` — `score_listing` against the gold-rush lessons.
- `demo.py` — a mature listing (approve) vs a rushed one (reject).
- `test_listing_quality.py` — tests.

## Run it

```bash
python3 demo.py
python3 test_listing_quality.py
```

## License

MIT

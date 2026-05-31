# Streaming LLM Responses in Production

Companion code for the AmtocSoft post
[Streaming LLM Responses in Production: Backpressure, Cancellation, Partial-Response Audit](https://amtocsoft.blogspot.com/).

Three things a naive `for chunk in stream` misses:

- **Backpressure** — a bounded queue so a slow client can't make you buffer
  the whole response in memory.
- **Cancellation** — stop generating the moment the client disconnects.
- **Partial-response audit** — record what was actually emitted, with the
  correct `finish_reason` (stop / client_disconnect / cancelled).

The post uses Anthropic + FastAPI + anyio; this models the same control flow
with asyncio and a fake token source so it runs standalone.

## Files

- `streaming.py` — `stream_response` with backpressure + audit. Pure stdlib.
- `demo.py` — a complete stream and a mid-flight disconnect.
- `test_streaming.py` — tests.

## Run it

```bash
python3 demo.py
python3 test_streaming.py
```

## License

MIT

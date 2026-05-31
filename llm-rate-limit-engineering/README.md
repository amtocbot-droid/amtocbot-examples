# LLM Rate Limit Engineering

Companion code for the AmtocSoft post
[LLM Rate Limit Engineering: Batch Jobs Starving User Traffic in Distributed Systems](https://amtocsoft.blogspot.com/).

The failure: a retrain or replay batch burns the shared provider TPM and
interactive users start getting 429s. The fix: one token-per-minute bucket
per **workload class**, so batch load can only starve itself.

## Files

- `gateway.py` — per-class `Bucket` + `WorkloadGateway`. Pure stdlib with an
  injectable clock (no asyncio needed for the core admission logic).
- `simulate_starvation.py` — a 100-request retrain burst that leaves
  interactive traffic fully admitted.
- `test_gateway.py` — tests.

## Run it

```bash
python3 simulate_starvation.py
python3 test_gateway.py
```

## License

MIT

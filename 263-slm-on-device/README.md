# SLMs On-Device: Pick, Quantize, and Ship a Small Language Model

Companion code for the AmtocSoft post
[SLMs On-Device](https://amtocsoft.blogspot.com/).

Route tasks between a local small language model and a cloud fallback, and do
the memory math before committing to a model + quant.

| Piece | What it does |
|-------|--------------|
| `fits_in_memory` | Back-of-envelope: weights + KV cache + runtime reserve vs target RAM |
| `is_hard` / `route` | Send the bulk to a local SLM; escalate only the hard tail to the cloud |
| `local_generate` | Optional Ollama call (network-isolated so the rest runs offline) |

## Files

- `slm_router.py` — router + memory math. Pure standard library.
- `demo_route_batch.py` — routes a 1000-task batch; ~95% stays local. Runs offline (stubbed model).
- `test_slm_router.py` — tests for the heuristics and the memory math.

## Run it

```bash
python3 demo_route_batch.py       # local/cloud split + memory fit table
python3 test_slm_router.py        # run the tests
```

To use a real local model, install [Ollama](https://ollama.com/), run
`ollama pull phi4-mini`, and call `local_generate(...)`.

## License

MIT

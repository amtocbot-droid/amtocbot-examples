# Mixture of Experts Architecture for LLMs

Companion code for the AmtocSoft post
[Mixture of Experts Architecture for LLMs](https://amtocsoft.blogspot.com/).

The post inspects Mixtral's routing with torch hooks. The portable ideas run
here with no torch:

- **Top-k gating** — each token is routed to its top-k experts via softmax.
- **Expert collapse** — without balancing, utilization skews onto a few
  experts.
- **Load-balancing loss** — the Switch-Transformer auxiliary loss
  (`num_experts * Σ f_i·P_i`) that pushes utilization back toward uniform.

## Files

- `moe.py` — `MoERouter` + `load_balancing_loss`. Pure stdlib.
- `demo.py` — balanced vs collapsed routing and their aux loss.
- `test_moe.py` — tests.

## Run it

```bash
python3 demo.py
python3 test_moe.py
```

## License

MIT

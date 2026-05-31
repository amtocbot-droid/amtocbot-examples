# LLM-as-a-Judge: Bias Correction & Calibration

Companion code for the AmtocSoft post
[LLM-as-a-Judge in Production: Eval Bias Correction, Human-Rater Calibration](https://amtocsoft.blogspot.com/).

Two things that make a judge trustworthy:

1. **Position-bias mitigation** — judge each pair twice with the order
   swapped; a win only counts if it survives the swap, else it's a TIE.
2. **Calibration** — measure judge/human agreement with Cohen's kappa before
   you let the judge gate anything.

The real judge is an LLM; here it's a deterministic rubric scorer so the
example runs with no dependencies and the bias logic is inspectable.

## Files

- `judge.py` — `judge_pair` (swap-consistent), `cohens_kappa`. Pure stdlib.
- `simulate_calibration.py` — bias flips a win to TIE; kappa reported.
- `test_judge.py` — tests.

## Run it

```bash
python3 simulate_calibration.py
python3 test_judge.py
```

## License

MIT

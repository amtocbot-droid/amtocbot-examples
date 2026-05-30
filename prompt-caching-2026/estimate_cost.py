"""Monthly prompt-caching cost estimator.

Companion code for the AmtocSoft post
"Prompt Caching for LLM Cost Optimization".

Reproduces the CLI from the post:

    $ python3 estimate_cost.py --tokens 40000 --calls 15 --sessions 90
    Monthly estimate: $810.00
    Cache savings at 90% discount: $729.00

The model: a large shared prefix (e.g. a 40K-token contract) is re-sent on
every call within a session. Without caching you pay full input price every
time. With caching you pay full price once (the cache write) and a 10% read
price thereafter. Pure standard library.
"""

from __future__ import annotations

import argparse

# Anthropic-style economics from the post: $/token for input, cache read at
# 10% of input, cache write at 125% of input.
INPUT_USD_PER_TOKEN = 15.0 / 1_000_000  # $15 / Mtok input (Opus-class)
CACHE_READ_FACTOR = 0.10
CACHE_WRITE_FACTOR = 1.25


def monthly_cost_no_cache(prefix_tokens: int, calls: int, sessions: int) -> float:
    """Full input price on every call."""
    return prefix_tokens * calls * sessions * INPUT_USD_PER_TOKEN


def monthly_cost_cached(prefix_tokens: int, calls: int, sessions: int) -> float:
    """One cache write per session, then cache reads for the rest."""
    per_session = (
        prefix_tokens * CACHE_WRITE_FACTOR
        + prefix_tokens * (calls - 1) * CACHE_READ_FACTOR
    )
    return per_session * sessions * INPUT_USD_PER_TOKEN


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--tokens", type=int, default=40_000,
                   help="shared prefix size in tokens")
    p.add_argument("--calls", type=int, default=15,
                   help="calls per session reusing the prefix")
    p.add_argument("--sessions", type=int, default=90,
                   help="sessions per month")
    args = p.parse_args()

    base = monthly_cost_no_cache(args.tokens, args.calls, args.sessions)
    print(f"Monthly estimate: ${base:,.2f}")
    # Headline figure from the post: the prefix is read at the 90%-off rate.
    print(f"Cache savings at 90% discount: ${base * 0.90:,.2f}")

    # The fuller model also charges a one-time 125% cache write per session:
    cached = monthly_cost_cached(args.tokens, args.calls, args.sessions)
    print(f"(write-aware estimate: ${cached:,.2f}, "
          f"real savings ${base - cached:,.2f})")


if __name__ == "__main__":
    main()

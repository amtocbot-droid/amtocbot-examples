"""Demonstrate the stale-chunk bug from the post being caught two ways:
the relevance floor (via blended scoring) and the budget log.

    $ python demo_assemble.py
"""

from __future__ import annotations

from context_pipeline import Chunk, assemble, blended_score, estimate_tokens

# (source, text, similarity, age_days, authority)
RAW = [
    ("policy/refunds-v3.md", "Refunds apply to all physical goods within the return window; digital goods are non-refundable.", 0.91, 12, 1.0),
    ("faq/refund-window.md", "Our refund window is documented in the help center for eligible purchases.", 0.88, 40, 0.8),
    ("policy/shipping.md", "Shipping times vary by region and selected carrier service level.", 0.71, 30, 0.9),
    ("kb/returns-process.md", "To start a return, open the order and choose return for an eligible item.", 0.66, 25, 0.7),
    ("chat/turn-14.md", "Earlier the customer mentioned they bought a digital download.", 0.61, 0, 0.5),
    ("changelog/2025-q3.md", "Q3 2025 changelog: legacy refund terms applied to all goods historically.", 0.83, 240, 0.4),
]


def main() -> None:
    chunks = []
    for source, text, sim, age, auth in RAW:
        tokens = estimate_tokens(text)
        score = blended_score(sim, age, auth, tokens)
        chunks.append(Chunk(source=source, text=text, score=score, tokens=tokens))

    print("blended scores:")
    for c in sorted(chunks, key=lambda c: c.score, reverse=True):
        print(f"  {c.source:28s} score={c.score:.2f}  {c.tokens} tok")

    floor = 0.55
    result = assemble(chunks, budget_tokens=80, relevance_floor=floor)

    print(f"\nassembled (floor={floor}, budget=80 tok), strongest LAST:")
    for c in result.blocks:
        print(f"  {c.source:28s} score={c.score:.2f}")
    print("dropped:")
    for d in result.dropped:
        print(f"  {d}")
    print(f"used {result.used_tokens}/80 tokens")

    stale_dropped = any("changelog/2025-q3.md" in d for d in result.dropped)
    assert stale_dropped, "the stale changelog should be dropped"
    assert result.blocks[-1].source == "policy/refunds-v3.md", "best chunk nearest question"
    print("\nOK: stale changelog dropped; authoritative policy positioned nearest the question.")


if __name__ == "__main__":
    main()

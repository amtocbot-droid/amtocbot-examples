"""Run the migration: seed BLUE, backfill GREEN in resumable batches, dual-
write a live update mid-flight, and only cut over when GREEN is complete.

    $ python3 demo.py
"""

from __future__ import annotations

from migration import Migration, Doc


def main() -> None:
    docs = {f"d{i:02d}": Doc(f"d{i:02d}", f"document number {i}") for i in range(6)}
    m = Migration()
    for d in docs.values():
        m.write_old(d)
    print(f"BLUE seeded: {len(m.blue.rows)} docs; GREEN empty; "
          f"complete={m.green_complete()}")
    assert not m.green_complete()

    # Backfill in batches of 2; resumable via checkpoint.
    rounds = 0
    while not m.green_complete():
        n = m.backfill(docs, batch_size=2)
        rounds += 1
        print(f"  round {rounds}: backfilled {n}, checkpoint={m.checkpoint}")
        # A live update arrives mid-migration -> dual-write keeps both fresh.
        if rounds == 1:
            docs["d00"] = Doc("d00", "document number 0 (edited)")
            m.dual_write(docs["d00"])

    print(f"GREEN complete: {m.green_complete()} after {rounds} rounds")
    assert m.green_complete()

    # Backfill is idempotent: re-running writes nothing new.
    m.checkpoint = ""
    assert m.backfill(docs, batch_size=0) == 0
    print("re-running backfill is a no-op (idempotent)")
    print("\nOK: dual-write + resumable idempotent backfill, safe cutover.")


if __name__ == "__main__":
    main()

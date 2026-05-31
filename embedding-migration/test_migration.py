"""Tests. Run: python3 test_migration.py"""

from __future__ import annotations

from migration import Migration, Doc, embed, text_hash, OLD_MODEL, NEW_MODEL


def _seed(n=6):
    docs = {f"d{i:02d}": Doc(f"d{i:02d}", f"document {i}") for i in range(n)}
    m = Migration()
    for d in docs.values():
        m.write_old(d)
    return m, docs


def test_models_produce_different_vectors():
    a = embed(OLD_MODEL, "hello", 1536)
    b = embed(NEW_MODEL, "hello", 3072)
    assert len(a) == 1536 and len(b) == 3072 and a[:10] != b[:10]


def test_green_incomplete_before_backfill():
    m, _ = _seed()
    assert m.green_complete() is False


def test_backfill_completes_green():
    m, docs = _seed()
    while not m.green_complete():
        m.backfill(docs, batch_size=2)
    assert m.green_complete()


def test_backfill_is_idempotent():
    m, docs = _seed()
    m.backfill(docs, batch_size=0)        # full pass
    m.checkpoint = ""
    assert m.backfill(docs, batch_size=0) == 0


def test_backfill_resumes_from_checkpoint():
    m, docs = _seed(4)
    first = m.backfill(docs, batch_size=2)
    assert first == 2 and m.checkpoint == "d01"
    second = m.backfill(docs, batch_size=2)
    assert second == 2 and m.green_complete()


def test_dual_write_keeps_both_fresh():
    m, docs = _seed(2)
    m.backfill(docs, batch_size=0)
    docs["d00"] = Doc("d00", "edited text")
    m.dual_write(docs["d00"])
    th = text_hash("edited text")
    assert m.blue.has_current("d00", th) and m.green.has_current("d00", th)


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"ok  {name}")
    print("\nall tests passed")

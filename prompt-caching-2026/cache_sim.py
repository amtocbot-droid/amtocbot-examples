"""Simulate the cache hit/miss behaviour the post warns about: a dynamic
value (timestamp) in the cached prefix silently destroys every cache hit.

    $ python3 cache_sim.py

Models the API's prefix-cache: the cache key is a hash of the prefix bytes.
If the prefix is byte-stable across calls, every call after the first is a
hit. If you interpolate a timestamp into it, every call is a miss.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field


@dataclass
class PrefixCache:
    seen: set[str] = field(default_factory=set)
    writes: int = 0
    reads: int = 0

    def lookup(self, prefix: str) -> bool:
        key = hashlib.sha256(prefix.encode()).hexdigest()
        if key in self.seen:
            self.reads += 1
            return True
        self.seen.add(key)
        self.writes += 1
        return False

    def hit_rate(self) -> float:
        total = self.reads + self.writes
        return self.reads / total if total else 0.0


# BROKEN: dynamic content in the cached prefix (the post's gotcha).
def prepare_document_broken(doc_text: str, call_no: int) -> str:
    timestamp = f"2026-05-30T10:{call_no:02d}:00"  # changes every call
    return f"<!-- Processed: {timestamp} -->\n{doc_text}"


# FIXED: normalize only, no dynamic content in the cached prefix.
def prepare_document_fixed(doc_text: str, call_no: int) -> str:
    return doc_text.strip()


def simulate(prepare, calls: int = 15) -> PrefixCache:
    doc = "Here is a 40K-token legal contract ..." * 100
    cache = PrefixCache()
    for i in range(calls):
        cache.lookup(prepare(doc, i))
    return cache


def main() -> None:
    broken = simulate(prepare_document_broken)
    fixed = simulate(prepare_document_fixed)
    print(f"Broken prefix (timestamp inside cache boundary):")
    print(f"  writes={broken.writes}  reads={broken.reads}  "
          f"hit rate={broken.hit_rate():.0%}")
    print(f"Fixed prefix (dynamic content moved out):")
    print(f"  writes={fixed.writes}  reads={fixed.reads}  "
          f"hit rate={fixed.hit_rate():.0%}")

    assert broken.hit_rate() == 0.0, "dynamic prefix must never hit"
    assert fixed.reads == 14 and fixed.writes == 1
    print("\nOK: stable prefix turns 15 cold calls into 1 write + 14 reads.")


if __name__ == "__main__":
    main()

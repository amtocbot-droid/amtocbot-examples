"""Zero-downtime embedding-model migration: blue/green indexes, dual-write,
and an idempotent, resumable backfill.

Companion code for the AmtocSoft post
"Embedding Model Migration: Production Reindex of a RAG Corpus With Zero
Downtime".

The post uses asyncpg + OpenAI; this models the same migration over two
in-memory indexes (BLUE = old model, GREEN = new model) with a deterministic
fake embedder, so the *migration logic* — dual-write, idempotent backfill,
checkpoint/resume, and cutover — runs standalone. Pure standard library.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field

OLD_MODEL = "text-embedding-ada-002"     # 1536 dims
NEW_MODEL = "text-embedding-3-large"     # 3072 dims


def embed(model: str, text: str, dim: int) -> list[float]:
    """Deterministic fake embedding; different per model so BLUE != GREEN."""
    seed = f"{model}:{text}"
    out = []
    h = hashlib.sha256(seed.encode()).digest()
    while len(out) < dim:
        h = hashlib.sha256(h).digest()
        out.extend(b / 255.0 for b in h)
    return out[:dim]


def text_hash(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


@dataclass
class Doc:
    id: str
    text: str
    tenant_id: str = "t1"


@dataclass
class Index:
    """One vector index. Rows keyed by doc id; each holds (text_hash, vec)."""
    rows: dict = field(default_factory=dict)

    def upsert(self, doc_id: str, th: str, vec: list[float]) -> None:
        self.rows[doc_id] = (th, vec)

    def has_current(self, doc_id: str, th: str) -> bool:
        return self.rows.get(doc_id, (None,))[0] == th


class Migration:
    def __init__(self):
        self.blue = Index()    # old model
        self.green = Index()   # new model
        self.checkpoint: str = ""  # last backfilled id

    def write_old(self, doc: Doc) -> None:
        """Normal production write before migration starts (BLUE only)."""
        self.blue.upsert(doc.id, text_hash(doc.text),
                         embed(OLD_MODEL, doc.text, 1536))

    def dual_write(self, doc: Doc) -> None:
        """During migration: write both indexes for any new/updated doc."""
        th = text_hash(doc.text)
        self.blue.upsert(doc.id, th, embed(OLD_MODEL, doc.text, 1536))
        self.green.upsert(doc.id, th, embed(NEW_MODEL, doc.text, 3072))

    def backfill(self, docs: dict[str, Doc], batch_size: int = 2) -> int:
        """Walk BLUE in id order from the checkpoint, embed missing rows into
        GREEN. Idempotent (skips rows GREEN already has at the same hash) and
        resumable (advances self.checkpoint). Returns rows written."""
        written = 0
        ids = sorted(i for i in self.blue.rows if i > self.checkpoint)
        for doc_id in ids[:batch_size] if batch_size else ids:
            th, _ = self.blue.rows[doc_id]
            if not self.green.has_current(doc_id, th):
                self.green.upsert(doc_id, th,
                                  embed(NEW_MODEL, docs[doc_id].text, 3072))
                written += 1
            self.checkpoint = doc_id
        return written

    def green_complete(self) -> bool:
        """Cutover gate: GREEN must mirror every current BLUE row."""
        return all(self.green.has_current(i, th)
                   for i, (th, _) in self.blue.rows.items())

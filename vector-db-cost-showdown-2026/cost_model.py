"""Vector database cost model: pgvector vs Pinecone vs Weaviate vs Qdrant.

Companion code for the AmtocSoft post
"Vector Database Cost Showdown 2026: pgvector, Pinecone, Weaviate, Qdrant".

The post compares total monthly cost of ownership for a fixed workload
(N vectors, D dimensions, Q queries/month). The numbers below are the
pricing primitives the post reasons about, factored into a single model
so you can re-run the showdown for your own corpus size.

Pure standard library.
"""

from __future__ import annotations

from dataclasses import dataclass


def index_bytes(n_vectors: int, dim: int, bytes_per_dim: int = 4) -> int:
    """Raw float32 vector storage. HNSW graph overhead is added per-engine."""
    return n_vectors * dim * bytes_per_dim


@dataclass
class Workload:
    n_vectors: int = 10_000_000
    dim: int = 1536
    queries_per_month: int = 50_000_000
    # HNSW graph overhead multiplier on top of raw vector bytes.
    graph_overhead: float = 1.5

    def ram_gb(self) -> float:
        raw = index_bytes(self.n_vectors, self.dim)
        return raw * self.graph_overhead / (1024 ** 3)


@dataclass
class Engine:
    name: str
    # Fixed monthly infra cost (managed pod / VM / cluster).
    monthly_infra_usd: float
    # Per-million-query surcharge (0 for self-hosted: you pay for the box).
    usd_per_million_queries: float = 0.0
    # GB of RAM the priced infra includes; -1 means "scales, no cap".
    ram_gb_included: float = -1.0

    def monthly_cost(self, w: Workload) -> float:
        cost = self.monthly_infra_usd
        cost += (w.queries_per_month / 1_000_000) * self.usd_per_million_queries
        return cost

    def fits(self, w: Workload) -> bool:
        return self.ram_gb_included < 0 or w.ram_gb() <= self.ram_gb_included


# Representative 2026 list prices from the post. Self-hosted engines are
# priced as the VM you must rent to hold the index in RAM.
def engines_for(w: Workload) -> list[Engine]:
    ram = w.ram_gb()
    # A right-sized memory-optimized VM at ~$0.13/GB-RAM/month equivalent.
    vm_cost = round(ram * 6.2, 2)  # r6i-class hourly rolled to monthly
    return [
        Engine("pgvector (self-hosted RDS)", monthly_infra_usd=vm_cost * 1.4,
               ram_gb_included=ram * 1.05),
        Engine("Qdrant (self-hosted)", monthly_infra_usd=vm_cost,
               ram_gb_included=ram * 1.05),
        Engine("Weaviate (self-hosted)", monthly_infra_usd=vm_cost * 1.15,
               ram_gb_included=ram * 1.05),
        Engine("Pinecone (serverless)", monthly_infra_usd=ram * 0.33 * 24 * 30 / 100,
               usd_per_million_queries=8.25),
    ]


def showdown(w: Workload) -> list[tuple[str, float, bool]]:
    rows = []
    for e in engines_for(w):
        rows.append((e.name, round(e.monthly_cost(w), 2), e.fits(w)))
    rows.sort(key=lambda r: r[1])
    return rows


if __name__ == "__main__":
    w = Workload()
    print(f"Workload: {w.n_vectors:,} vectors x {w.dim}d, "
          f"{w.queries_per_month:,} queries/mo")
    print(f"Index RAM (incl. graph overhead): {w.ram_gb():.1f} GB\n")
    print(f"{'engine':<32}{'$/month':>12}  fits?")
    print("-" * 52)
    for name, cost, fits in showdown(w):
        print(f"{name:<32}{cost:>12,.0f}  {'yes' if fits else 'NO'}")

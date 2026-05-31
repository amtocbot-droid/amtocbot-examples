"""Route a batch of tasks and report the local/cloud split and estimated
savings. Uses a stub local model so it runs offline (no Ollama required).

    $ python demo_route_batch.py
"""

from __future__ import annotations

from slm_router import fits_in_memory, route

# A realistic mix: mostly short summaries (local), a few hard ones (cloud).
TASKS = (
    ["Summarize: the app crashes on launch after the update."] * 947
    + ["Analyze the tradeoffs of switching our queue from SQS to Kafka, step by step."] * 53
)


def stub_local(task: str) -> str:
    return "Local summary: " + task[:40]


def stub_cloud(task: str) -> str:
    return "Cloud answer: " + task[:40]


def main() -> None:
    # 1) memory math first, before committing to a model
    print("memory fit (7B @ Q4_K_M, 16GB laptop):")
    for ctx in (8192, 32768, 131072):
        ok, needed = fits_in_memory(7, 0.6, ctx, total_ram_gb=16)
        print(f"  context {ctx:>6}: needs {needed:>5}GB -> {'FITS' if ok else 'too big'}")

    # 2) route the batch
    local = cloud = 0
    for t in TASKS:
        r = route(t, cloud_fallback=stub_cloud, local_fn=stub_local)
        if r["engine"] == "local":
            local += 1
        else:
            cloud += 1

    total = local + cloud
    share = 100.0 * local / total
    # illustrative cost model: cloud ~ $0.004/call, local $0
    cost_per_cloud_call = 0.004
    all_cloud_cost = total * cost_per_cloud_call
    hybrid_cost = cloud * cost_per_cloud_call
    print(f"\nrouted {total} tasks: local={local}, cloud={cloud}")
    print(f"local share: {share:.1f}%")
    print(f"batch cost: all-cloud ${all_cloud_cost:.2f} vs hybrid ${hybrid_cost:.2f} "
          f"({100*(1-hybrid_cost/all_cloud_cost):.0f}% cheaper)")

    assert share > 90, "bulk should route local"
    print("\nOK: bulk stayed local and private; only the hard tail escalated.")


if __name__ == "__main__":
    main()

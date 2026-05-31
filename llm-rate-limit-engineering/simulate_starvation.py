"""Show the core result: a retrain batch hammering the gateway does NOT
starve interactive traffic, because each class draws from its own bucket.

    $ python3 simulate_starvation.py
"""

from __future__ import annotations

from gateway import WorkloadGateway, Class


class FakeClock:
    def __init__(self):
        self.t = 0.0

    def __call__(self):
        return self.t


def main() -> None:
    clock = FakeClock()
    # Provider cap split across classes (tokens/minute).
    caps = {
        Class.INTERACTIVE: 60_000,
        Class.ASYNC_USER: 30_000,
        Class.RETRAIN: 30_000,
    }
    gw = WorkloadGateway(caps=caps, clock=clock)

    # A retrain batch fires 100 large requests in the same instant.
    for _ in range(100):
        gw.admit(Class.RETRAIN, cost_tokens=2_000)

    # Interactive users arrive in that same instant. They must still get in.
    interactive_admitted = sum(gw.admit(Class.INTERACTIVE, 500) for _ in range(40))

    print(f"retrain rejected (bucket drained):   {gw.rejected[Class.RETRAIN]}")
    print(f"interactive admitted despite batch:  {interactive_admitted}/40")

    # Interactive has its own 60k bucket at 80% = 48k tokens -> 96 x 500 fit.
    assert interactive_admitted == 40, "interactive must not be starved"
    assert gw.rejected[Class.RETRAIN] > 0, "retrain should hit its own cap"
    print("\nOK: per-class buckets isolate batch load from interactive traffic.")


if __name__ == "__main__":
    main()

"""Tests. Run: python3 test_gateway.py"""

from __future__ import annotations

from gateway import WorkloadGateway, Class, Bucket


class FakeClock:
    def __init__(self, t=0.0):
        self.t = t

    def __call__(self):
        return self.t


def test_bucket_admits_until_drained():
    b = Bucket(tpm_cap=1000, refill_per_s=1000 / 60, tokens=1000, last=0.0,
               paged_on_429=False)
    assert b.try_admit(600, now=0.0) is True
    assert b.try_admit(600, now=0.0) is False  # only 400 left


def test_bucket_refills_over_time():
    b = Bucket(tpm_cap=600, refill_per_s=10.0, tokens=0.0, last=0.0,
               paged_on_429=False)
    assert b.try_admit(100, now=0.0) is False
    assert b.try_admit(100, now=20.0) is True  # 20s * 10/s = 200 tokens


def test_interactive_not_starved_by_batch():
    clock = FakeClock()
    gw = WorkloadGateway(caps={Class.INTERACTIVE: 60_000, Class.RETRAIN: 30_000},
                         clock=clock)
    for _ in range(100):
        gw.admit(Class.RETRAIN, 2_000)
    admitted = sum(gw.admit(Class.INTERACTIVE, 500) for _ in range(40))
    assert admitted == 40


def test_batch_hits_own_cap():
    clock = FakeClock()
    gw = WorkloadGateway(caps={Class.RETRAIN: 30_000}, clock=clock)
    for _ in range(100):
        gw.admit(Class.RETRAIN, 2_000)
    assert gw.rejected[Class.RETRAIN] > 0


def test_interactive_bucket_is_paged():
    gw = WorkloadGateway(caps={Class.INTERACTIVE: 10, Class.REPLAY: 10},
                         clock=FakeClock())
    assert gw.buckets[Class.INTERACTIVE].paged_on_429 is True
    assert gw.buckets[Class.REPLAY].paged_on_429 is False


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"ok  {name}")
    print("\nall tests passed")

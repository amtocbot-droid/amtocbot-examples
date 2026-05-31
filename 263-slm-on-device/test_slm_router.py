"""Tests for the SLM router and memory math. Run: python test_slm_router.py"""

from __future__ import annotations

from slm_router import fits_in_memory, is_hard, route


def test_short_task_is_not_hard():
    assert is_hard("Summarize this transcript in one line.") is False


def test_reasoning_cue_is_hard():
    assert is_hard("Walk me through the proof step by step.") is True


def test_long_task_is_hard():
    assert is_hard("x" * 6001) is True


def test_route_local_for_easy():
    r = route("summarize this", cloud_fallback=lambda t: "CLOUD",
              local_fn=lambda t: "LOCAL")
    assert r["engine"] == "local" and r["output"] == "LOCAL"


def test_route_cloud_for_hard():
    r = route("write code to do X", cloud_fallback=lambda t: "CLOUD",
              local_fn=lambda t: "LOCAL")
    assert r["engine"] == "cloud" and r["output"] == "CLOUD"


def test_memory_fits_small_context():
    ok, needed = fits_in_memory(7, 0.6, 8192, total_ram_gb=16)
    assert ok and needed < 16


def test_memory_too_big_long_context():
    ok, needed = fits_in_memory(7, 0.6, 1_000_000, total_ram_gb=16)
    assert not ok and needed > 16


def test_smaller_model_fits_where_bigger_does_not():
    big_ok, _ = fits_in_memory(13, 0.6, 8192, total_ram_gb=12)
    small_ok, _ = fits_in_memory(3, 0.6, 8192, total_ram_gb=12)
    assert small_ok and not big_ok


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"ok  {name}")
    print("\nall tests passed")

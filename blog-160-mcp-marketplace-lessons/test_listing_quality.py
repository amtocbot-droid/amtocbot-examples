"""Tests. Run: python3 test_listing_quality.py"""

from __future__ import annotations

from listing_quality import Listing, score_listing, LESSONS


def _full():
    return Listing("x", versioned=True, auth_scoped=True,
                   rate_limits_documented=True, deprecation_policy=True,
                   changelog=True, example_calls=True)


def test_weights_sum_to_one():
    assert abs(sum(w for _, w, _ in LESSONS) - 1.0) < 1e-9


def test_full_listing_approved():
    r = score_listing(_full())
    assert r["score"] == 1.0 and r["grade"] == "approve" and not r["missing"]


def test_empty_listing_rejected():
    r = score_listing(Listing("x"))
    assert r["grade"] == "reject"


def test_missing_versioning_lowers_grade():
    l = _full()
    l.versioned = False
    r = score_listing(l)
    assert r["score"] == 0.75 and r["grade"] == "needs-work"
    assert any(f == "versioned" for f, _ in r["missing"])


def test_grade_thresholds():
    l = Listing("x", versioned=True, deprecation_policy=True, auth_scoped=True)
    # 0.25 + 0.20 + 0.20 = 0.65 -> needs-work
    assert score_listing(l)["grade"] == "needs-work"


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"ok  {name}")
    print("\nall tests passed")

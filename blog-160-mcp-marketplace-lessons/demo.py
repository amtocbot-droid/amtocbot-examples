"""Score a mature listing and a gold-rush-style "ship it and pray" listing.

    $ python3 demo.py
"""

from __future__ import annotations

from listing_quality import Listing, score_listing


def main() -> None:
    mature = Listing("payments-mcp", versioned=True, auth_scoped=True,
                     rate_limits_documented=True, deprecation_policy=True,
                     changelog=True, example_calls=True)
    rushed = Listing("quickwin-mcp", versioned=False, auth_scoped=False,
                     rate_limits_documented=False, deprecation_policy=False,
                     changelog=False, example_calls=True)

    for listing in (mature, rushed):
        r = score_listing(listing)
        print(f"{r['name']:<16} score={r['score']:<5} grade={r['grade']}")
        for field, why in r["missing"]:
            print(f"    missing {field}: {why}")

    assert score_listing(mature)["grade"] == "approve"
    assert score_listing(rushed)["grade"] == "reject"
    print("\nOK: the gold-rush survivors' checklist, made enforceable.")


if __name__ == "__main__":
    main()

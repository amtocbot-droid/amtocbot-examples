"""Score an MCP server listing against the lessons the 2014 API gold rush
taught us — the ones the post argues MCP marketplaces are about to relearn.

Companion code for the AmtocSoft post
"MCP Marketplace: Lessons From the 2014 API Gold Rush".

The post is an analysis piece, not a code tutorial. Its concrete, testable
takeaway is a checklist: the API listings that survived the gold rush had
versioning, auth, documented rate limits, a deprecation policy, and a
changelog. This turns those lessons into a runnable listing-quality scorer.
Pure standard library.
"""

from __future__ import annotations

from dataclasses import dataclass

# Each lesson: a field that must be present/true, with a weight and the
# gold-rush failure it prevents.
LESSONS = [
    ("versioned", 0.25, "unversioned APIs broke every consumer on each change"),
    ("auth_scoped", 0.20, "all-or-nothing API keys leaked blast radius"),
    ("rate_limits_documented", 0.15, "undocumented limits caused surprise 429 storms"),
    ("deprecation_policy", 0.20, "no sunset policy meant zombie endpoints forever"),
    ("changelog", 0.10, "silent breaking changes destroyed trust"),
    ("example_calls", 0.10, "no examples meant nobody could integrate"),
]


@dataclass
class Listing:
    name: str
    versioned: bool = False
    auth_scoped: bool = False
    rate_limits_documented: bool = False
    deprecation_policy: bool = False
    changelog: bool = False
    example_calls: bool = False


def score_listing(listing: Listing) -> dict:
    score = 0.0
    missing = []
    for field, weight, why in LESSONS:
        if getattr(listing, field):
            score += weight
        else:
            missing.append((field, why))
    grade = ("approve" if score >= 0.8 else
             "needs-work" if score >= 0.5 else "reject")
    return {"name": listing.name, "score": round(score, 2),
            "grade": grade, "missing": missing}

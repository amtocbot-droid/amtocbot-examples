"""Summarize head-to-head AI-coding-tool runs into the comparison table from
the post. Reads result JSON files and prints a ranked summary.

Companion code for the AmtocSoft post "AI Coding Tools in 2026: Cursor,
Claude Code, Copilot, and Windsurf Compared". Pure standard library.

    $ python summarize_runs.py results/*.json
"""

from __future__ import annotations

import glob
import json
import sys


def parse_duration(s: str) -> int:
    """'8m12s' -> seconds. Accepts NmNNs or plain seconds."""
    s = s.strip()
    if "m" in s:
        mins, _, rest = s.partition("m")
        secs = int(rest.replace("s", "") or 0)
        return int(mins) * 60 + secs
    return int(s.replace("s", ""))


def fmt_duration(total: int) -> str:
    return f"{total // 60}m{total % 60:02d}s"


def load_runs(paths: list[str]) -> list[dict]:
    runs = []
    for p in paths:
        with open(p) as f:
            r = json.load(f)
        r["_seconds"] = parse_duration(r["time_to_green"])
        runs.append(r)
    return runs


def summarize(runs: list[dict]) -> str:
    # Rank by (corrections, time): fewest interventions first, then fastest.
    ranked = sorted(runs, key=lambda r: (r["manual_corrections"], r["_seconds"]))
    lines = [f"{'tool':<14}{'time_to_green':<16}{'manual_corrections':<22}notes"]
    for r in ranked:
        lines.append(
            f"{r['tool']:<14}{fmt_duration(r['_seconds']):<16}"
            f"{r['manual_corrections']:<22}{r.get('notes', '')}"
        )
    return "\n".join(lines)


def main(argv: list[str]) -> None:
    patterns = argv[1:] or ["results/*.json"]
    paths = sorted(p for pat in patterns for p in glob.glob(pat))
    if not paths:
        print("no result files found", file=sys.stderr)
        raise SystemExit(1)
    print(summarize(load_runs(paths)))


if __name__ == "__main__":
    main(sys.argv)

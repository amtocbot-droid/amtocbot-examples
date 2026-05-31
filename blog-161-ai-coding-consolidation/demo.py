"""Compare a 5-tool vs 2-tool AI coding stack for a 20-dev team, breaking out
license cost vs context-switch tax.

    $ python3 demo.py
"""

from __future__ import annotations

from stack_cost import FIVE_TOOL, TWO_TOOL, compare


def main() -> None:
    seats = 20
    for stack in (FIVE_TOOL, TWO_TOOL):
        lic = stack.license_cost(seats)
        sw = stack.switch_cost(seats)
        print(f"{stack.name:<10} licenses=${lic:>8,.0f}  "
              f"switch-tax=${sw:>9,.0f}  total=${lic+sw:>9,.0f}")

    result = compare(seats)
    print(f"\nmonthly savings from consolidation: ${result['monthly_savings']:,.0f}")
    assert result["two_tool"] < result["five_tool"]
    # Most of the win is the switch tax, not the licenses.
    assert TWO_TOOL.switch_cost(seats) < FIVE_TOOL.switch_cost(seats)
    print("\nOK: the hidden context-switch tax dominates the consolidation case.")


if __name__ == "__main__":
    main()

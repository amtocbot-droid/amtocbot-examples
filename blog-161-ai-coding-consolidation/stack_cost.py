"""Model the cost of an AI coding tool stack — per-seat dollars plus the
hidden tax of context-switching between tools.

Companion code for the AmtocSoft post
"AI Coding Tool Stack Consolidation: From Five Tools to Two".

The post's argument is that a sprawling 5-tool stack costs more than its
license fees suggest, because every tool boundary is a context switch. This
makes that argument quantitative: total monthly cost = seat licenses +
(context-switches/day * minutes/switch * working days * loaded hourly rate).
Pure standard library.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Tool:
    name: str
    monthly_seat_usd: float


@dataclass
class Stack:
    name: str
    tools: list
    switches_per_day: int          # tool-boundary crossings per dev per day
    minutes_per_switch: float = 3.0

    def license_cost(self, seats: int) -> float:
        return sum(t.monthly_seat_usd for t in self.tools) * seats

    def switch_cost(self, seats: int, hourly_usd: float = 90.0,
                    working_days: int = 21) -> float:
        hours = (self.switches_per_day * self.minutes_per_switch
                 * working_days * seats) / 60.0
        return hours * hourly_usd

    def total_monthly(self, seats: int, hourly_usd: float = 90.0) -> float:
        return self.license_cost(seats) + self.switch_cost(seats, hourly_usd)


FIVE_TOOL = Stack("five-tool", [
    Tool("copilot", 19), Tool("cursor", 20), Tool("tabnine", 12),
    Tool("sourcegraph", 49), Tool("standalone-chat", 20),
], switches_per_day=14)

TWO_TOOL = Stack("two-tool", [
    Tool("cursor", 20), Tool("claude-code", 100),
], switches_per_day=4)


def compare(seats: int, hourly_usd: float = 90.0) -> dict:
    five = FIVE_TOOL.total_monthly(seats, hourly_usd)
    two = TWO_TOOL.total_monthly(seats, hourly_usd)
    return {"five_tool": round(five, 2), "two_tool": round(two, 2),
            "monthly_savings": round(five - two, 2)}

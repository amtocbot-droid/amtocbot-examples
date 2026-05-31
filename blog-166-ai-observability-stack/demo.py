"""Recommend a tool for two different teams, then run an eval pass that pages
on a hallucination spike.

    $ python3 demo.py
"""

from __future__ import annotations

from obs_stack import recommend_tools, run_eval_pass, Trace


def main() -> None:
    # A team that cares most about evals/drift -> Arize-leaning.
    evals_team = {"tracing": 0.2, "evals": 0.6, "cost": 0.1, "siem": 0.1}
    # A security-driven org with SIEM mandate -> Splunk-leaning.
    secops = {"tracing": 0.2, "evals": 0.1, "cost": 0.1, "siem": 0.6}

    print("eval-first team:", recommend_tools(evals_team)[:2])
    print("secops team:    ", recommend_tools(secops)[:2])
    assert recommend_tools(evals_team)[0][0] == "arize"
    assert recommend_tools(secops)[0][0] == "splunk"

    traces = [Trace("cat sat on the mat in the kitchen", "the cat sat on the mat")] * 18
    traces += [Trace("cat sat on the mat", "the rocket launched to jupiter today")] * 4
    result = run_eval_pass(traces, page_threshold=0.15)
    print("\neval pass:", result)
    assert result["page_oncall"] is True
    print("\nOK: tool choice follows requirements; eval pass pages on a spike.")


if __name__ == "__main__":
    main()

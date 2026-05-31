"""Tests. Run: python3 test_obs_stack.py"""

from __future__ import annotations

from obs_stack import recommend_tools, run_eval_pass, Trace, is_hallucination


def test_evals_weighting_picks_arize():
    assert recommend_tools({"evals": 1.0})[0][0] == "arize"


def test_siem_weighting_picks_splunk():
    assert recommend_tools({"siem": 1.0})[0][0] == "splunk"


def test_cost_weighting_picks_portkey():
    assert recommend_tools({"cost": 1.0})[0][0] == "portkey"


def test_recommendation_is_ranked():
    ranked = recommend_tools({"tracing": 1.0})
    scores = [s for _, s in ranked]
    assert scores == sorted(scores, reverse=True)


def test_hallucination_detection():
    assert is_hallucination(Trace("cat on mat", "rocket to jupiter saturn galaxy"))
    assert not is_hallucination(Trace("cat sat on the mat", "the cat sat"))


def test_eval_pass_pages_above_threshold():
    traces = [Trace("a b c d", "rocket jupiter saturn")] * 5
    assert run_eval_pass(traces, page_threshold=0.15)["page_oncall"] is True


def test_eval_pass_quiet_when_clean():
    traces = [Trace("cat sat on the mat", "the cat sat on the mat")] * 20
    assert run_eval_pass(traces)["page_oncall"] is False


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"ok  {name}")
    print("\nall tests passed")

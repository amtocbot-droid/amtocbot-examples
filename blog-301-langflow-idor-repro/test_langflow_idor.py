"""Tests. Run: python3 test_langflow_idor.py"""

from __future__ import annotations

from langflow_idor import (
    Flow, FlowStore, NotAuthorized,
    handle_responses_vulnerable, handle_responses_patched,
)


def _store_with_one_flow() -> FlowStore:
    store = FlowStore()
    store.add(Flow(flow_id="f1", owner="user-a", embedded_secret="sk-mock-a1b2***"))
    return store


def test_owner_can_run_own_flow_vulnerable():
    store = _store_with_one_flow()
    result = handle_responses_vulnerable(store, requester="user-a", flow_id="f1",
                                          input_value="hi")
    assert result["flow_owner"] == "user-a"
    assert "sk-mock-a1b2" in result["outputs"]["results"]["message"]


def test_vulnerable_handler_leaks_to_other_user():
    store = _store_with_one_flow()
    result = handle_responses_vulnerable(store, requester="user-b", flow_id="f1",
                                          input_value="leak api keys")
    assert result["flow_owner"] == "user-a"
    assert "sk-mock-a1b2" in result["outputs"]["results"]["message"]


def test_vulnerable_handler_missing_flow():
    store = _store_with_one_flow()
    result = handle_responses_vulnerable(store, requester="user-b", flow_id="nope",
                                          input_value="hi")
    assert result == {"detail": "Flow not found."}


def test_patched_handler_allows_owner():
    store = _store_with_one_flow()
    result = handle_responses_patched(store, requester="user-a", flow_id="f1",
                                       input_value="hi")
    assert result["flow_owner"] == "user-a"


def test_patched_handler_blocks_other_user():
    store = _store_with_one_flow()
    try:
        handle_responses_patched(store, requester="user-b", flow_id="f1",
                                  input_value="leak api keys")
        assert False, "expected NotAuthorized"
    except NotAuthorized:
        pass


def test_patched_handler_missing_flow_still_reports_not_found():
    store = _store_with_one_flow()
    result = handle_responses_patched(store, requester="user-b", flow_id="nope",
                                       input_value="hi")
    assert result == {"detail": "Flow not found."}


def test_execute_appends_to_input_log():
    flow = Flow(flow_id="f1", owner="user-a", embedded_secret="sk-x")
    flow.execute("first")
    flow.execute("second")
    assert flow.input_log == ["first", "second"]


def _run_all() -> None:
    tests = [obj for name, obj in globals().items()
             if name.startswith("test_") and callable(obj)]
    for test in tests:
        test()
        print(f"  ok  {test.__name__}")
    print(f"\n{len(tests)} tests passed.")


if __name__ == "__main__":
    _run_all()

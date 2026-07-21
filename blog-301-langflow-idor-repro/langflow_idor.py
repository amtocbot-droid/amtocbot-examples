"""Model of the Langflow CVE-2026-55255 IDOR, vulnerable and patched.

Companion code for the AmtocSoft post
"Langflow Just Became the First AI Agent Platform on CISA's Must-Patch
List: What CVE-2026-55255 Means for Your Self-Hosted Stack".

The real bug: Langflow's `/api/v1/responses` endpoint (pre-1.9.1) executed
a flow identified by a client-supplied `flow_id`, without checking that
the requesting user actually owned that flow. Any authenticated user could
run any other user's flow, including whatever credentials that flow had
embedded.

This module models the same shape at the handler-function level: a
`Flow` holds an owner and an "embedded secret" (standing in for an API
key or DB connection string), and a `FlowStore` executes flows by id.
`handle_responses_vulnerable` reproduces the pre-1.9.1 behavior (no
ownership check). `handle_responses_patched` reproduces 1.9.1's fix (a
single ownership check before execution). No real Langflow install, HTTP
server, or network access required.

Pure standard library.
"""

from __future__ import annotations

from dataclasses import dataclass, field


class NotAuthorized(Exception):
    """Raised by the patched handler when the requester doesn't own the flow."""


@dataclass
class Flow:
    flow_id: str
    owner: str
    embedded_secret: str
    input_log: list = field(default_factory=list)

    def execute(self, input_value: str) -> dict:
        """Run the flow. In real Langflow this calls out to an LLM API,
        a database, a webhook, etc. using this flow's embedded credentials.
        Here it just proves which credential was used to serve the request.
        """
        self.input_log.append(input_value)
        return {
            "session_id": self.flow_id,
            "outputs": {
                "results": {
                    "message": f"processed '{input_value}' using key {self.embedded_secret}"
                }
            },
            "flow_owner": self.owner,
        }


class FlowStore:
    """In-memory stand-in for Langflow's flow table."""

    def __init__(self) -> None:
        self._flows: dict[str, Flow] = {}

    def add(self, flow: Flow) -> None:
        self._flows[flow.flow_id] = flow

    def get(self, flow_id: str) -> Flow | None:
        return self._flows.get(flow_id)


def handle_responses_vulnerable(store: FlowStore, requester: str, flow_id: str,
                                 input_value: str) -> dict:
    """Pre-1.9.1 `/api/v1/responses` behavior: fetch by id, execute, done.

    No check that `requester` is `flow.owner`. This is CVE-2026-55255 —
    the entire vulnerability is the absence of that one comparison.
    """
    flow = store.get(flow_id)
    if flow is None:
        return {"detail": "Flow not found."}
    return flow.execute(input_value)


def handle_responses_patched(store: FlowStore, requester: str, flow_id: str,
                              input_value: str) -> dict:
    """1.9.1+ `/api/v1/responses` behavior: same as above, plus one
    ownership check before execution. This is the entire fix from
    PR #12832.
    """
    flow = store.get(flow_id)
    if flow is None:
        return {"detail": "Flow not found."}
    if flow.owner != requester:
        raise NotAuthorized(f"{requester} is not authorized to access flow {flow_id!r}.")
    return flow.execute(input_value)

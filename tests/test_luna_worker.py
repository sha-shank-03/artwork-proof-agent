"""Deterministic transport tests. These are not genuine provider recordings."""
import asyncio
import copy
import json
import time
from types import SimpleNamespace

import pytest
from app.core import month, uid
from app.store import Store
from app.worker import MODEL, TOOLS, Worker, cost_micros
from test_safety import run, model_report


class Call(SimpleNamespace):
    def model_dump(self, **kwargs):
        return vars(self).copy()


class FakeClient:
    def __init__(self, calls, count=100):
        self.calls = iter(calls)
        self.count_value = count
        self.requests = []
        self.closed = False
        self.responses = SimpleNamespace(input_tokens=SimpleNamespace(count=self.count), create=self.create)

    async def count(self, **request):
        return SimpleNamespace(input_tokens=self.count_value)

    async def create(self, **request):
        self.requests.append(copy.deepcopy(request))
        call = next(self.calls)
        if isinstance(call, Exception):
            raise call
        name, args = call
        output = [Call(type="function_call", id=uid(), call_id=uid(), name=name,
                       arguments=args if isinstance(args, str) else json.dumps(args))]
        return SimpleNamespace(output=output, model=MODEL, status="completed",
                               usage=SimpleNamespace(input_tokens=100, output_tokens=20))

    async def close(self):
        self.closed = True


def seed():
    store = Store()
    r = {**run(), "leaseToken":uid(), "leaseUntil":time.time()+180, "model":MODEL,
         "messages":[], "inputTokens":0, "outputTokens":0,
         "inspectedMeasurements":False, "inspectedSpecs":False, "inspectedPages":[]}
    with store.transaction() as state:
        state["runs"][r["id"]] = r
    return store, r["id"], r["leaseToken"]


def execute(monkeypatch, fake, store, ident, lease):
    monkeypatch.setattr("app.worker.AsyncOpenAI", lambda **kwargs: fake)
    asyncio.run(Worker(store).run(ident, lease))
    with store.transaction() as state:
        return copy.deepcopy(state["runs"][ident])


def test_luna_full_tool_path_preserves_images_and_approval(monkeypatch):
    store, ident, lease = seed()
    fake = FakeClient([("inspect_measurements", {}), ("read_demo_specs", {}),
                       ("inspect_preview", {"page":1}), ("submit_report", model_report())])
    r = execute(monkeypatch, fake, store, ident, lease)
    assert r["state"] == "awaiting_approval" and r["receipt"] is None
    assert r["turns"] == 4 and r["usedMicros"] == 4*cost_micros(100,20)
    assert r["reservedMicros"] == 0 and fake.closed
    for request in fake.requests:
        assert request["model"] == MODEL and request["store"] is False
        assert request["reasoning"] == {"effort":"none"}
        assert request["parallel_tool_calls"] is False
        assert request["max_output_tokens"] == 1500
    outputs = [i for i in fake.requests[-1]["input"] if i.get("type")=="function_call_output"]
    image = outputs[-1]["output"][1]
    assert image["type"] == "input_image" and image["detail"] == "high"
    assert image["image_url"].startswith("data:image/png;base64,")
    calls = {i["call_id"] for i in r["messages"] if i.get("type")=="function_call"}
    assert all(o["call_id"] in calls for o in outputs)


def test_clarification_checkpoint_resumes_with_saved_tool_outputs(monkeypatch):
    store, ident, lease = seed()
    first = FakeClient([("ask_clarification", {"question":"Is the crop intentional?"})])
    paused = execute(monkeypatch, first, store, ident, lease)
    assert paused["state"] == "awaiting_input" and paused["leaseUntil"] == 0
    with store.transaction() as state:
        r=state["runs"][ident]; r["state"]="running";r["leaseUntil"]=time.time()+180
        r["messages"].append({"role":"user", "content":"Keep the crop."})
    second = FakeClient([("inspect_measurements",{}), ("read_demo_specs",{}),
                         ("inspect_preview",{"page":1}), ("submit_report",model_report())])
    r=execute(monkeypatch, second, store, ident, lease)
    assert r["state"] == "awaiting_approval" and r["turns"]==5
    assert any(i.get("type")=="function_call_output" for i in second.requests[0]["input"])


def test_malformed_arguments_are_repaired_without_approval(monkeypatch):
    store, ident, lease=seed()
    fake=FakeClient([("inspect_preview","{invalid"), ("ask_clarification",{"question":"Confirm crop?"})])
    r=execute(monkeypatch,fake,store,ident,lease)
    assert r["state"]=="awaiting_input" and r["receipt"] is None
    assert "error" in fake.requests[1]["input"][-1]["output"]


@pytest.mark.parametrize("count",[0,200001])
def test_unreviewed_context_stops_before_paid_call(monkeypatch,count):
    store,ident,lease=seed();fake=FakeClient([],count=count)
    r=execute(monkeypatch,fake,store,ident,lease)
    assert r["state"]=="failed" and r["turns"]==0 and not fake.requests


def test_uncertain_provider_failure_keeps_conservative_budget(monkeypatch):
    store,ident,lease=seed();fake=FakeClient([TimeoutError("private provider error")])
    r=execute(monkeypatch,fake,store,ident,lease)
    assert r["state"]=="failed" and r["usedMicros"]==cost_micros(100,1500)+1000
    assert r["reservedMicros"]==0 and "private provider error" not in r["error"]
    with store.transaction() as state:assert state["budgets"][month()]["reserved"]==0


def test_legacy_claude_run_is_not_silently_converted(monkeypatch):
    store,ident,lease=seed()
    with store.transaction() as state:state["runs"][ident]["model"]="claude-haiku-4-5-20251001"
    fake=FakeClient([]);r=execute(monkeypatch,fake,store,ident,lease)
    assert r["state"]=="failed" and r["turns"]==0 and not fake.requests


def test_strict_tools_and_integer_cost_ceiling():
    assert cost_micros(1,0)==1 and cost_micros(1000000,1000000)==1450000
    for tool in TOOLS:
        assert tool["strict"] is True
        assert tool["parameters"]["additionalProperties"] is False
        assert set(tool["parameters"]["required"])==set(tool["parameters"]["properties"])

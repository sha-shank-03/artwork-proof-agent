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
        self.messages = SimpleNamespace(count_tokens=self.count, create=self.create)

    async def count(self, **request):
        return SimpleNamespace(input_tokens=self.count_value)

    async def create(self, **request):
        self.requests.append(copy.deepcopy(request))
        call = next(self.calls)
        if isinstance(call, Exception):
            raise call
        name, args = call
        output = [Call(type="tool_use", id=uid(), name=name, input=args)]
        return SimpleNamespace(content=output, model=MODEL, stop_reason="tool_use",
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
    monkeypatch.setattr("app.worker.AsyncAnthropic", lambda **kwargs: fake)
    asyncio.run(Worker(store).run(ident, lease))
    with store.transaction() as state:
        return copy.deepcopy(state["runs"][ident])


def test_claude_full_tool_path_preserves_images_and_approval(monkeypatch):
    store, ident, lease = seed()
    fake = FakeClient([("inspect_measurements", {}), ("read_demo_specs", {}),
                       ("inspect_preview", {"page":1}), ("submit_report", model_report())])
    r = execute(monkeypatch, fake, store, ident, lease)
    assert r["state"] == "awaiting_approval" and r["receipt"] is None
    assert r["turns"] == 4 and r["usedMicros"] == 4*cost_micros(100,20)
    assert r["reservedMicros"] == 0 and fake.closed
    starts = [e["call"] for e in r["events"] if e.get("call", {}).get("phase") == "started"]
    spans = [e["call"] for e in r["events"] if e.get("call", {}).get("phase") == "completed"]
    assert [s["id"] for s in starts] == [s["id"] for s in spans] == [f"model-{i}" for i in range(1,5)]
    assert all(s["model"] == MODEL and s["durationMs"] >= 0 for s in spans)
    assert sum(s["costMicros"] for s in spans) == r["usedMicros"]
    assert sum(s["inputTokens"] for s in spans) == r["inputTokens"]
    assert sum(s["outputTokens"] for s in spans) == r["outputTokens"]
    for request in fake.requests:
        assert request["model"] == MODEL
        assert "thinking" not in request and "cache_control" not in request
        assert request["tool_choice"] == {"type":"any","disable_parallel_tool_use":True}
        assert request["max_tokens"] == 1500
    outputs = [i for m in fake.requests[-1]["messages"] if isinstance(m["content"],list)
               for i in m["content"] if i.get("type")=="tool_result"]
    image = outputs[-1]["content"][1]
    assert image["type"] == "image" and image["source"]["media_type"] == "image/png"
    calls = {i["id"] for m in r["messages"] if isinstance(m["content"],list)
             for i in m["content"] if i.get("type")=="tool_use"}
    assert all(o["tool_use_id"] in calls for o in outputs)


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
    assert any(i.get("type")=="tool_result" for m in second.requests[0]["messages"]
               if isinstance(m["content"],list) for i in m["content"])


def test_malformed_arguments_are_repaired_without_approval(monkeypatch):
    store, ident, lease=seed()
    fake=FakeClient([("inspect_preview","{invalid"), ("ask_clarification",{"question":"Confirm crop?"})])
    r=execute(monkeypatch,fake,store,ident,lease)
    assert r["state"]=="awaiting_input" and r["receipt"] is None
    assert fake.requests[1]["messages"][-1]["content"][0]["is_error"]


@pytest.mark.parametrize("count",[0,180001,True,-1])
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


def test_legacy_luna_run_is_not_silently_converted(monkeypatch):
    store,ident,lease=seed()
    with store.transaction() as state:state["runs"][ident]["model"]="gpt-5.6-luna"
    fake=FakeClient([]);r=execute(monkeypatch,fake,store,ident,lease)
    assert r["state"]=="failed" and r["turns"]==0 and not fake.requests


def test_bounded_tool_schemas_and_integer_cost_ceiling():
    assert cost_micros(1,0)==1 and cost_micros(1000000,1000000)==6000000
    for tool in TOOLS:
        assert tool["input_schema"]["additionalProperties"] is False
        assert set(tool["input_schema"].get("required",[]))==set(tool["input_schema"]["properties"])
    report=next(t for t in TOOLS if t["name"]=="submit_report")
    fields=report["input_schema"]["$defs"]["Finding"]["properties"]
    assert fields["category"]["enum"]==["model-suggested","requires-human-review"]
    assert fields["evidence_id"]["pattern"]==r"^preview:page-[1-5]$"

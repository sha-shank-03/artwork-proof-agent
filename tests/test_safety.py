import base64
import copy
import io
import os
from pathlib import Path
import threading
import time

import pytest
from fastapi.testclient import TestClient
from PIL import Image
from pypdf import PdfReader,PdfWriter
from app.core import approve,digest,finalize,measured_findings,reserve,settle,uid
from app.inspect_file import inspect
from app.store import Store,empty_state
from app.main import create_app
from app.proof import build_pdf
from app.worker import Worker

def image_bytes(size=(900,900),fmt="PNG",mode="RGB"):
    im=Image.new(mode,size,"white");buf=io.BytesIO();im.save(buf,fmt);return buf.getvalue()
def run():
    decoded=inspect(image_bytes())
    return {"id":uid(),"owner":"alice","state":"running","events":[],"width":3,"height":3,"version":1,
            "artworkHash":digest(image_bytes()),"measurements":{"format":decoded["format"],"pages":decoded["pages"]},
            "previews":decoded["previews"],"report":None,"reportDigest":"","receipt":None,"turns":0,
            "usedMicros":0,"reservedMicros":0,"budgetMonth":"","inspectedMeasurements":True,"inspectedSpecs":True,"inspectedPages":[1]}
def model_report():
    return {"summary":"Deterministic test fixture, not a real model result.","findings":[{"category":"requires-human-review","severity":"warning","title":"Review before print","detail":"This is a test-only finding.","evidence_id":"preview:page-1"}]}

@pytest.mark.parametrize("data",[b"",b"<svg></svg>",b"GIF89a",b"%PDF-invalid",b"\x89PNG\r\n\x1a\ninvalid",b"x"*(10*1024*1024+1)])
def test_bad_files(data):
    with pytest.raises(Exception):inspect(data)
@pytest.mark.parametrize("fmt",["PNG","JPEG"])
def test_raster_measurements(fmt):
    result=inspect(image_bytes((300,600),fmt));assert result["format"]==fmt;assert result["pages"][0]["widthPixels"]==300
    findings=measured_findings({k:v for k,v in result.items() if k!="previews"},3,3)
    assert any(f["title"]=="Aspect-ratio mismatch" for f in findings)
    assert any("100.0 DPI" in f["detail"] for f in findings)
def test_transparent_margins():
    im=Image.new("RGBA",(100,100),(0,0,0,0));im.paste((0,255,0,255),(10,20,80,70));b=io.BytesIO();im.save(b,"PNG")
    p=inspect(b.getvalue())["pages"][0];assert p["transparent"];assert p["alphaMargins"]==[10,20,20,30]
@pytest.mark.parametrize("pages,encrypted",[(6,False),(1,True)])
def test_pdf_boundaries(pages,encrypted):
    writer=PdfWriter()
    for _ in range(pages):writer.add_blank_page(width=300,height=300)
    if encrypted:writer.encrypt("test-only")
    buf=io.BytesIO();writer.write(buf)
    with pytest.raises(ValueError):inspect(buf.getvalue())
def test_pdf_dpi_is_not_invented():
    writer=PdfWriter();writer.add_blank_page(width=216,height=216);buf=io.BytesIO();writer.write(buf)
    result=inspect(buf.getvalue());findings=measured_findings(result,3,3)
    assert any(f["category"]=="requires-human-review" and f["title"]=="PDF print resolution" for f in findings)
    assert not any(f["title"]=="Effective resolution" for f in findings)
def test_approval_idempotent():
    r=run();finalize(r,model_report());a=approve(r,r["reportDigest"]);b=approve(r,r["reportDigest"]);assert a["id"]==b["id"];assert r["state"]=="completed"
@pytest.mark.parametrize("change",["hash","version","digest","expired","state","content"])
def test_stale_approval(change):
    r=run();finalize(r,model_report());expected=r["reportDigest"]
    if change=="hash":r["artworkHash"]="changed"
    if change=="version":r["version"]+=1
    if change=="digest":expected="x"*64
    if change=="expired":r["approvalExpires"]=1
    if change=="state":r["state"]="cancelled"
    if change=="content":r["report"]["summary"]="tampered"
    with pytest.raises(ValueError):approve(r,expected)
@pytest.mark.parametrize("change",["measurement","citation","extra","missing_inspections"])
def test_model_output_restrictions(change):
    r=run();report=model_report()
    if change=="measurement":report["findings"][0]["category"]="measured"
    if change=="citation":report["findings"][0]["evidence_id"]="preview:page-999"
    if change=="extra":report["send_to_printer"]=True
    if change=="missing_inspections":r["inspectedPages"]=[]
    with pytest.raises(ValueError):Worker(Store()).execute_tool(r,"submit_report",report)
def test_cost_reservation_rollback_and_settlement():
    s=empty_state();r=run();reserve(s,r,200000)
    with pytest.raises(ValueError):reserve(s,r,50001)
    settle(s,r,1000);assert r["usedMicros"]==1000;assert not r["reservedMicros"]
    s["budgets"][r["budgetMonth"]]["used"]=2499999
    with pytest.raises(ValueError):reserve(s,r,2)
def test_concurrent_budget():
    store=Store();success=[]
    def attempt():
        try:
            with store.transaction() as state:
                r=run();reserve(state,r,100000);state["runs"][r["id"]]=r
            success.append(True)
        except ValueError:pass
    ts=[threading.Thread(target=attempt) for _ in range(40)]
    for t in ts:t.start()
    for t in ts:t.join()
    assert len(success)==25
def test_postgres_concurrency():
    url=os.getenv("TEST_DATABASE_URL")
    if not url:pytest.skip("TEST_DATABASE_URL required")
    store=Store(url)
    with store.transaction() as state:state.clear();state.update(empty_state())
    results=[]
    def attempt():
        try:
            with store.transaction() as state:reserve(state,run(),100000)
            results.append(True)
        except ValueError:pass
    ts=[threading.Thread(target=attempt) for _ in range(30)]
    for t in ts:t.start()
    for t in ts:t.join()
    assert len(results)==25
def client(monkeypatch,who="alice"):
    monkeypatch.setenv("ALLOW_MEMORY_STORE","test");monkeypatch.setenv("LIVE_ENABLED","true")
    s=Store();token="test-only-invitation-value";now=int(time.time())
    with s.transaction() as st:st["invites"][digest(token.encode())]={"id":who,"expires":now+1000,"remaining":5,"revoked":False}
    c=TestClient(create_app(s));c.headers["origin"]="http://localhost:5174";assert c.post("/session",json={"token":token}).status_code==200
    return c,s
def test_api_isolation_and_csrf(monkeypatch):
    c,s=client(monkeypatch)
    with s.transaction() as state:state["runs"]["bob-run"]={**run(),"id":"bob-run","owner":"bob","expires":int(time.time())+1000}
    assert c.get("/runs/bob-run").status_code==404
    assert c.post("/runs/bob-run/cancel",json={}).status_code==404
    assert c.post("/session",json={"token":"test-only-invitation-value"},headers={"origin":"https://evil.invalid"}).status_code==403

def test_request_and_expiry_limits(monkeypatch):
    c,s=client(monkeypatch)
    assert c.post("/session",content=b"x"*16385,headers={"content-type":"application/json"}).status_code==413
    with s.transaction() as state:state["runs"]["expired"]={**run(),"expires":1}
    assert c.get("/runs/expired").status_code==404
    statuses=[c.post("/session",json={"token":"invalid-token-value-long"}).status_code for _ in range(11)]
    assert statuses[-1]==429
def test_mime_spoof_and_missing_dimensions(monkeypatch):
    c,s=client(monkeypatch)
    assert c.post("/uploads",content=image_bytes(),headers={"content-type":"application/pdf"}).status_code==415
    upload=c.post("/uploads?name=test.png",content=image_bytes(),headers={"content-type":"image/png"});assert upload.status_code==201
    result=c.post("/runs",json={"uploadId":upload.json()["id"]});assert result.status_code==201
    assert result.json()["state"]=="awaiting_input";assert result.json()["turns"]==0
def test_pdf_export():
    r=run();finalize(r,model_report());data=build_pdf(r);reader=PdfReader(io.BytesIO(data));assert 1<=len(reader.pages)<=4
    text=" ".join(p.extract_text() for p in reader.pages);assert "not" in text.lower();assert r["artworkHash"] in text
    Path(".local").mkdir(exist_ok=True);Path(".local/proof-test.pdf").write_bytes(data)

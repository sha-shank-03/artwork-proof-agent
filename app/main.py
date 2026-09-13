import base64
import copy
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import time

from fastapi import BackgroundTasks, FastAPI, HTTPException, Request, Response
from pydantic import BaseModel, ConfigDict, Field
from .core import PROMPT_VERSION, approve, digest, event, settle, uid
from .store import Store, StorageLimitError
from fastapi.responses import JSONResponse
from .worker import Worker, MODEL
from .proof import build_pdf
from .http_limits import RequestLimits
from .contracts import PublicRun, Uploaded, RunEvent, ProofReport

class SessionInput(BaseModel):
    token:str=Field(min_length=20,max_length=200)
class StartInput(BaseModel):
    uploadId:str
    width:float|None=Field(default=None,gt=.1,le=40)
    height:float|None=Field(default=None,gt=.1,le=40)
class DecisionInput(BaseModel):
    digest:str=Field(min_length=64,max_length=64)
class ClarificationInput(BaseModel):
    text:str=Field(default="",max_length=2000)
    width:float|None=Field(default=None,gt=.1,le=40)
    height:float|None=Field(default=None,gt=.1,le=40)

def public_run(run):
    hide={"owner","leaseToken","messages","reservedMicros","budgetMonth","inspectedPages","inspectedSpecs","inspectedMeasurements"}
    return {k:v for k,v in run.items() if k not in hide}

def create_app(store=None):
    store=store or Store(os.environ.get("DATABASE_URL"))
    if store.url is None and os.environ.get("ALLOW_MEMORY_STORE")!="test":
        raise RuntimeError("DATABASE_URL is required outside explicit tests")
    api=FastAPI(title="Artwork Proof Agent",version="0.1.0")
    api.add_middleware(RequestLimits)
    @api.exception_handler(StorageLimitError)
    async def storage_limit(request,exc):
        return JSONResponse({"detail":str(exc)},status_code=429)
    api.state.store=store;worker=Worker(store,int(os.getenv("MONTHLY_BUDGET_MICRO_USD","2500000")))
    origin=os.getenv("ALLOWED_ORIGIN","http://localhost:5174")
    def live():
        if os.getenv("LIVE_ENABLED")!="true":raise HTTPException(503,"Live execution is disabled")
    @api.middleware("http")
    async def safety(request,call_next):
        if request.method not in ("GET","HEAD","OPTIONS") and request.headers.get("origin")!=origin:
            return Response("Origin not allowed",status_code=403)
        response=await call_next(request)
        response.headers["X-Content-Type-Options"]="nosniff";response.headers["Cache-Control"]="no-store"
        response.headers["Referrer-Policy"]="no-referrer"
        return response
    def owner(request):
        token=request.cookies.get("portfolio_session","")
        with store.transaction() as state:
            session=state["sessions"].get(digest(token.encode()))
            if not session or session["expires"]<=time.time():raise HTTPException(401,"Invitation required")
            inv=next((v for v in state["invites"].values() if v["id"]==session["owner"]),None)
            if not inv or inv["revoked"] or inv["expires"]<=time.time():raise HTTPException(401,"Invitation expired")
            return inv["id"]
    def owned(state,ident,who):
        r=state["runs"].get(ident)
        if not r or r["owner"]!=who or r.get("expires",0)<=time.time():raise HTTPException(404,"Run not found")
        if r["state"]=="running" and r["leaseUntil"]<=time.time():
            r["state"]="failed";r["error"]="Worker interrupted. Resume explicitly from the saved checkpoint."
        return r
    def claim(state,r):
        if r["model"]!=MODEL or r["promptVersion"]!=PROMPT_VERSION:
            raise HTTPException(409,"Model changed. Start a new analysis; historical reports remain readable.")
        if sum(v["state"]=="running" and v["leaseUntil"]>time.time() for v in state["runs"].values())>=2:
            raise HTTPException(429,"Two analyses are already running")
        r["state"]="running";r["leaseToken"]=uid();r["leaseUntil"]=int(time.time())+180;r["error"]=""
    @api.get("/health")
    def health():return {"ok":True}
    @api.get("/ready")
    def ready():
        try:store.ready()
        except Exception:raise HTTPException(503,"Database unavailable")
        return {"ready":True,"liveEnabled":os.getenv("LIVE_ENABLED")=="true"}
    @api.post("/session")
    def session(data:SessionInput,response:Response):
        token=uid()
        with store.transaction() as state:
            inv=state["invites"].get(digest(data.token.encode()))
            if not inv or inv["revoked"] or inv["expires"]<=time.time():raise HTTPException(401,"Invalid invitation")
            expires=min(inv["expires"],int(time.time())+86400)
            state["sessions"][digest(token.encode())]={"owner":inv["id"],"expires":expires}
        response.set_cookie("portfolio_session",token,httponly=True,secure=origin.startswith("https:"),samesite="lax",max_age=86400)
        return {"ok":True}
    @api.post("/uploads",status_code=201,response_model=Uploaded)
    async def upload(request:Request,name:str="artwork"):
        who=owner(request);data=bytearray()
        async for chunk in request.stream():
            data.extend(chunk)
            if len(data)>10*1024*1024:raise HTTPException(413,"10 MB maximum")
        try:
            proc=await __import__("asyncio").to_thread(subprocess.run,[sys.executable,"-m","app.inspect_file"],input=bytes(data),capture_output=True,timeout=15)
        except subprocess.TimeoutExpired:
            raise HTTPException(422,"File decoding exceeded its safe time limit")
        if proc.returncode!=0:raise HTTPException(422,"File could not be decoded safely")
        decoded=json.loads(proc.stdout)
        expected={"PNG":"image/png","JPEG":"image/jpeg","PDF":"application/pdf"}[decoded["format"]]
        if request.headers.get("content-type") not in (expected,"application/octet-stream"):
            raise HTTPException(415,"Declared MIME type does not match file content")
        ident=uid();now=int(time.time())
        with store.transaction() as state:
            state["uploads"]={k:v for k,v in state["uploads"].items() if v["expires"]>now}
            if sum(v["size"] for v in state["uploads"].values() if v["owner"]==who)+len(data)>25*1024*1024:
                raise HTTPException(429,"Invitation storage allowance exceeded")
            if sum(v["size"] for v in state["uploads"].values())+len(data)>100*1024*1024:raise HTTPException(429,"Demo storage allowance reached")
            state["uploads"][ident]={"id":ident,"owner":who,"hash":digest(bytes(data)),"size":len(data),"name":Path(name).name[:100],"created":now,"expires":now+7*86400,**decoded}
        return {"id":ident,"hash":digest(bytes(data)),"name":Path(name).name[:100],"format":decoded["format"],"pages":len(decoded["pages"])}
    @api.post("/runs",status_code=201,response_model=PublicRun)
    def start(data:StartInput,request:Request,background:BackgroundTasks):
        live();who=owner(request);now=int(time.time())
        with store.transaction() as state:
            upload=state["uploads"].get(data.uploadId)
            if not upload or upload["owner"]!=who or upload["expires"]<=now:raise HTTPException(404,"Upload not found")
            inv=next(v for v in state["invites"].values() if v["id"]==who)
            if inv["remaining"]<=0:raise HTTPException(429,"Invitation run allowance exhausted")
            inv["remaining"]-=1
            r={"id":uid(),"owner":who,"uploadId":data.uploadId,"artworkHash":upload["hash"],"name":upload["name"],"width":data.width,"height":data.height,"version":1,"state":"queued","summary":"","events":[],"measurements":{"format":upload["format"],"pages":upload["pages"]},"previews":upload["previews"],"messages":[],"created":now,"expires":now+7*86400,"leaseUntil":0,"leaseToken":"","report":None,"reportDigest":"","receipt":None,"turns":0,"inputTokens":0,"outputTokens":0,"usedMicros":0,"reservedMicros":0,"budgetMonth":"","error":"","model":os.getenv("ANTHROPIC_MODEL",MODEL),"promptVersion":PROMPT_VERSION,"inspectedMeasurements":False,"inspectedSpecs":False,"inspectedPages":[]}
            state["runs"][r["id"]]=r;event(r,"upload","Artwork received",f"{upload['format']} / {len(upload['pages'])} page(s)")
            if not data.width or not data.height:
                r["state"]="awaiting_input";r["summary"]="What width and height, in inches, should this artwork be printed at?"
            else:claim(state,r);background.add_task(worker.run,r["id"],r["leaseToken"])
            return public_run(r)
    @api.get("/runs",response_model=list[PublicRun])
    def runs(request:Request):
        who=owner(request)
        with store.transaction() as state:
            now=time.time();state["runs"]={k:v for k,v in state["runs"].items() if v["expires"]>now}
            return [public_run(v) for v in state["runs"].values() if v["owner"]==who]
    @api.get("/runs/{ident}",response_model=PublicRun)
    def get(ident:str,request:Request):
        who=owner(request)
        with store.transaction() as state:return public_run(owned(state,ident,who))
    @api.get("/runs/{ident}/events",response_model=list[RunEvent])
    def events(ident:str,request:Request,after:int=0):
        who=owner(request)
        with store.transaction() as state:return [e for e in owned(state,ident,who)["events"] if e["seq"]>after]
    @api.post("/runs/{ident}/approve",response_model=PublicRun)
    def accept(ident:str,data:DecisionInput,request:Request):
        who=owner(request)
        with store.transaction() as state:
            r=owned(state,ident,who)
            try:approve(r,data.digest)
            except ValueError as e:raise HTTPException(409,str(e))
            return public_run(r)
    @api.post("/runs/{ident}/reject",response_model=PublicRun)
    def reject(ident:str,data:DecisionInput,request:Request):
        who=owner(request)
        with store.transaction() as state:
            r=owned(state,ident,who)
            if r["state"]!="awaiting_approval" or r["reportDigest"]!=data.digest:raise HTTPException(409,"Report changed")
            r["state"]="completed";r["summary"]="Proof rejected by reviewer. Nothing sent to a printer.";event(r,"approval","Proof rejected");return public_run(r)
    @api.post("/runs/{ident}/clarify",response_model=PublicRun)
    def clarify(ident:str,data:ClarificationInput,request:Request,background:BackgroundTasks):
        live();who=owner(request)
        with store.transaction() as state:
            r=owned(state,ident,who)
            if r["state"]!="awaiting_input":raise HTTPException(409,"Run is not awaiting input")
            if data.width:r["width"]=data.width
            if data.height:r["height"]=data.height
            if not r["width"] or not r["height"]:raise HTTPException(422,"Width and height are required")
            if r["messages"]:r["messages"].append({"role":"user","content":"Reviewer clarification (untrusted data): "+data.text})
            event(r,"input","Reviewer clarification",data.text);claim(state,r);background.add_task(worker.run,r["id"],r["leaseToken"]);return public_run(r)
    @api.post("/runs/{ident}/cancel",response_model=PublicRun)
    def cancel(ident:str,request:Request):
        who=owner(request)
        with store.transaction() as state:
            r=owned(state,ident,who)
            if r["state"] not in ("completed","cancelled"):
                if r["reservedMicros"]:settle(state,r,r["reservedMicros"])
                r["state"]="cancelled";r["leaseToken"]="";r["leaseUntil"]=0;event(r,"status","Run cancelled")
            return public_run(r)
    @api.post("/runs/{ident}/resume",response_model=PublicRun)
    def resume(ident:str,request:Request,background:BackgroundTasks):
        live();who=owner(request)
        with store.transaction() as state:
            r=owned(state,ident,who)
            if r["state"]!="failed" and not(r["state"]=="running" and r["leaseUntil"]<=time.time()):raise HTTPException(409,"Run is not recoverable")
            if r["reservedMicros"]:settle(state,r,r["reservedMicros"])
            claim(state,r);background.add_task(worker.run,r["id"],r["leaseToken"]);return public_run(r)
    @api.get("/runs/{ident}/report.json",response_model=ProofReport)
    def report(ident:str,request:Request):
        who=owner(request)
        with store.transaction() as state:
            r=owned(state,ident,who)
            if not r["report"]:raise HTTPException(409,"Report not ready")
            return r["report"]
    @api.get("/runs/{ident}/proof.pdf")
    def pdf(ident:str,request:Request):
        who=owner(request)
        with store.transaction() as state:r=copy.deepcopy(owned(state,ident,who))
        if not r["report"]:raise HTTPException(409,"Report not ready")
        return Response(build_pdf(r),media_type="application/pdf",headers={"Content-Disposition":"attachment; filename=artwork-proof.pdf"})
    return api

def app():return create_app()

"""Real-provider evaluation only. No simulated model output fallback."""
import argparse
import atexit
import http.cookiejar
import io
import json
from pathlib import Path
import subprocess
import sys
import time
import urllib.request
import urllib.error

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from pypdf import PdfReader
from tools.fixtures import fixture
from app.core import digest
from app.worker import MODEL

def resume_results(report, cases, commit):
    if report.get("provider")!="OpenAI" or report.get("model")!=MODEL or report.get("commit")!=commit:
        raise ValueError("Resume requires the same provider, model and source commit")
    rows=report.get("results",[])
    if [r.get("id") for r in rows]!=[c["id"] for c in cases[:len(rows)]] or not all(r.get("passed") for r in rows):
        raise ValueError("Resume requires an ordered, passing prefix; failed cases need a new evaluation")
    return rows,report.get("recordings",[])

def main():
    parser=argparse.ArgumentParser();parser.add_argument("--limit",type=int,default=30)
    parser.add_argument("--resume",action="store_true",help="Continue a saved passing prefix without repeating model calls")
    parser.add_argument("--rerun-failed",action="store_true",help="Retain the full prior attempt and rerun only failed cases on the same source commit")
    parser.add_argument("--hosted-site");parser.add_argument("--railway-project");parser.add_argument("--railway-environment");parser.add_argument("--railway-service");args=parser.parse_args()
    selectors=[];issued=[]
    if args.hosted_site:
        if not args.hosted_site.startswith("https://") or not all([args.railway_project,args.railway_environment,args.railway_service]):parser.error("Hosted runs require HTTPS and exact Railway project/environment/service IDs")
        selectors=["--project",args.railway_project,"--environment",args.railway_environment,"--service",args.railway_service]
    origin=args.hosted_site.rstrip("/") if args.hosted_site else "http://localhost:5174"
    api=origin+"/api" if args.hosted_site else "http://127.0.0.1:8081"
    invite_path=Path(".local/eval-invite.txt" if args.hosted_site else ".local/invite.txt")
    cases=json.loads(Path("evals/cases.json").read_text())[:args.limit]
    commit=subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip()
    output=Path("evals/results");output.mkdir(parents=True,exist_ok=True)
    results=[];recordings=[];retry_notice=None
    if args.resume and args.rerun_failed:parser.error("Choose resume or rerun-failed, not both")
    if args.rerun_failed:
        saved=json.loads((output/"latest.json").read_text())
        if saved.get("provider")!="OpenAI" or saved.get("model")!=MODEL or saved.get("commit")!=commit or [r.get("id") for r in saved["results"]]!=[c["id"] for c in cases]:
            raise ValueError("Rerun requires the complete same-source/provider/model evaluation set")
        results=saved["results"];recordings=saved["recordings"]
        retry_notice={"priorPassed":saved["passed"],"priorCases":saved["cases"],"rerunCaseIds":[r["id"] for r in results if not r["passed"]],"method":"Only failed cases rerun; original attempt retained in evaluation history."}
        (output/"latest.json").rename(output/f"attempt-{time.time_ns()}.json")
    elif args.resume:
        results,recordings=resume_results(json.loads((output/"latest.json").read_text()),cases,commit)
    elif (output/"latest.json").exists():(output/"latest.json").rename(output/f"attempt-{time.time_ns()}.json")
    def cleanup():
        for invitation in issued[:]:
            result=subprocess.run([sys.executable,"tools/hosted_invite.py","revoke","--id",invitation,*selectors],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
            if result.returncode==0:issued.remove(invitation)
            else:print("Invitation cleanup requires retry for ID "+invitation,file=sys.stderr)
    atexit.register(cleanup)
    start_index=len(results)
    work=[(i,c) for i,c in enumerate(cases) if not results[i]["passed"]] if args.rerun_failed else list(enumerate(cases[start_index:],start_index))
    for work_index,(i,case) in enumerate(work):
        new_invitation=work_index%5==0
        if new_invitation:
            command=[sys.executable,"tools/hosted_invite.py","invite","--output-prefix","eval-invite",*selectors] if args.hosted_site else [sys.executable,"-m","app.cli","invite"]
            subprocess.run(command,check=True,stdout=subprocess.DEVNULL)
            if args.hosted_site:issued.append(json.loads(Path(".local/eval-invite.json").read_text())["id"])
            opener=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
        def request(path,data=None,mime="application/json",binary=False):
            body=(data if isinstance(data,bytes) else json.dumps(data).encode()) if data is not None else None
            req=urllib.request.Request(api+path,data=body,headers={"Origin":origin,"Content-Type":mime})
            for attempt in range(3 if data is None else 1):
                try:
                    with opener.open(req,timeout=190) as response:
                        return response.read() if binary else json.load(response)
                except (urllib.error.URLError,TimeoutError) as exc:
                    if data is not None or attempt==2 or isinstance(exc,urllib.error.HTTPError) and exc.code<500:raise
                    time.sleep(1)
        if new_invitation:request("/session",{"token":invite_path.read_text().strip()})
        start=time.monotonic();r={};checks={}
        try:
            raw,mime,extension=fixture(case["fixture"])
            upload=request("/uploads?name="+case["fixture"]+"."+extension,raw,mime)
            r=request("/runs",{"uploadId":upload["id"],"width":case["width"],"height":case["height"]})
            checks["hash_bound"]=r["artworkHash"]==digest(raw)
            if case["width"] is None:
                checks["missing_size_paused_without_model"]=r["state"]=="awaiting_input" and r["turns"]==0
                r=request(f"/runs/{r['id']}/clarify",{"width":3,"height":3,"text":"Use the original design at 3 x 3 inches. Do not alter the file."})
            end=time.monotonic()+180
            while r["state"]=="running" and time.monotonic()<end:
                time.sleep(1);r=request(f"/runs/{r['id']}")
            checks["approval_pause"]=r["state"]=="awaiting_approval"
            checks["no_unapproved_receipt"]=r["receipt"] is None
            checks["real_provider_usage"]=r["inputTokens"]>0 and r["outputTokens"]>0
            checks["requested_model"]=r["model"]==MODEL
            checks["bounded_cost"]=r["turns"]<=8 and r["usedMicros"]<=250000
            spans=[e["call"] for e in r["events"] if e.get("call",{} ) and e["call"]["phase"]=="completed"]
            checks["model_telemetry"]=len(spans)==r["turns"] and all(s["model"]==MODEL and s["durationMs"]>=0 for s in spans) and sum(s["costMicros"] for s in spans)==r["usedMicros"] and sum(s["inputTokens"] for s in spans)==r["inputTokens"] and sum(s["outputTokens"] for s in spans)==r["outputTokens"]
            if r["report"]:
                report=r["report"];checks["report_digest"]=digest(report)==r["reportDigest"]
                checks["evidence_valid"]=all(f["evidence_id"] in {f"{prefix}:page-{page+1}" for prefix in ("measurement","preview") for page in range(len(r["previews"]))} for f in report["findings"])
                checks["all_pages_inspected"]=sum(e["title"]=="inspect_preview" for e in r["events"])>=len(r["previews"])
                checks["measured_and_model_separated"]=all(f["evidence_id"].startswith("measurement:") for f in report["findings"] if f["category"]=="measured")
                proof=request(f"/runs/{r['id']}/proof.pdf",binary=True)
                checks["proof_pdf"]=len(PdfReader(io.BytesIO(proof)).pages)>0
                r=request(f"/runs/{r['id']}/{case['decision']}",{"digest":r["reportDigest"]})
                checks["decision_resolved"]=r["state"]=="completed" and bool(r["receipt"])==(case["decision"]=="approve")
                if r["receipt"]:
                    duplicate=request(f"/runs/{r['id']}/approve",{"digest":r["reportDigest"]})
                    checks["idempotent_receipt"]=r["receipt"]["id"]==duplicate["receipt"]["id"]
            passed=all(checks.values())
            row={"id":case["id"],"passed":passed,"checks":checks,"runId":r["id"],"state":r["state"],"costMicros":r["usedMicros"],"inputTokens":r["inputTokens"],"outputTokens":r["outputTokens"],"seconds":round(time.monotonic()-start,2)}
            if passed and case["fixture"] not in [v["fixture"] for v in recordings]:
                recordings.append({"fixture":case["fixture"],"label":case["fixture"].replace("-"," "),"run":r,"commit":commit,"recordedAt":r["events"][0]["at"],"providerVerified":True})
        except Exception as exc:
            row={"id":case["id"],"passed":False,"errorType":type(exc).__name__,"seconds":round(time.monotonic()-start,2)}
        if args.rerun_failed:results[i]=row
        else:results.append(row)
        report={"provider":"OpenAI","model":MODEL,"commit":commit,"cases":len(results),"passed":sum(v["passed"] for v in results),"results":results,"recordings":recordings,"notice":"30 executions: six original designs across five size/approval conditions. Deterministic graders do not certify visual accuracy."}
        if retry_notice:report["retryNotice"]=retry_notice
        (output/"latest.json").write_text(json.dumps(report,indent=2))
        print(case["id"],"PASS" if row["passed"] else "FAIL",flush=True)
        if r.get("state")=="failed" and r.get("turns")==0:
            print("Provider access failed before a billed call. Stop; do not repeat all cases.",flush=True);break
    cleanup()
    return 0 if len(results)==len(cases) and all(v["passed"] for v in results) else 1

if __name__=="__main__":raise SystemExit(main())

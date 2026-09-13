"""Hosted file/auth/recovery checks. Never starts a model call: dimensions stay null."""
import argparse, http.cookiejar, json, subprocess, sys, urllib.error, urllib.request
from pathlib import Path

p=argparse.ArgumentParser();p.add_argument("phase",choices=["prepare","complete"]);p.add_argument("--base-url",required=True);args=p.parse_args()
base=args.base_url.rstrip("/");assert base.startswith("https://")
root=Path(__file__).resolve().parents[1];path=root/".local/hosted-smoke.json"
report=json.loads(path.read_text()) if path.exists() else {"baseUrl":base,"checks":{}}
assert report["baseUrl"]==base
jar=http.cookiejar.CookieJar();client=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
def call(route,data=None,mime="application/json",expected=200):
    raw=json.dumps(data).encode() if data is not None and mime=="application/json" else data
    req=urllib.request.Request(base+"/api"+route,data=raw,headers={"Origin":base,"Content-Type":mime})
    try:
        with client.open(req,timeout=30) as response:
            assert response.status==expected
            return json.load(response)
    except urllib.error.HTTPError as exc:
        assert exc.code==expected,(route,exc.code,expected)
        return None
def check(name,condition):
    report["checks"][name]=bool(condition);path.write_text(json.dumps(report,indent=2));print(name,"PASS" if condition else "FAIL",flush=True);assert condition

call("/session",{"token":(root/".local/hosted-invite.txt").read_text().strip()})
check("secure_httponly_session",len(jar)>0 and all(c.secure and c.has_nonstandard_attr("HttpOnly") for c in jar))
if args.phase=="prepare":
    png=(root/"web/public/fixtures/clean-mark.png").read_bytes()
    uploaded=call("/uploads?name=clean-mark.png",png,"image/png",201)
    pdf=call("/uploads?name=two-page-proof.pdf",(root/"web/public/fixtures/two-page-proof.pdf").read_bytes(),"application/pdf",201)
    check("isolated_png_pdf_preflight",uploaded["format"]=="PNG" and pdf["pages"]==2)
    call("/uploads?name=spoof.jpg",png,"image/jpeg",415);check("spoofed_mime_rejected",True)
    call("/uploads?name=unsupported.svg",b"<svg></svg>","image/svg+xml",422);check("svg_rejected",True)
    call("/uploads?name=broken.pdf",b"%PDF-1.7\nnot-a-valid-pdf", "application/pdf",422);check("malformed_pdf_rejected",True)
    run=call("/runs",{"uploadId":uploaded["id"],"width":None,"height":None},expected=201)
    report["runId"]=run["id"];report["uploadId"]=uploaded["id"]
    check("missing_dimensions_pause_without_provider",run["state"]=="awaiting_input" and run["turns"]==0 and run["usedMicros"]==0)
    call("/runs/"+run["id"]+"/approve",{"digest":"0"*64},expected=409);check("unapproved_proof_denied",True)
    print("Ready for restart with LIVE_ENABLED=false; no model calls made.")
else:
    run=call("/runs/"+report["runId"])
    check("restart_preserved_clarification",run["state"]=="awaiting_input" and run["turns"]==0)
    run=call("/runs/"+report["runId"]+"/cancel",{})
    check("cancel_without_provider",run["state"]=="cancelled" and run["usedMicros"]==0)
    call("/runs",{"uploadId":report["uploadId"],"width":None,"height":None},expected=503);check("live_kill_switch",True)
    metadata=json.loads((root/".local/hosted-invite.json").read_text());selectors=["--project",metadata["project"],"--environment",metadata["environment"],"--service",metadata["service"]]
    subprocess.run([sys.executable,"tools/hosted_invite.py","invite",*selectors],cwd=root,stdout=subprocess.DEVNULL,check=True)
    call("/session",{"token":(root/".local/hosted-invite.txt").read_text().strip()})
    call("/runs/"+report["runId"],expected=404);check("reviewer_isolation",True)
    for ident in (metadata["id"],json.loads((root/".local/hosted-invite.json").read_text())["id"]):
        subprocess.run([sys.executable,"tools/hosted_invite.py","revoke","--id",ident,*selectors],cwd=root,stdout=subprocess.DEVNULL,check=True)
    call("/runs",expected=401);check("revoked_session_denied",True)
    print("Hosted file/auth/recovery smoke complete; no Claude evaluation is claimed.")

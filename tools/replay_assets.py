"""Publish only passing genuine Claude recordings; refuse incomplete evaluation sets."""
import json, re, statistics, sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from app.contracts import PublicRun
from app.core import digest
from app.proof import build_pdf
from app.worker import MODEL

def validate_gate(report):
    rows=report.get("results",[])
    if report.get("provider")!="Anthropic" or report.get("model")!=MODEL or report.get("cases")!=30 or len(rows)!=30 or sum(bool(r.get("passed")) for r in rows)<27:
        raise ValueError("The 30-case live evaluation gate has not passed")
    required=("hash_bound","no_unapproved_receipt","bounded_cost","report_digest","evidence_valid","measured_and_model_separated","requested_model")
    if any(not all(r.get("checks",{}).get(k,False) for k in required) for r in rows):
        raise ValueError("A safety invariant failed")
    for row in rows:
        if not row.get("inputTokens") or not row.get("outputTokens"):
            raise ValueError("Every case must exercise the real provider")

def build(report):
    validate_gate(report)
    prepared=[]
    for item in report["recordings"]:
        name=item["fixture"]
        if not re.fullmatch(r"[a-z0-9-]+",name) or not re.fullmatch(r"[a-f0-9]{40}",item["commit"]):raise ValueError("Invalid recording metadata")
        def private(value):
            if isinstance(value,dict):
                if {"owner","messages","checkpoint","leaseToken","authorization","apiKey"}.intersection(value):raise ValueError("Private field in recording")
                for child in value.values():private(child)
            elif isinstance(value,list):
                for child in value:private(child)
        private(item)
        run=PublicRun.model_validate(item["run"]).model_dump()
        if item.get("providerVerified") is not True or run["model"]!=MODEL or not run["inputTokens"] or not run["outputTokens"] or not run["report"] or digest(run["report"])!=run["reportDigest"]:
            raise ValueError("Recording is not a verified provider report")
        if not any(r.get("runId")==run["id"] and r.get("passed") for r in report["results"]):raise ValueError("Recording lacks a passing evaluation case")
        prepared.append((name,{"version":1,"label":item["label"],"recordedAt":item["recordedAt"],"commit":item["commit"],"providerVerified":True,"proofFile":f"/replays/{name}.pdf","run":run},build_pdf(run)))
    if len({n for n,_,_ in prepared})!=6:raise ValueError("Six genuine fixture recordings are required")
    directory=Path("web/public/replays");directory.mkdir(exist_ok=True,parents=True)
    for name,recording,pdf in prepared:
        (directory/f"{name}.json").write_text(json.dumps(recording,indent=2));(directory/f"{name}.pdf").write_bytes(pdf)
    (directory/"index.json").write_text(json.dumps({"version":1,"runs":[{"label":r["label"],"file":f"/replays/{n}.json"} for n,r,_ in prepared],"notice":"Genuine recorded Claude Haiku 4.5 executions, not live. Static browsing makes no backend/model calls."},indent=2))
    public={k:v for k,v in report.items() if k!="recordings"}
    Path("docs/evaluation-results.json").write_text(json.dumps(public,indent=2))
    history=[{k:v for k,v in json.loads(p.read_text()).items() if k!="recordings"} for p in sorted(Path("evals/results").glob("attempt-*.json"))]
    Path("docs/evaluation-history.json").write_text(json.dumps(history,indent=2))
    Path("web/public/verification.json").write_text(json.dumps(public,indent=2))
    Path("web/public/evaluation-history.json").write_text(json.dumps(history,indent=2))
    rows=report["results"];cost=sum(r["costMicros"] for r in rows)/1e6;latency=[r["seconds"] for r in rows]
    Path("docs/EVALUATIONS.md").write_text(f"""# Genuine live evaluation results

Actual result: **{sum(bool(r['passed']) for r in rows)}/30** on commit `{report['commit']}`. Six original designs under five size/decision conditions, not thirty unrelated visual tasks.

Model: `{report['model']}` via {report['provider']}. Prompt: `artwork-v3-claude`.

Application-estimated model usage: **${cost:.6f}**. Median end-to-end latency **{statistics.median(latency):.2f}s**; maximum **{max(latency):.2f}s**. Polling, tool processing and automated reviewer decisions are included. These estimates are not a provider invoice.

Grading checks real provider usage, hash/report binding, evidence validity, page inspection, measured/model separation, approval, proof PDF generation, quotas and idempotency. Visual accuracy still needs human review. Demo specifications are not commercial print certification. Earlier access failures and per-case outcomes are preserved in evaluation-history.json and evaluation-results.json. Generated proof PDFs must still be visually reviewed before release.
""")
    print(f"Prepared {len(prepared)} genuine static proof recordings; estimated set cost ${cost:.6f}")

if __name__=="__main__":
    try:build(json.loads(Path("evals/results/latest.json").read_text()))
    except (ValueError,KeyError) as exc:raise SystemExit("Replay publication refused: "+str(exc))

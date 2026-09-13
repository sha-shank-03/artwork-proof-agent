import hashlib
import json
import secrets
import time
from datetime import datetime, timezone
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field

PROMPT_VERSION = "artwork-v1"
SPEC_VERSION = "demo-print-v1"

class Finding(BaseModel):
    model_config = ConfigDict(extra="forbid")
    category: Literal["measured", "model-suggested", "requires-human-review"]
    severity: Literal["info", "warning", "error"]
    title: str = Field(min_length=1, max_length=100)
    detail: str = Field(min_length=1, max_length=800)
    evidence_id: str = Field(min_length=1, max_length=100)

class Report(BaseModel):
    model_config = ConfigDict(extra="forbid")
    summary: str = Field(min_length=1, max_length=1500)
    findings: list[Finding] = Field(max_length=20)

def uid(): return secrets.token_hex(24)
def digest(value):
    raw = value if isinstance(value, bytes) else json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()
def event(run, kind, title, detail=""):
    run["events"].append({"seq": len(run["events"])+1, "kind": kind, "title": title,
                          "detail": detail, "at": datetime.now(timezone.utc).isoformat()})
def month(): return datetime.now(timezone.utc).strftime("%Y-%m")

def reserve(state, run, amount, limit=2500000):
    if amount <= 0 or run["usedMicros"] + run["reservedMicros"] + amount > 250000:
        raise ValueError("Run spending limit reached")
    key = month(); budget = state["budgets"].setdefault(key, {"used": 0, "reserved": 0})
    if budget["used"] + budget["reserved"] + amount > limit:
        raise ValueError("Monthly model allowance exhausted")
    if run["turns"] >= 8:
        raise ValueError("Model turn limit reached")
    budget["reserved"] += amount; run["reservedMicros"] += amount
    run["budgetMonth"] = key; run["turns"] += 1

def settle(state, run, amount):
    budget = state["budgets"][run["budgetMonth"]]
    budget["reserved"] -= run["reservedMicros"]; budget["used"] += amount
    run["usedMicros"] += amount; run["reservedMicros"] = 0

def measured_findings(measurements, width, height):
    findings = []
    def add(severity, title, detail, evidence):
        findings.append(Finding(category="measured", severity=severity, title=title, detail=detail, evidence_id=evidence).model_dump())
    for i, page in enumerate(measurements["pages"]):
        ref = f"measurement:page-{i+1}"
        if measurements["format"] == "PDF":
            add("info", f"Page {i+1} dimensions", f"{page['widthPoints']} x {page['heightPoints']} PDF points. Preview pixel count is not source print resolution.", ref)
            findings.append(Finding(category="requires-human-review", severity="warning", title="PDF print resolution",
                detail="Vector and embedded raster content require specialist prepress review; a rendered preview cannot certify effective source DPI.", evidence_id=ref).model_dump())
            aspect = page["widthPoints"] / page["heightPoints"]
        else:
            dpi = min(page["widthPixels"]/width, page["heightPixels"]/height)
            add("warning" if dpi < 300 else "info", "Effective resolution", f"{dpi:.1f} DPI at {width:g} x {height:g} inches; demonstration target is 300 DPI.", ref)
            aspect = page["widthPixels"] / page["heightPixels"]
            add("info", "Transparency", "Transparent pixels detected." if page["transparent"] else "No transparent pixels detected; background colour is not inferred.", ref)
            if page.get("alphaMargins"):
                add("info", "Transparent margins", f"Left/top/right/bottom pixel margins: {page['alphaMargins']}. These are not certified bleed measurements.", ref)
        if abs(aspect/(width/height)-1) > .02:
            add("warning", "Aspect-ratio mismatch", "Artwork and requested print size differ by over 2%; fitting may add margins or crop content.", ref)
    return findings

def finalize(run, model_report):
    report = Report.model_validate(model_report)
    allowed = {f"preview:page-{i+1}" for i in range(len(run["measurements"]["pages"]))}
    model_findings = []
    for finding in report.findings:
        if finding.category == "measured" or finding.evidence_id not in allowed:
            raise ValueError("Model findings cannot claim measurements or cite unavailable evidence")
        model_findings.append(finding.model_dump())
    complete = {"summary": report.summary, "findings": measured_findings(run["measurements"], run["width"], run["height"])+model_findings,
                "specVersion": SPEC_VERSION, "artworkHash": run["artworkHash"], "version": run["version"]}
    run["report"] = complete; run["reportDigest"] = digest(complete); run["state"] = "awaiting_approval"
    run["approvalExpires"] = int(time.time())+86400
    event(run, "report", "Proof package ready", report.summary)

def approve(run, report_digest, now=None):
    now = int(time.time()) if now is None else now
    if run.get("receipt") and run["receipt"]["reportDigest"] == report_digest:
        return run["receipt"]
    if run["state"] != "awaiting_approval" or run.get("reportDigest") != report_digest:
        raise ValueError("Approval must match the pending report")
    if run["approvalExpires"] <= now or digest(run["report"]) != report_digest:
        raise ValueError("Report approval is expired or stale")
    if run["report"]["artworkHash"] != run["artworkHash"] or run["report"]["version"] != run["version"]:
        raise ValueError("Artwork version changed")
    run["receipt"] = {"id": uid(), "reportDigest": report_digest, "artworkHash": run["artworkHash"],
                      "version": run["version"], "at": now, "simulated": True}
    run["state"] = "completed"; event(run, "approval", "Proof approved", "Human review recorded. Nothing was sent to a printer.")
    return run["receipt"]

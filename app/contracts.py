"""Public response contracts; internal messages and lease credentials stay private."""
from pydantic import BaseModel, Field
from .core import Finding

class RunEvent(BaseModel):
    seq:int
    kind:str
    title:str
    detail:str
    at:str

class ProofReport(BaseModel):
    summary:str
    findings:list[Finding]
    specVersion:str
    artworkHash:str
    version:int

class Receipt(BaseModel):
    id:str
    reportDigest:str
    artworkHash:str
    version:int
    at:int
    simulated:bool

class PublicRun(BaseModel):
    id:str
    name:str
    state:str
    summary:str
    artworkHash:str
    version:int
    width:float|None
    height:float|None
    previews:list[str]
    events:list[RunEvent]
    report:ProofReport|None
    reportDigest:str
    receipt:Receipt|None
    turns:int
    inputTokens:int
    outputTokens:int
    usedMicros:int
    error:str
    model:str
    promptVersion:str
    created:int
    expires:int
    approvalExpires:int|None=None

class Uploaded(BaseModel):
    id:str
    hash:str
    name:str
    format:str
    pages:int

"""Public response contracts; internal messages and lease credentials stay private."""
from pydantic import BaseModel, Field
from .core import Finding
from typing import Literal
from pydantic import ConfigDict

class ModelCall(BaseModel):
    model_config=ConfigDict(extra="forbid")
    id:str=Field(pattern=r"^model-[1-8]$")
    phase:Literal["started","completed"]
    model:str
    durationMs:int|None=Field(default=None,ge=0)
    inputTokens:int|None=Field(default=None,ge=0)
    outputTokens:int|None=Field(default=None,ge=0)
    costMicros:int|None=Field(default=None,ge=0)

class RunEvent(BaseModel):
    seq:int
    kind:str
    title:str
    detail:str
    at:str
    call:ModelCall|None=None

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

import pytest
from tools.replay_assets import validate_gate

def passing_shape():
    return {"provider":"Anthropic","cases":30,"results":[{"passed":True,"inputTokens":1,"outputTokens":1,"checks":{k:True for k in ("hash_bound","no_unapproved_receipt","bounded_cost","report_digest","evidence_valid","measured_and_model_separated")}} for _ in range(30)]}

def test_incomplete_provider_set_cannot_publish():
    with pytest.raises(ValueError):validate_gate({"cases":1,"results":[]})

def test_safety_failure_cannot_be_hidden_by_success_percentage():
    report=passing_shape();report["results"][0]["checks"]["no_unapproved_receipt"]=False
    with pytest.raises(ValueError):validate_gate(report)

def test_unbilled_fake_case_cannot_publish():
    report=passing_shape();report["results"][0]["inputTokens"]=0
    with pytest.raises(ValueError):validate_gate(report)

def test_threshold_validation_does_not_create_assets():
    report=passing_shape();report["results"][0]["passed"]=False
    validate_gate(report)

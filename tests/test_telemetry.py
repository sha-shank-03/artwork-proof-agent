import pytest
from pydantic import ValidationError
from app.contracts import ModelCall, RunEvent
from app.core import event

def test_model_metadata_is_explicit_and_allowlisted():
    run={"events":[]}
    e=event(run,"model","Model call started")
    e["call"]={"id":"model-1","phase":"started","model":"gpt-5.6-luna"}
    parsed=RunEvent.model_validate(e)
    assert parsed.call.durationMs is None
    assert parsed.call.inputTokens is None
    with pytest.raises(ValidationError):
        ModelCall.model_validate({**e["call"],"messages":["private"]})

@pytest.mark.parametrize("field",["durationMs","inputTokens","outputTokens","costMicros"])
def test_negative_metadata_rejected(field):
    with pytest.raises(ValidationError):
        ModelCall.model_validate({"id":"model-1","phase":"completed","model":"gpt-5.6-luna",field:-1})

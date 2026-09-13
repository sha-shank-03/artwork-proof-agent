import copy
import pytest
from evals.run import resume_results

def sample():
    return {"provider":"Anthropic","model":"claude-haiku-4-5-20251001","commit":"same-commit",
            "results":[{"id":"a","passed":True}],"recordings":[]}

def test_resume_keeps_existing_rows_without_replaying():
    report=sample()
    assert resume_results(report,[{"id":"a"},{"id":"b"}],"same-commit")[0]==report["results"]

@pytest.mark.parametrize("change",["commit","model","order","failure"])
def test_resume_refuses_mixed_or_failed_results(change):
    report=copy.deepcopy(sample())
    if change=="commit":report["commit"]="different"
    if change=="model":report["model"]="gpt-5.6-luna"
    if change=="order":report["results"][0]["id"]="b"
    if change=="failure":report["results"][0]["passed"]=False
    with pytest.raises(ValueError):resume_results(report,[{"id":"a"},{"id":"b"}],"same-commit")

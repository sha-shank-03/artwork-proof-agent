"""Inject a credential from an explicitly selected local file without copying it."""
import os
import re
import subprocess
import sys
from pathlib import Path
from dotenv import dotenv_values

if len(sys.argv)<4:
    raise SystemExit("Usage: with_provider.py PATH KEY_VARIABLE COMMAND [ARGS...]")
source,variable,*command=sys.argv[1:]
if variable!="OPENAI_API_KEY":raise SystemExit("Only OpenAI access is used by this application")
value=dotenv_values(source).get(variable)
if not value:
    matches=re.findall(r"sk-(?!ant-)[A-Za-z0-9_-]{20,}",Path(source).read_text())
    if len(matches)==1:value=matches[0]
if not value:raise SystemExit("No unambiguous credential found")
environment=os.environ.copy();environment[variable]=value
try:raise SystemExit(subprocess.call(command,env=environment))
except KeyboardInterrupt:raise SystemExit(130)

"""Issue/revoke hosted invitations over Railway SSH; never print bearer tokens."""
import argparse
import json
from pathlib import Path
import re
import shlex
import subprocess
import time

parser = argparse.ArgumentParser()
parser.add_argument("command", choices=["invite", "revoke"])
parser.add_argument("--project", required=True)
parser.add_argument("--environment", required=True)
parser.add_argument("--service", required=True)
parser.add_argument("--id")
args = parser.parse_args()
root = Path(__file__).resolve().parents[1]
is_commerce = (root / "go.mod").exists()
base = ["/app/bin/server"] if is_commerce else ["python", "-m", "app.cli"]

def remote(command, attempts=1):
    # Only callers performing a read may request retries. Never blindly repeat issuance.
    for attempt in range(attempts):
        result = subprocess.run(
            ["railway", "ssh", "--project", args.project, "--environment", args.environment,
             "--service", args.service, "--", shlex.join(command)],
            capture_output=True, text=True, timeout=45)
        if result.returncode==0:return result.stdout.strip()
        if attempt+1<attempts:time.sleep(1)
    raise SystemExit("Hosted invitation operation failed; remote output suppressed.")

if args.command == "invite":
    info = remote(base + (["-invite"] if is_commerce else ["invite"]))
    match = re.search(r"Invitation ([a-f0-9]+) saved", info)
    if not match:
        raise SystemExit("Unexpected invitation response; output suppressed.")
    # A transient SSH read failure must not cause another invitation to be issued.
    try:token = remote(["cat", "/app/.local/invite.txt"],attempts=3)
    except (SystemExit,subprocess.TimeoutExpired):
        print("Created invitation needs cleanup: "+match[1])
        raise
    if not re.fullmatch(r"[a-f0-9]{32,100}", token):
        raise SystemExit("Unexpected token format; output suppressed.")
    target = root / ".local"
    target.mkdir(mode=0o700, exist_ok=True)
    for name, data in [
        ("hosted-invite.txt", token),
        ("hosted-invite.json", json.dumps({"id":match[1],"project":args.project,"environment":args.environment,"service":args.service})),
    ]:
        path = target / name
        if path.is_symlink():
            raise SystemExit("Refusing symlink destination.")
        path.touch(mode=0o600, exist_ok=True)
        path.chmod(0o600)
        path.write_text(data)
    print("Hosted invitation saved to ignored .local/hosted-invite.txt; ID " + match[1])
else:
    if not args.id or not re.fullmatch(r"[a-f0-9]{32,100}", args.id):
        raise SystemExit("An exact invitation --id is required.")
    remote(base + (["-revoke", args.id] if is_commerce else ["revoke", args.id]))
    print("Hosted invitation revoked: " + args.id)

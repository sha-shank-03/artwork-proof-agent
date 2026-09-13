"""Issue/revoke hosted invitations over Railway SSH; never print bearer tokens."""
import argparse
import json
from pathlib import Path
import re
import shlex
import subprocess

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

def remote(command):
    result = subprocess.run(
        ["railway", "ssh", "--project", args.project, "--environment", args.environment,
         "--service", args.service, "--", shlex.join(command)],
        capture_output=True, text=True, timeout=45)
    if result.returncode:
        raise SystemExit("Hosted invitation operation failed; remote output suppressed.")
    return result.stdout.strip()

if args.command == "invite":
    info = remote(base + (["-invite"] if is_commerce else ["invite"]))
    match = re.search(r"Invitation ([a-f0-9]+) saved", info)
    if not match:
        raise SystemExit("Unexpected invitation response; output suppressed.")
    token = remote(["cat", "/app/.local/invite.txt"])
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

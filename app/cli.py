import argparse
import json
import os
from pathlib import Path
import time
from .core import uid,digest
from .store import Store
from .main import public_run

def main():
    parser=argparse.ArgumentParser();parser.add_argument("command",choices=["invite","revoke","export","schema"]);parser.add_argument("id",nargs="?");args=parser.parse_args()
    if args.command=="schema":
        from .main import create_app
        os.environ["ALLOW_MEMORY_STORE"]="test";print(json.dumps(create_app(Store()).openapi()));return
    store=Store(os.environ["DATABASE_URL"])
    with store.transaction() as state:
        if args.command=="invite":
            token=uid();ident=uid();state["invites"][digest(token.encode())]={"id":ident,"expires":int(time.time())+7*86400,"remaining":5,"revoked":False}
            Path(".local").mkdir(mode=0o700,exist_ok=True);path=Path(".local/invite.txt");path.write_text(token);path.chmod(0o600);print(f"Invitation {ident} saved to ignored .local/invite.txt")
        elif args.command=="revoke":
            for v in state["invites"].values():
                if v["id"]==args.id:v["revoked"]=True
            print("Revocation processed")
        else:print(json.dumps(public_run(state["runs"][args.id])))

if __name__=="__main__":main()

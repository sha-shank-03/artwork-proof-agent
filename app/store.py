"""Serialized PostgreSQL aggregate for a deliberately low-volume portfolio demo."""
import copy
import json
import threading
import time
from contextlib import contextmanager
from pathlib import Path
import psycopg

def empty_state():
    return {"invites": {}, "sessions": {}, "runs": {}, "uploads": {}, "budgets": {}}

def prune(state):
    now = time.time()
    for collection in ("sessions", "uploads", "runs"):
        state[collection] = {k:v for k,v in state[collection].items()
                             if v.get("expires", now+1) > now}

def validate_storage(state):
    # Include persisted messages and duplicated preview bytes, not just upload size.
    if len(json.dumps(state).encode()) > 128 * 1024 * 1024:
        raise ValueError("Global portfolio storage allowance exceeded")
    owners = {}
    for collection in ("runs", "uploads"):
        for item in state[collection].values():
            owner = item.get("owner", "")
            owners[owner] = owners.get(owner, 0) + len(json.dumps(item).encode())
    if any(size > 25 * 1024 * 1024 for size in owners.values()):
        raise ValueError("Reviewer storage allowance exceeded")

class Store:
    def __init__(self, url=None):
        self.url = url
        self.memory = empty_state()
        self.lock = threading.RLock()
        if url:
            with psycopg.connect(url) as conn:
                conn.execute(Path(__file__).with_name("migrations").joinpath("001_init.sql").read_text())

    @contextmanager
    def transaction(self):
        if not self.url:
            with self.lock:
                snapshot = copy.deepcopy(self.memory)
                prune(snapshot)
                yield snapshot
                validate_storage(snapshot)
                self.memory = snapshot
            return
        with psycopg.connect(self.url) as conn:
            row = conn.execute("SELECT data FROM portfolio_state WHERE id=1 FOR UPDATE").fetchone()
            state = row[0]
            prune(state)
            yield state
            validate_storage(state)
            conn.execute("UPDATE portfolio_state SET data=%s,version=version+1 WHERE id=1", (json.dumps(state),))

    def ready(self):
        if self.url:
            with psycopg.connect(self.url, connect_timeout=3) as conn:
                conn.execute("SELECT 1")

"""Request-size and token-exchange limits before validation/file decoding."""
import time
from collections import deque
from starlette.responses import JSONResponse

class RequestLimits:
    def __init__(self, app):
        self.app = app
        self.attempts = {}

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http" or scope["method"] in ("GET", "HEAD", "OPTIONS"):
            return await self.app(scope, receive, send)
        upload = scope["path"] == "/uploads"
        limit = 10 * 1024 * 1024 if upload else 16384
        headers = dict(scope["headers"])
        if not upload and not headers.get(b"content-type", b"").startswith(b"application/json"):
            return await JSONResponse({"detail": "JSON required"}, 415)(scope, receive, send)
        if scope["path"] == "/session":
            now = time.monotonic()
            host = (scope.get("client") or ("unknown",))[0]
            if len(self.attempts) > 1024:
                self.attempts = {k:v for k,v in self.attempts.items() if v and v[-1] > now-60}
            times = self.attempts.setdefault(host, deque())
            while times and times[0] <= now-60:
                times.popleft()
            if len(times) >= 10:
                return await JSONResponse({"detail": "Try again later"}, 429)(scope, receive, send)
            times.append(now)
        chunks = []; total = 0
        while True:
            message = await receive()
            if message["type"] == "http.disconnect":
                return
            part = message.get("body", b""); total += len(part)
            if total > limit:
                return await JSONResponse({"detail": "Request body too large"}, 413)(scope, receive, send)
            chunks.append(part)
            if not message.get("more_body", False):
                break
        delivered = False
        async def bounded_receive():
            nonlocal delivered
            if not delivered:
                delivered = True
                return {"type": "http.request", "body": b"".join(chunks), "more_body": False}
            return await receive()
        return await self.app(scope, bounded_receive, send)

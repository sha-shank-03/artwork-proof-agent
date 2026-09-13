# Operations and release gates

Default access: seven-day invitations with five live runs; sessions up to 24 hours; report approval valid for 24 hours; seven-day run/upload retention. `uv run python -m app.cli invite` writes the bearer token to ignored `.local/invite.txt`. `uv run python -m app.cli revoke INVITATION_ID` invalidates the invitation and its sessions. Commands require this application's database URL.

Set `LIVE_ENABLED=false` to disable new analysis/resume calls. Approval records no model call or printer side effect. Cancellation revokes the lease. Calls already at the provider may finish and be billed, which is covered conservatively by the reservation ledger.

Model configuration: `claude-haiku-4-5-20251001` only until another price configuration is reviewed. Each turn counts tokens with Anthropic before reserving estimated input plus bounded output. Eight turns, $0.25/run, two live leases and $2.50/month inclusive of evaluations. Concurrent reservations lock the same PostgreSQL row; do not use independent replicas with separate budget ledgers.

## Hosted layout

Vercel hosts `web/dist`; the catalogue currently contains no genuine Claude recordings. The new `agentic-portfolio` Railway project hosts this backend alongside commerce and a **new portfolio-only PostgreSQL instance**, with separate databases, credentials and denied cross-database CONNECT privileges. The database has no public port. `ALLOWED_ORIGIN` is the exact Vercel frontend origin and the `/api` rewrite is verified. The Anthropic key is stored only in this Railway backend, not Vercel or GitHub. See [deployment commands](HOSTING.md).

The combined portfolio target is $10/month additional cost, with $5 allocated to both model providers. Existing Railway Pro usage is shared and not a free dedicated allowance. Enable backend sleeping where supported; do not add uptime traffic. Baseline memory, volume and live workload must be measured before claiming the target is met. If not affordable, keep live execution local and publish only verified static replays. No plan upgrade or credit purchase is automatic.

## Release checklist

- Deterministic file, API, budget and approval tests pass on local PostgreSQL and Linux CI.
- Docker build is verified; known release-blocking dependencies are fixed.
- All thirty defined cases run through the real Claude path; >=90% task success; zero failed safety invariants. Publish actual token usage, latency, failures and limits of the grader.
- Genuine proof recordings and PDFs pass manual visual inspection; their public pages make zero backend/model calls.
- Chromium, Firefox, WebKit, mobile, keyboard, invited upload, refresh, clarification and approval flows pass.
- Full history/build/CI secret scan and licence review pass.
- Hosted invited workflows, costs, revocation and live-disable controls verified.
- Only then merge/tag verified code and make this new repository public.

Current blocker: the supplied Anthropic account returned insufficient API credit before any billed model turn. No live success score or fabricated recording is substituted for that gate.

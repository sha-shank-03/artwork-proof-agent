# Operations and release gates

Default access: seven-day invitations with five live runs; sessions up to 24 hours; report approval valid for 24 hours; seven-day run/upload retention. `uv run python -m app.cli invite` writes the bearer token to ignored `.local/invite.txt`. `uv run python -m app.cli revoke INVITATION_ID` invalidates the invitation and its sessions. Commands require this application's database URL.

Set `LIVE_ENABLED=false` to disable new analysis/resume calls. Approval records no model call or printer side effect. Cancellation revokes the lease. Calls already at the provider may finish and be billed, which is covered conservatively by the reservation ledger.

Model configuration: `OPENAI_MODEL=gpt-5.6-luna` with `OPENAI_API_KEY` only in this backend. Each turn counts tokens with OpenAI before reserving conservative input plus bounded output. All input is costed at the $0.25/M cache-write ceiling, output at $1.20/M, with integer rounding and $0.001 reservation headroom. Reject input above 200,000 tokens. Eight turns, $0.25/run, two live leases and $2.50/month inclusive of evaluations. Concurrent reservations lock the same PostgreSQL row; do not use independent replicas with separate budget ledgers. See [migration details](LUNA_MIGRATION.md). Old Claude checkpoints require a new run; they are not silently translated.

## Hosted layout

Vercel hosts `web/dist`; public recordings are published only after the live evaluation gate. The `agentic-portfolio` Railway project hosts this backend alongside commerce and a **portfolio-only PostgreSQL instance**, with separate databases, credentials and denied cross-database CONNECT privileges. The database has no public port. `ALLOWED_ORIGIN` is the exact Vercel frontend origin and the `/api` rewrite is verified. The OpenAI key is stored in the approved Railway backend, not Vercel or GitHub. See [deployment commands](HOSTING.md).

The combined portfolio target is $10/month additional cost, with $5 allocated to model usage ($2.50 per application, now both using OpenAI). Existing Railway Pro usage is shared and not a free dedicated allowance. Enable backend sleeping where supported; do not add uptime traffic. Baseline memory, volume and live workload must be measured before claiming the target is met. If not affordable, keep live execution local and publish only verified static replays. No plan upgrade or credit purchase is automatic.

## Release checklist

- Deterministic file, API, budget and approval tests pass on local PostgreSQL and Linux CI.
- Docker build is verified; known release-blocking dependencies are fixed.
- All thirty defined cases run through the real Luna path; >=90% task success; zero failed safety invariants. Publish actual token usage, latency, failures and limits of the grader.
- Genuine proof recordings and PDFs pass manual visual inspection; their public pages make zero backend/model calls.
- Chromium, Firefox, WebKit, mobile, keyboard, invited upload, refresh, clarification and approval flows pass.
- Full history/build/CI secret scan and licence review pass.
- Hosted invited workflows, costs, revocation and live-disable controls verified.
- Only then merge/tag verified code and make this new repository public.

The earlier Anthropic access failure is retained as history. The user subsequently requested Luna; no historical Claude result can satisfy the Luna release gate. See the current verification record in LUNA_MIGRATION.md.

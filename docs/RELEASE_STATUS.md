# Current release candidate - 13 September 2026

[Artwork](https://artwork-proof-agent.vercel.app) now uses **Claude Haiku 4.5** (claude-haiku-4-5-20251001) through Anthropic's API, not Luna. The public graph, tool-loop description, traces and six genuine replay recordings agree with the deployed model. All six downloadable proof PDFs were regenerated from actual Claude results.

## Actual verification

- **30/30 Claude workflow cases** passed, with no failed cases retested.
- Six original designs under five size/decision conditions, not thirty unrelated visual tasks.
- 235,665 input / 14,822 output tokens; estimated **$0.309775** for the evaluation set. Median 20.845 s, maximum 28.85 s end-to-end. These are application estimates, not a provider invoice.
- 54 local Python tests passed; one PostgreSQL-only test is run in Linux CI. Schema generation, production build and dependency audit passed.
- **24 local offline browser checks** and **27 applicable hosted browser checks** passed across Chromium, Firefox and WebKit. Real Claude inspection, refresh, approval and telemetry were exercised. Three local-only preflight checks were intentionally skipped in the hosted invocation.
- All 12 proof-PDF pages passed visual layout review. All 16 hosted static assets checked matched the reviewed local files byte for byte.
- Source/history/build secret scan found zero matches. Railway and Vercel build/runtime log scans found zero credential matches.

Claude missed clipped text in the low-resolution sample while describing it as properly aligned. A separate digest-bound reviewer note flags the miss; its authentic report and digest are unchanged. Workflow graders are not visual-accuracy certification and no artwork is sent to a printer.

## Deployment and source

- Railway: 963f501d-5526-4fe9-bff2-3e751f3b8f4a; backend/evaluation source 47a8a764b63d587dc2d11cb01db1129fe55259ec.
- Vercel production: dpl_8FSSJWfG3BsqfgwkSdwAH2Cj4Sh4.
- Verified frontend/replay source: 480b0fbb18fd38f09c36db9b48e0b1000f69e16f.
- [Current Linux verification](https://github.com/sha-shank-03/artwork-proof-agent/actions/runs/34763361510) passed, including PostgreSQL, schema/browser checks, dependency audits and Docker build. Complete CI logs also passed the credential scan; see model-log-audit.json.

The approved Anthropic key was restored only to this backend and its obsolete OpenAI credential value cleared. No provider key is in Vercel/GitHub. Existing budgets, database credentials, hosting caps, sleeping and repository visibility were preserved. Old Luna checkpoints require a fresh analysis; historical reports remain readable. [Migration details](CLAUDE_MIGRATION.md).

Evaluation/browser invitations were revoked; the user's existing reviewer invitation files were preserved. The repository remains private on codex/initial-build with no release tag. Public source/licensing review remains separate work. The $10/month combined target is not a guaranteed bill.

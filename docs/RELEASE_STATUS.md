# Public release v0.1.0 - 13 September 2026

The [repository](https://github.com/sha-shank-03/artwork-proof-agent) is public, with `main` as the default branch and a verified `v0.1.0` release. Both the system map and recorded-run UI screenshots are embedded in the README. The companion [Commerce Support Agent](https://github.com/sha-shank-03/commerce-support-agent) is public too. Original code ownership is retained; no permissive licence was added.

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
- Vercel production: dpl_QF7KeLkh4oujxiCcEhxNTVgQhevx, READY, static Vite frontend.
- Verified publication UI/source: d93c4432b65c612d769e1d9f135891dd45427121. Subsequent audit/handoff commits are documentation-only.
- Genuine replay/PDF content remains from the reviewed Claude release, 480b0fbb18fd38f09c36db9b48e0b1000f69e16f; publication did not alter model reports or evaluation scores.
- [Final Linux verification](https://github.com/sha-shank-03/artwork-proof-agent/actions/runs/34764974329) passed, including PostgreSQL, Python safety tests, schema/browser checks, dependency audits and Docker build.

## Publication checks

- A fresh **24/24 hosted non-billed browser checks** passed on the publication deployment in Chromium, Firefox and WebKit. Three paid live checks and three local-only preflight checks were intentionally not repeated here; the 27 applicable live-deployment checks above remain the evidence for the unchanged backend.
- Complete Git blob history, working files and build assets passed both the repository scanner and exact-approved-credential scan. All **14 available completed CI runs** had zero credential matches. GitHub reported no uploaded workflow artifacts. [Audit record](publication-audit.json).
- Current Railway/Vercel build/runtime logs had zero credential matches. [Runtime log audit](publication-runtime-audit.json). Browser checks reported no page errors. The static frontend has no model-serving functions; no new log drains or keep-alive monitoring were enabled.
- [Dependency/asset review](LICENSE_REVIEW.md) and deployed browser licence notices are included. Screenshots show original synthetic fixtures and genuine recorded results, with no invitation credentials.
- The console now links to public source. The known Claude visual miss remains disclosed; workflow success is not print certification.

The approved Anthropic key was restored only to this backend and its obsolete OpenAI credential value cleared. No provider key is in Vercel/GitHub. Existing budgets, database credentials, hosting caps and sleeping were preserved. Old Luna checkpoints require a fresh analysis; historical reports remain readable. [Migration details](CLAUDE_MIGRATION.md).

Evaluation/browser invitations were revoked; the user's existing reviewer invitation files were preserved. Invite-only hosted execution remains enabled with the existing controls. See [local setup](../README.md), [invite/revoke and disable-live commands](HOSTING.md), and [operations](OPERATIONS.md). The $10/month combined target is not a guaranteed bill; actual monthly hosting spend still needs observation.

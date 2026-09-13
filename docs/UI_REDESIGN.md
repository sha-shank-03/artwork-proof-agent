# Agent console redesign — implementation plan

Build a compact Run / System map / Reviewer brief console using the existing React/Vite and FastAPI contracts. Preserve the reviewed GPT-5.6 Luna tool loop, prompts, exact-report approval, ownership and cost ceilings.

1. Add allowlisted per-call model events with real duration and usage; reject private metadata and never backfill invented timing into old recordings.
2. Add an interactive system map distinguishing isolated file processing, deterministic measurements, Luna visual inspection, report generation, human approval and PostgreSQL persistence.
3. Synchronize replay controls with findings, reports, approvals and receipts; provide state-aware next actions and readable event details.
4. Add a reviewer brief with architecture, actual evaluation results, limitations and recording provenance. Generate the six already verified recordings through the existing gate and visually inspect every proof PDF page before public asset publication.
5. Verify deterministic safety tests, contract generation, browser tests on Chromium/Firefox/WebKit, keyboard/mobile layouts, replay zero-backend behavior and invited workflows.
6. Deploy only to the existing portfolio services/projects. Use bounded temporary test invitations, revoke them afterwards, and report remaining limitations honestly.

No provider/model changes, new keys, plan upgrades, external tracing service, production-repository edits or GitHub visibility changes are included. Public replay and documentation navigation must not call the API. The custom React rendering pipeline is retained; this is not a chat-framework migration.

Model-call views show only recorded status, duration, tokens, estimated cost and concise public summaries. No prompts, provider error bodies, credentials, raw artwork instructions or hidden model reasoning are exported. Historical recordings show unavailable timing explicitly.

Status: plan recorded; implementation and verification in progress.

## Implemented and verified locally

The system-map landing view, component inspector, synchronized run playback, state-aware next actions, reviewer brief, light/dark themes and direct hash links are implemented. Keyboard/mobile layouts and all 24 offline browser checks passed in Chromium, Firefox and WebKit. A WebKit initial-navigation race and an invitation-history race have regression coverage.

The additive telemetry backend is deployed. The refreshed live set passed 30/30 after one network-failed case was rerun; initial outcomes are retained. Final-case model cost estimate is $0.039116, excluding any unobserved failed-attempt usage. Six authentic recordings include measured per-call timing, provider token counts and estimated cost.

All twelve pages of the six proof PDFs were rendered and inspected. Document layout passed. A visual miss in the low-resolution model report is annotated separately without changing the authentic report or digest. The workflow grader is not a visual-accuracy certification.

Python: 52 tests passed locally; PostgreSQL integration runs in Linux CI. Dependency and working/history/build secret scans passed. Models, prompts, keys, budgets, hosting resources and repository visibility are unchanged.

Frontend production rollout and hosted UI checks remain to be completed.

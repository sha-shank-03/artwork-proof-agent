# Release candidate status - 13 September 2026

The redesigned [Artwork console](https://artwork-proof-agent.vercel.app) is deployed. It opens on an interactive system map, with synchronized Run view and reviewer brief. Six genuine GPT-5.6 Luna recordings and downloadable proof PDFs work anonymously without backend/model calls. All twelve proof pages were rendered and visually inspected.

The current telemetry refresh passed 30/30 final workflow cases after one network-failed case was rerun; the initial 29/30 attempt is preserved. Final-case model usage estimate: $0.039116, excluding unobserved failed-request usage. All 27 applicable hosted browser checks passed in Chromium, Firefox and WebKit, including real Luna execution, refresh before approval and model-call telemetry. Local Python tests: 52 passed plus one PostgreSQL-only test exercised in CI. [Linux CI for the UI code](https://github.com/sha-shank-03/artwork-proof-agent/actions/runs/34760379936) passed, including generated contracts, PostgreSQL, browser tests, dependency/secret checks and Docker build.

A visual miss in the low-resolution model report is annotated separately in the UI and reviewer guide; its authentic text and digest remain unchanged. Workflow safety scores are not visual-accuracy certification. Demo print specifications are not commercial print rules, and no artwork is sent to a printer.

The isolated Railway backend remains on GPT-5.6 Luna with approved OpenAI access, hashed invitations, exact-report approval, spending reservations and private PostgreSQL. Models, prompts, keys, budgets, resources and repository visibility were not changed by the UI rollout. Test invitations were revoked; the existing reviewer invitation files were preserved.

Prior hosted file-validation, ownership, cancellation, restart, revocation and live-disable checks are retained in hosting-verification.json. The earlier Claude access failure and later Luna migration remain documented as history, not rewritten as current failures.

The new repository remains private on codex/initial-build. No verified release tag or visibility change has been made. Remaining separate publication work: final paired source/licensing review, merge/tag and deliberate public release. The $10/month combined target remains a planning estimate, not a bill guarantee. See [UI verification](UI_VERIFICATION.md), [actual evaluations](EVALUATIONS.md) and [operations](HOSTING.md).

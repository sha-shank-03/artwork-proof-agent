# Connected console verification - 13 September 2026

Historical UI-redesign report, before the requested model changes. For current
Claude validation and limitations, see [Claude migration](CLAUDE_MIGRATION.md).

## Story

A reviewer opens the system map, inspects integration boundaries, plays a genuine recorded run, and follows measured model calls through evidence and a human decision. An invited reviewer can also start a synthetic live run, refresh its persisted state and approve the exact result. Public browsing never needs a live backend.

## Verified boundaries

| Boundary | Actual evidence |
|---|---|
| UI and navigation | 24 offline checks passed locally across Chromium, Firefox and WebKit. System-map nodes, theme persistence, direct hash links, keyboard/mobile layouts, playback and future-output hiding were exercised. |
| Public deployment | https://artwork-proof-agent.vercel.app is live with the new console. Public map, guide and replay checks block /api requests and pass without backend access. |
| Client to API | All three hosted browsers authenticated using temporary invitations and started real provider-backed runs. |
| API to database | Refresh before approval restored the persisted pending result; approval produced a bound simulated receipt. |
| Model to telemetry | 30/30 final evaluation cases checked call count, model, nonnegative measured durations, provider tokens and total estimated cost. |
| API response to UI | Per-call telemetry rendered in expanded trace entries. All 27 applicable hosted browser tests passed. Three local-only preflight tests were intentionally skipped in this hosted invocation; the real-model flow ran in all browsers. |
| Safety | No receipt before approval; replay cannot approve or execute. Existing isolation, digest and budget tests remain in the backend suite. All six report digests and genuine proof exports passed publication validation. |
| Assets | Six replay JSON files and six proof PDFs exactly match the reviewed local assets; all twelve PDF pages passed visual layout review. |

## Failures and limitations retained

The initial refresh set was 29/30: one harness request failed with URLError. Only that case was rerun; the original attempt and rerun policy remain in the downloadable results/history. Final recorded-case usage estimate is $0.039116, excluding any unobserved usage from the failed request. This is not a provider invoice, a consecutive-run success rate or a production reliability claim.

The low-resolution recording contains a visual miss: one model finding says no obvious clipping is visible although sample text is truncated. A separate version-bound reviewer note flags this; the authentic report is not edited. The workflow grader does not certify visual correctness.

A login/history race and an initial hash-navigation race exposed by WebKit were fixed and regression-tested. Missing historical timings are displayed as unavailable, not fabricated. The system map represents allowed architecture paths rather than a live traffic animation; replay advances at an explicitly illustrative event pace.

## Deployment provenance

- UI code commit: `4b06a3b3f7c9c5c9a8e5b632dd15aa323499b872`.
- Telemetry backend source: `e3011b1`; genuine replay manifests retain their full recording commit.
- Railway deployment: `980ff84e-cb09-4532-a2b3-743df442e1ad`.
- Vercel deployment: `dpl_8hFT7o1YiSZDxFwP5ax9SaJkWsst` (CLI upload of the tested working tree; the subsequent UI commit contains that source).
- Code CI: https://github.com/sha-shank-03/artwork-proof-agent/actions/runs/34760379936.
- No key, model, prompt, budget, resource or repository visibility changes were part of this UI rollout.

Temporary test invitations are revoked after verification. The pre-existing reviewer invitation files were not overwritten. Backend sleeping, one-replica resource caps and existing readiness checks remain enabled. Public source publication and a verified release tag remain separate work.

## Final security and source check

Both Linux code CI pipelines passed, including PostgreSQL, schema generation, offline browser tests, dependency audits, secret scans and Docker builds. Railway build/runtime logs, Vercel build logs and complete CI logs were scanned for credential patterns and the known provider credential without printing raw data: zero matches. Non-secret scan evidence is in ui-log-audit.json. The hosted static recordings match their reviewed local files byte for byte.

Subsequent handoff commits are documentation-only and do not change the verified runtime source. No permissive licence was added and both GitHub repositories remain private.

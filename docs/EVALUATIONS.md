# Genuine live evaluation results

## UI telemetry refresh - 13 September 2026

All twelve pages of the six exported proof PDFs were rendered and visually inspected. Layout, image aspect ratios and pagination passed. This is document QA, not validation of every model statement: the low-resolution recording misses visibly truncated text in one finding. That limitation is annotated separately in the UI and reviewer guide without changing the original report or digest.

The refreshed set initially passed 29/30; one harness request failed with URLError. Only that failed case was rerun, and the final per-case outcome is 30/30. The original attempt and exact rerun IDs are retained in evaluation-history.json and the retryNotice field of evaluation-results.json. No failed attempt was silently relabelled.

Final recorded-case model usage totals $0.039116. This excludes any unobserved usage from the network-failed attempt; the database spending ledger retains reservations/settlements. Model-call duration and token/cost metadata were graded against persisted run totals. Public recordings now carry genuine per-call telemetry.

Actual result: **30/30** on commit `e3011b10929f39961bfb3bcc01bbc4bbdf9d1639`. Six original designs under five size/decision conditions, not thirty unrelated visual tasks.

Application-estimated model usage: **$0.039116**. Median end-to-end latency **14.52s**; maximum **22.71s**. Polling, tool processing and automated reviewer decisions are included. These estimates are not a provider invoice.

Grading checks real provider usage, hash/report binding, evidence validity, page inspection, measured/model separation, approval, proof PDF generation, quotas and idempotency. Visual accuracy still needs human review. Demo specifications are not commercial print certification. Earlier access failures and per-case outcomes are preserved in evaluation-history.json and evaluation-results.json. Generated proof PDFs must still be visually reviewed before release.

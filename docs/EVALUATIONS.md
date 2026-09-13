# Genuine Luna evaluation results

Actual result: **30/30** workflow cases through OpenAI `gpt-5.6-luna`, prompt `artwork-v2-luna`, backend source commit `1fe66948fa8c6d1f0e7401d54dbb517f0a938c2e` on 13 September 2026. All defined safety checks passed. Six original designs under five size/decision conditions, not thirty unrelated visual tasks.

Conservative application-accounted set cost: **$0.039310**; **114170 input / 8944 output tokens**. Median end-to-end latency **11.98s**; maximum **17.70s**. Tool processing, polling and automated reviewer decisions are included. Input is estimated at the cache-write ceiling, so this is not an exact provider invoice.

Cases cover clean, low-resolution, wide, transparent, embedded-instruction and two-page PDF artwork, including missing dimensions, approval/rejection and idempotent receipts. Graders verify real provider usage, requested model, hash/report binding, valid evidence, all-page inspection, measured/model separation, proof PDF generation and spending bounds. They do not certify visual accuracy or production print readiness.

An SSH invitation-read interruption occurred after 20 passing cases. Those rows were retained and the same backend/model/commit evaluation resumed for the final 10; no completed case was replayed or replaced. The runner now validates the saved prefix before resuming. Test invitations were cleaned up separately.

Earlier Anthropic access failure, the first Luna schema failure and a successful corrected smoke case remain in [evaluation history](evaluation-history.json). The first Luna failure exposed a too-broad tool schema; it was fixed without relaxing server validation or increasing the eight-turn cap.

The public replay catalogue remains unpublished until six proof packages receive visual review and the final portfolio publication checks are complete. This report verifies the Railway provider migration, not the entire original portfolio release.

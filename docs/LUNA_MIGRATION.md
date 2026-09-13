# GPT-5.6 Luna migration — 13 September 2026

## Inventory and target

The original Artwork worker used Anthropic Messages with `claude-haiku-4-5-20251001`, no thinking option, five application-owned tools, a 1,500-output-token ceiling, and persisted messages. The user explicitly requested replacing it with `gpt-5.6-luna` in the existing Railway artwork service. Commerce and its GPT-4.1 Mini integration are unchanged.

This is a provider/transport migration, not just a model-string replacement. The application-owned loop now uses OpenAI Responses; it does not introduce hosted sandboxes, extra agents, or printer access. The existing OpenAI key is reused only in the approved artwork backend. No key belongs in the frontend, replay files or Git.

## Compatibility changes

- `OPENAI_MODEL=gpt-5.6-luna`; OpenAI Python SDK pinned in dependency locks. No fallback model or new API key.
- Explicit `reasoning.effort=none` preserves the old non-thinking latency/cost class. A targeted clarification was added after a real schema failure (below), versioned `artwork-v2-luna`.
- Strict function schemas preserve all tool names and business validation. `parallel_tool_calls=false` makes preview inspection and report submission separate turns.
- Preview results are Responses `input_image` items with explicit high detail, still bounded to the application's 1,200-pixel previews. Original image/PDF decoding restrictions are unchanged.
- `store=false`; all output items and function call IDs are checkpointed in the application's private PostgreSQL state. Internal messages/any encrypted reasoning never enter public run/replay exports.
- Official input-token counting runs before each paid request. A 200,000-input-token ceiling prevents unreviewed long-context pricing. Output remains capped at 1,500 tokens.
- Standard short-context pricing is $0.20/M input, $0.02/M cache reads, $0.25/M cache writes and $1.20/M output. For a safe upper estimate, the ledger rounds up all input at $0.25/M, plus output at $1.20/M. Reservations add $0.001 headroom; uncertain failures retain the reservation. Estimates may exceed the invoice because cache discounts are not assumed.
- Eight turns, two concurrent leases, $0.25/run and $2.50/month remain unchanged. This is Artwork's allocation; Commerce has a separate $2.50 allocation, now both using OpenAI. They must not each start independent duplicate local ledgers.
- Existing Claude checkpoints are not translated or relabelled. Start a new run; historical failed Claude evaluations remain historical evidence.
- The replay release gate requires 30 real OpenAI/Luna cases, at least 90% task success and all safety invariants. A successful model request alone is not release approval.

## Verification

**Railway migration verified.** Runtime inspection confirmed `gpt-5.6-luna`, the existing OpenAI key present, `LIVE_ENABLED=true`, and no remaining Anthropic key/model variables. Backend deployment `f2129d4b-664b-4199-9e10-9f3e1c483558` runs the verified worker from `1fe66948fa8c6d1f0e7401d54dbb517f0a938c2e`. The frontend production deployment is `dpl_AJnY8QyVTL85he5xqzpueGEuUqgq` at https://artwork-proof-agent.vercel.app. Commerce was not changed.

Actual hosted evaluation: **30/30 passed**, 114,170 input / 8,944 output tokens, **$0.039310** conservative set cost; median 11.99 seconds and maximum 17.70 seconds. See [per-case evidence](evaluation-results.json) and [methodology/history](EVALUATIONS.md). The six genuine recordings remain in private evaluation output until final replay/PDF publication review.

Local Python suite: **47 passed**, one PostgreSQL-only check skipped locally; PostgreSQL and Docker passed the source CI. **12/12 hosted browser checks passed** on the corrected production frontend: public no-backend browsing, mobile/keyboard access, delayed-auth regression and real Luna analysis/refresh/approval, each in Chromium, Firefox and WebKit. A genuine two-page proof report was rendered and visually inspected; this is not a review of all six future public proof packages. Dependency audits and working-tree/history/build/CI/Railway-log credential scans passed.

Deterministic transport tests cover image/call-ID replay, clarification continuation, malformed arguments, input bounds, uncertain usage, legacy-checkpoint rejection, strict schemas and integer pricing. Model metadata lookup is prohibited by the existing key's `api.model.read` scope; actual Luna requests succeed. No key permissions were broadened. Provider files on the user's Mac were not changed, and no purchase or plan upgrade was made.

First hosted baseline on `118edb0`: `clean-1` failed safely after eight turns, with 14,383 input / 1,487 output tokens and $0.005383 conservative cost. Luna completed all inspections but repeatedly included `measured` findings in its report. The shared public report schema incorrectly advertised that category as model input, despite the validator forbidding it. Fixed by narrowing the model-only tool schema to `model-suggested` / `requires-human-review` and preview citations, while leaving the public merged schema and server-side safety checks intact. A single prompt sentence explains that code adds measured findings. No extra turns or weakened validation.

Operational findings: a Railway SSH token-read interruption paused the evaluation after 20 passing cases. Exact test invitations were revoked and the same set resumed without repeating those cases; the runner now checks provider/model/commit and the passing prefix. Browser verification also exposed a pre-existing login race: a late unauthenticated history response could overwrite successful sign-in. An authentication epoch now ignores stale results. The deterministic regression failed against the old hosted build and passed in all three browsers after the fix; all three live approval tests then passed. No backend authorization was weakened.

Remaining original-release work: render/review all six public proof packages, publish genuine replay assets, run the final publication review, then make/tag the portfolio repositories public. Both repositories remain private; the completed provider migration is not claimed as completion of that larger release.

## Official sources

- [Luna model and supported capabilities](https://developers.openai.com/api/docs/models/gpt-5.6-luna)
- [GPT-5.6 migration guidance](https://developers.openai.com/api/docs/guides/upgrading-to-gpt-5p6-sol)
- [API pricing](https://developers.openai.com/api/docs/pricing)
- [Function calling and multimodal tool results](https://developers.openai.com/api/docs/guides/function-calling)

# Claude migration - 13 September 2026

The user's latest choice supersedes the earlier Luna migration: Artwork uses
`claude-haiku-4-5-20251001` through Anthropic's Messages API. The original Claude
tool-loop design was restored while retaining the newer telemetry, stricter
visual finding schemas, isolation, approval controls and bounded recovery.

The model selects the same five application tools. Each call can request one
tool; actual arguments are validated by application code. Every page must be
inspected before submission. Code-owned measurements never become model-owned
findings. Claude does not modify artwork, approve reports or send print jobs.

## API, checkpoints and cost

The Anthropic SDK uses native `tool_use` / `tool_result` messages, preserving call
IDs and base64 PNG previews. Extended thinking and prompt caching are not enabled.
The provider counts input before reservation; the bound is 180,000 input tokens
and 1,500 output tokens. Standard pricing is $1/M input and $5/M output, plus
$0.001 reservation headroom. Unknown failures consume the outstanding reservation
conservatively. No automatic paid-call retries, fallback or limit increases.

The same locked application ledger retains prior usage; it is not reset when
providers change. Eight turns, $0.25/run, two concurrent runs and $2.50/month remain.
Only `ANTHROPIC_API_KEY` is needed in this Railway backend; Vercel gets no keys.
Luna checkpoints cannot resume as Claude. Existing reports remain readable and
retain the original model identity. New prompt identifier: `artwork-v3-claude`;
the prompt's actual behavior text is unchanged from the last reviewed version.

Sources: [Claude API](https://platform.claude.com/docs/en/claude_api_primer),
[token counting](https://platform.claude.com/docs/en/build-with-claude/token-counting),
[Haiku pricing](https://platform.claude.com/docs/en/about-claude/pricing).

## Validation status

Local: 54 deterministic tests passed, one PostgreSQL-only test skipped locally;
schema generation, frontend build and Python dependency audit passed. All 24
offline browser checks passed across Chromium, Firefox and WebKit.

The full Claude set passed **30/30**: six original designs under five size/decision
conditions. No failed cases were retested into this score. Case usage: 235,665
input / 14,822 output tokens; estimated **$0.309775**. Median end-to-end latency
20.845 s; maximum 28.85 s. These are application estimates, not a provider invoice.

Six genuine Claude recordings and proof PDFs are deployed anonymously. All twelve
proof pages were rendered and visually reviewed for layout. The low-resolution
report incorrectly describes clipped text as properly aligned. Its original text
and report digest are unchanged; a separate digest-bound reviewer note flags the
miss. Workflow graders do not certify visual accuracy.

The graph displays **Claude Haiku 4.5** and a bounded Claude tool loop. Exact API
model IDs remain in telemetry. The approved Anthropic credential was restored
only to this Railway backend; the obsolete OpenAI credential value was cleared.
No Vercel/GitHub key, database credential, budget, resource or visibility change.

Railway deployment: `963f501d-5526-4fe9-bff2-3e751f3b8f4a`.
Backend/evaluation source: `47a8a764b63d587dc2d11cb01db1129fe55259ec`.
Vercel production deployment: `dpl_8FSSJWfG3BsqfgwkSdwAH2Cj4Sh4`.
Hosted browser checks: **27/27 applicable checks passed**. Genuine Claude
inspection, refresh before approval and token/duration telemetry were verified
in Chromium, Firefox and WebKit. Three local-only preflight checks were skipped
in this hosted invocation. The public graph was inspected with no browser errors.
All 16 checked static assets matched reviewed bytes, including all six PDFs.

Temporary evaluation/browser invitations were revoked. The existing reviewer
invitation metadata and private file permissions remain unchanged.
Frontend/replay source: `480b0fbb18fd38f09c36db9b48e0b1000f69e16f`.
[Linux CI](https://github.com/sha-shank-03/artwork-proof-agent/actions/runs/34763361510)
passed, including PostgreSQL, schema, browser, dependency, secret and Docker checks.

Railway build/runtime logs, Vercel build logs and complete CI logs have zero
credential matches. See model-log-audit.json and RELEASE_STATUS.md. Subsequent
handoff commits are documentation-only and do not change the verified runtime.

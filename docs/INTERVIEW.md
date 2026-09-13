# Walkthrough and interview preparation

Use the original low-resolution fixture, request a three-inch print, inspect measured DPI separately from Luna's visual concerns, then approve the exact proof version. Refresh before approval to demonstrate persistence. Download the JSON report and PDF. Claim live validation only to the extent recorded in LUNA_MIGRATION.md and the actual evaluation report.

**Why use tools for vision?** The model chooses which page/measurement to inspect, but it cannot invent a measured DPI or declare a file safe. Tools return actual decoded metadata and bounded previews. The final report is validated and merged with measured findings in code.

**Can you trust PDF DPI?** Not from a rendered preview. PDFs can mix vector objects and embedded raster images. This release reports page points and a human-review requirement, avoiding a misleading precision claim.

**How is approval bound to artwork?** The report includes a cryptographic hash of the uploaded bytes, a report version and a versioned spec. The server verifies the digest, artwork hash, version and expiry. A replacement upload starts a new run; the old receipt cannot approve it.

**What about prompt injection inside an image?** Treat it as untrusted visual content. There is no send-to-printer tool and the model cannot approve a report. The embedded-instructions fixture tests the model's handling; the server's restricted action surface supplies the hard boundary even if the prompt fails.

**How do you handle model/provider failure?** Bound turns, output tokens, cost and wall time. Persist tool results and pending questions. Disable automatic provider retries; surface an understandable failed/recoverable state and conservatively account for uncertain usage.

**What would production require?** Stronger decoder sandboxing/fuzzing, a normalized schema/object store, durable job queue, richer print-spec validation, independent visual evaluation, enterprise auth, operational monitoring and proper document data governance.

**AI-development disclosure.** Codex assisted in implementing and testing this repository. The user requested replacing the original Claude runtime with GPT-5.6 Luna on 13 September 2026. This is not a claim that Claude Code authored the project. Deterministic fixtures and mocked/offline checks are not represented as genuine model executions. Review and understand the tool loop, validation code, tests and limitations before presenting this work in interviews.

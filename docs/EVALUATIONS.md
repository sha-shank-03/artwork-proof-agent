# Evaluation status — incomplete

The 30-case live set has not completed. A real-provider attempt on commit `5977b81a4630a1c52df8e4df018b65ea4210f550` stopped on the first case because Anthropic rejected access before a billed model turn. Result: **0 successful live cases; 0 input/output tokens; $0 application model usage for that attempt**. The earlier token-count probe explicitly reported insufficient API credit.

Case `clean-1`, run `3886590d69a2fa07b303842677beb25145b4783aff87a176`: upload hash binding passed, no unapproved receipt existed, spending remained within limits, but no report/approval state or real provider token usage was produced. This is an access blocker, not a visual-quality benchmark result. No fake Claude recording is published.

The catalogue covers six original designs under five size/approval conditions. Graders check hash binding, missing-size pause without model usage, real provider token usage, exact report digest, evidence references, page inspections, measured/model separation, proof PDF generation, human decision outcome and receipt idempotency. They do not certify the model's visual accuracy or print readiness. At least 90% task success plus all safety invariants are required for release; all 30 cases must actually run through the provider.

Separate verification already passed: 30 deterministic tests against local PostgreSQL, public-shell checks in Chromium/Firefox/WebKit, and invited upload/refresh/cancel tests in all three browsers without model calls. Linux CI also passed those offline gates and the Docker build. These checks do not replace live-provider evaluation.

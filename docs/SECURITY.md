# Threat model and limitations

Trust boundaries: anonymous static browser, invited reviewer, uploaded binary content, decoder subprocess, provider/model, tool executor, PostgreSQL. Main assets: provider credential, artwork ownership, approval integrity, spending budget and execution history.

Controls tested locally: request byte limits before parsing, spoofed MIME rejection, unsupported file signatures, encrypted/too-long PDFs, malformed binaries, decoded pixel bounds, exact Origin, hashed expiring/revocable invitation tokens, owner isolation, stale report/hash/version rejection, duplicate approval, measured/model separation, output-schema/citation validation and concurrent budget reservations.

The decoder never receives a model-generated command or arbitrary filesystem path. SVG is explicitly unsupported. The renderer is isolated with timeout/CPU bounds; Linux also applies an address-space cap. This is not a hardened untrusted-document processing service—production use would need container/seccomp isolation, broader fuzzing, robust concurrency admission and independent security review.

Visual judgments are uncertain. Tiny text, precise object positioning, colour management, bleed, fonts and embedded PDF raster resolution may require specialist prepress review. A low-resolution preview is not a print certificate. The original artwork is never silently changed. Approval records human review, not a printing instruction.

No private model reasoning is displayed. Provider error bodies and keys are not logged. The browser never receives provider keys. Public replay export must remove internal messages, ownership/session identifiers and leases. The owner should scan complete history, build artifacts and CI logs before repository visibility changes.

Known implementation trade-offs: serialized JSONB writes; opportunistic physical retention cleanup while the service sleeps; in-memory session-exchange throttling; a small synthetic development evaluation set; no enterprise SSO; no real printer integration. Replacing artwork creates a new run rather than editing a past approved report. The 30-case Luna evaluation gate is necessary but does not certify visual accuracy; human prepress review remains required.

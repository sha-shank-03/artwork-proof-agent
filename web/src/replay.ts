import { runSchema, type Run } from "./api";
import { replayState } from "./console-types";
export function projectRun(
  run: Run | null | undefined,
  step: number,
): Run | null {
  if (!run) return null;
  const events = run.events.slice(0, step),
    atEnd = step >= run.events.length;
  if (atEnd) return run;
  const reportReady = events.some((e) => e.kind === "report");
  const summary = [...events]
    .reverse()
    .find((e) => e.kind === "report" || e.title === "Clarification needed");
  return {
    ...run,
    events,
    state: runSchema.shape.state.parse(replayState(events, run.state, false)),
    summary: summary?.detail || "",
    error: events.some((e) => e.kind === "error") ? run.error : "",
    report: reportReady ? run.report : null,
    reportDigest: reportReady ? run.reportDigest : "",
    receipt: events.some(
      (e) => e.kind === "approval" && e.title === "Proof approved",
    )
      ? run.receipt
      : null,
  };
}

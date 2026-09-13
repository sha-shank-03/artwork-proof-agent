export type AppKind = "commerce" | "artwork";
export type ConsoleView = "run" | "system" | "brief";
export type Call = {
  id: string;
  phase: "started" | "completed";
  model: string;
  durationMs?: number | null;
  inputTokens?: number | null;
  outputTokens?: number | null;
  costMicros?: number | null;
};
export type TraceEvent = {
  seq: number;
  kind: string;
  title: string;
  detail: string;
  at: string;
  call?: Call | null;
};
export type ConsoleRun = {
  id: string;
  state: string;
  model: string;
  promptVersion: string;
  turns: number;
  usedMicros: number;
  inputTokens?: number;
  outputTokens?: number;
  events: TraceEvent[];
};
export type Provenance = {
  recordedAt: string;
  commit: string;
  providerVerified: boolean;
};
export const money = (micros: number) => "$" + (micros / 1e6).toFixed(4);
export function componentFor(event: TraceEvent): string {
  if (event.call || event.kind === "model") return "llm";
  if (event.kind === "mcp" || event.title === "audit_mcp") return "mcp";
  if (event.title.includes("browser")) return "browser";
  if (event.kind === "approval" || event.kind === "input") return "reviewer";
  if (event.kind === "receipt") return "api";
  if (
    event.title.includes("measure") ||
    event.title.includes("preview") ||
    event.title.includes("spec")
  )
    return "tools";
  if (event.kind === "report" || event.kind === "proposal") return "api";
  return "agent";
}
export function replayState(
  events: TraceEvent[],
  fallback: string,
  atEnd: boolean,
): string {
  if (atEnd) return fallback;
  if (!events.length) return "queued";
  let state = "running";
  for (const e of events) {
    const title = e.title.toLowerCase().replaceAll("_", " ");
    if (e.kind === "error") state = "failed";
    else if (title.includes("cancel")) state = "cancelled";
    else if (e.kind === "report" || title === "awaiting approval")
      state = "awaiting_approval";
    else if (title === "clarification needed" || title === "awaiting input")
      state = "awaiting_input";
    else if (
      title === "completed" ||
      title === "proof approved" ||
      title === "proof rejected"
    )
      state = "completed";
    else if (
      title === "agent started" ||
      title === "analysis started" ||
      title === "explicit recovery" ||
      title === "reviewer clarification"
    )
      state = "running";
  }
  return state;
}
export function nextAction(
  state: string,
  replay: boolean,
): { title: string; text: string } {
  const prefix = replay ? "Recorded state" : "Current state";
  const items: Record<string, [string, string]> = {
    queued: [
      "Ready to begin",
      replay
        ? "Play the recording to reveal each event and its evidence."
        : "Choose a case or artwork, then start a bounded investigation.",
    ],
    running: [
      "Investigation in progress",
      "The agent can request a scoped tool, return findings, or ask for missing information. Its next choice is not predetermined.",
    ],
    awaiting_input: [
      "Reviewer input required",
      replay
        ? "At this recorded point, only reviewer input could resume the run. Advance playback to inspect the next recorded event; replay cannot send an answer."
        : "The run is paused. Answer the clarification before the agent can continue.",
    ],
    awaiting_approval: [
      "Human approval required",
      replay
        ? "The recorded run paused for review of the exact proposal or report. Advance playback to inspect the decision. Replay cannot approve or execute anything."
        : "Review the exact proposal or report. Approval permits a server recheck; rejection executes no action.",
    ],
    completed: [
      "Run complete",
      "Inspect the evidence and outcome. Any receipt represents a simulated action, not a payment, message or print order.",
    ],
    failed: [
      "Stopped safely",
      "Inspect the recorded error. Recovery is explicit; uncertain calls and side effects are never blindly repeated.",
    ],
    cancelled: [
      "Run cancelled",
      "No further tools can execute for this run. Existing audit events remain available.",
    ],
  };
  const [title, text] = items[state] || [
    "State unavailable",
    "Refresh the authenticated workspace to verify the current state.",
  ];
  return { title: prefix + " · " + title, text };
}

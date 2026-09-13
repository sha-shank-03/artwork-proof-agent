import {
  useEffect,
  useId,
  useRef,
  useState,
  type Dispatch,
  type SetStateAction,
} from "react";
import {
  Activity,
  ArrowRight,
  ArrowUpRight,
  BookOpen,
  Box,
  Check,
  CheckCircle2,
  ChevronLeft,
  ChevronRight,
  Clock3,
  Database,
  FileCheck2,
  Globe,
  Image,
  Layers3,
  LockKeyhole,
  Moon,
  Network,
  Pause,
  Play,
  Plug,
  ScanLine,
  ShieldCheck,
  SkipBack,
  SkipForward,
  Sparkles,
  Sun,
  UserCheck,
  Workflow,
} from "lucide-react";
import {
  componentFor,
  money,
  nextAction,
  type AppKind,
  type ConsoleRun,
  type ConsoleView,
  type Provenance,
  type TraceEvent,
} from "./console-types";
import "./console.css";

export function ConsoleHeader({
  app,
  view,
  onView,
}: {
  app: AppKind;
  view: ConsoleView;
  onView: (v: ConsoleView) => void;
}) {
  const [theme, setTheme] = useState(() => {
    try {
      return localStorage.getItem("console-theme") === "light"
        ? "light"
        : "dark";
    } catch {
      return "dark";
    }
  });
  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    try {
      localStorage.setItem("console-theme", theme);
    } catch {
      /* Theme preference is optional. */
    }
  }, [theme]);
  const artwork = app === "artwork";
  return (
    <>
      <header className="console-header">
        <a className="console-brand" href="/">
          <span className="console-mark">
            {artwork ? <ScanLine size={21} /> : <Layers3 size={21} />}
          </span>
          <span>
            {artwork ? "Artwork" : "Commerce"}
            <small>AGENT CONSOLE</small>
          </span>
        </a>
        <nav className="console-nav" aria-label="Console views">
          {(
            [
              ["run", "Run view", Activity],
              ["system", "System map", Network],
              ["brief", "Reviewer brief", BookOpen],
            ] as const
          ).map(([id, label, Icon]) => (
            <button
              key={id}
              aria-current={view === id ? "page" : undefined}
              onClick={() => onView(id)}
            >
              <Icon size={15} />
              {label}
            </button>
          ))}
        </nav>
        <div className="console-utilities">
          <a
            href={
              artwork
                ? "https://commerce-support-agent.vercel.app/"
                : "https://artwork-proof-agent.vercel.app/"
            }
          >
            {artwork ? "Commerce" : "Artwork"}
            <ArrowUpRight size={13} />
          </a>
          <button
            aria-label={
              theme === "dark"
                ? "Switch to light theme"
                : "Switch to dark theme"
            }
            onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
          >
            {theme === "dark" ? <Sun size={16} /> : <Moon size={16} />}
          </button>
        </div>
      </header>
      <section className="console-title">
        <div>
          <div className="eyebrow">Independent portfolio / Shashank</div>
          <h1>
            {artwork ? "Artwork preflight & proof" : "Commerce support agent"}
          </h1>
          <p>
            {artwork
              ? "Measured checks. AI-assisted inspection. Your final approval."
              : "From a customer issue to an evidence-backed, controlled resolution."}
          </p>
        </div>
        <div className="system-label">
          <ShieldCheck size={15} />
          <span>
            One agent. Explicit boundaries.
            <small>Synthetic data · simulated actions</small>
          </span>
        </div>
      </section>
    </>
  );
}

type NodeInfo = {
  id: string;
  title: string;
  tag: string;
  sub: string;
  input: string;
  output: string;
  control: string;
  next: string;
  icon: typeof Box;
  tone?: string;
};
function nodesFor(app: AppKind, model: string): NodeInfo[] {
  const artwork = app === "artwork";
  return [
    {
      id: "reviewer",
      title: "Reviewer",
      tag: "Human decision",
      sub: artwork ? "Version-bound proof approval" : "Exact-action approval",
      input: "A pending proposal or report, with evidence.",
      output: "Start, clarification, approval or rejection.",
      control: artwork
        ? "Approval binds artwork hash and report version."
        : "Approval binds exact arguments and order version.",
      next: "Approval permits a server recheck. Rejection executes nothing.",
      icon: UserCheck,
      tone: "human",
    },
    {
      id: "api",
      title: artwork ? "FastAPI" : "Go / GraphQL",
      tag: "Application authority",
      sub: "Identity · policy · action gate",
      input: "Authenticated requests and validated worker results.",
      output: artwork
        ? "Owned reports and simulated approval receipts."
        : "Scoped evidence and simulated action receipts.",
      control: "Ownership, quotas, expiry and idempotency are checked in code.",
      next: "Persist verified state. No model output can bypass these checks.",
      icon: ShieldCheck,
    },
    {
      id: "agent",
      title: "Python agent",
      tag: "Orchestration",
      sub: artwork ? "Bounded Claude tool loop" : "OpenAI Agents SDK",
      input: "Run-scoped input and reviewer clarifications.",
      output: "Typed tool requests, checkpoints and validated findings.",
      control:
        "One agent; bounded turns, timeout, cancellation and explicit recovery.",
      next: "Request a tool, ask for clarification, or pause for approval.",
      icon: Workflow,
    },
    {
      id: "llm",
      title:
        model === "gpt-5.6-luna"
          ? "GPT-5.6 Luna"
          : model === "claude-haiku-4-5-20251001"
            ? "Claude Haiku 4.5"
            : model,
      tag: "LLM call",
      sub: artwork
        ? "Text + image → typed findings"
        : "Evidence → tool choice / resolution",
      input: artwork
        ? "Measured context, demo specs and bounded page previews."
        : "Synthetic ticket, scoped evidence and available tool schemas.",
      output: "Tool requests or a structured response; never authorization.",
      control:
        "8 model turns · $0.25/run ceiling. Provider keys stay server-side.",
      next: "The application validates the response before any tool or action proceeds.",
      icon: Sparkles,
      tone: "ai",
    },
    {
      id: "db",
      title: "PostgreSQL",
      tag: "Persistence",
      sub: "Runs · approvals · receipts",
      input: "Application-validated state updates.",
      output: "Persisted state, usage ledger and verified checkpoints.",
      control: "Portfolio-only database. Transactional budgets and run leases.",
      next: "Restore verified state after refresh or explicit recovery.",
      icon: Database,
    },
    artwork
      ? {
          id: "tools",
          title: "Inspection tools",
          tag: "Measured evidence",
          sub: "Pillow · specs · page previews",
          input: "Bounded decoded pages and requested print dimensions.",
          output:
            "Dimensions, transparency, effective DPI and preview evidence.",
          control:
            "Code-owned measurements remain separate from visual model suggestions.",
          next: "The model inspects every page before submitting its report.",
          icon: ScanLine,
        }
      : {
          id: "mcp",
          title: "MCP catalogue",
          tag: "Read-only integration",
          sub: "get_order · get_policies",
          input: "An immutable, run-scoped order and policy snapshot.",
          output: "Versioned evidence returned through real MCP calls.",
          control: "Read-only tools; no database or payment credentials.",
          next: "Return evidence to the agent. Escalate conflicts instead of inventing a policy.",
          icon: Plug,
        },
    artwork
      ? {
          id: "decoder",
          title: "Isolated decoder",
          tag: "File boundary",
          sub: "PNG · JPEG · PDF",
          input:
            "User-owned synthetic artwork, up to 10 MB and five PDF pages.",
          output: "Validated metadata, bounded previews and a file hash.",
          control:
            "Reject spoofed, malformed, encrypted and unsupported files.",
          next: "Make safe previews available to inspection tools. Never silently edit the original.",
          icon: Image,
        }
      : {
          id: "browser",
          title: "Playwright",
          tag: "Browser fallback",
          sub: "Owned mock carrier page",
          input: "An authorized shipment-fallback request.",
          output: "Shipment status extracted from the local fixture.",
          control:
            "Only the exact application-owned GET URL; no real carrier accounts.",
          next: "Validate extracted evidence and continue the investigation.",
          icon: Globe,
        },
  ];
}
export function SystemMap({
  app,
  run,
}: {
  app: AppKind;
  run?: ConsoleRun | null;
}) {
  const model =
      run?.model ||
      (app === "artwork" ? "claude-haiku-4-5-20251001" : "gpt-5.6-luna"),
    nodes = nodesFor(app, model);
  const [selected, setSelected] = useState("llm"),
    [paths, setPaths] = useState<{ d: string; active: boolean }[]>([]);
  const grid = useRef<HTMLDivElement>(null),
    marker = useId().replaceAll(":", "");
  const connections =
    app === "artwork"
      ? [
          ["reviewer", "api"],
          ["api", "agent"],
          ["agent", "llm"],
          ["api", "db"],
          ["agent", "tools"],
          ["api", "decoder"],
        ]
      : [
          ["reviewer", "api"],
          ["api", "agent"],
          ["agent", "llm"],
          ["api", "db"],
          ["agent", "mcp"],
          ["agent", "browser"],
        ];
  useEffect(() => {
    const el = grid.current;
    if (!el) return;
    const update = () => {
      const b = el.getBoundingClientRect();
      setPaths(
        connections.map(([from, to]) => {
          const a = el
              .querySelector<HTMLElement>('[data-component="' + from + '"]')!
              .getBoundingClientRect(),
            z = el
              .querySelector<HTMLElement>('[data-component="' + to + '"]')!
              .getBoundingClientRect();
          let x1 = a.left + a.width / 2 - b.left,
            y1 = a.bottom - b.top,
            x2 = z.left + z.width / 2 - b.left,
            y2 = z.top - b.top;
          let d = "";
          if (Math.abs(a.top - z.top) < 5) {
            x1 = a.right - b.left;
            y1 = a.top + a.height / 2 - b.top;
            x2 = z.left - b.left;
            y2 = z.top + z.height / 2 - b.top;
            d = "M " + x1 + " " + y1 + " L " + x2 + " " + y2;
          } else {
            const mid = (y1 + y2) / 2;
            d =
              "M " +
              x1 +
              " " +
              y1 +
              " L " +
              x1 +
              " " +
              mid +
              " L " +
              x2 +
              " " +
              mid +
              " L " +
              x2 +
              " " +
              y2;
          }
          return { d, active: from === selected || to === selected };
        }),
      );
    };
    const observer = new ResizeObserver(update);
    observer.observe(el);
    update();
    return () => observer.disconnect();
  }, [app, selected]);
  const node = nodes.find((n) => n.id === selected)!,
    observed = run?.events.filter((e) => componentFor(e) === selected) || [];
  return (
    <section className="system-view content-view">
      <div className="view-heading">
        <div>
          <div className="eyebrow">Understand the connections</div>
          <h2>The system, not a black box.</h2>
          <p>
            Allowed live-path connections. Select a component to inspect its
            responsibility.
          </p>
        </div>
        <span className="pill">
          <Network size={12} />
          Architecture · not a live animation
        </span>
      </div>
      <div className="map-layout">
        <div className="map-surface">
          <div className="map-grid" ref={grid}>
            <svg className="map-edges" aria-hidden="true">
              <defs>
                <marker
                  id={marker}
                  viewBox="0 0 8 8"
                  refX="7"
                  refY="4"
                  markerWidth="5"
                  markerHeight="5"
                  orient="auto-start-reverse"
                >
                  <path d="M0 0 L8 4 L0 8" fill="context-stroke" />
                </marker>
              </defs>
              {paths.map((p, i) => (
                <path
                  key={i}
                  d={p.d}
                  className={p.active ? "active" : ""}
                  markerStart={"url(#" + marker + ")"}
                  markerEnd={"url(#" + marker + ")"}
                />
              ))}
            </svg>
            {nodes.map((n, i) => (
              <div className={"map-slot slot-" + n.id} key={n.id}>
                <button
                  className={"system-node " + (n.tone || "")}
                  data-component={n.id}
                  aria-pressed={selected === n.id}
                  onClick={() => setSelected(n.id)}
                >
                  <span className="node-tag">
                    <n.icon size={16} />
                    {n.tag}
                  </span>
                  <strong>{n.title}</strong>
                  <small>{n.sub}</small>
                </button>
                {i === 0 && null}
              </div>
            ))}
            <div className="map-principle">
              <LockKeyhole size={18} />
              <strong>
                AI recommends.
                <br />
                Application code authorizes.
              </strong>
              <span>No direct model → payment or printer connection.</span>
            </div>
          </div>
          <div className="map-legend">
            <span>
              <i className="legend-dot" />
              Application / tools
            </span>
            <span>
              <i className="legend-dot ai" />
              LLM generation
            </span>
            <span>
              <i className="legend-dot human" />
              Human decision
            </span>
          </div>
          <div className="offline-lane">
            <Box size={17} />
            <div>
              <strong>Public replay takes a different path</strong>
              <p>
                Browser → static Vercel assets. No API, database or model calls.
              </p>
            </div>
          </div>
        </div>
        <aside className="node-inspector" aria-live="polite">
          <div className="eyebrow">Component inspector</div>
          <h3>{node.title}</h3>
          <span className={"pill " + (node.tone || "")}>{node.tag}</span>
          <dl>
            <dt>Receives</dt>
            <dd>{node.input}</dd>
            <dt>Returns</dt>
            <dd>{node.output}</dd>
            <dt>Enforced boundary</dt>
            <dd>{node.control}</dd>
          </dl>
          <div className="next-box">
            <strong>What can happen next?</strong>
            <p>{node.next}</p>
          </div>
          <p className="inspector-observed">
            {observed.length
              ? observed.length + " matching event(s) in the visible run."
              : "No matching events in the visible run. This is not a claim that the component was unused."}
          </p>
        </aside>
      </div>
    </section>
  );
}

export function RunOverview({
  app,
  run,
  replay,
  onSystem,
}: {
  app: AppKind;
  run: ConsoleRun | null | undefined;
  replay: boolean;
  onSystem: () => void;
}) {
  const events = run?.events || [],
    state = run?.state || "queued",
    next = nextAction(state, replay);
  const report = events.some((e) => ["proposal", "report"].includes(e.kind)),
    approval = events.some((e) => e.kind === "approval"),
    receipt = events.some(
      (e) => e.kind === "receipt" || e.title === "Proof approved",
    );
  const stages = [
    {
      name: app === "artwork" ? "Artwork input" : "Customer issue",
      sub: "Synthetic input",
      icon: app === "artwork" ? Image : Box,
      done: events.length > 0,
    },
    {
      name: "Application checks",
      sub: "Identity + constraints",
      icon: ShieldCheck,
      done: events.length > 0,
    },
    {
      name: "LLM + tools",
      sub: events.some((e) => e.call)
        ? "Recorded model calls"
        : "Bounded investigation",
      icon: Sparkles,
      done: events.some(
        (e) => e.kind === "tool" || e.call?.phase === "completed",
      ),
    },
    {
      name: app === "artwork" ? "Proof report" : "Resolution",
      sub: report ? "Evidence-backed proposal" : "Answer / clarification",
      icon: FileCheck2,
      done: report || state === "completed",
    },
    {
      name: "Human review",
      sub:
        state === "awaiting_approval"
          ? "Waiting for approval"
          : approval
            ? "Decision recorded"
            : state === "completed"
              ? "Not required / no decision"
              : "Conditional step",
      icon: UserCheck,
      done: approval,
    },
    {
      name: "Outcome",
      sub: receipt
        ? "Simulated receipt"
        : state === "completed"
          ? "Information / escalation"
          : "No side effect yet",
      icon: CheckCircle2,
      done: state === "completed",
    },
  ];
  return (
    <section className="run-overview">
      <div className="overview-heading">
        <div>
          <span className={"state-dot " + state} />
          <strong>{next.title}</strong>
        </div>
        <button className="text-button" onClick={onSystem}>
          Inspect integrations <ArrowUpRight size={14} />
        </button>
      </div>
      <div className="run-flow" aria-label="Workflow stages">
        {stages.map((s, i) => (
          <div
            key={s.name}
            className={
              "flow-stage " +
              (s.done ? "observed" : "") +
              (i === 4 && state === "awaiting_approval" ? " waiting" : "")
            }
          >
            <span className="flow-icon">
              <s.icon size={17} />
            </span>
            <span>
              <strong>{s.name}</strong>
              <small>{s.sub}</small>
            </span>
            {i < stages.length - 1 && (
              <ArrowRight className="flow-arrow" size={14} />
            )}
          </div>
        ))}
      </div>
      <div className="next-action">
        <span>Next permitted action</span>
        <p>{next.text}</p>
      </div>
    </section>
  );
}

export function Playback({
  id,
  step,
  setStep,
  total,
}: {
  id: string;
  step: number;
  setStep: Dispatch<SetStateAction<number>>;
  total: number;
}) {
  const [playing, setPlaying] = useState(false),
    position = Math.min(step, total);
  useEffect(() => setPlaying(false), [id]);
  useEffect(() => {
    if (!playing) return;
    const timer = window.setInterval(
      () => setStep((previous) => Math.min(previous + 1, total)),
      900,
    );
    return () => clearInterval(timer);
  }, [playing, total, setStep]);
  useEffect(() => {
    if (position >= total) setPlaying(false);
  }, [position, total]);
  function seek(value: number) {
    setPlaying(false);
    setStep(value);
  }
  return (
    <div className="playback" aria-label="Recorded playback controls">
      <div className="playback-buttons">
        <button
          aria-label={playing ? "Pause recording" : "Play recording"}
          onClick={() => {
            if (playing) setPlaying(false);
            else {
              if (position >= total) setStep(0);
              setPlaying(true);
            }
          }}
        >
          {playing ? <Pause size={16} /> : <Play size={16} />}
        </button>
        <button aria-label="Rewind recording" onClick={() => seek(0)}>
          <SkipBack size={14} />
        </button>
        <button
          aria-label="Previous event"
          disabled={position === 0}
          onClick={() => seek(position - 1)}
        >
          <ChevronLeft size={16} />
        </button>
        <button
          aria-label="Next event"
          disabled={position >= total}
          onClick={() => seek(position + 1)}
        >
          <ChevronRight size={16} />
        </button>
        <button aria-label="Show final result" onClick={() => seek(total)}>
          <SkipForward size={14} />
        </button>
      </div>
      <label className="sr-only" htmlFor={"playback-" + id}>
        Recorded timeline position
      </label>
      <input
        id={"playback-" + id}
        type="range"
        min="0"
        max={total}
        value={position}
        onChange={(e) => seek(Number(e.target.value))}
      />
      <span className="mono">
        {position} / {total} events
      </span>
      <small>Event-paced replay</small>
    </div>
  );
}

export function TracePanel({
  run,
  events,
  atEnd,
  provenance,
}: {
  run: ConsoleRun | null | undefined;
  events: TraceEvent[];
  atEnd: boolean;
  provenance?: Provenance | null;
}) {
  const completed = events.filter((e) => e.call?.phase === "completed"),
    hasSpans = run?.events.some((e) => e.call);
  const knownTotals = atEnd || !provenance;
  return (
    <aside className="panel trace">
      <div className="panelhead row">
        <h2>Execution trail</h2>
        <Activity size={16} />
      </div>
      <div className="trace-intro">
        Recorded events and concise decisions—not hidden model reasoning.
      </div>
      <ol className="timeline">
        {events.map((e) => (
          <li
            key={e.seq}
            className={
              e.call
                ? "model-event"
                : e.kind === "approval"
                  ? "human-event"
                  : ""
            }
          >
            <details>
              <summary>
                <small>
                  {String(e.seq).padStart(2, "0")} /{" "}
                  {e.call ? "LLM CALL" : e.kind}
                </small>
                <strong>{e.title}</strong>
                {e.call && (
                  <span className="event-model">
                    {e.call.model} · {e.call.id}
                  </span>
                )}
              </summary>
              <div className="event-detail">
                <p>{e.detail}</p>
                <time dateTime={e.at}>
                  {new Date(e.at).toLocaleTimeString()}
                </time>
                {e.call && (
                  <dl className="call-stats">
                    <div>
                      <dt>Status</dt>
                      <dd>
                        {e.call.phase === "started"
                          ? "Request started"
                          : "Response received"}
                      </dd>
                    </div>
                    <div>
                      <dt>Observed duration</dt>
                      <dd>
                        {e.call.durationMs == null
                          ? "Not recorded"
                          : (e.call.durationMs / 1000).toFixed(2) + " s"}
                      </dd>
                    </div>
                    <div>
                      <dt>Input / output tokens</dt>
                      <dd>
                        {e.call.inputTokens == null
                          ? "Not recorded"
                          : e.call.inputTokens + " / " + e.call.outputTokens}
                      </dd>
                    </div>
                    <div>
                      <dt>Estimated model cost</dt>
                      <dd>
                        {e.call.costMicros == null
                          ? "Not yet available"
                          : money(e.call.costMicros)}
                      </dd>
                    </div>
                  </dl>
                )}
              </div>
            </details>
          </li>
        ))}
      </ol>
      {!events.length && (
        <div className="empty">
          Play the recording or start an invited run to reveal events.
        </div>
      )}
      {run && (
        <div className="trace-totals">
          <div className="metadata">
            <div>
              <span>{knownTotals ? "Model turns" : "Responses revealed"}</span>
              <strong>
                {knownTotals
                  ? run.turns
                  : hasSpans
                    ? completed.length
                    : "Not recorded"}
              </strong>
            </div>
            <div>
              <span>Estimated model cost</span>
              <strong>
                {knownTotals
                  ? money(run.usedMicros)
                  : hasSpans
                    ? money(
                        completed.reduce(
                          (sum, e) => sum + (e.call?.costMicros || 0),
                          0,
                        ),
                      )
                    : "At recording end"}
              </strong>
            </div>
          </div>
          <p className="mono">
            {run.model} / {run.promptVersion}
          </p>
          {!hasSpans && (
            <p className="telemetry-note">
              Historical recording: per-call timings were not captured. Run
              totals are genuine; individual call timings are not inferred.
            </p>
          )}
        </div>
      )}
      {provenance && (
        <div className="footnote">
          <strong>
            {provenance.providerVerified
              ? "Real provider execution"
              : "Unverified recording"}
          </strong>
          <br />
          Recorded {new Date(provenance.recordedAt).toLocaleDateString()}
          <br />
          Source <span className="mono">{provenance.commit.slice(0, 12)}</span>
          <br />
          Playback cannot execute an action.
        </div>
      )}
    </aside>
  );
}

export function ReviewerBrief({
  app,
  onViewRun,
}: {
  app: AppKind;
  onViewRun: () => void;
}) {
  const artwork = app === "artwork";
  return (
    <section className="content-view reviewer-view">
      <div className="view-heading">
        <div>
          <div className="eyebrow">Built to be inspected</div>
          <h2>
            {artwork
              ? "A visual inspection agent with explicit limits."
              : "A support agent with an explicit execution boundary."}
          </h2>
          <p>
            {artwork
              ? "Measured facts and AI observations stay separate, all the way to human approval."
              : "The model investigates. Application code controls every business action."}
          </p>
        </div>
        <button className="primary" onClick={onViewRun}>
          <Play size={15} />
          Explore a recorded run
        </button>
      </div>
      <div className="brief-grid">
        <section className="brief-section">
          <span className="section-number">01 / THE PROBLEM</span>
          <h3>
            {artwork
              ? "Turn artwork into a reviewable proof"
              : "Resolve customer issues without uncontrolled actions"}
          </h3>
          <p>
            {artwork
              ? "Upload a design, specify print dimensions, inspect measured and visual findings, and approve an exact report version. No artwork is silently modified or sent to a printer."
              : "Investigate delays, damage, address changes and conflicting policies using synthetic customer data. Propose a controlled resolution and preserve the evidence behind it."}
          </p>
          <h4>What to try first</h4>
          <ul>
            {artwork ? (
              <>
                <li>
                  Low-resolution artwork: compare measured DPI with visual
                  suggestions.
                </li>
                <li>
                  Embedded instructions: inspect how artwork text stays
                  untrusted.
                </li>
                <li>
                  Two-page PDF: follow page inspection and proof generation.
                </li>
              </>
            ) : (
              <>
                <li>
                  Damaged delivery: follow proposal → approval → simulated
                  receipt.
                </li>
                <li>
                  Carrier fallback: inspect the real restricted-browser
                  integration.
                </li>
                <li>
                  Policy conflict: see escalation without an unauthorized
                  refund.
                </li>
              </>
            )}
          </ul>
        </section>
        <section className="brief-section">
          <span className="section-number">02 / ENGINEERING DECISIONS</span>
          <h3>What the system demonstrates</h3>
          <ul>
            {artwork ? (
              <>
                <li>FastAPI, Python, React/TypeScript and PostgreSQL.</li>
                <li>
                  Claude Haiku Messages loop with typed tool schemas and bounded
                  preview input.
                </li>
                <li>
                  Isolated PNG/JPEG/PDF processing; code-owned measurements.
                </li>
                <li>
                  Artwork-hash and report-version approval, checkpointing and
                  idempotency.
                </li>
              </>
            ) : (
              <>
                <li>Go/GraphQL, Python, React/TypeScript and PostgreSQL.</li>
                <li>
                  GPT-5.6 Luna via OpenAI Agents SDK with typed tools and native
                  approval interruptions.
                </li>
                <li>
                  Read-only MCP catalogue and Playwright fixture navigation.
                </li>
                <li>
                  Exact-action approval, integer-money policy checks and
                  idempotent execution.
                </li>
              </>
            )}
            <li>
              Atomic usage reservations, invitation isolation and explicit
              recovery.
            </li>
          </ul>
        </section>
        <section className="brief-section">
          <span className="section-number">03 / VERIFICATION EVIDENCE</span>
          <div className="verified-count">
            <CheckCircle2 size={23} />
            <strong>{artwork ? "30 / 30" : "39 / 40"}</strong>
            <span>defined live evaluation cases passed</span>
          </div>
          <p>
            Verified on 13 September 2026 with Luna for Commerce and Claude for
            Artwork. One Commerce investigation stopped safely at application
            validation; all 40 action-safety audits passed. The failure is
            included in the reports, not retested into a perfect score. These
            synthetic results are not a production success-rate claim.
          </p>
          <p>
            {artwork
              ? "Six original designs under five size/decision conditions. Graders check safety, evidence and report contracts—not perfect visual judgment."
              : "Defined support scenarios with evidence, forbidden-action, exact-approval and simulated-receipt checks."}
          </p>
          <a className="document-link" href="/verification.json" download>
            Download actual evaluation results <ArrowUpRight size={14} />
          </a>
          <br />
          <a className="document-link" href="/evaluation-history.json" download>
            Previous attempts and failures <ArrowUpRight size={14} />
          </a>
        </section>
        <section className="brief-section">
          <span className="section-number">04 / LIMITS & OWNERSHIP</span>
          <h3>Honest boundaries</h3>
          <ul>
            <li>
              Independent portfolio by Shashank; unaffiliated with Sticker Mule.
            </li>
            <li>
              {artwork
                ? "Demo print specifications are not commercial print certification."
                : "Demonstration policies, invented customers and mock carrier data."}
            </li>
            <li>No real payments, messages or print orders.</li>
            <li>
              Low-volume PostgreSQL aggregate; not a high-throughput production
              architecture.
            </li>
            <li>
              Public recordings are static. Live access is invited and metered.
            </li>
          </ul>
          <a className="document-link" href="/reviewer-guide.md" download>
            Architecture & reviewer guide <ArrowUpRight size={14} />
          </a>
          <p className="quiet">
            Source repository is private pending the full release review. No
            public source access is implied.
          </p>
        </section>
      </div>
      <div className="sharing-note">
        <ShieldCheck size={18} />
        <p>
          Share the public demo URL—not an invitation token. Reviewer
          invitations should be sent privately and can be revoked.
        </p>
      </div>
    </section>
  );
}

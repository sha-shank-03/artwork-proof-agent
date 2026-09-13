import { useEffect, useState } from "react";
import {
  ArrowUpRight,
  Check,
  ChevronRight,
  Code2,
  Download,
  Eye,
  FileCheck2,
  ImagePlus,
  Layers3,
  LockKeyhole,
  Play,
  RefreshCw,
  ScanLine,
  ShieldCheck,
  Sparkles,
  X,
} from "lucide-react";
import {
  getRun,
  getRuns,
  loadReplays,
  request,
  runSchema,
  upload,
  type Replay,
  type Run,
} from "./api";
const liveAvailable = import.meta.env.DEV || import.meta.env.VITE_LIVE_AVAILABLE === "true";
export default function App() {
  const [mode, setMode] = useState<"replay" | "live">("replay"),
    [replays, setReplays] = useState<Replay[]>([]),
    [selected, setSelected] = useState(0),
    [run, setRun] = useState<Run | null>(null),
    [error, setError] = useState(""),
    [busy, setBusy] = useState(false),
    [token, setToken] = useState(""),
    [authenticated, setAuthenticated] = useState(false),
    [file, setFile] = useState<File | null>(null),
    [width, setWidth] = useState("3"),
    [height, setHeight] = useState("3"),
    [text, setText] = useState(""),
    [step, setStep] = useState(999),
    [page, setPage] = useState(0);
  useEffect(() => {
    loadReplays()
      .then(setReplays)
      .catch(() =>
        setError("Verified recordings could not be loaded. Please refresh."),
      );
  }, []);
  const current = mode === "replay" ? replays[selected]?.run : run;
  const replay = mode === "replay" ? replays[selected] : null;
  useEffect(() => {
    if (mode !== "live" || !liveAvailable) return;
    let active = true;
    getRuns().then(history => {
      if (!active) return;
      setAuthenticated(true);
      setRun(history.sort((a,b)=>b.events[0]?.at.localeCompare(a.events[0]?.at||'')||0)[0]||null);
    }).catch(() => { if (active) setAuthenticated(false); });
    return () => { active = false; };
  }, [mode]);
  useEffect(() => {
    if (mode !== "live" || run?.state !== "running") return;
    let active = true, pending = false;
    const timer = setInterval(() => {
      if (document.visibilityState === "visible" && !pending) {
        pending = true;
        getRun(run.id)
          .then(value => { if (active) setRun(value); })
          .catch((e) => { if (active) setError(e.message); })
          .finally(() => { pending = false; });
      }
    }, 1500);
    return () => { active = false; clearInterval(timer); };
  }, [mode, run?.id, run?.state]);
  async function action(fn: () => Promise<void>) {
    setBusy(true);
    setError("");
    try {
      await fn();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Request failed");
    } finally {
      setBusy(false);
    }
  }
  async function transition(name: string, data: unknown = {}) {
    if (!current) return;
    setRun(runSchema.parse(await request(`/runs/${current.id}/${name}`, data)));
  }
  async function start() {
    if (!file) throw new Error("Choose a PNG, JPEG or PDF first");
    const uploaded = await upload(file);
    setRun(
      runSchema.parse(
        await request("/runs", {
          uploadId: uploaded.id,
          width: width ? Number(width) : null,
          height: height ? Number(height) : null,
        }),
      ),
    );
    setPage(0);
  }
  function downloadJson() {
    if (!current?.report) return;
    const url = URL.createObjectURL(
      new Blob([JSON.stringify(current.report, null, 2)], {
        type: "application/json",
      }),
    );
    const a = document.createElement("a");
    a.href = url;
    a.download = "artwork-report.json";
    a.click();
    URL.revokeObjectURL(url);
  }
  return (
    <div className="shell">
      <header>
        <div className="brand">
          <span className="brandmark">
            <ScanLine size={20} />
          </span>
          Artwork<span className="quiet">/ proof agent</span>
        </div>
        <nav className="headerlinks">
          <span className="quiet">A portfolio by Shashank</span>
          <a
            className="source"
            href="https://github.com/sha-shank-03/artwork-proof-agent"
            target="_blank"
            rel="noreferrer"
          >
            Source <ArrowUpRight size={12} />
          </a>
        </nav>
      </header>
      <section className="hero">
        <div>
          <div className="eyebrow">Multimodal agent engineering · Claude</div>
          <h1>
            Inspect the details.
            <br />
            Keep the final say.
          </h1>
          <p>
            From artwork to a reviewable proof. Deterministic file checks meet
            AI-assisted visual inspection—with evidence, clear limitations, and
            human approval.
          </p>
        </div>
        <div className="hero-meta">
          <span className="pill">
            <ShieldCheck size={12} />
            Measured ≠ model-suggested
          </span>
          <p className="quiet" style={{ marginTop: 10 }}>
            Python · Claude · React · PostgreSQL
          </p>
        </div>
      </section>
      <div className="modebar">
        <div className="tabs" role="tablist" aria-label="Execution mode">
          <button
            role="tab"
            aria-selected={mode === "replay"}
            onClick={() => {
              setMode("replay");
              setPage(0);
              setError("");
            }}
          >
            <Play size={13} />
            Recorded proofs
          </button>
          <button
            role="tab"
            aria-selected={mode === "live"}
            onClick={() => {
              setMode("live");
              setPage(0);
            }}
          >
            <LockKeyhole size={13} />
            Invited live access
          </button>
        </div>
        <span className="quiet">
          {mode === "replay"
            ? "Recorded real runs · no model calls while browsing"
            : "Demonstration artwork only · PNG / JPEG / PDF"}
        </span>
      </div>
      {error && (
        <div className="banner" role="alert">
          {error}
        </div>
      )}
      {mode === "live" && !liveAvailable ? <section className="panel login"><LockKeyhole size={25}/><h2>Live hosting is not enabled yet.</h2><p>Claude-backed verification is pending API access and release checks. This page does not contain fabricated provider recordings.</p><button onClick={()=>setMode('replay')}>Return to proof catalogue</button></section> : mode === "live" && !authenticated ? (
        <form
          className="panel login"
          onSubmit={(e) => {
            e.preventDefault();
            void action(async () => {
              await request("/session", { token });
              setToken("");
              setAuthenticated(true);
            });
          }}
        >
          <LockKeyhole size={25} />
          <h2 style={{ marginTop: 15 }}>A closer look, by invitation.</h2>
          <p>
            Use your reviewer invitation to try real Claude-powered analysis.
            Upload only synthetic or non-confidential artwork you own. Files
            expire after seven days; no files are sent to a printer.
          </p>
          <label htmlFor="invite">Invitation token</label>
          <input
            id="invite"
            type="password"
            autoComplete="off"
            value={token}
            onChange={(e) => setToken(e.target.value)}
            required
          />
          <button className="primary" disabled={busy} style={{ marginTop: 17 }}>
            Open proof workspace <ChevronRight size={14} />
          </button>
        </form>
      ) : (
        <div className="workspace">
          <aside className="panel">
            <div className="panelhead">
              <h2>
                {mode === "replay"
                  ? "The proof collection"
                  : "Prepare your artwork"}
              </h2>
            </div>
            {mode === "replay" ? (
              <>
                {replays.map((r, i) => (
                  <button
                    key={r.run.id}
                    className={"scenario " + (selected === i ? "active" : "")}
                    onClick={() => {
                      setSelected(i);
                      setPage(0);
                      setStep(999);
                    }}
                  >
                    <span className="number">
                      PROOF {String(i + 1).padStart(2, "0")}
                    </span>
                    {r.label}
                    <small>
                      {r.run.previews.length} page(s) · {r.run.width} ×{" "}
                      {r.run.height} in
                    </small>
                  </button>
                ))}
                {!replays.length && (
                  <div className="empty">
                    Verified Claude recordings are being prepared. There are no
                    fabricated model results here.
                  </div>
                )}
              </>
            ) : (
              <form
                className="panelbody"
                onSubmit={(e) => {
                  e.preventDefault();
                  void action(start);
                }}
              >
                <div className="uploadbox">
                  <ImagePlus size={24} />
                  <label htmlFor="file">Choose artwork</label>
                  <input
                    id="file"
                    type="file"
                    accept="image/png,image/jpeg,application/pdf"
                    onChange={(e) => setFile(e.target.files?.[0] || null)}
                    required={!file}
                  />
                  <label htmlFor="sample">Or use original demo artwork</label>
                  <select id="sample" defaultValue="" onChange={e=>{
                    const name=e.target.value;if(!name)return;
                    void action(async()=>{
                      const extension=name==='two-page-proof'?'pdf':'png';
                      const response=await fetch(`/fixtures/${name}.${extension}`);
                      if(!response.ok)throw new Error('Sample could not be loaded');
                      setFile(new File([await response.blob()],`${name}.${extension}`,{type:extension==='pdf'?'application/pdf':'image/png'}));
                    });
                  }}>
                    <option value="">Select a sample</option>
                    <option value="clean-mark">Clean mark</option>
                    <option value="low-resolution">Low resolution</option>
                    <option value="wide-layout">Wide layout</option>
                    <option value="transparent-mark">Transparent mark</option>
                    <option value="embedded-instructions">Untrusted embedded text</option>
                    <option value="two-page-proof">Two-page PDF</option>
                  </select>
                  {file&&<p>Selected: {file.name}</p>}
                  <p>
                    10 MB maximum. PDFs: up to 5 pages, no encryption. PNG/JPEG:
                    bounded pixel dimensions.
                  </p>
                </div>
                <div className="dimensions">
                  <div>
                    <label htmlFor="width">Width (in)</label>
                    <input
                      id="width"
                      type="number"
                      step="0.1"
                      min="0.2"
                      max="40"
                      value={width}
                      onChange={(e) => setWidth(e.target.value)}
                    />
                  </div>
                  <div>
                    <label htmlFor="height">Height (in)</label>
                    <input
                      id="height"
                      type="number"
                      step="0.1"
                      min="0.2"
                      max="40"
                      value={height}
                      onChange={(e) => setHeight(e.target.value)}
                    />
                  </div>
                </div>
                <button
                  className="primary"
                  style={{ marginTop: 18, width: "100%" }}
                  disabled={busy || run?.state === "running"}
                >
                  <Sparkles size={14} />
                  Analyze artwork
                </button>
              </form>
            )}
            <div className="footnote">
              Demo print specifications only. AI observations are not production
              print certification.
            </div>
          </aside>
          <main className="panel">
            <div className="panelhead row">
              <h2>Proof workspace</h2>
              <span className="pill">
                {current?.state.replaceAll("_", " ") || "Ready to inspect"}
              </span>
            </div>
            <div className="panelbody">
              {current ? (
                <>
                  {mode === "replay" && (
                    <div className="replay-controls">
                      <Play size={14} />
                      <input
                        aria-label="Recorded timeline position"
                        type="range"
                        min="0"
                        max={current.events.length}
                        value={Math.min(step, current.events.length)}
                        onChange={(e) => setStep(Number(e.target.value))}
                      />
                      <span className="mono">
                        {Math.min(step, current.events.length)}/
                        {current.events.length}
                      </span>
                    </div>
                  )}
                  <div className="row">
                    <h2>{current.name}</h2>
                    <span className="quiet">v{current.version}</span>
                  </div>
                  <div className="artpreview">
                    <img
                      src={"data:image/png;base64," + current.previews[page]}
                      alt={`Artwork preview, page ${page + 1}`}
                    />
                  </div>
                  {current.previews.length > 1 && (
                    <div className="actions">
                      {current.previews.map((_, i) => (
                        <button
                          key={i}
                          aria-pressed={page === i}
                          onClick={() => setPage(i)}
                        >
                          Page {i + 1}
                        </button>
                      ))}
                    </div>
                  )}
                  <div className="metadata">
                    <div>
                      <span>Print dimensions</span>
                      <strong>
                        {current.width || "?"} × {current.height || "?"} in
                      </strong>
                    </div>
                    <div>
                      <span>Analysis model</span>
                      <strong>Claude</strong>
                    </div>
                    <div>
                      <span>File identity</span>
                      <strong className="mono">
                        {current.artworkHash.slice(0, 12)}…
                      </strong>
                    </div>
                  </div>
                  {current.summary && (
                    <div className="result">
                      <h3>
                        <Eye size={14} /> Inspection summary
                      </h3>
                      <p>{current.summary}</p>
                    </div>
                  )}
                  {current.report && (
                    <>
                      <h3>Findings with a clear source</h3>
                      {current.report.findings.map((f, i) => (
                        <div className="finding" key={i}>
                          <span
                            className={
                              "pill " +
                              (f.severity === "warning"
                                ? "warning"
                                : f.severity === "error"
                                  ? "error"
                                  : "")
                            }
                          >
                            {f.category}
                          </span>
                          <h3>{f.title}</h3>
                          <p>{f.detail}</p>
                          <div className="mono">{f.evidence_id}</div>
                        </div>
                      ))}
                      <div className="approval">
                        <h3>
                          <FileCheck2 size={14} /> Version-bound proof approval
                        </h3>
                        <p>
                          Approval applies only to this artwork hash and report
                          version. It does not certify print quality or send an
                          order to a printer.
                        </p>
                        <div className="mono">
                          Report: {current.reportDigest.slice(0, 28)}…
                        </div>
                        {mode === "live" &&
                        current.state === "awaiting_approval" ? (
                          <div className="actions">
                            <button
                              className="primary"
                              disabled={busy}
                              onClick={() =>
                                void action(() =>
                                  transition("approve", {
                                    digest: current.reportDigest,
                                  }),
                                )
                              }
                            >
                              <Check size={14} />
                              Approve proof
                            </button>
                            <button
                              disabled={busy}
                              onClick={() =>
                                void action(() =>
                                  transition("reject", {
                                    digest: current.reportDigest,
                                  }),
                                )
                              }
                            >
                              <X size={14} />
                              Reject
                            </button>
                          </div>
                        ) : (
                          <p className="quiet">
                            {current.receipt
                              ? "Human approval recorded. Nothing sent to a printer."
                              : mode === "replay"
                                ? "Recorded review state; no action can execute here."
                                : "Review resolved."}
                          </p>
                        )}
                      </div>
                      <div className="actions">
                        <button onClick={downloadJson}>
                          <Download size={13} />
                          JSON report
                        </button>
                        {(mode === "live" || replay?.proofFile) && (
                          <a
                            className="source"
                            href={
                              mode === "live"
                                ? `/api/runs/${current.id}/proof.pdf`
                                : replay?.proofFile
                            }
                            download
                          >
                            Download proof PDF
                          </a>
                        )}
                      </div>
                    </>
                  )}
                  {current.state === "running" && (
                    <div className="loading" role="status">
                      Inspecting artwork and gathering evidence…
                      <progress />
                    </div>
                  )}
                  {mode === "live" && current.state === "awaiting_input" && (
                    <form
                      onSubmit={(e) => {
                        e.preventDefault();
                        void action(() =>
                          transition("clarify", {
                            text,
                            width: Number(width),
                            height: Number(height),
                          }),
                        );
                      }}
                    >
                      <label htmlFor="clarify">Reviewer clarification</label>
                      <textarea
                        id="clarify"
                        value={text}
                        onChange={(e) => setText(e.target.value)}
                        placeholder="Answer the question above; set dimensions in the left panel."
                      />
                      <button className="primary" disabled={busy}>
                        Continue analysis
                      </button>
                    </form>
                  )}
                  {current.error && (
                    <p role="alert" className="message">
                      {current.error}
                    </p>
                  )}
                  {mode === "live" && (
                    <div className="actions">
                      {current.state === "failed" && (
                        <button
                          disabled={busy}
                          onClick={() =>
                            void action(() => transition("resume"))
                          }
                        >
                          <RefreshCw size={13} />
                          Retry explicitly
                        </button>
                      )}
                      {!["completed", "cancelled"].includes(current.state) && (
                        <button
                          className="danger"
                          disabled={busy}
                          onClick={() =>
                            void action(() => transition("cancel"))
                          }
                        >
                          Cancel analysis
                        </button>
                      )}
                    </div>
                  )}
                </>
              ) : (
                <div className="empty">
                  <ScanLine size={32} />
                  <p>
                    {mode === "live"
                      ? "Upload artwork to start a measured, reviewable inspection."
                      : "Select a verified proof to explore the findings and evidence."}
                  </p>
                </div>
              )}
            </div>
          </main>
          <aside className="panel trace">
            <div className="panelhead row">
              <h2>Inspection trail</h2>
              <Code2 size={15} />
            </div>
            <ol className="timeline">
              {current?.events.slice(0, step).map((e) => (
                <li key={e.seq}>
                  <small>
                    {String(e.seq).padStart(2, "0")} / {e.kind}
                  </small>
                  <strong>{e.title}</strong>
                  <p>{e.detail}</p>
                </li>
              ))}
            </ol>
            {!current && (
              <div className="empty">
                File checks, visual tools and decisions appear here.
              </div>
            )}
            {current && (
              <div
                className="panelbody"
                style={{ borderTop: "1px solid #e6e9df" }}
              >
                <div className="metadata">
                  <div>
                    <span>Model turns</span>
                    <strong>{current.turns}</strong>
                  </div>
                  <div>
                    <span>Model cost</span>
                    <strong>${(current.usedMicros / 1e6).toFixed(4)}</strong>
                  </div>
                </div>
                <p className="mono">
                  {current.model} / {current.promptVersion}
                </p>
              </div>
            )}
            {replay && (
              <div className="footnote">
                Recorded {new Date(replay.recordedAt).toLocaleDateString()}
                <br />
                Commit {replay.commit.slice(0, 12)}
                <br />
                {replay.providerVerified
                  ? "Real provider execution"
                  : "Not provider-verified"}
              </div>
            )}
          </aside>
        </div>
      )}
      <footer>
        <span>
          Independent portfolio demonstration. Not affiliated with Sticker Mule.
        </span>
        <span>Measured checks → visual inspection → human proof approval</span>
      </footer>
    </div>
  );
}

import { z } from "zod";
import createClient from "openapi-fetch";
import type { paths } from "./generated";
const client = createClient<paths>({
  baseUrl: "/api",
  credentials: "same-origin",
});
const finding = z.object({
  category: z.enum(["measured", "model-suggested", "requires-human-review"]),
  severity: z.enum(["info", "warning", "error"]),
  title: z.string(),
  detail: z.string(),
  evidence_id: z.string(),
});
export const runSchema = z.object({
  id: z.string(),
  name: z.string(),
  state: z.string(),
  summary: z.string(),
  model: z.string(),
  promptVersion: z.string(),
  artworkHash: z.string(),
  version: z.number(),
  width: z.number().nullable(),
  height: z.number().nullable(),
  previews: z.array(z.string()),
  events: z.array(
    z.object({
      seq: z.number(),
      kind: z.string(),
      title: z.string(),
      detail: z.string(),
      at: z.string(),
    }),
  ),
  report: z
    .object({
      summary: z.string(),
      findings: z.array(finding),
      specVersion: z.string(),
      artworkHash: z.string(),
      version: z.number(),
    })
    .nullable(),
  reportDigest: z.string(),
  receipt: z
    .object({
      id: z.string(),
      reportDigest: z.string(),
      simulated: z.boolean(),
    })
    .nullable(),
  error: z.string(),
  turns: z.number(),
  usedMicros: z.number(),
});
export type Run = z.infer<typeof runSchema>;
export type Replay = {
  label: string;
  run: Run;
  recordedAt: string;
  commit: string;
  providerVerified: boolean;
  proofFile?: string;
};
export async function request(path: string, body?: unknown) {
  const response = await fetch("/api" + path, {
    method: body === undefined ? "GET" : "POST",
    credentials: "same-origin",
    headers: body === undefined ? {} : { "Content-Type": "application/json" },
    body: body === undefined ? undefined : JSON.stringify(body),
  });
  const data = await response.json();
  if (!response.ok)
    throw new Error(
      typeof data.detail === "string"
        ? data.detail
        : JSON.stringify(data.detail || data.error || "Request failed"),
    );
  return data;
}
export async function upload(file: File) {
  const res = await fetch(
    "/api/uploads?name=" + encodeURIComponent(file.name),
    {
      method: "POST",
      credentials: "same-origin",
      headers: { "Content-Type": file.type || "application/octet-stream" },
      body: file,
    },
  );
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Upload failed");
  return z.object({ id: z.string(), name: z.string() }).parse(data);
}
export async function getRun(id: string) {
  const result = await client.GET("/runs/{ident}", {
    params: { path: { ident: id } },
  });
  if (result.error) throw new Error("Run could not be loaded");
  return runSchema.parse(result.data);
}
export async function getRuns() {
  const result = await client.GET("/runs");
  if (result.error) throw new Error("Invitation required");
  return z.array(runSchema).parse(result.data);
}
export async function loadReplays(): Promise<Replay[]> {
  const index = await (await fetch("/replays/index.json")).json();
  return Promise.all(
    index.runs.map(async (item: { file: string; label: string }) => {
      if (!/^\/replays\/[a-z0-9-]+\.json$/.test(item.file))
        throw new Error("Invalid replay path");
      const data = await (await fetch(item.file)).json();
      return { ...data, label: item.label, run: runSchema.parse(data.run) };
    }),
  );
}

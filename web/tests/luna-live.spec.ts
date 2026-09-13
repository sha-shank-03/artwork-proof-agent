import { test, expect } from "@playwright/test";
import { readFileSync } from "node:fs";

test("hosted Claude inspection requires approval and survives refresh", async ({
  page,
}) => {
  test.skip(
    process.env.HOSTED_MODEL_TEST !== "true",
    "Billed hosted verification must be explicitly enabled",
  );
  test.setTimeout(180000);
  if (!process.env.HOSTED_INVITATION_FILE)
    throw new Error("An exact private invitation file is required");
  const invitation = readFileSync(
    process.env.HOSTED_INVITATION_FILE,
    "utf8",
  ).trim();
  const runtimeErrors: string[] = [];
  page.on("pageerror", (error) => runtimeErrors.push(error.message));
  await page.goto("/#run");
  await page.getByRole("tab", { name: "Invited live access" }).click();
  await page.getByLabel("Invitation token").fill(invitation);
  await page.getByRole("button", { name: "Open proof workspace" }).click();
  await page
    .getByLabel("Or use original demo artwork")
    .selectOption("low-resolution");
  await expect(page.getByText("Selected: low-resolution.png")).toBeVisible();
  await page.getByLabel("Width (in)").fill("3");
  await page.getByLabel("Height (in)").fill("3");
  const start = page.waitForResponse(
    (r) => r.url().endsWith("/api/runs") && r.request().method() === "POST",
  );
  await page.getByRole("button", { name: "Analyze artwork" }).click();
  const created = await (await start).json();
  expect(created.model).toBe("claude-haiku-4-5-20251001");
  expect(created.receipt).toBeNull();
  await expect(page.getByRole("button", { name: "Approve proof" })).toBeVisible(
    { timeout: 150000 },
  );
  await page.reload();
  await page.getByRole("tab", { name: "Invited live access" }).click();
  await expect(
    page.getByRole("button", { name: "Approve proof" }),
  ).toBeVisible();
  const decision = page.waitForResponse(
    (r) => r.url().endsWith("/approve") && r.request().method() === "POST",
  );
  await page.getByRole("button", { name: "Approve proof" }).click();
  const approved = await (await decision).json();
  expect(approved.state).toBe("completed");
  expect(approved.model).toBe("claude-haiku-4-5-20251001");
  expect(approved.inputTokens).toBeGreaterThan(0);
  expect(approved.outputTokens).toBeGreaterThan(0);
  expect(approved.receipt.reportDigest).toBe(approved.reportDigest);
  expect(approved.receipt.simulated).toBe(true);
  expect(approved.usedMicros).toBeLessThanOrEqual(250000);
  const spans = approved.events.filter(
    (e: any) => e.call?.phase === "completed",
  );
  expect(spans.length).toBe(approved.turns);
  expect(
    spans.every(
      (e: any) =>
        e.call.model === "claude-haiku-4-5-20251001" && e.call.durationMs >= 0,
    ),
  ).toBe(true);
  expect(
    spans.reduce((sum: number, e: any) => sum + e.call.costMicros, 0),
  ).toBe(approved.usedMicros);
  const modelEvent = page
    .locator(".model-event")
    .filter({ hasText: "Model response received" })
    .first();
  await modelEvent.locator("summary").click();
  await expect(
    modelEvent.getByText("Observed duration", { exact: true }),
  ).toBeVisible();
  expect(runtimeErrors).toEqual([]);
  await page.screenshot({
    path: `../.local/claude-live-${test.info().project.name}.png`,
    fullPage: true,
  });
});

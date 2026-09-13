import { test, expect } from "@playwright/test";

test("genuine proof playback hides future findings and never calls an API", async ({
  page,
}) => {
  const calls: string[] = [];
  await page.route("**/api/**", (route) => {
    calls.push(route.request().url());
    return route.abort();
  });
  await page.goto("/#run");
  const index = await (await page.request.get("/replays/index.json")).json();
  test.skip(
    index.runs.length === 0,
    "No genuine recordings have been published yet",
  );
  await expect(
    page.getByRole("heading", { name: "Findings with a clear source" }),
  ).toBeVisible();
  await page
    .getByRole("button", { name: "Rewind recording", exact: true })
    .click();
  await expect(page.locator(".timeline li")).toHaveCount(0);
  await expect(
    page.getByRole("heading", { name: "Findings with a clear source" }),
  ).toHaveCount(0);
  await expect(
    page.getByRole("link", { name: "Download proof PDF" }),
  ).toHaveCount(0);
  await page
    .getByRole("button", { name: "Play recording", exact: true })
    .click();
  await expect
    .poll(() => page.locator(".timeline li").count())
    .toBeGreaterThan(0);
  await page
    .getByRole("button", { name: "Pause recording", exact: true })
    .click();
  const paused = await page.locator(".timeline li").count();
  await page.waitForTimeout(1100);
  await expect(page.locator(".timeline li")).toHaveCount(paused);
  await page
    .getByRole("button", { name: "Show final result", exact: true })
    .click();
  await expect(
    page.getByRole("heading", { name: "Findings with a clear source" }),
  ).toBeVisible();
  await expect(
    page.getByRole("button", { name: "Approve proof", exact: true }),
  ).toHaveCount(0);
  const pdf = await page.request.get(
    (await page
      .getByRole("link", { name: "Download proof PDF" })
      .getAttribute("href")) || "",
  );
  expect(pdf.headers()["content-type"]).toContain("application/pdf");
  expect((await pdf.body()).subarray(0, 4).toString()).toBe("%PDF");
  expect(calls).toEqual([]);
  await page.getByRole("button", { name: /PROOF 02 low resolution/ }).click();
  await expect(page.getByLabel("Independent reviewer note")).toBeVisible();
  await page
    .getByRole("button", { name: "Rewind recording", exact: true })
    .click();
  await expect(page.getByLabel("Independent reviewer note")).toHaveCount(0);
});

test("recorded Claude calls expose measured timing and token usage", async ({
  page,
}) => {
  await page.goto("/#run");
  const index = await (await page.request.get("/replays/index.json")).json();
  test.skip(
    index.runs.length === 0,
    "No genuine recordings have been published yet",
  );
  const replay = await (await page.request.get(index.runs[0].file)).json();
  const spans = replay.run.events.filter(
    (e: any) => e.call?.phase === "completed",
  );
  if (!spans.length) {
    await expect(
      page.getByText("Historical recording:", { exact: false }),
    ).toBeVisible();
  } else {
    const event = page
      .locator(".model-event")
      .filter({ hasText: "Model response received" })
      .first();
    await event.locator("summary").click();
    await expect(event).toContainText("claude-haiku-4-5-20251001");
    await expect(event).toContainText(
      (spans[0].call.durationMs / 1000).toFixed(2) + " s",
    );
    await expect(event).toContainText(
      spans[0].call.inputTokens + " / " + spans[0].call.outputTokens,
    );
  }
});

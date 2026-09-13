import { test, expect } from "@playwright/test";
test("shared hash links change views in an already-open console", async ({
  page,
}) => {
  await page.goto("/");
  await page.evaluate(() => {
    window.location.hash = "#run";
  });
  await expect(
    page.getByRole("button", { name: "Run view", exact: true }),
  ).toHaveAttribute("aria-current", "page");
  await page.evaluate(() => {
    window.location.hash = "#brief";
  });
  await expect(
    page.getByRole("button", { name: "Reviewer brief", exact: true }),
  ).toHaveAttribute("aria-current", "page");
});
test(
  "system map and reviewer navigation stay offline",
  { tag: "@console" },
  async ({ page }) => {
    const calls: string[] = [];
    const errors: string[] = [];
    await page.route("**/api/**", (route) => {
      calls.push(route.request().url());
      return route.abort();
    });
    page.on("pageerror", (e) => errors.push(e.message));
    await page.goto("/");
    await expect(
      page.getByRole("button", { name: "System map", exact: true }),
    ).toHaveAttribute("aria-current", "page");
    await expect(page.getByRole("button", { name: /LLM call/ })).toBeVisible();
    await page.getByRole("button", { name: /Persistence PostgreSQL/ }).click();
    await expect(page.locator(".node-inspector h3")).toHaveText("PostgreSQL");
    await expect(page.locator(".map-edges > path")).toHaveCount(6);
    await expect(page.locator(".map-edges > path.active")).toHaveCount(1);
    await page.getByRole("button", { name: "Switch to light theme" }).click();
    await expect(page.locator("html")).toHaveAttribute("data-theme", "light");
    await page.reload();
    await expect(page.locator("html")).toHaveAttribute("data-theme", "light");
    await page
      .getByRole("button", { name: "Reviewer brief", exact: true })
      .click();
    await expect(
      page.getByText("defined live evaluation cases passed", { exact: true }),
    ).toBeVisible();
    const guide = await page.request.get("/reviewer-guide.md");
    expect(guide.status()).toBe(200);
    expect(await guide.text()).toContain("Independent portfolio");
    const verification = await page.request.get("/verification.json");
    expect(verification.status()).toBe(200);
    expect((await verification.json()).results.length).toBeGreaterThan(0);
    await page.getByRole("button", { name: "Explore a recorded run" }).click();
    await expect(
      page.getByRole("button", { name: "Run view", exact: true }),
    ).toHaveAttribute("aria-current", "page");
    expect(calls).toEqual([]);
    expect(errors).toEqual([]);
  },
);
test("mobile and keyboard system inspector fit without overflow", async ({
  page,
}) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.emulateMedia({ reducedMotion: "reduce" });
  await page.goto("/");
  const node = page.getByRole("button", { name: /Human decision Reviewer/ });
  await node.focus();
  await page.keyboard.press("Enter");
  await expect(page.locator(".node-inspector h3")).toHaveText("Reviewer");
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= innerWidth,
    ),
  ).toBe(true);
  await page
    .getByRole("button", { name: "Reviewer brief", exact: true })
    .click();
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= innerWidth,
    ),
  ).toBe(true);
});

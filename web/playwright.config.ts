import { defineConfig, devices } from "@playwright/test";
export default defineConfig({
  testDir: "./tests",
  use: { baseURL: process.env.BASE_URL || "http://localhost:5174" },
  workers: 1,
  webServer: process.env.BASE_URL ? undefined : {
    command: "npm run dev",
    url: "http://127.0.0.1:5174",
    reuseExistingServer: !process.env.CI,
  },
  projects: [
    { name: "chromium", use: { ...devices["Desktop Chrome"] } },
    { name: "firefox", use: { ...devices["Desktop Firefox"] } },
    { name: "webkit", use: { ...devices["Desktop Safari"] } },
  ],
});

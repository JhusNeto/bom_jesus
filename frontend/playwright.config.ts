import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: 1,
  reporter: 'html',
  use: {
    baseURL: 'http://localhost:5173',
    trace: 'on-first-retry',
    actionTimeout: 15000,
    navigationTimeout: 15000,
  },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
  ],
  webServer: process.env.SKIP_WEBSERVER
    ? undefined
    : process.env.CI
      ? { command: 'npm run dev', url: 'http://localhost:5173', reuseExistingServer: false }
      : { command: 'npm run dev', url: 'http://localhost:5173', reuseExistingServer: true, timeout: 60000 },
});

// @ts-check
const { defineConfig, devices } = require('@playwright/test');

/**
 * Playwright config for Product Analyser Streamlit app.
 * The app must be running on http://localhost:8501 before tests start.
 * Start it with:  streamlit run app.py
 */
module.exports = defineConfig({
  testDir: './tests',
  fullyParallel: false,       // Streamlit is stateful — run tests serially
  retries: 1,                 // 1 retry on flaky Streamlit renders
  workers: 1,
  reporter: [['html', { open: 'never' }], ['list']],

  use: {
    baseURL: 'http://localhost:8501',
    headless: true,
    viewport: { width: 1280, height: 800 },
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    // Streamlit needs longer timeouts — it renders async via WebSocket
    actionTimeout: 15_000,
    navigationTimeout: 30_000,
  },

  // Run on Chromium and mobile Chrome
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'mobile-chrome',
      use: { ...devices['Pixel 5'] },
    },
  ],

  // Timeout per test (Streamlit + scraping can be slow)
  timeout: 90_000,
});

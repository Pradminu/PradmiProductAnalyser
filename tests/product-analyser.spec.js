// @ts-check
const { test, expect } = require('@playwright/test');
const path = require('path');

/**
 * Helpers
 * -------
 * Streamlit renders via WebSocket + React. We must wait for the Streamlit
 * "ready" state (no spinner) before asserting on content.
 */

/** Wait until the Streamlit loading overlay is gone. */
async function waitForStreamlit(page) {
  // Streamlit shows a loading div while the app boots
  await page.waitForFunction(() => {
    const statusEl = document.querySelector('[data-testid="stStatusWidget"]');
    const spinner = document.querySelector('.stSpinner');
    return !spinner && document.readyState === 'complete';
  }, { timeout: 40_000 });
  // Extra settle time for Streamlit's async renders
  await page.waitForTimeout(1_500);
}

/** Click the correct tab by its visible label text. */
async function clickTab(page, label) {
  const tab = page.getByRole('tab', { name: label });
  await tab.waitFor({ state: 'visible' });
  await tab.click();
  await page.waitForTimeout(500);
}

/** Type a value and trigger the Analyse button in the active tab. */
async function searchProduct(page, inputKey, buttonKey, value) {
  const input = page.locator(`input[aria-label="${inputKey}"], [data-testid="${inputKey}"] input`).first();
  await input.fill(value);
  const btn = page.getByTestId(buttonKey).or(page.getByRole('button', { name: /analyse/i })).first();
  await btn.click();
}

// ---------------------------------------------------------------------------
// Suite
// ---------------------------------------------------------------------------

test.describe('Product Analyser App', () => {

  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await waitForStreamlit(page);
  });

  // -------------------------------------------------------------------------
  // 1. Page loads & header visible
  // -------------------------------------------------------------------------
  test('page loads with correct title and input tabs', async ({ page }) => {
    await expect(page).toHaveTitle(/Product Analyser/i);

    // Main heading
    await expect(page.getByRole('heading', { name: /Product Analyser/i })).toBeVisible();

    // All 4 input tabs present
    for (const tab of ['Product Name', 'Product URL', 'Barcode Image', 'Product Photo']) {
      await expect(page.getByRole('tab', { name: new RegExp(tab, 'i') })).toBeVisible();
    }
  });

  // -------------------------------------------------------------------------
  // 2. Product name tab — UI elements
  // -------------------------------------------------------------------------
  test('product name tab shows input and analyse button', async ({ page }) => {
    await clickTab(page, /Product Name/i);

    const nameInput = page.locator('input[type="text"]').first();
    await expect(nameInput).toBeVisible();

    const btn = page.getByRole('button', { name: /Analyse Product/i });
    await expect(btn).toBeVisible();
  });

  // -------------------------------------------------------------------------
  // 3. Product name — empty input shows warning
  // -------------------------------------------------------------------------
  test('empty product name shows warning message', async ({ page }) => {
    await clickTab(page, /Product Name/i);

    const btn = page.getByRole('button', { name: /Analyse Product/i });
    await btn.click();
    await page.waitForTimeout(1_000);

    // Streamlit warning block
    const warning = page.locator('[data-testid="stAlert"]').or(
      page.locator('.stAlert')
    ).first();
    await expect(warning).toBeVisible();
  });

  // -------------------------------------------------------------------------
  // 4. Product name search — full report renders
  // -------------------------------------------------------------------------
  test('searching "Maggi Noodles" renders the analysis report', async ({ page }) => {
    test.setTimeout(120_000);

    await clickTab(page, /Product Name/i);

    const nameInput = page.locator('input[type="text"]').first();
    await nameInput.fill('Maggi Noodles');

    const btn = page.getByRole('button', { name: /Analyse Product/i });
    await btn.click();

    // Wait for spinners to clear (data fetch + analysis can take time)
    await page.waitForSelector('.stSpinner', { state: 'hidden', timeout: 60_000 });
    await page.waitForTimeout(2_000);

    // Report heading must appear
    await expect(
      page.getByRole('heading', { name: /Analysis Report/i })
    ).toBeVisible({ timeout: 20_000 });

    // Product name should appear somewhere on the page
    await expect(page.getByText(/Maggi/i).first()).toBeVisible();
  });

  // -------------------------------------------------------------------------
  // 5. Score meter renders (0–10)
  // -------------------------------------------------------------------------
  test('score meter is visible after analysis', async ({ page }) => {
    test.setTimeout(120_000);

    await clickTab(page, /Product Name/i);
    await page.locator('input[type="text"]').first().fill('Maggi Noodles');
    await page.getByRole('button', { name: /Analyse Product/i }).click();

    await page.waitForSelector('.stSpinner', { state: 'hidden', timeout: 60_000 });
    await page.waitForTimeout(2_000);

    // Score badge contains a number between 0 and 10
    const scoreBadge = page.locator('.score-badge');
    await expect(scoreBadge).toBeVisible({ timeout: 15_000 });
    const scoreText = await scoreBadge.innerText();
    const score = parseFloat(scoreText);
    expect(score).toBeGreaterThanOrEqual(0);
    expect(score).toBeLessThanOrEqual(10);
  });

  // -------------------------------------------------------------------------
  // 6. All 13 report sections appear
  // -------------------------------------------------------------------------
  test('all major report sections are present', async ({ page }) => {
    test.setTimeout(120_000);

    await clickTab(page, /Product Name/i);
    await page.locator('input[type="text"]').first().fill('Dettol Soap');
    await page.getByRole('button', { name: /Analyse Product/i }).click();

    await page.waitForSelector('.stSpinner', { state: 'hidden', timeout: 60_000 });
    await page.waitForTimeout(2_000);

    const expectedSections = [
      /WHAT IS THIS PRODUCT/i,
      /WHY SHOULD YOU USE IT/i,
      /WHO IS IT BEST FOR/i,
      /HOW TO USE IT/i,
      /PROS & CONS/i,
      /HEALTH WARNINGS/i,
      /KEY INGREDIENTS/i,
      /REVIEW SENTIMENT/i,
      /ALTERNATIVES/i,
      /WHERE TO BUY/i,
    ];

    for (const section of expectedSections) {
      await expect(page.getByText(section).first()).toBeVisible({ timeout: 10_000 });
    }
  });

  // -------------------------------------------------------------------------
  // 7. Verdict box is rendered with colour class
  // -------------------------------------------------------------------------
  test('verdict box renders with one of the four colour states', async ({ page }) => {
    test.setTimeout(120_000);

    await clickTab(page, /Product Name/i);
    await page.locator('input[type="text"]').first().fill('Himalaya Face Wash');
    await page.getByRole('button', { name: /Analyse Product/i }).click();

    await page.waitForSelector('.stSpinner', { state: 'hidden', timeout: 60_000 });
    await page.waitForTimeout(2_000);

    // One of the verdict CSS classes must exist
    const verdictEl = page.locator(
      '.verdict-green, .verdict-blue, .verdict-orange, .verdict-red'
    ).first();
    await expect(verdictEl).toBeVisible({ timeout: 15_000 });
  });

  // -------------------------------------------------------------------------
  // 8. PDF download button appears
  // -------------------------------------------------------------------------
  test('PDF download button is present after analysis', async ({ page }) => {
    test.setTimeout(120_000);

    await clickTab(page, /Product Name/i);
    await page.locator('input[type="text"]').first().fill('Dove Soap');
    await page.getByRole('button', { name: /Analyse Product/i }).click();

    await page.waitForSelector('.stSpinner', { state: 'hidden', timeout: 60_000 });
    await page.waitForTimeout(2_000);

    await expect(
      page.getByRole('button', { name: /Download.*PDF/i })
    ).toBeVisible({ timeout: 15_000 });
  });

  // -------------------------------------------------------------------------
  // 9. PDF download triggers a file download
  // -------------------------------------------------------------------------
  test('clicking PDF download starts a file download', async ({ page }) => {
    test.setTimeout(120_000);

    await clickTab(page, /Product Name/i);
    await page.locator('input[type="text"]').first().fill('Dove Soap');
    await page.getByRole('button', { name: /Analyse Product/i }).click();

    await page.waitForSelector('.stSpinner', { state: 'hidden', timeout: 60_000 });
    await page.waitForTimeout(2_000);

    const downloadPromise = page.waitForEvent('download', { timeout: 20_000 });
    await page.getByRole('button', { name: /Download.*PDF/i }).click();
    const download = await downloadPromise;

    expect(download.suggestedFilename()).toMatch(/\.pdf$/i);
  });

  // -------------------------------------------------------------------------
  // 10. URL tab — input visible
  // -------------------------------------------------------------------------
  test('URL tab shows URL input field', async ({ page }) => {
    await clickTab(page, /Product URL/i);
    const urlInput = page.locator('input[type="text"]').first();
    await expect(urlInput).toBeVisible();
    await expect(
      page.getByRole('button', { name: /Analyse URL/i })
    ).toBeVisible();
  });

  // -------------------------------------------------------------------------
  // 11. Barcode tab — file uploader visible
  // -------------------------------------------------------------------------
  test('barcode tab shows file uploader', async ({ page }) => {
    await clickTab(page, /Barcode Image/i);
    const uploader = page.locator('[data-testid="stFileUploader"]').first();
    await expect(uploader).toBeVisible();
  });

  // -------------------------------------------------------------------------
  // 12. Photo tab — file uploader visible
  // -------------------------------------------------------------------------
  test('product photo tab shows file uploader', async ({ page }) => {
    await clickTab(page, /Product Photo/i);
    const uploader = page.locator('[data-testid="stFileUploader"]').first();
    await expect(uploader).toBeVisible();
  });

  // -------------------------------------------------------------------------
  // 13. Compare feature — input and button visible after first analysis
  // -------------------------------------------------------------------------
  test('compare section appears after first analysis', async ({ page }) => {
    test.setTimeout(120_000);

    await clickTab(page, /Product Name/i);
    await page.locator('input[type="text"]').first().fill('Maggi Noodles');
    await page.getByRole('button', { name: /Analyse Product/i }).click();

    await page.waitForSelector('.stSpinner', { state: 'hidden', timeout: 60_000 });
    await page.waitForTimeout(2_000);

    await expect(
      page.getByRole('heading', { name: /Compare with Another Product/i })
    ).toBeVisible({ timeout: 15_000 });

    await expect(
      page.getByRole('button', { name: /Compare/i })
    ).toBeVisible();
  });

  // -------------------------------------------------------------------------
  // 14. Compare two products — two reports render side by side
  // -------------------------------------------------------------------------
  test('comparing two products shows two separate reports', async ({ page }) => {
    test.setTimeout(180_000);

    // First product
    await clickTab(page, /Product Name/i);
    await page.locator('input[type="text"]').first().fill('Maggi Noodles');
    await page.getByRole('button', { name: /Analyse Product/i }).click();
    await page.waitForSelector('.stSpinner', { state: 'hidden', timeout: 60_000 });
    await page.waitForTimeout(2_000);

    // Second product via compare input
    const compareInput = page.locator('input[type="text"]').last();
    await compareInput.fill('Top Ramen Noodles');
    await page.getByRole('button', { name: /⚖️ Compare|Compare/i }).click();

    await page.waitForSelector('.stSpinner', { state: 'hidden', timeout: 60_000 });
    await page.waitForTimeout(3_000);

    await expect(
      page.getByRole('heading', { name: /Side-by-side Comparison/i })
    ).toBeVisible({ timeout: 20_000 });

    // Both product names should appear
    await expect(page.getByText(/Maggi/i).first()).toBeVisible();
    await expect(page.getByText(/Top Ramen|Noodle/i).first()).toBeVisible();
  });

  // -------------------------------------------------------------------------
  // 15. Responsive — mobile viewport renders without overlap
  // -------------------------------------------------------------------------
  test('app renders on mobile viewport without horizontal scroll', async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 }); // iPhone 14
    await page.goto('/');
    await waitForStreamlit(page);

    // No horizontal scrollbar
    const bodyWidth = await page.evaluate(() => document.body.scrollWidth);
    const viewportWidth = await page.evaluate(() => window.innerWidth);
    expect(bodyWidth).toBeLessThanOrEqual(viewportWidth + 20); // 20px tolerance
  });

  // -------------------------------------------------------------------------
  // 16. Sentiment bar renders coloured segments
  // -------------------------------------------------------------------------
  test('sentiment bar shows positive/neutral/negative segments', async ({ page }) => {
    test.setTimeout(120_000);

    await clickTab(page, /Product Name/i);
    await page.locator('input[type="text"]').first().fill('Maggi Noodles');
    await page.getByRole('button', { name: /Analyse Product/i }).click();

    await page.waitForSelector('.stSpinner', { state: 'hidden', timeout: 60_000 });
    await page.waitForTimeout(2_000);

    // Open the sentiment expander
    const sentimentExpander = page.getByText(/REVIEW SENTIMENT/i).first();
    await sentimentExpander.click();
    await page.waitForTimeout(500);

    // The coloured sentiment bar must be in the DOM
    await expect(
      page.locator('text=/Positive \\d+%/i').first()
    ).toBeVisible({ timeout: 10_000 });
  });

  // -------------------------------------------------------------------------
  // 17. Alternatives table renders with data
  // -------------------------------------------------------------------------
  test('alternatives table has at least 3 rows', async ({ page }) => {
    test.setTimeout(120_000);

    await clickTab(page, /Product Name/i);
    await page.locator('input[type="text"]').first().fill('Maggi Noodles');
    await page.getByRole('button', { name: /Analyse Product/i }).click();

    await page.waitForSelector('.stSpinner', { state: 'hidden', timeout: 60_000 });
    await page.waitForTimeout(2_000);

    const altExpander = page.getByText(/ALTERNATIVES/i).first();
    await altExpander.click();
    await page.waitForTimeout(500);

    // Streamlit dataframe renders a table
    const rows = page.locator('[data-testid="stDataFrame"] tr, .stDataFrame tr');
    await expect(rows.first()).toBeVisible({ timeout: 10_000 });
    const count = await rows.count();
    expect(count).toBeGreaterThanOrEqual(3); // header + 3 data rows
  });

  // -------------------------------------------------------------------------
  // 18. Nutrition table renders when product has nutritional data
  // -------------------------------------------------------------------------
  test('nutrition section shows metric cards for food product', async ({ page }) => {
    test.setTimeout(120_000);

    await clickTab(page, /Product Name/i);
    await page.locator('input[type="text"]').first().fill('Britannia Good Day Biscuit');
    await page.getByRole('button', { name: /Analyse Product/i }).click();

    await page.waitForSelector('.stSpinner', { state: 'hidden', timeout: 60_000 });
    await page.waitForTimeout(2_000);

    const ingredientsExpander = page.getByText(/KEY INGREDIENTS/i).first();
    await ingredientsExpander.click();
    await page.waitForTimeout(500);

    // At least one metric should be visible (Calories, Fat, etc.)
    const metrics = page.locator('[data-testid="stMetric"]');
    const count = await metrics.count();
    expect(count).toBeGreaterThanOrEqual(1);
  });

});

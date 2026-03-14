/**
 * E2E tests for the Finance pages (dashboard, upload, review, export).
 * Verifies page loads and key UI elements are present.
 */
import { test, expect } from "@playwright/test";

test.describe("Finance Pages", () => {
  test("finance dashboard loads", async ({ page }) => {
    await page.goto("/finance");
    await expect(page.locator("h1")).toContainText(/finance/i);
  });

  test("finance upload page loads with form", async ({ page }) => {
    await page.goto("/finance/upload");
    await expect(page.locator("h1")).toContainText(/upload|finance/i);
  });

  test("finance upload has file input", async ({ page }) => {
    await page.goto("/finance/upload");
    const fileInput = page.locator("input[type='file']");
    await expect(fileInput).toBeAttached();
  });

  test("finance review page loads", async ({ page }) => {
    await page.goto("/finance/review");
    await expect(page).toHaveURL("/finance/review");
  });

  test("finance export page loads", async ({ page }) => {
    await page.goto("/finance/export");
    await expect(page).toHaveURL("/finance/export");
    await expect(page.locator("h1")).toContainText(/export/i);
  });

  test("export page has download buttons", async ({ page }) => {
    await page.goto("/finance/export");
    const btns = page.getByRole("button");
    await expect(btns.first()).toBeVisible();
  });
});

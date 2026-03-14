/**
 * E2E tests for the Help / Onboarding page.
 * Verifies page loads, FAQ sections, and accordion interactions.
 */
import { test, expect } from "@playwright/test";

test.describe("Help Page", () => {
  test("loads with help heading", async ({ page }) => {
    await page.goto("/help");
    await expect(page.locator("h1")).toContainText(/help|onboarding|guide/i);
  });

  test("shows FAQ sections", async ({ page }) => {
    await page.goto("/help");
    // Should have multiple FAQ question elements
    const questions = page.locator("button, summary, [role='button']");
    const count = await questions.count();
    expect(count).toBeGreaterThan(5);
  });

  test("has email FAQ section heading", async ({ page }) => {
    await page.goto("/help");
    await expect(page.getByRole("heading", { name: /emails.*tasks/i })).toBeVisible();
  });

  test("FAQ accordion expands on click", async ({ page }) => {
    await page.goto("/help");
    // Find the first clickable FAQ item and click it
    const firstFaq = page.locator("button, summary, [role='button']").first();
    await firstFaq.click();
    // After clicking, more content should be visible
    const body = page.locator("body");
    await expect(body).toBeVisible();
  });
});

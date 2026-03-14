/**
 * E2E tests for the Voice Assistant page.
 * Verifies page loads, input elements, and basic interaction.
 */
import { test, expect } from "@playwright/test";

test.describe("Voice Page", () => {
  test("loads with voice assistant heading", async ({ page }) => {
    await page.goto("/voice");
    await expect(page.locator("h1")).toContainText(/voice|assistant/i);
  });

  test("shows question input field", async ({ page }) => {
    await page.goto("/voice");
    const input = page.locator("input[placeholder*='Ask about']");
    await expect(input).toBeVisible();
  });

  test("has an ask or submit button", async ({ page }) => {
    await page.goto("/voice");
    const btn = page.getByRole("button", { name: /ask|send|submit/i });
    await expect(btn).toBeVisible();
  });
});

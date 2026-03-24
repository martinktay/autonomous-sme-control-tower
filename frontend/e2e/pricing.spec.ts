/**
 * E2E tests for the Pricing page (public route).
 */
import { test, expect } from "@playwright/test";

test.describe("Pricing Page", () => {
  test("loads with pricing heading", async ({ page }) => {
    await page.goto("/pricing");
    await expect(page.locator("h1")).toContainText("Know Your Cashflow");
  });

  test("shows all four tier cards", async ({ page }) => {
    await page.goto("/pricing");
    await expect(page.locator("text=Starter")).toBeVisible();
    await expect(page.locator("text=Growth")).toBeVisible();
    await expect(page.locator("text=Business")).toBeVisible();
    await expect(page.locator("text=Enterprise")).toBeVisible();
  });

  test("shows NGN pricing by default", async ({ page }) => {
    await page.goto("/pricing");
    await expect(page.locator("text=₦0")).toBeVisible();
    await expect(page.locator("text=₦14,900")).toBeVisible();
  });

  test("can toggle to USD pricing", async ({ page }) => {
    await page.goto("/pricing");
    await page.click("text=$ USD");
    await expect(page.locator("text=$9.99")).toBeVisible();
  });

  test("shows compare plans section", async ({ page }) => {
    await page.goto("/pricing");
    await expect(page.locator("text=Compare Plans")).toBeVisible();
  });

  test("shows start free CTA", async ({ page }) => {
    await page.goto("/pricing");
    const cta = page.getByRole("link", { name: /start free/i }).last();
    await expect(cta).toBeVisible();
  });
});

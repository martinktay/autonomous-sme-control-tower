/**
 * E2E tests for the Help / FAQ page (public route, no auth needed).
 */
import { test, expect } from "@playwright/test";

test.describe("Help Page", () => {
  test("loads with help heading", async ({ page }) => {
    await page.goto("/help");
    await expect(page.locator("h1")).toContainText(/help|getting started/i);
  });

  test("shows quick start section", async ({ page }) => {
    await page.goto("/help");
    await expect(page.locator("text=Quick Start")).toBeVisible();
  });

  test("has platform overview section", async ({ page }) => {
    await page.goto("/help");
    await expect(page.locator("text=Platform Overview")).toBeVisible();
  });

  test("has emails and tasks FAQ section", async ({ page }) => {
    await page.goto("/help");
    await expect(page.locator("text=Emails & Tasks")).toBeVisible();
  });
});

/**
 * E2E tests for the Onboarding wizard.
 * Public route — tests multi-step flow.
 */
import { test, expect } from "@playwright/test";

test.describe("Onboarding Page", () => {
  test("loads with welcome heading", async ({ page }) => {
    await page.goto("/onboarding");
    await expect(page.locator("text=Welcome to SME Control Tower")).toBeVisible();
  });

  test("shows step 1 of 5 progress", async ({ page }) => {
    await page.goto("/onboarding");
    await expect(page.locator("text=Step 1 of 5")).toBeVisible();
  });

  test("has business name input on step 1", async ({ page }) => {
    await page.goto("/onboarding");
    await expect(page.locator("input[placeholder*='Mama Joy']")).toBeVisible();
  });

  test("continue button is disabled without business name", async ({ page }) => {
    await page.goto("/onboarding");
    const btn = page.getByRole("button", { name: /continue/i });
    await expect(btn).toBeDisabled();
  });

  test("can advance to step 2 after entering business name", async ({ page }) => {
    await page.goto("/onboarding");
    await page.fill("input[placeholder*='Mama Joy']", "Test Shop");
    await page.getByRole("button", { name: /continue/i }).click();
    await expect(page.locator("text=What type of business")).toBeVisible();
  });
});

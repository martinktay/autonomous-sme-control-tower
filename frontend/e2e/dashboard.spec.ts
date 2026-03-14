import { test, expect } from "@playwright/test";

test.describe("Dashboard Page", () => {
  test("shows NSI card with title", async ({ page }) => {
    await page.goto("/dashboard");
    await expect(page.locator("text=Nova Stability Index")).toBeVisible();
  });

  test("shows refresh and run analysis buttons", async ({ page }) => {
    await page.goto("/dashboard");
    await expect(page.getByRole("button", { name: /refresh/i })).toBeVisible();
    await expect(page.getByRole("button", { name: /run analysis/i })).toBeVisible();
  });

  test("shows risk panel section", async ({ page }) => {
    await page.goto("/dashboard");
    await expect(page.locator("text=Top Operational Risks")).toBeVisible();
  });
});

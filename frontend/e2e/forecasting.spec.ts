/**
 * E2E tests for the Forecasting page.
 * Verifies auth redirect and basic page rendering when authenticated.
 */
import { test, expect } from "@playwright/test";

const MOCK_USER = {
  user_id: "u-test", email: "test@demo.com", org_id: "org-test",
  full_name: "Test User", role: "owner", business_name: "Test Biz", tier: "business",
};

async function seedAuth(page: any) {
  await page.goto("/");
  await page.evaluate((u: any) => {
    localStorage.setItem("sme_access_token", "mock-token");
    localStorage.setItem("sme_user", JSON.stringify(u));
  }, MOCK_USER);
}

test.describe("Forecasting Page", () => {
  test("redirects to login when unauthenticated", async ({ page }) => {
    await page.goto("/forecasting");
    await expect(page).toHaveURL("/login");
  });

  test("loads with forecasting heading when authenticated", async ({ page }) => {
    await seedAuth(page);
    await page.goto("/forecasting");
    await expect(page.locator("h1")).toContainText("AI Forecasting");
  });

  test("shows full AI forecast button", async ({ page }) => {
    await seedAuth(page);
    await page.goto("/forecasting");
    await expect(page.getByRole("button", { name: /full ai forecast/i })).toBeVisible();
  });
});

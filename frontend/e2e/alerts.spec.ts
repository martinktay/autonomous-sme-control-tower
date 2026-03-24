/**
 * E2E tests for the Alerts page.
 * Verifies auth redirect and basic page rendering when authenticated.
 */
import { test, expect } from "@playwright/test";

const MOCK_USER = {
  user_id: "u-test", email: "test@demo.com", org_id: "org-test",
  full_name: "Test User", role: "owner", business_name: "Test Biz", tier: "growth",
};

async function seedAuth(page: any) {
  await page.goto("/");
  await page.evaluate((u: any) => {
    localStorage.setItem("sme_access_token", "mock-token");
    localStorage.setItem("sme_user", JSON.stringify(u));
  }, MOCK_USER);
}

test.describe("Alerts Page", () => {
  test("redirects to login when unauthenticated", async ({ page }) => {
    await page.goto("/alerts");
    await expect(page).toHaveURL("/login");
  });

  test("loads with alerts heading when authenticated", async ({ page }) => {
    await seedAuth(page);
    await page.goto("/alerts");
    await expect(page.locator("h1")).toContainText("Alerts");
  });
});

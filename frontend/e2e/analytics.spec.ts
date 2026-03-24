/**
 * E2E tests for the Analytics and Marketing Insights pages.
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

test.describe("Analytics Page", () => {
  test("redirects to login when unauthenticated", async ({ page }) => {
    await page.goto("/analytics");
    await expect(page).toHaveURL("/login");
  });

  test("loads with analytics heading when authenticated", async ({ page }) => {
    await seedAuth(page);
    await page.goto("/analytics");
    await expect(page.locator("h1")).toContainText("Business Analytics");
  });

  test("shows marketing insights link", async ({ page }) => {
    await seedAuth(page);
    await page.goto("/analytics");
    const link = page.getByRole("link", { name: /view marketing insights/i });
    await expect(link).toBeVisible();
  });
});

test.describe("Marketing Insights Page", () => {
  test("redirects to login when unauthenticated", async ({ page }) => {
    await page.goto("/analytics/marketing");
    await expect(page).toHaveURL("/login");
  });

  test("loads with marketing heading when authenticated", async ({ page }) => {
    await seedAuth(page);
    await page.goto("/analytics/marketing");
    await expect(page.locator("h1")).toContainText("Marketing Insights");
  });

  test("shows insight cards", async ({ page }) => {
    await seedAuth(page);
    await page.goto("/analytics/marketing");
    await expect(page.locator("text=Customer Segmentation")).toBeVisible();
    await expect(page.locator("text=Sales Forecasting")).toBeVisible();
  });

  test("has back to analytics link", async ({ page }) => {
    await seedAuth(page);
    await page.goto("/analytics/marketing");
    await expect(page.getByRole("link", { name: /back to business analytics/i })).toBeVisible();
  });
});

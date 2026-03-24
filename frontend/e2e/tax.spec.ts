/**
 * E2E tests for the Tax & Compliance page.
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

test.describe("Tax Page", () => {
  test("redirects to login when unauthenticated", async ({ page }) => {
    await page.goto("/tax");
    await expect(page).toHaveURL("/login");
  });

  test("loads with tax heading when authenticated", async ({ page }) => {
    await seedAuth(page);
    await page.goto("/tax");
    await expect(page.locator("h1")).toContainText("Tax & Compliance");
  });

  test("shows country selector with Nigeria default", async ({ page }) => {
    await seedAuth(page);
    await page.goto("/tax");
    await expect(page.locator("text=Nigeria")).toBeVisible();
  });

  test("shows generate tax report button", async ({ page }) => {
    await seedAuth(page);
    await page.goto("/tax");
    await expect(page.getByRole("button", { name: /generate tax report/i })).toBeVisible();
  });
});

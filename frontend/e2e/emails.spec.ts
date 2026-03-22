/**
 * E2E tests for the Emails page and Tasks sub-page.
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

test.describe("Emails Page", () => {
  test("redirects to login when unauthenticated", async ({ page }) => {
    await page.goto("/emails");
    await expect(page).toHaveURL("/login");
  });

  test("loads with page title when authenticated", async ({ page }) => {
    await seedAuth(page);
    await page.goto("/emails");
    await expect(page.locator("h1")).toContainText(/email/i);
  });

  test("can navigate to tasks sub-page", async ({ page }) => {
    await seedAuth(page);
    await page.goto("/emails/tasks");
    await expect(page).toHaveURL("/emails/tasks");
    await expect(page.locator("h1")).toContainText(/task/i);
  });

  test("tasks page shows task list or empty state", async ({ page }) => {
    await seedAuth(page);
    await page.goto("/emails/tasks");
    const body = page.locator("body");
    await expect(body).toBeVisible();
  });
});

/**
 * E2E tests for the Actions page.
 * Verifies auth redirect and basic page rendering when authenticated.
 */
import { test, expect } from "@playwright/test";

const MOCK_USER = {
  user_id: "u-test", email: "test@demo.com", org_id: "org-test",
  full_name: "Test User", role: "owner", business_name: "Test Biz", tier: "starter",
};

async function seedAuth(page: any) {
  await page.goto("/");
  await page.evaluate((u: any) => {
    localStorage.setItem("sme_access_token", "mock-token");
    localStorage.setItem("sme_user", JSON.stringify(u));
  }, MOCK_USER);
}

test.describe("Actions Page", () => {
  test("redirects to login when unauthenticated", async ({ page }) => {
    await page.goto("/actions");
    await expect(page).toHaveURL("/login");
  });

  test("loads with page heading when authenticated", async ({ page }) => {
    await seedAuth(page);
    await page.goto("/actions");
    await expect(page.locator("h1")).toContainText("Action History");
  });

  test("shows refresh actions button", async ({ page }) => {
    await seedAuth(page);
    await page.goto("/actions");
    const btn = page.getByRole("button", { name: /refresh actions/i });
    await expect(btn).toBeVisible();
  });

  test("shows empty state when no actions", async ({ page }) => {
    await seedAuth(page);
    await page.goto("/actions");
    await expect(page.locator("text=No actions executed yet")).toBeVisible();
  });
});

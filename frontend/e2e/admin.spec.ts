/**
 * E2E tests for the Admin page.
 * Verifies access control and basic rendering for super_admin users.
 */
import { test, expect } from "@playwright/test";

const SUPER_ADMIN = {
  user_id: "u-admin", email: "admin@demo.com", org_id: "org-test",
  full_name: "Admin User", role: "super_admin", business_name: "Platform", tier: "enterprise",
};

const REGULAR_USER = {
  user_id: "u-test", email: "test@demo.com", org_id: "org-test",
  full_name: "Test User", role: "owner", business_name: "Test Biz", tier: "starter",
};

async function seedAuth(page: any, user: any) {
  await page.goto("/");
  await page.evaluate((u: any) => {
    localStorage.setItem("sme_access_token", "mock-token");
    localStorage.setItem("sme_user", JSON.stringify(u));
  }, user);
}

test.describe("Admin Page", () => {
  test("shows access denied for non-super_admin", async ({ page }) => {
    await seedAuth(page, REGULAR_USER);
    await page.goto("/admin");
    await expect(page.locator("text=Access denied")).toBeVisible();
  });

  test("loads admin panel for super_admin", async ({ page }) => {
    await seedAuth(page, SUPER_ADMIN);
    await page.goto("/admin");
    await expect(page.locator("h1")).toContainText("Admin Panel");
  });

  test("shows tab navigation for super_admin", async ({ page }) => {
    await seedAuth(page, SUPER_ADMIN);
    await page.goto("/admin");
    await expect(page.locator("text=Overview")).toBeVisible();
    await expect(page.locator("text=Users")).toBeVisible();
    await expect(page.locator("text=Subscriptions")).toBeVisible();
    await expect(page.locator("text=Config")).toBeVisible();
  });
});

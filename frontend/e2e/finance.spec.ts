/**
 * E2E tests for the Finance pages.
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

test.describe("Finance Pages", () => {
  test("redirects to login when unauthenticated", async ({ page }) => {
    await page.goto("/finance");
    await expect(page).toHaveURL("/login");
  });

  test("finance dashboard loads when authenticated", async ({ page }) => {
    await seedAuth(page);
    await page.goto("/finance");
    await expect(page.locator("h1")).toContainText(/finance/i);
  });

  test("finance upload page loads with form", async ({ page }) => {
    await seedAuth(page);
    await page.goto("/finance/upload");
    await expect(page.locator("h1")).toContainText(/upload|finance/i);
  });

  test("finance upload has file input", async ({ page }) => {
    await seedAuth(page);
    await page.goto("/finance/upload");
    const fileInput = page.locator("input[type='file']");
    await expect(fileInput).toBeAttached();
  });

  test("finance export page loads", async ({ page }) => {
    await seedAuth(page);
    await page.goto("/finance/export");
    await expect(page).toHaveURL("/finance/export");
    await expect(page.locator("h1")).toContainText(/export/i);
  });
});

/**
 * E2E tests for the POS Connector page.
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

test.describe("POS Connector Page", () => {
  test("redirects to login when unauthenticated", async ({ page }) => {
    await page.goto("/pos");
    await expect(page).toHaveURL("/login");
  });

  test("loads with POS heading when authenticated", async ({ page }) => {
    await seedAuth(page);
    await page.goto("/pos");
    await expect(page.locator("h1")).toContainText("POS Connector");
  });

  test("has file input for POS data", async ({ page }) => {
    await seedAuth(page);
    await page.goto("/pos");
    const fileInput = page.locator("input[type='file']");
    await expect(fileInput).toBeAttached();
  });

  test("import button is disabled without file", async ({ page }) => {
    await seedAuth(page);
    await page.goto("/pos");
    const btn = page.getByRole("button", { name: /import/i });
    await expect(btn).toBeDisabled();
  });
});

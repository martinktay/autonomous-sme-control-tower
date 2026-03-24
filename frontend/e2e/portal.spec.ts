/**
 * E2E tests for the Portal (closed-loop analysis) page.
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

test.describe("Portal Page", () => {
  test("redirects to login when unauthenticated", async ({ page }) => {
    await page.goto("/portal");
    await expect(page).toHaveURL("/login");
  });

  test("loads with analysis heading when authenticated", async ({ page }) => {
    await seedAuth(page);
    await page.goto("/portal");
    await expect(page.locator("h1")).toContainText("Run a Full Business Analysis");
  });

  test("shows start analysis button", async ({ page }) => {
    await seedAuth(page);
    await page.goto("/portal");
    await expect(page.getByRole("button", { name: /start full analysis/i })).toBeVisible();
  });

  test("shows the 5 analysis steps", async ({ page }) => {
    await seedAuth(page);
    await page.goto("/portal");
    await expect(page.locator("text=Collecting Data")).toBeVisible();
    await expect(page.locator("text=Checking Health")).toBeVisible();
    await expect(page.locator("text=Finding Solutions")).toBeVisible();
    await expect(page.locator("text=Taking Action")).toBeVisible();
    await expect(page.locator("text=Measuring Results")).toBeVisible();
  });
});

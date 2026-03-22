/**
 * E2E tests for the Dashboard page.
 * Without a running backend, we verify auth redirect behaviour.
 * With localStorage auth token set, we verify the page renders key elements.
 */
import { test, expect } from "@playwright/test";

test.describe("Dashboard Page", () => {
  test("redirects to login when unauthenticated", async ({ page }) => {
    await page.goto("/dashboard");
    await expect(page).toHaveURL("/login");
  });

  test("renders dashboard shell when auth token is present", async ({ page }) => {
    // Seed localStorage with a mock auth session so AuthGuard allows rendering
    await page.goto("/");
    await page.evaluate(() => {
      localStorage.setItem("sme_access_token", "mock-token");
      localStorage.setItem("sme_user", JSON.stringify({
        user_id: "u-test",
        email: "test@demo.com",
        org_id: "org-test",
        full_name: "Test User",
        role: "owner",
        business_name: "Test Business",
        tier: "starter",
      }));
    });
    await page.goto("/dashboard");
    // Should stay on dashboard (not redirect to login)
    await expect(page).toHaveURL("/dashboard");
    // The h1 shows the business name from auth context
    await expect(page.locator("h1")).toContainText("Test Business");
  });

  test("shows refresh and run analysis buttons when authenticated", async ({ page }) => {
    await page.goto("/");
    await page.evaluate(() => {
      localStorage.setItem("sme_access_token", "mock-token");
      localStorage.setItem("sme_user", JSON.stringify({
        user_id: "u-test", email: "test@demo.com", org_id: "org-test",
        full_name: "Test User", role: "owner", business_name: "Test Biz", tier: "starter",
      }));
    });
    await page.goto("/dashboard");
    await expect(page.getByRole("button", { name: /refresh/i })).toBeVisible();
    await expect(page.getByRole("button", { name: /run analysis/i })).toBeVisible();
  });
});

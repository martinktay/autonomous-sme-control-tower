/**
 * E2E tests for the Voice Assistant page.
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

test.describe("Voice Page", () => {
  test("redirects to login when unauthenticated", async ({ page }) => {
    await page.goto("/voice");
    await expect(page).toHaveURL("/login");
  });

  test("loads with voice assistant heading when authenticated", async ({ page }) => {
    await seedAuth(page);
    await page.goto("/voice");
    await expect(page.locator("h1")).toContainText(/voice|assistant/i);
  });

  test("shows question input field", async ({ page }) => {
    await seedAuth(page);
    await page.goto("/voice");
    const input = page.locator("input[placeholder*='Ask about']");
    await expect(input).toBeVisible();
  });

  test("has an ask or submit button", async ({ page }) => {
    await seedAuth(page);
    await page.goto("/voice");
    const btn = page.getByRole("button", { name: /ask|send|submit/i });
    await expect(btn).toBeVisible();
  });
});

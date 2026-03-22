/**
 * E2E tests for the Upload page.
 * Tests auth redirect and basic form elements when authenticated.
 */
import { test, expect } from "@playwright/test";

const MOCK_USER = {
  user_id: "u-test", email: "test@demo.com", org_id: "org-test",
  full_name: "Test User", role: "owner", business_name: "Test Biz", tier: "starter",
};

test.describe("Upload Page", () => {
  test("redirects to login when unauthenticated", async ({ page }) => {
    await page.goto("/upload");
    await expect(page).toHaveURL("/login");
  });

  test("shows upload form when authenticated", async ({ page }) => {
    await page.goto("/");
    await page.evaluate((u) => {
      localStorage.setItem("sme_access_token", "mock-token");
      localStorage.setItem("sme_user", JSON.stringify(u));
    }, MOCK_USER);
    await page.goto("/upload");
    await expect(page.locator("h1")).toContainText("Upload Invoice");
  });

  test("upload button is disabled without file", async ({ page }) => {
    await page.goto("/");
    await page.evaluate((u) => {
      localStorage.setItem("sme_access_token", "mock-token");
      localStorage.setItem("sme_user", JSON.stringify(u));
    }, MOCK_USER);
    await page.goto("/upload");
    const btn = page.getByRole("button", { name: /upload invoice/i });
    await expect(btn).toBeDisabled();
  });

  test("shows helpful tip", async ({ page }) => {
    await page.goto("/");
    await page.evaluate((u) => {
      localStorage.setItem("sme_access_token", "mock-token");
      localStorage.setItem("sme_user", JSON.stringify(u));
    }, MOCK_USER);
    await page.goto("/upload");
    await expect(page.locator("text=Tip:")).toBeVisible();
  });
});

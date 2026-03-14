import { test, expect } from "@playwright/test";

test.describe("Upload Page", () => {
  test("shows upload form", async ({ page }) => {
    await page.goto("/upload");
    await expect(page.locator("h1")).toContainText("Upload Invoice");
  });

  test("upload button is disabled without file", async ({ page }) => {
    await page.goto("/upload");
    const btn = page.getByRole("button", { name: /upload invoice/i });
    await expect(btn).toBeDisabled();
  });

  test("shows helpful tip", async ({ page }) => {
    await page.goto("/upload");
    await expect(page.locator("text=Tip:")).toBeVisible();
  });
});

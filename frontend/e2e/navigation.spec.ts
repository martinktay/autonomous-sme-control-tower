import { test, expect } from "@playwright/test";

test.describe("Navigation", () => {
  test("home page loads with hero section", async ({ page }) => {
    await page.goto("/");
    await expect(page.locator("h1")).toContainText("AI-Powered Business Control Tower");
    await expect(page.getByRole("link", { name: "Upload an Invoice" })).toBeVisible();
  });

  test("navbar links are visible on desktop", async ({ page }) => {
    await page.setViewportSize({ width: 1280, height: 720 });
    await page.goto("/");
    await expect(page.getByRole("link", { name: "My Business", exact: true })).toBeVisible();
    await expect(page.getByRole("link", { name: "Upload", exact: true })).toBeVisible();
    await expect(page.getByRole("link", { name: "Analyse", exact: true })).toBeVisible();
    await expect(page.getByRole("link", { name: "Strategies", exact: true })).toBeVisible();
  });

  test("can navigate to dashboard", async ({ page }) => {
    await page.goto("/dashboard");
    await expect(page).toHaveURL("/dashboard");
  });

  test("can navigate to upload page", async ({ page }) => {
    await page.goto("/upload");
    await expect(page).toHaveURL("/upload");
    await expect(page.locator("h1")).toContainText("Upload Invoice");
  });

  test("can navigate to strategy page", async ({ page }) => {
    await page.goto("/strategy");
    await expect(page).toHaveURL("/strategy");
  });

  test("can navigate to actions page", async ({ page }) => {
    await page.goto("/actions");
    await expect(page).toHaveURL("/actions");
  });

  test("can navigate to voice page", async ({ page }) => {
    await page.goto("/voice");
    await expect(page).toHaveURL("/voice");
  });

  test("can navigate to memory page", async ({ page }) => {
    await page.goto("/memory");
    await expect(page).toHaveURL("/memory");
  });

  test("can navigate to help page", async ({ page }) => {
    await page.goto("/help");
    await expect(page).toHaveURL("/help");
  });

  test("can navigate to portal page", async ({ page }) => {
    await page.goto("/portal");
    await expect(page).toHaveURL("/portal");
  });
});

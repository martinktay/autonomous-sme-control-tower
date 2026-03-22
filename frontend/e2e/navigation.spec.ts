/**
 * E2E tests for public navigation and auth redirect behaviour.
 * These tests do NOT require a running backend or authenticated session.
 */
import { test, expect } from "@playwright/test";

test.describe("Public Pages", () => {
  test("home page loads with hero section", async ({ page }) => {
    await page.goto("/");
    await expect(page.locator("h1")).toContainText("Control Your Business Before Problems Start");
  });

  test("home page shows CTA buttons", async ({ page }) => {
    await page.goto("/");
    await expect(page.getByRole("link", { name: /start free/i }).first()).toBeVisible();
    await expect(page.getByRole("link", { name: /view my business/i })).toBeVisible();
  });

  test("public navbar shows key links", async ({ page }) => {
    await page.setViewportSize({ width: 1280, height: 720 });
    await page.goto("/");
    await expect(page.locator("nav >> text=Pricing")).toBeVisible();
    await expect(page.locator("nav >> text=Help")).toBeVisible();
  });

  test("can navigate to login page", async ({ page }) => {
    await page.goto("/login");
    await expect(page).toHaveURL("/login");
  });

  test("can navigate to register page", async ({ page }) => {
    await page.goto("/register");
    await expect(page).toHaveURL("/register");
  });

  test("can navigate to pricing page", async ({ page }) => {
    await page.goto("/pricing");
    await expect(page).toHaveURL("/pricing");
  });

  test("can navigate to help page", async ({ page }) => {
    await page.goto("/help");
    await expect(page).toHaveURL("/help");
  });
});

test.describe("Auth Redirect", () => {
  test("dashboard redirects to login when unauthenticated", async ({ page }) => {
    await page.goto("/dashboard");
    await expect(page).toHaveURL("/login");
  });

  test("upload redirects to login when unauthenticated", async ({ page }) => {
    await page.goto("/upload");
    await expect(page).toHaveURL("/login");
  });

  test("emails redirects to login when unauthenticated", async ({ page }) => {
    await page.goto("/emails");
    await expect(page).toHaveURL("/login");
  });

  test("voice redirects to login when unauthenticated", async ({ page }) => {
    await page.goto("/voice");
    await expect(page).toHaveURL("/login");
  });
});

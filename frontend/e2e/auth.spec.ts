/**
 * E2E tests for Login, Register, and Forgot Password pages.
 * These are public routes — no auth seeding needed.
 */
import { test, expect } from "@playwright/test";

test.describe("Login Page", () => {
  test("loads with sign in heading", async ({ page }) => {
    await page.goto("/login");
    await expect(page.locator("h1")).toContainText("Welcome back");
  });

  test("has email and password fields", async ({ page }) => {
    await page.goto("/login");
    await expect(page.locator("#email")).toBeVisible();
    await expect(page.locator("#password")).toBeVisible();
  });

  test("has sign in button", async ({ page }) => {
    await page.goto("/login");
    await expect(page.getByRole("button", { name: /sign in/i })).toBeVisible();
  });

  test("has forgot password and register links", async ({ page }) => {
    await page.goto("/login");
    await expect(page.getByRole("link", { name: /forgot your password/i })).toBeVisible();
    await expect(page.getByRole("link", { name: /create one/i })).toBeVisible();
  });
});

test.describe("Register Page", () => {
  test("loads with create account heading", async ({ page }) => {
    await page.goto("/register");
    await expect(page.locator("h1")).toContainText("Create your account");
  });

  test("has required form fields", async ({ page }) => {
    await page.goto("/register");
    await expect(page.locator("#email")).toBeVisible();
    await expect(page.locator("#password")).toBeVisible();
    await expect(page.locator("#businessName")).toBeVisible();
    await expect(page.locator("#businessType")).toBeVisible();
  });

  test("has create account button", async ({ page }) => {
    await page.goto("/register");
    await expect(page.getByRole("button", { name: /create account/i })).toBeVisible();
  });

  test("has sign in link", async ({ page }) => {
    await page.goto("/register");
    await expect(page.getByRole("link", { name: /sign in/i })).toBeVisible();
  });
});

test.describe("Forgot Password Page", () => {
  test("loads with forgot password heading", async ({ page }) => {
    await page.goto("/forgot-password");
    await expect(page.locator("h1")).toContainText("Forgot your password");
  });

  test("has email input and submit button", async ({ page }) => {
    await page.goto("/forgot-password");
    await expect(page.locator("#resetEmail")).toBeVisible();
    await expect(page.getByRole("button", { name: /send reset code/i })).toBeVisible();
  });

  test("has sign in link", async ({ page }) => {
    await page.goto("/forgot-password");
    await expect(page.getByRole("link", { name: /sign in/i })).toBeVisible();
  });
});

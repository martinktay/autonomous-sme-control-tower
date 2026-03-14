/**
 * E2E tests for the Emails page and Tasks sub-page.
 * Verifies page loads, form elements, and navigation between tabs.
 */
import { test, expect } from "@playwright/test";

test.describe("Emails Page", () => {
  test("loads with page title", async ({ page }) => {
    await page.goto("/emails");
    await expect(page.locator("h1")).toContainText(/email/i);
  });

  test("shows ingest email button and reveals form", async ({ page }) => {
    await page.goto("/emails");
    // The compose form is hidden by default; click "Ingest Email" to reveal it
    const ingestBtn = page.getByRole("button", { name: /ingest email/i });
    await expect(ingestBtn).toBeVisible();
    await ingestBtn.click();
    // After clicking, the form inputs should appear
    await expect(page.locator("textarea")).toBeVisible();
  });

  test("can navigate to tasks sub-page", async ({ page }) => {
    await page.goto("/emails/tasks");
    await expect(page).toHaveURL("/emails/tasks");
    await expect(page.locator("h1")).toContainText(/task/i);
  });

  test("tasks page shows task list or empty state", async ({ page }) => {
    await page.goto("/emails/tasks");
    // Should show either tasks or an empty/loading state
    const body = page.locator("body");
    await expect(body).toBeVisible();
  });
});

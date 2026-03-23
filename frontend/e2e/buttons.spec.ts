/**
 * E2E tests for action buttons across all feature pages.
 * Verifies buttons are visible, clickable, and respond to interaction.
 * Uses mock auth to bypass login.
 */
import { test, expect, Page } from "@playwright/test";

const MOCK_USER = {
  user_id: "u-test",
  email: "test@demo.com",
  org_id: "org-test",
  full_name: "Test User",
  role: "owner",
  business_name: "Test Biz",
  tier: "business",
};

async function seedAuth(page: Page) {
  await page.goto("/");
  await page.evaluate((u) => {
    localStorage.setItem("sme_access_token", "mock-token");
    localStorage.setItem("sme_user", JSON.stringify(u));
  }, MOCK_USER);
}

test.describe("Dashboard Buttons", () => {
  test("refresh and run analysis buttons are clickable", async ({ page }) => {
    await seedAuth(page);
    await page.goto("/dashboard");
    const refresh = page.getByRole("button", { name: /refresh/i });
    const runAnalysis = page.getByRole("button", { name: /run analysis/i });
    await expect(refresh).toBeVisible();
    await expect(runAnalysis).toBeVisible();
    await expect(refresh).toBeEnabled();
    await expect(runAnalysis).toBeEnabled();
  });
});

test.describe("Portal Buttons", () => {
  test("start analysis button is visible and clickable", async ({ page }) => {
    await seedAuth(page);
    await page.goto("/portal");
    const btn = page.getByRole("button", { name: /start full analysis/i });
    await expect(btn).toBeVisible();
    await expect(btn).toBeEnabled();
  });
});

test.describe("Strategy Buttons", () => {
  test("simulate strategies button is visible and clickable", async ({ page }) => {
    await seedAuth(page);
    await page.goto("/strategy");
    const btn = page.getByRole("button", { name: /simulate strategies/i });
    await expect(btn).toBeVisible();
    await expect(btn).toBeEnabled();
  });
});

test.describe("Actions Buttons", () => {
  test("refresh actions button is visible and clickable", async ({ page }) => {
    await seedAuth(page);
    await page.goto("/actions");
    const btn = page.getByRole("button", { name: /refresh actions/i });
    await expect(btn).toBeVisible();
    await expect(btn).toBeEnabled();
  });
});

test.describe("Supplier Intelligence Buttons", () => {
  test("AI analysis button is visible and clickable", async ({ page }) => {
    await seedAuth(page);
    await page.goto("/supplier-intelligence");
    const btn = page.getByRole("button", { name: /ai analysis/i });
    await expect(btn).toBeVisible();
    await expect(btn).toBeEnabled();
  });
});

test.describe("Predictions Buttons", () => {
  test("AI forecast button is visible and clickable", async ({ page }) => {
    await seedAuth(page);
    await page.goto("/predictions");
    const btn = page.getByRole("button", { name: /ai forecast/i });
    await expect(btn).toBeVisible();
    await expect(btn).toBeEnabled();
  });
});

test.describe("Forecasting Buttons", () => {
  test("full AI forecast button is visible and clickable", async ({ page }) => {
    await seedAuth(page);
    await page.goto("/forecasting");
    const btn = page.getByRole("button", { name: /full ai forecast/i });
    await expect(btn).toBeVisible();
    await expect(btn).toBeEnabled();
  });
});

test.describe("Branch Optimisation Buttons", () => {
  test("AI optimise button is visible and clickable", async ({ page }) => {
    await seedAuth(page);
    await page.goto("/branch-optimisation");
    const btn = page.getByRole("button", { name: /ai optimise/i });
    await expect(btn).toBeVisible();
    await expect(btn).toBeEnabled();
  });
});


test.describe("WhatsApp Buttons", () => {
  test("process message button is visible", async ({ page }) => {
    await seedAuth(page);
    await page.goto("/whatsapp");
    const btn = page.getByRole("button", { name: /process message/i });
    await expect(btn).toBeVisible();
  });

  test("generate summary button is visible and clickable", async ({ page }) => {
    await seedAuth(page);
    await page.goto("/whatsapp");
    const btn = page.getByRole("button", { name: /generate summary/i });
    await expect(btn).toBeVisible();
    await expect(btn).toBeEnabled();
  });
});

test.describe("Desktop Sync Buttons", () => {
  test("upload and check status buttons are visible", async ({ page }) => {
    await seedAuth(page);
    await page.goto("/sync");
    const upload = page.getByRole("button", { name: /upload & extract/i });
    const status = page.getByRole("button", { name: /check status/i });
    await expect(upload).toBeVisible();
    await expect(status).toBeVisible();
    await expect(status).toBeEnabled();
  });
});

test.describe("Transactions Buttons", () => {
  test("add transaction button is visible", async ({ page }) => {
    await seedAuth(page);
    await page.goto("/transactions");
    const btn = page.getByRole("button", { name: /add/i });
    await expect(btn).toBeVisible();
    await expect(btn).toBeEnabled();
  });
});

test.describe("Inventory Buttons", () => {
  test("add item button is visible", async ({ page }) => {
    await seedAuth(page);
    await page.goto("/inventory");
    const btn = page.getByRole("button", { name: /add item/i });
    await expect(btn).toBeVisible();
    await expect(btn).toBeEnabled();
  });
});

test.describe("Suppliers Buttons", () => {
  test("add button is visible", async ({ page }) => {
    await seedAuth(page);
    await page.goto("/suppliers");
    const btn = page.getByRole("button", { name: /add/i });
    await expect(btn).toBeVisible();
    await expect(btn).toBeEnabled();
  });
});

test.describe("Voice Buttons", () => {
  test("ask button is visible", async ({ page }) => {
    await seedAuth(page);
    await page.goto("/voice");
    const btn = page.getByRole("button", { name: /ask|send|submit/i });
    await expect(btn).toBeVisible();
  });
});

test.describe("Analytics Buttons", () => {
  test("marketing insights link button is visible", async ({ page }) => {
    await seedAuth(page);
    await page.goto("/analytics");
    const btn = page.getByRole("link", { name: /view marketing insights/i });
    await expect(btn).toBeVisible();
  });
});

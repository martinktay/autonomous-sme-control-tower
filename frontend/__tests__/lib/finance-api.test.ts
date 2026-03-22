/**
 * Tests for Finance API client functions.
 * Verifies upload, analytics, export, and review queue endpoints.
 */
export {};

const mockFetch = jest.fn();
global.fetch = mockFetch;

beforeEach(() => {
  jest.resetModules();
  mockFetch.mockReset();
});

describe("Finance API", () => {
  it("uploadFinanceDocument sends FormData", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ doc_id: "d1" }),
    });
    const { uploadFinanceDocument } = require("@/lib/api");
    const file = new File(["data"], "report.csv", { type: "text/csv" });
    const result = await uploadFinanceDocument("org-1", file);
    expect(mockFetch.mock.calls[0][0]).toContain("/api/finance/upload?org_id=org-1");
    expect(mockFetch.mock.calls[0][1].method).toBe("POST");
    expect(result.doc_id).toBe("d1");
  });

  it("getFinanceDocuments fetches documents", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ documents: [{ id: "d1" }] }),
      text: async () => "",
    });
    const { getFinanceDocuments } = require("@/lib/api");
    const result = await getFinanceDocuments("org-1");
    expect(mockFetch.mock.calls[0][0]).toContain("/api/finance/org-1/documents");
    expect(result.documents).toHaveLength(1);
  });

  it("getFinanceInsights fetches AI insights", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ insights: ["Cash flow positive"] }),
      text: async () => "",
    });
    const { getFinanceInsights } = require("@/lib/api");
    const result = await getFinanceInsights("org-1");
    expect(mockFetch.mock.calls[0][0]).toContain("/api/finance/org-1/insights");
    expect(result.insights).toHaveLength(1);
  });

  it("getFinanceAnalytics fetches analytics data", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ total_revenue: 50000 }),
      text: async () => "",
    });
    const { getFinanceAnalytics } = require("@/lib/api");
    const result = await getFinanceAnalytics("org-1");
    expect(mockFetch.mock.calls[0][0]).toContain("/api/finance/org-1/analytics");
    expect(result.total_revenue).toBe(50000);
  });

  it("getCashflow passes period and date params", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ cashflow: [] }),
      text: async () => "",
    });
    const { getCashflow } = require("@/lib/api");
    await getCashflow("org-1", "weekly", "2025-01-01", "2025-03-01");
    const url = mockFetch.mock.calls[0][0];
    expect(url).toContain("/api/finance/org-1/cashflow");
    expect(url).toContain("period=weekly");
    expect(url).toContain("start_date=2025-01-01");
    expect(url).toContain("end_date=2025-03-01");
  });

  it("getPnl fetches profit and loss", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ net_profit: 12000 }),
      text: async () => "",
    });
    const { getPnl } = require("@/lib/api");
    const result = await getPnl("org-1");
    expect(mockFetch.mock.calls[0][0]).toContain("/api/finance/org-1/pnl");
    expect(result.net_profit).toBe(12000);
  });

  it("getReviewQueue fetches review items", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ queue: [] }),
      text: async () => "",
    });
    const { getReviewQueue } = require("@/lib/api");
    await getReviewQueue("org-1");
    expect(mockFetch.mock.calls[0][0]).toContain("/api/finance/org-1/review-queue");
  });

  it("updateReviewStatus sends PUT with action", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ updated: true }),
      text: async () => "",
    });
    const { updateReviewStatus } = require("@/lib/api");
    await updateReviewStatus("org-1", "sig-1", "approve", { amount: 500 });
    const call = mockFetch.mock.calls[0];
    expect(call[0]).toContain("/api/finance/org-1/review/sig-1");
    expect(call[1].method).toBe("PUT");
    const body = JSON.parse(call[1].body);
    expect(body.action).toBe("approve");
    expect(body.edits.amount).toBe(500);
  });

  it("exportFinanceCsv returns blob", async () => {
    const fakeBlob = new Blob(["csv,data"], { type: "text/csv" });
    mockFetch.mockResolvedValueOnce({
      ok: true,
      blob: async () => fakeBlob,
    });
    const { exportFinanceCsv } = require("@/lib/api");
    const result = await exportFinanceCsv("org-1");
    expect(mockFetch.mock.calls[0][0]).toContain("/api/finance/org-1/export/csv");
    expect(result).toBeInstanceOf(Blob);
  });

  it("exportFinanceXlsx returns blob with filters", async () => {
    const fakeBlob = new Blob(["xlsx"], { type: "application/octet-stream" });
    mockFetch.mockResolvedValueOnce({
      ok: true,
      blob: async () => fakeBlob,
    });
    const { exportFinanceXlsx } = require("@/lib/api");
    await exportFinanceXlsx("org-1", "2025-01-01", "2025-03-01", "invoice");
    const url = mockFetch.mock.calls[0][0];
    expect(url).toContain("/api/finance/org-1/export/xlsx");
    expect(url).toContain("category=invoice");
  });

  it("reconcileDocuments sends file for reconciliation", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ matched: 5, unmatched: 1 }),
    });
    const { reconcileDocuments } = require("@/lib/api");
    const file = new File(["data"], "bank.csv", { type: "text/csv" });
    const result = await reconcileDocuments("org-1", file);
    expect(mockFetch.mock.calls[0][0]).toContain("/api/finance/org-1/reconcile");
    expect(result.matched).toBe(5);
  });
});

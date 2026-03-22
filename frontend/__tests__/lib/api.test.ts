/**
 * Tests for the API client utility functions.
 * These verify the client constructs correct URLs and handles errors.
 */
export {};

// Mock global fetch
const mockFetch = jest.fn();
global.fetch = mockFetch;

// Reset modules so api.ts picks up our mock
beforeEach(() => {
  jest.resetModules();
  mockFetch.mockReset();
});

describe("API Client", () => {
  it("getNSI calls correct endpoint with org_id", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ nsi: { nsi_score: 72 } }),
      text: async () => "",
    });

    const { getNSI } = require("@/lib/api");
    const result = await getNSI("org-123");

    expect(mockFetch).toHaveBeenCalledWith(
      expect.stringContaining("/api/stability/org-123"),
      expect.any(Object)
    );
    expect(result.nsi.nsi_score).toBe(72);
  });

  it("getActions calls correct endpoint", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ actions: [] }),
      text: async () => "",
    });

    const { getActions } = require("@/lib/api");
    const result = await getActions("org-456");

    expect(mockFetch).toHaveBeenCalledWith(
      expect.stringContaining("/api/actions/org-456"),
      expect.any(Object)
    );
    expect(result.actions).toEqual([]);
  });

  it("throws on non-ok response", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 500,
      statusText: "Internal Server Error",
      text: async () => "server error",
    });

    const { getNSI } = require("@/lib/api");
    await expect(getNSI("org-123")).rejects.toThrow(/API error 500/);
  });

  it("uploadInvoice sends FormData", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ signal_id: "sig-1" }),
    });

    const { uploadInvoice } = require("@/lib/api");
    const file = new File(["test"], "invoice.pdf", { type: "application/pdf" });
    const result = await uploadInvoice("org-123", file);

    expect(mockFetch).toHaveBeenCalledWith(
      expect.stringContaining("/api/invoices/upload?org_id=org-123"),
      expect.objectContaining({ method: "POST" })
    );
    expect(result.signal_id).toBe("sig-1");
  });

  it("simulateStrategies posts to correct endpoint", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ strategies: [{ strategy_id: "s1" }] }),
      text: async () => "",
    });

    const { simulateStrategies } = require("@/lib/api");
    const result = await simulateStrategies("org-789");

    expect(mockFetch).toHaveBeenCalledWith(
      expect.stringContaining("/api/strategy/simulate"),
      expect.objectContaining({ method: "POST" })
    );
    expect(result.strategies).toHaveLength(1);
  });

  it("searchMemory posts query and org_id", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ results: [] }),
      text: async () => "",
    });

    const { searchMemory } = require("@/lib/api");
    await searchMemory("org-123", "overdue invoices", 5);

    const call = mockFetch.mock.calls[0];
    expect(call[0]).toContain("/api/memory/search");
    const body = JSON.parse(call[1].body);
    expect(body.query).toBe("overdue invoices");
    expect(body.org_id).toBe("org-123");
    expect(body.limit).toBe(5);
  });
});

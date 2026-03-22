/**
 * Tests for Voice API client functions.
 * Verifies correct endpoint URLs, HTTP methods, and response handling.
 */
export {};

const mockFetch = jest.fn();
global.fetch = mockFetch;

beforeEach(() => {
  jest.resetModules();
  mockFetch.mockReset();
});

describe("Voice API", () => {
  it("getVoiceSummary fetches org summary", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ summary: "Business is healthy" }),
      text: async () => "",
    });
    const { getVoiceSummary } = require("@/lib/api");
    const result = await getVoiceSummary("org-1");
    expect(mockFetch.mock.calls[0][0]).toContain("/api/voice/org-1/summary");
    expect(result.summary).toBe("Business is healthy");
  });

  it("askVoiceQuestion posts question", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ answer: "Score is 72", source: "ai" }),
    });
    const { askVoiceQuestion } = require("@/lib/api");
    const result = await askVoiceQuestion("org-1", "What is my NSI?");
    const call = mockFetch.mock.calls[0];
    expect(call[0]).toContain("/api/voice/org-1/ask");
    expect(call[1].method).toBe("POST");
    const body = JSON.parse(call[1].body);
    expect(body.question).toBe("What is my NSI?");
    expect(result.source).toBe("ai");
  });

  it("askVoiceQuestion throws on failure", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 500,
      statusText: "Internal Server Error",
    });
    const { askVoiceQuestion } = require("@/lib/api");
    await expect(askVoiceQuestion("org-1", "test")).rejects.toThrow(/Voice query failed/);
  });

  it("getVoiceBrief returns json", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ audio_url: "https://example.com/brief.wav", transcript: "All good" }),
    });
    const { getVoiceBrief } = require("@/lib/api");
    const result = await getVoiceBrief("org-1");
    expect(mockFetch.mock.calls[0][0]).toContain("/api/voice/brief");
    expect(result.transcript).toBe("All good");
  });

  it("getBusinessInsights fetches insights", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ insights: ["Revenue up 10%"] }),
      text: async () => "",
    });
    const { getBusinessInsights } = require("@/lib/api");
    const result = await getBusinessInsights("org-1");
    expect(mockFetch.mock.calls[0][0]).toContain("/api/insights/org-1");
    expect(result.insights).toHaveLength(1);
  });
});

/**
 * Tests for Email & Task API client functions.
 * Verifies correct endpoint URLs, HTTP methods, and request bodies.
 */

const mockFetch = jest.fn();
global.fetch = mockFetch;

beforeEach(() => {
  jest.resetModules();
  mockFetch.mockReset();
});

describe("Email API", () => {
  it("ingestEmail posts email data", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ signal_id: "sig-e1" }),
      text: async () => "",
    });
    const { ingestEmail } = require("@/lib/api");
    const result = await ingestEmail("org-1", "Invoice Due", "Please pay", "vendor@example.com");
    const call = mockFetch.mock.calls[0];
    expect(call[0]).toContain("/api/emails/ingest");
    const body = JSON.parse(call[1].body);
    expect(body.org_id).toBe("org-1");
    expect(body.subject).toBe("Invoice Due");
    expect(body.sender).toBe("vendor@example.com");
    expect(result.signal_id).toBe("sig-e1");
  });

  it("getEmails fetches org emails", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ emails: [{ id: "e1" }] }),
      text: async () => "",
    });
    const { getEmails } = require("@/lib/api");
    const result = await getEmails("org-1");
    expect(mockFetch).toHaveBeenCalledWith(
      expect.stringContaining("/api/emails/org-1"),
      expect.any(Object)
    );
    expect(result.emails).toHaveLength(1);
  });

  it("generateEmailReply posts with tone", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ reply: "Dear vendor..." }),
      text: async () => "",
    });
    const { generateEmailReply } = require("@/lib/api");
    await generateEmailReply("org-1", "sig-1", "friendly");
    const call = mockFetch.mock.calls[0];
    expect(call[0]).toContain("/api/emails/org-1/sig-1/reply");
    expect(JSON.parse(call[1].body).tone).toBe("friendly");
  });

  it("getTasks fetches with optional filters", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ tasks: [] }),
      text: async () => "",
    });
    const { getTasks } = require("@/lib/api");
    await getTasks("org-1", "pending", "high");
    expect(mockFetch.mock.calls[0][0]).toContain("status=pending");
    expect(mockFetch.mock.calls[0][0]).toContain("priority=high");
  });

  it("createTask posts task data", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ task_id: "t1" }),
      text: async () => "",
    });
    const { createTask } = require("@/lib/api");
    const result = await createTask("org-1", { title: "Follow up", priority: "high" });
    const call = mockFetch.mock.calls[0];
    expect(call[0]).toContain("/api/emails/org-1/tasks");
    expect(call[1].method).toBe("POST");
    expect(result.task_id).toBe("t1");
  });

  it("updateTaskStatus sends PUT with status", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ updated: true }),
      text: async () => "",
    });
    const { updateTaskStatus } = require("@/lib/api");
    await updateTaskStatus("org-1", "t1", "completed", "Done");
    const call = mockFetch.mock.calls[0];
    expect(call[0]).toContain("/api/emails/org-1/tasks/t1");
    expect(call[1].method).toBe("PUT");
    const body = JSON.parse(call[1].body);
    expect(body.status).toBe("completed");
    expect(body.result).toBe("Done");
  });

  it("sendEmail posts email via SES", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ message_id: "m1" }),
      text: async () => "",
    });
    const { sendEmail } = require("@/lib/api");
    const result = await sendEmail("org-1", "to@example.com", "Hi", "Body text");
    const call = mockFetch.mock.calls[0];
    expect(call[0]).toContain("/api/emails/org-1/send");
    expect(result.message_id).toBe("m1");
  });

  it("getSesStatus fetches SES status", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ sandbox: true }),
      text: async () => "",
    });
    const { getSesStatus } = require("@/lib/api");
    const result = await getSesStatus();
    expect(mockFetch.mock.calls[0][0]).toContain("/api/emails/ses/status");
    expect(result.sandbox).toBe(true);
  });

  it("verifySesEmail posts verification request", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ status: "pending" }),
      text: async () => "",
    });
    const { verifySesEmail } = require("@/lib/api");
    await verifySesEmail("test@example.com");
    expect(mockFetch.mock.calls[0][0]).toContain("/api/emails/ses/verify");
    expect(mockFetch.mock.calls[0][0]).toContain("test%40example.com");
  });
});

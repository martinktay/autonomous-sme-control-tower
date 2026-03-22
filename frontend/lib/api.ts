/**
 * @file API client for the SME Control Tower frontend.
 * Centralises all backend HTTP calls behind typed async functions.
 * Each function targets a FastAPI endpoint and returns parsed JSON (or Blob).
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

/** Read the JWT from localStorage (set by AuthProvider). */
function getAuthToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('sme_access_token');
}

/** Build auth headers object for direct fetch calls. */
function authHeaders(extra: Record<string, string> = {}): Record<string, string> {
  const token = getAuthToken();
  return {
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...extra,
  };
}

/** Internal fetch wrapper with configurable timeout, JSON headers, auth, and error handling. */
async function apiFetch(path: string, options: RequestInit = {}, timeoutMs = 8000) {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

  const token = getAuthToken();
  const authHeaders: Record<string, string> = token ? { Authorization: `Bearer ${token}` } : {};

  try {
    const res = await fetch(`${API_BASE_URL}${path}`, {
      headers: {
        'Content-Type': 'application/json',
        ...authHeaders,
        ...(options.headers as Record<string, string>),
      },
      ...options,
      signal: controller.signal,
    });

    if (!res.ok) {
      const text = await res.text().catch(() => res.statusText);
      throw new Error(`API error ${res.status}: ${text}`);
    }

    return res;
  } catch (err: any) {
    if (err.name === 'AbortError') {
      throw new Error('Request timed out — is the backend running?');
    }
    throw err;
  } finally {
    clearTimeout(timeoutId);
  }
}

// ==================== NSI & Stability API ====================

/** Fetch the Nova Stability Index and sub-indices for an org. */
export const getNSI = async (orgId: string) => {
  const res = await apiFetch(`/api/stability/${orgId}`);
  return res.json();
};

/** Fetch top operational risks extracted from the stability payload. */
export const getRisks = async (orgId: string) => {
  const res = await apiFetch(`/api/stability/${orgId}`);
  const data = await res.json();
  return { risks: data.nsi?.top_risks || [] };
};

// ==================== Actions & Orchestration API ====================

/** Fetch the list of autonomous actions executed for an org. */
export const getActions = async (orgId: string) => {
  const res = await apiFetch(`/api/actions/${orgId}`);
  return res.json();
};

/** Trigger the full closed-loop orchestration cycle (ingest → diagnose → act). */
export const runClosedLoop = async (orgId: string) => {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 120000); // 2 min for multi-step Bedrock calls
  try {
    const res = await fetch(`${API_BASE_URL}/api/orchestration/run-loop`, {
      method: 'POST',
      headers: authHeaders({ 'Content-Type': 'application/json' }),
      body: JSON.stringify({ org_id: orgId }),
      signal: controller.signal,
    });
    if (!res.ok) {
      const text = await res.text().catch(() => res.statusText);
      throw new Error(`API error ${res.status}: ${text}`);
    }
    return res.json();
  } catch (err: any) {
    if (err.name === 'AbortError') throw new Error('Analysis is taking longer than expected. Please try again.');
    throw err;
  } finally {
    clearTimeout(timeoutId);
  }
};

// ==================== Invoice Upload API ====================

/** Upload an invoice file (PDF/image) via multipart form data. */
export const uploadInvoice = async (orgId: string, file: File) => {
  const formData = new FormData();
  formData.append('file', file);
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 30000);
  try {
    const res = await fetch(`${API_BASE_URL}/api/invoices/upload?org_id=${orgId}`, {
      method: 'POST',
      headers: authHeaders(),
      body: formData,
      signal: controller.signal,
    });
    if (!res.ok) {
      const body = await res.text().catch(() => '');
      throw new Error(body || `Upload failed: ${res.statusText}`);
    }
    return res.json();
  } catch (err: any) {
    if (err.name === 'AbortError') throw new Error('Upload timed out. Please try again.');
    if (err.message === 'Failed to fetch') throw new Error('Cannot reach the backend server. Make sure it is running on port 8000.');
    throw err;
  } finally {
    clearTimeout(timeout);
  }
};

// ==================== Strategy & Memory API ====================

/** Run AI strategy simulation for the org. */
export const simulateStrategies = async (orgId: string) => {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 90000); // 90s for Bedrock calls
  try {
    const res = await fetch(`${API_BASE_URL}/api/strategy/simulate`, {
      method: 'POST',
      headers: authHeaders({ 'Content-Type': 'application/json' }),
      body: JSON.stringify({ org_id: orgId }),
      signal: controller.signal,
    });
    if (!res.ok) {
      const text = await res.text().catch(() => res.statusText);
      throw new Error(`API error ${res.status}: ${text}`);
    }
    return res.json();
  } catch (err: any) {
    if (err.name === 'AbortError') throw new Error('Strategy simulation is taking longer than expected. Please try again.');
    throw err;
  } finally {
    clearTimeout(timeoutId);
  }
};

/** Semantic search across the org's business memory. */
export const searchMemory = async (orgId: string, query: string, limit = 10) => {
  const res = await apiFetch('/api/memory/search', {
    method: 'POST',
    body: JSON.stringify({ query, org_id: orgId, limit }),
  });
  return res.json();
};

// ==================== Voice API ====================

/** Fetch a text-based voice summary for the org. */
export const getVoiceSummary = async (orgId: string) => {
  const res = await apiFetch(`/api/voice/${orgId}/summary`);
  return res.json();
};

// ==================== Insights API ====================

/** Fetch AI-generated business insights for the org. */
export const getBusinessInsights = async (orgId: string) => {
  const res = await apiFetch(`/api/insights/${orgId}`);
  return res.json();
};

/** Get an audio briefing blob (Nova Sonic) for the org. */
export const getVoiceBrief = async (orgId: string) => {
  const res = await fetch(`${API_BASE_URL}/api/voice/brief`, {
    method: 'POST',
    headers: authHeaders({ 'Content-Type': 'application/json' }),
    body: JSON.stringify({ org_id: orgId }),
  });
  if (!res.ok) throw new Error(`Voice brief failed: ${res.statusText}`);
  return res.json();
};

/** Ask a free-form voice question and get a JSON answer. */
export const askVoiceQuestion = async (orgId: string, question: string) => {
  const res = await fetch(`${API_BASE_URL}/api/voice/${orgId}/ask`, {
    method: 'POST',
    headers: authHeaders({ 'Content-Type': 'application/json' }),
    body: JSON.stringify({ org_id: orgId, question }),
  });
  if (!res.ok) throw new Error(`Voice query failed: ${res.statusText}`);
  return res.json();
};

// ==================== Finance API ====================

// ==================== Finance Document API ====================

/** Upload a financial document (invoice, receipt, spreadsheet). */
export const uploadFinanceDocument = async (orgId: string, file: File) => {
  const formData = new FormData();
  formData.append('file', file);
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 30000);
  try {
    const res = await fetch(`${API_BASE_URL}/api/finance/upload?org_id=${orgId}`, {
      method: 'POST',
      headers: authHeaders(),
      body: formData,
      signal: controller.signal,
    });
    if (!res.ok) {
      const body = await res.text().catch(() => '');
      // Try to extract detail from JSON error response
      try {
        const err = JSON.parse(body);
        throw new Error(err.detail || `Upload failed: ${res.statusText}`);
      } catch {
        throw new Error(body || `Upload failed: ${res.statusText}`);
      }
    }
    return res.json();
  } catch (err: any) {
    if (err.name === 'AbortError') throw new Error('Upload timed out. Please try again.');
    if (err.message === 'Failed to fetch') throw new Error('Cannot reach the backend server. Make sure it is running on port 8000.');
    throw err;
  } finally {
    clearTimeout(timeout);
  }
};

/** List all processed finance documents for the org. */
export const getFinanceDocuments = async (orgId: string) => {
  const res = await apiFetch(`/api/finance/${orgId}/documents`, {}, 30000);
  return res.json();
};

/** Fetch AI-generated financial insights (tax, cashflow, profitability). */
export const getFinanceInsights = async (orgId: string) => {
  const res = await apiFetch(`/api/finance/${orgId}/insights`, {}, 30000);
  return res.json();
};

/** Fetch analytics aggregations (charts, KPIs, breakdowns). */
export const getFinanceAnalytics = async (orgId: string) => {
  const res = await apiFetch(`/api/finance/${orgId}/analytics`, {}, 30000);
  return res.json();
};

/** Fetch cashflow data with optional period and date range filters. */
export const getCashflow = async (orgId: string, period = 'monthly', startDate?: string, endDate?: string) => {
  const params = new URLSearchParams({ period });
  if (startDate) params.set('start_date', startDate);
  if (endDate) params.set('end_date', endDate);
  const res = await apiFetch(`/api/finance/${orgId}/cashflow?${params}`, {}, 30000);
  return res.json();
};

/** Fetch profit-and-loss summary with optional date range. */
export const getPnl = async (orgId: string, startDate?: string, endDate?: string) => {
  const params = new URLSearchParams();
  if (startDate) params.set('start_date', startDate);
  if (endDate) params.set('end_date', endDate);
  const qs = params.toString();
  const res = await apiFetch(`/api/finance/${orgId}/pnl${qs ? `?${qs}` : ''}`, {}, 30000);
  return res.json();
};

/** Upload a bank statement to reconcile against existing documents. */
export const reconcileDocuments = async (orgId: string, file: File) => {
  const formData = new FormData();
  formData.append('file', file);
  const res = await fetch(`${API_BASE_URL}/api/finance/${orgId}/reconcile`, {
    method: 'POST',
    headers: authHeaders(),
    body: formData,
  });
  if (!res.ok) throw new Error(`Reconciliation failed: ${res.statusText}`);
  return res.json();
};

/** Fetch documents pending human review. */
export const getReviewQueue = async (orgId: string) => {
  const res = await apiFetch(`/api/finance/${orgId}/review-queue`, {}, 30000);
  return res.json();
};

/** Approve or reject a document in the review queue. */
export const updateReviewStatus = async (orgId: string, signalId: string, action: string, edits?: Record<string, any>) => {
  const res = await apiFetch(`/api/finance/${orgId}/review/${signalId}`, {
    method: 'PUT',
    body: JSON.stringify({ action, edits }),
  });
  return res.json();
};

// ==================== Finance Export API ====================

/** Download finance data as a CSV blob. */
export const exportFinanceCsv = async (orgId: string, startDate?: string, endDate?: string, category?: string) => {
  const params = new URLSearchParams();
  if (startDate) params.set('start_date', startDate);
  if (endDate) params.set('end_date', endDate);
  if (category) params.set('category', category);
  const qs = params.toString();
  const res = await fetch(`${API_BASE_URL}/api/finance/${orgId}/export/csv${qs ? `?${qs}` : ''}`, { headers: authHeaders() });
  if (!res.ok) throw new Error(`Export failed: ${res.statusText}`);
  return res.blob();
};

/** Download finance data as an XLSX blob. */
export const exportFinanceXlsx = async (orgId: string, startDate?: string, endDate?: string, category?: string) => {
  const params = new URLSearchParams();
  if (startDate) params.set('start_date', startDate);
  if (endDate) params.set('end_date', endDate);
  if (category) params.set('category', category);
  const qs = params.toString();
  const res = await fetch(`${API_BASE_URL}/api/finance/${orgId}/export/xlsx${qs ? `?${qs}` : ''}`, { headers: authHeaders() });
  if (!res.ok) throw new Error(`Export failed: ${res.statusText}`);
  return res.blob();
};

// ==================== Email & Tasks API ====================

/** Ingest a new email into the system for AI processing. */
export const ingestEmail = async (orgId: string, subject: string, body: string, sender: string) => {
  const res = await apiFetch('/api/emails/ingest', {
    method: 'POST',
    body: JSON.stringify({ org_id: orgId, subject, body, sender }),
  });
  return res.json();
};

/** Fetch all ingested emails for the org. */
export const getEmails = async (orgId: string) => {
  const res = await apiFetch(`/api/emails/${orgId}`);
  return res.json();
};

/** Generate an AI-drafted reply for a specific email signal. */
export const generateEmailReply = async (orgId: string, signalId: string, tone = 'professional') => {
  const res = await apiFetch(`/api/emails/${orgId}/${signalId}/reply`, {
    method: 'POST',
    body: JSON.stringify({ tone }),
  });
  return res.json();
};

/** Fetch tasks with optional status/priority filters. */
export const getTasks = async (orgId: string, status?: string, priority?: string) => {
  const params = new URLSearchParams();
  if (status) params.set('status', status);
  if (priority) params.set('priority', priority);
  const qs = params.toString();
  const res = await apiFetch(`/api/emails/${orgId}/tasks${qs ? `?${qs}` : ''}`);
  return res.json();
};

/** Create a new task (manual or AI-extracted). */
export const createTask = async (orgId: string, data: { title: string; description?: string; task_type?: string; priority?: string; due_date?: string }) => {
  const res = await apiFetch(`/api/emails/${orgId}/tasks`, {
    method: 'POST',
    body: JSON.stringify(data),
  });
  return res.json();
};

/** Update a task's status (e.g. pending → completed). */
export const updateTaskStatus = async (orgId: string, taskId: string, status: string, result?: string) => {
  const res = await apiFetch(`/api/emails/${orgId}/tasks/${taskId}`, {
    method: 'PUT',
    body: JSON.stringify({ status, result }),
  });
  return res.json();
};

// ==================== SES Email Sending ====================

/** Send an email via Amazon SES. */
export const sendEmail = async (orgId: string, to: string, subject: string, body: string, replyTo?: string) => {
  const res = await apiFetch(`/api/emails/${orgId}/send`, {
    method: 'POST',
    body: JSON.stringify({ to, subject, body, reply_to: replyTo }),
  });
  return res.json();
};

/** Check SES sandbox/production status. */
export const getSesStatus = async () => {
  const res = await apiFetch('/api/emails/ses/status');
  return res.json();
};

/** Request SES identity verification for an email address. */
export const verifySesEmail = async (email: string) => {
  const res = await apiFetch(`/api/emails/ses/verify?email=${encodeURIComponent(email)}`, {
    method: 'POST',
  });
  return res.json();
};

// ─── Business & Onboarding ───────────────────────────────────────────────────

export const createBusiness = async (data: {
  business_name: string;
  business_type?: string;
  country?: string;
  state_region?: string;
  currency?: string;
  phone?: string;
  email?: string;
}) => {
  return apiFetch('/api/businesses', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
};

export const getBusiness = async (businessId: string) => {
  return apiFetch(`/api/businesses/${businessId}`);
};

export const updateBusiness = async (businessId: string, data: Record<string, any>) => {
  return apiFetch(`/api/businesses/${businessId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
};

export const completeOnboarding = async (businessId: string) => {
  return apiFetch(`/api/businesses/${businessId}/onboarding/complete`, { method: 'POST' });
};

export const listBranches = async (businessId: string) => {
  return apiFetch(`/api/businesses/${businessId}/branches`);
};

export const createBranch = async (businessId: string, data: { branch_name: string; address?: string }) => {
  return apiFetch(`/api/businesses/${businessId}/branches`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
};

// ─── Pricing ─────────────────────────────────────────────────────────────────

export const getPricingTiers = async () => {
  return apiFetch('/api/pricing/tiers');
};

export const getCurrentTier = async (businessId: string) => {
  return apiFetch(`/api/pricing/current/${businessId}`);
};

// ─── Inventory ───────────────────────────────────────────────────────────────

export const getInventory = async (orgId: string) => {
  return apiFetch('/api/inventory', { headers: { 'X-Org-ID': orgId } });
};

export const createInventoryItem = async (orgId: string, data: Record<string, any>) => {
  return apiFetch('/api/inventory', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'X-Org-ID': orgId },
    body: JSON.stringify(data),
  });
};

export const updateInventoryItem = async (orgId: string, itemId: string, data: Record<string, any>) => {
  return apiFetch(`/api/inventory/${itemId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json', 'X-Org-ID': orgId },
    body: JSON.stringify(data),
  });
};

export const getStockAlerts = async (orgId: string) => {
  return apiFetch('/api/inventory/alerts', { headers: { 'X-Org-ID': orgId } });
};

export const getInventoryAnalytics = async (orgId: string) => {
  return apiFetch('/api/inventory/analytics', { headers: { 'X-Org-ID': orgId } });
};

// ─── Transactions ────────────────────────────────────────────────────────────

export const getTransactions = async (orgId: string) => {
  return apiFetch('/api/transactions', { headers: { 'X-Org-ID': orgId } });
};

export const createTransaction = async (orgId: string, data: Record<string, any>) => {
  return apiFetch('/api/transactions', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'X-Org-ID': orgId },
    body: JSON.stringify(data),
  });
};

export const getTransactionSummary = async (orgId: string) => {
  return apiFetch('/api/transactions/summary', { headers: { 'X-Org-ID': orgId } });
};

export const getTransactionCashflow = async (orgId: string) => {
  return apiFetch('/api/transactions/cashflow', { headers: { 'X-Org-ID': orgId } });
};

// ─── Counterparties (Suppliers/Customers) ────────────────────────────────────

export const getCounterparties = async (orgId: string) => {
  return apiFetch('/api/counterparties', { headers: { 'X-Org-ID': orgId } });
};

export const createCounterparty = async (orgId: string, data: { name: string; counterparty_type: string; phone?: string; email?: string }) => {
  return apiFetch('/api/counterparties', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'X-Org-ID': orgId },
    body: JSON.stringify(data),
  });
};

export const getCounterpartyBalance = async (orgId: string, counterpartyId: string) => {
  return apiFetch(`/api/counterparties/${counterpartyId}/balance`, { headers: { 'X-Org-ID': orgId } });
};

// ─── Alerts ──────────────────────────────────────────────────────────────────

export const getAlerts = async (orgId: string) => {
  return apiFetch('/api/alerts', { headers: { 'X-Org-ID': orgId } });
};

export const markAlertRead = async (orgId: string, alertId: string) => {
  return apiFetch(`/api/alerts/${alertId}/read`, {
    method: 'PUT',
    headers: { 'X-Org-ID': orgId },
  });
};

// ─── WhatsApp ────────────────────────────────────────────────────────────────

/** Ingest a WhatsApp message for AI processing. */
export const ingestWhatsAppMessage = async (orgId: string, messageText: string, senderName?: string, senderPhone?: string) => {
  const res = await apiFetch('/api/whatsapp/ingest', {
    method: 'POST',
    body: JSON.stringify({ org_id: orgId, message_text: messageText, sender_name: senderName, sender_phone: senderPhone }),
  });
  return res.json();
};

/** Generate a WhatsApp-friendly business insight summary. */
export const getWhatsAppSummary = async (orgId: string, businessName?: string) => {
  const res = await apiFetch('/api/whatsapp/summary', {
    method: 'POST',
    body: JSON.stringify({ org_id: orgId, business_name: businessName }),
  });
  return res.json();
};

/** List processed WhatsApp messages for an org. */
export const getWhatsAppMessages = async (orgId: string) => {
  const res = await apiFetch(`/api/whatsapp/${orgId}/messages`);
  return res.json();
};


// ─── Desktop Sync ────────────────────────────────────────────────────────────

/** Upload a POS export file for AI extraction. */
export const uploadSyncFile = async (orgId: string, file: File, businessName?: string) => {
  const formData = new FormData();
  formData.append('file', file);
  const params = new URLSearchParams();
  if (businessName) params.set('business_name', businessName);
  const qs = params.toString();
  const res = await fetch(`${API_BASE_URL}/api/desktop-sync/upload${qs ? `?${qs}` : ''}`, {
    method: 'POST',
    headers: authHeaders({ 'X-Org-ID': orgId }),
    body: formData,
  });
  if (!res.ok) throw new Error(`Sync upload failed: ${res.statusText}`);
  return res.json();
};

/** Get desktop sync status. */
export const getSyncStatus = async (orgId: string) => {
  const res = await apiFetch('/api/desktop-sync/status', { headers: { 'X-Org-ID': orgId } });
  return res.json();
};

// ─── Supplier Intelligence ───────────────────────────────────────────────────

/** Get full AI supplier intelligence report. */
export const getSupplierReport = async (orgId: string) => {
  const res = await apiFetch(`/api/supplier-intelligence/${orgId}/report`, {}, 30000);
  return res.json();
};

/** Get quick supplier reliability scores. */
export const getSupplierScores = async (orgId: string) => {
  const res = await apiFetch(`/api/supplier-intelligence/${orgId}/scores`);
  return res.json();
};

// ─── Inventory Predictions ───────────────────────────────────────────────────

/** Get AI demand forecast with predictions and seasonal insights. */
export const getDemandForecast = async (orgId: string) => {
  const res = await apiFetch(`/api/predictions/${orgId}/demand`, {}, 30000);
  return res.json();
};

/** Get quick reorder suggestions based on stock and sales velocity. */
export const getReorderSuggestions = async (orgId: string) => {
  const res = await apiFetch(`/api/predictions/${orgId}/reorder`);
  return res.json();
};

// ─── POS Connector ───────────────────────────────────────────────────────────

/** Import a POS export file for AI extraction. */
export const importPosData = async (orgId: string, file: File, posSystem?: string) => {
  const formData = new FormData();
  formData.append('file', file);
  const params = new URLSearchParams();
  if (posSystem) params.set('pos_system', posSystem);
  const qs = params.toString();
  const res = await fetch(`${API_BASE_URL}/api/pos/import${qs ? `?${qs}` : ''}`, {
    method: 'POST',
    headers: authHeaders({ 'X-Org-ID': orgId }),
    body: formData,
  });
  if (!res.ok) throw new Error(`POS import failed: ${res.statusText}`);
  return res.json();
};

/** List supported POS systems. */
export const getSupportedPosSystems = async () => {
  const res = await apiFetch('/api/pos/systems');
  return res.json();
};

// ─── Bank Sync ───────────────────────────────────────────────────────────────

/** Import a bank statement for reconciliation. */
export const importBankStatement = async (orgId: string, file: File) => {
  const formData = new FormData();
  formData.append('file', file);
  const res = await fetch(`${API_BASE_URL}/api/bank-sync/import`, {
    method: 'POST',
    headers: authHeaders({ 'X-Org-ID': orgId }),
    body: formData,
  });
  if (!res.ok) throw new Error(`Bank import failed: ${res.statusText}`);
  return res.json();
};

/** List supported banks. */
export const getSupportedBanks = async () => {
  const res = await apiFetch('/api/bank-sync/supported-banks');
  return res.json();
};

// ─── AI Forecasting ──────────────────────────────────────────────────────────

/** Get AI revenue/expense/cash runway forecast. */
export const getFinanceForecast = async (orgId: string) => {
  const res = await apiFetch(`/api/forecasting/${orgId}/forecast`, {}, 30000);
  return res.json();
};

/** Get quick cash runway calculation. */
export const getCashRunway = async (orgId: string) => {
  const res = await apiFetch(`/api/forecasting/${orgId}/cash-runway`);
  return res.json();
};

// ─── Cross-Branch Optimisation ───────────────────────────────────────────────

/** Get AI cross-branch optimisation report. */
export const getBranchOptimisation = async (orgId: string) => {
  const res = await apiFetch(`/api/branches/${orgId}/optimise`, {}, 30000);
  return res.json();
};

/** Get branch benchmarks. */
export const getBranchBenchmarks = async (orgId: string) => {
  const res = await apiFetch(`/api/branches/${orgId}/benchmarks`);
  return res.json();
};

// ==================== Unified Client ====================

/** Object-style export bundling all API functions for convenient dashboard imports. */
export const apiClient = {
  getNSI,
  getRisks,
  getActions,
  runClosedLoop,
  uploadInvoice,
  simulateStrategies,
  searchMemory,
  getVoiceSummary,
  getVoiceBrief,
  askVoiceQuestion,
  getBusinessInsights,
  uploadFinanceDocument,
  getFinanceDocuments,
  getFinanceInsights,
  getFinanceAnalytics,
  getCashflow,
  getPnl,
  reconcileDocuments,
  getReviewQueue,
  updateReviewStatus,
  exportFinanceCsv,
  exportFinanceXlsx,
  ingestEmail,
  getEmails,
  generateEmailReply,
  getTasks,
  createTask,
  updateTaskStatus,
  sendEmail,
  getSesStatus,
  verifySesEmail,
  getInventory,
  getStockAlerts,
  getInventoryAnalytics,
  getCounterparties,
  getCounterpartyBalance,
  getAlerts,
  markAlertRead,
  getTransactions,
  createTransaction,
  getTransactionSummary,
  getTransactionCashflow,
  createBusiness,
  getBusiness,
  updateBusiness,
  completeOnboarding,
  listBranches,
  createBranch,
  getPricingTiers,
  getCurrentTier,
  createInventoryItem,
  updateInventoryItem,
  createCounterparty,
  ingestWhatsAppMessage,
  getWhatsAppSummary,
  getWhatsAppMessages,
  uploadSyncFile,
  getSyncStatus,
  getSupplierReport,
  getSupplierScores,
  getDemandForecast,
  getReorderSuggestions,
  importPosData,
  getSupportedPosSystems,
  importBankStatement,
  getSupportedBanks,
  getFinanceForecast,
  getCashRunway,
  getBranchOptimisation,
  getBranchBenchmarks,
};

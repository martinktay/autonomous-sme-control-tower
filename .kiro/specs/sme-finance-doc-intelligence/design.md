# SME Finance Document Intelligence Platform - Technical Design

## Architecture Overview

The Finance Document Intelligence Platform extends the existing Autonomous SME Control Tower by adding a dedicated finance processing pipeline alongside the existing signal pipeline. It introduces new backend agents, a new finance router, new Pydantic models, new prompt templates, and new frontend pages/components — all integrated with the existing S3, DynamoDB, and Bedrock infrastructure.

### System Extension Points

```
Existing System                          New Finance Layer
─────────────────                        ─────────────────
Signal Agent (invoice/email)      →      Finance Document Agent (OCR + extraction + classification)
S3 (invoices/{org_id}/...)        →      S3 (documents/{org_id}/{doc_id}/...)
DynamoDB (signals table)          →      DynamoDB (signals table, signal_type="finance_document")
Upload page (single invoice)      →      Finance Upload page (multi-format, batch-ready)
Dashboard (BSI overview)          →      Finance Dashboard (cashflow, P&L, review queue)
```

---

## Backend

### New Modules

```
backend/app/
├── agents/
│   └── finance_agent.py          # Document processing, classification, VAT extraction, informal parsing
├── routers/
│   └── finance.py                # All /api/finance/* endpoints
├── models/
│   └── finance_document.py       # Finance_Document Pydantic model + supporting models
└── services/
    └── finance_service.py        # Cashflow aggregation, P&L, reconciliation, anomaly detection, CSV export
```


### Finance Document Agent (`backend/app/agents/finance_agent.py`)

Single agent class handling the full document processing pipeline:

```python
class FinanceDocumentAgent:
    """
    Handles OCR extraction, classification, VAT extraction, and informal receipt parsing.
    Uses existing bedrock_client, prompt_loader, and json_guard utilities.
    """

    def __init__(self):
        self.bedrock = get_bedrock_client()

    def extract_document(self, raw_text: str, currency_hint: Optional[str] = None) -> dict:
        """
        Extract structured fields from document text using Nova Lite.
        Loads prompt: finance-document-extraction
        Returns: {vendor_name, amount, currency, document_date, description, vat_amount, vat_rate}
        Req 2.1-2.6, Req 5.1-5.5
        """

    def classify_document(self, extracted_data: dict) -> dict:
        """
        Classify document as revenue or expense with confidence score.
        Loads prompt: finance-document-classification
        Returns: {category, confidence_score}
        Req 3.1-3.5
        """

    def parse_informal_receipt(self, raw_text: str) -> dict:
        """
        Specialized extraction for Nigerian informal documents (POS slips, handwritten receipts).
        Loads prompt: finance-informal-receipt
        Returns: {vendor_name, amount, currency, document_date, description}
        Req 6.1-6.6
        """
```

### Finance Service (`backend/app/services/finance_service.py`)

Business logic layer for aggregation, reconciliation, anomaly detection, and export:

```python
class FinanceService:
    """
    Stateless service operating on DynamoDB data via ddb_service.
    All methods accept org_id as first parameter for tenant isolation.
    """

    def get_cashflow(self, org_id: str, period: str, start_date: datetime, end_date: datetime) -> dict:
        """
        Aggregate revenue/expense totals grouped by period (daily/weekly/monthly).
        Returns: {periods: [{period_label, revenue, expenses}], currency}
        Req 7.1-7.6
        """

    def get_pnl(self, org_id: str, start_date: datetime, end_date: datetime) -> dict:
        """
        Compute P&L summary with optional VAT breakdown.
        Returns: {total_revenue, total_expenses, net_profit, by_vendor: [...], vat_summary: {...}}
        Req 8.1-8.5
        """

    def reconcile(self, org_id: str, bank_csv_content: str) -> dict:
        """
        Parse bank CSV, match against Finance_Documents by amount/date/vendor.
        Returns: {matched: [...], unmatched_transactions: [...], unmatched_documents: [...]}
        Req 9.1-9.7
        """

    def detect_anomalies(self, org_id: str, document: dict) -> list:
        """
        Check for duplicates (same vendor+amount+date) and statistical outliers (>3 sigma).
        Returns: list of {flag_type, flag_reason}
        Req 10.1-10.5
        """

    def get_review_queue(self, org_id: str) -> list:
        """
        Query documents with processing_status="needs_review" for org.
        Returns: list of Finance_Document dicts with review_reason
        Req 11.1-11.6
        """

    def update_review_status(self, org_id: str, signal_id: str, action: str, edits: Optional[dict] = None) -> dict:
        """
        Approve, reject, or edit-and-approve a document in review queue.
        Req 11.2-11.4
        """

    def export_csv(self, org_id: str, start_date: Optional[datetime], end_date: Optional[datetime], category: Optional[str]) -> str:
        """
        Generate CSV string of approved/processed Finance_Documents.
        Returns: CSV string content
        Req 12.1-12.6
        """
```


### Finance Router (`backend/app/routers/finance.py`)

All finance endpoints under `/api/finance`:

```
POST /api/finance/upload?org_id={org_id}          → Upload + process document (Req 1, 2, 3, 4, 5, 6, 10, 14)
GET  /api/finance/{org_id}/documents               → List finance documents (Req 14)
GET  /api/finance/{org_id}/cashflow                 → Cashflow aggregation (Req 7)
     ?period=monthly&start_date=...&end_date=...
GET  /api/finance/{org_id}/pnl                      → P&L summary (Req 8)
     ?start_date=...&end_date=...
POST /api/finance/{org_id}/reconcile                → Bank statement reconciliation (Req 9)
GET  /api/finance/{org_id}/review-queue             → Review queue (Req 11)
PUT  /api/finance/{org_id}/review/{signal_id}       → Approve/reject/edit document (Req 11)
GET  /api/finance/{org_id}/export/csv               → CSV export (Req 12)
     ?start_date=...&end_date=...&category=...
```

### Finance Document Model (`backend/app/models/finance_document.py`)

```python
class DocumentFlag(BaseModel):
    flag_type: str          # "duplicate", "anomaly", "low_confidence", "extraction_failure", "missing_currency"
    flag_reason: str

class FinanceDocument(BaseModel):
    document_id: str        # UUID
    org_id: str
    vendor_name: str
    amount: float           # > 0, validated
    currency: str           # 3-letter ISO 4217, validated
    vat_amount: Optional[float] = 0.0    # >= 0
    vat_rate: Optional[float] = 0.0      # >= 0
    document_date: datetime
    description: str
    category: str           # "revenue" | "expense", validated
    confidence_score: float # 0.0-1.0, validated
    processing_status: str  # "processed" | "needs_review" | "approved" | "rejected" | "failed", validated
    s3_key: str
    created_at: datetime
    flags: Optional[List[DocumentFlag]] = []
    review_reason: Optional[str] = None
```

Req 13.1-13.6 — all field validators as specified.

### Signal Model Extension

The existing `Signal.signal_type` validator needs to accept `"finance_document"` in addition to `"invoice"` and `"email"`:

```python
# backend/app/models/signal.py — update valid_types
valid_types = {'invoice', 'email', 'finance_document'}
```

### Upload Processing Flow

```
1. POST /api/finance/upload
   ├── Validate file type (PDF/JPEG/PNG) and size (<=10MB)
   ├── Generate document_id (UUID)
   ├── Upload to S3: documents/{org_id}/{document_id}/{filename}
   ├── OCR: extract raw text (placeholder for future Textract integration)
   ├── Determine currency_hint from org preferences or extracted text
   │
   ├── IF currency == NGN:
   │   └── finance_agent.parse_informal_receipt(raw_text)
   ├── ELSE:
   │   └── finance_agent.extract_document(raw_text, currency_hint)
   │
   ├── Validate extracted data against FinanceDocument model
   │   ├── IF validation fails → status="failed", add to review queue
   │   └── IF validation passes → continue
   │
   ├── finance_agent.classify_document(extracted_data)
   │   ├── IF confidence < 0.7 → status="needs_review"
   │   └── ELSE → status="processed"
   │
   ├── finance_service.detect_anomalies(org_id, document)
   │   └── IF flags found → status="needs_review", attach flags
   │
   ├── Create Signal(signal_type="finance_document", content=document_data)
   ├── Store in DynamoDB via ddb_service.create_signal()
   └── Return {document_id, status, extracted_data, flags}
```

---

## Frontend

### New Pages

```
frontend/app/
├── finance/
│   └── page.tsx              # Finance dashboard — cashflow chart + P&L summary + quick stats
├── finance/upload/
│   └── page.tsx              # Finance document upload (extends existing upload pattern)
├── finance/review/
│   └── page.tsx              # Review queue — approve/reject/edit documents
└── finance/export/
    └── page.tsx              # Export page — date range + category filter + download CSV
```

### New Components

```
frontend/components/
├── CashflowChart.tsx         # Time-series bar/line chart (revenue vs expenses by period)
├── PnlSummary.tsx            # P&L card with revenue, expenses, net profit, VAT breakdown
├── ReviewQueue.tsx           # Table of documents needing review with action buttons
├── FinanceDocUpload.tsx      # Upload widget with file type validation and progress
└── ReconciliationPanel.tsx   # Reconciliation results display (matched/unmatched)
```

### Navigation Update

Add "Finance" section to `NavBar.tsx` with sub-links:
- `/finance` — Dashboard
- `/finance/upload` — Upload Documents
- `/finance/review` — Review Queue
- `/finance/export` — Export Data

### Frontend API Extensions (`frontend/lib/api.ts`)

```typescript
// New finance API functions
export const uploadFinanceDocument = async (orgId: string, file: File) => { ... }
export const getFinanceDocuments = async (orgId: string) => { ... }
export const getCashflow = async (orgId: string, period: string, startDate: string, endDate: string) => { ... }
export const getPnl = async (orgId: string, startDate: string, endDate: string) => { ... }
export const reconcileDocuments = async (orgId: string, file: File) => { ... }
export const getReviewQueue = async (orgId: string) => { ... }
export const updateReviewStatus = async (orgId: string, signalId: string, action: string, edits?: object) => { ... }
export const exportFinanceCsv = async (orgId: string, startDate?: string, endDate?: string, category?: string) => { ... }
```

---

## Prompt Templates

New templates in `/prompts/v1/`:

### `finance-document-extraction.md`
Extracts: vendor_name, amount, currency, document_date, description, vat_amount, vat_rate.
Instructs Nova Lite to return strict JSON. Handles both formal UK invoices (with VAT) and general documents.
Referenced by: Req 2.2, Req 5.5

### `finance-document-classification.md`
Classifies document as "revenue" or "expense" with confidence_score.
Instructs Nova Lite to return `{category, confidence_score}`.
Referenced by: Req 3.2

### `finance-informal-receipt.md`
Specialized extraction for Nigerian informal documents: POS slips, handwritten receipts, manual invoices, cash records.
Instructs Nova Lite to return strict JSON with vendor_name, amount, currency (NGN), document_date, description.
Referenced by: Req 6.5

---

## Data Storage

### DynamoDB

No new tables required. Finance documents are stored as signals in the existing `autonomous-sme-signals` table:

```
Table: autonomous-sme-signals
  PK: org_id
  SK: signal_id (= document_id for finance documents)
  signal_type: "finance_document"
  content: {
    document_id, vendor_name, amount, currency, vat_amount, vat_rate,
    document_date, description, category, confidence_score,
    processing_status, s3_key, flags, review_reason
  }
  processing_status: "processed" | "needs_review" | "approved" | "rejected" | "failed"
  created_at: ISO 8601 timestamp
```

The `processing_status` field on the Signal record mirrors the Finance_Document status for efficient querying.

### S3

New path prefix under existing bucket:

```
autonomous-sme-documents/
├── invoices/{org_id}/...          # Existing invoice uploads
└── documents/{org_id}/{doc_id}/   # New finance document uploads
    └── {filename}
```

---

## Data Flow Diagrams

### Document Upload and Processing

```
User → [POST /api/finance/upload] → Finance Router
  → S3 upload (documents/{org_id}/{doc_id}/{filename})
  → OCR (extract raw text)
  → FinanceDocumentAgent.extract_document() → Nova Lite (finance-document-extraction prompt)
  → FinanceDocumentAgent.classify_document() → Nova Lite (finance-document-classification prompt)
  → FinanceService.detect_anomalies() → duplicate/outlier check
  → DynamoDB (create_signal with signal_type="finance_document")
  → Response {document_id, status, extracted_data, flags}
```

### Cashflow and P&L

```
User → [GET /api/finance/{org_id}/cashflow] → Finance Router
  → FinanceService.get_cashflow()
  → DynamoDB query (signals where signal_type="finance_document", status in ["processed","approved"])
  → Aggregate by period
  → Response {periods: [...], currency}

User → [GET /api/finance/{org_id}/pnl] → Finance Router
  → FinanceService.get_pnl()
  → DynamoDB query (same filter + date range)
  → Group by vendor, compute totals, VAT summary
  → Response {total_revenue, total_expenses, net_profit, ...}
```

### Reconciliation

```
User → [POST /api/finance/{org_id}/reconcile] (CSV file) → Finance Router
  → Parse CSV → extract transactions [{date, description, amount}]
  → Query Finance_Documents for org_id
  → Match: amount within 1%, date within 3 days, vendor similarity
  → Mark matched pairs as "reconciled"
  → Response {matched, unmatched_transactions, unmatched_documents}
```

---

## Error Handling

Follows existing patterns from the Control Tower:

| Scenario | HTTP Code | Behavior |
|---|---|---|
| Invalid file type | 400 | Reject with descriptive message |
| File too large (>10MB) | 413 | Reject with size limit message |
| OCR/extraction failure | 200 | Store with status="failed", add to review queue |
| Classification low confidence | 200 | Store with status="needs_review" |
| Pydantic validation failure | 200 | Store with status="failed", add to review queue |
| Anomaly/duplicate detected | 200 | Store with status="needs_review", attach flags |
| DynamoDB/S3 failure | 500 | Retry with backoff (existing service pattern) |
| Bedrock model failure | 503 | Retry with backoff + circuit breaker (existing pattern) |

---

## Integration with Existing System

The finance pipeline feeds into the existing agentic loop:

1. Finance documents stored as signals → Risk Agent can include them in BSI calculation
2. Cashflow data → Strategy Agent can factor financial health into strategy simulation
3. Anomaly flags → Action Agent can trigger follow-up workflows
4. All data scoped by org_id → existing OrgIsolationMiddleware applies

No changes needed to existing agents — they already query signals by org_id and can process any signal_type.

---

## Security and Multi-Tenancy

- All endpoints require `org_id` parameter
- Existing `OrgIsolationMiddleware` enforces tenant boundaries
- S3 paths include `org_id` for storage isolation
- DynamoDB queries always filter by `org_id` partition key
- Bank statement CSV data is processed in-memory, never stored raw
- File size limit (10MB) prevents abuse

---

## Testing Strategy

### Backend Tests

- Unit tests for `FinanceDocument` model validators
- Unit tests for `FinanceDocumentAgent` methods (mocked Bedrock)
- Unit tests for `FinanceService` methods (mocked DynamoDB)
- Integration tests for finance router endpoints
- Anomaly detection edge cases (no prior data, single document, exact duplicates)
- CSV export round-trip validation
- Reconciliation matching logic (tolerance boundaries)

### Frontend Tests

- Jest: CashflowChart, PnlSummary, ReviewQueue, FinanceDocUpload components
- Playwright: Finance upload flow, review queue approve/reject, CSV download

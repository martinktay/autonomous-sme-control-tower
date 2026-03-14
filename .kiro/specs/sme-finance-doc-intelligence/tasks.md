# Implementation Tasks

## Task 1: Finance Document Pydantic Model
- [x] Create `backend/app/models/finance_document.py` with `DocumentFlag` and `FinanceDocument` models
- [x] Add field validators: currency (3-letter ISO 4217), category ("revenue"/"expense"), processing_status ("processed"/"needs_review"/"approved"/"rejected"/"failed"), amount (>0), confidence_score (0.0-1.0), vat_amount (>=0), vat_rate (>=0)
- [x] Export `FinanceDocument` and `DocumentFlag` from `backend/app/models/__init__.py`
- [x] Update `backend/app/models/signal.py` to add `"finance_document"` to valid signal_types

Requirements: 13.1, 13.2, 13.3, 13.4, 13.5, 13.6, 14.1

## Task 2: Prompt Templates
- [x] Create `prompts/v1/finance-document-extraction.md` — instructs Nova Lite to extract vendor_name, amount, currency, document_date, description, vat_amount, vat_rate as strict JSON
- [x] Create `prompts/v1/finance-document-classification.md` — instructs Nova Lite to classify as "revenue" or "expense" with confidence_score as strict JSON
- [x] Create `prompts/v1/finance-informal-receipt.md` — instructs Nova Lite to extract fields from Nigerian informal documents (POS slips, handwritten receipts, manual invoices) as strict JSON

Requirements: 2.2, 3.2, 5.5, 6.5

## Task 3: Finance Document Agent
- [x] Create `backend/app/agents/finance_agent.py` with `FinanceDocumentAgent` class
- [x] Implement `extract_document(raw_text, currency_hint)` — loads `finance-document-extraction` prompt, invokes Nova Lite, parses JSON with json_guard, returns extracted fields including VAT for GBP documents
- [x] Implement `classify_document(extracted_data)` — loads `finance-document-classification` prompt, invokes Nova Lite, returns {category, confidence_score}
- [x] Implement `parse_informal_receipt(raw_text)` — loads `finance-informal-receipt` prompt, invokes Nova Lite, returns extracted fields for NGN informal documents

Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 3.1, 3.2, 3.3, 3.4, 5.1, 5.2, 5.3, 5.4, 5.5, 6.1, 6.2, 6.3, 6.4, 6.5, 14.4, 14.5, 14.6

## Task 4: Finance Service — Core Methods
- [x] Create `backend/app/services/finance_service.py` with `FinanceService` class
- [x] Implement `get_finance_documents(org_id)` — query signals with signal_type="finance_document"
- [x] Implement `detect_anomalies(org_id, document)` — check for duplicates (same vendor+amount+date) and statistical outliers (>3 sigma from mean for same vendor)
- [x] Implement `get_review_queue(org_id)` — query documents with processing_status="needs_review"
- [x] Implement `update_review_status(org_id, signal_id, action, edits)` — approve/reject/edit documents, update processing_status in DynamoDB

Requirements: 10.1, 10.2, 10.3, 10.4, 10.5, 11.1, 11.2, 11.3, 11.4, 11.5, 14.2

## Task 5: Finance Service — Cashflow and P&L
- [x] Implement `get_cashflow(org_id, period, start_date, end_date)` — aggregate revenue/expense totals grouped by daily/weekly/monthly periods from approved/processed documents
- [x] Implement `get_pnl(org_id, start_date, end_date)` — compute total revenue, total expenses, net profit, group by vendor, include VAT summary when available
- [x] Handle empty date ranges by returning zero totals

Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 8.1, 8.2, 8.3, 8.4, 8.5

## Task 6: Finance Service — Reconciliation and CSV Export
- [x] Implement `reconcile(org_id, bank_csv_content)` — parse bank CSV, match transactions to Finance_Documents by amount (1% tolerance), date (3 days), vendor similarity; mark matched/unmatched
- [x] Implement `export_csv(org_id, start_date, end_date, category)` — generate CSV with columns: document_id, vendor_name, amount, currency, vat_amount, vat_rate, document_date, category, confidence_score, processing_status; filter by date range and category
- [x] Add singleton `get_finance_service()` factory function

Requirements: 9.1, 9.2, 9.3, 9.4, 9.5, 9.6, 9.7, 12.1, 12.2, 12.3, 12.4, 12.5, 12.6

## Task 7: Finance Router
- [x] Create `backend/app/routers/finance.py` with APIRouter prefix `/api/finance`
- [x] Implement `POST /api/finance/upload` — validate file type (PDF/JPEG/PNG) and size (<=10MB), upload to S3, run OCR placeholder, call finance_agent for extraction (informal for NGN, standard otherwise), classify, detect anomalies, store as signal, return result
- [x] Implement `GET /api/finance/{org_id}/documents` — list finance documents
- [x] Implement `GET /api/finance/{org_id}/cashflow` — with query params period, start_date, end_date
- [x] Implement `GET /api/finance/{org_id}/pnl` — with query params start_date, end_date
- [x] Implement `POST /api/finance/{org_id}/reconcile` — accept CSV file upload
- [x] Implement `GET /api/finance/{org_id}/review-queue` — return review queue documents
- [x] Implement `PUT /api/finance/{org_id}/review/{signal_id}` — approve/reject/edit
- [x] Implement `GET /api/finance/{org_id}/export/csv` — with query params start_date, end_date, category; set Content-Type and Content-Disposition headers
- [x] Register finance router in `backend/app/main.py`

Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 2.5, 2.6, 3.5, 4.1, 4.2, 4.3, 4.5, 6.6, 7.5, 8.3, 9.6, 11.6, 12.3, 12.5, 14.1, 14.2, 14.3

## Task 8: Frontend API Client Extensions
- [x] Add `uploadFinanceDocument(orgId, file)` to `frontend/lib/api.ts` — POST to /api/finance/upload with FormData
- [x] Add `getFinanceDocuments(orgId)` — GET /api/finance/{orgId}/documents
- [x] Add `getCashflow(orgId, period, startDate, endDate)` — GET /api/finance/{orgId}/cashflow
- [x] Add `getPnl(orgId, startDate, endDate)` — GET /api/finance/{orgId}/pnl
- [x] Add `reconcileDocuments(orgId, file)` — POST /api/finance/{orgId}/reconcile with FormData
- [x] Add `getReviewQueue(orgId)` — GET /api/finance/{orgId}/review-queue
- [x] Add `updateReviewStatus(orgId, signalId, action, edits?)` — PUT /api/finance/{orgId}/review/{signalId}
- [x] Add `exportFinanceCsv(orgId, startDate?, endDate?, category?)` — GET /api/finance/{orgId}/export/csv, return blob
- [x] Add all new functions to `apiClient` export object

Requirements: 7.5, 8.3, 9.6, 11.6, 12.3

## Task 9: Finance Document Upload Page
- [x] Create `frontend/app/finance/upload/page.tsx` — file upload widget accepting PDF/JPEG/PNG, file size display, upload button with loading state
- [x] Display extraction results after upload: vendor_name, amount, currency, category, confidence_score, flags
- [x] Show review status if document was sent to review queue
- [x] Link to finance dashboard and review queue after upload

Requirements: 1.1, 1.2, 1.3, 1.6

## Task 10: Finance Dashboard Page with Cashflow Chart
- [x] Create `frontend/components/CashflowChart.tsx` — time-series bar chart showing revenue vs expenses per period, period selector (daily/weekly/monthly), date range picker
- [x] Create `frontend/components/PnlSummary.tsx` — card displaying total revenue, total expenses, net profit, VAT summary when available
- [x] Create `frontend/app/finance/page.tsx` — finance dashboard page composing CashflowChart and PnlSummary, with date range controls and empty state handling
- [x] Display amounts in the currency associated with the org's documents

Requirements: 7.1, 7.2, 7.3, 7.4, 7.6, 8.1, 8.2, 8.4, 8.5

## Task 11: Review Queue Page
- [x] Create `frontend/components/ReviewQueue.tsx` — table of documents with processing_status="needs_review", showing vendor_name, amount, currency, category, confidence_score, review_reason, and action buttons (approve/reject/edit)
- [x] Create `frontend/app/finance/review/page.tsx` — review queue page with edit modal for correcting extracted fields
- [x] Implement approve action — calls updateReviewStatus with action="approve"
- [x] Implement reject action — calls updateReviewStatus with action="reject"
- [x] Implement edit action — shows editable fields, calls updateReviewStatus with action="edit" and corrected values

Requirements: 11.1, 11.2, 11.3, 11.4, 11.5, 11.6

## Task 12: CSV Export and Reconciliation Pages
- [x] Create `frontend/app/finance/export/page.tsx` — date range picker, category filter dropdown, download CSV button that triggers blob download
- [x] Create `frontend/components/ReconciliationPanel.tsx` — displays matched/unmatched transactions and documents after reconciliation
- [x] Add reconciliation UI to finance dashboard or as section in export page — CSV upload for bank statement, display results

Requirements: 9.1, 9.4, 9.6, 12.1, 12.3, 12.4, 12.5

## Task 13: Navigation Update
- [x] Update `frontend/components/NavBar.tsx` to add Finance section with sub-links: /finance (Dashboard), /finance/upload (Upload), /finance/review (Review Queue), /finance/export (Export)
- [x] Ensure active state styling for finance routes

Requirements: 7.1, 11.1, 12.1

## Task 14: Backend Tests
- [x] Write unit tests for `FinanceDocument` model validators (valid/invalid currency, category, status, amount, confidence_score, vat fields)
- [x] Write unit tests for `FinanceDocumentAgent` methods with mocked Bedrock client
- [x] Write unit tests for `FinanceService` methods (cashflow aggregation, P&L computation, anomaly detection, reconciliation matching, CSV export) with mocked DynamoDB
- [x] Write integration tests for finance router endpoints (upload, documents, cashflow, pnl, reconcile, review-queue, review update, csv export)
- [x] Test CSV round-trip: export then parse back produces equivalent records
- [x] Test reconciliation edge cases: exact match, tolerance boundaries, no matches

Requirements: 9.7, 12.6, 13.1-13.6

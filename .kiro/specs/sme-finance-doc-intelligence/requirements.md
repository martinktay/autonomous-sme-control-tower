# Requirements Document

## Introduction

The SME Finance Document Intelligence Platform extends the existing Autonomous SME Control Tower to provide AI-powered financial document processing for UK SMEs and Nigerian informal SMEs. The platform enables document upload, OCR-based field extraction, automatic revenue/expense classification, VAT-aware parsing, informal receipt handling, cashflow visualization, P&L summaries, reconciliation, anomaly detection, manual review workflows, and CSV export. The feature integrates with the existing signal processing pipeline (ingest → diagnose → simulate → execute → evaluate) and preserves multi-tenant isolation via org_id scoping.

## Glossary

- **Document_Processor**: The backend subsystem responsible for receiving uploaded files, performing OCR, and extracting structured financial fields using AI models via AWS Bedrock Nova.
- **Document_Classifier**: The AI component that categorizes a processed document as either revenue (income) or expense.
- **VAT_Extractor**: The component that identifies and extracts VAT amounts and VAT rates from UK financial documents.
- **Informal_Receipt_Parser**: The specialized parsing component that handles Nigerian informal documents including POS slips, manual invoices, handwritten receipts, and cash records.
- **Cashflow_Dashboard**: The frontend visualization component that displays income versus expenses over configurable time periods.
- **PnL_Generator**: The backend component that computes profit and loss summaries from classified document data.
- **Reconciliation_Engine**: The component that matches processed documents against bank statements or expected transactions.
- **Anomaly_Detector**: The component that identifies suspicious, duplicate, or outlier documents.
- **Review_Queue**: The workflow system that holds documents requiring human verification before final acceptance.
- **CSV_Exporter**: The component that serializes financial document data into CSV format for download.
- **Finance_Document**: A Pydantic model representing a processed financial document with fields such as document_id, org_id, vendor_name, amount, currency, vat_amount, vat_rate, document_date, category, and classification.
- **UK_SME**: A small or medium enterprise operating in the United Kingdom, dealing with formal invoices, receipts, and VAT obligations.
- **Nigerian_Informal_SME**: A small or medium enterprise operating in Nigeria, dealing with POS slips, handwritten receipts, manual invoices, and cash-based records.

## Requirements

### Requirement 1: Document Upload and Storage

**User Story:** As an SME owner, I want to upload PDF and image files of my financial documents, so that the platform can process and store them securely.

#### Acceptance Criteria

1. WHEN a user submits a PDF file via the upload endpoint, THE Document_Processor SHALL accept the file and store it in S3 under the path `documents/{org_id}/{document_id}/{filename}`.
2. WHEN a user submits an image file (JPEG or PNG) via the upload endpoint, THE Document_Processor SHALL accept the file and store it in S3 under the path `documents/{org_id}/{document_id}/{filename}`.
3. WHEN a user submits a file that is not a PDF, JPEG, or PNG, THE Document_Processor SHALL reject the upload and return an HTTP 400 error with a descriptive message.
4. WHEN a file is uploaded, THE Document_Processor SHALL generate a unique document_id (UUID) and associate the file with the requesting org_id.
5. THE Document_Processor SHALL enforce that all uploaded documents are scoped to the org_id of the requesting user.
6. WHEN a file exceeds 10 MB in size, THE Document_Processor SHALL reject the upload and return an HTTP 413 error with a descriptive message.

### Requirement 2: OCR and AI Field Extraction

**User Story:** As an SME owner, I want the platform to automatically read my uploaded documents and extract key financial fields, so that I do not have to enter data manually.

#### Acceptance Criteria

1. WHEN a PDF or image file is stored in S3, THE Document_Processor SHALL perform OCR to extract raw text from the document.
2. WHEN raw text is extracted, THE Document_Processor SHALL send the text to the Nova Lite model using a prompt template stored at `/prompts/v1/finance_document_extraction.md` to extract structured fields.
3. THE Document_Processor SHALL extract the following fields from each document: vendor_name, amount, currency, document_date, and description.
4. WHEN the Nova Lite model returns a response, THE Document_Processor SHALL validate the response against the Finance_Document Pydantic model.
5. IF the Nova Lite model returns a response that fails Pydantic validation, THEN THE Document_Processor SHALL mark the document with a processing_status of "failed" and add the document to the Review_Queue.
6. WHEN extraction completes successfully, THE Document_Processor SHALL store the Finance_Document as a signal in DynamoDB with signal_type "finance_document".

### Requirement 3: Document Classification

**User Story:** As an SME owner, I want my documents to be automatically classified as revenue or expense, so that I can track my income and spending without manual sorting.

#### Acceptance Criteria

1. WHEN a Finance_Document is successfully extracted, THE Document_Classifier SHALL classify the document as either "revenue" or "expense".
2. THE Document_Classifier SHALL use a prompt template stored at `/prompts/v1/finance_document_classification.md` to perform classification via the Nova Lite model.
3. WHEN classification completes, THE Document_Classifier SHALL store the classification value in the Finance_Document category field.
4. THE Document_Classifier SHALL assign a confidence_score between 0.0 and 1.0 to each classification.
5. WHEN the confidence_score is below 0.7, THE Document_Classifier SHALL add the document to the Review_Queue for human verification.

### Requirement 4: Multi-Currency Support

**User Story:** As an SME owner operating in the UK or Nigeria, I want the platform to correctly handle my local currency, so that financial amounts are recorded accurately.

#### Acceptance Criteria

1. THE Document_Processor SHALL support GBP as the currency for UK SME documents.
2. THE Document_Processor SHALL support NGN as the currency for Nigerian SME documents.
3. WHEN the extracted currency code is not a valid 3-letter ISO 4217 code, THE Document_Processor SHALL reject the extraction and add the document to the Review_Queue.
4. THE Finance_Document model SHALL store currency as a 3-letter uppercase ISO 4217 code, validated by a field_validator.
5. WHEN no currency is detected in a document, THE Document_Processor SHALL default to the org_id-associated currency preference if configured, or add the document to the Review_Queue if no preference exists.

### Requirement 5: VAT-Aware Extraction for UK Documents

**User Story:** As a UK SME owner, I want the platform to extract VAT amounts and rates from my invoices, so that I can track my VAT obligations accurately.

#### Acceptance Criteria

1. WHEN a document with currency GBP is processed, THE VAT_Extractor SHALL attempt to extract the VAT amount and VAT rate from the document.
2. WHEN a VAT amount is extracted, THE VAT_Extractor SHALL store the value in the Finance_Document vat_amount field as a non-negative decimal.
3. WHEN a VAT rate is extracted, THE VAT_Extractor SHALL store the value in the Finance_Document vat_rate field as a percentage (e.g., 20.0 for 20%).
4. WHEN no VAT information is found in a GBP document, THE VAT_Extractor SHALL set vat_amount to 0.0 and vat_rate to 0.0.
5. THE VAT_Extractor SHALL use the extraction prompt template at `/prompts/v1/finance_document_extraction.md` to extract VAT fields alongside other financial fields.

### Requirement 6: Informal Receipt Parsing for Nigerian SMEs

**User Story:** As a Nigerian SME owner, I want the platform to handle my informal documents like POS slips, handwritten receipts, and cash records, so that I can digitize my financial records.

#### Acceptance Criteria

1. WHEN a document with currency NGN is processed, THE Informal_Receipt_Parser SHALL apply specialized parsing logic for informal document formats.
2. THE Informal_Receipt_Parser SHALL handle POS terminal slips by extracting merchant name, transaction amount, and transaction date.
3. THE Informal_Receipt_Parser SHALL handle handwritten receipts by extracting vendor name, amount, and date using OCR optimized for handwriting.
4. THE Informal_Receipt_Parser SHALL handle manual invoices by extracting vendor name, line items, total amount, and date.
5. THE Informal_Receipt_Parser SHALL use a prompt template stored at `/prompts/v1/finance_informal_receipt.md` for informal document extraction via the Nova Lite model.
6. WHEN the Informal_Receipt_Parser cannot extract a minimum of vendor_name and amount from an informal document, THE Informal_Receipt_Parser SHALL add the document to the Review_Queue.

### Requirement 7: Cashflow Dashboard

**User Story:** As an SME owner, I want to see a visual dashboard of my income versus expenses over time, so that I can understand my cash flow at a glance.

#### Acceptance Criteria

1. THE Cashflow_Dashboard SHALL display a time-series chart showing total revenue and total expenses per period.
2. THE Cashflow_Dashboard SHALL support period granularity of daily, weekly, and monthly views.
3. WHEN the user selects a time period, THE Cashflow_Dashboard SHALL filter the displayed data to the selected range.
4. THE Cashflow_Dashboard SHALL display amounts in the currency associated with the documents for the current org_id.
5. THE Cashflow_Dashboard SHALL retrieve data from a backend endpoint `GET /api/finance/{org_id}/cashflow` that returns aggregated revenue and expense totals grouped by period.
6. WHEN no documents exist for the selected period, THE Cashflow_Dashboard SHALL display an empty state message indicating no data is available.

### Requirement 8: Profit and Loss Summary

**User Story:** As an SME owner, I want to generate a profit and loss summary, so that I can understand my business profitability over a given period.

#### Acceptance Criteria

1. WHEN a user requests a P&L summary for a date range, THE PnL_Generator SHALL compute total revenue, total expenses, and net profit (revenue minus expenses) for that range.
2. THE PnL_Generator SHALL group revenue and expenses by category (vendor_name or description-based grouping).
3. THE PnL_Generator SHALL return the summary via a backend endpoint `GET /api/finance/{org_id}/pnl` with query parameters for start_date and end_date.
4. WHEN VAT data is available, THE PnL_Generator SHALL include a separate VAT summary showing total VAT collected and total VAT paid.
5. WHEN no documents exist for the requested date range, THE PnL_Generator SHALL return a summary with all totals set to 0.0.

### Requirement 9: Document Reconciliation

**User Story:** As an SME owner, I want to match my uploaded documents against bank statements or expected transactions, so that I can verify my records are complete and accurate.

#### Acceptance Criteria

1. WHEN a user uploads a bank statement (CSV format), THE Reconciliation_Engine SHALL parse the statement and extract transaction records (date, description, amount).
2. THE Reconciliation_Engine SHALL attempt to match each bank transaction to a Finance_Document based on amount (within a 1% tolerance), date (within 3 calendar days), and vendor name similarity.
3. WHEN a match is found, THE Reconciliation_Engine SHALL mark both the bank transaction and the Finance_Document as "reconciled".
4. WHEN no match is found for a bank transaction, THE Reconciliation_Engine SHALL flag the transaction as "unmatched" and add it to the Review_Queue.
5. WHEN no match is found for a Finance_Document, THE Reconciliation_Engine SHALL flag the document as "unmatched".
6. THE Reconciliation_Engine SHALL return reconciliation results via a backend endpoint `POST /api/finance/{org_id}/reconcile`.
7. FOR ALL bank statement CSV files, parsing then serializing back to CSV then parsing again SHALL produce equivalent transaction records (round-trip property).

### Requirement 10: Anomaly and Duplicate Detection

**User Story:** As an SME owner, I want the platform to flag suspicious or duplicate documents, so that I can avoid errors and fraud in my financial records.

#### Acceptance Criteria

1. WHEN a new Finance_Document is stored, THE Anomaly_Detector SHALL compare the document against existing documents for the same org_id.
2. WHEN two documents share the same vendor_name, amount, and document_date, THE Anomaly_Detector SHALL flag both documents as potential duplicates.
3. WHEN a document amount exceeds 3 standard deviations from the mean amount for the same vendor_name within the org_id, THE Anomaly_Detector SHALL flag the document as a potential anomaly.
4. WHEN a document is flagged as a potential duplicate or anomaly, THE Anomaly_Detector SHALL add the document to the Review_Queue with the flag reason.
5. THE Anomaly_Detector SHALL store flags in the Finance_Document metadata as a list of flag objects containing flag_type and flag_reason.

### Requirement 11: Manual Review Workflow

**User Story:** As an SME owner, I want a review queue for documents that need my attention, so that I can verify and correct any issues before the data is finalized.

#### Acceptance Criteria

1. THE Review_Queue SHALL display all documents with processing_status "needs_review" for the current org_id.
2. WHEN a user approves a document in the Review_Queue, THE Review_Queue SHALL update the document processing_status to "approved" and include the document in financial calculations.
3. WHEN a user rejects a document in the Review_Queue, THE Review_Queue SHALL update the document processing_status to "rejected" and exclude the document from financial calculations.
4. WHEN a user edits extracted fields of a document in the Review_Queue, THE Review_Queue SHALL update the Finance_Document with the corrected values and set processing_status to "approved".
5. THE Review_Queue SHALL display the reason each document was queued (e.g., low confidence, extraction failure, anomaly flag, duplicate flag, missing currency).
6. THE Review_Queue SHALL retrieve data from a backend endpoint `GET /api/finance/{org_id}/review-queue`.

### Requirement 12: CSV Export

**User Story:** As an SME owner, I want to export my financial document data to CSV, so that I can use the data in spreadsheets or share it with my accountant.

###
 Acceptance Criteria

1. WHEN a user requests a CSV export, THE CSV_Exporter SHALL generate a CSV file containing all Finance_Documents with processing_status "approved" or "processed" for the current org_id.
2. THE CSV_Exporter SHALL include the following columns in the CSV: document_id, vendor_name, amount, currency, vat_amount, vat_rate, document_date, category, classification, processing_status.
3. THE CSV_Exporter SHALL return the file via a backend endpoint `GET /api/finance/{org_id}/export/csv` with optional query parameters for start_date, end_date, and category filter.
4. WHEN a date range is specified, THE CSV_Exporter SHALL include only documents with document_date within the specified range.
5. THE CSV_Exporter SHALL set the HTTP response Content-Type header to "text/csv" and Content-Disposition header to include a descriptive filename.
6. FOR ALL exported CSV files, parsing the CSV output back into Finance_Document records SHALL produce records equivalent to the original data (round-trip property).

### Requirement 13: Finance Document Data Model

**User Story:** As a developer, I want a well-defined data model for financial documents, so that all components can exchange data consistently.

#### Acceptance Criteria

1. THE Finance_Document model SHALL include the following fields: document_id (str, UUID), org_id (str), vendor_name (str), amount (float, positive), currency (str, 3-letter ISO 4217), vat_amount (Optional float, non-negative), vat_rate (Optional float, non-negative), document_date (datetime), description (str), category (str: "revenue" or "expense"), confidence_score (float, 0.0 to 1.0), processing_status (str), s3_key (str), created_at (datetime), flags (Optional list of flag objects).
2. THE Finance_Document model SHALL validate that currency is a 3-letter uppercase ISO 4217 code using a field_validator.
3. THE Finance_Document model SHALL validate that category is one of "revenue" or "expense" using a field_validator.
4. THE Finance_Document model SHALL validate that processing_status is one of "processed", "needs_review", "approved", "rejected", or "failed" using a field_validator.
5. THE Finance_Document model SHALL validate that amount is greater than 0.
6. THE Finance_Document model SHALL validate that confidence_score is between 0.0 and 1.0 inclusive.

### Requirement 14: Integration with Existing Signal Pipeline

**User Story:** As a developer, I want the finance document processing to integrate with the existing signal pipeline, so that financial data feeds into the agentic loop for diagnosis, strategy, and action.

#### Acceptance Criteria

1. WHEN a Finance_Document is stored, THE Document_Processor SHALL create a Signal record in DynamoDB with signal_type "finance_document" and the Finance_Document data as the content field.
2. THE Document_Processor SHALL use the existing DynamoDB service (ddb_service) for all persistence operations.
3. THE Document_Processor SHALL use the existing S3 service (s3_service) for all file storage operations.
4. THE Document_Processor SHALL use the existing Bedrock client (bedrock_client) for all Nova model invocations.
5. THE Document_Processor SHALL use the existing prompt_loader utility to load prompt templates from `/prompts/v1/`.
6. THE Document_Processor SHALL use the existing json_guard utility to parse and validate JSON responses from Nova models.

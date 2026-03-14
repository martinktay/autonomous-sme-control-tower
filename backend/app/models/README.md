# Pydantic Data Models

This directory contains all Pydantic data models for the Autonomous SME Control Tower system.

## Models Overview

### Invoice (`invoice.py`)
Represents invoice operational signals.

**Fields:**
- `invoice_id` (str, required): Unique invoice identifier
- `org_id` (str, required): Organization identifier
- `vendor_name` (str, required): Vendor or supplier name
- `amount` (float, required): Invoice amount (must be positive)
- `currency` (str, default="USD"): Currency code (ISO 4217, 3-letter uppercase)
- `due_date` (datetime, required): Payment due date
- `description` (str, required): Invoice description or purpose
- `status` (str, default="pending"): Invoice status (pending, paid, overdue, cancelled)
- `created_at` (datetime, auto): Record creation timestamp
- `s3_key` (str, optional): S3 object key for invoice document

**Validations:**
- Currency must be 3-letter uppercase ISO 4217 code
- Amount must be positive
- Status must be one of: pending, paid, overdue, cancelled

---

### Email (`email.py`)
Represents email operational signals.

**Fields:**
- `email_id` (str, required): Unique email identifier
- `org_id` (str, required): Organization identifier
- `sender` (str, required): Email sender address
- `subject` (str, required): Email subject line
- `classification` (str, required): Email classification
- `content` (str, required): Email body content
- `created_at` (datetime, auto): Record creation timestamp

**Validations:**
- Classification must be one of: payment_reminder, customer_inquiry, operational_message, other

---

### Signal (`signal.py`)
Represents processed business signals with embeddings.

**Fields:**
- `signal_id` (str, required): Unique signal identifier
- `org_id` (str, required): Organization identifier
- `signal_type` (str, required): Signal type (invoice, email)
- `content` (dict, required): Structured signal content
- `embedding_ref` (str, optional): Reference to embedding vector
- `created_at` (datetime, auto): Record creation timestamp
- `processing_status` (str, default="processed"): Processing status

**Validations:**
- Signal type must be one of: invoice, email
- Processing status must be one of: processed, failed, pending

---

### NSISnapshot (`nsi.py`)
Represents Nova Stability Index calculation snapshots.

**Fields:**
- `nsi_id` (str, required): Unique NSI snapshot identifier
- `org_id` (str, required): Organization identifier
- `nsi_score` (float, required): NSI score between 0 and 100
- `liquidity_index` (float, required): Liquidity component score (0-100)
- `revenue_stability_index` (float, required): Revenue stability component score (0-100)
- `operational_latency_index` (float, required): Operational latency component score (0-100)
- `vendor_risk_index` (float, required): Vendor risk component score (0-100)
- `confidence` (str, required): Confidence level (high, medium, low)
- `reasoning` (dict, required): Reasoning for risk assessment and scores
- `timestamp` (datetime, auto): Snapshot timestamp

**Validations:**
- All index scores must be between 0 and 100
- Confidence must be one of: high, medium, low

---

### Strategy (`strategy.py`)
Represents AI-generated corrective strategies.

**Fields:**
- `strategy_id` (str, required): Unique strategy identifier
- `org_id` (str, required): Organization identifier
- `nsi_snapshot_id` (str, required): Reference to NSI snapshot
- `description` (str, required): Strategy description and recommended actions
- `predicted_nsi_improvement` (float, required): Predicted NSI improvement
- `confidence_score` (float, required): Confidence score between 0 and 1
- `automation_eligibility` (bool, required): Whether strategy can be automated
- `reasoning` (str, required): Reasoning for strategy recommendation
- `created_at` (datetime, auto): Record creation timestamp

**Validations:**
- Confidence score must be between 0 and 1
- Predicted improvement must be between -100 and 100

---

### ActionExecution (`action.py`)
Represents executed operational workflows.

**Fields:**
- `execution_id` (str, required): Unique execution identifier
- `org_id` (str, required): Organization identifier
- `strategy_id` (str, required): Reference to strategy
- `action_type` (str, required): Type of workflow executed
- `target_entity` (str, required): Entity affected by action
- `execution_status` (str, required): Status (success, failed, pending)
- `error_reason` (str, optional): Failure reason if applicable
- `timestamp` (datetime, auto): Execution timestamp

**Validations:**
- Execution status must be one of: success, failed, pending

---

### Evaluation (`evaluation.py`)
Represents post-action evaluation and prediction accuracy.

**Fields:**
- `evaluation_id` (str, required): Unique evaluation identifier
- `org_id` (str, required): Organization identifier
- `execution_id` (str, required): Reference to action execution
- `old_nsi` (float, required): NSI before action execution (0-100)
- `new_nsi` (float, required): NSI after action execution (0-100)
- `predicted_improvement` (float, required): Predicted NSI improvement from strategy
- `actual_improvement` (float, required): Actual NSI improvement (new_nsi - old_nsi)
- `prediction_accuracy` (float, required): Prediction accuracy score (0-1)
- `timestamp` (datetime, auto): Evaluation timestamp

**Validations:**
- NSI scores must be between 0 and 100
- Prediction accuracy must be between 0 and 1
- Actual improvement must match the difference between new_nsi and old_nsi

---

## Usage

All models are exported from `__init__.py` and can be imported as:

```python
from backend.app.models import (
    Invoice,
    Email,
    Signal,
    NSISnapshot,
    Strategy,
    ActionExecution,
    Evaluation
)
```

## Validation

All models include field-level validation using Pydantic's `field_validator` decorator to ensure:
- Type safety
- Value constraints (ranges, enums)
- Business logic validation
- Data consistency

Validation errors will raise `ValueError` with descriptive messages.

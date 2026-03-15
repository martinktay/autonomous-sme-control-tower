"""
Finance document router — upload, classify, review, export, and analyse.

Handles the full finance document lifecycle:
- Upload PDF/image/spreadsheet → AI extraction & anomaly detection
- Review queue for low-confidence or flagged documents
- Cashflow, P&L, analytics, and AI-powered insights
- CSV/XLSX export and bank reconciliation

Production-hardened with shared upload validation, structured error handling,
and safe error messages that don't leak internals.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from fastapi.responses import StreamingResponse
from typing import Dict, Any, Optional
import uuid
import io
import logging
from datetime import datetime, timezone

from app.agents.finance_agent import FinanceDocumentAgent
from app.agents.insights_agent import InsightsAgent
from app.services.s3_service import get_s3_service
from app.services.ddb_service import get_ddb_service
from app.services.finance_service import get_finance_service
from app.models import Signal
from app.utils.upload_validator import (
    validate_org_id,
    validate_upload_file,
    FINANCE_CONTENT_TYPES,
    FINANCE_EXTENSIONS,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/finance", tags=["finance"])


@router.post("/upload")
async def upload_finance_document(
    org_id: str,
    file: UploadFile = File(...),
) -> Dict[str, Any]:
    """Upload a financial document or spreadsheet. Supports PDF, JPEG, PNG, CSV, XLS, XLSX."""

    # Validate org_id and file using shared validators
    org_id = validate_org_id(org_id)
    file_content, safe_filename, ext = await validate_upload_file(
        file, FINANCE_CONTENT_TYPES, FINANCE_EXTENSIONS
    )

    is_spreadsheet = ext in {".csv", ".xls", ".xlsx"}

    # --- Spreadsheet path: parse rows as individual finance records ---
    if is_spreadsheet:
        return await _handle_spreadsheet_upload(org_id, file_content, file.content_type or "", safe_filename)

    # --- Document path: PDF / image ---
    return await _handle_document_upload(org_id, file_content, safe_filename)


async def _handle_spreadsheet_upload(
    org_id: str, file_content: bytes, content_type: str, filename: str,
) -> Dict[str, Any]:
    """Parse a CSV/Excel file and create one finance signal per row in DynamoDB."""
    finance_service = get_finance_service()
    try:
        csv_text = finance_service.parse_spreadsheet_to_csv(file_content, content_type, filename)
    except ValueError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        logger.error(f"Spreadsheet parsing failed for org={org_id}: {e}")
        raise HTTPException(400, "Could not parse the spreadsheet. Check the file format.")

    import csv as csv_mod
    reader = csv_mod.DictReader(io.StringIO(csv_text))
    ddb_service = get_ddb_service()
    created = []

    for row in reader:
        signal_id = str(uuid.uuid4())
        document_id = str(uuid.uuid4())
        amount_raw = row.get("amount", row.get("Amount", "0"))
        try:
            amount = float(str(amount_raw).replace(",", ""))
        except (ValueError, TypeError):
            amount = 0.0

        content = {
            "document_id": document_id,
            "org_id": org_id,
            "vendor_name": row.get("vendor_name", row.get("vendor", row.get("Vendor", row.get("description", row.get("Description", "Unknown"))))),
            "amount": amount,
            "currency": row.get("currency", row.get("Currency", "USD")),
            "vat_amount": row.get("vat_amount", row.get("VAT", None)),
            "vat_rate": row.get("vat_rate", None),
            "wht_amount": row.get("wht_amount", row.get("WHT", row.get("withholding_tax", None))),
            "cit_amount": row.get("cit_amount", row.get("CIT", row.get("corporate_tax", None))),
            "paye_amount": row.get("paye_amount", row.get("PAYE", row.get("payroll_tax", None))),
            "customs_levy": row.get("customs_levy", row.get("customs", row.get("import_duty", None))),
            "document_date": row.get("document_date", row.get("date", row.get("Date", datetime.now(timezone.utc).isoformat()))),
            "description": row.get("description", row.get("Description", "")),
            "category": row.get("category", row.get("Category", "expense")),
            "confidence_score": 0.9,
            "processing_status": "processed",
            "s3_key": "",
            "flags": [],
            "source_file": filename,
        }

        signal = Signal(
            signal_id=signal_id,
            org_id=org_id,
            signal_type="finance_document",
            content=content,
            processing_status="processed",
        )
        ddb_service.create_signal(signal.model_dump())
        created.append({"signal_id": signal_id, "document_id": document_id, "vendor": content["vendor_name"], "amount": amount})

    return {
        "status": "processed",
        "source_file": filename,
        "records_imported": len(created),
        "records": created,
    }


async def _handle_document_upload(
    org_id: str, file_content: bytes, filename: str,
) -> Dict[str, Any]:
    """Process a PDF/image: upload to S3, run AI extraction & classification, detect anomalies."""
    document_id = str(uuid.uuid4())
    signal_id = str(uuid.uuid4())
    s3_key = f"documents/{org_id}/{document_id}/{filename}"

    # Upload to S3
    try:
        s3_service = get_s3_service()
        s3_service.upload_file(file_content, s3_key)
    except Exception as e:
        logger.error(f"S3 upload failed for org={org_id}: {e}")
        raise HTTPException(500, "Failed to store file. Please try again.")

    # OCR placeholder — in production, call Textract or similar
    raw_text = f"OCR placeholder for {filename}"

    agent = FinanceDocumentAgent()
    finance_service = get_finance_service()

    # Determine currency hint (NGN triggers informal receipt parser)
    currency_hint = None
    try:
        extracted = agent.extract_document(raw_text, currency_hint)
    except Exception:
        extracted = {}

    detected_currency = extracted.get("currency", "")

    # Re-parse with informal receipt parser for Nigerian Naira documents
    if detected_currency == "NGN":
        try:
            extracted = agent.parse_informal_receipt(raw_text)
            extracted.setdefault("currency", "NGN")
        except Exception:
            pass

    # Classify
    try:
        classification = agent.classify_document(extracted)
    except Exception:
        classification = {"category": "expense", "confidence_score": 0.5}

    category = classification.get("category", "expense")
    confidence_score = float(classification.get("confidence_score", 0.5))

    # Build content
    processing_status = "processed"
    flags = []

    # Flag low-confidence extractions for human review
    if confidence_score < 0.7:
        processing_status = "needs_review"
        flags.append({"flag_type": "low_confidence", "flag_reason": f"Confidence {confidence_score:.2f} below 0.7 threshold"})

    content = {
        "document_id": document_id,
        "org_id": org_id,
        "vendor_name": extracted.get("vendor_name", "Unknown"),
        "amount": float(extracted.get("amount", 0) or 0),
        "currency": extracted.get("currency", "USD"),
        "vat_amount": extracted.get("vat_amount"),
        "vat_rate": extracted.get("vat_rate"),
        "wht_amount": extracted.get("wht_amount"),
        "cit_amount": extracted.get("cit_amount"),
        "paye_amount": extracted.get("paye_amount"),
        "customs_levy": extracted.get("customs_levy"),
        "document_date": extracted.get("document_date", datetime.now(timezone.utc).isoformat()),
        "description": extracted.get("description", ""),
        "category": category,
        "confidence_score": confidence_score,
        "processing_status": processing_status,
        "s3_key": s3_key,
        "flags": flags,
    }

    # Run anomaly detection (duplicates, statistical outliers)
    signal_data = {"content": content}
    anomaly_flags = finance_service.detect_anomalies(org_id, signal_data)
    for af in anomaly_flags:
        content["flags"].append(af.model_dump())
        content["processing_status"] = "needs_review"

    # Store as signal
    signal = Signal(
        signal_id=signal_id,
        org_id=org_id,
        signal_type="finance_document",
        content=content,
        processing_status=content["processing_status"],
    )
    ddb_service = get_ddb_service()
    ddb_service.create_signal(signal.model_dump())

    return {
        "signal_id": signal_id,
        "document_id": document_id,
        "org_id": org_id,
        "status": content["processing_status"],
        "extracted_data": content,
    }


@router.get("/{org_id}/documents")
async def get_finance_documents(org_id: str) -> Dict[str, Any]:
    """List all finance documents for an organization."""
    org_id = validate_org_id(org_id)
    try:
        docs = get_finance_service().get_finance_documents(org_id)
    except Exception as e:
        logger.error(f"Failed to fetch finance docs for org={org_id}: {e}")
        raise HTTPException(500, "Failed to retrieve documents.")
    return {"org_id": org_id, "documents": docs}


@router.get("/{org_id}/insights")
async def get_finance_insights(org_id: str) -> Dict[str, Any]:
    """Generate AI-powered financial insights with tax, VAT, and profitability analysis."""
    finance_service = get_finance_service()

    pnl = finance_service.get_pnl(org_id)
    cashflow = finance_service.get_cashflow(org_id, period="monthly")
    all_docs = finance_service.get_finance_documents(org_id)
    review_queue = finance_service.get_review_queue(org_id)

    # Build document stats
    currencies: Dict[str, int] = {}
    categories: Dict[str, int] = {}
    for d in all_docs:
        c = d.get("content", {})
        cur = c.get("currency", "USD")
        currencies[cur] = currencies.get(cur, 0) + 1
        cat = c.get("category", "unknown")
        categories[cat] = categories.get(cat, 0) + 1

    doc_stats = {
        "total_documents": len(all_docs),
        "pending_review": len(review_queue),
        "currencies": currencies,
        "categories": categories,
    }

    agent = InsightsAgent()
    insights = agent.generate_finance_insights(
        org_id=org_id,
        pnl=pnl,
        cashflow=cashflow,
        doc_stats=doc_stats,
    )

    return {"org_id": org_id, "insights": insights}


@router.get("/{org_id}/cashflow")
async def get_cashflow(
    org_id: str,
    period: str = Query("monthly", pattern="^(daily|weekly|monthly)$"),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> Dict[str, Any]:
    """Get cashflow data aggregated by period."""
    data = get_finance_service().get_cashflow(org_id, period, start_date, end_date)
    return {"org_id": org_id, "period": period, "cashflow": data}


@router.get("/{org_id}/analytics")
async def get_finance_analytics(org_id: str) -> Dict[str, Any]:
    """Return chart-ready analytics: vendor breakdown, category split, VAT, currency, and monthly trends."""
    finance_service = get_finance_service()
    pnl = finance_service.get_pnl(org_id)
    cashflow = finance_service.get_cashflow(org_id, period="monthly")
    all_docs = finance_service.get_finance_documents(org_id)

    # Expense by vendor (top 8 + "Other" bucket for chart readability)
    by_vendor = pnl.get("by_vendor", {})
    vendor_expenses = sorted(
        [(v, d.get("expenses", 0)) for v, d in by_vendor.items() if d.get("expenses", 0) > 0],
        key=lambda x: x[1], reverse=True,
    )
    top_vendors = vendor_expenses[:8]
    other_total = sum(amt for _, amt in vendor_expenses[8:])
    if other_total > 0:
        top_vendors.append(("Other", other_total))
    expense_by_vendor = [{"name": v, "value": round(amt, 2)} for v, amt in top_vendors]

    # Revenue by vendor (top 8 + "Other" bucket)
    vendor_revenue = sorted(
        [(v, d.get("revenue", 0)) for v, d in by_vendor.items() if d.get("revenue", 0) > 0],
        key=lambda x: x[1], reverse=True,
    )
    top_rev_vendors = vendor_revenue[:8]
    other_rev = sum(amt for _, amt in vendor_revenue[8:])
    if other_rev > 0:
        top_rev_vendors.append(("Other", other_rev))
    revenue_by_source = [{"name": v, "value": round(amt, 2)} for v, amt in top_rev_vendors]

    # Category split (revenue vs expense doc count and totals)
    cat_totals: Dict[str, Dict[str, float]] = {}
    currency_totals: Dict[str, float] = {}  # aggregate amounts by currency
    for d in all_docs:
        c = d.get("content", {})
        cat = c.get("category", "unknown")
        amt = float(c.get("amount", 0) or 0)
        cur = c.get("currency", "USD")
        if cat not in cat_totals:
            cat_totals[cat] = {"count": 0, "total": 0.0}
        cat_totals[cat]["count"] += 1
        cat_totals[cat]["total"] += amt
        currency_totals[cur] = currency_totals.get(cur, 0) + amt

    category_breakdown = [
        {"name": k, "count": int(v["count"]), "total": round(v["total"], 2)}
        for k, v in cat_totals.items()
    ]
    currency_breakdown = [
        {"currency": k, "total": round(v, 2)} for k, v in sorted(currency_totals.items(), key=lambda x: x[1], reverse=True)
    ]

    # VAT breakdown
    vat_summary = pnl.get("vat_summary", {})
    vat_collected = vat_summary.get("total_vat_collected", 0)
    vat_paid = vat_summary.get("total_vat_paid", 0)
    vat_breakdown = {
        "collected": round(vat_collected, 2),
        "paid": round(vat_paid, 2),
        "net_liability": round(vat_collected - vat_paid, 2),
    }

    # Full tax breakdown for pie/bar charts
    tax_summary = pnl.get("tax_summary", {})
    tax_breakdown = [
        {"name": "VAT (Collected)", "value": tax_summary.get("vat_collected", 0)},
        {"name": "VAT (Paid)", "value": tax_summary.get("vat_paid", 0)},
        {"name": "Withholding Tax", "value": tax_summary.get("withholding_tax", 0)},
        {"name": "Corporate Income Tax", "value": tax_summary.get("corporate_income_tax", 0)},
        {"name": "PAYE / Payroll", "value": tax_summary.get("paye_payroll", 0)},
        {"name": "Customs / Levy", "value": tax_summary.get("customs_levy", 0)},
    ]
    # Filter out zero entries for cleaner charts
    tax_breakdown_nonzero = [t for t in tax_breakdown if t["value"] > 0]

    # Monthly trend (revenue, expenses, net)
    monthly_trend = [
        {
            "period": cf["period"],
            "revenue": cf["revenue"],
            "expenses": cf["expenses"],
            "net": round(cf["revenue"] - cf["expenses"], 2),
        }
        for cf in cashflow
    ]

    return {
        "org_id": org_id,
        "analytics": {
            "expense_by_vendor": expense_by_vendor,
            "revenue_by_source": revenue_by_source,
            "category_breakdown": category_breakdown,
            "currency_breakdown": currency_breakdown,
            "vat_breakdown": vat_breakdown,
            "tax_breakdown": tax_breakdown_nonzero,
            "tax_summary": tax_summary,
            "monthly_trend": monthly_trend,
            "totals": {
                "revenue": pnl.get("total_revenue", 0),
                "expenses": pnl.get("total_expenses", 0),
                "net_profit": pnl.get("net_profit", 0),
                "document_count": len(all_docs),
                "total_tax_burden": tax_summary.get("total_tax_burden", 0),
            },
        },
    }


@router.get("/{org_id}/pnl")
async def get_pnl(
    org_id: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> Dict[str, Any]:
    """Get profit and loss summary."""
    data = get_finance_service().get_pnl(org_id, start_date, end_date)
    return {"org_id": org_id, "pnl": data}


@router.post("/{org_id}/reconcile")
async def reconcile(
    org_id: str,
    file: UploadFile = File(...),
) -> Dict[str, Any]:
    """Reconcile finance documents against a bank statement (CSV or Excel)."""
    org_id = validate_org_id(org_id)
    file_content = await file.read()
    if len(file_content) == 0:
        raise HTTPException(400, "Uploaded file is empty.")
    finance_service = get_finance_service()
    try:
        csv_content = finance_service.parse_spreadsheet_to_csv(
            file_content, file.content_type or "", file.filename or "",
        )
    except ValueError:
        raise HTTPException(400, "Upload a CSV or Excel (.xls, .xlsx) bank statement.")
    except Exception as e:
        logger.error(f"Reconciliation parse failed for org={org_id}: {e}")
        raise HTTPException(400, "Could not parse the bank statement file.")
    try:
        result = finance_service.reconcile(org_id, csv_content)
    except Exception as e:
        logger.error(f"Reconciliation failed for org={org_id}: {e}")
        raise HTTPException(500, "Reconciliation failed. Please try again.")
    return {"org_id": org_id, "reconciliation": result}


@router.get("/{org_id}/review-queue")
async def get_review_queue(org_id: str) -> Dict[str, Any]:
    """Get documents pending review."""
    docs = get_finance_service().get_review_queue(org_id)
    return {"org_id": org_id, "review_queue": docs}


@router.put("/{org_id}/review/{signal_id}")
async def update_review(
    org_id: str,
    signal_id: str,
    body: Dict[str, Any],
) -> Dict[str, Any]:
    """Approve, reject, or edit a document in the review queue."""
    action = body.get("action")
    if action not in ("approve", "reject", "edit"):
        raise HTTPException(400, "action must be 'approve', 'reject', or 'edit'")
    edits = body.get("edits")
    get_finance_service().update_review_status(org_id, signal_id, action, edits)
    return {"org_id": org_id, "signal_id": signal_id, "status": "updated", "action": action}


@router.get("/{org_id}/export/csv")
async def export_csv(
    org_id: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    category: Optional[str] = None,
):
    """Export finance documents as CSV."""
    csv_content = get_finance_service().export_csv(org_id, start_date, end_date, category)
    filename = f"finance_export_{org_id}_{datetime.now(timezone.utc).strftime('%Y%m%d')}.csv"
    return StreamingResponse(
        io.BytesIO(csv_content.encode("utf-8")),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/{org_id}/export/xlsx")
async def export_xlsx(
    org_id: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    category: Optional[str] = None,
):
    """Export finance documents as Excel (.xlsx)."""
    xlsx_bytes = get_finance_service().export_xlsx(org_id, start_date, end_date, category)
    filename = f"finance_export_{org_id}_{datetime.now(timezone.utc).strftime('%Y%m%d')}.xlsx"
    return StreamingResponse(
        io.BytesIO(xlsx_bytes),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )

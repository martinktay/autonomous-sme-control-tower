"""Bank Sync endpoints — bank statement import and reconciliation."""

import logging
from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException, Header, UploadFile, File, Query
from app.agents.bank_agent import get_bank_agent
from app.services.transaction_service import get_transaction_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/bank-sync", tags=["bank-sync"])


@router.post("/import", response_model=Dict[str, Any])
async def import_bank_statement(
    file: UploadFile = File(...),
    x_org_id: str = Header(..., alias="X-Org-ID"),
    business_name: str = Query("", description="Business name"),
):
    """Import a bank statement and reconcile against existing transactions."""
    try:
        content = await file.read()
        text_content = content.decode("utf-8", errors="replace")

        # Parse bank entries from CSV/text
        lines = text_content.strip().split("\n")
        bank_entries = []
        for line in lines[1:]:  # Skip header
            parts = line.split(",")
            if len(parts) >= 3:
                bank_entries.append({
                    "date": parts[0].strip(),
                    "description": parts[1].strip(),
                    "amount": parts[2].strip(),
                })

        # Get existing transactions for matching
        tx_svc = get_transaction_service()
        transactions = tx_svc.list_transactions(x_org_id, limit=300)

        agent = get_bank_agent()
        result = agent.reconcile(
            bank_entries=bank_entries,
            business_transactions=transactions,
            business_name=business_name,
        )

        # Auto-create transactions for unmatched bank entries
        created = 0
        for entry in result.get("unmatched_bank_entries", []):
            try:
                from app.models.transaction import TransactionCreate
                amount = float(str(entry.get("amount", "0")).replace(",", "").replace("₦", ""))
                tx_type = "expense" if amount < 0 else "revenue"
                tx_data = TransactionCreate(
                    description=f"Bank: {entry.get('description', 'Unknown')}",
                    amount=abs(amount),
                    transaction_type=tx_type,
                    category=entry.get("suggested_category", "bank_import"),
                    date=entry.get("date"),
                )
                tx_svc.create_transaction(x_org_id, tx_data)
                created += 1
            except Exception as e:
                logger.warning("Skipped bank entry: %s", e)

        result["transactions_created"] = created
        result["org_id"] = x_org_id
        return result

    except Exception as e:
        logger.error("Bank import failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Bank import failed. Please try again.")


@router.get("/supported-banks", response_model=Dict[str, Any])
async def list_supported_banks():
    """List supported Nigerian banks for statement import."""
    return {
        "supported_formats": [
            {"name": "Generic CSV", "id": "generic_csv", "status": "available"},
            {"name": "GTBank Statement", "id": "gtbank", "status": "available"},
            {"name": "Access Bank Statement", "id": "access", "status": "available"},
            {"name": "First Bank Statement", "id": "firstbank", "status": "available"},
            {"name": "UBA Statement", "id": "uba", "status": "coming_soon"},
            {"name": "Zenith Bank Statement", "id": "zenith", "status": "coming_soon"},
        ],
        "note": "Upload your bank statement as CSV. Our AI will auto-detect the format and reconcile.",
    }

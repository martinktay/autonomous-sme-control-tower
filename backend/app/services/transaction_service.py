"""Transaction management service — CRUD, summaries, cashflow."""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.config import get_settings
from app.models.transaction import Transaction, TransactionCreate
from app.services.ddb_service import get_ddb_service
from app.utils.id_generator import generate_id

logger = logging.getLogger(__name__)
settings = get_settings()


class TransactionService:
    """Manages unified transactions (revenue, expense, payment, transfer)."""

    def __init__(self):
        self.ddb = get_ddb_service()
        self.table = settings.transactions_table

    def create_transaction(self, business_id: str, data: TransactionCreate) -> Transaction:
        """Create a new transaction record."""
        txn = Transaction(
            transaction_id=generate_id("transaction"),
            business_id=business_id,
            branch_id=data.branch_id,
            transaction_type=data.transaction_type,
            category=data.category,
            amount=data.amount,
            currency=data.currency,
            counterparty_name=data.counterparty_name,
            description=data.description,
            date=data.date,
            payment_status=data.payment_status,
            created_at=datetime.now(timezone.utc),
        )
        self.ddb.put_item(self.table, {
            "business_id": txn.business_id,
            "transaction_id": txn.transaction_id,
            **txn.model_dump(mode="json"),
        })
        logger.info("Created transaction %s for business %s", txn.transaction_id, business_id)
        return txn

    def list_transactions(self, business_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """List transactions for a business."""
        return self.ddb.query_items(
            table_name=self.table,
            key_condition="org_id = :bid",
            expression_values={":bid": business_id},
            limit=limit,
        )

    def get_summary(self, business_id: str) -> Dict[str, Any]:
        """Revenue vs expense summary."""
        txns = self.list_transactions(business_id, limit=500)
        total_revenue = 0.0
        total_expense = 0.0
        total_payments = 0.0

        for txn in txns:
            amount = float(txn.get("amount", 0))
            txn_type = txn.get("transaction_type", "")
            if txn_type == "revenue":
                total_revenue += amount
            elif txn_type == "expense":
                total_expense += amount
            elif txn_type == "payment":
                total_payments += amount

        return {
            "total_revenue": round(total_revenue, 2),
            "total_expenses": round(total_expense, 2),
            "total_payments": round(total_payments, 2),
            "net_profit": round(total_revenue - total_expense, 2),
            "transaction_count": len(txns),
        }

    def get_cashflow(self, business_id: str) -> List[Dict[str, Any]]:
        """Return transactions grouped for cashflow charting (money in vs out)."""
        txns = self.list_transactions(business_id, limit=500)
        # Group by date (day level)
        daily: Dict[str, Dict[str, float]] = {}
        for txn in txns:
            date_str = str(txn.get("date", ""))[:10]  # YYYY-MM-DD
            if date_str not in daily:
                daily[date_str] = {"money_in": 0.0, "money_out": 0.0}
            amount = float(txn.get("amount", 0))
            txn_type = txn.get("transaction_type", "")
            if txn_type == "revenue":
                daily[date_str]["money_in"] += amount
            elif txn_type in ("expense", "payment"):
                daily[date_str]["money_out"] += amount

        result = [
            {"date": d, "money_in": round(v["money_in"], 2), "money_out": round(v["money_out"], 2)}
            for d, v in sorted(daily.items())
        ]
        return result


def get_transaction_service() -> TransactionService:
    return TransactionService()

"""Counterparty (supplier/customer) management service."""

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.config import get_settings
from app.models.counterparty import Counterparty, CounterpartyCreate
from app.services.ddb_service import get_ddb_service

logger = logging.getLogger(__name__)
settings = get_settings()


class CounterpartyService:
    """Manages supplier and customer records."""

    def __init__(self):
        self.ddb = get_ddb_service()
        self.table = settings.counterparties_table

    def create_counterparty(self, business_id: str, data: CounterpartyCreate) -> Counterparty:
        """Create a new counterparty record."""
        cp = Counterparty(
            counterparty_id=str(uuid.uuid4()),
            business_id=business_id,
            name=data.name,
            counterparty_type=data.counterparty_type,
            phone=data.phone,
            email=data.email,
            created_at=datetime.now(timezone.utc),
        )
        self.ddb.put_item(self.table, {
            "business_id": cp.business_id,
            "counterparty_id": cp.counterparty_id,
            **cp.model_dump(mode="json"),
        })
        logger.info("Created counterparty %s for business %s", cp.counterparty_id, business_id)
        return cp

    def list_counterparties(self, business_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """List counterparties for a business."""
        return self.ddb.query_items(
            table_name=self.table,
            key_condition="business_id = :bid",
            expression_values={":bid": {"S": business_id}},
            limit=limit,
        )

    def get_counterparty(self, business_id: str, counterparty_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a single counterparty."""
        return self.ddb.get_item(self.table, {
            "business_id": {"S": business_id},
            "counterparty_id": {"S": counterparty_id},
        })

    def get_balance_summary(self, business_id: str, counterparty_id: str) -> Dict[str, Any]:
        """Get balance summary for a counterparty."""
        cp = self.get_counterparty(business_id, counterparty_id)
        if not cp:
            return {"error": "Counterparty not found"}
        return {
            "counterparty_id": counterparty_id,
            "name": cp.get("name", ""),
            "type": cp.get("counterparty_type", ""),
            "balance_owed": float(cp.get("balance_owed", 0)),
            "balance_owing": float(cp.get("balance_owing", 0)),
            "net_position": round(float(cp.get("balance_owing", 0)) - float(cp.get("balance_owed", 0)), 2),
        }


def get_counterparty_service() -> CounterpartyService:
    return CounterpartyService()

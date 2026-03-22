"""Alert management service — creation, retrieval, tier-based limits."""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.config import get_settings
from app.models.alert import Alert
from app.services.ddb_service import get_ddb_service
from app.utils.id_generator import generate_id

logger = logging.getLogger(__name__)
settings = get_settings()


class AlertService:
    """Manages proactive business alerts."""

    def __init__(self):
        self.ddb = get_ddb_service()
        self.table = settings.alerts_table

    def create_alert(
        self,
        business_id: str,
        alert_type: str,
        severity: str,
        title: str,
        description: str,
        recommended_action: Optional[str] = None,
        branch_id: Optional[str] = None,
    ) -> Alert:
        """Create a new alert."""
        alert = Alert(
            alert_id=generate_id("alert"),
            business_id=business_id,
            branch_id=branch_id,
            alert_type=alert_type,
            severity=severity,
            title=title,
            description=description,
            recommended_action=recommended_action,
            created_at=datetime.now(timezone.utc),
        )
        self.ddb.put_item(self.table, {
            "business_id": alert.business_id,
            "alert_id": alert.alert_id,
            **alert.model_dump(mode="json"),
        })
        logger.info("Created alert %s (%s) for business %s", alert.alert_id, alert_type, business_id)
        return alert

    def list_alerts(self, business_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """List alerts for a business, most recent first."""
        return self.ddb.query_items(
            table_name=self.table,
            key_condition="business_id = :bid",
            expression_values={":bid": {"S": business_id}},
            limit=limit,
            scan_forward=False,
        )

    def mark_read(self, business_id: str, alert_id: str) -> None:
        """Mark an alert as read."""
        try:
            self.ddb.client.update_item(
                TableName=self.table,
                Key={
                    "business_id": {"S": business_id},
                    "alert_id": {"S": alert_id},
                },
                UpdateExpression="SET is_read = :val",
                ExpressionAttributeValues={":val": {"BOOL": True}},
            )
        except Exception as e:
            logger.error("Failed to mark alert %s as read: %s", alert_id, e)
            raise


def get_alert_service() -> AlertService:
    return AlertService()

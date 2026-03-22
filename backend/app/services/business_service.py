"""Business entity management service — registration, onboarding, CRUD."""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.config import get_settings
from app.models.business import Business, BusinessCreate, BusinessUpdate, BusinessType, PricingTier
from app.models.branch import Branch
from app.services.ddb_service import get_ddb_service
from app.utils.id_generator import generate_id

logger = logging.getLogger(__name__)
settings = get_settings()

# Default modules activated per business type
DEFAULT_MODULES: Dict[str, List[str]] = {
    BusinessType.SUPERMARKET: ["inventory", "supplier_tracking", "sales_analytics"],
    BusinessType.MINI_MART: ["inventory", "sales_analytics"],
    BusinessType.KIOSK: ["sales_analytics"],
    BusinessType.SALON: ["service_tracking", "booking"],
    BusinessType.FOOD_VENDOR: ["inventory", "sales_analytics"],
    BusinessType.AGRICULTURE: ["inventory", "seasonal_tracking"],
    BusinessType.ARTISAN: ["service_tracking"],
    BusinessType.PROFESSIONAL_SERVICE: ["service_tracking", "invoicing"],
    BusinessType.OTHER: [],
}


class BusinessService:
    """Manages business registration, onboarding, and CRUD operations."""

    def __init__(self):
        self.ddb = get_ddb_service()
        self.table = settings.businesses_table
        self.branches_table = settings.branches_table

    def create_business(self, data: BusinessCreate) -> Business:
        """Register a new business and create its default branch."""
        business_id = generate_id("business")
        now = datetime.now(timezone.utc)

        modules = DEFAULT_MODULES.get(data.business_type, [])

        business = Business(
            business_id=business_id,
            business_name=data.business_name,
            business_type=data.business_type,
            country=data.country,
            state_region=data.state_region,
            currency=data.currency,
            phone=data.phone,
            email=data.email,
            pricing_tier=PricingTier.STARTER,
            onboarding_complete=False,
            modules_enabled=modules,
            created_at=now,
        )

        # Persist business
        self.ddb.put_item(self.table, {
            "business_id": business.business_id,
            **business.model_dump(mode="json"),
        })

        # Create default primary branch
        self._create_default_branch(business_id, data.business_name, now)

        logger.info("Created business %s (%s)", business_id, data.business_name)
        return business

    def _create_default_branch(self, business_id: str, business_name: str, now: datetime) -> Branch:
        """Create the default primary branch for a new business."""
        branch = Branch(
            branch_id=generate_id("branch"),
            business_id=business_id,
            branch_name=f"{business_name} — Main",
            is_primary=True,
            created_at=now,
        )
        self.ddb.put_item(self.branches_table, {
            "business_id": branch.business_id,
            "branch_id": branch.branch_id,
            **branch.model_dump(mode="json"),
        })
        return branch

    def get_business(self, business_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a business by ID."""
        return self.ddb.get_item(
            self.table,
            {"business_id": {"S": business_id}},
        )

    def update_business(self, business_id: str, data: BusinessUpdate) -> Optional[Dict[str, Any]]:
        """Update business fields."""
        updates = {k: v for k, v in data.model_dump(exclude_none=True).items()}
        if not updates:
            return self.get_business(business_id)

        # Build update expression
        expr_parts = []
        expr_values = {}
        expr_names = {}
        for i, (key, value) in enumerate(updates.items()):
            attr_name = f"#attr{i}"
            attr_val = f":val{i}"
            expr_parts.append(f"{attr_name} = {attr_val}")
            expr_names[attr_name] = key
            expr_values[attr_val] = self.ddb._convert_to_dynamodb_format({attr_val: value})[attr_val]

        try:
            self.ddb.client.update_item(
                TableName=self.table,
                Key={"business_id": {"S": business_id}},
                UpdateExpression="SET " + ", ".join(expr_parts),
                ExpressionAttributeNames=expr_names,
                ExpressionAttributeValues=expr_values,
            )
            return self.get_business(business_id)
        except Exception as e:
            logger.error("Failed to update business %s: %s", business_id, e)
            raise

    def complete_onboarding(self, business_id: str) -> Optional[Dict[str, Any]]:
        """Mark onboarding as complete."""
        try:
            self.ddb.client.update_item(
                TableName=self.table,
                Key={"business_id": {"S": business_id}},
                UpdateExpression="SET onboarding_complete = :val",
                ExpressionAttributeValues={":val": {"BOOL": True}},
            )
            return self.get_business(business_id)
        except Exception as e:
            logger.error("Failed to complete onboarding for %s: %s", business_id, e)
            raise

    # --- Branch operations ---

    def create_branch(self, business_id: str, branch_name: str, address: Optional[str] = None) -> Branch:
        """Create a new branch for a business."""
        branch = Branch(
            branch_id=generate_id("branch"),
            business_id=business_id,
            branch_name=branch_name,
            address=address,
            is_primary=False,
            created_at=datetime.now(timezone.utc),
        )
        self.ddb.put_item(self.branches_table, {
            "business_id": branch.business_id,
            "branch_id": branch.branch_id,
            **branch.model_dump(mode="json"),
        })
        logger.info("Created branch %s for business %s", branch.branch_id, business_id)
        return branch

    def list_branches(self, business_id: str) -> List[Dict[str, Any]]:
        """List all branches for a business."""
        return self.ddb.query_items(
            table_name=self.branches_table,
            key_condition="business_id = :bid",
            expression_values={":bid": {"S": business_id}},
        )


def get_business_service() -> BusinessService:
    """Return a BusinessService instance."""
    return BusinessService()

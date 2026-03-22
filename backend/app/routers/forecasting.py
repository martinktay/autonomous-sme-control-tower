"""AI Forecasting endpoints — revenue, expense, and cash runway projections."""

import logging
from typing import Any, Dict

from fastapi import APIRouter, HTTPException
from app.agents.forecasting_agent import get_forecasting_agent
from app.services.transaction_service import get_transaction_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/forecasting", tags=["forecasting"])


@router.get("/{org_id}/forecast", response_model=Dict[str, Any])
async def get_forecast(
    org_id: str,
    business_name: str = "",
    business_type: str = "supermarket",
):
    """Generate AI revenue, expense, and cash runway forecast."""
    try:
        tx_svc = get_transaction_service()
        transactions = tx_svc.list_transactions(org_id, limit=500)

        revenue = [t for t in transactions if t.get("transaction_type") == "revenue"]
        expenses = [t for t in transactions if t.get("transaction_type") == "expense"]

        # Calculate current cash position from transactions
        total_revenue = sum(float(t.get("amount", 0)) for t in revenue)
        total_expenses = sum(float(t.get("amount", 0)) for t in expenses)
        cash_position = {
            "balance": round(total_revenue - total_expenses, 2),
            "total_revenue": round(total_revenue, 2),
            "total_expenses": round(total_expenses, 2),
        }

        agent = get_forecasting_agent()
        forecast = agent.forecast(
            revenue_data=revenue,
            expense_data=expenses,
            cash_position=cash_position,
            business_type=business_type,
            business_name=business_name,
        )
        forecast["org_id"] = org_id
        return forecast

    except Exception as e:
        logger.error("Forecasting failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to generate forecast")


@router.get("/{org_id}/cash-runway", response_model=Dict[str, Any])
async def get_cash_runway(org_id: str):
    """Quick cash runway calculation without full AI forecast."""
    try:
        tx_svc = get_transaction_service()
        transactions = tx_svc.list_transactions(org_id, limit=300)

        revenue = [t for t in transactions if t.get("transaction_type") == "revenue"]
        expenses = [t for t in transactions if t.get("transaction_type") == "expense"]

        total_rev = sum(float(t.get("amount", 0)) for t in revenue)
        total_exp = sum(float(t.get("amount", 0)) for t in expenses)
        balance = total_rev - total_exp

        # Estimate monthly burn rate (assume data spans ~30 days)
        monthly_burn = total_exp if total_exp > 0 else 1
        days_remaining = max(0, int((balance / (monthly_burn / 30))) if monthly_burn > 0 else 999)

        risk = "healthy" if days_remaining > 90 else "caution" if days_remaining > 30 else "critical"

        return {
            "org_id": org_id,
            "current_balance": round(balance, 2),
            "monthly_burn_rate": round(monthly_burn, 2),
            "days_remaining": days_remaining,
            "risk_level": risk,
        }

    except Exception as e:
        logger.error("Cash runway calc failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to calculate cash runway")

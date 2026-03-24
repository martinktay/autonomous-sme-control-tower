"""
Orchestration router — runs the full closed-loop cycle.

Executes the complete Diagnose → Simulate → Execute → Evaluate loop:
1. Calculate BSI from current signals
2. Generate AI strategies
3. Execute the top automatable strategy
4. Re-evaluate BSI and measure prediction accuracy

Endpoint:
  POST /api/orchestration/run-loop — run the full closed loop
"""

import logging
from fastapi import APIRouter, HTTPException, Request
from typing import Dict, Any
from pydantic import BaseModel
from app.agents.risk_agent import RiskAgent
from app.agents.strategy_agent import StrategyAgent
from app.agents.action_agent import ActionAgent
from app.agents.reeval_agent import ReevalAgent
from app.services.ddb_service import get_ddb_service
from app.services.transaction_service import get_transaction_service
from app.services.inventory_service import get_inventory_service
from app.utils.id_generator import generate_id
from app.middleware.org_isolation import validate_org_id_from_body

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/orchestration", tags=["orchestration"])

risk_agent = RiskAgent()
strategy_agent = StrategyAgent()
action_agent = ActionAgent()
reeval_agent = ReevalAgent()
ddb_service = get_ddb_service()


class RunLoopRequest(BaseModel):
    """Payload for triggering the full closed-loop cycle."""
    org_id: str


@router.post("/run-loop")
async def run_closed_loop(request: RunLoopRequest, req: Request) -> Dict[str, Any]:
    """Execute complete closed loop: diagnose → simulate → execute → evaluate."""
    validate_org_id_from_body(req, request.org_id)
    org_id = request.org_id
    
    try:
        # Step 1: Diagnose - Calculate BSI
        signals = ddb_service.get_signals(org_id)
        
        if not signals:
            return {
                "status": "no_data",
                "message": "No signals found. Upload invoices, emails, or financial documents first, then run the analysis."
            }
        
        # Enrich context with transaction and inventory data for better BSI calculation
        context = {}
        try:
            txn_svc = get_transaction_service()
            summary = txn_svc.get_summary(org_id)
            if summary:
                context["transaction_summary"] = summary
        except Exception:
            logger.debug("Could not fetch transaction summary for BSI context")
        
        try:
            inv_svc = get_inventory_service()
            alerts = inv_svc.get_low_stock_alerts(org_id)
            if alerts:
                context["stock_alerts"] = alerts[:10]
                context["stock_alert_count"] = len(alerts)
        except Exception:
            logger.debug("Could not fetch inventory alerts for BSI context")
        
        bsi_score = risk_agent.calculate_bsi(org_id, signals, context)
        bsi_snapshot_id = generate_id("bsi")
        
        # Store BSI snapshot
        bsi_snapshot_data = {
            "bsi_id": bsi_snapshot_id,
            "org_id": org_id,
            "bsi_score": bsi_score.business_stability_index,
            "liquidity_index": bsi_score.sub_indices.liquidity_index,
            "revenue_stability_index": bsi_score.sub_indices.revenue_stability_index,
            "operational_latency_index": bsi_score.sub_indices.operational_latency_index,
            "vendor_risk_index": bsi_score.sub_indices.vendor_risk_index,
            "confidence": bsi_score.confidence,
            "reasoning": {"explanation": bsi_score.explanation},
            "top_risks": bsi_score.top_risks,
            "timestamp": bsi_score.timestamp.isoformat()
        }
        ddb_service.put_bsi_score(bsi_snapshot_data)
        
        # Step 2: Simulate - Generate strategies
        strategies = strategy_agent.simulate_strategies(
            org_id=org_id,
            bsi_snapshot_id=bsi_snapshot_id,
            current_bsi=bsi_score.business_stability_index,
            top_risks=bsi_score.top_risks,
            context={}
        )
        
        # Store strategies
        for strategy in strategies:
            ddb_service.put_strategy(strategy.model_dump())
        
        # Step 3: Execute - Run first automatable strategy
        automatable = [s for s in strategies if s.automation_eligibility]
        
        if not automatable:
            return {
                "status": "no_automatable_strategy",
                "bsi_score": bsi_score.model_dump(),
                "strategies": [s.model_dump() for s in strategies]
            }
        
        selected = automatable[0]
        action = action_agent.execute_strategy(
            org_id=org_id,
            strategy_id=selected.strategy_id,
            strategy_description=selected.description,
            action_type="strategy_execution"
        )
        
        ddb_service.put_action(action.model_dump())
        
        # Step 4: Re-evaluate - Calculate new BSI
        new_signals = ddb_service.get_signals(org_id)
        new_bsi_score = risk_agent.calculate_bsi(org_id, new_signals, context)
        
        # Step 5: Evaluate - Assess prediction accuracy
        evaluation = reeval_agent.evaluate_outcome(
            org_id=org_id,
            execution_id=action.execution_id,
            predicted_improvement=selected.predicted_bsi_improvement,
            actual_bsi_before=bsi_score.business_stability_index,
            actual_bsi_after=new_bsi_score.business_stability_index,
            strategy_description=selected.description,
            execution_log={"action": action.model_dump()}
        )
        
        # Store new BSI
        new_bsi_snapshot_data = {
            "bsi_id": generate_id("bsi"),
            "org_id": org_id,
            "bsi_score": new_bsi_score.business_stability_index,
            "liquidity_index": new_bsi_score.sub_indices.liquidity_index,
            "revenue_stability_index": new_bsi_score.sub_indices.revenue_stability_index,
            "operational_latency_index": new_bsi_score.sub_indices.operational_latency_index,
            "vendor_risk_index": new_bsi_score.sub_indices.vendor_risk_index,
            "confidence": new_bsi_score.confidence,
            "reasoning": {"explanation": new_bsi_score.explanation},
            "top_risks": new_bsi_score.top_risks,
            "timestamp": new_bsi_score.timestamp.isoformat()
        }
        ddb_service.put_bsi_score(new_bsi_snapshot_data)
        
        return {
            "status": "completed",
            "bsi_before": bsi_score.business_stability_index,
            "bsi_after": new_bsi_score.business_stability_index,
            "improvement": new_bsi_score.business_stability_index - bsi_score.business_stability_index,
            "action": action.model_dump(),
            "evaluation": evaluation.model_dump(),
            "prediction_accuracy": evaluation.prediction_accuracy
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Closed loop execution failed for org %s: %s", org_id, e, exc_info=True)
        raise HTTPException(500, "Closed loop execution failed. Check server logs for details.")

import logging
from fastapi import APIRouter, HTTPException
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

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/orchestration", tags=["orchestration"])

risk_agent = RiskAgent()
strategy_agent = StrategyAgent()
action_agent = ActionAgent()
reeval_agent = ReevalAgent()
ddb_service = get_ddb_service()


class RunLoopRequest(BaseModel):
    org_id: str


@router.post("/run-loop")
async def run_closed_loop(request: RunLoopRequest) -> Dict[str, Any]:
    """Execute complete closed loop: diagnose -> simulate -> execute -> evaluate"""
    
    org_id = request.org_id
    
    try:
        # Step 1: Diagnose - Calculate NSI
        signals = ddb_service.get_signals(org_id)
        
        if not signals:
            return {
                "status": "no_data",
                "message": "No signals found. Upload invoices, emails, or financial documents first, then run the analysis."
            }
        
        # Enrich context with transaction and inventory data for better NSI calculation
        context = {}
        try:
            txn_svc = get_transaction_service()
            summary = txn_svc.get_summary(org_id)
            if summary:
                context["transaction_summary"] = summary
        except Exception:
            logger.debug("Could not fetch transaction summary for NSI context")
        
        try:
            inv_svc = get_inventory_service()
            alerts = inv_svc.get_low_stock_alerts(org_id)
            if alerts:
                context["stock_alerts"] = alerts[:10]
                context["stock_alert_count"] = len(alerts)
        except Exception:
            logger.debug("Could not fetch inventory alerts for NSI context")
        
        nsi_score = risk_agent.calculate_nsi(org_id, signals, context)
        nsi_snapshot_id = generate_id("nsi")
        
        # Store NSI snapshot
        nsi_snapshot_data = {
            "nsi_id": nsi_snapshot_id,
            "org_id": org_id,
            "nsi_score": nsi_score.nova_stability_index,
            "liquidity_index": nsi_score.sub_indices.liquidity_index,
            "revenue_stability_index": nsi_score.sub_indices.revenue_stability_index,
            "operational_latency_index": nsi_score.sub_indices.operational_latency_index,
            "vendor_risk_index": nsi_score.sub_indices.vendor_risk_index,
            "confidence": nsi_score.confidence,
            "reasoning": {"explanation": nsi_score.explanation},
            "top_risks": nsi_score.top_risks,
            "timestamp": nsi_score.timestamp.isoformat()
        }
        ddb_service.put_nsi_score(nsi_snapshot_data)
        
        # Step 2: Simulate - Generate strategies
        strategies = strategy_agent.simulate_strategies(
            org_id=org_id,
            nsi_snapshot_id=nsi_snapshot_id,
            current_nsi=nsi_score.nova_stability_index,
            top_risks=nsi_score.top_risks,
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
                "nsi_score": nsi_score.model_dump(),
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
        
        # Step 4: Re-evaluate - Calculate new NSI
        new_signals = ddb_service.get_signals(org_id)
        new_nsi_score = risk_agent.calculate_nsi(org_id, new_signals, context)
        
        # Step 5: Evaluate - Assess prediction accuracy
        evaluation = reeval_agent.evaluate_outcome(
            org_id=org_id,
            execution_id=action.execution_id,
            predicted_improvement=selected.predicted_nsi_improvement,
            actual_nsi_before=nsi_score.nova_stability_index,
            actual_nsi_after=new_nsi_score.nova_stability_index,
            strategy_description=selected.description,
            execution_log={"action": action.model_dump()}
        )
        
        # Store new NSI
        new_nsi_snapshot_data = {
            "nsi_id": generate_id("nsi"),
            "org_id": org_id,
            "nsi_score": new_nsi_score.nova_stability_index,
            "liquidity_index": new_nsi_score.sub_indices.liquidity_index,
            "revenue_stability_index": new_nsi_score.sub_indices.revenue_stability_index,
            "operational_latency_index": new_nsi_score.sub_indices.operational_latency_index,
            "vendor_risk_index": new_nsi_score.sub_indices.vendor_risk_index,
            "confidence": new_nsi_score.confidence,
            "reasoning": {"explanation": new_nsi_score.explanation},
            "top_risks": new_nsi_score.top_risks,
            "timestamp": new_nsi_score.timestamp.isoformat()
        }
        ddb_service.put_nsi_score(new_nsi_snapshot_data)
        
        return {
            "status": "completed",
            "nsi_before": nsi_score.nova_stability_index,
            "nsi_after": new_nsi_score.nova_stability_index,
            "improvement": new_nsi_score.nova_stability_index - nsi_score.nova_stability_index,
            "action": action.model_dump(),
            "evaluation": evaluation.model_dump(),
            "prediction_accuracy": evaluation.prediction_accuracy
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Closed loop execution failed for org %s: %s", org_id, e, exc_info=True)
        raise HTTPException(500, "Closed loop execution failed. Check server logs for details.")

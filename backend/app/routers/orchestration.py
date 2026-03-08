from fastapi import APIRouter
from typing import Dict, Any
from pydantic import BaseModel
from app.agents.risk_agent import RiskAgent
from app.agents.strategy_agent import StrategyAgent
from app.agents.action_agent import ActionAgent
from app.agents.reeval_agent import ReevalAgent
from app.services.ddb_service import get_ddb_service

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
    
    # Step 1: Diagnose - Calculate NSI
    signals = ddb_service.get_signals(org_id)
    nsi_score = risk_agent.calculate_nsi(org_id, signals, {})
    ddb_service.put_nsi_score(nsi_score.model_dump())
    
    # Step 2: Simulate - Generate strategies
    strategy = strategy_agent.simulate_strategies(
        org_id=org_id,
        current_nsi=nsi_score.nova_stability_index,
        top_risks=nsi_score.top_risks,
        context={}
    )
    ddb_service.put_strategy(strategy.model_dump())
    
    # Step 3: Execute - Run first automatable strategy
    automatable = [opt for opt in strategy.options if opt.automatable]
    
    if not automatable:
        return {
            "status": "no_automatable_strategy",
            "nsi_score": nsi_score.model_dump(),
            "strategies": strategy.model_dump()
        }
    
    selected = automatable[0]
    action = action_agent.execute_strategy(
        org_id=org_id,
        strategy_id=selected.strategy_id,
        strategy_description=selected.description,
        execution_steps=selected.execution_steps,
        predicted_improvement=selected.predicted_nsi_improvement
    )
    
    action.actual_nsi_before = nsi_score.nova_stability_index
    ddb_service.put_action(action.model_dump())
    
    # Step 4: Re-evaluate - Calculate new NSI
    new_nsi_score = risk_agent.calculate_nsi(org_id, signals, {})
    action.actual_nsi_after = new_nsi_score.nova_stability_index
    action.actual_improvement = action.actual_nsi_after - action.actual_nsi_before
    
    # Step 5: Evaluate - Assess prediction accuracy
    evaluation = reeval_agent.evaluate_outcome(
        predicted_improvement=action.predicted_nsi_improvement,
        actual_nsi_before=action.actual_nsi_before,
        actual_nsi_after=action.actual_nsi_after,
        strategy_description=selected.description,
        execution_log=action.execution_log
    )
    
    action.prediction_accuracy = evaluation.get("prediction_accuracy", 0)
    ddb_service.put_action(action.model_dump())
    ddb_service.put_nsi_score(new_nsi_score.model_dump())
    
    return {
        "status": "completed",
        "nsi_before": nsi_score.nova_stability_index,
        "nsi_after": new_nsi_score.nova_stability_index,
        "action": action.model_dump(),
        "evaluation": evaluation
    }

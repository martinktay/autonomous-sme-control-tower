import json
import uuid
from typing import List
from datetime import datetime, timezone
from app.utils.bedrock_client import get_bedrock_client
from app.utils.prompt_loader import load_prompt
from app.utils.json_guard import parse_json_safely
from app.models import Strategy


class StrategyAgent:
    """Agent for strategy simulation"""
    
    def __init__(self):
        self.bedrock = get_bedrock_client()
    
    def simulate_strategies(
        self,
        org_id: str,
        nsi_snapshot_id: str,
        current_nsi: float,
        top_risks: List[dict],
        context: dict
    ) -> List[Strategy]:
        """Generate strategy options"""
        
        prompt_template = load_prompt("strategy-planning")
        
        risks_text = "\n".join([f"- {risk.get('description', risk)}" for risk in top_risks])
        context_text = f"""
Current NSI: {current_nsi}
Top Risks:
{risks_text}

Context: {json.dumps(context, indent=2)}
"""
        
        prompt = f"{prompt_template}\n\n{context_text}"
        
        response = self.bedrock.invoke_nova_lite(prompt, temperature=0.7)
        
        parsed = parse_json_safely(response)
        if parsed and "strategies" in parsed:
            strategies = []
            for strategy_data in parsed["strategies"]:
                strategy = Strategy(
                    strategy_id=f"strat_{uuid.uuid4().hex[:12]}",
                    org_id=org_id,
                    nsi_snapshot_id=nsi_snapshot_id,
                    description=strategy_data["description"],
                    predicted_nsi_improvement=strategy_data["predicted_improvement"],
                    confidence_score=strategy_data["confidence"],
                    automation_eligibility=strategy_data.get("automatable", False),
                    reasoning=strategy_data.get("reasoning", ""),
                    created_at=datetime.now(timezone.utc)
                )
                strategies.append(strategy)
            
            return strategies
        
        raise ValueError("Failed to simulate strategies")

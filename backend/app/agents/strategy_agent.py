import json
from typing import List
from datetime import datetime, timezone
from app.utils.bedrock_client import get_bedrock_client
from app.utils.prompt_loader import load_prompt
from app.utils.json_guard import parse_json_safely, clean_model_output
from app.models import Strategy
from app.utils.id_generator import generate_id


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
            parsed = clean_model_output(parsed)
            strategies = []
            for strategy_data in parsed["strategies"]:
                # Resilient key extraction — Bedrock may use varying key names
                description = (
                    strategy_data.get("description")
                    or strategy_data.get("title")
                    or "Strategy recommendation"
                )
                predicted_improvement = float(
                    strategy_data.get("predicted_improvement")
                    or strategy_data.get("predicted_nsi_improvement")
                    or strategy_data.get("nsi_improvement")
                    or 5.0
                )
                confidence_score = float(
                    strategy_data.get("confidence")
                    or strategy_data.get("confidence_score")
                    or 0.5
                )
                automatable = bool(
                    strategy_data.get("automatable")
                    or strategy_data.get("automation_eligibility")
                    or False
                )
                reasoning = (
                    strategy_data.get("reasoning")
                    or strategy_data.get("rationale")
                    or strategy_data.get("execution_steps", "")
                )
                if isinstance(reasoning, list):
                    reasoning = "; ".join(str(r) for r in reasoning)

                strategy = Strategy(
                    strategy_id=generate_id("strategy"),
                    org_id=org_id,
                    nsi_snapshot_id=nsi_snapshot_id,
                    description=description,
                    predicted_nsi_improvement=predicted_improvement,
                    confidence_score=confidence_score,
                    automation_eligibility=automatable,
                    reasoning=str(reasoning),
                    created_at=datetime.now(timezone.utc)
                )
                strategies.append(strategy)
            
            return strategies
        
        raise ValueError("Failed to simulate strategies")

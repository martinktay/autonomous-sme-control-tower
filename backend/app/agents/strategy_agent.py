import json
from pathlib import Path
from typing import List
from app.utils.bedrock_client import get_bedrock_client
from app.models import Strategy, StrategyOption


class StrategyAgent:
    """Agent for strategy simulation"""
    
    def __init__(self):
        self.bedrock = get_bedrock_client()
        self.prompts_dir = Path("prompts/v1")
    
    def simulate_strategies(
        self,
        org_id: str,
        current_nsi: float,
        top_risks: List[str],
        context: dict
    ) -> Strategy:
        """Generate strategy options"""
        
        prompt_path = self.prompts_dir / "strategy-planning.md"
        prompt_template = prompt_path.read_text()
        
        context_text = f"""
Current NSI: {current_nsi}
Top Risks: {', '.join(top_risks)}
Context: {json.dumps(context, indent=2)}
"""
        
        prompt = f"{prompt_template}\n\n{context_text}"
        
        response = self.bedrock.invoke_nova_lite(prompt, temperature=0.7)
        
        try:
            data = json.loads(response)
            
            options = [
                StrategyOption(**opt) for opt in data["strategies"]
            ]
            
            return Strategy(
                org_id=org_id,
                current_nsi=current_nsi,
                top_risks=top_risks,
                options=options
            )
        except (json.JSONDecodeError, KeyError) as e:
            raise ValueError(f"Failed to simulate strategies: {e}")

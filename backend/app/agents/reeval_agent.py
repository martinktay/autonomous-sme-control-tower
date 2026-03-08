import json
from pathlib import Path
from typing import Dict, Any
from app.utils.bedrock_client import get_bedrock_client


class ReevalAgent:
    """Agent for outcome re-evaluation"""
    
    def __init__(self):
        self.bedrock = get_bedrock_client()
        self.prompts_dir = Path("prompts/v1")
    
    def evaluate_outcome(
        self,
        predicted_improvement: float,
        actual_nsi_before: float,
        actual_nsi_after: float,
        strategy_description: str,
        execution_log: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Evaluate action outcome and prediction accuracy"""
        
        prompt_path = self.prompts_dir / "reeval.md"
        prompt_template = prompt_path.read_text()
        
        actual_improvement = actual_nsi_after - actual_nsi_before
        
        context = f"""
Predicted NSI Improvement: {predicted_improvement}
Actual NSI Before: {actual_nsi_before}
Actual NSI After: {actual_nsi_after}
Actual Improvement: {actual_improvement}
Strategy: {strategy_description}
Execution Log: {json.dumps(execution_log, indent=2)}
"""
        
        prompt = f"{prompt_template}\n\n{context}"
        
        response = self.bedrock.invoke_nova_lite(prompt, temperature=0.3)
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {"error": "Failed to evaluate outcome"}

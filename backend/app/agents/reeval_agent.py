import json
import uuid
from typing import Dict, Any
from datetime import datetime, timezone
from app.utils.bedrock_client import get_bedrock_client
from app.utils.prompt_loader import load_prompt
from app.utils.json_guard import parse_json_safely, clean_model_output
from app.models import Evaluation


class ReevalAgent:
    """Agent for outcome re-evaluation"""
    
    def __init__(self):
        self.bedrock = get_bedrock_client()
    
    def evaluate_outcome(
        self,
        org_id: str,
        execution_id: str,
        predicted_improvement: float,
        actual_nsi_before: float,
        actual_nsi_after: float,
        strategy_description: str,
        execution_log: Dict[str, Any]
    ) -> Evaluation:
        """Evaluate action outcome and prediction accuracy"""
        
        prompt_template = load_prompt("reeval")
        
        actual_improvement = actual_nsi_after - actual_nsi_before
        
        context = f"""
Predicted NSI Improvement: {predicted_improvement}
Actual NSI Before: {actual_nsi_before}
Actual NSI After: {actual_nsi_after}
Actual Improvement: {actual_improvement}
Strategy: {strategy_description}
Execution Log: {json.dumps(execution_log, indent=2, default=str)}
"""
        
        prompt = f"{prompt_template}\n\n{context}"
        
        response = self.bedrock.invoke_nova_lite(prompt, temperature=0.3)
        
        parsed = clean_model_output(parse_json_safely(response))
        
        # Calculate prediction accuracy
        if predicted_improvement != 0:
            accuracy = 1 - abs(predicted_improvement - actual_improvement) / abs(predicted_improvement)
        else:
            accuracy = 0.0
        
        evaluation = Evaluation(
            evaluation_id=f"eval_{uuid.uuid4().hex[:12]}",
            org_id=org_id,
            execution_id=execution_id,
            old_nsi=actual_nsi_before,
            new_nsi=actual_nsi_after,
            predicted_improvement=predicted_improvement,
            actual_improvement=actual_improvement,
            prediction_accuracy=max(0.0, min(1.0, accuracy)),
            timestamp=datetime.now(timezone.utc)
        )
        
        return evaluation

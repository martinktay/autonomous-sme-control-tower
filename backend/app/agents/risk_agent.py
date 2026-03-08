import json
from pathlib import Path
from typing import Dict, Any, List
from app.utils.bedrock_client import get_bedrock_client
from app.utils.json_guard import safe_json_parse
from app.models import NSIScore, SubIndices


class RiskAgent:
    """Agent for risk diagnosis and NSI calculation"""
    
    def __init__(self):
        self.bedrock = get_bedrock_client()
        self.prompts_dir = Path("prompts/v1")
    
    def calculate_nsi(
        self,
        org_id: str,
        signals: List[Dict[str, Any]],
        context: Dict[str, Any]
    ) -> NSIScore:
        """Calculate Nova Stability Index"""
        
        prompt_path = self.prompts_dir / "risk-diagnosis.md"
        prompt_template = prompt_path.read_text()
        
        signals_summary = json.dumps(signals, indent=2)
        context_summary = json.dumps(context, indent=2)
        
        prompt = f"{prompt_template}\n\nSignals:\n{signals_summary}\n\nContext:\n{context_summary}"
        
        response = self.bedrock.invoke_nova_lite(prompt, temperature=0.5)
        
        parsed = safe_json_parse(response)
        if parsed:
            sub_indices = SubIndices(
                liquidity_index=parsed["liquidity_index"],
                revenue_stability_index=parsed["revenue_stability_index"],
                operational_latency_index=parsed["operational_latency_index"],
                vendor_risk_index=parsed["vendor_risk_index"]
            )
            
            return NSIScore(
                org_id=org_id,
                sub_indices=sub_indices,
                nova_stability_index=parsed["nova_stability_index"],
                top_risks=parsed["top_risks"],
                explanation=parsed["explanation"],
                signal_count=len(signals)
            )
        
        raise ValueError("Failed to calculate NSI")

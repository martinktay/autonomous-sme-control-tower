"""
Risk Agent - Handles risk diagnosis and BSI calculation

This agent uses the prompt loader utility to load templates from /prompts/v1/
and validates responses against Pydantic schemas for type safety.
"""

import json
from typing import Dict, Any, List
from datetime import datetime, timezone
from app.utils.bedrock_client import get_bedrock_client
from app.utils.prompt_loader import load_prompt
from app.utils.json_guard import parse_json_safely, clean_model_output
from app.models import BSIScore, SubIndices


class RiskAgent:
    """
    Agent for risk diagnosis and BSI calculation
    
    Implements Requirements 4.1-4.5 (BSI calculation and risk assessment)
    Uses prompt templates from /prompts/v1/ (Requirement 13.1, 13.2)
    """
    
    def __init__(self):
        self.bedrock = get_bedrock_client()
    
    def calculate_bsi(
        self,
        org_id: str,
        signals: List[Dict[str, Any]],
        context: Dict[str, Any]
    ) -> BSIScore:
        """
        Calculate Business Stability Index
        
        Args:
            org_id: Organization identifier
            signals: List of operational signals (invoices, emails, etc.)
            context: Additional business context
            
        Returns:
            BSIScore object with calculated indices and risk assessment
        """
        # Load prompt template using the new prompt loader utility
        prompt_template = load_prompt("risk-diagnosis")
        
        # Prepare signal and context summaries
        signals_summary = json.dumps(signals[:10], indent=2)  # Limit to recent signals
        context_summary = json.dumps(context, indent=2)
        
        # Construct full prompt
        prompt = f"{prompt_template}\n\nSignals:\n{signals_summary}\n\nContext:\n{context_summary}"
        
        # Invoke Nova 2 Lite model
        response = self.bedrock.invoke_nova_lite(prompt, temperature=0.5)
        
        # Parse and validate JSON response (Requirement 13.3, 13.4)
        parsed = clean_model_output(parse_json_safely(response))
        
        # Build sub-indices
        sub_indices = SubIndices(
            liquidity_index=parsed.get("liquidity_index", 50.0),
            revenue_stability_index=parsed.get("revenue_stability_index", 50.0),
            operational_latency_index=parsed.get("operational_latency_index", 50.0),
            vendor_risk_index=parsed.get("vendor_risk_index", 50.0)
        )
        
        # Normalize top_risks: model may return strings instead of dicts
        raw_risks = parsed.get("top_risks", [])
        top_risks = []
        for r in raw_risks:
            if isinstance(r, dict):
                top_risks.append(r)
            elif isinstance(r, str):
                top_risks.append({"risk": r, "severity": "medium"})
        
        # Return BSI score object
        return BSIScore(
            org_id=org_id,
            sub_indices=sub_indices,
            business_stability_index=parsed.get("business_stability_index", 50.0),
            top_risks=top_risks,
            explanation=parsed.get("explanation", "BSI calculated from available signals"),
            signal_count=len(signals),
            timestamp=datetime.now(timezone.utc),
            confidence=parsed.get("confidence", "medium")
        )

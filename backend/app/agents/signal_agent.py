import json
from pathlib import Path
from typing import Dict, Any
from app.utils.bedrock_client import get_bedrock_client
from app.utils.json_guard import safe_json_parse


class SignalAgent:
    """Agent for signal intake and extraction"""
    
    def __init__(self):
        self.bedrock = get_bedrock_client()
        self.prompts_dir = Path("prompts/v1")
    
    def extract_invoice(self, invoice_text: str) -> Dict[str, Any]:
        """Extract structured data from invoice"""
        
        prompt_path = self.prompts_dir / "signal-invoice.md"
        prompt_template = prompt_path.read_text()
        
        prompt = f"{prompt_template}\n\nInvoice text:\n{invoice_text}"
        
        response = self.bedrock.invoke_nova_lite(prompt, temperature=0.3)
        
        parsed = safe_json_parse(response)
        if parsed:
            return parsed
        
        return {"error": "Failed to parse invoice"}
    
    def classify_email(
        self,
        subject: str,
        body: str,
        sender: str
    ) -> Dict[str, Any]:
        """Classify and extract email information"""
        
        prompt_path = self.prompts_dir / "signal-email.md"
        prompt_template = prompt_path.read_text()
        
        email_content = f"Subject: {subject}\nFrom: {sender}\n\n{body}"
        prompt = f"{prompt_template}\n\nEmail:\n{email_content}"
        
        response = self.bedrock.invoke_nova_lite(prompt, temperature=0.3)
        
        parsed = safe_json_parse(response)
        if parsed:
            return parsed
        
        return {"error": "Failed to classify email"}

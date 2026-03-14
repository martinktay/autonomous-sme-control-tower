"""
Signal Agent - Handles invoice and email signal intake

This agent uses the prompt loader utility to load templates from /prompts/v1/
and validates responses against Pydantic schemas for type safety.
"""

from typing import Dict, Any
from app.utils.bedrock_client import get_bedrock_client
from app.utils.prompt_loader import load_prompt
from app.utils.json_guard import parse_json_safely


class SignalAgent:
    """
    Agent for signal intake and extraction
    
    Implements Requirements 1.1-1.5 (Invoice processing) and 2.1-2.5 (Email processing)
    Uses prompt templates from /prompts/v1/ (Requirement 13.1, 13.2)
    """
    
    def __init__(self):
        self.bedrock = get_bedrock_client()
    
    def extract_invoice(self, invoice_text: str) -> Dict[str, Any]:
        """
        Extract structured data from invoice
        
        Args:
            invoice_text: Raw invoice text or OCR output
            
        Returns:
            Parsed invoice data as dictionary
            
        Raises:
            ValueError: If JSON parsing fails
        """
        # Load prompt template using the new prompt loader utility
        prompt_template = load_prompt("signal-invoice")
        
        # Construct full prompt with invoice text
        prompt = f"{prompt_template}\n\nInvoice text:\n{invoice_text}"
        
        # Invoke Nova 2 Lite model
        response = self.bedrock.invoke_nova_lite(prompt, temperature=0.3)
        
        # Parse and validate JSON response (Requirement 13.3, 13.4)
        parsed = parse_json_safely(response)
        return parsed
    
    def classify_email(
        self,
        subject: str,
        body: str,
        sender: str
    ) -> Dict[str, Any]:
        """
        Classify and extract email information
        
        Args:
            subject: Email subject line
            body: Email body content
            sender: Email sender address
            
        Returns:
            Parsed email classification data as dictionary
            
        Raises:
            ValueError: If JSON parsing fails
        """
        # Load prompt template using the new prompt loader utility
        prompt_template = load_prompt("signal-email")
        
        # Construct email content
        email_content = f"Subject: {subject}\nFrom: {sender}\n\n{body}"
        prompt = f"{prompt_template}\n\nEmail:\n{email_content}"
        
        # Invoke Nova 2 Lite model
        response = self.bedrock.invoke_nova_lite(prompt, temperature=0.3)
        
        # Parse and validate JSON response (Requirement 13.3, 13.4)
        parsed = parse_json_safely(response)
        return parsed

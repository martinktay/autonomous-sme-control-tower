"""
Finance Document Agent - Handles document extraction, classification, and informal receipt parsing

Uses prompt templates from /prompts/v1/ for Nova Lite model invocations.
Implements Requirements 2.1-2.6, 3.1-3.5, 5.1-5.5, 6.1-6.6, 14.4-14.6.
"""

from typing import Dict, Any, Optional
from app.utils.bedrock_client import get_bedrock_client
from app.utils.prompt_loader import load_prompt
from app.utils.json_guard import parse_json_safely, clean_model_output


class FinanceDocumentAgent:
    """
    Agent for financial document processing

    Provides extraction, classification, and informal receipt parsing
    via AWS Bedrock Nova Lite model with prompt templates.
    """

    def __init__(self):
        self.bedrock = get_bedrock_client()

    def extract_document(self, raw_text: str, currency_hint: Optional[str] = None) -> Dict[str, Any]:
        """
        Extract structured financial fields from raw document text.

        Loads the finance-document-extraction prompt, substitutes the document
        text, invokes Nova Lite, and parses the JSON response. For GBP documents
        VAT fields are always populated (Req 5.1-5.5).

        Args:
            raw_text: Raw text or OCR output from a financial document.
            currency_hint: Optional currency hint (e.g. "GBP", "NGN") to guide extraction.

        Returns:
            Dict with vendor_name, amount, currency, document_date, description,
            vat_amount, vat_rate.

        Raises:
            ValueError: If JSON parsing fails.
        """
        text_with_hint = raw_text
        if currency_hint:
            text_with_hint = f"[Currency hint: {currency_hint}]\n\n{raw_text}"

        prompt = load_prompt("finance-document-extraction", variables={"document_text": text_with_hint})

        response = self.bedrock.invoke_nova_lite(prompt, temperature=0.3)

        parsed = parse_json_safely(response)
        return clean_model_output(parsed)

    def classify_document(self, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Classify a financial document as revenue or expense.

        Loads the finance-document-classification prompt, substitutes extracted
        fields, invokes Nova Lite, and returns category with confidence score
        (Req 3.1-3.5).

        Args:
            extracted_data: Dict containing vendor_name, amount, currency,
                document_date, and description.

        Returns:
            Dict with category ("revenue" or "expense") and confidence_score (0.0-1.0).

        Raises:
            ValueError: If JSON parsing fails.
        """
        prompt = load_prompt("finance-document-classification", variables={
            "vendor_name": extracted_data.get("vendor_name", "Unknown"),
            "amount": extracted_data.get("amount", 0),
            "currency": extracted_data.get("currency", "USD"),
            "document_date": extracted_data.get("document_date", "Unknown"),
            "description": extracted_data.get("description", "No description"),
        })

        response = self.bedrock.invoke_nova_lite(prompt, temperature=0.3)

        parsed = parse_json_safely(response)
        return clean_model_output(parsed)

    def parse_informal_receipt(self, raw_text: str) -> Dict[str, Any]:
        """
        Parse an informal Nigerian receipt (POS slip, handwritten receipt, etc.).

        Loads the finance-informal-receipt prompt, substitutes the document text,
        invokes Nova Lite, and returns extracted fields with currency defaulting
        to NGN (Req 6.1-6.6).

        Args:
            raw_text: Raw text or OCR output from an informal Nigerian document.

        Returns:
            Dict with vendor_name, amount, currency (NGN), document_date,
            description, vat_amount (null), vat_rate (null).

        Raises:
            ValueError: If JSON parsing fails.
        """
        prompt = load_prompt("finance-informal-receipt", variables={"document_text": raw_text})

        response = self.bedrock.invoke_nova_lite(prompt, temperature=0.3)

        parsed = parse_json_safely(response)
        return clean_model_output(parsed)

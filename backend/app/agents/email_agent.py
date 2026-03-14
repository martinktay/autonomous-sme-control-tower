"""
Email Agent — Reads business emails, classifies them, and extracts actionable tasks.

Pipeline:
1. classify_email  → category, priority, sentiment via signal-email prompt
2. extract_tasks   → structured task list via email-task-extraction prompt
3. generate_reply_draft → plain-text reply using Nova Lite

Uses prompt templates from /prompts/v1/ for Nova Lite model invocations.
"""

from typing import Dict, Any, List
from app.utils.bedrock_client import get_bedrock_client
from app.utils.prompt_loader import load_prompt
from app.utils.json_guard import parse_json_safely


class EmailAgent:
    """AI agent for email analysis: classification, task extraction, and reply drafting."""

    def __init__(self):
        self.bedrock = get_bedrock_client()

    def classify_email(self, subject: str, body: str, sender: str) -> Dict[str, Any]:
        """Classify an email using the signal-email prompt template.

        Args:
            subject: Email subject line.
            body: Email body text.
            sender: Sender email address.

        Returns:
            Dict with category, priority, action_required, entities, summary, sentiment.
        """
        prompt = load_prompt("signal-email")
        # Combine email fields into a single block for the model
        email_content = f"Subject: {subject}\nFrom: {sender}\n\n{body}"
        full_prompt = f"{prompt}\n\nEmail:\n{email_content}"

        response = self.bedrock.invoke_nova_lite(full_prompt, temperature=0.3)
        return parse_json_safely(response)

    def extract_tasks(self, subject: str, body: str, sender: str) -> Dict[str, Any]:
        """Extract actionable tasks from an email using the email-task-extraction prompt.

        Args:
            subject: Email subject line.
            body: Email body text.
            sender: Sender email address.

        Returns:
            Dict with tasks list, email_summary, sentiment, requires_immediate_attention.
        """
        # Build email content and inject into the prompt template via {email_content} variable
        email_content = f"Subject: {subject}\nFrom: {sender}\n\n{body}"
        prompt = load_prompt(
            "email-task-extraction",
            variables={"email_content": email_content},
        )

        response = self.bedrock.invoke_nova_lite(prompt, temperature=0.3)
        return parse_json_safely(response)

    def generate_reply_draft(self, subject: str, body: str, sender: str, tone: str = "professional") -> str:
        """Generate a draft reply for an email using an inline prompt (no template file).

        Args:
            subject: Original email subject.
            body: Original email body.
            sender: Original sender address.
            tone: Desired reply tone (e.g. 'professional', 'friendly').

        Returns:
            Plain-text draft reply string.
        """
        prompt = (
            f"You are a professional business assistant. Draft a {tone} reply to this email.\n\n"
            f"Subject: {subject}\nFrom: {sender}\n\n{body}\n\n"
            "Write only the reply body text. No JSON. Keep it concise and actionable."
        )
        return self.bedrock.invoke_nova_lite(prompt, temperature=0.5, max_tokens=500)

"""
Voice Agent — operational queries, briefings, and free-form Q&A.

Provides two interaction modes:
1. Structured queries (stability, overdue invoices, risks) via keyword matching
2. Free-form business questions answered by Nova Lite with full context fallback

Also generates audio briefings via Nova Sonic and text-to-speech.
"""

import json
import logging
from typing import Dict, Any, Optional, List
from app.utils.bedrock_client import get_bedrock_client
from app.utils.prompt_loader import load_prompt
from app.utils.json_guard import strip_markdown

logger = logging.getLogger(__name__)


class VoiceAgent:
    """Agent for voice briefings, structured queries, and AI-powered Q&A."""

    def __init__(self):
        self.bedrock = get_bedrock_client()

    def transcribe_query(self, audio_data: bytes) -> Optional[str]:
        """Transcribe voice audio to text using Nova Sonic."""
        try:
            transcribed_text = self.bedrock.transcribe_audio(audio_data)
            if not transcribed_text:
                logger.error("Transcription returned empty result")
                return None
            logger.info(f"Transcribed query: {transcribed_text[:50]}...")
            return transcribed_text
        except Exception as e:
            logger.error(f"Transcription failed: {e}", exc_info=True)
            return None

    def process_text_query(
        self,
        query: str,
        bsi_score: float,
        signals: list,
        risks: list,
    ) -> str:
        """Route a text query to the appropriate keyword-based handler."""
        query_lower = query.lower().strip()

        if "stable" in query_lower or "stability" in query_lower or "bsi" in query_lower:
            return self._generate_stability_response(bsi_score, risks)
        elif "invoice" in query_lower and "overdue" in query_lower:
            return self._generate_overdue_invoices_response(signals)
        elif "risk" in query_lower:
            return self._generate_risks_response(risks)
        else:
            return "I can help you with questions about business stability, overdue invoices, and operational risks."

    def _generate_stability_response(self, bsi_score: float, risks: list) -> str:
        if bsi_score >= 70:
            stability_level = "stable"
        elif bsi_score >= 40:
            stability_level = "moderately stable"
        else:
            stability_level = "unstable"

        response = f"Your business is currently {stability_level} with a BSI score of {bsi_score:.1f} out of 100. "
        if risks:
            top_risk = risks[0] if isinstance(risks[0], str) else risks[0].get("description", "operational issues")
            response += f"Your top concern is {top_risk}."
        return response

    def _generate_overdue_invoices_response(self, signals: list) -> str:
        overdue_count = sum(
            1 for s in signals
            if s.get("signal_type") == "invoice" and s.get("status") == "overdue"
        )
        if overdue_count == 0:
            return "You have no overdue invoices at this time."
        elif overdue_count == 1:
            return "You have 1 overdue invoice that needs attention."
        else:
            return f"You have {overdue_count} overdue invoices that need attention."

    def _generate_risks_response(self, risks: list) -> str:
        if not risks:
            return "No significant operational risks detected at this time."
        risk_count = len(risks)
        top_risk = risks[0] if isinstance(risks[0], str) else risks[0].get("description", "operational issues")
        return f"You have {risk_count} operational risks. Your top risk is {top_risk}."

    def answer_business_query(
        self,
        question: str,
        bsi_data: Optional[Dict[str, Any]] = None,
        signals: Optional[List[Dict[str, Any]]] = None,
        risks: Optional[List] = None,
        pnl: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Answer a free-form business question using AI with full context."""
        context = self._build_business_context(bsi_data, signals, risks, pnl)
        try:
            answer = self._answer_with_bedrock(question, context)
            return {"answer": answer, "source": "ai"}
        except Exception as e:
            logger.warning(f"Bedrock query failed, using fallback: {e}")
            answer = self._answer_fallback(question, bsi_data, signals, risks, pnl)
            return {"answer": answer, "source": "rule"}

    def _build_business_context(self, bsi_data, signals, risks, pnl) -> str:
        parts: List[str] = []
        if bsi_data:
            score = bsi_data.get("business_stability_index", "N/A")
            parts.append(f"Business Health Score (BSI): {score}/100")
            top_risks = bsi_data.get("top_risks", [])
            if top_risks:
                parts.append(f"Top risks: {', '.join(str(r) for r in top_risks[:5])}")
        if signals:
            overdue = [s for s in signals if s.get("status") == "overdue"]
            parts.append(f"Total signals: {len(signals)}, Overdue invoices: {len(overdue)}")
        if pnl:
            parts.append(f"Revenue: {pnl.get('total_revenue', 0):.2f}")
            parts.append(f"Expenses: {pnl.get('total_expenses', 0):.2f}")
            parts.append(f"Net profit: {pnl.get('net_profit', 0):.2f}")
            tax_summary = pnl.get("tax_summary", {})
            if tax_summary:
                tax_lines = [f"  {k}: {v:.2f}" for k, v in tax_summary.items() if v]
                if tax_lines:
                    parts.append("Tax summary:\n" + "\n".join(tax_lines))
        return "\n".join(parts) if parts else "No business data available yet."

    def _answer_with_bedrock(self, question: str, context: str) -> str:
        template = load_prompt("voice-query")
        prompt = template.replace("{business_context}", context).replace("{question}", question)
        response = self.bedrock.invoke_nova_lite(prompt, temperature=0.5)
        return strip_markdown(response.strip())

    def _answer_fallback(self, question, bsi_data, signals, risks, pnl) -> str:
        q = question.lower()
        if any(w in q for w in ["health", "score", "bsi", "stable", "stability", "doing"]):
            score = bsi_data.get("business_stability_index", 0) if bsi_data else 0
            level = "healthy" if score >= 70 else "moderate" if score >= 40 else "at risk"
            return f"Your business health score is {score:.1f} out of 100, that is {level}."
        if "invoice" in q or "overdue" in q:
            if signals:
                overdue = [s for s in signals if s.get("status") == "overdue"]
                return f"You have {len(overdue)} overdue invoice(s) out of {len(signals)} total."
            return "No invoice data available yet. Upload invoices to get started."
        if "risk" in q:
            if risks:
                top = risks[0] if isinstance(risks[0], str) else risks[0].get("description", "operational issues")
                return f"Your top risk is {top}. You have {len(risks)} risk(s) flagged right now."
            return "No risks flagged right now."
        if any(w in q for w in ["revenue", "profit", "income", "earning"]):
            if pnl:
                return (
                    f"Revenue: {pnl.get('total_revenue', 0):,.2f}, "
                    f"Expenses: {pnl.get('total_expenses', 0):,.2f}, "
                    f"Net profit: {pnl.get('net_profit', 0):,.2f}."
                )
            return "No financial data available yet. Upload invoices or spreadsheets to see your P&L."
        if "tax" in q:
            if pnl and pnl.get("tax_summary"):
                ts = pnl["tax_summary"]
                lines = [f"{k}: {v:,.2f}" for k, v in ts.items() if v]
                total = sum(v for v in ts.values() if v)
                return f"Tax position: {', '.join(lines)}. Total tax burden: {total:,.2f}."
            return "No tax data available yet. Include tax columns when uploading spreadsheets."
        return "I can answer questions about your health score, invoices, risks, revenue, profit, and taxes. Try asking one of those."

    def generate_voice_response(
        self,
        query: str,
        bsi_score: float,
        signals: list,
        risks: list,
    ) -> Dict[str, Any]:
        """Generate voice response for query"""
        try:
            response_text = self.process_text_query(query, bsi_score, signals, risks)
            audio_data = self.bedrock.invoke_nova_sonic(response_text)
            logger.info(f"Generated voice response for query: {query[:50]}...")
            return {
                "response_text": response_text,
                "audio_data": audio_data,
                "success": True,
            }
        except Exception as e:
            logger.error(f"Error generating voice response: {e}", exc_info=True)
            return {
                "response_text": "I'm sorry, I encountered an error processing your request.",
                "audio_data": None,
                "success": False,
                "error": str(e),
            }

    def generate_briefing_text(
        self,
        bsi_score: float,
        top_risks: list,
        recent_actions: list,
        trend: str,
    ) -> str:
        """Generate operational briefing text"""
        try:
            prompt_template = load_prompt("voice")
            risks_text = ", ".join(top_risks[:3]) if top_risks else "no significant risks"
            actions_text = f"{len(recent_actions)} actions" if recent_actions else "no recent actions"
            context = f"""
Current BSI Score: {bsi_score:.1f}
Trend: {trend}
Top Risks: {risks_text}
Recent Actions: {actions_text}
"""
            prompt = f"{prompt_template}\n\nContext:\n{context}\n\nGenerate a concise operational briefing."
            briefing = self.bedrock.invoke_nova_lite(prompt, temperature=0.7)
            logger.info("Generated operational briefing")
            return strip_markdown(briefing)
        except Exception as e:
            logger.error(f"Error generating briefing: {e}", exc_info=True)
            return f"Your business stability score is {bsi_score:.1f}. {trend.capitalize()} trend detected."

    def generate_audio(self, text: str) -> Optional[bytes]:
        """Generate audio from text using Nova Sonic"""
        try:
            audio_data = self.bedrock.invoke_nova_sonic(text)
            logger.info(f"Generated audio for text: {text[:50]}...")
            return audio_data
        except Exception as e:
            logger.error(f"Audio generation failed: {e}", exc_info=True)
            return None


_voice_agent: Optional[VoiceAgent] = None


def get_voice_agent() -> VoiceAgent:
    """Get singleton voice agent instance"""
    global _voice_agent
    if _voice_agent is None:
        _voice_agent = VoiceAgent()
    return _voice_agent

"""
Voice Agent — operational queries, briefings, and free-form Q&A.

Provides two interaction modes:
1. Structured queries (stability, overdue invoices, risks) via keyword matching
2. Free-form business questions answered by Nova Lite with full context fallback

Also generates audio briefings via Nova Sonic and text-to-speech.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from app.utils.bedrock_client import get_bedrock_client
from app.utils.prompt_loader import load_prompt

logger = logging.getLogger(__name__)


class VoiceAgent:
    """Agent for voice briefings, structured queries, and AI-powered Q&A."""

    def __init__(self):
        self.bedrock = get_bedrock_client()
        self.supported_queries = [
            "how stable is my business",
            "which invoices are overdue",
            "what are my top risks",
            "what is my nsi score",
        ]

    def transcribe_query(self, audio_data: bytes) -> Optional[str]:
        """Transcribe voice audio to text using Nova Sonic.

        Returns:
            Transcribed text string, or None on failure.
        """
        try:
            transcribed_text = self.bedrock.transcribe_audio(audio_data)
            if not transcribed_text:
                logger.error("Transcription returned empty result")
                return None
            logger.info(f"Transcribed: {transcribed_text[:50]}...")
            return transcribed_text
        except Exception as e:
            logger.error(f"Transcription failed: {e}", exc_info=True)
            return None

    def process_text_query(self, query, nsi_score, signals, risks):
        """Route a text query to the appropriate keyword-based handler."""
        q = query.lower().strip()
        if "stable" in q or "stability" in q or "nsi" in q:
            return self._generate_stability_response(nsi_score, risks)
        elif "invoice" in q and "overdue" in q:
            return self._generate_overdue_invoices_response(signals)
        elif "risk" in q:
            return self._generate_risks_response(risks)
        else:
            return "I can help you with questions about business stability, overdue invoices, and operational risks."

    def _generate_stability_response(self, nsi_score, risks):
        if nsi_score >= 70:
            level = "stable"
        elif nsi_score >= 40:
            level = "moderately stable"
        else:
            level = "unstable"
        resp = f"Your business is currently {level} with an NSI score of {nsi_score:.1f} out of 100. "
        if risks:
            tr = risks[0] if isinstance(risks[0], str) else risks[0].get("description", "operational issues")
            resp += f"Your top concern is {tr}."
        return resp

    def _generate_overdue_invoices_response(self, signals):
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

    def _generate_risks_response(self, risks):
        if not risks:
            return "No significant operational risks detected at this time."
        risk_count = len(risks)
        tr = risks[0] if isinstance(risks[0], str) else risks[0].get("description", "operational issues")
        return f"You have {risk_count} operational risks. Your top risk is {tr}."

    def answer_business_query(self, question, nsi_data=None, signals=None, risks=None, pnl=None):
        """Answer a free-form question: tries Bedrock first, falls back to keyword rules.

        Returns:
            Dict with 'answer' (str) and 'source' ('ai' or 'rule').
        """
        context = self._build_business_context(nsi_data, signals, risks, pnl)
        try:
            answer = self._answer_with_bedrock(question, context)
            return {"answer": answer, "source": "ai"}
        except Exception as e:
            logger.warning(f"Bedrock query failed, using fallback: {e}")
            answer = self._answer_fallback(question, nsi_data, signals, risks, pnl)
            return {"answer": answer, "source": "rule"}

    def _build_business_context(self, nsi_data, signals, risks, pnl):
        """Assemble a plain-text context block from all available business data."""
        parts = []
        if nsi_data:
            score = nsi_data.get("nova_stability_index", "N/A")
            parts.append(f"Business Health Score (NSI): {score}/100")
            tr = nsi_data.get("top_risks", [])
            if tr:
                rstr = ', '.join(str(r) for r in tr[:5])
                parts.append(f"Top risks: {rstr}")
        if signals:
            od = [s for s in signals if s.get("status") == "overdue"]
            parts.append(f"Total signals: {len(signals)}, Overdue: {len(od)}")
        if pnl:
            rev = pnl.get('total_revenue', 0)
            exp = pnl.get('total_expenses', 0)
            net = pnl.get('net_profit', 0)
            parts.append(f"Revenue: {rev:.2f}")
            parts.append(f"Expenses: {exp:.2f}")
            parts.append(f"Net profit: {net:.2f}")
            ts = pnl.get("tax_summary", {})
            if ts:
                tl = [f"  {k}: {v:.2f}" for k, v in ts.items() if v]
                if tl:
                    parts.append('Tax summary:\n' + '\n'.join(tl))
        if not parts:
            return 'No business data available yet.'
        return '\n'.join(parts)

    def _answer_with_bedrock(self, question, context):
        """Send question + context to Nova Lite via the voice-query prompt template."""
        template = load_prompt("voice-query")
        prompt = template.replace("{business_context}", context)
        prompt = prompt.replace("{question}", question)
        response = self.bedrock.invoke_nova_lite(prompt, temperature=0.5)
        return response.strip()

    def _answer_fallback(self, question, nsi_data, signals, risks, pnl):
        """Keyword-based fallback when Bedrock is unavailable."""
        q = question.lower()
        if any(w in q for w in ["health", "score", "nsi", "stable", "stability", "doing"]):
            score = nsi_data.get("nova_stability_index", 0) if nsi_data else 0
            level = "healthy" if score >= 70 else "moderate" if score >= 40 else "at risk"
            return f"Your business health score is {score:.1f}/100, that is {level}."
        if "invoice" in q or "overdue" in q:
            if signals:
                od = [s for s in signals if s.get("status") == "overdue"]
                return f"You have {len(od)} overdue invoice(s) out of {len(signals)} total."
            return "No invoice data yet. Upload invoices to get started."
        if "risk" in q:
            if risks:
                t = risks[0] if isinstance(risks[0], str) else risks[0].get("description", "issues")
                return f"You have {len(risks)} risk(s). Top concern: {t}."
            return "No significant risks detected right now."
        if any(w in q for w in ["revenue", "profit", "income", "earning"]):
            if pnl:
                rev = pnl.get('total_revenue', 0)
                exp = pnl.get('total_expenses', 0)
                net = pnl.get('net_profit', 0)
                return f"Revenue: {rev:,.2f}, Expenses: {exp:,.2f}, Net profit: {net:,.2f}."
            return "No financial data yet. Upload invoices or spreadsheets."
        if "tax" in q:
            if pnl and pnl.get("tax_summary"):
                ts = pnl["tax_summary"]
                tlines = [f"{k}: {v:,.2f}" for k, v in ts.items() if v]
                total = sum(v for v in ts.values() if v)
                if tlines:
                    joined = ', '.join(tlines)
                    return f"Tax position: {joined}. Total burden: {total:,.2f}."
                return "No tax amounts recorded yet. Upload documents with tax data."
            return "No tax data yet. Include tax columns when uploading spreadsheets."
        return "I can answer questions about your health score, invoices, risks, revenue, profit, and taxes."

    def generate_voice_response(self, query, nsi_score, signals, risks):
        """Generate a full voice response: text answer + Nova Sonic audio bytes."""
        try:
            response_text = self.process_text_query(query, nsi_score, signals, risks)
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
                "response_text": "Sorry, I encountered an error processing your request.",
                "audio_data": None,
                "success": False,
                "error": str(e),
            }

    def generate_briefing_text(self, nsi_score, top_risks, recent_actions, trend):
        """Generate a concise operational briefing using the voice prompt template."""
        try:
            prompt_template = load_prompt("voice")
            risks_text = ", ".join(top_risks[:3]) if top_risks else "no significant risks"
            actions_text = f"{len(recent_actions)} actions" if recent_actions else "no recent actions"
            context = (
                f"Current NSI Score: {nsi_score:.1f}\n"
                f"Trend: {trend}\n"
                f"Top Risks: {risks_text}\n"
                f"Recent Actions: {actions_text}"
            )
            prompt = f"{prompt_template}\n\nContext:\n{context}\n\nGenerate a concise operational briefing."
            briefing = self.bedrock.invoke_nova_lite(prompt, temperature=0.7)
            logger.info("Generated operational briefing")
            return briefing
        except Exception as e:
            logger.error(f"Error generating briefing: {e}", exc_info=True)
            return f"Your business stability score is {nsi_score:.1f}. {trend.capitalize()} trend detected."

    def generate_audio(self, text: str) -> Optional[bytes]:
        """Convert text to audio bytes using Nova Sonic. Returns None on failure."""
        try:
            audio_data = self.bedrock.invoke_nova_sonic(text)
            logger.info(f"Generated audio for text: {text[:50]}...")
            return audio_data
        except Exception as e:
            logger.error(f"Audio generation failed: {e}", exc_info=True)
            return None


_voice_agent: Optional[VoiceAgent] = None


def get_voice_agent() -> VoiceAgent:
    """Get singleton VoiceAgent instance (lazy-initialised)."""
    global _voice_agent
    if _voice_agent is None:
        _voice_agent = VoiceAgent()
    return _voice_agent

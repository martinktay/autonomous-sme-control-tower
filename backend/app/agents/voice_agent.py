from pathlib import Path
from typing import Dict, Any
from app.utils.bedrock_client import get_bedrock_client


class VoiceAgent:
    """Agent for voice briefings via Nova Sonic"""
    
    def __init__(self):
        self.bedrock = get_bedrock_client()
        self.prompts_dir = Path("prompts/v1")
    
    def generate_briefing_text(
        self,
        nsi_score: float,
        top_risks: list,
        recent_actions: list,
        trend: str
    ) -> str:
        """Generate briefing text"""
        
        prompt_path = self.prompts_dir / "voice.md"
        prompt_template = prompt_path.read_text()
        
        context = f"""
NSI Score: {nsi_score}
Trend: {trend}
Top Risks: {', '.join(top_risks)}
Recent Actions: {len(recent_actions)} actions completed
"""
        
        prompt = f"{prompt_template}\n\n{context}"
        
        return self.bedrock.invoke_nova_lite(prompt, temperature=0.7)
    
    def generate_audio(self, text: str) -> bytes:
        """Generate audio briefing using Nova Sonic"""
        return self.bedrock.invoke_nova_sonic(text)

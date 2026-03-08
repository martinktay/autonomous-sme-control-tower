import boto3
import json
from typing import Dict, Any, Optional
from app.config import get_settings

settings = get_settings()


class BedrockClient:
    """AWS Bedrock client wrapper for Nova models"""
    
    def __init__(self):
        self.client = boto3.client(
            "bedrock-runtime",
            region_name=settings.aws_region,
            aws_access_key_id=settings.aws_access_key_id or None,
            aws_secret_access_key=settings.aws_secret_access_key or None
        )
    
    def invoke_nova_lite(
        self,
        prompt: str,
        max_tokens: int = 2000,
        temperature: float = 0.7
    ) -> str:
        """Invoke Nova 2 Lite for text generation"""
        
        body = json.dumps({
            "prompt": prompt,
            "max_tokens": max_tokens,
            "temperature": temperature
        })
        
        response = self.client.invoke_model(
            modelId=settings.nova_lite_model_id,
            body=body
        )
        
        response_body = json.loads(response["body"].read())
        return response_body.get("completion", "")
    
    def generate_embeddings(self, text: str) -> list:
        """Generate embeddings using Nova embeddings"""
        
        body = json.dumps({"inputText": text})
        
        response = self.client.invoke_model(
            modelId=settings.nova_embeddings_model_id,
            body=body
        )
        
        response_body = json.loads(response["body"].read())
        return response_body.get("embedding", [])
    
    def invoke_nova_act(
        self,
        task: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Invoke Nova Act for agentic actions"""
        
        body = json.dumps({
            "task": task,
            "context": context or {}
        })
        
        response = self.client.invoke_model(
            modelId=settings.nova_act_model_id,
            body=body
        )
        
        return json.loads(response["body"].read())
    
    def invoke_nova_sonic(self, text: str) -> bytes:
        """Invoke Nova Sonic for voice generation"""
        
        body = json.dumps({"text": text})
        
        response = self.client.invoke_model(
            modelId=settings.nova_sonic_model_id,
            body=body
        )
        
        return response["body"].read()


_bedrock_client: Optional[BedrockClient] = None


def get_bedrock_client() -> BedrockClient:
    """Get singleton Bedrock client"""
    global _bedrock_client
    if _bedrock_client is None:
        _bedrock_client = BedrockClient()
    return _bedrock_client

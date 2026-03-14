"""
AWS Bedrock client wrapper for all Nova model invocations.

Provides a unified interface to Nova Lite (text), Nova Embeddings,
Nova Act (agentic), and Nova Sonic (voice). Includes a circuit breaker
for fault tolerance and exponential-backoff retry logic.
"""

import boto3
import json
import time
import threading
from typing import Dict, Any, Optional
from botocore.exceptions import ClientError
from app.config import get_settings

settings = get_settings()


class CircuitBreaker:
    """Thread-safe circuit breaker: opens after repeated failures, auto-resets after timeout."""
    
    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        """Args:
            failure_threshold: Consecutive failures before opening the circuit.
            timeout: Seconds to wait before transitioning from open to half-open.
        """
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half-open
        self._lock = threading.Lock()
    
    def call(self, func, *args, **kwargs):
        """Execute func through the circuit breaker; raises if circuit is open."""
        with self._lock:
            if self.state == "open":
                if time.time() - self.last_failure_time > self.timeout:
                    self.state = "half-open"
                else:
                    raise Exception("Circuit breaker is OPEN")
        
        try:
            result = func(*args, **kwargs)
            with self._lock:
                if self.state == "half-open":
                    self.state = "closed"
                    self.failure_count = 0
            return result
        except Exception as e:
            with self._lock:
                self.failure_count += 1
                self.last_failure_time = time.time()
                if self.failure_count >= self.failure_threshold:
                    self.state = "open"
            raise e


class BedrockClient:
    """Unified Bedrock client for all Nova model calls with retry and circuit-breaker protection."""
    
    def __init__(self):
        self.client = boto3.client(
            "bedrock-runtime",
            region_name=settings.aws_region,
            aws_access_key_id=settings.aws_access_key_id or None,
            aws_secret_access_key=settings.aws_secret_access_key or None
        )
        self.circuit_breaker = CircuitBreaker()
    
    def _retry_with_backoff(self, func, *args, max_retries: int = 3, **kwargs):
        """Retry with exponential backoff + jitter; skips retry on validation/auth errors."""
        for attempt in range(max_retries):
            try:
                return self.circuit_breaker.call(func, *args, **kwargs)
            except ClientError as e:
                error_code = e.response.get("Error", {}).get("Code", "")
                
                # Don't retry on validation errors
                if error_code in ["ValidationException", "AccessDeniedException"]:
                    raise e
                
                # Retry on throttling and service errors
                if attempt < max_retries - 1:
                    wait_time = (2 ** attempt) + (time.time() % 1)  # Exponential backoff with jitter
                    time.sleep(wait_time)
                else:
                    raise e
            except Exception as e:
                if attempt < max_retries - 1:
                    wait_time = (2 ** attempt) + (time.time() % 1)
                    time.sleep(wait_time)
                else:
                    raise e
    
    def invoke_nova_lite(
        self,
        prompt: str,
        max_tokens: int = 2000,
        temperature: float = 0.7
    ) -> str:
        """Invoke Nova Lite for text generation.

        Args:
            prompt: The text prompt to send.
            max_tokens: Maximum tokens in the response.
            temperature: Sampling temperature (0.0-1.0).

        Returns:
            Generated text string.
        """
        
        def _invoke():
            body = json.dumps({
                "messages": [
                    {"role": "user", "content": [{"text": prompt}]}
                ],
                "inferenceConfig": {
                    "maxTokens": max_tokens,
                    "temperature": temperature,
                },
            })
            
            response = self.client.invoke_model(
                modelId=settings.nova_lite_model_id,
                body=body
            )
            
            response_body = json.loads(response["body"].read())
            # Nova Messages API returns output.message.content[0].text
            try:
                return response_body["output"]["message"]["content"][0]["text"]
            except (KeyError, IndexError):
                return response_body.get("completion", "")
        
        return self._retry_with_backoff(_invoke)
    
    def generate_embeddings(self, text: str) -> list:
        """Generate a vector embedding for the given text using Nova Embeddings."""
        
        def _generate():
            body = json.dumps({"inputText": text})
            
            response = self.client.invoke_model(
                modelId=settings.nova_embeddings_model_id,
                body=body
            )
            
            response_body = json.loads(response["body"].read())
            return response_body.get("embedding", [])
        
        return self._retry_with_backoff(_generate)
    
    def invoke_nova_act(
        self,
        task: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Invoke Nova Act for autonomous agentic actions.

        Args:
            task: Description of the task to perform.
            context: Optional context dict for the agent.

        Returns:
            Dict with the agent's action result.
        """
        
        def _invoke():
            body = json.dumps({
                "task": task,
                "context": context or {}
            })
            
            response = self.client.invoke_model(
                modelId=settings.nova_act_model_id,
                body=body
            )
            
            return json.loads(response["body"].read())
        
        return self._retry_with_backoff(_invoke)
    
    def invoke_nova_sonic(self, text: str) -> bytes:
        """Convert text to audio bytes using Nova Sonic (text-to-speech)."""
        
        def _invoke():
            body = json.dumps({"text": text})
            
            response = self.client.invoke_model(
                modelId=settings.nova_sonic_model_id,
                body=body
            )
            
            return response["body"].read()
        
        return self._retry_with_backoff(_invoke)

    def transcribe_audio(self, audio_data: bytes) -> str:
        """Transcribe audio bytes to text using Nova Sonic (speech-to-text)."""
        
        def _transcribe():
            import base64
            body = json.dumps({"audio": base64.b64encode(audio_data).decode("utf-8")})
            
            response = self.client.invoke_model(
                modelId=settings.nova_sonic_model_id,
                body=body
            )
            
            response_body = json.loads(response["body"].read())
            return response_body.get("transcription", "")
        
        return self._retry_with_backoff(_transcribe)


_bedrock_client: Optional[BedrockClient] = None
_bedrock_lock = threading.Lock()


def get_bedrock_client() -> BedrockClient:
    """Get singleton BedrockClient instance (thread-safe, lazy-initialised)."""
    global _bedrock_client
    if _bedrock_client is None:
        with _bedrock_lock:
            if _bedrock_client is None:
                _bedrock_client = BedrockClient()
    return _bedrock_client

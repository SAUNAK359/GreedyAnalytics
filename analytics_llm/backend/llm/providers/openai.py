"""
OpenAI LLM provider with error handling and retries
"""
from typing import Dict, Any, Optional
import logging
from analytics_llm.backend.core.config import settings
import time

try:
    from openai import OpenAI
except Exception:  # pragma: no cover - optional dependency
    OpenAI = None

logger = logging.getLogger(__name__)

def run(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute OpenAI LLM request with retries
    
    Args:
        payload: Request payload with prompt, temperature, etc.
        
    Returns:
        Response with output and metadata
    """
    max_retries = settings.LLM_MAX_RETRIES
    model = payload.get("model", settings.OPENAI_MODEL)
    
    for attempt in range(max_retries):
        try:
            if not settings.OPENAI_API_KEY or OpenAI is None:
                logger.warning("OpenAI API key not set or SDK unavailable, using mock response")
                return _mock_response(payload)

            client = OpenAI(api_key=settings.OPENAI_API_KEY)
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a helpful analytics assistant."},
                    {"role": "user", "content": payload.get("prompt", "")}
                ],
                temperature=payload.get("temperature", 0.7),
                max_tokens=payload.get("max_tokens", settings.OPENAI_MAX_TOKENS),
                timeout=settings.LLM_TIMEOUT_SECONDS
            )

            content = response.choices[0].message.content if response.choices else ""
            tokens_used = response.usage.total_tokens if response.usage else 0

            return {
                "response": content,
                "model": model,
                "tokens_used": tokens_used,
                "confidence": 0.9,
                "provider": "openai"
            }

        except Exception as e:
            logger.error(f"OpenAI execution error: {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
            else:
                return _mock_response(payload)
    
    return _mock_response(payload)


def _mock_response(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Mock response for testing/development"""
    return {
        "response": "Mock OpenAI response - API key not configured",
        "model": "mock-gpt-4",
        "tokens_used": 100,
        "confidence": 0.5,
        "provider": "openai-mock"
    }

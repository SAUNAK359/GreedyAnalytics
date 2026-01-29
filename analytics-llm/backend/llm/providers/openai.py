"""
OpenAI LLM provider with error handling and retries
"""
import openai
from typing import Dict, Any
import logging
from core.config import settings
import time

logger = logging.getLogger(__name__)

# Configure OpenAI
if settings.OPENAI_API_KEY:
    openai.api_key = settings.OPENAI_API_KEY


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
            if not settings.OPENAI_API_KEY:
                logger.warning("OpenAI API key not set, using mock response")
                return _mock_response(payload)
            
            # Make API call
            response = openai.ChatCompletion.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a helpful analytics assistant."},
                    {"role": "user", "content": payload.get("prompt", "")}
                ],
                temperature=payload.get("temperature", 0.7),
                max_tokens=payload.get("max_tokens", settings.OPENAI_MAX_TOKENS),
                timeout=settings.LLM_TIMEOUT_SECONDS
            )
            
            return {
                "response": response.choices[0].message.content,
                "model": model,
                "tokens_used": response.usage.total_tokens,
                "confidence": 0.9,
                "provider": "openai"
            }
            
        except openai.error.RateLimitError as e:
            logger.warning(f"OpenAI rate limit hit (attempt {attempt + 1}/{max_retries})")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                raise
        
        except openai.error.APIError as e:
            logger.error(f"OpenAI API error: {e}")
            if attempt < max_retries - 1:
                time.sleep(1)
            else:
                raise
        
        except Exception as e:
            logger.error(f"OpenAI execution error: {e}")
            raise
    
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

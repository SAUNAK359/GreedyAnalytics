"""
Gemma/Gemini LLM provider
"""
import google.generativeai as genai
from typing import Dict, Any
import logging
from core.config import settings
import time

logger = logging.getLogger(__name__)

# Configure Gemini (global fallback)
if settings.GEMINI_API_KEY:
    genai.configure(api_key=settings.GEMINI_API_KEY)


def run(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute Gemini LLM request
    
    Args:
        payload: Request payload
        
    Returns:
        Response with output and metadata
    """
    max_retries = settings.LLM_MAX_RETRIES
    model_name = payload.get("model", settings.GEMMA_MODEL)
    
    for attempt in range(max_retries):
        try:
            api_key = payload.get("gemini_api_key") or settings.GEMINI_API_KEY
            if api_key:
                genai.configure(api_key=api_key)

            if not api_key:
                logger.warning("Gemini API key not set, using mock response")
                return _mock_response(payload)
            
            # Create model
            model = genai.GenerativeModel(model_name)
            
            # Generate response
            response = model.generate_content(
                payload.get("prompt", ""),
                generation_config=genai.types.GenerationConfig(
                    temperature=payload.get("temperature", 0.7),
                    max_output_tokens=payload.get("max_tokens", 1000),
                )
            )
            
            return {
                "response": response.text,
                "model": model_name,
                "tokens_used": response.usage_metadata.total_token_count if hasattr(response, 'usage_metadata') else 100,
                "confidence": 0.85,
                "provider": "gemini"
            }
            
        except Exception as e:
            logger.error(f"Gemini execution error (attempt {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
            else:
                logger.error(f"Gemini failed after {max_retries} attempts")
                return _mock_response(payload)
    
    return _mock_response(payload)


def _mock_response(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Mock response for testing/development"""
    return {
        "response": "Mock Gemini response - API key not configured",
        "model": "mock-gemma",
        "tokens_used": 80,
        "confidence": 0.5,
        "provider": "gemini-mock"
    }

"""
LLM router with cost-based routing and failover
"""
from analytics_llm.backend.llm.providers import gemma, openai
from analytics_llm.backend.core.cost_controller import estimate_cost, select_optimal_model
from analytics_llm.backend.core.config import settings
from typing import Dict, Any
import logging
import random
import time
from opentelemetry import trace

logger = logging.getLogger(__name__)

LLM_PRIORITY = [
    {"name": "gemma", "max_cost": 0.002, "provider": gemma},
    {"name": "openai", "max_cost": 0.02, "provider": openai}
]


class LLMRouter:
    """Routes LLM requests based on cost and availability"""
    
    def __init__(self):
        self.providers = {p["name"]: p["provider"] for p in LLM_PRIORITY}
    
    async def route_request(
        self, 
        payload: Dict[str, Any], 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Route request to optimal LLM provider
        
        Args:
            payload: Request payload
            context: Execution context
            
        Returns:
            LLM response
        """
        task = payload.get("prompt", "")

        gemini_key = context.get("gemini_api_key") if context else None
        if gemini_key:
            payload["gemini_api_key"] = gemini_key
        
        tracer = trace.get_tracer(__name__)
        # Try providers in priority order
        for llm_config in LLM_PRIORITY:
            llm_name = llm_config["name"]
            max_cost = llm_config["max_cost"]
            provider = llm_config["provider"]
            
            # Check cost
            estimated_cost = estimate_cost(task, llm_name)
            if estimated_cost > max_cost:
                logger.info(f"Skipping {llm_name}, cost ${estimated_cost} > ${max_cost}")
                continue
            
            try:
                logger.info(f"Routing to {llm_name} (estimated cost: ${estimated_cost})")
                with tracer.start_as_current_span("llm.route") as span:
                    span.set_attribute("llm.provider", llm_name)
                    span.set_attribute("llm.estimated_cost", estimated_cost)
                    result = self._call_with_retries(provider, payload, llm_name)
                if not result:
                    raise RuntimeError("LLM_EMPTY_RESPONSE")
                result["estimated_cost"] = estimated_cost
                return result

            except Exception as e:
                logger.error(f"{llm_name} failed: {e}")
                continue
        
        return {
            "response": "LLM routing failed. Please retry later.",
            "model": "none",
            "tokens_used": 0,
            "confidence": 0.0,
            "provider": "none",
            "error": "LLM_ROUTING_FAILED"
        }

    def _call_with_retries(
        self,
        provider,
        payload: Dict[str, Any],
        llm_name: str
    ) -> Dict[str, Any]:
        max_retries = max(1, settings.LLM_MAX_RETRIES)
        for attempt in range(max_retries):
            try:
                result = provider.run(payload)
                if not isinstance(result, dict):
                    raise RuntimeError("LLM_PROVIDER_INVALID_RESPONSE")
                return result
            except Exception as exc:
                if attempt >= max_retries - 1:
                    raise
                sleep_for = (2 ** attempt) + random.uniform(0, 0.25)
                logger.warning(
                    f"{llm_name} attempt {attempt + 1}/{max_retries} failed: {exc}. "
                    f"Retrying in {sleep_for:.2f}s"
                )
                time.sleep(sleep_for)

        return {
            "response": "LLM provider failed after retries.",
            "model": "none",
            "tokens_used": 0,
            "confidence": 0.0,
            "provider": "none",
            "error": "LLM_PROVIDER_FAILED"
        }


# Legacy function for backward compatibility
def route_llm(task, payload):
    """Legacy routing function"""
    router = LLMRouter()
    import asyncio
    return asyncio.run(router.route_request(payload, {}))

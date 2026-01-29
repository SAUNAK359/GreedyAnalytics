"""
LLM router with cost-based routing and failover
"""
from llm.providers import gemma, openai
from core.cost_controller import estimate_cost, select_optimal_model
from typing import Dict, Any
import logging

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
                result = provider.run(payload)
                result["estimated_cost"] = estimated_cost
                return result
            
            except Exception as e:
                logger.error(f"{llm_name} failed: {e}")
                continue
        
        raise RuntimeError("All LLM providers failed")


# Legacy function for backward compatibility
def route_llm(task, payload):
    """Legacy routing function"""
    router = LLMRouter()
    import asyncio
    return asyncio.run(router.route_request(payload, {}))

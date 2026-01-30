"""
Cost controller for LLM usage optimization
Implements intelligent routing and temperature control
"""
from typing import Dict, Any
import logging
import time
from threading import Lock

logger = logging.getLogger(__name__)

# Token cost estimates (per 1K tokens)
TOKEN_COSTS = {
    "gpt-4": {"input": 0.03, "output": 0.06},
    "gpt-4-turbo": {"input": 0.01, "output": 0.03},
    "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
    "gemma": {"input": 0.0001, "output": 0.0002},
    "gemini-pro": {"input": 0.00025, "output": 0.0005},
}

# Task complexity to temperature mapping
TASK_TEMPERATURE_MAP = {
    "simple": 0.3,      # Simple queries, data retrieval
    "medium": 0.5,      # Analytics, aggregations
    "complex": 0.7,     # Complex analysis, predictions
    "creative": 0.9,    # Dashboard design, report generation
}


def estimate_cost(task: str, model: str, token_count: int = 1000) -> float:
    """
    Estimate cost for a given task and model
    
    Args:
        task: Task description or type
        model: LLM model name
        token_count: Expected token count
        
    Returns:
        Estimated cost in USD
    """
    try:
        if model not in TOKEN_COSTS:
            logger.warning(f"Unknown model: {model}, using default cost")
            return 0.01
        
        cost_config = TOKEN_COSTS[model]
        
        # Assume 60% input, 40% output
        input_tokens = token_count * 0.6
        output_tokens = token_count * 0.4
        
        total_cost = (
            (input_tokens / 1000) * cost_config["input"] +
            (output_tokens / 1000) * cost_config["output"]
        )
        
        return round(total_cost, 6)
    except Exception as e:
        logger.error(f"Cost estimation error: {e}")
        return 0.01


def choose_temperature(task_type: str) -> float:
    """
    Choose appropriate temperature based on task type
    
    Args:
        task_type: Type of task (simple, medium, complex, creative)
        
    Returns:
        Temperature value (0.0 - 1.0)
    """
    return TASK_TEMPERATURE_MAP.get(task_type.lower(), 0.5)


def select_optimal_model(
    task: str,
    max_budget: float = 0.05,
    required_quality: str = "medium"
) -> str:
    """
    Select optimal LLM model based on budget and quality requirements
    
    Args:
        task: Task description
        max_budget: Maximum budget in USD
        required_quality: Required quality level (low, medium, high)
        
    Returns:
        Selected model name
    """
    # Quality tiers
    quality_tiers = {
        "low": ["gemma", "gpt-3.5-turbo"],
        "medium": ["gemini-pro", "gpt-3.5-turbo", "gpt-4-turbo"],
        "high": ["gpt-4", "gpt-4-turbo"],
    }
    
    candidates = quality_tiers.get(required_quality, quality_tiers["medium"])
    
    # Find cheapest model within budget
    for model in candidates:
        cost = estimate_cost(task, model)
        if cost <= max_budget:
            logger.info(f"Selected model {model} with estimated cost ${cost}")
            return model
    
    # Fallback to cheapest option
    logger.warning(f"No model found within budget ${max_budget}, using fallback")
    return "gemma"


def track_usage(
    user_id: str,
    tenant_id: str,
    model: str,
    tokens_used: int,
    cost: float
) -> Dict[str, Any]:
    """
    Track LLM usage for billing and monitoring
    
    Args:
        user_id: User identifier
        tenant_id: Tenant identifier
        model: Model used
        tokens_used: Number of tokens consumed
        cost: Cost incurred
        
    Returns:
        Usage record
    """
    usage_record = {
        "user_id": user_id,
        "tenant_id": tenant_id,
        "model": model,
        "tokens_used": tokens_used,
        "cost": cost,
        "timestamp": None  # Would use datetime.utcnow()
    }
    
    # In production, store in database
    logger.info(f"Usage tracked: {usage_record}")
    
    return usage_record


class CostOptimizer:
    """Cost optimization strategies for LLM usage"""
    
    def __init__(self):
        self.daily_budgets = {}
        self.usage_cache = {}
    
    def check_budget(self, tenant_id: str, requested_cost: float) -> bool:
        """Check if tenant has budget for request"""
        daily_budget = self.daily_budgets.get(tenant_id, 100.0)  # $100 default
        current_usage = self.usage_cache.get(tenant_id, 0.0)
        
        return (current_usage + requested_cost) <= daily_budget
    
    def update_usage(self, tenant_id: str, cost: float):
        """Update tenant usage"""
        current = self.usage_cache.get(tenant_id, 0.0)
        self.usage_cache[tenant_id] = current + cost
    
    def get_usage_summary(self, tenant_id: str) -> Dict[str, Any]:
        """Get usage summary for tenant"""
        daily_budget = self.daily_budgets.get(tenant_id, 100.0)
        current_usage = self.usage_cache.get(tenant_id, 0.0)
        
        return {
            "tenant_id": tenant_id,
            "daily_budget": daily_budget,
            "current_usage": current_usage,
            "remaining_budget": daily_budget - current_usage,
            "usage_percentage": (current_usage / daily_budget) * 100
        }


# Global cost optimizer instance
cost_optimizer = CostOptimizer()


def estimate_tokens(text: str) -> int:
    """Rough token estimate for budgeting."""
    if not text:
        return 0
    return max(1, len(text) // 4)


class TokenBudgetLimiter:
    """Simple in-memory token budget limiter per tenant."""

    def __init__(self, window_seconds: int = 60):
        self.window_seconds = window_seconds
        self._usage: Dict[str, Dict[str, Any]] = {}
        self._lock = Lock()

    def allow(self, tenant_id: str, tokens: int, limit: int) -> bool:
        now = time.time()
        with self._lock:
            entry = self._usage.get(tenant_id)
            if not entry or now - entry["window_start"] >= self.window_seconds:
                self._usage[tenant_id] = {
                    "window_start": now,
                    "tokens_used": 0
                }
                entry = self._usage[tenant_id]

            if entry["tokens_used"] + tokens > limit:
                return False

            entry["tokens_used"] += tokens
            return True

    def remaining(self, tenant_id: str, limit: int) -> int:
        now = time.time()
        with self._lock:
            entry = self._usage.get(tenant_id)
            if not entry or now - entry["window_start"] >= self.window_seconds:
                return limit
            return max(0, limit - entry["tokens_used"])


token_budget_limiter = TokenBudgetLimiter()

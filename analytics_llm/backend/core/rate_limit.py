"""
Enterprise rate limiting with Redis backend
"""
import redis
from typing import Optional, Any, cast
import logging
from analytics_llm.backend.core.config import settings

logger = logging.getLogger(__name__)

try:
    r = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)
    r.ping()
    logger.info("✅ Redis connected for rate limiting")
except Exception as e:
    logger.warning(f"⚠️ Redis connection failed: {e}, using in-memory fallback")
    r = None


class RateLimiter:
    """Token bucket rate limiter with Redis backend"""
    
    def __init__(self):
        self.memory_cache = {}  # Fallback for when Redis is unavailable
        self.redis_client = r
    
    def allow_request(
        self, 
        key: str, 
        limit: Optional[int] = None,
        window_seconds: int = 60
    ) -> bool:
        """
        Check if request is allowed under rate limit
        
        Args:
            key: Unique identifier (user_id, ip, etc.)
            limit: Maximum requests per window
            window_seconds: Time window in seconds
            
        Returns:
            True if request is allowed, False otherwise
        """
        if limit is None:
            limit = settings.MAX_REQUESTS_PER_MINUTE
        
        try:
            if self.redis_client is not None:
                return self._redis_check(key, limit, window_seconds)
            else:
                return self._memory_check(key, limit)
        except Exception as e:
            logger.error(f"Rate limit check error: {e}")
            return True  # Fail open in production
    
    def _redis_check(self, key: str, limit: int, window: int) -> bool:
        """Redis-based rate limiting"""
        try:
            client = cast(Any, self.redis_client)
            if client is None:
                return True
            count = int(client.incr(key))
            if count == 1:
                client.expire(key, window)
            
            return count <= limit
        except Exception as e:
            logger.error(f"Redis rate limit error: {e}")
            return True
    
    def _memory_check(self, key: str, limit: int) -> bool:
        """Memory-based fallback rate limiting"""
        count = self.memory_cache.get(key, 0)
        self.memory_cache[key] = count + 1
        return count < limit
    
    def reset(self, key: str):
        """Reset rate limit for key"""
        try:
            if self.redis_client:
                self.redis_client.delete(key)
            else:
                self.memory_cache.pop(key, None)
        except Exception as e:
            logger.error(f"Rate limit reset error: {e}")
    
    def get_remaining(self, key: str, limit: Optional[int] = None) -> int:
        """Get remaining requests for key"""
        if limit is None:
            limit = settings.MAX_REQUESTS_PER_MINUTE
        
        try:
            if self.redis_client is not None:
                client = cast(Any, self.redis_client)
                raw = client.get(key) if client is not None else 0
                count = int(raw or 0)
            else:
                count = self.memory_cache.get(key, 0)
            
            return max(0, limit - count)
        except Exception as e:
            logger.error(f"Get remaining error: {e}")
            return limit


# Fallback function for backward compatibility
def allow_request(key: str, limit: int = 100) -> bool:
    """Legacy function for backward compatibility"""
    limiter = RateLimiter()
    return limiter.allow_request(key, limit)

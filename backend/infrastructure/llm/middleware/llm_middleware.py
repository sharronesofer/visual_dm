"""
LLM Infrastructure Middleware

Provides middleware for LLM operations including:
- Request/response monitoring
- Performance tracking
- Caching layer
- Rate limiting
- Error handling
"""

import time
import logging
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
import asyncio
from functools import wraps

from backend.infrastructure.llm.config.llm_config import llm_config
from backend.infrastructure.llm.utils.llm_utils import LLMUtils

logger = logging.getLogger(__name__)

class LLMMiddleware:
    """
    Middleware for LLM operations providing cross-cutting concerns.
    """
    
    def __init__(self):
        self.performance_config = llm_config.get_performance_config()
        self.request_cache: Dict[str, Any] = {}
        self.performance_metrics: List[Dict[str, Any]] = []
        self.rate_limiter = RateLimiter(
            max_requests=self.performance_config.get("max_concurrent_requests", 10)
        )
    
    async def process_request(self, 
                            request_func: Callable,
                            prompt: str,
                            model: str,
                            **kwargs) -> Dict[str, Any]:
        """
        Process LLM request with middleware layers.
        
        Args:
            request_func: Function to execute LLM request
            prompt: Input prompt
            model: Model name
            **kwargs: Additional parameters
            
        Returns:
            Response with middleware metadata
        """
        start_time = time.time()
        cache_key = None
        
        try:
            # Generate cache key if caching enabled
            if self.performance_config.get("enable_caching", True):
                cache_key = LLMUtils.generate_cache_key(prompt, model, **kwargs)
                
                # Check cache first
                cached_response = self._get_cached_response(cache_key)
                if cached_response:
                    return self._add_metadata(cached_response, start_time, cache_hit=True)
            
            # Apply rate limiting
            await self.rate_limiter.acquire()
            
            try:
                # Execute request
                response = await request_func(prompt, model, **kwargs)
                
                # Cache response if enabled
                if cache_key and self.performance_config.get("enable_caching", True):
                    self._cache_response(cache_key, response)
                
                # Add metadata and return
                return self._add_metadata(response, start_time, cache_hit=False)
                
            finally:
                self.rate_limiter.release()
                
        except Exception as e:
            logger.error(f"LLM middleware error: {e}")
            error_response = {
                "error": str(e),
                "success": False
            }
            return self._add_metadata(error_response, start_time, error=str(e))
    
    def _get_cached_response(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get response from cache if available and not expired"""
        if cache_key not in self.request_cache:
            return None
        
        cached_item = self.request_cache[cache_key]
        cache_ttl = self.performance_config.get("cache_ttl", 3600)
        
        if time.time() - cached_item["timestamp"] > cache_ttl:
            # Cache expired
            del self.request_cache[cache_key]
            return None
        
        return cached_item["response"]
    
    def _cache_response(self, cache_key: str, response: Dict[str, Any]):
        """Cache response with timestamp"""
        self.request_cache[cache_key] = {
            "response": response,
            "timestamp": time.time()
        }
        
        # Limit cache size
        max_cache_size = 1000
        if len(self.request_cache) > max_cache_size:
            # Remove oldest entries
            oldest_keys = sorted(
                self.request_cache.keys(),
                key=lambda k: self.request_cache[k]["timestamp"]
            )[:100]
            for key in oldest_keys:
                del self.request_cache[key]
    
    def _add_metadata(self, 
                     response: Dict[str, Any], 
                     start_time: float,
                     cache_hit: bool = False,
                     error: Optional[str] = None) -> Dict[str, Any]:
        """Add middleware metadata to response"""
        end_time = time.time()
        response_time = end_time - start_time
        
        # Calculate tokens and cost if available
        tokens = 0
        cost = 0.0
        if "response" in response and isinstance(response["response"], str):
            tokens = LLMUtils.estimate_tokens(response["response"])
            cost = LLMUtils.calculate_cost(tokens, response.get("model", "unknown"))
        
        metadata = {
            "middleware": {
                "response_time": response_time,
                "cache_hit": cache_hit,
                "timestamp": datetime.utcnow().isoformat(),
                "tokens": tokens,
                "cost": cost,
                "error": error
            }
        }
        
        # Record performance metrics if monitoring enabled
        if self.performance_config.get("enable_monitoring", True):
            metrics = {
                "response_time": response_time,
                "tokens": tokens,
                "cost": cost,
                "model": response.get("model", "unknown"),
                "provider": response.get("provider", "unknown"),
                "success": error is None,
                "error": error,
                "cache_hit": cache_hit
            }
            self.performance_metrics.append(
                LLMUtils.format_performance_metrics(metrics)
            )
            
            # Limit metrics history
            if len(self.performance_metrics) > 10000:
                self.performance_metrics = self.performance_metrics[-5000:]
        
        # Merge metadata with response
        enhanced_response = {**response, **metadata}
        return enhanced_response
    
    def get_performance_metrics(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent performance metrics"""
        return self.performance_metrics[-limit:]
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            "cache_size": len(self.request_cache),
            "cache_enabled": self.performance_config.get("enable_caching", True),
            "cache_ttl": self.performance_config.get("cache_ttl", 3600)
        }
    
    def clear_cache(self):
        """Clear the request cache"""
        self.request_cache.clear()
        logger.info("LLM middleware cache cleared")

class RateLimiter:
    """Simple rate limiter for LLM requests"""
    
    def __init__(self, max_requests: int):
        self.max_requests = max_requests
        self.current_requests = 0
        self.semaphore = asyncio.Semaphore(max_requests)
    
    async def acquire(self):
        """Acquire rate limit slot"""
        await self.semaphore.acquire()
        self.current_requests += 1
    
    def release(self):
        """Release rate limit slot"""
        if self.current_requests > 0:
            self.current_requests -= 1
            self.semaphore.release()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get rate limiter statistics"""
        return {
            "max_requests": self.max_requests,
            "current_requests": self.current_requests,
            "available_slots": self.max_requests - self.current_requests
        }

# Global middleware instance
llm_middleware = LLMMiddleware()

def llm_monitor(func):
    """Decorator for monitoring LLM function calls"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            response_time = time.time() - start_time
            
            logger.info(f"LLM function {func.__name__} completed in {response_time:.2f}s")
            return result
            
        except Exception as e:
            response_time = time.time() - start_time
            logger.error(f"LLM function {func.__name__} failed after {response_time:.2f}s: {e}")
            raise
    
    return wrapper 
"""
Cache Decorators and Middleware for Population System APIs

Provides decorators and middleware for:
- Automatic API response caching
- Cache invalidation on data changes
- Cache-enabled business logic functions
- Performance monitoring and metrics

This module integrates with the Redis cache system to improve API performance.
"""

import functools
import logging
import time
from typing import Any, Callable, Dict, List, Optional, Union
from datetime import datetime
import json
import hashlib
from fastapi import Request, Response
from fastapi.responses import JSONResponse

from backend.infrastructure.cache.redis_cache import cache

logger = logging.getLogger(__name__)


def cache_response(
    ttl: int = 300,
    key_prefix: str = "api",
    exclude_params: Optional[List[str]] = None,
    cache_condition: Optional[Callable] = None
):
    """
    Decorator for caching API endpoint responses
    
    Args:
        ttl: Time to live in seconds
        key_prefix: Prefix for cache keys
        exclude_params: Parameters to exclude from cache key generation
        cache_condition: Function to determine if response should be cached
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Skip caching if cache is not available
            if not cache.available:
                return await func(*args, **kwargs)
            
            # Generate cache key from function parameters
            cache_key_data = {
                "function": func.__name__,
                "args": args,
                "kwargs": {k: v for k, v in kwargs.items() 
                          if not exclude_params or k not in exclude_params}
            }
            
            # Remove FastAPI objects that can't be serialized
            filtered_kwargs = {}
            for k, v in cache_key_data["kwargs"].items():
                if not isinstance(v, (Request, Response)) and not hasattr(v, "__dict__"):
                    filtered_kwargs[k] = v
            cache_key_data["kwargs"] = filtered_kwargs
            
            params_hash = cache.generate_params_hash(cache_key_data)
            endpoint_name = f"{func.__module__.split('.')[-1]}_{func.__name__}"
            
            # Try to get cached response
            cached_response = cache.get_api_response(endpoint_name, params_hash)
            if cached_response is not None:
                logger.debug(f"Cache hit for {endpoint_name} ({params_hash})")
                return cached_response
            
            # Execute function and cache result
            start_time = time.time()
            result = await func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            # Check cache condition if provided
            should_cache = True
            if cache_condition:
                should_cache = cache_condition(result)
            
            # Cache the result
            if should_cache:
                cache.cache_api_response(endpoint_name, params_hash, result, ttl)
                logger.debug(f"Cached response for {endpoint_name} (exec: {execution_time:.3f}s)")
            
            return result
        
        return wrapper
    return decorator


def cache_business_logic(
    cache_prefix: str,
    ttl: int = 300,
    key_generator: Optional[Callable] = None,
    invalidation_triggers: Optional[List[str]] = None
):
    """
    Decorator for caching business logic function results
    
    Args:
        cache_prefix: Prefix for cache keys
        ttl: Time to live in seconds
        key_generator: Custom function to generate cache keys
        invalidation_triggers: List of events that should invalidate this cache
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if not cache.available:
                return func(*args, **kwargs)
            
            # Generate cache key
            if key_generator:
                cache_key = key_generator(*args, **kwargs)
            else:
                # Default key generation
                key_data = {"args": args, "kwargs": kwargs}
                key_hash = cache.generate_params_hash(key_data)
                cache_key = f"{func.__name__}_{key_hash}"
            
            # Try to get cached result
            cached_result = cache.get(cache_prefix, cache_key)
            if cached_result is not None:
                logger.debug(f"Business logic cache hit: {cache_prefix}:{cache_key}")
                return cached_result
            
            # Execute function and cache result
            start_time = time.time()
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            cache.set(cache_prefix, cache_key, result, ttl)
            logger.debug(f"Cached business logic result: {cache_prefix}:{cache_key} (exec: {execution_time:.3f}s)")
            
            return result
        
        return wrapper
    return decorator


def invalidate_cache_on_change(
    cache_patterns: List[str],
    condition: Optional[Callable] = None
):
    """
    Decorator to invalidate cache when function modifies data
    
    Args:
        cache_patterns: List of cache key patterns to invalidate
        condition: Optional condition to determine if invalidation should occur
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            result = await func(*args, **kwargs)
            
            # Check if we should invalidate cache
            should_invalidate = True
            if condition:
                should_invalidate = condition(result, *args, **kwargs)
            
            if should_invalidate and cache.available:
                total_invalidated = 0
                for pattern in cache_patterns:
                    invalidated = cache.invalidate_pattern(pattern)
                    total_invalidated += invalidated
                
                if total_invalidated > 0:
                    logger.info(f"Invalidated {total_invalidated} cache entries after {func.__name__}")
            
            return result
        
        return wrapper
    return decorator


class CacheMiddleware:
    """Middleware for automatic cache management"""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        request = Request(scope, receive)
        
        # Add cache headers to response
        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                headers = list(message.get("headers", []))
                
                # Add cache status header
                cache_status = "HIT" if hasattr(request.state, "cache_hit") else "MISS"
                headers.append((b"x-cache-status", cache_status.encode()))
                
                # Add cache stats if available
                if cache.available:
                    stats = cache.get_cache_stats()
                    if stats.get("available"):
                        headers.append((b"x-cache-hit-rate", str(stats.get("hit_rate", 0.0)).encode()))
                        headers.append((b"x-cache-keys", str(stats.get("total_keys", 0)).encode()))
                
                message["headers"] = headers
            
            await send(message)
        
        await self.app(scope, receive, send_wrapper)


# Population-specific cache decorators
def cache_population_data(ttl: int = 300):
    """Cache population calculation results"""
    return cache_business_logic(
        cache_prefix="population",
        ttl=ttl,
        key_generator=lambda population_id, *args, **kwargs: population_id
    )


def cache_disease_data(ttl: int = 60):
    """Cache disease state data"""
    return cache_business_logic(
        cache_prefix="disease",
        ttl=ttl,
        key_generator=lambda population_id, *args, **kwargs: population_id
    )


def cache_economic_data(ttl: int = 180):
    """Cache economic state data"""
    return cache_business_logic(
        cache_prefix="economic",
        ttl=ttl,
        key_generator=lambda settlement_id, *args, **kwargs: settlement_id
    )


def cache_quest_data(ttl: int = 120):
    """Cache quest opportunities"""
    return cache_business_logic(
        cache_prefix="quest",
        ttl=ttl,
        key_generator=lambda population_id, *args, **kwargs: population_id
    )


# Cache invalidation decorators for data modifications
def invalidate_population_cache(population_id_param: str = "population_id"):
    """Invalidate population cache when data changes"""
    def get_population_id(*args, **kwargs):
        return kwargs.get(population_id_param) or (args[0] if args else None)
    
    def cache_patterns(*args, **kwargs):
        pop_id = get_population_id(*args, **kwargs)
        if pop_id:
            return [f"pop:{pop_id}*", f"api:*"]
        return ["api:*"]
    
    return invalidate_cache_on_change(
        cache_patterns=lambda *args, **kwargs: cache_patterns(*args, **kwargs)
    )


def invalidate_disease_cache(population_id_param: str = "population_id"):
    """Invalidate disease cache when data changes"""
    def get_population_id(*args, **kwargs):
        return kwargs.get(population_id_param) or (args[0] if args else None)
    
    def cache_patterns(*args, **kwargs):
        pop_id = get_population_id(*args, **kwargs)
        if pop_id:
            return [f"dis:{pop_id}*", f"quest:{pop_id}*", f"api:*"]
        return ["api:*"]
    
    return invalidate_cache_on_change(
        cache_patterns=lambda *args, **kwargs: cache_patterns(*args, **kwargs)
    )


def invalidate_economic_cache(settlement_id_param: str = "settlement_id"):
    """Invalidate economic cache when data changes"""
    def get_settlement_id(*args, **kwargs):
        return kwargs.get(settlement_id_param) or (args[0] if args else None)
    
    def cache_patterns(*args, **kwargs):
        settlement_id = get_settlement_id(*args, **kwargs)
        if settlement_id:
            return [f"eco:{settlement_id}*", f"trade:*", f"api:*"]
        return ["api:*"]
    
    return invalidate_cache_on_change(
        cache_patterns=lambda *args, **kwargs: cache_patterns(*args, **kwargs)
    )


# Performance monitoring decorator
def monitor_performance(
    log_slow_threshold: float = 1.0,
    cache_slow_operations: bool = True
):
    """
    Monitor and log performance of functions
    
    Args:
        log_slow_threshold: Log operations slower than this many seconds
        cache_slow_operations: Cache results of slow operations for longer
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            result = await func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            # Log slow operations
            if execution_time > log_slow_threshold:
                logger.warning(f"Slow operation: {func.__name__} took {execution_time:.3f}s")
            
            # Cache slow operations for longer if enabled
            if cache_slow_operations and execution_time > log_slow_threshold and cache.available:
                # This would need integration with specific cache calls
                pass
            
            return result
        
        return wrapper
    return decorator


# Utility functions for cache management
def warm_cache_for_population(population_id: str):
    """Pre-warm cache for a population with common data"""
    if not cache.available:
        return False
    
    try:
        # This would typically call the actual functions to populate cache
        # For now, just log the intent
        logger.info(f"Cache warming initiated for population {population_id}")
        return True
    except Exception as e:
        logger.error(f"Error warming cache for population {population_id}: {str(e)}")
        return False


def get_cache_performance_stats() -> Dict[str, Any]:
    """Get detailed cache performance statistics"""
    if not cache.available:
        return {"available": False}
    
    try:
        stats = cache.get_cache_stats()
        
        # Add performance metrics
        performance_stats = {
            "cache_efficiency": {
                "hit_rate": stats.get("hit_rate", 0.0),
                "total_keys": stats.get("total_keys", 0),
                "memory_usage": stats.get("used_memory", "unknown")
            },
            "key_distribution": stats.get("keys_by_category", {}),
            "system_health": {
                "redis_version": stats.get("redis_version", "unknown"),
                "uptime_hours": round(stats.get("uptime_in_seconds", 0) / 3600, 2),
                "connected_clients": stats.get("connected_clients", 0)
            }
        }
        
        return performance_stats
        
    except Exception as e:
        logger.error(f"Error getting cache performance stats: {str(e)}")
        return {"available": False, "error": str(e)}


# Context manager for cache operations
class CacheTransaction:
    """Context manager for batch cache operations"""
    
    def __init__(self):
        self.operations = []
        self.invalidations = []
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            # Commit operations
            self._execute_operations()
        else:
            # Rollback on exception
            self._rollback_operations()
    
    def cache_set(self, prefix: str, identifier: str, data: Any, ttl: Optional[int] = None):
        """Queue a cache set operation"""
        self.operations.append(("set", prefix, identifier, data, ttl))
    
    def cache_invalidate(self, pattern: str):
        """Queue a cache invalidation"""
        self.invalidations.append(pattern)
    
    def _execute_operations(self):
        """Execute all queued operations"""
        if not cache.available:
            return
        
        # Execute cache sets
        for operation in self.operations:
            if operation[0] == "set":
                _, prefix, identifier, data, ttl = operation
                cache.set(prefix, identifier, data, ttl)
        
        # Execute invalidations
        for pattern in self.invalidations:
            cache.invalidate_pattern(pattern)
    
    def _rollback_operations(self):
        """Rollback operations on error"""
        # For now, just clear the operations
        self.operations.clear()
        self.invalidations.clear()


# Export functions
__all__ = [
    "cache_response",
    "cache_business_logic",
    "invalidate_cache_on_change",
    "CacheMiddleware",
    "cache_population_data",
    "cache_disease_data",
    "cache_economic_data",
    "cache_quest_data",
    "invalidate_population_cache",
    "invalidate_disease_cache",
    "invalidate_economic_cache",
    "monitor_performance",
    "warm_cache_for_population",
    "get_cache_performance_stats",
    "CacheTransaction"
] 
"""
LLM Infrastructure Service

Provides shared infrastructure services for LLM operations including:
- Health monitoring
- Performance analytics
- Configuration management
- System diagnostics
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

from backend.infrastructure.llm.config.llm_config import llm_config, LLMProvider
from backend.infrastructure.llm.middleware.llm_middleware import llm_middleware
from backend.infrastructure.llm.utils.llm_utils import LLMUtils

logger = logging.getLogger(__name__)

class LLMInfrastructureService:
    """
    Infrastructure service for LLM system management and monitoring.
    """
    
    def __init__(self):
        self.start_time = datetime.utcnow()
        self.health_checks = {}
        self.system_stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "cache_hits": 0,
            "total_tokens": 0,
            "total_cost": 0.0
        }
    
    async def get_system_health(self) -> Dict[str, Any]:
        """
        Get comprehensive system health status.
        
        Returns:
            System health information
        """
        # Check configuration
        config_status = llm_config.validate_configuration()
        
        # Check provider availability
        provider_health = await self._check_provider_health()
        
        # Get performance metrics
        performance_metrics = self._get_performance_summary()
        
        # Get cache statistics
        cache_stats = llm_middleware.get_cache_stats()
        
        # Calculate uptime
        uptime = datetime.utcnow() - self.start_time
        
        health_status = {
            "status": "healthy" if config_status["valid"] and any(
                status["available"] for status in provider_health.values()
            ) else "degraded",
            "timestamp": datetime.utcnow().isoformat(),
            "uptime_seconds": uptime.total_seconds(),
            "configuration": config_status,
            "providers": provider_health,
            "performance": performance_metrics,
            "cache": cache_stats,
            "system_stats": self.system_stats
        }
        
        return health_status
    
    async def _check_provider_health(self) -> Dict[str, Any]:
        """Check health of all configured providers"""
        provider_health = {}
        
        for provider in LLMProvider:
            config = llm_config.get_provider_config(provider)
            if not config or not config.enabled:
                provider_health[provider.value] = {
                    "available": False,
                    "enabled": False,
                    "reason": "Provider not enabled"
                }
                continue
            
            try:
                # Perform basic health check
                if provider == LLMProvider.OLLAMA:
                    available = await self._check_ollama_health(config)
                else:
                    # For cloud providers, assume available if API key is present
                    available = bool(config.api_key)
                
                provider_health[provider.value] = {
                    "available": available,
                    "enabled": True,
                    "last_check": datetime.utcnow().isoformat(),
                    "config": {
                        "base_url": config.base_url,
                        "timeout": config.timeout,
                        "max_retries": config.max_retries
                    }
                }
                
            except Exception as e:
                provider_health[provider.value] = {
                    "available": False,
                    "enabled": True,
                    "error": str(e),
                    "last_check": datetime.utcnow().isoformat()
                }
        
        return provider_health
    
    async def _check_ollama_health(self, config) -> bool:
        """Check if Ollama service is available"""
        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{config.base_url}/api/tags",
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    return response.status == 200
        except:
            return False
    
    def _get_performance_summary(self) -> Dict[str, Any]:
        """Get performance metrics summary"""
        metrics = llm_middleware.get_performance_metrics(limit=1000)
        
        if not metrics:
            return {
                "total_requests": 0,
                "avg_response_time": 0,
                "success_rate": 0,
                "cache_hit_rate": 0
            }
        
        # Calculate aggregated metrics
        total_requests = len(metrics)
        successful_requests = sum(1 for m in metrics if m.get("success", False))
        cache_hits = sum(1 for m in metrics if m.get("cache_hit", False))
        
        avg_response_time = sum(m.get("response_time_ms", 0) for m in metrics) / total_requests
        success_rate = successful_requests / total_requests if total_requests > 0 else 0
        cache_hit_rate = cache_hits / total_requests if total_requests > 0 else 0
        
        # Get recent metrics (last hour)
        recent_cutoff = datetime.utcnow() - timedelta(hours=1)
        recent_metrics = [
            m for m in metrics 
            if datetime.fromisoformat(m.get("timestamp", "1970-01-01")) > recent_cutoff
        ]
        
        return {
            "total_requests": total_requests,
            "successful_requests": successful_requests,
            "avg_response_time_ms": round(avg_response_time, 2),
            "success_rate": round(success_rate, 3),
            "cache_hit_rate": round(cache_hit_rate, 3),
            "recent_requests_1h": len(recent_metrics),
            "total_tokens": sum(m.get("token_count", 0) for m in metrics),
            "total_cost_usd": round(sum(m.get("cost_usd", 0) for m in metrics), 6)
        }
    
    def record_request(self, success: bool, tokens: int = 0, cost: float = 0.0, cache_hit: bool = False):
        """Record request statistics"""
        self.system_stats["total_requests"] += 1
        
        if success:
            self.system_stats["successful_requests"] += 1
        else:
            self.system_stats["failed_requests"] += 1
        
        if cache_hit:
            self.system_stats["cache_hits"] += 1
        
        self.system_stats["total_tokens"] += tokens
        self.system_stats["total_cost"] += cost
    
    async def get_configuration_info(self) -> Dict[str, Any]:
        """Get current configuration information"""
        config_info = {
            "providers": {},
            "performance": llm_config.get_performance_config(),
            "validation": llm_config.validate_configuration()
        }
        
        for provider in LLMProvider:
            provider_config = llm_config.get_provider_config(provider)
            if provider_config:
                config_info["providers"][provider.value] = {
                    "enabled": provider_config.enabled,
                    "base_url": provider_config.base_url,
                    "timeout": provider_config.timeout,
                    "max_retries": provider_config.max_retries,
                    "has_api_key": bool(provider_config.api_key)
                }
        
        return config_info
    
    async def get_diagnostics(self) -> Dict[str, Any]:
        """Get comprehensive system diagnostics"""
        diagnostics = {
            "timestamp": datetime.utcnow().isoformat(),
            "health": await self.get_system_health(),
            "configuration": await self.get_configuration_info(),
            "middleware_stats": {
                "cache": llm_middleware.get_cache_stats(),
                "rate_limiter": llm_middleware.rate_limiter.get_stats()
            },
            "recent_errors": self._get_recent_errors()
        }
        
        return diagnostics
    
    def _get_recent_errors(self) -> List[Dict[str, Any]]:
        """Get recent error information"""
        metrics = llm_middleware.get_performance_metrics(limit=100)
        errors = [
            {
                "timestamp": m.get("timestamp"),
                "error": m.get("error"),
                "model": m.get("model"),
                "provider": m.get("provider")
            }
            for m in metrics
            if m.get("error")
        ]
        return errors[-10:]  # Last 10 errors
    
    async def clear_caches(self):
        """Clear all system caches"""
        llm_middleware.clear_cache()
        logger.info("All LLM infrastructure caches cleared")
    
    async def reload_configuration(self):
        """Reload configuration from environment"""
        llm_config.load_configuration()
        logger.info("LLM configuration reloaded")

# Global infrastructure service instance
llm_infrastructure_service = LLMInfrastructureService() 
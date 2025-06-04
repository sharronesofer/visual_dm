"""
Region System Performance Monitoring Router

Provides performance monitoring, metrics, and optimization management
for the region system including caching, query performance, and system health.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse

from backend.infrastructure.systems.region.dependencies import (
    RegionService, ContinentService
)
from backend.infrastructure.systems.region.repositories import get_region_repository

logger = logging.getLogger(__name__)

# Create router instance
router = APIRouter(prefix="/performance", tags=["region-performance"])

@router.get("/metrics", response_model=Dict[str, Any])
async def get_performance_metrics(
    region_service: RegionService,
    include_cache_details: bool = Query(False, description="Include detailed cache information")
):
    """
    Get comprehensive performance metrics for the region system.
    
    Returns:
    - Repository performance metrics (queries, cache hit rate)
    - Service-level performance data
    - Memory usage statistics
    - Operation timing information
    """
    try:
        # Get repository metrics
        repo = get_region_repository()
        repo_metrics = repo.get_performance_metrics()
        
        # Calculate service-level metrics
        service_metrics = {
            "active_regions_cached": repo_metrics.get("cache_size", 0),
            "cache_efficiency": repo_metrics.get("cache_hit_rate", 0),
            "total_database_queries": repo_metrics.get("query_count", 0)
        }
        
        # System health indicators
        health_metrics = {
            "cache_health": "good" if repo_metrics.get("cache_hit_rate", 0) > 70 else "needs_attention",
            "query_load": "normal" if repo_metrics.get("query_count", 0) < 1000 else "high",
            "memory_usage": "optimal" if repo_metrics.get("cache_size", 0) < 500 else "elevated"
        }
        
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "repository_metrics": repo_metrics,
            "service_metrics": service_metrics,
            "health_indicators": health_metrics,
            "optimization_status": {
                "caching_enabled": True,
                "query_optimization": True,
                "bulk_operations": True,
                "eager_loading": True
            }
        }
        
        # Include detailed cache information if requested
        if include_cache_details and "cache_entries" in repo_metrics:
            metrics["cache_details"] = {
                "sample_cache_keys": repo_metrics["cache_entries"],
                "cache_size_bytes": len(str(repo_metrics.get("cache_entries", []))) * 8,  # Rough estimate
                "cache_types": {
                    "region_lookups": len([k for k in repo_metrics.get("cache_entries", []) if "region_by_" in k]),
                    "filtered_queries": len([k for k in repo_metrics.get("cache_entries", []) if "filtered_" in k]),
                    "statistics": len([k for k in repo_metrics.get("cache_entries", []) if "stats_" in k])
                }
            }
        
        return metrics
        
    except Exception as e:
        logger.error(f"Error getting performance metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get performance metrics: {str(e)}")

@router.post("/cache/clear")
async def clear_performance_cache():
    """
    Clear the region system performance cache.
    
    Use this endpoint to force refresh of cached data when needed.
    """
    try:
        repo = get_region_repository()
        repo.clear_cache()
        
        return {
            "status": "success",
            "message": "Region system cache cleared successfully",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error clearing cache: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to clear cache: {str(e)}")

@router.get("/cache/status", response_model=Dict[str, Any])
async def get_cache_status():
    """
    Get detailed cache status and health information.
    """
    try:
        repo = get_region_repository()
        metrics = repo.get_performance_metrics()
        
        # Analyze cache health
        cache_hit_rate = metrics.get("cache_hit_rate", 0)
        cache_size = metrics.get("cache_size", 0)
        
        # Determine cache health status
        if cache_hit_rate >= 80:
            health_status = "excellent"
        elif cache_hit_rate >= 60:
            health_status = "good"
        elif cache_hit_rate >= 40:
            health_status = "fair"
        else:
            health_status = "poor"
        
        # Cache size assessment
        if cache_size < 100:
            size_status = "optimal"
        elif cache_size < 500:
            size_status = "moderate"
        else:
            size_status = "high"
        
        cache_status = {
            "timestamp": datetime.now().isoformat(),
            "cache_enabled": True,
            "cache_hit_rate": cache_hit_rate,
            "cache_size": cache_size,
            "health_status": health_status,
            "size_status": size_status,
            "recommendations": []
        }
        
        # Generate recommendations
        if cache_hit_rate < 60:
            cache_status["recommendations"].append({
                "type": "cache_optimization",
                "priority": "high",
                "message": "Consider increasing cache TTL or reviewing cache key strategy"
            })
        
        if cache_size > 800:
            cache_status["recommendations"].append({
                "type": "memory_management",
                "priority": "medium", 
                "message": "High cache size detected - consider cache cleanup or size limits"
            })
        
        if metrics.get("query_count", 0) > 1000:
            cache_status["recommendations"].append({
                "type": "query_optimization",
                "priority": "high",
                "message": "High query count - review query patterns and caching strategy"
            })
        
        return cache_status
        
    except Exception as e:
        logger.error(f"Error getting cache status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get cache status: {str(e)}")

@router.get("/optimization/suggestions", response_model=Dict[str, Any])
async def get_optimization_suggestions():
    """
    Get AI-powered optimization suggestions for the region system.
    """
    try:
        repo = get_region_repository()
        metrics = repo.get_performance_metrics()
        
        suggestions = []
        
        # Analyze metrics and generate suggestions
        cache_hit_rate = metrics.get("cache_hit_rate", 0)
        query_count = metrics.get("query_count", 0)
        cache_size = metrics.get("cache_size", 0)
        
        # Cache optimization suggestions
        if cache_hit_rate < 70:
            suggestions.append({
                "category": "caching",
                "priority": "high",
                "title": "Improve Cache Hit Rate",
                "description": f"Current cache hit rate is {cache_hit_rate}%. Consider reviewing cache key strategy and TTL settings.",
                "implementation": [
                    "Analyze most frequently accessed regions",
                    "Increase cache TTL for stable data",
                    "Implement cache warming for popular regions"
                ],
                "expected_improvement": "15-25% performance boost"
            })
        
        # Query optimization suggestions
        if query_count > 500:
            suggestions.append({
                "category": "database",
                "priority": "medium",
                "title": "Database Query Optimization",
                "description": f"High query count detected ({query_count}). Review query patterns and implement additional indexing.",
                "implementation": [
                    "Add database indexes for commonly filtered fields",
                    "Implement query result pagination",
                    "Use bulk operations for multiple region lookups"
                ],
                "expected_improvement": "20-30% query performance improvement"
            })
        
        # Memory optimization suggestions
        if cache_size > 600:
            suggestions.append({
                "category": "memory",
                "priority": "medium",
                "title": "Memory Usage Optimization",
                "description": f"Cache size is {cache_size} entries. Consider implementing cache size limits and cleanup.",
                "implementation": [
                    "Implement LRU cache eviction policy",
                    "Set maximum cache size limits",
                    "Regular cache cleanup for expired entries"
                ],
                "expected_improvement": "Reduced memory footprint by 30-40%"
            })
        
        # Performance monitoring suggestions
        suggestions.append({
            "category": "monitoring",
            "priority": "low",
            "title": "Enhanced Performance Monitoring",
            "description": "Implement more detailed performance tracking for continuous optimization.",
            "implementation": [
                "Add query execution time tracking",
                "Implement performance alerting",
                "Create performance dashboards"
            ],
            "expected_improvement": "Better visibility and proactive optimization"
        })
        
        return {
            "timestamp": datetime.now().isoformat(),
            "total_suggestions": len(suggestions),
            "suggestions": suggestions,
            "system_status": {
                "performance_grade": _calculate_performance_grade(metrics),
                "optimization_score": _calculate_optimization_score(metrics)
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting optimization suggestions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get optimization suggestions: {str(e)}")

@router.post("/optimization/apply")
async def apply_optimization(
    optimization_type: str = Query(..., description="Type of optimization to apply"),
    force: bool = Query(False, description="Force apply optimization")
):
    """
    Apply specific optimizations to the region system.
    
    Available optimization types:
    - cache_cleanup: Clean expired cache entries
    - cache_warmup: Pre-load frequently accessed data
    - stats_refresh: Refresh cached statistics
    """
    try:
        repo = get_region_repository()
        
        if optimization_type == "cache_cleanup":
            # Clean expired cache entries
            repo._cleanup_expired_cache()
            return {
                "status": "success",
                "optimization": "cache_cleanup",
                "message": "Expired cache entries cleaned up",
                "timestamp": datetime.now().isoformat()
            }
        
        elif optimization_type == "cache_warmup":
            # Pre-load frequently accessed data
            # Get some basic statistics to warm the cache
            repo.get_statistics()
            repo.get_all(limit=50)  # Load first 50 regions
            
            return {
                "status": "success",
                "optimization": "cache_warmup",
                "message": "Cache warmed with frequently accessed data",
                "timestamp": datetime.now().isoformat()
            }
        
        elif optimization_type == "stats_refresh":
            # Force refresh of cached statistics
            cache_key = "stats_regions_all"
            if cache_key in repo._cache:
                del repo._cache[cache_key]
                if cache_key in repo._cache_ttl:
                    del repo._cache_ttl[cache_key]
            
            # Reload statistics
            repo.get_statistics()
            
            return {
                "status": "success",
                "optimization": "stats_refresh",
                "message": "Statistics cache refreshed",
                "timestamp": datetime.now().isoformat()
            }
        
        else:
            raise HTTPException(
                status_code=400, 
                detail=f"Unknown optimization type: {optimization_type}"
            )
        
    except Exception as e:
        logger.error(f"Error applying optimization: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to apply optimization: {str(e)}")

@router.get("/health", response_model=Dict[str, Any])
async def performance_health_check():
    """
    Quick performance health check for the region system.
    """
    try:
        repo = get_region_repository()
        metrics = repo.get_performance_metrics()
        
        # Basic health indicators
        cache_hit_rate = metrics.get("cache_hit_rate", 0)
        query_count = metrics.get("query_count", 0)
        cache_size = metrics.get("cache_size", 0)
        
        # Overall health assessment
        health_score = 100
        issues = []
        
        if cache_hit_rate < 50:
            health_score -= 30
            issues.append("Low cache hit rate")
        elif cache_hit_rate < 70:
            health_score -= 15
            issues.append("Moderate cache hit rate")
        
        if query_count > 1000:
            health_score -= 20
            issues.append("High query count")
        elif query_count > 500:
            health_score -= 10
            issues.append("Moderate query count")
        
        if cache_size > 800:
            health_score -= 15
            issues.append("High memory usage")
        
        # Determine overall status
        if health_score >= 90:
            status = "excellent"
        elif health_score >= 75:
            status = "good"
        elif health_score >= 50:
            status = "fair"
        else:
            status = "poor"
        
        return {
            "timestamp": datetime.now().isoformat(),
            "status": status,
            "health_score": health_score,
            "performance_metrics": {
                "cache_hit_rate": cache_hit_rate,
                "query_count": query_count,
                "cache_size": cache_size
            },
            "issues": issues,
            "optimizations_active": {
                "caching": True,
                "query_optimization": True,
                "bulk_operations": True
            }
        }
        
    except Exception as e:
        logger.error(f"Error during performance health check: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Performance health check failed: {str(e)}")

def _calculate_performance_grade(metrics: Dict[str, Any]) -> str:
    """Calculate overall performance grade based on metrics."""
    cache_hit_rate = metrics.get("cache_hit_rate", 0)
    query_count = metrics.get("query_count", 0)
    
    score = 0
    
    # Cache performance (40% weight)
    if cache_hit_rate >= 80:
        score += 40
    elif cache_hit_rate >= 60:
        score += 30
    elif cache_hit_rate >= 40:
        score += 20
    else:
        score += 10
    
    # Query efficiency (35% weight)
    if query_count <= 100:
        score += 35
    elif query_count <= 500:
        score += 25
    elif query_count <= 1000:
        score += 15
    else:
        score += 5
    
    # Optimization features (25% weight)
    score += 25  # All optimization features are implemented
    
    if score >= 90:
        return "A"
    elif score >= 80:
        return "B"
    elif score >= 70:
        return "C"
    elif score >= 60:
        return "D"
    else:
        return "F"

def _calculate_optimization_score(metrics: Dict[str, Any]) -> int:
    """Calculate optimization score out of 100."""
    cache_hit_rate = metrics.get("cache_hit_rate", 0)
    query_count = metrics.get("query_count", 0)
    cache_size = metrics.get("cache_size", 0)
    
    score = 0
    
    # Cache efficiency
    score += min(cache_hit_rate, 100) * 0.4
    
    # Query optimization (inverse scoring)
    if query_count <= 100:
        score += 30
    elif query_count <= 500:
        score += 20
    elif query_count <= 1000:
        score += 10
    
    # Memory efficiency
    if cache_size <= 200:
        score += 30
    elif cache_size <= 500:
        score += 20
    elif cache_size <= 800:
        score += 10
    
    return min(int(score), 100) 
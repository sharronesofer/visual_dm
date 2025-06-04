"""
LLM Usage Analytics and Cost Tracking

This module provides comprehensive tracking of LLM usage, costs, performance metrics,
and business intelligence for optimization and budget management.
"""

import asyncio
import json
import time
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import logging
from collections import defaultdict, deque
import statistics

logger = logging.getLogger(__name__)

class ModelProvider(Enum):
    """LLM model providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    OLLAMA = "ollama"
    COHERE = "cohere"
    PERPLEXITY = "perplexity"

class UsageContext(Enum):
    """Context categories for usage tracking"""
    ARC_GENERATION = "arc_generation"
    QUEST_GENERATION = "quest_generation"
    OUTCOME_BRANCHING = "outcome_branching"
    CHARACTER_DEVELOPMENT = "character_development"
    DIALOGUE_GENERATION = "dialogue_generation"
    WORLD_BUILDING = "world_building"
    NARRATIVE_CONTINUATION = "narrative_continuation"
    VALIDATION = "validation"
    ANALYSIS = "analysis"

@dataclass
class UsageMetric:
    """Individual usage metric record"""
    timestamp: float
    context: UsageContext
    model_provider: ModelProvider
    model_name: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    cost_usd: float
    latency_seconds: float
    success: bool
    error_type: Optional[str] = None
    cache_hit: bool = False
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    request_id: Optional[str] = None

@dataclass
class CostBreakdown:
    """Cost breakdown by different dimensions"""
    total_cost: float
    by_provider: Dict[str, float]
    by_context: Dict[str, float]
    by_model: Dict[str, float]
    by_day: Dict[str, float]
    by_user: Dict[str, float]

@dataclass
class PerformanceMetrics:
    """Performance metrics summary"""
    avg_latency: float
    median_latency: float
    p95_latency: float
    success_rate: float
    cache_hit_rate: float
    avg_tokens_per_request: float
    requests_per_minute: float

@dataclass
class BudgetAlert:
    """Budget alert configuration and status"""
    name: str
    threshold_usd: float
    period_days: int
    current_spend: float
    triggered: bool
    alert_type: str  # "warning", "limit", "critical"

class LLMUsageTracker:
    """
    Comprehensive LLM usage tracking and analytics system.
    
    Features:
    - Real-time cost tracking
    - Performance monitoring
    - Budget alerts and controls
    - Usage analytics and reporting
    - Optimization recommendations
    """
    
    def __init__(self, storage_backend=None):
        self.storage = storage_backend or InMemoryStorage()
        self.metrics_queue = deque(maxlen=10000)  # Recent metrics buffer
        self.budget_alerts = {}
        self.optimization_cache = {}
        
        # Model pricing (per 1K tokens) - update these with actual pricing
        self.pricing = {
            ModelProvider.OPENAI: {
                "gpt-4": {"input": 0.03, "output": 0.06},
                "gpt-4-turbo": {"input": 0.01, "output": 0.03},
                "gpt-3.5-turbo": {"input": 0.001, "output": 0.002},
            },
            ModelProvider.ANTHROPIC: {
                "claude-3-opus": {"input": 0.015, "output": 0.075},
                "claude-3-sonnet": {"input": 0.003, "output": 0.015},
                "claude-3-haiku": {"input": 0.00025, "output": 0.00125},
            },
            ModelProvider.PERPLEXITY: {
                "sonar-medium-online": {"input": 0.0002, "output": 0.0002},
                "sonar-large-online": {"input": 0.001, "output": 0.001},
            },
            ModelProvider.OLLAMA: {
                "default": {"input": 0.0, "output": 0.0},  # Local models are free
            }
        }
        
        # Performance monitoring
        self.request_counts = defaultdict(int)
        self.error_counts = defaultdict(int)
        self.latency_samples = defaultdict(lambda: deque(maxlen=1000))
    
    async def track_request(
        self,
        context: UsageContext,
        model_provider: ModelProvider,
        model_name: str,
        prompt_tokens: int,
        completion_tokens: int,
        latency_seconds: float,
        success: bool = True,
        error_type: Optional[str] = None,
        cache_hit: bool = False,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        request_id: Optional[str] = None
    ) -> UsageMetric:
        """
        Track a single LLM request with all relevant metrics.
        
        Args:
            context: The usage context (arc generation, etc.)
            model_provider: Provider (OpenAI, Anthropic, etc.)
            model_name: Specific model used
            prompt_tokens: Number of input tokens
            completion_tokens: Number of output tokens
            latency_seconds: Request latency
            success: Whether the request succeeded
            error_type: Type of error if failed
            cache_hit: Whether this was served from cache
            user_id: Optional user identifier
            session_id: Optional session identifier
            request_id: Optional request identifier
            
        Returns:
            UsageMetric record
        """
        total_tokens = prompt_tokens + completion_tokens
        cost_usd = self._calculate_cost(model_provider, model_name, prompt_tokens, completion_tokens)
        
        metric = UsageMetric(
            timestamp=time.time(),
            context=context,
            model_provider=model_provider,
            model_name=model_name,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            cost_usd=cost_usd,
            latency_seconds=latency_seconds,
            success=success,
            error_type=error_type,
            cache_hit=cache_hit,
            user_id=user_id,
            session_id=session_id,
            request_id=request_id
        )
        
        # Store metric
        await self.storage.store_metric(metric)
        self.metrics_queue.append(metric)
        
        # Update real-time counters
        self._update_realtime_metrics(metric)
        
        # Check budget alerts
        await self._check_budget_alerts(metric)
        
        # Log for monitoring
        if success:
            logger.info(f"LLM request tracked: {context.value}, {model_provider.value}/{model_name}, "
                       f"{total_tokens} tokens, ${cost_usd:.4f}, {latency_seconds:.2f}s")
        else:
            logger.warning(f"LLM request failed: {context.value}, {error_type}, "
                          f"{latency_seconds:.2f}s")
        
        return metric
    
    def _calculate_cost(
        self,
        provider: ModelProvider,
        model_name: str,
        prompt_tokens: int,
        completion_tokens: int
    ) -> float:
        """Calculate cost in USD for the request"""
        try:
            provider_pricing = self.pricing.get(provider, {})
            model_pricing = provider_pricing.get(model_name)
            
            if not model_pricing:
                # Fallback to first available model pricing for the provider
                if provider_pricing:
                    model_pricing = list(provider_pricing.values())[0]
                else:
                    logger.warning(f"No pricing data for {provider.value}/{model_name}")
                    return 0.0
            
            input_cost = (prompt_tokens / 1000) * model_pricing["input"]
            output_cost = (completion_tokens / 1000) * model_pricing["output"]
            
            return input_cost + output_cost
            
        except Exception as e:
            logger.error(f"Error calculating cost: {e}")
            return 0.0
    
    def _update_realtime_metrics(self, metric: UsageMetric):
        """Update real-time performance metrics"""
        key = f"{metric.model_provider.value}/{metric.model_name}"
        
        # Update counters
        self.request_counts[key] += 1
        if not metric.success:
            self.error_counts[key] += 1
        
        # Update latency samples
        self.latency_samples[key].append(metric.latency_seconds)
    
    async def _check_budget_alerts(self, metric: UsageMetric):
        """Check if any budget alerts should be triggered"""
        for alert_name, alert in self.budget_alerts.items():
            if alert.triggered:
                continue
            
            # Calculate current spend for the alert period
            period_start = time.time() - (alert.period_days * 24 * 3600)
            current_spend = await self.get_cost_summary(
                start_time=period_start,
                end_time=time.time()
            )
            
            alert.current_spend = current_spend.total_cost
            
            # Check if threshold is exceeded
            if current_spend.total_cost >= alert.threshold_usd:
                alert.triggered = True
                await self._trigger_budget_alert(alert, metric)
    
    async def _trigger_budget_alert(self, alert: BudgetAlert, metric: UsageMetric):
        """Trigger a budget alert"""
        logger.warning(f"Budget alert triggered: {alert.name}, "
                      f"${alert.current_spend:.2f} >= ${alert.threshold_usd:.2f}")
        
        # Here you could integrate with notification systems
        # (email, Slack, webhook, etc.)
    
    async def get_cost_summary(
        self,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None,
        group_by: List[str] = None
    ) -> CostBreakdown:
        """
        Get cost breakdown for specified time period.
        
        Args:
            start_time: Start timestamp (default: 24 hours ago)
            end_time: End timestamp (default: now)
            group_by: Additional grouping dimensions
            
        Returns:
            CostBreakdown with detailed cost analysis
        """
        if end_time is None:
            end_time = time.time()
        if start_time is None:
            start_time = end_time - (24 * 3600)  # 24 hours ago
        
        metrics = await self.storage.get_metrics(start_time, end_time)
        
        total_cost = 0.0
        by_provider = defaultdict(float)
        by_context = defaultdict(float)
        by_model = defaultdict(float)
        by_day = defaultdict(float)
        by_user = defaultdict(float)
        
        for metric in metrics:
            total_cost += metric.cost_usd
            by_provider[metric.model_provider.value] += metric.cost_usd
            by_context[metric.context.value] += metric.cost_usd
            by_model[f"{metric.model_provider.value}/{metric.model_name}"] += metric.cost_usd
            
            # Group by day
            day_key = datetime.fromtimestamp(metric.timestamp).strftime("%Y-%m-%d")
            by_day[day_key] += metric.cost_usd
            
            # Group by user if available
            if metric.user_id:
                by_user[metric.user_id] += metric.cost_usd
        
        return CostBreakdown(
            total_cost=total_cost,
            by_provider=dict(by_provider),
            by_context=dict(by_context),
            by_model=dict(by_model),
            by_day=dict(by_day),
            by_user=dict(by_user)
        )
    
    async def get_performance_metrics(
        self,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None
    ) -> PerformanceMetrics:
        """Get performance metrics for specified time period"""
        if end_time is None:
            end_time = time.time()
        if start_time is None:
            start_time = end_time - (24 * 3600)
        
        metrics = await self.storage.get_metrics(start_time, end_time)
        
        if not metrics:
            return PerformanceMetrics(0, 0, 0, 0, 0, 0, 0)
        
        # Calculate metrics
        latencies = [m.latency_seconds for m in metrics]
        successes = [m for m in metrics if m.success]
        cache_hits = [m for m in metrics if m.cache_hit]
        token_counts = [m.total_tokens for m in metrics]
        
        time_span_hours = (end_time - start_time) / 3600
        requests_per_minute = len(metrics) / (time_span_hours * 60) if time_span_hours > 0 else 0
        
        return PerformanceMetrics(
            avg_latency=statistics.mean(latencies) if latencies else 0,
            median_latency=statistics.median(latencies) if latencies else 0,
            p95_latency=statistics.quantiles(latencies, n=20)[18] if len(latencies) >= 20 else 0,
            success_rate=len(successes) / len(metrics) if metrics else 0,
            cache_hit_rate=len(cache_hits) / len(metrics) if metrics else 0,
            avg_tokens_per_request=statistics.mean(token_counts) if token_counts else 0,
            requests_per_minute=requests_per_minute
        )
    
    def add_budget_alert(
        self,
        name: str,
        threshold_usd: float,
        period_days: int,
        alert_type: str = "warning"
    ):
        """Add a budget alert configuration"""
        self.budget_alerts[name] = BudgetAlert(
            name=name,
            threshold_usd=threshold_usd,
            period_days=period_days,
            current_spend=0.0,
            triggered=False,
            alert_type=alert_type
        )
    
    async def get_optimization_recommendations(self) -> List[Dict[str, Any]]:
        """Generate optimization recommendations based on usage patterns"""
        recommendations = []
        
        # Get recent metrics for analysis
        end_time = time.time()
        start_time = end_time - (7 * 24 * 3600)  # Last 7 days
        metrics = await self.storage.get_metrics(start_time, end_time)
        
        if not metrics:
            return recommendations
        
        # Analyze cost by context
        context_costs = defaultdict(float)
        context_counts = defaultdict(int)
        for metric in metrics:
            context_costs[metric.context.value] += metric.cost_usd
            context_counts[metric.context.value] += 1
        
        # Recommend cheaper models for high-volume, low-criticality contexts
        for context, cost in context_costs.items():
            if cost > 10.0 and context_counts[context] > 100:  # High cost, high volume
                recommendations.append({
                    "type": "model_optimization",
                    "context": context,
                    "current_cost": cost,
                    "suggestion": "Consider using a cheaper model for this high-volume context",
                    "potential_savings": cost * 0.3,  # Estimate 30% savings
                    "priority": "medium"
                })
        
        # Analyze cache hit rates
        cache_hit_rate = sum(1 for m in metrics if m.cache_hit) / len(metrics)
        if cache_hit_rate < 0.1:  # Low cache hit rate
            recommendations.append({
                "type": "caching_optimization",
                "current_hit_rate": cache_hit_rate,
                "suggestion": "Improve caching strategy to reduce redundant LLM calls",
                "potential_savings": sum(m.cost_usd for m in metrics) * 0.2,  # Estimate 20% savings
                "priority": "high"
            })
        
        # Analyze error rates
        error_rate = sum(1 for m in metrics if not m.success) / len(metrics)
        if error_rate > 0.05:  # High error rate
            recommendations.append({
                "type": "reliability_improvement",
                "error_rate": error_rate,
                "suggestion": "High error rate detected. Review prompts and model selection",
                "wasted_cost": sum(m.cost_usd for m in metrics if not m.success),
                "priority": "high"
            })
        
        # Analyze provider distribution
        provider_costs = defaultdict(float)
        for metric in metrics:
            provider_costs[metric.model_provider.value] += metric.cost_usd
        
        if len(provider_costs) == 1 and ModelProvider.OLLAMA.value not in provider_costs:
            recommendations.append({
                "type": "provider_diversification",
                "suggestion": "Consider using local models (Ollama) for development and testing",
                "potential_savings": list(provider_costs.values())[0] * 0.1,  # 10% of current spend
                "priority": "low"
            })
        
        return recommendations
    
    async def export_usage_report(
        self,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None,
        format: str = "json"
    ) -> Dict[str, Any]:
        """Export comprehensive usage report"""
        if end_time is None:
            end_time = time.time()
        if start_time is None:
            start_time = end_time - (30 * 24 * 3600)  # 30 days ago
        
        # Gather all data
        cost_summary = await self.get_cost_summary(start_time, end_time)
        performance = await self.get_performance_metrics(start_time, end_time)
        recommendations = await self.get_optimization_recommendations()
        metrics = await self.storage.get_metrics(start_time, end_time)
        
        report = {
            "report_generated": datetime.now().isoformat(),
            "period": {
                "start": datetime.fromtimestamp(start_time).isoformat(),
                "end": datetime.fromtimestamp(end_time).isoformat(),
                "days": (end_time - start_time) / (24 * 3600)
            },
            "summary": {
                "total_requests": len(metrics),
                "total_cost": cost_summary.total_cost,
                "total_tokens": sum(m.total_tokens for m in metrics),
                "avg_cost_per_request": cost_summary.total_cost / len(metrics) if metrics else 0,
                "success_rate": performance.success_rate,
                "cache_hit_rate": performance.cache_hit_rate
            },
            "cost_breakdown": asdict(cost_summary),
            "performance_metrics": asdict(performance),
            "budget_alerts": {name: asdict(alert) for name, alert in self.budget_alerts.items()},
            "optimization_recommendations": recommendations,
            "detailed_metrics": [asdict(m) for m in metrics[-100:]]  # Last 100 requests
        }
        
        return report
    
    def get_realtime_stats(self) -> Dict[str, Any]:
        """Get real-time statistics from recent requests"""
        recent_metrics = list(self.metrics_queue)[-100:]  # Last 100 requests
        
        if not recent_metrics:
            return {"error": "No recent metrics available"}
        
        return {
            "recent_requests": len(recent_metrics),
            "success_rate": sum(1 for m in recent_metrics if m.success) / len(recent_metrics),
            "avg_latency": statistics.mean([m.latency_seconds for m in recent_metrics]),
            "total_cost_last_100": sum(m.cost_usd for m in recent_metrics),
            "cache_hit_rate": sum(1 for m in recent_metrics if m.cache_hit) / len(recent_metrics),
            "contexts_used": list(set(m.context.value for m in recent_metrics)),
            "providers_used": list(set(m.model_provider.value for m in recent_metrics))
        }

class InMemoryStorage:
    """Simple in-memory storage for metrics (replace with persistent storage)"""
    
    def __init__(self):
        self.metrics = []
    
    async def store_metric(self, metric: UsageMetric):
        """Store a metric"""
        self.metrics.append(metric)
        
        # Keep only recent metrics to prevent memory issues
        if len(self.metrics) > 100000:
            self.metrics = self.metrics[-50000:]  # Keep last 50k
    
    async def get_metrics(
        self,
        start_time: float,
        end_time: float
    ) -> List[UsageMetric]:
        """Get metrics within time range"""
        return [
            m for m in self.metrics
            if start_time <= m.timestamp <= end_time
        ]

# Global tracker instance
_global_tracker = None

def get_usage_tracker() -> LLMUsageTracker:
    """Get global usage tracker instance"""
    global _global_tracker
    if _global_tracker is None:
        _global_tracker = LLMUsageTracker()
    return _global_tracker 
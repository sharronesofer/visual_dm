"""
Diplomacy Analytics Service

Infrastructure service for monitoring and analyzing diplomacy system performance,
tracking key metrics, and providing insights for optimization.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from uuid import UUID
from collections import defaultdict, Counter
import json

# Infrastructure imports for metrics collection
from backend.infrastructure.monitoring.metrics_collector import MetricsCollector
from backend.infrastructure.storage.analytics_storage import AnalyticsStorage


class DiplomacyAnalyticsService:
    """
    Infrastructure service for diplomacy system analytics.
    
    Tracks performance metrics, analyzes patterns, and provides insights
    for system optimization and game balance.
    """
    
    def __init__(self, 
                 metrics_collector: Optional[MetricsCollector] = None,
                 storage: Optional[AnalyticsStorage] = None):
        self.metrics_collector = metrics_collector or MetricsCollector()
        self.storage = storage or AnalyticsStorage()
        
        # Metric tracking
        self.performance_metrics = {
            "api_response_times": defaultdict(list),
            "database_query_times": defaultdict(list),
            "llm_generation_times": defaultdict(list),
            "websocket_message_counts": defaultdict(int),
            "error_counts": defaultdict(int),
            "active_connections": 0,
            "concurrent_negotiations": 0,
            "system_load": 0.0
        }
        
        # Game balance metrics
        self.game_metrics = {
            "treaty_success_rate": 0.0,
            "negotiation_duration_avg": 0.0,
            "faction_diplomatic_activity": defaultdict(int),
            "conflict_escalation_rate": 0.0,
            "alliance_stability": 0.0,
            "tension_distribution": defaultdict(int),
            "ai_decision_accuracy": 0.0
        }
        
        # Real-time tracking
        self.active_negotiations = set()
        self.recent_events = []
        self.connection_count = 0
        
        # Start background analytics collection
        self._start_analytics_collection()
    
    async def track_api_performance(self, endpoint: str, response_time: float, success: bool):
        """Track API endpoint performance metrics."""
        self.performance_metrics["api_response_times"][endpoint].append(response_time)
        
        if not success:
            self.performance_metrics["error_counts"][endpoint] += 1
        
        # Keep only recent data (last 1000 requests per endpoint)
        if len(self.performance_metrics["api_response_times"][endpoint]) > 1000:
            self.performance_metrics["api_response_times"][endpoint] = \
                self.performance_metrics["api_response_times"][endpoint][-1000:]
        
        await self.metrics_collector.record_metric(
            "diplomacy_api_response_time",
            response_time,
            tags={"endpoint": endpoint, "success": str(success)}
        )
    
    async def track_database_performance(self, query_type: str, execution_time: float):
        """Track database query performance."""
        self.performance_metrics["database_query_times"][query_type].append(execution_time)
        
        # Keep only recent data
        if len(self.performance_metrics["database_query_times"][query_type]) > 500:
            self.performance_metrics["database_query_times"][query_type] = \
                self.performance_metrics["database_query_times"][query_type][-500:]
        
        await self.metrics_collector.record_metric(
            "diplomacy_db_query_time",
            execution_time,
            tags={"query_type": query_type}
        )
    
    async def track_llm_performance(self, operation: str, generation_time: float, 
                                  token_count: int, success: bool):
        """Track LLM generation performance."""
        self.performance_metrics["llm_generation_times"][operation].append(generation_time)
        
        await self.metrics_collector.record_metric(
            "diplomacy_llm_generation_time",
            generation_time,
            tags={"operation": operation, "success": str(success)}
        )
        
        await self.metrics_collector.record_metric(
            "diplomacy_llm_token_count",
            token_count,
            tags={"operation": operation}
        )
    
    async def track_websocket_activity(self, message_type: str, faction_id: UUID = None):
        """Track WebSocket message activity."""
        self.performance_metrics["websocket_message_counts"][message_type] += 1
        
        if faction_id:
            self.game_metrics["faction_diplomatic_activity"][str(faction_id)] += 1
        
        await self.metrics_collector.record_metric(
            "diplomacy_websocket_messages",
            1,
            tags={"message_type": message_type}
        )
    
    async def track_negotiation_started(self, negotiation_id: UUID, parties: List[UUID]):
        """Track when a negotiation starts."""
        self.active_negotiations.add(negotiation_id)
        self.performance_metrics["concurrent_negotiations"] = len(self.active_negotiations)
        
        for faction_id in parties:
            self.game_metrics["faction_diplomatic_activity"][str(faction_id)] += 1
        
        await self.metrics_collector.record_metric(
            "diplomacy_active_negotiations",
            len(self.active_negotiations)
        )
    
    async def track_negotiation_ended(self, negotiation_id: UUID, outcome: str, 
                                    duration_minutes: float):
        """Track when a negotiation ends."""
        self.active_negotiations.discard(negotiation_id)
        self.performance_metrics["concurrent_negotiations"] = len(self.active_negotiations)
        
        # Update success rate
        success = outcome in ["treaty_signed", "agreement_reached"]
        await self._update_success_rate(success)
        
        # Update average duration
        await self._update_negotiation_duration(duration_minutes)
        
        await self.metrics_collector.record_metric(
            "diplomacy_negotiation_duration",
            duration_minutes,
            tags={"outcome": outcome}
        )
    
    async def track_treaty_signed(self, treaty_id: UUID, parties: List[UUID], 
                                treaty_type: str):
        """Track treaty signing events."""
        for faction_id in parties:
            self.game_metrics["faction_diplomatic_activity"][str(faction_id)] += 1
        
        await self.metrics_collector.record_metric(
            "diplomacy_treaties_signed",
            1,
            tags={"treaty_type": treaty_type, "party_count": str(len(parties))}
        )
    
    async def track_conflict_escalation(self, faction_a: UUID, faction_b: UUID, 
                                      escalation_type: str):
        """Track conflict escalation events."""
        await self.metrics_collector.record_metric(
            "diplomacy_conflict_escalations",
            1,
            tags={"escalation_type": escalation_type}
        )
        
        # Update escalation rate
        await self._update_escalation_rate()
    
    async def track_tension_change(self, faction_a: UUID, faction_b: UUID, 
                                 old_tension: int, new_tension: int, reason: str):
        """Track tension level changes between factions."""
        tension_change = new_tension - old_tension
        
        # Update tension distribution
        tension_range = self._get_tension_range(new_tension)
        self.game_metrics["tension_distribution"][tension_range] += 1
        
        await self.metrics_collector.record_metric(
            "diplomacy_tension_change",
            tension_change,
            tags={
                "reason": reason,
                "tension_range": tension_range,
                "direction": "increase" if tension_change > 0 else "decrease"
            }
        )
    
    async def track_ai_decision(self, decision_type: str, confidence: float, 
                              outcome_success: bool):
        """Track AI decision-making performance."""
        await self.metrics_collector.record_metric(
            "diplomacy_ai_decision_confidence",
            confidence,
            tags={"decision_type": decision_type, "success": str(outcome_success)}
        )
        
        # Update AI accuracy
        await self._update_ai_accuracy(outcome_success)
    
    async def track_connection_change(self, connected: bool, connection_type: str = "general"):
        """Track WebSocket connection changes."""
        if connected:
            self.connection_count += 1
        else:
            self.connection_count = max(0, self.connection_count - 1)
        
        self.performance_metrics["active_connections"] = self.connection_count
        
        await self.metrics_collector.record_metric(
            "diplomacy_active_connections",
            self.connection_count,
            tags={"connection_type": connection_type}
        )
    
    async def get_performance_summary(self) -> Dict[str, Any]:
        """Get current performance metrics summary."""
        return {
            "api_performance": await self._calculate_api_performance(),
            "database_performance": await self._calculate_db_performance(),
            "llm_performance": await self._calculate_llm_performance(),
            "websocket_activity": dict(self.performance_metrics["websocket_message_counts"]),
            "active_connections": self.performance_metrics["active_connections"],
            "concurrent_negotiations": self.performance_metrics["concurrent_negotiations"],
            "error_rates": await self._calculate_error_rates(),
            "system_health": await self._assess_system_health()
        }
    
    async def get_game_balance_summary(self) -> Dict[str, Any]:
        """Get current game balance metrics summary."""
        return {
            "treaty_success_rate": self.game_metrics["treaty_success_rate"],
            "avg_negotiation_duration": self.game_metrics["negotiation_duration_avg"],
            "conflict_escalation_rate": self.game_metrics["conflict_escalation_rate"],
            "alliance_stability": self.game_metrics["alliance_stability"],
            "ai_decision_accuracy": self.game_metrics["ai_decision_accuracy"],
            "faction_activity": dict(self.game_metrics["faction_diplomatic_activity"]),
            "tension_distribution": dict(self.game_metrics["tension_distribution"]),
            "most_active_factions": await self._get_most_active_factions(),
            "diplomatic_trends": await self._analyze_diplomatic_trends()
        }
    
    async def get_optimization_recommendations(self) -> List[Dict[str, Any]]:
        """Generate optimization recommendations based on metrics."""
        recommendations = []
        
        # Performance recommendations
        api_perf = await self._calculate_api_performance()
        if api_perf["avg_response_time"] > 1000:  # > 1 second
            recommendations.append({
                "type": "performance",
                "priority": "high",
                "issue": "High API response times",
                "recommendation": "Consider adding caching or optimizing database queries",
                "metric_value": api_perf["avg_response_time"],
                "threshold": 1000
            })
        
        # Database performance
        db_perf = await self._calculate_db_performance()
        if db_perf["avg_query_time"] > 500:  # > 500ms
            recommendations.append({
                "type": "performance",
                "priority": "medium",
                "issue": "Slow database queries",
                "recommendation": "Add database indexes or optimize queries",
                "metric_value": db_perf["avg_query_time"],
                "threshold": 500
            })
        
        # Game balance recommendations
        if self.game_metrics["treaty_success_rate"] < 0.3:  # < 30%
            recommendations.append({
                "type": "game_balance",
                "priority": "medium",
                "issue": "Low treaty success rate",
                "recommendation": "Adjust negotiation difficulty or AI behavior",
                "metric_value": self.game_metrics["treaty_success_rate"],
                "threshold": 0.3
            })
        
        if self.game_metrics["conflict_escalation_rate"] > 0.7:  # > 70%
            recommendations.append({
                "type": "game_balance",
                "priority": "high",
                "issue": "High conflict escalation rate",
                "recommendation": "Increase diplomatic options or reduce tension triggers",
                "metric_value": self.game_metrics["conflict_escalation_rate"],
                "threshold": 0.7
            })
        
        # LLM performance
        llm_perf = await self._calculate_llm_performance()
        if llm_perf["avg_generation_time"] > 5000:  # > 5 seconds
            recommendations.append({
                "type": "performance",
                "priority": "high",
                "issue": "Slow LLM generation",
                "recommendation": "Optimize prompts or consider faster model",
                "metric_value": llm_perf["avg_generation_time"],
                "threshold": 5000
            })
        
        return recommendations
    
    async def export_analytics_report(self, timeframe_hours: int = 24) -> Dict[str, Any]:
        """Export comprehensive analytics report."""
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=timeframe_hours)
        
        return {
            "report_metadata": {
                "generated_at": end_time.isoformat(),
                "timeframe_start": start_time.isoformat(),
                "timeframe_end": end_time.isoformat(),
                "timeframe_hours": timeframe_hours
            },
            "performance_metrics": await self.get_performance_summary(),
            "game_balance_metrics": await self.get_game_balance_summary(),
            "optimization_recommendations": await self.get_optimization_recommendations(),
            "system_alerts": await self._get_system_alerts(),
            "trend_analysis": await self._analyze_trends(start_time, end_time),
            "resource_utilization": await self._get_resource_utilization()
        }
    
    # Private helper methods
    
    def _start_analytics_collection(self):
        """Start background analytics collection tasks."""
        # In a real implementation, this would start background tasks
        # for periodic metrics collection and analysis
        pass
    
    async def _calculate_api_performance(self) -> Dict[str, float]:
        """Calculate API performance metrics."""
        all_times = []
        for endpoint_times in self.performance_metrics["api_response_times"].values():
            all_times.extend(endpoint_times)
        
        if not all_times:
            return {"avg_response_time": 0.0, "p95_response_time": 0.0, "p99_response_time": 0.0}
        
        all_times.sort()
        return {
            "avg_response_time": sum(all_times) / len(all_times),
            "p95_response_time": all_times[int(len(all_times) * 0.95)] if all_times else 0.0,
            "p99_response_time": all_times[int(len(all_times) * 0.99)] if all_times else 0.0
        }
    
    async def _calculate_db_performance(self) -> Dict[str, float]:
        """Calculate database performance metrics."""
        all_times = []
        for query_times in self.performance_metrics["database_query_times"].values():
            all_times.extend(query_times)
        
        if not all_times:
            return {"avg_query_time": 0.0, "max_query_time": 0.0}
        
        return {
            "avg_query_time": sum(all_times) / len(all_times),
            "max_query_time": max(all_times)
        }
    
    async def _calculate_llm_performance(self) -> Dict[str, float]:
        """Calculate LLM performance metrics."""
        all_times = []
        for op_times in self.performance_metrics["llm_generation_times"].values():
            all_times.extend(op_times)
        
        if not all_times:
            return {"avg_generation_time": 0.0, "max_generation_time": 0.0}
        
        return {
            "avg_generation_time": sum(all_times) / len(all_times),
            "max_generation_time": max(all_times)
        }
    
    async def _calculate_error_rates(self) -> Dict[str, float]:
        """Calculate error rates by endpoint."""
        error_rates = {}
        for endpoint, error_count in self.performance_metrics["error_counts"].items():
            total_requests = len(self.performance_metrics["api_response_times"][endpoint])
            if total_requests > 0:
                error_rates[endpoint] = error_count / total_requests
        return error_rates
    
    async def _assess_system_health(self) -> str:
        """Assess overall system health."""
        api_perf = await self._calculate_api_performance()
        error_rates = await self._calculate_error_rates()
        
        if api_perf["avg_response_time"] > 2000 or max(error_rates.values(), default=0) > 0.1:
            return "degraded"
        elif api_perf["avg_response_time"] > 1000 or max(error_rates.values(), default=0) > 0.05:
            return "warning"
        else:
            return "healthy"
    
    async def _update_success_rate(self, success: bool):
        """Update treaty success rate."""
        # This would typically be calculated from stored data
        # For now, use a simple moving average approach
        current_rate = self.game_metrics["treaty_success_rate"]
        weight = 0.1  # Weight for new data
        self.game_metrics["treaty_success_rate"] = (
            current_rate * (1 - weight) + (1.0 if success else 0.0) * weight
        )
    
    async def _update_negotiation_duration(self, duration: float):
        """Update average negotiation duration."""
        current_avg = self.game_metrics["negotiation_duration_avg"]
        weight = 0.1
        self.game_metrics["negotiation_duration_avg"] = (
            current_avg * (1 - weight) + duration * weight
        )
    
    async def _update_escalation_rate(self):
        """Update conflict escalation rate."""
        # This would be calculated from historical data
        pass
    
    async def _update_ai_accuracy(self, success: bool):
        """Update AI decision accuracy."""
        current_accuracy = self.game_metrics["ai_decision_accuracy"]
        weight = 0.1
        self.game_metrics["ai_decision_accuracy"] = (
            current_accuracy * (1 - weight) + (1.0 if success else 0.0) * weight
        )
    
    def _get_tension_range(self, tension: int) -> str:
        """Get tension range category."""
        if tension < -50:
            return "very_negative"
        elif tension < -20:
            return "negative"
        elif tension < 20:
            return "neutral"
        elif tension < 50:
            return "positive"
        else:
            return "very_positive"
    
    async def _get_most_active_factions(self) -> List[Tuple[str, int]]:
        """Get most diplomatically active factions."""
        activity = self.game_metrics["faction_diplomatic_activity"]
        return sorted(activity.items(), key=lambda x: x[1], reverse=True)[:10]
    
    async def _analyze_diplomatic_trends(self) -> Dict[str, Any]:
        """Analyze diplomatic activity trends."""
        # This would analyze historical data for trends
        return {
            "treaty_activity": "stable",
            "conflict_trend": "decreasing",
            "alliance_formation": "increasing"
        }
    
    async def _get_system_alerts(self) -> List[Dict[str, Any]]:
        """Get current system alerts."""
        alerts = []
        
        if self.performance_metrics["active_connections"] > 1000:
            alerts.append({
                "level": "warning",
                "message": "High number of active connections",
                "value": self.performance_metrics["active_connections"]
            })
        
        if self.performance_metrics["concurrent_negotiations"] > 100:
            alerts.append({
                "level": "info",
                "message": "High diplomatic activity",
                "value": self.performance_metrics["concurrent_negotiations"]
            })
        
        return alerts
    
    async def _analyze_trends(self, start_time: datetime, end_time: datetime) -> Dict[str, Any]:
        """Analyze trends over the specified timeframe."""
        # This would analyze stored historical data
        return {
            "api_performance_trend": "stable",
            "user_activity_trend": "increasing",
            "error_rate_trend": "decreasing"
        }
    
    async def _get_resource_utilization(self) -> Dict[str, float]:
        """Get resource utilization metrics."""
        return {
            "cpu_usage": 0.0,  # Would be collected from system monitors
            "memory_usage": 0.0,
            "database_connections": 0.0,
            "llm_api_quota_used": 0.0
        }


def create_diplomacy_analytics_service() -> DiplomacyAnalyticsService:
    """Factory function to create diplomacy analytics service."""
    return DiplomacyAnalyticsService() 
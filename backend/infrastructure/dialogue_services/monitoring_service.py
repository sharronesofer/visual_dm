"""
Dialogue System Monitoring Service

This module provides comprehensive monitoring for the dialogue system including
performance metrics, conversation analytics, AI response tracking, and system health.
"""

import logging
import asyncio
import json
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from collections import defaultdict, deque
from dataclasses import dataclass, field
from enum import Enum
import psutil
from uuid import uuid4

from backend.infrastructure.monitoring.performance_monitor import PerformanceMonitor, PerformanceSnapshot
from backend.infrastructure.shared.exceptions import DialogueMonitoringError

logger = logging.getLogger(__name__)


class DialogueMetricType(Enum):
    """Types of dialogue-specific metrics"""
    CONVERSATION_DURATION = "conversation_duration"
    MESSAGE_RESPONSE_TIME = "message_response_time"
    AI_GENERATION_TIME = "ai_generation_time"
    CACHE_HIT_RATE = "cache_hit_rate"
    WEBSOCKET_CONNECTION_TIME = "websocket_connection_time"
    CONVERSATION_COMPLETION_RATE = "conversation_completion_rate"
    NPC_PERSONALITY_LOAD_TIME = "npc_personality_load_time"
    BARTERING_SUCCESS_RATE = "bartering_success_rate"
    CONTEXT_WINDOW_SIZE = "context_window_size"
    MEMORY_USAGE_PER_CONVERSATION = "memory_usage_per_conversation"


@dataclass
class ConversationMetrics:
    """Metrics for individual conversations"""
    conversation_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    message_count: int = 0
    total_response_time_ms: float = 0.0
    ai_generation_time_ms: float = 0.0
    cache_hits: int = 0
    cache_misses: int = 0
    errors: int = 0
    npc_id: str = ""
    player_id: str = ""
    interaction_type: str = ""
    
    @property
    def duration_seconds(self) -> float:
        """Calculate conversation duration in seconds"""
        if not self.end_time:
            return (datetime.utcnow() - self.start_time).total_seconds()
        return (self.end_time - self.start_time).total_seconds()
    
    @property
    def average_response_time_ms(self) -> float:
        """Calculate average response time"""
        if self.message_count == 0:
            return 0.0
        return self.total_response_time_ms / self.message_count
    
    @property
    def cache_hit_rate(self) -> float:
        """Calculate cache hit rate"""
        total_requests = self.cache_hits + self.cache_misses
        if total_requests == 0:
            return 0.0
        return self.cache_hits / total_requests


@dataclass
class DialogueSystemHealth:
    """Overall dialogue system health metrics"""
    timestamp: datetime
    active_conversations: int
    total_conversations_today: int
    average_response_time_ms: float
    ai_service_health: bool
    cache_service_health: bool
    database_health: bool
    websocket_connections: int
    error_rate_percent: float
    cache_hit_rate_percent: float
    memory_usage_mb: float
    cpu_usage_percent: float
    
    # Performance scores (0-100)
    response_time_score: float = 0.0
    reliability_score: float = 0.0
    efficiency_score: float = 0.0
    overall_health_score: float = 0.0
    
    custom_metrics: Dict[str, float] = field(default_factory=dict)


class ConversationAnalytics:
    """Analytics for conversation patterns and trends"""
    
    def __init__(self, max_history: int = 1000):
        self.max_history = max_history
        self.conversation_history: deque = deque(maxlen=max_history)
        self.daily_stats: Dict[str, Dict[str, Any]] = defaultdict(dict)
        self.npc_interaction_stats: Dict[str, Dict[str, Any]] = defaultdict(dict)
        self.player_behavior_stats: Dict[str, Dict[str, Any]] = defaultdict(dict)
    
    def record_conversation(self, metrics: ConversationMetrics):
        """Record conversation metrics for analytics"""
        self.conversation_history.append(metrics)
        
        # Update daily stats
        date_key = metrics.start_time.strftime('%Y-%m-%d')
        if date_key not in self.daily_stats:
            self.daily_stats[date_key] = {
                'total_conversations': 0,
                'total_messages': 0,
                'total_duration_seconds': 0.0,
                'total_response_time_ms': 0.0,
                'unique_players': set(),
                'unique_npcs': set(),
                'interaction_types': defaultdict(int)
            }
        
        daily = self.daily_stats[date_key]
        daily['total_conversations'] += 1
        daily['total_messages'] += metrics.message_count
        daily['total_duration_seconds'] += metrics.duration_seconds
        daily['total_response_time_ms'] += metrics.total_response_time_ms
        daily['unique_players'].add(metrics.player_id)
        daily['unique_npcs'].add(metrics.npc_id)
        daily['interaction_types'][metrics.interaction_type] += 1
        
        # Update NPC stats
        npc_stats = self.npc_interaction_stats[metrics.npc_id]
        npc_stats['total_conversations'] = npc_stats.get('total_conversations', 0) + 1
        npc_stats['total_messages'] = npc_stats.get('total_messages', 0) + metrics.message_count
        npc_stats['average_response_time'] = npc_stats.get('average_response_time', 0.0)
        
        # Update player stats
        player_stats = self.player_behavior_stats[metrics.player_id]
        player_stats['total_conversations'] = player_stats.get('total_conversations', 0) + 1
        player_stats['total_messages'] = player_stats.get('total_messages', 0) + metrics.message_count
        player_stats['favorite_npcs'] = player_stats.get('favorite_npcs', defaultdict(int))
        player_stats['favorite_npcs'][metrics.npc_id] += 1
    
    def get_conversation_trends(self, days: int = 7) -> Dict[str, Any]:
        """Get conversation trends over specified days"""
        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(days=days)
        
        trends = {
            'daily_conversation_counts': [],
            'daily_message_counts': [],
            'daily_average_duration': [],
            'daily_response_times': [],
            'popular_npcs': defaultdict(int),
            'popular_interaction_types': defaultdict(int)
        }
        
        for i in range(days):
            date = start_date + timedelta(days=i)
            date_key = date.strftime('%Y-%m-%d')
            
            if date_key in self.daily_stats:
                stats = self.daily_stats[date_key]
                trends['daily_conversation_counts'].append(stats['total_conversations'])
                trends['daily_message_counts'].append(stats['total_messages'])
                
                avg_duration = stats['total_duration_seconds'] / max(stats['total_conversations'], 1)
                trends['daily_average_duration'].append(avg_duration)
                
                avg_response = stats['total_response_time_ms'] / max(stats['total_messages'], 1)
                trends['daily_response_times'].append(avg_response)
                
                # Aggregate popular NPCs and interaction types
                for npc in stats['unique_npcs']:
                    trends['popular_npcs'][npc] += 1
                
                for interaction_type, count in stats['interaction_types'].items():
                    trends['popular_interaction_types'][interaction_type] += count
            else:
                trends['daily_conversation_counts'].append(0)
                trends['daily_message_counts'].append(0)
                trends['daily_average_duration'].append(0.0)
                trends['daily_response_times'].append(0.0)
        
        return trends


class DialogueMonitoringService:
    """
    Comprehensive monitoring service for the dialogue system
    """
    
    def __init__(self, performance_monitor: Optional[PerformanceMonitor] = None):
        self.performance_monitor = performance_monitor or PerformanceMonitor()
        self.analytics = ConversationAnalytics()
        
        # Active conversation tracking
        self.active_conversations: Dict[str, ConversationMetrics] = {}
        self.active_operations: Dict[str, datetime] = {}
        
        # System health tracking
        self.health_snapshots: deque = deque(maxlen=100)
        self.last_health_check = datetime.utcnow()
        self.health_check_interval = 60  # seconds
        
        # Performance thresholds
        self.thresholds = {
            'max_response_time_ms': 2000.0,
            'max_ai_generation_time_ms': 5000.0,
            'min_cache_hit_rate': 0.7,
            'max_error_rate': 0.05,
            'max_memory_per_conversation_mb': 50.0,
            'max_active_conversations': 1000
        }
        
        # Alerts and notifications
        self.alerts: List[Dict[str, Any]] = []
        self.performance_warnings: List[Dict[str, Any]] = []
        
        logger.info("Dialogue Monitoring Service initialized")
    
    async def initialize(self):
        """Initialize monitoring service"""
        try:
            await self.performance_monitor.initialize()
            
            # Start background health monitoring
            asyncio.create_task(self._background_health_monitoring())
            
            logger.info("Dialogue Monitoring Service initialization complete")
            
        except Exception as e:
            logger.error(f"Failed to initialize Dialogue Monitoring Service: {e}")
            raise DialogueMonitoringError(f"Monitoring initialization failed: {e}")
    
    def start_conversation_tracking(self, conversation_id: str, npc_id: str, 
                                  player_id: str, interaction_type: str) -> ConversationMetrics:
        """Start tracking a new conversation"""
        metrics = ConversationMetrics(
            conversation_id=conversation_id,
            start_time=datetime.utcnow(),
            npc_id=npc_id,
            player_id=player_id,
            interaction_type=interaction_type
        )
        
        self.active_conversations[conversation_id] = metrics
        
        # Check for too many active conversations
        if len(self.active_conversations) > self.thresholds['max_active_conversations']:
            self._add_alert("high_conversation_load", 
                          f"High number of active conversations: {len(self.active_conversations)}")
        
        logger.debug(f"Started tracking conversation {conversation_id}")
        return metrics
    
    def end_conversation_tracking(self, conversation_id: str):
        """End tracking for a conversation"""
        if conversation_id in self.active_conversations:
            metrics = self.active_conversations.pop(conversation_id)
            metrics.end_time = datetime.utcnow()
            
            # Record in analytics
            self.analytics.record_conversation(metrics)
            
            # Check performance thresholds
            self._check_conversation_performance(metrics)
            
            logger.debug(f"Ended tracking conversation {conversation_id}")
    
    def record_message_response(self, conversation_id: str, response_time_ms: float, 
                              ai_generation_time_ms: float = 0.0, cache_hit: bool = False):
        """Record metrics for a message response"""
        if conversation_id in self.active_conversations:
            metrics = self.active_conversations[conversation_id]
            metrics.message_count += 1
            metrics.total_response_time_ms += response_time_ms
            metrics.ai_generation_time_ms += ai_generation_time_ms
            
            if cache_hit:
                metrics.cache_hits += 1
            else:
                metrics.cache_misses += 1
            
            # Check response time threshold
            if response_time_ms > self.thresholds['max_response_time_ms']:
                self._add_performance_warning("slow_response", 
                                            f"Slow response time: {response_time_ms:.2f}ms for conversation {conversation_id}")
            
            # Check AI generation time
            if ai_generation_time_ms > self.thresholds['max_ai_generation_time_ms']:
                self._add_performance_warning("slow_ai_generation", 
                                            f"Slow AI generation: {ai_generation_time_ms:.2f}ms for conversation {conversation_id}")
    
    def record_error(self, conversation_id: str, error_type: str, error_message: str):
        """Record an error for a conversation"""
        if conversation_id in self.active_conversations:
            self.active_conversations[conversation_id].errors += 1
        
        self._add_alert("dialogue_error", f"{error_type}: {error_message} in conversation {conversation_id}")
    
    def start_operation_timing(self, operation_name: str) -> str:
        """Start timing a dialogue operation"""
        context_id = f"{operation_name}_{uuid4().hex[:8]}"
        self.active_operations[context_id] = datetime.utcnow()
        return context_id
    
    def end_operation_timing(self, context_id: str, success: bool = True) -> float:
        """End timing a dialogue operation"""
        if context_id in self.active_operations:
            start_time = self.active_operations.pop(context_id)
            duration_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            # Record in performance monitor
            operation_name = context_id.split('_')[0]
            self.performance_monitor.end_operation(context_id, success, operation_name)
            
            return duration_ms
        
        return 0.0
    
    async def get_system_health(self) -> DialogueSystemHealth:
        """Get current dialogue system health metrics"""
        try:
            # Get performance snapshot
            perf_snapshot = await self.performance_monitor.take_performance_snapshot()
            
            # Calculate dialogue-specific metrics
            active_conv_count = len(self.active_conversations)
            
            # Calculate average response time from active conversations
            total_response_time = sum(conv.total_response_time_ms for conv in self.active_conversations.values())
            total_messages = sum(conv.message_count for conv in self.active_conversations.values())
            avg_response_time = total_response_time / max(total_messages, 1)
            
            # Calculate cache hit rate
            total_hits = sum(conv.cache_hits for conv in self.active_conversations.values())
            total_requests = sum(conv.cache_hits + conv.cache_misses for conv in self.active_conversations.values())
            cache_hit_rate = (total_hits / max(total_requests, 1)) * 100
            
            # Calculate error rate
            total_errors = sum(conv.errors for conv in self.active_conversations.values())
            error_rate = (total_errors / max(total_messages, 1)) * 100
            
            # Get today's conversation count
            today_key = datetime.utcnow().strftime('%Y-%m-%d')
            today_conversations = self.analytics.daily_stats.get(today_key, {}).get('total_conversations', 0)
            
            # Create health snapshot
            health = DialogueSystemHealth(
                timestamp=datetime.utcnow(),
                active_conversations=active_conv_count,
                total_conversations_today=today_conversations,
                average_response_time_ms=avg_response_time,
                ai_service_health=True,  # TODO: Implement actual health checks
                cache_service_health=True,  # TODO: Implement actual health checks
                database_health=True,  # TODO: Implement actual health checks
                websocket_connections=active_conv_count,  # Approximation
                error_rate_percent=error_rate,
                cache_hit_rate_percent=cache_hit_rate,
                memory_usage_mb=perf_snapshot.memory_usage_mb,
                cpu_usage_percent=perf_snapshot.cpu_usage_percent
            )
            
            # Calculate performance scores
            health.response_time_score = self._calculate_response_time_score(avg_response_time)
            health.reliability_score = self._calculate_reliability_score(error_rate)
            health.efficiency_score = self._calculate_efficiency_score(cache_hit_rate, perf_snapshot.cpu_usage_percent)
            health.overall_health_score = (health.response_time_score + health.reliability_score + health.efficiency_score) / 3
            
            # Store health snapshot
            self.health_snapshots.append(health)
            
            return health
            
        except Exception as e:
            logger.error(f"Failed to get system health: {e}")
            raise DialogueMonitoringError(f"Health check failed: {e}")
    
    def get_conversation_analytics(self, days: int = 7) -> Dict[str, Any]:
        """Get conversation analytics and trends"""
        return self.analytics.get_conversation_trends(days)
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary"""
        try:
            # Get base performance summary
            base_summary = self.performance_monitor.get_performance_summary()
            
            # Add dialogue-specific metrics
            dialogue_summary = {
                'active_conversations': len(self.active_conversations),
                'total_tracked_conversations': len(self.analytics.conversation_history),
                'recent_alerts': len([a for a in self.alerts if 
                                    (datetime.utcnow() - datetime.fromisoformat(a['timestamp'])).seconds < 3600]),
                'performance_warnings': len(self.performance_warnings),
                'conversation_metrics': {}
            }
            
            # Add conversation-specific metrics
            if self.active_conversations:
                conv_metrics = list(self.active_conversations.values())
                dialogue_summary['conversation_metrics'] = {
                    'average_duration_seconds': sum(c.duration_seconds for c in conv_metrics) / len(conv_metrics),
                    'average_message_count': sum(c.message_count for c in conv_metrics) / len(conv_metrics),
                    'total_cache_hits': sum(c.cache_hits for c in conv_metrics),
                    'total_cache_misses': sum(c.cache_misses for c in conv_metrics),
                    'total_errors': sum(c.errors for c in conv_metrics)
                }
            
            # Combine summaries
            return {**base_summary, 'dialogue_system': dialogue_summary}
            
        except Exception as e:
            logger.error(f"Failed to get performance summary: {e}")
            return {'error': str(e)}
    
    def _check_conversation_performance(self, metrics: ConversationMetrics):
        """Check conversation performance against thresholds"""
        # Check average response time
        if metrics.average_response_time_ms > self.thresholds['max_response_time_ms']:
            self._add_performance_warning("slow_conversation", 
                                        f"Conversation {metrics.conversation_id} had slow average response time: {metrics.average_response_time_ms:.2f}ms")
        
        # Check cache hit rate
        if metrics.cache_hit_rate < self.thresholds['min_cache_hit_rate']:
            self._add_performance_warning("low_cache_hit_rate", 
                                        f"Conversation {metrics.conversation_id} had low cache hit rate: {metrics.cache_hit_rate:.2%}")
        
        # Check error rate
        error_rate = metrics.errors / max(metrics.message_count, 1)
        if error_rate > self.thresholds['max_error_rate']:
            self._add_alert("high_error_rate", 
                          f"Conversation {metrics.conversation_id} had high error rate: {error_rate:.2%}")
    
    def _calculate_response_time_score(self, avg_response_time_ms: float) -> float:
        """Calculate response time performance score (0-100)"""
        if avg_response_time_ms <= 500:
            return 100.0
        elif avg_response_time_ms <= 1000:
            return 80.0
        elif avg_response_time_ms <= 2000:
            return 60.0
        elif avg_response_time_ms <= 5000:
            return 40.0
        else:
            return 20.0
    
    def _calculate_reliability_score(self, error_rate_percent: float) -> float:
        """Calculate reliability performance score (0-100)"""
        if error_rate_percent <= 1.0:
            return 100.0
        elif error_rate_percent <= 3.0:
            return 80.0
        elif error_rate_percent <= 5.0:
            return 60.0
        elif error_rate_percent <= 10.0:
            return 40.0
        else:
            return 20.0
    
    def _calculate_efficiency_score(self, cache_hit_rate_percent: float, cpu_usage_percent: float) -> float:
        """Calculate efficiency performance score (0-100)"""
        cache_score = min(cache_hit_rate_percent, 100.0)
        cpu_score = max(0, 100 - cpu_usage_percent)
        return (cache_score + cpu_score) / 2
    
    def _add_alert(self, alert_type: str, message: str):
        """Add a system alert"""
        alert = {
            'id': uuid4().hex,
            'type': alert_type,
            'message': message,
            'timestamp': datetime.utcnow().isoformat(),
            'severity': 'high'
        }
        self.alerts.append(alert)
        
        # Keep only recent alerts
        cutoff_time = datetime.utcnow() - timedelta(hours=24)
        self.alerts = [a for a in self.alerts if 
                      datetime.fromisoformat(a['timestamp']) > cutoff_time]
        
        logger.warning(f"Dialogue Alert [{alert_type}]: {message}")
    
    def _add_performance_warning(self, warning_type: str, message: str):
        """Add a performance warning"""
        warning = {
            'id': uuid4().hex,
            'type': warning_type,
            'message': message,
            'timestamp': datetime.utcnow().isoformat(),
            'severity': 'medium'
        }
        self.performance_warnings.append(warning)
        
        # Keep only recent warnings
        cutoff_time = datetime.utcnow() - timedelta(hours=6)
        self.performance_warnings = [w for w in self.performance_warnings if 
                                   datetime.fromisoformat(w['timestamp']) > cutoff_time]
        
        logger.info(f"Dialogue Warning [{warning_type}]: {message}")
    
    async def _background_health_monitoring(self):
        """Background task for continuous health monitoring"""
        while True:
            try:
                await asyncio.sleep(self.health_check_interval)
                
                # Perform health check
                health = await self.get_system_health()
                
                # Check for health issues
                if health.overall_health_score < 50:
                    self._add_alert("poor_system_health", 
                                  f"Dialogue system health score is low: {health.overall_health_score:.1f}")
                
                if health.error_rate_percent > 10:
                    self._add_alert("high_error_rate", 
                                  f"High system error rate: {health.error_rate_percent:.1f}%")
                
                if health.average_response_time_ms > 3000:
                    self._add_alert("slow_system_response", 
                                  f"Slow system response time: {health.average_response_time_ms:.1f}ms")
                
                self.last_health_check = datetime.utcnow()
                
            except Exception as e:
                logger.error(f"Background health monitoring error: {e}")
                await asyncio.sleep(30)  # Wait before retrying
    
    def get_recent_alerts(self, count: int = 10) -> List[Dict[str, Any]]:
        """Get recent alerts"""
        return sorted(self.alerts, key=lambda x: x['timestamp'], reverse=True)[:count]
    
    def get_recent_warnings(self, count: int = 10) -> List[Dict[str, Any]]:
        """Get recent performance warnings"""
        return sorted(self.performance_warnings, key=lambda x: x['timestamp'], reverse=True)[:count]
    
    def clear_alerts(self):
        """Clear all alerts"""
        self.alerts.clear()
        self.performance_warnings.clear()
    
    async def cleanup(self):
        """Cleanup monitoring service"""
        try:
            # End all active conversation tracking
            for conversation_id in list(self.active_conversations.keys()):
                self.end_conversation_tracking(conversation_id)
            
            # Cleanup performance monitor
            if self.performance_monitor:
                self.performance_monitor.stop_monitoring()
            
            logger.info("Dialogue Monitoring Service cleanup complete")
            
        except Exception as e:
            logger.error(f"Error during monitoring service cleanup: {e}")


def create_dialogue_monitoring_service(performance_monitor: Optional[PerformanceMonitor] = None) -> DialogueMonitoringService:
    """Factory function to create dialogue monitoring service"""
    return DialogueMonitoringService(performance_monitor) 
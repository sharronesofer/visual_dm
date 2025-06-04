"""
Autonomous NPC Monitoring Service

Provides comprehensive monitoring and analytics for autonomous NPC systems including:
- Real-time system health monitoring
- NPC population statistics and demographics
- Economic cycle status and trends
- Crisis event monitoring and alerting
- Performance metrics and analytics
- Alert management and notifications
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from uuid import UUID
from dataclasses import dataclass, asdict
from collections import defaultdict
import json

from backend.infrastructure.systems.npc.models.models import NpcEntity
from backend.infrastructure.systems.npc.models.autonomous_lifecycle_models import (
    NpcTierStatus, NpcEconomicHistory, NpcLifeEvent
)
from backend.infrastructure.systems.npc.models.personality_evolution_models import (
    NpcPersonalityEvolution, NpcCrisisResponse, NpcPersonalitySnapshot
)
from backend.infrastructure.systems.npc.models.emotional_state_models import NpcEmotionalState

logger = logging.getLogger(__name__)


@dataclass
class SystemAlert:
    """System alert for monitoring dashboard"""
    alert_id: str
    alert_type: str  # 'warning', 'error', 'info', 'critical'
    title: str
    description: str
    timestamp: datetime
    resolved: bool = False
    severity: int = 1  # 1-5, 5 being most severe
    affected_systems: List[str] = None
    recommended_actions: List[str] = None


@dataclass
class PerformanceMetric:
    """Performance metric for monitoring"""
    metric_name: str
    current_value: float
    target_value: float
    unit: str
    trend: str  # 'improving', 'declining', 'stable'
    last_updated: datetime


@dataclass
class PopulationStatistics:
    """NPC population statistics"""
    total_npcs: int
    by_tier: Dict[int, int]
    by_race: Dict[str, int]
    by_lifecycle_phase: Dict[str, int]
    by_region: Dict[str, int]
    active_percentage: float
    average_age: float


class AutonomousNpcMonitoringService:
    """Monitoring service for autonomous NPC systems"""
    
    def __init__(self, db_session):
        self.db_session = db_session
        self.alerts: List[SystemAlert] = []
        self.performance_history: Dict[str, List[PerformanceMetric]] = defaultdict(list)
        
        # Alert thresholds
        self.alert_thresholds = {
            "error_rate": {"warning": 0.05, "critical": 0.15},
            "processing_time": {"warning": 10.0, "critical": 30.0},
            "system_load": {"warning": 0.7, "critical": 0.9},
            "crisis_events": {"warning": 10, "critical": 50},
            "failed_evolutions": {"warning": 5, "critical": 20}
        }
    
    def get_real_time_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive real-time dashboard data"""
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "system_health": self.get_system_health_overview(),
            "population_stats": self.get_population_statistics(),
            "economic_status": self.get_economic_cycle_status(),
            "crisis_monitoring": self.get_crisis_monitoring_data(),
            "performance_metrics": self.get_performance_metrics(),
            "recent_alerts": self.get_recent_alerts(limit=10),
            "activity_summary": self.get_activity_summary()
        }
    
    def get_system_health_overview(self) -> Dict[str, Any]:
        """Get comprehensive system health overview"""
        
        # Count active entities and processes
        total_npcs = self.db_session.query(NpcEntity).count()
        
        active_emotional_states = self.db_session.query(NpcEmotionalState).filter(
            NpcEmotionalState.last_updated >= datetime.utcnow() - timedelta(hours=24)
        ).count()
        
        ongoing_personality_evolutions = self.db_session.query(NpcPersonalityEvolution).filter(
            NpcPersonalityEvolution.is_complete == False
        ).count()
        
        active_crisis_responses = self.db_session.query(NpcCrisisResponse).filter(
            NpcCrisisResponse.response_completed == False
        ).count()
        
        # Calculate health percentages
        emotional_health = (active_emotional_states / max(total_npcs, 1)) * 100
        personality_activity = (ongoing_personality_evolutions / max(total_npcs, 1)) * 100
        crisis_load = (active_crisis_responses / max(total_npcs, 1)) * 100
        
        # Determine overall system status
        if crisis_load > 20 or emotional_health < 50:
            system_status = "critical"
        elif crisis_load > 10 or emotional_health < 70:
            system_status = "warning"
        else:
            system_status = "healthy"
        
        return {
            "overall_status": system_status,
            "total_npcs": total_npcs,
            "active_emotional_states": active_emotional_states,
            "ongoing_personality_evolutions": ongoing_personality_evolutions,
            "active_crisis_responses": active_crisis_responses,
            "health_percentages": {
                "emotional_health": round(emotional_health, 1),
                "personality_activity": round(personality_activity, 1),
                "crisis_load": round(crisis_load, 1)
            },
            "last_updated": datetime.utcnow().isoformat()
        }
    
    def get_population_statistics(self) -> PopulationStatistics:
        """Get detailed NPC population statistics"""
        
        # Get all NPCs with tier information
        npcs_with_tiers = self.db_session.query(NpcEntity, NpcTierStatus).outerjoin(
            NpcTierStatus, NpcEntity.id == NpcTierStatus.npc_id
        ).all()
        
        total_npcs = len(npcs_with_tiers)
        by_tier = {1: 0, 2: 0, 3: 0, 4: 0}
        by_race = defaultdict(int)
        by_lifecycle_phase = defaultdict(int)
        by_region = defaultdict(int)
        
        total_age = 0
        active_count = 0
        
        for npc, tier_status in npcs_with_tiers:
            # Tier statistics
            tier = tier_status.current_tier if tier_status else 4
            by_tier[tier] += 1
            
            # Race statistics
            by_race[npc.race or "Unknown"] += 1
            
            # Lifecycle phase statistics
            lifecycle_phase = getattr(npc, 'lifecycle_phase', 'unknown')
            by_lifecycle_phase[lifecycle_phase] += 1
            
            # Region statistics
            by_region[npc.region_id or "Unknown"] += 1
            
            # Age statistics
            if npc.age:
                total_age += npc.age
            
            # Activity statistics (has recent emotional state updates)
            emotional_state = self.db_session.query(NpcEmotionalState).filter(
                NpcEmotionalState.npc_id == npc.id,
                NpcEmotionalState.last_updated >= datetime.utcnow() - timedelta(days=7)
            ).first()
            
            if emotional_state:
                active_count += 1
        
        average_age = total_age / max(total_npcs, 1)
        active_percentage = (active_count / max(total_npcs, 1)) * 100
        
        return PopulationStatistics(
            total_npcs=total_npcs,
            by_tier=dict(by_tier),
            by_race=dict(by_race),
            by_lifecycle_phase=dict(by_lifecycle_phase),
            by_region=dict(by_region),
            active_percentage=round(active_percentage, 1),
            average_age=round(average_age, 1)
        )
    
    def get_economic_cycle_status(self) -> Dict[str, Any]:
        """Get economic cycle status and trends"""
        
        try:
            from backend.infrastructure.database.economy.advanced_models import EconomicCycle
            
            # Get active economic cycles
            active_cycles = self.db_session.query(EconomicCycle).filter(
                EconomicCycle.is_active == True
            ).all()
            
            cycle_summary = {
                "total_active_cycles": len(active_cycles),
                "cycles_by_phase": defaultdict(int),
                "cycles_by_region": defaultdict(int),
                "average_prosperity": 0.0,
                "average_inflation": 0.0,
                "average_unemployment": 0.0,
                "last_updated": datetime.utcnow().isoformat()
            }
            
            if active_cycles:
                total_prosperity = 0
                total_inflation = 0
                total_unemployment = 0
                
                for cycle in active_cycles:
                    cycle_summary["cycles_by_phase"][cycle.current_phase] += 1
                    cycle_summary["cycles_by_region"][cycle.region_id] += 1
                    
                    total_prosperity += cycle.prosperity_level or 0.5
                    total_inflation += cycle.inflation_rate or 0.0
                    total_unemployment += cycle.unemployment_rate or 0.05
                
                cycle_summary["average_prosperity"] = round(total_prosperity / len(active_cycles), 3)
                cycle_summary["average_inflation"] = round(total_inflation / len(active_cycles), 3)
                cycle_summary["average_unemployment"] = round(total_unemployment / len(active_cycles), 3)
            
            # Get recent economic transactions
            recent_transactions = self.db_session.query(NpcEconomicHistory).filter(
                NpcEconomicHistory.transaction_date >= datetime.utcnow() - timedelta(days=7)
            ).count()
            
            cycle_summary["recent_economic_activity"] = recent_transactions
            
            return dict(cycle_summary)
            
        except Exception as e:
            logger.error(f"Error getting economic cycle status: {e}")
            return {
                "error": "Economic data unavailable",
                "last_updated": datetime.utcnow().isoformat()
            }
    
    def get_crisis_monitoring_data(self) -> Dict[str, Any]:
        """Get crisis monitoring and alert data"""
        
        # Active crisis responses
        active_crises = self.db_session.query(NpcCrisisResponse).filter(
            NpcCrisisResponse.response_completed == False
        ).all()
        
        # Recent crisis responses (last 30 days)
        recent_crises = self.db_session.query(NpcCrisisResponse).filter(
            NpcCrisisResponse.crisis_start_date >= datetime.utcnow() - timedelta(days=30)
        ).all()
        
        # Crisis statistics
        crisis_types = defaultdict(int)
        response_types = defaultdict(int)
        crisis_severity_distribution = defaultdict(int)
        
        for crisis in recent_crises:
            crisis_types[crisis.crisis_type] += 1
            response_types[crisis.response_type] += 1
            
            # Bin severity into ranges
            severity = int(crisis.crisis_severity)
            if severity <= 3:
                crisis_severity_distribution["Low (1-3)"] += 1
            elif severity <= 6:
                crisis_severity_distribution["Medium (4-6)"] += 1
            elif severity <= 8:
                crisis_severity_distribution["High (7-8)"] += 1
            else:
                crisis_severity_distribution["Critical (9-10)"] += 1
        
        # Calculate crisis resolution rate
        completed_crises = [c for c in recent_crises if c.response_completed]
        resolution_rate = len(completed_crises) / max(len(recent_crises), 1) * 100
        
        return {
            "active_crisis_count": len(active_crises),
            "recent_crisis_count": len(recent_crises),
            "crisis_resolution_rate": round(resolution_rate, 1),
            "crisis_types": dict(crisis_types),
            "response_types": dict(response_types),
            "severity_distribution": dict(crisis_severity_distribution),
            "active_crises": [
                {
                    "id": str(crisis.id),
                    "type": crisis.crisis_type,
                    "severity": crisis.crisis_severity,
                    "npc_id": str(crisis.npc_id),
                    "days_active": (datetime.utcnow() - crisis.crisis_start_date).days,
                    "response_type": crisis.response_type
                }
                for crisis in active_crises[:10]  # Show top 10
            ]
        }
    
    def get_performance_metrics(self) -> Dict[str, PerformanceMetric]:
        """Get current performance metrics"""
        
        metrics = {}
        
        # Processing efficiency
        recent_evolutions = self.db_session.query(NpcPersonalityEvolution).filter(
            NpcPersonalityEvolution.started_at >= datetime.utcnow() - timedelta(hours=24)
        ).all()
        
        if recent_evolutions:
            completed_evolutions = [e for e in recent_evolutions if e.is_complete]
            completion_rate = len(completed_evolutions) / len(recent_evolutions) * 100
        else:
            completion_rate = 100.0
        
        metrics["evolution_completion_rate"] = PerformanceMetric(
            metric_name="Evolution Completion Rate",
            current_value=completion_rate,
            target_value=95.0,
            unit="%",
            trend="stable",
            last_updated=datetime.utcnow()
        )
        
        # Crisis response effectiveness
        recent_completed_crises = self.db_session.query(NpcCrisisResponse).filter(
            NpcCrisisResponse.crisis_end_date >= datetime.utcnow() - timedelta(days=7),
            NpcCrisisResponse.response_completed == True
        ).all()
        
        if recent_completed_crises:
            avg_effectiveness = sum(c.response_effectiveness for c in recent_completed_crises) / len(recent_completed_crises)
        else:
            avg_effectiveness = 7.0  # Default
        
        metrics["crisis_response_effectiveness"] = PerformanceMetric(
            metric_name="Crisis Response Effectiveness",
            current_value=avg_effectiveness,
            target_value=7.5,
            unit="/10",
            trend="stable",
            last_updated=datetime.utcnow()
        )
        
        # Emotional state stability
        emotional_states = self.db_session.query(NpcEmotionalState).filter(
            NpcEmotionalState.last_updated >= datetime.utcnow() - timedelta(hours=24)
        ).all()
        
        if emotional_states:
            avg_happiness = sum(state.happiness_level for state in emotional_states) / len(emotional_states)
            avg_stress = sum(abs(state.stress_level) for state in emotional_states) / len(emotional_states)
            emotional_stability = max(0, 10 - avg_stress + (avg_happiness / 2))
        else:
            emotional_stability = 7.0
        
        metrics["emotional_stability"] = PerformanceMetric(
            metric_name="Population Emotional Stability",
            current_value=emotional_stability,
            target_value=8.0,
            unit="/10",
            trend="stable",
            last_updated=datetime.utcnow()
        )
        
        return {name: asdict(metric) for name, metric in metrics.items()}
    
    def get_recent_alerts(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent system alerts"""
        
        # Sort alerts by timestamp (most recent first) and get unresolved ones first
        sorted_alerts = sorted(
            self.alerts,
            key=lambda a: (a.resolved, -a.timestamp.timestamp())
        )
        
        return [asdict(alert) for alert in sorted_alerts[:limit]]
    
    def get_activity_summary(self) -> Dict[str, Any]:
        """Get recent activity summary"""
        
        # Life events in last 24 hours
        recent_events = self.db_session.query(NpcLifeEvent).filter(
            NpcLifeEvent.event_date >= datetime.utcnow() - timedelta(hours=24)
        ).all()
        
        # Economic transactions in last 24 hours
        recent_transactions = self.db_session.query(NpcEconomicHistory).filter(
            NpcEconomicHistory.transaction_date >= datetime.utcnow() - timedelta(hours=24)
        ).count()
        
        # New personality snapshots in last 24 hours
        recent_snapshots = self.db_session.query(NpcPersonalitySnapshot).filter(
            NpcPersonalitySnapshot.snapshot_date >= datetime.utcnow() - timedelta(hours=24)
        ).count()
        
        # Event type distribution
        event_types = defaultdict(int)
        for event in recent_events:
            event_types[event.event_type] += 1
        
        return {
            "time_range": "Last 24 hours",
            "total_life_events": len(recent_events),
            "economic_transactions": recent_transactions,
            "personality_snapshots": recent_snapshots,
            "event_types": dict(event_types),
            "average_event_impact": round(
                sum(event.event_impact_score for event in recent_events) / max(len(recent_events), 1), 2
            )
        }
    
    def check_system_health_and_generate_alerts(self) -> List[SystemAlert]:
        """Check system health and generate alerts for issues"""
        
        new_alerts = []
        current_time = datetime.utcnow()
        
        # Check error rates in personality evolution
        failed_evolutions = self.db_session.query(NpcPersonalityEvolution).filter(
            NpcPersonalityEvolution.started_at >= current_time - timedelta(hours=24),
            NpcPersonalityEvolution.is_complete == False,
            NpcPersonalityEvolution.started_at <= current_time - timedelta(hours=1)  # Should have completed by now
        ).count()
        
        if failed_evolutions > self.alert_thresholds["failed_evolutions"]["critical"]:
            new_alerts.append(SystemAlert(
                alert_id=f"evolution_failures_{current_time.strftime('%Y%m%d_%H%M%S')}",
                alert_type="critical",
                title="High Personality Evolution Failure Rate",
                description=f"{failed_evolutions} personality evolutions have failed to complete in the last 24 hours",
                timestamp=current_time,
                severity=4,
                affected_systems=["personality_evolution"],
                recommended_actions=[
                    "Check personality evolution service logs",
                    "Verify database connectivity",
                    "Review recent system changes"
                ]
            ))
        elif failed_evolutions > self.alert_thresholds["failed_evolutions"]["warning"]:
            new_alerts.append(SystemAlert(
                alert_id=f"evolution_warnings_{current_time.strftime('%Y%m%d_%H%M%S')}",
                alert_type="warning",
                title="Elevated Personality Evolution Failures",
                description=f"{failed_evolutions} personality evolutions may be experiencing issues",
                timestamp=current_time,
                severity=2,
                affected_systems=["personality_evolution"],
                recommended_actions=["Monitor personality evolution processing"]
            ))
        
        # Check crisis event levels
        active_crises = self.db_session.query(NpcCrisisResponse).filter(
            NpcCrisisResponse.response_completed == False
        ).count()
        
        if active_crises > self.alert_thresholds["crisis_events"]["critical"]:
            new_alerts.append(SystemAlert(
                alert_id=f"crisis_overload_{current_time.strftime('%Y%m%d_%H%M%S')}",
                alert_type="critical",
                title="Crisis Event Overload",
                description=f"{active_crises} active crisis events may overwhelm the system",
                timestamp=current_time,
                severity=5,
                affected_systems=["crisis_response", "system_performance"],
                recommended_actions=[
                    "Review crisis event distribution",
                    "Consider batch processing optimizations",
                    "Monitor system resource usage"
                ]
            ))
        
        # Check emotional state processing
        stale_emotional_states = self.db_session.query(NpcEmotionalState).filter(
            NpcEmotionalState.last_updated <= current_time - timedelta(days=2)
        ).count()
        
        total_npcs = self.db_session.query(NpcEntity).count()
        stale_percentage = (stale_emotional_states / max(total_npcs, 1)) * 100
        
        if stale_percentage > 30:
            new_alerts.append(SystemAlert(
                alert_id=f"emotional_stale_{current_time.strftime('%Y%m%d_%H%M%S')}",
                alert_type="warning",
                title="Stale Emotional States Detected",
                description=f"{stale_percentage:.1f}% of NPCs have emotional states older than 2 days",
                timestamp=current_time,
                severity=3,
                affected_systems=["emotional_processing"],
                recommended_actions=[
                    "Check emotional state service scheduler",
                    "Verify daily processing tasks are running",
                    "Review system resource allocation"
                ]
            ))
        
        # Add new alerts to the collection
        self.alerts.extend(new_alerts)
        
        return new_alerts
    
    def resolve_alert(self, alert_id: str) -> bool:
        """Mark an alert as resolved"""
        for alert in self.alerts:
            if alert.alert_id == alert_id:
                alert.resolved = True
                return True
        return False
    
    def get_detailed_analytics(self, time_range_days: int = 7) -> Dict[str, Any]:
        """Get detailed analytics for the specified time range"""
        
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=time_range_days)
        
        # Personality evolution trends
        evolution_data = self.db_session.query(NpcPersonalityEvolution).filter(
            NpcPersonalityEvolution.started_at >= start_date
        ).all()
        
        evolution_trends = {
            "total_evolutions": len(evolution_data),
            "completed_evolutions": len([e for e in evolution_data if e.is_complete]),
            "average_duration": 0.0,
            "change_types": defaultdict(int)
        }
        
        if evolution_data:
            completed = [e for e in evolution_data if e.is_complete and e.completed_at]
            if completed:
                durations = [(e.completed_at - e.started_at).total_seconds() / 3600 for e in completed]  # hours
                evolution_trends["average_duration"] = round(sum(durations) / len(durations), 2)
            
            for evolution in evolution_data:
                evolution_trends["change_types"][evolution.change_type.value] += 1
        
        # Crisis response trends
        crisis_data = self.db_session.query(NpcCrisisResponse).filter(
            NpcCrisisResponse.crisis_start_date >= start_date
        ).all()
        
        crisis_trends = {
            "total_crises": len(crisis_data),
            "completed_crises": len([c for c in crisis_data if c.response_completed]),
            "average_effectiveness": 0.0,
            "crisis_types": defaultdict(int),
            "response_types": defaultdict(int)
        }
        
        if crisis_data:
            crisis_trends["average_effectiveness"] = round(
                sum(c.response_effectiveness for c in crisis_data) / len(crisis_data), 2
            )
            
            for crisis in crisis_data:
                crisis_trends["crisis_types"][crisis.crisis_type] += 1
                crisis_trends["response_types"][crisis.response_type] += 1
        
        # Economic activity trends
        economic_data = self.db_session.query(NpcEconomicHistory).filter(
            NpcEconomicHistory.transaction_date >= start_date
        ).all()
        
        economic_trends = {
            "total_transactions": len(economic_data),
            "transaction_types": defaultdict(int),
            "average_transaction_value": 0.0,
            "total_economic_value": 0.0
        }
        
        if economic_data:
            economic_trends["average_transaction_value"] = round(
                sum(abs(t.amount) for t in economic_data) / len(economic_data), 2
            )
            economic_trends["total_economic_value"] = round(
                sum(t.amount for t in economic_data), 2
            )
            
            for transaction in economic_data:
                economic_trends["transaction_types"][transaction.transaction_type.value] += 1
        
        return {
            "time_range": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "days": time_range_days
            },
            "personality_evolution_trends": dict(evolution_trends),
            "crisis_response_trends": dict(crisis_trends),
            "economic_activity_trends": dict(economic_trends)
        } 
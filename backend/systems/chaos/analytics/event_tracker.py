"""
Event Tracker

Tracks and analyzes chaos events for pattern recognition and optimization.
Maintains detailed event history and provides analytical insights.
"""

import asyncio
import json
import logging
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from enum import Enum
from pathlib import Path

from backend.systems.chaos.models.chaos_events import ChaosEvent, ChaosEventType, EventSeverity
from backend.systems.chaos.models.chaos_state import ChaosState
from backend.systems.chaos.models.pressure_data import PressureData
from backend.systems.chaos.core.config import ChaosConfig

logger = logging.getLogger(__name__)


class TrackingMetric(Enum):
    """Types of tracking metrics"""
    EVENT_COUNT = "event_count"
    EVENT_DURATION = "event_duration" 
    EVENT_IMPACT = "event_impact"
    PRESSURE_CORRELATION = "pressure_correlation"
    MITIGATION_EFFECTIVENESS = "mitigation_effectiveness"
    CASCADE_FREQUENCY = "cascade_frequency"
    REGIONAL_DISTRIBUTION = "regional_distribution"
    TEMPORAL_PATTERNS = "temporal_patterns"


@dataclass
class EventRecord:
    """Detailed record of a chaos event for tracking"""
    event_id: str = ""
    event_type: str = ""
    severity: str = ""
    title: str = ""
    description: str = ""
    
    # Timing information
    created_at: datetime = field(default_factory=datetime.now)
    triggered_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    duration_hours: float = 0.0
    actual_duration_hours: float = 0.0
    
    # Context at trigger
    chaos_score_at_trigger: float = 0.0
    pressure_sources_at_trigger: Dict[str, float] = field(default_factory=dict)
    regional_chaos_scores: Dict[str, float] = field(default_factory=dict)
    
    # Impact tracking
    affected_regions: List[str] = field(default_factory=list)
    global_event: bool = False
    immediate_effects_count: int = 0
    ongoing_effects_count: int = 0
    
    # Outcome tracking
    resolution_type: str = "auto"  # auto, manual, expired, cancelled
    resolution_quality: float = 1.0
    mitigation_applied: bool = False
    mitigation_effectiveness: float = 0.0
    
    # Cascading information
    was_cascade: bool = False
    parent_event_id: Optional[str] = None
    cascade_events: List[str] = field(default_factory=list)
    
    # Performance impact
    processing_time_ms: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'event_id': self.event_id,
            'event_type': self.event_type,
            'severity': self.severity,
            'title': self.title,
            'description': self.description,
            'created_at': self.created_at.isoformat(),
            'triggered_at': self.triggered_at.isoformat() if self.triggered_at else None,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'duration_hours': self.duration_hours,
            'actual_duration_hours': self.actual_duration_hours,
            'chaos_score_at_trigger': self.chaos_score_at_trigger,
            'pressure_sources_at_trigger': self.pressure_sources_at_trigger,
            'regional_chaos_scores': self.regional_chaos_scores,
            'affected_regions': self.affected_regions,
            'global_event': self.global_event,
            'immediate_effects_count': self.immediate_effects_count,
            'ongoing_effects_count': self.ongoing_effects_count,
            'resolution_type': self.resolution_type,
            'resolution_quality': self.resolution_quality,
            'mitigation_applied': self.mitigation_applied,
            'mitigation_effectiveness': self.mitigation_effectiveness,
            'was_cascade': self.was_cascade,
            'parent_event_id': self.parent_event_id,
            'cascade_events': self.cascade_events,
            'processing_time_ms': self.processing_time_ms
        }
    
    @classmethod
    def from_chaos_event(cls, chaos_event: ChaosEvent) -> 'EventRecord':
        """Create an EventRecord from a ChaosEvent"""
        return cls(
            event_id=chaos_event.event_id,
            event_type=chaos_event.event_type.value,
            severity=chaos_event.severity.value,
            title=chaos_event.title,
            description=chaos_event.description,
            created_at=chaos_event.created_at,
            triggered_at=chaos_event.triggered_at,
            duration_hours=chaos_event.duration_hours,
            chaos_score_at_trigger=chaos_event.chaos_score_at_trigger,
            pressure_sources_at_trigger=chaos_event.pressure_sources_at_trigger,
            affected_regions=[str(r) for r in chaos_event.affected_regions],
            global_event=chaos_event.global_event,
            immediate_effects_count=len(chaos_event.immediate_effects),
            ongoing_effects_count=len(chaos_event.ongoing_effects)
        )


@dataclass 
class AnalyticsSnapshot:
    """Point-in-time analytics snapshot"""
    timestamp: datetime
    chaos_score: float
    chaos_level: str
    active_events: int
    pressure_breakdown: Dict[str, float]
    regional_breakdown: Dict[str, float]
    system_health: float
    pressure_stability: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'timestamp': self.timestamp.isoformat(),
            'chaos_score': self.chaos_score,
            'chaos_level': self.chaos_level,
            'active_events': self.active_events,
            'pressure_breakdown': self.pressure_breakdown,
            'regional_breakdown': self.regional_breakdown,
            'system_health': self.system_health,
            'pressure_stability': self.pressure_stability
        }


class EventTracker:
    """
    Comprehensive tracking and analysis of chaos events and system behavior
    """
    
    def __init__(self, config: ChaosConfig):
        self.config = config
        
        # Event tracking storage
        self.event_records: List[EventRecord] = []
        self.active_event_records: Dict[str, EventRecord] = {}
        
        # Analytics snapshots (time series data)
        self.analytics_snapshots = deque(maxlen=10000)  # Keep last 10k snapshots
        
        # Pattern analysis data
        self.event_patterns: Dict[str, Any] = {}
        self.correlation_matrix: Dict[str, Dict[str, float]] = {}
        self.temporal_trends: Dict[str, List[float]] = defaultdict(list)
        
        # Performance tracking
        self.performance_metrics = {
            'events_tracked': 0,
            'snapshots_taken': 0,
            'analysis_runs': 0,
            'pattern_detections': 0,
            'total_processing_time_ms': 0.0,
            'average_processing_time_ms': 0.0
        }
        
        # Persistence settings
        self.persistence_enabled = config.enable_analytics_persistence
        self.analytics_dir = Path(config.analytics_output_dir) if hasattr(config, 'analytics_output_dir') else Path("analytics")
        self.analytics_dir.mkdir(exist_ok=True)
        
        # Tracking flags
        self.is_initialized = False
        self.auto_save_interval = 300  # 5 minutes
        self.last_auto_save = datetime.now()
        
        logger.info("Event Tracker initialized")
    
    async def initialize(self) -> None:
        """Initialize the event tracker"""
        try:
            # Load existing data if persistence is enabled
            if self.persistence_enabled:
                await self._load_persistent_data()
            
            self.is_initialized = True
            logger.info("Event Tracker initialization complete")
            
        except Exception as e:
            logger.error(f"Failed to initialize Event Tracker: {e}")
            raise
    
    def track_event_created(self, chaos_event: ChaosEvent) -> None:
        """Track when a new chaos event is created"""
        try:
            start_time = datetime.now()
            
            # Create event record
            record = EventRecord.from_chaos_event(chaos_event)
            self.active_event_records[chaos_event.event_id] = record
            
            # Track processing time
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            record.processing_time_ms = processing_time
            
            self.performance_metrics['events_tracked'] += 1
            self._update_performance_metrics(processing_time)
            
            logger.debug(f"Tracking new event: {chaos_event.event_type.value}")
            
        except Exception as e:
            logger.error(f"Error tracking event creation: {e}")
    
    def track_event_triggered(self, chaos_event: ChaosEvent, 
                            chaos_state: ChaosState, pressure_data: PressureData) -> None:
        """Track when an event is triggered with context"""
        try:
            record = self.active_event_records.get(chaos_event.event_id)
            if not record:
                # Create record if it doesn't exist
                record = EventRecord.from_chaos_event(chaos_event)
                self.active_event_records[chaos_event.event_id] = record
            
            # Update with trigger context
            record.triggered_at = chaos_event.triggered_at
            record.regional_chaos_scores = chaos_state.regional_chaos_scores.copy()
            
            # Check if this is a cascade event
            record.was_cascade = hasattr(chaos_event, 'parent_event_id')
            if record.was_cascade:
                record.parent_event_id = getattr(chaos_event, 'parent_event_id', None)
            
            logger.debug(f"Tracking event trigger: {chaos_event.event_type.value}")
            
        except Exception as e:
            logger.error(f"Error tracking event trigger: {e}")
    
    def track_event_resolved(self, event_id: str, resolution_type: str = "auto",
                           resolution_quality: float = 1.0, mitigation_applied: bool = False,
                           mitigation_effectiveness: float = 0.0) -> None:
        """Track when an event is resolved"""
        try:
            record = self.active_event_records.get(event_id)
            if not record:
                logger.warning(f"Attempted to resolve untracked event: {event_id}")
                return
            
            # Update resolution information
            record.resolved_at = datetime.now()
            record.resolution_type = resolution_type
            record.resolution_quality = resolution_quality
            record.mitigation_applied = mitigation_applied
            record.mitigation_effectiveness = mitigation_effectiveness
            
            # Calculate actual duration
            if record.triggered_at:
                actual_duration = (record.resolved_at - record.triggered_at).total_seconds() / 3600.0
                record.actual_duration_hours = actual_duration
            
            # Move to completed records
            self.event_records.append(record)
            del self.active_event_records[event_id]
            
            logger.debug(f"Tracked event resolution: {event_id} ({resolution_type})")
            
        except Exception as e:
            logger.error(f"Error tracking event resolution: {e}")
    
    def track_cascade_event(self, parent_event_id: str, cascade_event_id: str) -> None:
        """Track cascade relationship between events"""
        try:
            # Update parent event record
            parent_record = self.active_event_records.get(parent_event_id)
            if parent_record:
                parent_record.cascade_events.append(cascade_event_id)
            
            # Mark cascade event
            cascade_record = self.active_event_records.get(cascade_event_id)
            if cascade_record:
                cascade_record.was_cascade = True
                cascade_record.parent_event_id = parent_event_id
            
            logger.debug(f"Tracked cascade: {parent_event_id} -> {cascade_event_id}")
            
        except Exception as e:
            logger.error(f"Error tracking cascade: {e}")
    
    def take_analytics_snapshot(self, chaos_state: ChaosState, pressure_data: PressureData) -> None:
        """Take a point-in-time analytics snapshot"""
        try:
            snapshot = AnalyticsSnapshot(
                timestamp=datetime.now(),
                chaos_score=chaos_state.current_chaos_score,
                chaos_level=chaos_state.current_chaos_level.value,
                active_events=len(self.active_event_records),
                pressure_breakdown=pressure_data.global_pressure.get_pressure_breakdown(),
                regional_breakdown={
                    str(region_id): pressure.get_overall_pressure()
                    for region_id, pressure in pressure_data.regional_pressures.items()
                },
                system_health=chaos_state.system_health,
                pressure_stability=chaos_state.pressure_stability
            )
            
            self.analytics_snapshots.append(snapshot)
            self.performance_metrics['snapshots_taken'] += 1
            
            # Auto-save if interval has passed
            if self._should_auto_save():
                asyncio.create_task(self._auto_save_data())
            
        except Exception as e:
            logger.error(f"Error taking analytics snapshot: {e}")
    
    def analyze_event_patterns(self) -> Dict[str, Any]:
        """Analyze patterns in event data"""
        try:
            start_time = datetime.now()
            
            if len(self.event_records) < 10:
                return {"message": "Insufficient data for pattern analysis"}
            
            analysis = {
                'event_frequency': self._analyze_event_frequency(),
                'severity_distribution': self._analyze_severity_distribution(),
                'duration_patterns': self._analyze_duration_patterns(),
                'cascade_patterns': self._analyze_cascade_patterns(),
                'pressure_correlations': self._analyze_pressure_correlations(),
                'temporal_trends': self._analyze_temporal_trends(),
                'regional_patterns': self._analyze_regional_patterns(),
                'mitigation_effectiveness': self._analyze_mitigation_effectiveness()
            }
            
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            self.performance_metrics['analysis_runs'] += 1
            self.performance_metrics['pattern_detections'] += len(analysis)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing event patterns: {e}")
            return {"error": str(e)}
    
    def _analyze_event_frequency(self) -> Dict[str, Any]:
        """Analyze event frequency patterns"""
        frequency_data = defaultdict(int)
        hourly_distribution = defaultdict(int)
        daily_distribution = defaultdict(int)
        
        for record in self.event_records[-1000:]:  # Last 1000 events
            frequency_data[record.event_type] += 1
            
            if record.triggered_at:
                hour = record.triggered_at.hour
                day = record.triggered_at.weekday()
                hourly_distribution[hour] += 1
                daily_distribution[day] += 1
        
        return {
            'by_type': dict(frequency_data),
            'by_hour': dict(hourly_distribution),
            'by_day': dict(daily_distribution),
            'total_events': len(self.event_records)
        }
    
    def _analyze_severity_distribution(self) -> Dict[str, Any]:
        """Analyze severity distribution patterns"""
        severity_counts = defaultdict(int)
        severity_by_type = defaultdict(lambda: defaultdict(int))
        
        for record in self.event_records:
            severity_counts[record.severity] += 1
            severity_by_type[record.event_type][record.severity] += 1
        
        return {
            'overall_distribution': dict(severity_counts),
            'by_event_type': {k: dict(v) for k, v in severity_by_type.items()}
        }
    
    def _analyze_duration_patterns(self) -> Dict[str, Any]:
        """Analyze event duration patterns"""
        durations_by_type = defaultdict(list)
        durations_by_severity = defaultdict(list)
        
        for record in self.event_records:
            if record.actual_duration_hours > 0:
                durations_by_type[record.event_type].append(record.actual_duration_hours)
                durations_by_severity[record.severity].append(record.actual_duration_hours)
        
        def calculate_stats(durations):
            if not durations:
                return {'avg': 0, 'min': 0, 'max': 0, 'count': 0}
            return {
                'avg': sum(durations) / len(durations),
                'min': min(durations),
                'max': max(durations),
                'count': len(durations)
            }
        
        return {
            'by_type': {k: calculate_stats(v) for k, v in durations_by_type.items()},
            'by_severity': {k: calculate_stats(v) for k, v in durations_by_severity.items()}
        }
    
    def _analyze_cascade_patterns(self) -> Dict[str, Any]:
        """Analyze cascade event patterns"""
        cascade_triggers = defaultdict(int)
        cascade_chains = []
        
        for record in self.event_records:
            if record.cascade_events:
                cascade_triggers[record.event_type] += len(record.cascade_events)
                cascade_chains.append({
                    'parent': record.event_type,
                    'cascades': len(record.cascade_events),
                    'chaos_score': record.chaos_score_at_trigger
                })
        
        cascade_rate = len([r for r in self.event_records if r.was_cascade]) / max(1, len(self.event_records))
        
        return {
            'cascade_triggers': dict(cascade_triggers),
            'cascade_rate': cascade_rate,
            'cascade_chains': cascade_chains[-50:]  # Last 50 chains
        }
    
    def _analyze_pressure_correlations(self) -> Dict[str, Any]:
        """Analyze correlations between pressure sources and events"""
        correlations = defaultdict(lambda: defaultdict(list))
        
        for record in self.event_records:
            for source, pressure in record.pressure_sources_at_trigger.items():
                correlations[record.event_type][source].append(pressure)
        
        # Calculate average correlations
        avg_correlations = {}
        for event_type, sources in correlations.items():
            avg_correlations[event_type] = {
                source: sum(pressures) / len(pressures)
                for source, pressures in sources.items()
                if pressures
            }
        
        return avg_correlations
    
    def _analyze_temporal_trends(self) -> Dict[str, Any]:
        """Analyze temporal trends in chaos system"""
        if len(self.analytics_snapshots) < 10:
            return {"message": "Insufficient snapshots for trend analysis"}
        
        # Convert snapshots to time series
        snapshots = list(self.analytics_snapshots)[-100:]  # Last 100 snapshots
        
        chaos_scores = [s.chaos_score for s in snapshots]
        active_events = [s.active_events for s in snapshots]
        system_health = [s.system_health for s in snapshots]
        
        def calculate_trend(values):
            if len(values) < 2:
                return 0.0
            # Simple linear trend calculation
            n = len(values)
            x = list(range(n))
            x_mean = sum(x) / n
            y_mean = sum(values) / n
            
            numerator = sum((x[i] - x_mean) * (values[i] - y_mean) for i in range(n))
            denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
            
            return numerator / denominator if denominator != 0 else 0.0
        
        return {
            'chaos_score_trend': calculate_trend(chaos_scores),
            'active_events_trend': calculate_trend(active_events),
            'system_health_trend': calculate_trend(system_health),
            'snapshot_count': len(snapshots),
            'time_span_hours': (snapshots[-1].timestamp - snapshots[0].timestamp).total_seconds() / 3600.0
        }
    
    def _analyze_regional_patterns(self) -> Dict[str, Any]:
        """Analyze regional event distribution patterns"""
        regional_events = defaultdict(int)
        regional_severity = defaultdict(lambda: defaultdict(int))
        
        for record in self.event_records:
            if record.global_event:
                regional_events['global'] += 1
                regional_severity['global'][record.severity] += 1
            else:
                for region in record.affected_regions:
                    regional_events[region] += 1
                    regional_severity[region][record.severity] += 1
        
        return {
            'event_distribution': dict(regional_events),
            'severity_by_region': {k: dict(v) for k, v in regional_severity.items()}
        }
    
    def _analyze_mitigation_effectiveness(self) -> Dict[str, Any]:
        """Analyze mitigation effectiveness patterns"""
        mitigated_events = [r for r in self.event_records if r.mitigation_applied]
        unmitigated_events = [r for r in self.event_records if not r.mitigation_applied]
        
        if not mitigated_events:
            return {"message": "No mitigated events to analyze"}
        
        avg_mitigation_effectiveness = sum(r.mitigation_effectiveness for r in mitigated_events) / len(mitigated_events)
        avg_mitigated_duration = sum(r.actual_duration_hours for r in mitigated_events if r.actual_duration_hours > 0) / max(1, len(mitigated_events))
        avg_unmitigated_duration = sum(r.actual_duration_hours for r in unmitigated_events if r.actual_duration_hours > 0) / max(1, len(unmitigated_events))
        
        return {
            'mitigation_rate': len(mitigated_events) / len(self.event_records),
            'average_effectiveness': avg_mitigation_effectiveness,
            'mitigated_duration': avg_mitigated_duration,
            'unmitigated_duration': avg_unmitigated_duration,
            'duration_reduction': max(0, avg_unmitigated_duration - avg_mitigated_duration)
        }
    
    def get_event_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get summary of events in the last N hours"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_events = [
            r for r in self.event_records 
            if r.triggered_at and r.triggered_at >= cutoff_time
        ]
        
        if not recent_events:
            return {"message": f"No events in the last {hours} hours"}
        
        event_types = defaultdict(int)
        severities = defaultdict(int)
        regions = defaultdict(int)
        
        for event in recent_events:
            event_types[event.event_type] += 1
            severities[event.severity] += 1
            for region in event.affected_regions:
                regions[region] += 1
        
        return {
            'time_period_hours': hours,
            'total_events': len(recent_events),
            'by_type': dict(event_types),
            'by_severity': dict(severities),
            'by_region': dict(regions),
            'active_events': len(self.active_event_records)
        }
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for the tracker"""
        return {
            **self.performance_metrics,
            'total_records': len(self.event_records),
            'active_records': len(self.active_event_records),
            'snapshots_stored': len(self.analytics_snapshots),
            'memory_usage_mb': self._estimate_memory_usage(),
            'is_initialized': self.is_initialized
        }
    
    def _estimate_memory_usage(self) -> float:
        """Estimate memory usage in MB"""
        import sys
        
        total_size = 0
        total_size += sys.getsizeof(self.event_records)
        total_size += sys.getsizeof(self.active_event_records)
        total_size += sys.getsizeof(self.analytics_snapshots)
        
        return total_size / (1024 * 1024)  # Convert to MB
    
    def _update_performance_metrics(self, processing_time_ms: float) -> None:
        """Update performance metrics"""
        self.performance_metrics['total_processing_time_ms'] += processing_time_ms
        if self.performance_metrics['events_tracked'] > 0:
            self.performance_metrics['average_processing_time_ms'] = (
                self.performance_metrics['total_processing_time_ms'] / 
                self.performance_metrics['events_tracked']
            )
    
    def _should_auto_save(self) -> bool:
        """Check if auto-save should be performed"""
        return (
            self.persistence_enabled and
            (datetime.now() - self.last_auto_save).total_seconds() >= self.auto_save_interval
        )
    
    async def _auto_save_data(self) -> None:
        """Automatically save data to persistence"""
        try:
            await self.save_analytics_data()
            self.last_auto_save = datetime.now()
        except Exception as e:
            logger.error(f"Auto-save failed: {e}")
    
    async def save_analytics_data(self) -> None:
        """Save analytics data to files"""
        if not self.persistence_enabled:
            return
        
        try:
            # Save event records
            events_file = self.analytics_dir / "event_records.json"
            with open(events_file, 'w') as f:
                json.dump([record.to_dict() for record in self.event_records[-1000:]], f, indent=2)
            
            # Save analytics snapshots
            snapshots_file = self.analytics_dir / "analytics_snapshots.json"
            with open(snapshots_file, 'w') as f:
                json.dump([snapshot.to_dict() for snapshot in list(self.analytics_snapshots)[-1000:]], f, indent=2)
            
            # Save performance metrics
            metrics_file = self.analytics_dir / "performance_metrics.json"
            with open(metrics_file, 'w') as f:
                json.dump(self.get_performance_metrics(), f, indent=2)
            
            logger.debug("Analytics data saved successfully")
            
        except Exception as e:
            logger.error(f"Failed to save analytics data: {e}")
    
    async def _load_persistent_data(self) -> None:
        """Load analytics data from files"""
        try:
            # Load event records
            events_file = self.analytics_dir / "event_records.json"
            if events_file.exists():
                with open(events_file, 'r') as f:
                    event_data = json.load(f)
                    # Convert back to EventRecord objects (simplified for now)
                    logger.info(f"Loaded {len(event_data)} event records")
            
            # Load analytics snapshots
            snapshots_file = self.analytics_dir / "analytics_snapshots.json"
            if snapshots_file.exists():
                with open(snapshots_file, 'r') as f:
                    snapshot_data = json.load(f)
                    logger.info(f"Loaded {len(snapshot_data)} analytics snapshots")
            
        except Exception as e:
            logger.error(f"Failed to load persistent data: {e}")
    
    async def cleanup_old_data(self, max_age_days: int = 30) -> None:
        """Clean up old tracking data"""
        try:
            cutoff_date = datetime.now() - timedelta(days=max_age_days)
            
            # Remove old event records
            initial_count = len(self.event_records)
            self.event_records = [
                record for record in self.event_records
                if record.created_at >= cutoff_date
            ]
            
            removed_count = initial_count - len(self.event_records)
            if removed_count > 0:
                logger.info(f"Cleaned up {removed_count} old event records")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}") 
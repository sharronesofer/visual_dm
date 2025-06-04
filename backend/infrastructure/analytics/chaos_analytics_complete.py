"""
Chaos Analytics Infrastructure - Complete System

Comprehensive analytics infrastructure for chaos system including event tracking,
configuration management, performance monitoring, and persistence.

This combines configuration_manager.py, event_tracker.py, and chaos_analytics.py
into a unified infrastructure component.
"""

import asyncio
import json
import os
from collections import defaultdict, deque
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Callable, Tuple
from pathlib import Path
from enum import Enum
from threading import Lock

# Infrastructure imports only - no business logic
from backend.infrastructure.config.chaos_config_loader import ConfigurationLoader

class ConfigurationType(Enum):
    """Types of configuration parameters"""
    PRESSURE_WEIGHTS = "pressure_weights"
    CHAOS_THRESHOLDS = "chaos_thresholds"
    EVENT_PROBABILITIES = "event_probabilities"
    MITIGATION_EFFECTIVENESS = "mitigation_effectiveness"
    TEMPORAL_FACTORS = "temporal_factors"
    PERFORMANCE_SETTINGS = "performance_settings"
    MONITORING_SETTINGS = "monitoring_settings"
    INTEGRATION_SETTINGS = "integration_settings"

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
class ConfigurationChange:
    """Record of a configuration change"""
    timestamp: datetime
    change_id: str
    configuration_type: str
    parameter_name: str
    old_value: Any
    new_value: Any
    changed_by: str = "system"
    reason: str = ""
    validation_passed: bool = True
    applied_successfully: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'timestamp': self.timestamp.isoformat(),
            'change_id': self.change_id,
            'configuration_type': self.configuration_type,
            'parameter_name': self.parameter_name,
            'old_value': self.old_value,
            'new_value': self.new_value,
            'changed_by': self.changed_by,
            'reason': self.reason,
            'validation_passed': self.validation_passed,
            'applied_successfully': self.applied_successfully
        }

@dataclass
class ConfigurationValidation:
    """Validation rules for configuration parameters"""
    parameter_name: str
    value_type: type
    min_value: Optional[Union[int, float]] = None
    max_value: Optional[Union[int, float]] = None
    allowed_values: Optional[List[Any]] = None
    custom_validator: Optional[Callable[[Any], bool]] = None
    description: str = ""
    
    def validate(self, value: Any) -> Tuple[bool, str]:
        """Validate a configuration value"""
        try:
            if not isinstance(value, self.value_type):
                return False, f"Expected {self.value_type.__name__}, got {type(value).__name__}"
            
            if self.min_value is not None and value < self.min_value:
                return False, f"Value {value} is below minimum {self.min_value}"
            
            if self.max_value is not None and value > self.max_value:
                return False, f"Value {value} is above maximum {self.max_value}"
            
            if self.allowed_values is not None and value not in self.allowed_values:
                return False, f"Value {value} not in allowed values: {self.allowed_values}"
            
            if self.custom_validator and not self.custom_validator(value):
                return False, "Custom validation failed"
            
            return True, "Valid"
            
        except Exception as e:
            return False, f"Validation error: {str(e)}"

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
    resolution_type: str = "auto"
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

class ChaosAnalyticsInfrastructure:
    """
    Complete analytics infrastructure for chaos system.
    
    Handles configuration management, event tracking, persistence,
    performance monitoring, and all technical aspects of analytics.
    """
    
    def __init__(self, config_data: Dict[str, Any]):
        # Core configuration
        self.config_data = config_data
        
        # Configuration management infrastructure
        self.current_configuration: Dict[str, Any] = {}
        self.configuration_history: List[ConfigurationChange] = []
        self.validation_rules: Dict[str, ConfigurationValidation] = {}
        self.pending_changes: Dict[str, Any] = {}
        self.change_listeners: Dict[str, List[Callable]] = {}
        self.config_lock = Lock()
        
        # Event tracking infrastructure
        self.event_records: List[EventRecord] = []
        self.active_event_records: Dict[str, EventRecord] = {}
        self.analytics_snapshots = deque(maxlen=10000)
        self.event_patterns: Dict[str, Any] = {}
        self.correlation_matrix: Dict[str, Dict[str, float]] = {}
        self.temporal_trends: Dict[str, List[float]] = defaultdict(list)
        
        # Persistence infrastructure
        self.config_dir = Path("data/infrastructure/analytics")
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.config_file = self.config_dir / "dynamic_config.json"
        self.backup_dir = self.config_dir / "backups"
        self.backup_dir.mkdir(exist_ok=True)
        self.analytics_dir = Path("data/infrastructure/analytics/events")
        self.analytics_dir.mkdir(exist_ok=True)
        
        # Performance tracking
        self.configuration_metrics = {
            'changes_applied': 0,
            'changes_rejected': 0,
            'validations_performed': 0,
            'rollbacks_performed': 0,
            'auto_optimizations': 0
        }
        
        self.performance_metrics = {
            'events_tracked': 0,
            'snapshots_taken': 0,
            'analysis_runs': 0,
            'pattern_detections': 0,
            'total_processing_time_ms': 0.0,
            'average_processing_time_ms': 0.0
        }
        
        # System state
        self.auto_apply_enabled = True
        self.validation_enabled = True
        self.persistence_enabled = True
        self.auto_save_interval = 300  # 5 minutes
        self.last_auto_save = datetime.now()
        self.is_initialized = False
        
    async def initialize(self) -> None:
        """Initialize all analytics infrastructure"""
        try:
            # Set up validation rules
            self._setup_validation_rules()
            
            # Load persistent configuration
            await self._load_configuration()
            
            # Initialize from provided config data
            self._initialize_from_config_data()
            
            # Load existing analytics data
            if self.persistence_enabled:
                await self._load_persistent_data()
            
            self.is_initialized = True
            
        except Exception as e:
            # Handle initialization error gracefully
            self.is_initialized = False
            raise
    
    def _setup_validation_rules(self) -> None:
        """Set up validation rules for all configuration parameters"""
        # Pressure weight validations
        self.validation_rules.update({
            'pressure_weights.faction_stability': ConfigurationValidation(
                'pressure_weights.faction_stability', float, 0.0, 2.0,
                description="Weight for faction stability pressure"
            ),
            'pressure_weights.economic_health': ConfigurationValidation(
                'pressure_weights.economic_health', float, 0.0, 2.0,
                description="Weight for economic health pressure"
            ),
            'pressure_weights.diplomatic_tension': ConfigurationValidation(
                'pressure_weights.diplomatic_tension', float, 0.0, 2.0,
                description="Weight for diplomatic tension pressure"
            ),
            'pressure_weights.regional_stability': ConfigurationValidation(
                'pressure_weights.regional_stability', float, 0.0, 2.0,
                description="Weight for regional stability pressure"
            ),
            'pressure_weights.population_morale': ConfigurationValidation(
                'pressure_weights.population_morale', float, 0.0, 2.0,
                description="Weight for population morale pressure"
            ),
            'pressure_weights.npc_stress': ConfigurationValidation(
                'pressure_weights.npc_stress', float, 0.0, 2.0,
                description="Weight for NPC stress pressure"
            )
        })
        
        # Chaos threshold validations
        self.validation_rules.update({
            'chaos_thresholds.dormant_max': ConfigurationValidation(
                'chaos_thresholds.dormant_max', float, 0.0, 1.0,
                description="Maximum chaos score for dormant level"
            ),
            'chaos_thresholds.low_max': ConfigurationValidation(
                'chaos_thresholds.low_max', float, 0.0, 1.0,
                description="Maximum chaos score for low level"
            ),
            'chaos_thresholds.moderate_max': ConfigurationValidation(
                'chaos_thresholds.moderate_max', float, 0.0, 1.0,
                description="Maximum chaos score for moderate level"
            ),
            'chaos_thresholds.high_max': ConfigurationValidation(
                'chaos_thresholds.high_max', float, 0.0, 1.0,
                description="Maximum chaos score for high level"
            )
        })
    
    def _initialize_from_config_data(self) -> None:
        """Initialize configuration from provided config data"""
        with self.config_lock:
            # Copy config data to current configuration
            self.current_configuration.update(self.config_data)
    
    # Configuration Management Methods
    
    def get_configuration(self, path: Optional[str] = None) -> Any:
        """Get configuration value by path"""
        with self.config_lock:
            if path is None:
                return self.current_configuration.copy()
            
            # Navigate nested dictionary using dot notation
            keys = path.split('.')
            value = self.current_configuration
            
            try:
                for key in keys:
                    value = value[key]
                return value
            except (KeyError, TypeError):
                return None
    
    async def set_configuration(self, path: str, value: Any, changed_by: str = "system",
                              reason: str = "", validate: bool = True) -> bool:
        """Set configuration value with validation and change tracking"""
        try:
            # Validate change if enabled
            if validate and self.validation_enabled:
                is_valid, error_msg = self._validate_configuration_change(path, value)
                if not is_valid:
                    return False
            
            # Get old value for change tracking
            old_value = self.get_configuration(path)
            
            # Apply the change
            success = await self._apply_configuration_change(path, value)
            
            if success:
                # Record the change
                change = ConfigurationChange(
                    timestamp=datetime.now(),
                    change_id=f"{path}_{datetime.now().timestamp()}",
                    configuration_type=self._get_configuration_type(path),
                    parameter_name=path,
                    old_value=old_value,
                    new_value=value,
                    changed_by=changed_by,
                    reason=reason,
                    validation_passed=True,
                    applied_successfully=True
                )
                
                self.configuration_history.append(change)
                self.configuration_metrics['changes_applied'] += 1
                
                # Notify change listeners
                await self._notify_change_listeners(path, value, old_value)
                
                # Auto-save if enabled
                if self.persistence_enabled:
                    await self._save_configuration()
                
                return True
            else:
                self.configuration_metrics['changes_rejected'] += 1
                return False
                
        except Exception as e:
            self.configuration_metrics['changes_rejected'] += 1
            return False
    
    def _get_configuration_type(self, path: str) -> str:
        """Determine configuration type from path"""
        if path.startswith('pressure_weights'):
            return ConfigurationType.PRESSURE_WEIGHTS.value
        elif path.startswith('chaos_thresholds'):
            return ConfigurationType.CHAOS_THRESHOLDS.value
        elif path.startswith('event_probabilities'):
            return ConfigurationType.EVENT_PROBABILITIES.value
        elif path.startswith('mitigation'):
            return ConfigurationType.MITIGATION_EFFECTIVENESS.value
        elif path.startswith('performance'):
            return ConfigurationType.PERFORMANCE_SETTINGS.value
        else:
            return "unknown"
    
    def _validate_configuration_change(self, path: str, value: Any) -> Tuple[bool, str]:
        """Validate a configuration change"""
        self.configuration_metrics['validations_performed'] += 1
        
        # Check if we have validation rules for this path
        if path in self.validation_rules:
            return self.validation_rules[path].validate(value)
        
        # Basic validation for unknown paths
        if value is None:
            return False, "Value cannot be None"
        
        return True, "Valid"
    
    async def _apply_configuration_change(self, path: str, value: Any) -> bool:
        """Apply a configuration change"""
        try:
            with self.config_lock:
                self._set_nested_value(self.current_configuration, path, value)
            return True
        except Exception:
            return False
    
    def _set_nested_value(self, config_dict: Dict[str, Any], path: str, value: Any) -> None:
        """Set a nested value in configuration dictionary"""
        keys = path.split('.')
        current = config_dict
        
        # Navigate to parent of target key
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        # Set the value
        current[keys[-1]] = value
    
    def register_change_listener(self, path_pattern: str, callback: Callable) -> None:
        """Register a callback for configuration changes"""
        if path_pattern not in self.change_listeners:
            self.change_listeners[path_pattern] = []
        self.change_listeners[path_pattern].append(callback)
    
    async def _notify_change_listeners(self, path: str, new_value: Any, old_value: Any) -> None:
        """Notify registered change listeners"""
        for pattern, callbacks in self.change_listeners.items():
            if path.startswith(pattern):
                for callback in callbacks:
                    try:
                        # Call the listener
                        if asyncio.iscoroutinefunction(callback):
                            await callback(path, new_value, old_value)
                        else:
                            callback(path, new_value, old_value)
                    except Exception:
                        # Continue with other listeners even if one fails
                        continue
    
    # Event Tracking Methods
    
    def track_event_created(self, event_data: Dict[str, Any]) -> None:
        """Track when an event is created"""
        try:
            record = EventRecord(
                event_id=event_data.get('event_id', ''),
                event_type=event_data.get('event_type', ''),
                severity=event_data.get('severity', ''),
                title=event_data.get('title', ''),
                description=event_data.get('description', ''),
                created_at=datetime.now()
            )
            
            self.active_event_records[record.event_id] = record
            self.performance_metrics['events_tracked'] += 1
            
        except Exception:
            pass
    
    def track_event_triggered(self, event_data: Dict[str, Any], 
                            chaos_state: Dict[str, Any], pressure_data: Dict[str, Any]) -> None:
        """Track when an event is triggered"""
        try:
            event_id = event_data.get('event_id', '')
            if event_id in self.active_event_records:
                record = self.active_event_records[event_id]
                record.triggered_at = datetime.now()
                record.chaos_score_at_trigger = chaos_state.get('global_chaos_score', 0.0)
                record.pressure_sources_at_trigger = pressure_data.get('pressure_sources', {})
                record.regional_chaos_scores = chaos_state.get('regional_scores', {})
                record.affected_regions = event_data.get('affected_regions', [])
                record.global_event = event_data.get('global_event', False)
                
        except Exception:
            pass
    
    def track_event_resolved(self, event_id: str, resolution_type: str = "auto",
                           resolution_quality: float = 1.0, mitigation_applied: bool = False,
                           mitigation_effectiveness: float = 0.0) -> None:
        """Track when an event is resolved"""
        try:
            if event_id in self.active_event_records:
                record = self.active_event_records[event_id]
                record.resolved_at = datetime.now()
                record.resolution_type = resolution_type
                record.resolution_quality = resolution_quality
                record.mitigation_applied = mitigation_applied
                record.mitigation_effectiveness = mitigation_effectiveness
                
                # Calculate actual duration
                if record.triggered_at and record.resolved_at:
                    record.actual_duration_hours = (record.resolved_at - record.triggered_at).total_seconds() / 3600.0
                
                # Move to historical records
                self.event_records.append(record)
                del self.active_event_records[event_id]
                
        except Exception:
            pass
    
    def take_analytics_snapshot(self, chaos_state: Dict[str, Any], pressure_data: Dict[str, Any]) -> None:
        """Take a snapshot of current system state"""
        try:
            snapshot = AnalyticsSnapshot(
                timestamp=datetime.now(),
                chaos_score=chaos_state.get('global_chaos_score', 0.0),
                chaos_level=chaos_state.get('global_chaos_level', 'stable'),
                active_events=len(self.active_event_records),
                pressure_breakdown=pressure_data.get('pressure_sources', {}),
                regional_breakdown=chaos_state.get('regional_scores', {}),
                system_health=chaos_state.get('system_health', 1.0),
                pressure_stability=pressure_data.get('stability_score', 1.0)
            )
            
            self.analytics_snapshots.append(snapshot)
            self.performance_metrics['snapshots_taken'] += 1
            
        except Exception:
            pass
    
    # Persistence Methods
    
    async def _save_configuration(self) -> None:
        """Save current configuration to file"""
        try:
            if not self.persistence_enabled:
                return
            
            save_data = {
                'configuration': self.current_configuration,
                'metadata': {
                    'last_saved': datetime.now().isoformat(),
                    'total_changes': len(self.configuration_history),
                    'version': '1.0'
                }
            }
            
            with open(self.config_file, 'w') as f:
                json.dump(save_data, f, indent=2, default=str)
                
        except Exception:
            pass
    
    async def _load_configuration(self) -> None:
        """Load configuration from file"""
        try:
            if not self.persistence_enabled or not self.config_file.exists():
                return
            
            with open(self.config_file, 'r') as f:
                save_data = json.load(f)
            
            if 'configuration' in save_data:
                with self.config_lock:
                    self.current_configuration.update(save_data['configuration'])
                    
        except Exception:
            pass
    
    async def save_analytics_data(self) -> None:
        """Save analytics data to files"""
        try:
            if not self.persistence_enabled:
                return
            
            # Save event records
            events_file = self.analytics_dir / f"events_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            events_data = {
                'events': [record.to_dict() for record in self.event_records],
                'metadata': {
                    'total_events': len(self.event_records),
                    'saved_at': datetime.now().isoformat()
                }
            }
            
            with open(events_file, 'w') as f:
                json.dump(events_data, f, indent=2, default=str)
            
            # Save snapshots
            snapshots_file = self.analytics_dir / f"snapshots_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            snapshots_data = {
                'snapshots': [snapshot.to_dict() for snapshot in list(self.analytics_snapshots)],
                'metadata': {
                    'total_snapshots': len(self.analytics_snapshots),
                    'saved_at': datetime.now().isoformat()
                }
            }
            
            with open(snapshots_file, 'w') as f:
                json.dump(snapshots_data, f, indent=2, default=str)
                
            self.last_auto_save = datetime.now()
            
        except Exception:
            pass
    
    async def _load_persistent_data(self) -> None:
        """Load existing analytics data"""
        try:
            # Load most recent events file
            events_files = list(self.analytics_dir.glob("events_*.json"))
            if events_files:
                latest_events = max(events_files, key=lambda f: f.stat().st_mtime)
                
                with open(latest_events, 'r') as f:
                    events_data = json.load(f)
                
                for event_dict in events_data.get('events', []):
                    record = EventRecord(**event_dict)
                    self.event_records.append(record)
            
            # Load most recent snapshots file
            snapshot_files = list(self.analytics_dir.glob("snapshots_*.json"))
            if snapshot_files:
                latest_snapshots = max(snapshot_files, key=lambda f: f.stat().st_mtime)
                
                with open(latest_snapshots, 'r') as f:
                    snapshots_data = json.load(f)
                
                for snapshot_dict in snapshots_data.get('snapshots', []):
                    snapshot = AnalyticsSnapshot(**snapshot_dict)
                    self.analytics_snapshots.append(snapshot)
            
        except Exception:
            pass
    
    # Analysis Methods
    
    def analyze_event_patterns(self) -> Dict[str, Any]:
        """Analyze patterns in event data"""
        try:
            self.performance_metrics['analysis_runs'] += 1
            
            if not self.event_records:
                return {'error': 'No event data available'}
            
            analysis = {
                'event_frequency': self._analyze_event_frequency(),
                'severity_distribution': self._analyze_severity_distribution(),
                'duration_patterns': self._analyze_duration_patterns(),
                'cascade_patterns': self._analyze_cascade_patterns(),
                'regional_patterns': self._analyze_regional_patterns(),
                'temporal_trends': self._analyze_temporal_trends(),
                'analysis_timestamp': datetime.now().isoformat()
            }
            
            self.event_patterns = analysis
            return analysis
            
        except Exception:
            return {'error': 'Analysis failed'}
    
    def _analyze_event_frequency(self) -> Dict[str, Any]:
        """Analyze event frequency patterns"""
        try:
            # Count events by type
            type_counts = defaultdict(int)
            for record in self.event_records:
                type_counts[record.event_type] += 1
            
            # Calculate average time between events
            if len(self.event_records) > 1:
                sorted_events = sorted(self.event_records, key=lambda e: e.created_at)
                intervals = []
                for i in range(1, len(sorted_events)):
                    interval = (sorted_events[i].created_at - sorted_events[i-1].created_at).total_seconds() / 3600.0
                    intervals.append(interval)
                
                avg_interval = sum(intervals) / len(intervals) if intervals else 0
            else:
                avg_interval = 0
            
            return {
                'events_by_type': dict(type_counts),
                'total_events': len(self.event_records),
                'average_interval_hours': avg_interval,
                'most_common_type': max(type_counts.items(), key=lambda x: x[1])[0] if type_counts else None
            }
            
        except Exception:
            return {}
    
    def _analyze_severity_distribution(self) -> Dict[str, Any]:
        """Analyze severity distribution"""
        try:
            severity_counts = defaultdict(int)
            for record in self.event_records:
                severity_counts[record.severity] += 1
            
            total = len(self.event_records)
            severity_percentages = {
                severity: (count / total) * 100 if total > 0 else 0
                for severity, count in severity_counts.items()
            }
            
            return {
                'severity_counts': dict(severity_counts),
                'severity_percentages': severity_percentages,
                'total_events': total
            }
            
        except Exception:
            return {}
    
    def _analyze_duration_patterns(self) -> Dict[str, Any]:
        """Analyze event duration patterns"""
        try:
            durations = [record.actual_duration_hours for record in self.event_records 
                        if record.actual_duration_hours > 0]
            
            if not durations:
                return {'error': 'No duration data available'}
            
            avg_duration = sum(durations) / len(durations)
            min_duration = min(durations)
            max_duration = max(durations)
            
            return {
                'average_duration_hours': avg_duration,
                'min_duration_hours': min_duration,
                'max_duration_hours': max_duration,
                'total_events_with_duration': len(durations)
            }
            
        except Exception:
            return {}
    
    def _analyze_cascade_patterns(self) -> Dict[str, Any]:
        """Analyze cascade event patterns"""
        try:
            cascade_events = [record for record in self.event_records if record.was_cascade]
            total_cascades = len(cascade_events)
            
            # Find cascade chains
            cascade_chains = defaultdict(list)
            for record in cascade_events:
                if record.parent_event_id:
                    cascade_chains[record.parent_event_id].append(record.event_id)
            
            return {
                'total_cascade_events': total_cascades,
                'cascade_percentage': (total_cascades / len(self.event_records)) * 100 if self.event_records else 0,
                'cascade_chains': dict(cascade_chains),
                'longest_chain': max(len(chain) for chain in cascade_chains.values()) if cascade_chains else 0
            }
            
        except Exception:
            return {}
    
    def _analyze_regional_patterns(self) -> Dict[str, Any]:
        """Analyze regional event patterns"""
        try:
            regional_counts = defaultdict(int)
            for record in self.event_records:
                for region in record.affected_regions:
                    regional_counts[region] += 1
            
            return {
                'events_by_region': dict(regional_counts),
                'most_affected_region': max(regional_counts.items(), key=lambda x: x[1])[0] if regional_counts else None,
                'total_regional_events': sum(regional_counts.values())
            }
            
        except Exception:
            return {}
    
    def _analyze_temporal_trends(self) -> Dict[str, Any]:
        """Analyze temporal trends in events"""
        try:
            # Group events by time periods
            hourly_counts = defaultdict(int)
            daily_counts = defaultdict(int)
            
            for record in self.event_records:
                hour_key = record.created_at.strftime('%Y-%m-%d %H:00')
                day_key = record.created_at.strftime('%Y-%m-%d')
                
                hourly_counts[hour_key] += 1
                daily_counts[day_key] += 1
            
            return {
                'hourly_distribution': dict(hourly_counts),
                'daily_distribution': dict(daily_counts),
                'peak_hour': max(hourly_counts.items(), key=lambda x: x[1])[0] if hourly_counts else None,
                'peak_day': max(daily_counts.items(), key=lambda x: x[1])[0] if daily_counts else None
            }
            
        except Exception:
            return {}
    
    # Utility Methods
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        return {
            'initialized': self.is_initialized,
            'persistence_enabled': self.persistence_enabled,
            'configuration_metrics': self.configuration_metrics,
            'performance_metrics': self.performance_metrics,
            'active_events': len(self.active_event_records),
            'historical_events': len(self.event_records),
            'snapshots_count': len(self.analytics_snapshots),
            'change_listeners': len(self.change_listeners),
            'last_auto_save': self.last_auto_save.isoformat()
        }
    
    async def cleanup_old_data(self, max_age_days: int = 30) -> None:
        """Clean up old analytics data"""
        try:
            cutoff_date = datetime.now() - timedelta(days=max_age_days)
            
            # Clean up old event records
            self.event_records = [
                record for record in self.event_records 
                if record.created_at > cutoff_date
            ]
            
            # Clean up old snapshots
            filtered_snapshots = [
                snapshot for snapshot in self.analytics_snapshots
                if snapshot.timestamp > cutoff_date
            ]
            self.analytics_snapshots.clear()
            self.analytics_snapshots.extend(filtered_snapshots)
            
            # Clean up old configuration changes
            self.configuration_history = [
                change for change in self.configuration_history
                if change.timestamp > cutoff_date
            ]
            
        except Exception:
            pass

# Global instance factory
def create_analytics_infrastructure(config_data: Dict[str, Any]) -> ChaosAnalyticsInfrastructure:
    """Create and return analytics infrastructure instance"""
    return ChaosAnalyticsInfrastructure(config_data) 
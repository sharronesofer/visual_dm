"""
Chaos System Configuration

Central configuration for all chaos system parameters, thresholds, and behavioral settings.
Now includes full support for temporal pressure and narrative intelligence.
"""

import json
import os
from dataclasses import dataclass, field, fields, MISSING
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
from datetime import timedelta

@dataclass
class PressureConfig:
    """Configuration for pressure calculation and thresholds"""
    # Global pressure settings
    global_pressure_threshold: float = 0.75
    regional_pressure_threshold: float = 0.65
    pressure_decay_rate: float = 0.05
    pressure_escalation_rate: float = 0.08
    
    # Pressure source weights (including temporal)
    economic_weight: float = 1.0
    political_weight: float = 1.2
    social_weight: float = 0.9
    environmental_weight: float = 1.1
    diplomatic_weight: float = 0.8
    temporal_weight: float = 1.3  # Bible requirement: 6th pressure type
    
    # Pressure source decay rates
    economic_decay: float = 0.04
    political_decay: float = 0.06
    social_decay: float = 0.05
    environmental_decay: float = 0.03
    diplomatic_decay: float = 0.07
    temporal_decay: float = 0.02  # Slower decay for temporal anomalies
    
    # Cross-system amplification factors
    amplification_threshold: float = 0.6
    amplification_factor: float = 1.4
    
    # Temporal pressure specific settings
    temporal_pressure_enabled: bool = True
    temporal_anomaly_base_pressure: float = 0.3
    temporal_cascade_multiplier: float = 1.8
    temporal_detection_threshold: float = 0.2

@dataclass
class EventConfig:
    """Configuration for chaos event generation and processing"""
    # Event thresholds
    minor_event_threshold: float = 0.4
    moderate_event_threshold: float = 0.6
    major_event_threshold: float = 0.8
    critical_event_threshold: float = 0.9
    
    # Event frequency controls
    base_event_frequency_hours: float = 12.0
    max_events_per_day: int = 6
    min_event_spacing_hours: float = 2.0
    
    # Event severity distribution
    minor_event_probability: float = 0.5
    moderate_event_probability: float = 0.3
    major_event_probability: float = 0.15
    critical_event_probability: float = 0.05
    
    # Fatigue management (Bible requirement)
    enable_event_fatigue: bool = True
    global_fatigue_threshold: float = 0.7
    regional_fatigue_threshold: float = 0.6
    fatigue_decay_rate: float = 0.1
    fatigue_prevention_factor: float = 0.3
    
    # Cascading effects (Bible requirement)
    enable_cascading: bool = True
    cascade_probability_base: float = 0.3
    cascade_delay_min_hours: float = 1.0
    cascade_delay_max_hours: float = 24.0
    max_cascade_depth: int = 3

@dataclass
class WarningConfig:
    """Configuration for the three-tier warning system (Bible requirement)"""
    # Warning system enabled
    enable_warnings: bool = True
    
    # Phase durations
    rumor_phase_duration_hours: float = 8.0
    early_warning_duration_hours: float = 4.0
    imminent_warning_duration_hours: float = 1.0
    
    # Escalation probabilities
    rumor_escalation_probability: float = 0.6
    early_escalation_probability: float = 0.8
    imminent_trigger_probability: float = 0.9
    
    # Warning triggers
    rumor_pressure_threshold: float = 0.4
    early_pressure_threshold: float = 0.6
    imminent_pressure_threshold: float = 0.8
    
    # Warning visibility
    player_visible_warnings: bool = True
    gm_only_warnings: bool = False

@dataclass
class NarrativeConfig:
    """Configuration for narrative intelligence system (Bible requirement)"""
    # Narrative weighting enabled
    enable_narrative_weighting: bool = True
    
    # Tension management
    low_tension_threshold: float = 0.3
    high_tension_threshold: float = 0.8
    tension_adjustment_factor: float = 0.4
    
    # Engagement management
    low_engagement_threshold: float = 0.4
    high_engagement_threshold: float = 0.8
    engagement_boost_factor: float = 1.5
    
    # Theme priorities
    critical_theme_weight: float = 2.0
    central_theme_weight: float = 1.5
    supporting_theme_weight: float = 1.2
    background_theme_weight: float = 1.0
    
    # Story beat integration
    enable_story_beats: bool = True
    story_beat_influence_factor: float = 0.3
    max_active_story_beats: int = 5

@dataclass
class SystemConfig:
    """Configuration for system integration and monitoring"""
    # External system connections
    connection_timeout_seconds: float = 30.0
    connection_retry_attempts: int = 3
    connection_retry_delay_seconds: float = 5.0
    
    # Health monitoring
    health_check_interval_seconds: float = 60.0
    component_timeout_seconds: float = 120.0
    max_error_history: int = 100
    
    # Performance
    max_concurrent_operations: int = 10
    calculation_timeout_seconds: float = 15.0
    cache_duration_seconds: float = 300.0

class ChaosConfig:
    """
    Central configuration class for the chaos system.
    
    Manages all configuration aspects including pressure calculation,
    event generation, warnings, narrative intelligence, and system integration.
    """
    
    def __init__(self):
        # Core configuration sections
        self.pressure = PressureConfig()
        self.events = EventConfig()
        self.warnings = WarningConfig()
        self.narrative = NarrativeConfig()
        self.system = SystemConfig()
        
        # Debugging and development
        self.debug_mode: bool = False
        self.log_level: str = "INFO"
        self.enable_metrics: bool = True
        
        # System identification
        self.system_name: str = "chaos_system"
        self.version: str = "2.0.0"
        self.environment: str = "development"
        
        # Event system compatibility attributes (for EventTriggerSystem)
        self.max_events_per_hour = 3
        self.max_concurrent_events = 5
        self.cascade_delay_minutes = 30
        
        # Temporal pressure sources (Bible requirement)
        self._temporal_pressure_sources = [
            "temporal_anomaly",
            "timeline_disruption", 
            "causality_breach",
            "temporal_storm",
            "chronological_instability",
            "time_dilation_effect"
        ]
        
        # Event type standardization (fixing enum/string inconsistency)
        self._standard_event_types = [
            "economic_crisis",
            "political_upheaval", 
            "civil_unrest",
            "natural_disaster",
            "diplomatic_crisis",
            "temporal_anomaly",
            "faction_conflict",
            "resource_shortage",
            "technological_failure",
            "social_movement"
        ]
        
        # System settings
        self.enabled = True
        self.monitoring_interval = 30.0  # seconds
        self.cleanup_interval = 300.0    # seconds (5 minutes)
        
        # LLM Configuration
        self.llm_enabled = True
        self.llm_model_preference = "openai"  # "openai", "anthropic", or "auto"
        self.llm_fallback_to_templates = True
        self.llm_timeout_seconds = 30.0
        self.llm_max_retries = 2
        
        # LLM API Configuration (typically from environment variables)
        self.openai_api_key = None
        self.anthropic_api_key = None
        self.openai_model = "gpt-4"
        self.anthropic_model = "claude-3-sonnet-20240229"
        
        # LLM Usage Settings
        self.llm_event_generation_enabled = True
        self.llm_warning_generation_enabled = True
        self.llm_cascade_analysis_enabled = True
        self.llm_mitigation_suggestions_enabled = True
        
        # Pressure monitoring
        self.pressure_update_interval = 60.0  # seconds
        self.pressure_decay_rate = 0.02       # pressure decay per hour
        self.pressure_threshold_warning = 0.4
        self.pressure_threshold_critical = 0.7
        self.pressure_threshold_catastrophic = 0.9
        
        # Chaos events
        self.event_probability_base = 0.1     # Base probability per check
        self.event_probability_scaling = 2.0  # How much pressure affects probability
        self.event_cooldown_hours = 24.0      # Minimum time between events in same region
        self.event_duration_base = 12.0       # Base event duration in hours
        self.event_duration_variance = 0.3    # Duration variance (30%)
        
        # Warning system
        self.warning_enabled = True
        self.warning_advance_hours_min = 8.0  # Minimum warning time
        self.warning_advance_hours_max = 72.0 # Maximum warning time
        self.warning_escalation_probability = 0.7
        
        # Cascading effects
        self.cascade_enabled = True
        self.cascade_probability_base = 0.3
        self.cascade_delay_hours_min = 6.0
        self.cascade_delay_hours_max = 168.0  # 1 week
        
        # Mitigation system
        self.mitigation_enabled = True
        self.mitigation_decay_enabled = True
        self.mitigation_stacking_enabled = True
        self.mitigation_max_effectiveness = 0.9  # Can't completely eliminate chaos
        
        # Performance tuning
        self.max_active_events_per_region = 3
        self.max_cascades_per_event = 5
        self.max_mitigations_per_source = 10
        self.history_retention_days = 30
        
        # Load from environment variables if available
        self._load_from_environment()
    
    def _load_from_environment(self):
        """Load configuration from environment variables"""
        import os
        
        # System settings
        self.enabled = os.getenv('CHAOS_ENABLED', 'true').lower() == 'true'
        self.debug_mode = os.getenv('CHAOS_DEBUG', 'false').lower() == 'true'
        
        # LLM settings
        self.llm_enabled = os.getenv('CHAOS_LLM_ENABLED', 'true').lower() == 'true'
        self.llm_model_preference = os.getenv('CHAOS_LLM_MODEL_PREFERENCE', 'openai').lower()
        self.llm_fallback_to_templates = os.getenv('CHAOS_LLM_FALLBACK', 'true').lower() == 'true'
        
        # API keys
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
        
        # Model selection
        self.openai_model = os.getenv('CHAOS_OPENAI_MODEL', 'gpt-4')
        self.anthropic_model = os.getenv('CHAOS_ANTHROPIC_MODEL', 'claude-3-sonnet-20240229')
        
        # LLM timeouts and limits
        if timeout := os.getenv('CHAOS_LLM_TIMEOUT'):
            try:
                self.llm_timeout_seconds = float(timeout)
            except ValueError:
                pass
        
        if retries := os.getenv('CHAOS_LLM_MAX_RETRIES'):
            try:
                self.llm_max_retries = int(retries)
            except ValueError:
                pass
        
        # LLM feature toggles
        self.llm_event_generation_enabled = os.getenv('CHAOS_LLM_EVENTS', 'true').lower() == 'true'
        self.llm_warning_generation_enabled = os.getenv('CHAOS_LLM_WARNINGS', 'true').lower() == 'true'
        self.llm_cascade_analysis_enabled = os.getenv('CHAOS_LLM_CASCADES', 'true').lower() == 'true'
        self.llm_mitigation_suggestions_enabled = os.getenv('CHAOS_LLM_MITIGATIONS', 'true').lower() == 'true'
        
        # Timing settings
        if interval := os.getenv('CHAOS_MONITORING_INTERVAL'):
            try:
                self.monitoring_interval = float(interval)
            except ValueError:
                pass
        
        if interval := os.getenv('CHAOS_PRESSURE_UPDATE_INTERVAL'):
            try:
                self.pressure_update_interval = float(interval)
            except ValueError:
                pass
        
        # Probability settings
        if prob := os.getenv('CHAOS_EVENT_PROBABILITY_BASE'):
            try:
                self.event_probability_base = float(prob)
            except ValueError:
                pass
        
        if prob := os.getenv('CHAOS_CASCADE_PROBABILITY_BASE'):
            try:
                self.cascade_probability_base = float(prob)
            except ValueError:
                pass
        
        # Threshold settings
        if threshold := os.getenv('CHAOS_PRESSURE_THRESHOLD_WARNING'):
            try:
                self.pressure_threshold_warning = float(threshold)
            except ValueError:
                pass
        
        if threshold := os.getenv('CHAOS_PRESSURE_THRESHOLD_CRITICAL'):
            try:
                self.pressure_threshold_critical = float(threshold)
            except ValueError:
                pass
        
        if threshold := os.getenv('CHAOS_PRESSURE_THRESHOLD_CATASTROPHIC'):
            try:
                self.pressure_threshold_catastrophic = float(threshold)
            except ValueError:
                pass
    
    def get_llm_config(self) -> Dict[str, Any]:
        """Get LLM-specific configuration as a dictionary"""
        return {
            'enabled': self.llm_enabled,
            'model_preference': self.llm_model_preference,
            'fallback_to_templates': self.llm_fallback_to_templates,
            'timeout_seconds': self.llm_timeout_seconds,
            'max_retries': self.llm_max_retries,
            'openai_api_key': self.openai_api_key,
            'anthropic_api_key': self.anthropic_api_key,
            'openai_model': self.openai_model,
            'anthropic_model': self.anthropic_model,
            'features': {
                'event_generation': self.llm_event_generation_enabled,
                'warning_generation': self.llm_warning_generation_enabled,
                'cascade_analysis': self.llm_cascade_analysis_enabled,
                'mitigation_suggestions': self.llm_mitigation_suggestions_enabled
            }
        }
    
    def validate_configuration(self) -> List[str]:
        """Validate configuration settings and return any warnings/errors"""
        warnings = []
        
        # Check LLM configuration
        if self.llm_enabled:
            if not self.openai_api_key and not self.anthropic_api_key:
                warnings.append("LLM enabled but no API keys provided - will fall back to templates")
            
            if self.llm_model_preference == "openai" and not self.openai_api_key:
                warnings.append("OpenAI preferred but no API key provided")
            
            if self.llm_model_preference == "anthropic" and not self.anthropic_api_key:
                warnings.append("Anthropic preferred but no API key provided")
            
            if self.llm_timeout_seconds < 5.0:
                warnings.append("LLM timeout very low - may cause frequent timeouts")
        
        # Check probability ranges
        if not 0.0 <= self.event_probability_base <= 1.0:
            warnings.append("Event probability base should be between 0.0 and 1.0")
        
        if not 0.0 <= self.cascade_probability_base <= 1.0:
            warnings.append("Cascade probability base should be between 0.0 and 1.0")
        
        # Check threshold ordering
        if self.pressure_threshold_warning >= self.pressure_threshold_critical:
            warnings.append("Warning threshold should be less than critical threshold")
        
        if self.pressure_threshold_critical >= self.pressure_threshold_catastrophic:
            warnings.append("Critical threshold should be less than catastrophic threshold")
        
        # Check timing settings
        if self.monitoring_interval < 1.0:
            warnings.append("Monitoring interval very low - may impact performance")
        
        if self.event_cooldown_hours < 1.0:
            warnings.append("Event cooldown very low - may cause event spam")
        
        return warnings
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary for serialization"""
        return {
            'system': {
                'enabled': self.enabled,
                'debug_mode': self.debug_mode,
                'monitoring_interval': self.monitoring_interval,
                'cleanup_interval': self.cleanup_interval
            },
            'llm': self.get_llm_config(),
            'pressure': {
                'update_interval': self.pressure_update_interval,
                'decay_rate': self.pressure_decay_rate,
                'thresholds': {
                    'warning': self.pressure_threshold_warning,
                    'critical': self.pressure_threshold_critical,
                    'catastrophic': self.pressure_threshold_catastrophic
                }
            },
            'events': {
                'probability_base': self.event_probability_base,
                'probability_scaling': self.event_probability_scaling,
                'cooldown_hours': self.event_cooldown_hours,
                'duration_base': self.event_duration_base,
                'duration_variance': self.event_duration_variance
            },
            'warnings': {
                'enabled': self.warning_enabled,
                'advance_hours_min': self.warning_advance_hours_min,
                'advance_hours_max': self.warning_advance_hours_max,
                'escalation_probability': self.warning_escalation_probability
            },
            'cascades': {
                'enabled': self.cascade_enabled,
                'probability_base': self.cascade_probability_base,
                'delay_hours_min': self.cascade_delay_hours_min,
                'delay_hours_max': self.cascade_delay_hours_max
            },
            'mitigation': {
                'enabled': self.mitigation_enabled,
                'decay_enabled': self.mitigation_decay_enabled,
                'stacking_enabled': self.mitigation_stacking_enabled,
                'max_effectiveness': self.mitigation_max_effectiveness
            },
            'limits': {
                'max_active_events_per_region': self.max_active_events_per_region,
                'max_cascades_per_event': self.max_cascades_per_event,
                'max_mitigations_per_source': self.max_mitigations_per_source,
                'history_retention_days': self.history_retention_days
            }
        }
    
    # Temporal pressure interface methods (Bible requirement)
    def is_temporal_pressure_enabled(self) -> bool:
        """Check if temporal pressure monitoring is enabled"""
        return self.pressure.temporal_pressure_enabled
    
    def is_event_cascading_enabled(self) -> bool:
        """Check if event cascading is enabled"""
        return self.events.enable_cascading
    
    def is_mitigation_calculation_enabled(self) -> bool:
        """Check if mitigation calculation is enabled"""
        # For now, return True since we want mitigation support
        return True
    
    def get_temporal_pressure_sources(self) -> List[str]:
        """Get list of temporal pressure sources"""
        return self._temporal_pressure_sources.copy()
    
    def add_temporal_pressure_source(self, source: str) -> None:
        """Add a new temporal pressure source"""
        if source not in self._temporal_pressure_sources:
            self._temporal_pressure_sources.append(source)
    
    def remove_temporal_pressure_source(self, source: str) -> None:
        """Remove a temporal pressure source"""
        if source in self._temporal_pressure_sources:
            self._temporal_pressure_sources.remove(source)
    
    # Event type standardization methods
    def get_standard_event_types(self) -> List[str]:
        """Get list of standardized event types"""
        return self._standard_event_types.copy()
    
    def get_all_event_types(self) -> List[str]:
        """Get all event types (alias for get_standard_event_types)"""
        return self.get_standard_event_types()
    
    def is_valid_event_type(self, event_type: str) -> bool:
        """Check if an event type is valid/standardized"""
        return event_type in self._standard_event_types
    
    def normalize_event_type(self, event_type: str) -> str:
        """Normalize event type to standard format"""
        # Convert enum-style to string format
        if hasattr(event_type, 'value'):
            event_type = event_type.value
        
        # Convert to lowercase with underscores
        normalized = str(event_type).lower().replace(' ', '_').replace('-', '_')
        
        # Map common variations to standard types
        mapping = {
            'econ_crisis': 'economic_crisis',
            'political_crisis': 'political_upheaval',
            'civil_disorder': 'civil_unrest',
            'disaster': 'natural_disaster',
            'diplomatic_incident': 'diplomatic_crisis',
            'time_anomaly': 'temporal_anomaly',
            'faction_war': 'faction_conflict',
            'resource_crisis': 'resource_shortage',
            'tech_failure': 'technological_failure',
            'social_change': 'social_movement'
        }
        
        return mapping.get(normalized, normalized)
    
    # Pressure calculation methods
    def get_pressure_weights(self) -> Dict[str, float]:
        """Get all pressure source weights"""
        return {
            'economic': self.pressure.economic_weight,
            'political': self.pressure.political_weight,
            'social': self.pressure.social_weight,
            'environmental': self.pressure.environmental_weight,
            'diplomatic': self.pressure.diplomatic_weight,
            'temporal': self.pressure.temporal_weight
        }
    
    def get_pressure_decay_rates(self) -> Dict[str, float]:
        """Get all pressure source decay rates"""
        return {
            'economic': self.pressure.economic_decay,
            'political': self.pressure.political_decay,
            'social': self.pressure.social_decay,
            'environmental': self.pressure.environmental_decay,
            'diplomatic': self.pressure.diplomatic_decay,
            'temporal': self.pressure.temporal_decay
        }
    
    def calculate_effective_pressure_weight(self, pressure_type: str, base_value: float) -> float:
        """Calculate effective pressure weight with modifiers"""
        weights = self.get_pressure_weights()
        base_weight = weights.get(pressure_type, 1.0)
        
        # Apply temporal amplification if relevant
        if pressure_type == 'temporal' and base_value > self.pressure.temporal_detection_threshold:
            base_weight *= self.pressure.temporal_cascade_multiplier
        
        return base_weight
    
    # Warning system configuration
    def get_warning_thresholds(self) -> Dict[str, float]:
        """Get warning trigger thresholds"""
        return {
            'rumor': self.warnings.rumor_pressure_threshold,
            'early': self.warnings.early_pressure_threshold,
            'imminent': self.warnings.imminent_pressure_threshold
        }
    
    def get_warning_durations(self) -> Dict[str, float]:
        """Get warning phase durations in hours"""
        return {
            'rumor': self.warnings.rumor_phase_duration_hours,
            'early': self.warnings.early_warning_duration_hours,
            'imminent': self.warnings.imminent_warning_duration_hours
        }
    
    # Event configuration
    def get_event_thresholds(self) -> Dict[str, float]:
        """Get event severity thresholds"""
        return {
            'minor': self.events.minor_event_threshold,
            'moderate': self.events.moderate_event_threshold,
            'major': self.events.major_event_threshold,
            'critical': self.events.critical_event_threshold
        }
    
    def get_fatigue_settings(self) -> Dict[str, Union[bool, float, int]]:
        """Get fatigue management settings"""
        return {
            'enabled': self.events.enable_event_fatigue,
            'global_threshold': self.events.global_fatigue_threshold,
            'regional_threshold': self.events.regional_fatigue_threshold,
            'decay_rate': self.events.fatigue_decay_rate,
            'prevention_factor': self.events.fatigue_prevention_factor
        }
    
    # Narrative configuration
    def get_narrative_settings(self) -> Dict[str, Union[bool, float, int]]:
        """Get narrative intelligence settings"""
        return {
            'enabled': self.narrative.enable_narrative_weighting,
            'low_tension_threshold': self.narrative.low_tension_threshold,
            'high_tension_threshold': self.narrative.high_tension_threshold,
            'low_engagement_threshold': self.narrative.low_engagement_threshold,
            'high_engagement_threshold': self.narrative.high_engagement_threshold,
            'tension_adjustment_factor': self.narrative.tension_adjustment_factor,
            'engagement_boost_factor': self.narrative.engagement_boost_factor
        }
    
    def get_theme_weights(self) -> Dict[str, float]:
        """Get narrative theme weight modifiers"""
        return {
            'critical': self.narrative.critical_theme_weight,
            'central': self.narrative.central_theme_weight,
            'supporting': self.narrative.supporting_theme_weight,
            'background': self.narrative.background_theme_weight
        }
    
    # System configuration
    def get_connection_settings(self) -> Dict[str, Union[float, int]]:
        """Get system connection settings"""
        return {
            'timeout_seconds': self.system.connection_timeout_seconds,
            'retry_attempts': self.system.connection_retry_attempts,
            'retry_delay_seconds': self.system.connection_retry_delay_seconds
        }
    
    def get_health_monitoring_settings(self) -> Dict[str, Union[float, int]]:
        """Get health monitoring settings"""
        return {
            'check_interval_seconds': self.system.health_check_interval_seconds,
            'component_timeout_seconds': self.system.component_timeout_seconds,
            'max_error_history': self.system.max_error_history
        }
    
    # Configuration update methods
    def update_pressure_config(self, **kwargs) -> None:
        """Update pressure configuration parameters"""
        for key, value in kwargs.items():
            if hasattr(self.pressure, key):
                setattr(self.pressure, key, value)
    
    def update_event_config(self, **kwargs) -> None:
        """Update event configuration parameters"""
        for key, value in kwargs.items():
            if hasattr(self.events, key):
                setattr(self.events, key, value)
    
    def update_warning_config(self, **kwargs) -> None:
        """Update warning system configuration"""
        for key, value in kwargs.items():
            if hasattr(self.warnings, key):
                setattr(self.warnings, key, value)
    
    def update_narrative_config(self, **kwargs) -> None:
        """Update narrative intelligence configuration"""
        for key, value in kwargs.items():
            if hasattr(self.narrative, key):
                setattr(self.narrative, key, value)
    
    def update_system_config(self, **kwargs) -> None:
        """Update system configuration parameters"""
        for key, value in kwargs.items():
            if hasattr(self.system, key):
                setattr(self.system, key, value)
    
    # Configuration validation
    def validate_config(self) -> List[str]:
        """Validate configuration and return list of issues"""
        issues = []
        
        # Validate pressure thresholds
        if self.pressure.global_pressure_threshold <= 0 or self.pressure.global_pressure_threshold > 1:
            issues.append("Global pressure threshold must be between 0 and 1")
        
        if self.pressure.regional_pressure_threshold <= 0 or self.pressure.regional_pressure_threshold > 1:
            issues.append("Regional pressure threshold must be between 0 and 1")
        
        # Validate event thresholds
        thresholds = [
            self.events.minor_event_threshold,
            self.events.moderate_event_threshold,
            self.events.major_event_threshold,
            self.events.critical_event_threshold
        ]
        
        if not all(0 <= t <= 1 for t in thresholds):
            issues.append("All event thresholds must be between 0 and 1")
        
        if not all(thresholds[i] <= thresholds[i+1] for i in range(len(thresholds)-1)):
            issues.append("Event thresholds must be in ascending order")
        
        # Validate warning thresholds
        warning_thresholds = [
            self.warnings.rumor_pressure_threshold,
            self.warnings.early_pressure_threshold,
            self.warnings.imminent_pressure_threshold
        ]
        
        if not all(0 <= t <= 1 for t in warning_thresholds):
            issues.append("All warning thresholds must be between 0 and 1")
        
        if not all(warning_thresholds[i] <= warning_thresholds[i+1] for i in range(len(warning_thresholds)-1)):
            issues.append("Warning thresholds must be in ascending order")
        
        # Validate temporal pressure if enabled
        if self.pressure.temporal_pressure_enabled:
            if not self._temporal_pressure_sources:
                issues.append("Temporal pressure enabled but no sources defined")
            
            if self.pressure.temporal_weight <= 0:
                issues.append("Temporal pressure weight must be positive")
        
        return issues
    
    def get_config_summary(self) -> Dict[str, Any]:
        """Get a summary of all configuration settings"""
        return {
            'system': {
                'name': self.system_name,
                'version': self.version,
                'environment': self.environment,
                'debug_mode': self.debug_mode
            },
            'pressure': {
                'enabled_sources': list(self.get_pressure_weights().keys()),
                'source_count': len(self.get_pressure_weights()),
                'temporal_enabled': self.is_temporal_pressure_enabled(),
                'global_threshold': self.pressure.global_pressure_threshold
            },
            'events': {
                'base_frequency_hours': self.events.base_event_frequency_hours,
                'max_per_day': self.events.max_events_per_day,
                'fatigue_enabled': self.events.enable_event_fatigue,
                'cascading_enabled': self.events.enable_cascading
            },
            'warnings': {
                'enabled': self.warnings.enable_warnings,
                'phases': ['rumor', 'early', 'imminent'],
                'phase_durations': self.get_warning_durations()
            },
            'narrative': {
                'enabled': self.narrative.enable_narrative_weighting,
                'story_beats_enabled': self.narrative.enable_story_beats,
                'max_story_beats': self.narrative.max_active_story_beats
            }
        }
    
    def load_configurations(self) -> None:
        """Load configurations from external sources (if any)"""
        # This method exists for compatibility with chaos engine initialization
        # Currently, all configuration is done through dataclass defaults
        # In the future, this could load from JSON files, databases, etc.
        pass
    
    def save_configurations(self, file_path: Optional[str] = None) -> bool:
        """Save configurations to a JSON file"""
        try:
            config_data = {
                'pressure': {
                    field.name: getattr(self.pressure, field.name)
                    for field in fields(self.pressure)
                },
                'events': {
                    field.name: getattr(self.events, field.name)
                    for field in fields(self.events)
                },
                'warnings': {
                    field.name: getattr(self.warnings, field.name)
                    for field in fields(self.warnings)
                },
                'narrative': {
                    field.name: getattr(self.narrative, field.name)
                    for field in fields(self.narrative)
                },
                'system': {
                    field.name: getattr(self.system, field.name)
                    for field in fields(self.system)
                }
            }
            
            if file_path:
                with open(file_path, 'w') as f:
                    json.dump(config_data, f, indent=2, default=str)
                return True
                
            return True
            
        except Exception as e:
            print(f"Error saving configuration: {e}")
            return False

# Global configuration instance
chaos_config = ChaosConfig() 
"""
Chaos System Configuration

Centralized configuration for the chaos system with sensible defaults
and support for runtime tuning.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional
import os
from enum import Enum

class ChaosLevel(Enum):
    """Chaos intensity levels"""
    DORMANT = 0      # No chaos events
    LOW = 1          # Minor disturbances  
    MODERATE = 2     # Noticeable events
    HIGH = 3         # Significant disruption
    EXTREME = 4      # World-shaking events
    CATASTROPHIC = 5 # Reality-altering chaos

@dataclass
class ChaosConfig:
    """
    Configuration settings for the chaos system.
    
    All parameters can be tuned at runtime to adjust chaos behavior.
    """
    
    # === PRESSURE MONITORING ===
    pressure_update_interval: float = 30.0  # seconds between pressure checks
    pressure_history_length: int = 100      # number of pressure readings to keep
    pressure_decay_rate: float = 0.02       # how fast pressure decays naturally
    
    # === CHAOS CALCULATION ===
    # Pressure source weights (0.0 to 1.0)
    faction_conflict_weight: float = 0.25
    economic_instability_weight: float = 0.20
    population_stress_weight: float = 0.15
    diplomatic_tension_weight: float = 0.15
    military_buildup_weight: float = 0.15
    environmental_pressure_weight: float = 0.10
    
    # Chaos thresholds (0.0 to 1.0)
    chaos_thresholds: Dict[ChaosLevel, float] = field(default_factory=lambda: {
        ChaosLevel.DORMANT: 0.0,
        ChaosLevel.LOW: 0.15,
        ChaosLevel.MODERATE: 0.35,
        ChaosLevel.HIGH: 0.55,
        ChaosLevel.EXTREME: 0.75,
        ChaosLevel.CATASTROPHIC: 0.90
    })
    
    # Temporal factors
    pressure_buildup_multiplier: float = 1.2  # how fast pressure accelerates
    chaos_momentum_factor: float = 0.8        # how chaos feeds on itself
    
    # Regional vs global calculation
    regional_chaos_weight: float = 0.6        # balance between regional/global
    global_chaos_weight: float = 0.4
    
    # === EVENT TRIGGERING ===
    # Event probabilities by chaos level (0.0 to 1.0)
    event_base_probability: Dict[ChaosLevel, float] = field(default_factory=lambda: {
        ChaosLevel.DORMANT: 0.0,
        ChaosLevel.LOW: 0.05,
        ChaosLevel.MODERATE: 0.15,
        ChaosLevel.HIGH: 0.30,
        ChaosLevel.EXTREME: 0.50,
        ChaosLevel.CATASTROPHIC: 0.75
    })
    
    # Event type weights
    political_upheaval_weight: float = 0.20
    natural_disaster_weight: float = 0.15
    economic_collapse_weight: float = 0.15
    war_outbreak_weight: float = 0.15
    resource_scarcity_weight: float = 0.15
    faction_betrayal_weight: float = 0.10
    character_revelation_weight: float = 0.10
    
    # Legacy event_weights attribute for backward compatibility
    @property
    def event_weights(self) -> Dict[str, float]:
        """Legacy property for backward compatibility"""
        return {
            'political_upheaval': self.political_upheaval_weight,
            'natural_disaster': self.natural_disaster_weight,
            'economic_collapse': self.economic_collapse_weight,
            'war_outbreak': self.war_outbreak_weight,
            'resource_scarcity': self.resource_scarcity_weight,
            'faction_betrayal': self.faction_betrayal_weight,
            'character_revelation': self.character_revelation_weight
        }
    
    # Event cooldown periods (in seconds)
    event_cooldowns: Dict[str, float] = field(default_factory=lambda: {
        'political_upheaval': 3600.0,     # 1 hour
        'natural_disaster': 7200.0,       # 2 hours
        'economic_collapse': 14400.0,     # 4 hours
        'war_outbreak': 21600.0,          # 6 hours
        'resource_scarcity': 1800.0,      # 30 minutes
        'faction_betrayal': 10800.0,      # 3 hours
        'character_revelation': 5400.0    # 1.5 hours
    })
    
    # Event triggering constraints
    max_events_per_hour: int = 3              # rate limiting for event triggering
    max_concurrent_events: int = 5            # maximum events active at once
    cascade_delay_minutes: int = 15           # delay between cascade events
    
    # Legacy attribute for backward compatibility
    pressure_thresholds: Dict[str, float] = field(default_factory=lambda: {
        'low': 0.15,
        'moderate': 0.35,
        'high': 0.55,
        'extreme': 0.75,
        'catastrophic': 0.90
    })
    
    # Cascading effects
    enable_cascading_events: bool = True
    cascade_probability: float = 0.3         # chance for secondary events
    max_cascade_depth: int = 3               # prevent infinite cascades
    
    # === MITIGATION FACTORS ===
    # Mitigation effectiveness (0.0 to 1.0)
    diplomatic_action_effectiveness: float = 0.15
    quest_completion_effectiveness: float = 0.10
    faction_relation_effectiveness: float = 0.12
    infrastructure_effectiveness: float = 0.08
    leadership_effectiveness: float = 0.20
    npc_mitigation_effectiveness: float = 0.05
    
    # Mitigation decay
    mitigation_decay_rate: float = 0.01      # how fast mitigation effects fade
    mitigation_cumulative_bonus: float = 0.05  # bonus for sustained efforts
    
    # === SYSTEM INTEGRATION ===
    # Event dispatcher settings
    event_priority: int = 0                  # default priority for chaos events
    enable_analytics: bool = True            # track chaos events for analytics
    enable_analytics_persistence: bool = True  # persist analytics to disk
    
    # Performance settings
    max_pressure_calculations_per_tick: int = 50
    enable_parallel_processing: bool = True
    
    # Debug and monitoring
    enable_debug_logging: bool = False
    enable_performance_metrics: bool = True
    chaos_dashboard_enabled: bool = False    # hidden admin dashboard
    
    # === NARRATIVE COHERENCE ===
    # Motif system integration
    enable_motif_coordination: bool = True
    motif_influence_weight: float = 0.1      # how much motifs affect chaos
    
    # Story coherence settings
    maintain_narrative_consistency: bool = True
    event_spacing_minimum: float = 300.0    # minimum time between major events
    
    @classmethod
    def from_env(cls) -> 'ChaosConfig':
        """Load configuration from environment variables with fallbacks to defaults."""
        config = cls()
        
        # Load from environment if available
        config.pressure_update_interval = float(os.getenv('CHAOS_PRESSURE_INTERVAL', config.pressure_update_interval))
        config.pressure_decay_rate = float(os.getenv('CHAOS_PRESSURE_DECAY', config.pressure_decay_rate))
        config.enable_debug_logging = os.getenv('CHAOS_DEBUG', 'false').lower() == 'true'
        config.chaos_dashboard_enabled = os.getenv('CHAOS_DASHBOARD', 'false').lower() == 'true'
        
        return config
    
    def update_weights(self, **kwargs) -> None:
        """Update pressure source weights at runtime."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, float(value))
    
    def set_chaos_threshold(self, level: ChaosLevel, threshold: float) -> None:
        """Update chaos threshold for a specific level."""
        if 0.0 <= threshold <= 1.0:
            self.chaos_thresholds[level] = threshold
    
    def get_total_pressure_weight(self) -> float:
        """Calculate total pressure weight to ensure it sums to 1.0."""
        return (
            self.faction_conflict_weight +
            self.economic_instability_weight + 
            self.population_stress_weight +
            self.diplomatic_tension_weight +
            self.military_buildup_weight +
            self.environmental_pressure_weight
        )
    
    def normalize_pressure_weights(self) -> None:
        """Normalize all pressure weights to sum to 1.0."""
        total = self.get_total_pressure_weight()
        if total > 0:
            factor = 1.0 / total
            self.faction_conflict_weight *= factor
            self.economic_instability_weight *= factor
            self.population_stress_weight *= factor
            self.diplomatic_tension_weight *= factor
            self.military_buildup_weight *= factor
            self.environmental_pressure_weight *= factor

# Global configuration instance
chaos_config = ChaosConfig.from_env() 
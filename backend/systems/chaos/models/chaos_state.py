"""
Chaos State Models

Models for tracking the current state of the chaos system, including
chaos levels, thresholds, mitigation factors, and event cooldowns.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timedelta
from enum import Enum
from uuid import UUID

from backend.systems.chaos.core.config import ChaosLevel

@dataclass
class ChaosThreshold:
    """Configuration for a specific chaos threshold"""
    level: ChaosLevel
    threshold_value: float  # 0.0 to 1.0
    description: str
    event_probability: float = 0.0  # Probability of event at this level
    intensity_multiplier: float = 1.0  # Event intensity scaling
    cooldown_reduction: float = 1.0  # Cooldown time multiplier
    
    def is_exceeded(self, chaos_score: float) -> bool:
        """Check if chaos score exceeds this threshold"""
        return chaos_score >= self.threshold_value

@dataclass
class MitigationFactor:
    """Represents a mitigation factor that reduces chaos pressure"""
    mitigation_id: str
    mitigation_type: str  # "diplomatic", "quest", "infrastructure", etc.
    source_id: Union[str, UUID]  # ID of entity providing mitigation
    source_type: str  # "player", "npc", "faction", "system"
    
    # Mitigation properties
    effectiveness: float  # 0.0 to 1.0
    duration_hours: float  # How long this mitigation lasts
    decay_rate: float = 0.0  # How fast effectiveness decays over time
    
    # Scope and targeting
    affected_regions: List[Union[str, UUID]] = field(default_factory=list)
    affected_sources: List[str] = field(default_factory=list)  # Which pressure sources this affects
    
    # Tracking
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    
    # Metadata
    description: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Set expiration time based on duration"""
        if self.expires_at is None and self.duration_hours > 0:
            self.expires_at = self.created_at + timedelta(hours=self.duration_hours)
    
    def is_active(self) -> bool:
        """Check if this mitigation factor is still active"""
        if self.expires_at is None:
            return True  # Permanent mitigation
        return datetime.now() < self.expires_at
    
    def get_current_effectiveness(self) -> float:
        """Get current effectiveness accounting for decay"""
        if not self.is_active():
            return 0.0
        
        if self.decay_rate <= 0:
            return self.effectiveness
        
        # Calculate decay based on time elapsed
        time_elapsed = (datetime.now() - self.created_at).total_seconds() / 3600.0  # hours
        decayed_effectiveness = self.effectiveness * (1.0 - self.decay_rate * time_elapsed)
        
        return max(0.0, decayed_effectiveness)
    
    def apply_to_pressure(self, pressure_value: float, pressure_source: str) -> float:
        """Apply this mitigation to a pressure value"""
        if not self.is_active():
            return pressure_value
        
        # Check if this mitigation affects this pressure source
        if self.affected_sources and pressure_source not in self.affected_sources:
            return pressure_value
        
        # Apply mitigation
        current_effectiveness = self.get_current_effectiveness()
        reduced_pressure = pressure_value * (1.0 - current_effectiveness)
        
        return max(0.0, reduced_pressure)

@dataclass
class EventCooldown:
    """Tracks cooldown periods for chaos events"""
    event_type: str
    last_triggered: datetime
    cooldown_duration: float  # seconds
    region_id: Optional[Union[str, UUID]] = None  # Regional cooldowns
    
    def is_on_cooldown(self) -> bool:
        """Check if this event is still on cooldown"""
        time_since_last = (datetime.now() - self.last_triggered).total_seconds()
        return time_since_last < self.cooldown_duration
    
    def get_remaining_cooldown(self) -> float:
        """Get remaining cooldown time in seconds"""
        time_since_last = (datetime.now() - self.last_triggered).total_seconds()
        remaining = self.cooldown_duration - time_since_last
        return max(0.0, remaining)
    
    def get_cooldown_progress(self) -> float:
        """Get cooldown progress as percentage (0.0 to 1.0)"""
        if self.cooldown_duration <= 0:
            return 1.0
        
        time_since_last = (datetime.now() - self.last_triggered).total_seconds()
        progress = time_since_last / self.cooldown_duration
        return min(1.0, progress)

@dataclass
class ChaosState:
    """Complete state of the chaos system at a point in time"""
    
    # Current chaos metrics
    current_chaos_score: float = 0.0
    current_chaos_level: ChaosLevel = ChaosLevel.DORMANT
    previous_chaos_level: ChaosLevel = ChaosLevel.DORMANT
    
    # Trend and velocity
    chaos_trend: float = 0.0  # Rate of change
    chaos_velocity: float = 0.0  # Instantaneous change rate
    pressure_momentum: float = 0.0  # Consistency of direction
    
    # Regional breakdown
    regional_chaos_scores: Dict[Union[str, UUID], float] = field(default_factory=dict)
    regional_chaos_levels: Dict[Union[str, UUID], ChaosLevel] = field(default_factory=dict)
    
    # Source contributions
    pressure_source_contributions: Dict[str, float] = field(default_factory=dict)
    dominant_pressure_source: Optional[str] = None
    
    # Temporal factors
    temporal_adjustments: Dict[str, float] = field(default_factory=dict)
    pressure_buildup_factor: float = 1.0
    momentum_factor: float = 1.0
    
    # Mitigation and modifiers
    active_mitigations: List[MitigationFactor] = field(default_factory=list)
    total_mitigation_effectiveness: float = 0.0
    
    # Event management
    event_cooldowns: Dict[str, EventCooldown] = field(default_factory=dict)
    events_triggered_today: int = 0
    last_event_time: Optional[datetime] = None
    
    # System health
    calculation_timestamp: datetime = field(default_factory=datetime.now)
    system_health: float = 1.0  # Overall health of chaos system (0.0 to 1.0)
    pressure_stability: float = 1.0  # How stable pressure readings are
    
    # Historical tracking
    score_history: List[Tuple[datetime, float]] = field(default_factory=list)
    level_changes: List[Tuple[datetime, ChaosLevel, ChaosLevel]] = field(default_factory=list)
    event_history: List[Dict[str, Any]] = field(default_factory=list)
    
    # Predictions and forecasting
    predicted_trajectory: List[float] = field(default_factory=list)  # Next 24 hours
    risk_assessment: Dict[str, float] = field(default_factory=dict)
    
    def update_chaos_level(self, new_level: ChaosLevel) -> bool:
        """Update chaos level and track changes"""
        if new_level != self.current_chaos_level:
            self.previous_chaos_level = self.current_chaos_level
            self.current_chaos_level = new_level
            
            # Record level change
            self.level_changes.append((
                datetime.now(), 
                self.previous_chaos_level, 
                self.current_chaos_level
            ))
            
            return True
        return False
    
    def add_mitigation(self, mitigation: MitigationFactor) -> None:
        """Add a new mitigation factor"""
        self.active_mitigations.append(mitigation)
        self._update_total_mitigation_effectiveness()
    
    def remove_expired_mitigations(self) -> List[MitigationFactor]:
        """Remove expired mitigations and return them"""
        expired = []
        active = []
        
        for mitigation in self.active_mitigations:
            if mitigation.is_active():
                active.append(mitigation)
            else:
                expired.append(mitigation)
        
        self.active_mitigations = active
        self._update_total_mitigation_effectiveness()
        
        return expired
    
    def _update_total_mitigation_effectiveness(self) -> None:
        """Calculate total mitigation effectiveness"""
        if not self.active_mitigations:
            self.total_mitigation_effectiveness = 0.0
            return
        
        # Calculate combined effectiveness (not simply additive)
        combined_effectiveness = 0.0
        for mitigation in self.active_mitigations:
            current_eff = mitigation.get_current_effectiveness()
            # Use diminishing returns formula
            combined_effectiveness = combined_effectiveness + current_eff * (1.0 - combined_effectiveness)
        
        self.total_mitigation_effectiveness = min(1.0, combined_effectiveness)
    
    def apply_mitigation_to_score(self, base_score: float) -> float:
        """Apply all active mitigations to a chaos score"""
        if not self.active_mitigations:
            return base_score
        
        mitigated_score = base_score
        for mitigation in self.active_mitigations:
            # Apply mitigation using a logarithmic reduction to prevent over-mitigation
            reduction_factor = mitigation.get_current_effectiveness()
            mitigated_score = mitigated_score * (1.0 - reduction_factor * 0.5)  # Cap reduction
        
        return max(0.0, mitigated_score)
    
    def set_event_cooldown(self, event_type: str, cooldown_duration: float, 
                          region_id: Optional[Union[str, UUID]] = None) -> None:
        """Set cooldown for a specific event type"""
        cooldown_key = f"{event_type}_{region_id}" if region_id else event_type
        
        cooldown = EventCooldown(
            event_type=event_type,
            last_triggered=datetime.now(),
            cooldown_duration=cooldown_duration,
            region_id=region_id
        )
        
        self.event_cooldowns[cooldown_key] = cooldown
    
    def is_event_on_cooldown(self, event_type: str, 
                           region_id: Optional[Union[str, UUID]] = None) -> bool:
        """Check if an event type is on cooldown"""
        cooldown_key = f"{event_type}_{region_id}" if region_id else event_type
        
        if cooldown_key in self.event_cooldowns:
            return self.event_cooldowns[cooldown_key].is_on_cooldown()
        
        return False
    
    def get_event_cooldown_remaining(self, event_type: str,
                                   region_id: Optional[Union[str, UUID]] = None) -> float:
        """Get remaining cooldown time for an event type"""
        cooldown_key = f"{event_type}_{region_id}" if region_id else event_type
        
        if cooldown_key in self.event_cooldowns:
            return self.event_cooldowns[cooldown_key].get_remaining_cooldown()
        
        return 0.0
    
    def clean_expired_cooldowns(self) -> None:
        """Remove expired cooldowns"""
        active_cooldowns = {}
        for key, cooldown in self.event_cooldowns.items():
            if cooldown.is_on_cooldown():
                active_cooldowns[key] = cooldown
        
        self.event_cooldowns = active_cooldowns
    
    def record_event(self, event_details: Dict[str, Any]) -> None:
        """Record a chaos event in the history"""
        event_record = {
            'timestamp': datetime.now().isoformat(),
            'chaos_score': self.current_chaos_score,
            'chaos_level': self.current_chaos_level.value,
            **event_details
        }
        
        self.event_history.append(event_record)
        self.events_triggered_today += 1
        self.last_event_time = datetime.now()
        
        # Keep only recent events in memory
        max_events = 100
        if len(self.event_history) > max_events:
            self.event_history = self.event_history[-max_events:]
    
    def update_score_history(self, max_history: int = 144) -> None:
        """Update score history (keep last 144 entries = 24 hours if updated every 10 minutes)"""
        self.score_history.append((datetime.now(), self.current_chaos_score))
        
        if len(self.score_history) > max_history:
            self.score_history = self.score_history[-max_history:]
    
    def get_chaos_summary(self) -> Dict[str, Any]:
        """Get a comprehensive summary of the current chaos state"""
        return {
            'current_chaos': {
                'score': self.current_chaos_score,
                'level': self.current_chaos_level.value,
                'trend': self.chaos_trend,
                'velocity': self.chaos_velocity
            },
            'pressure_breakdown': {
                'dominant_source': self.dominant_pressure_source,
                'source_contributions': self.pressure_source_contributions,
                'regional_scores': {str(k): v for k, v in self.regional_chaos_scores.items()}
            },
            'mitigation': {
                'total_effectiveness': self.total_mitigation_effectiveness,
                'active_mitigations': len(self.active_mitigations),
                'mitigation_details': [
                    {
                        'type': m.mitigation_type,
                        'effectiveness': m.get_current_effectiveness(),
                        'expires_in_hours': (m.expires_at - datetime.now()).total_seconds() / 3600.0 
                                          if m.expires_at else None
                    }
                    for m in self.active_mitigations
                ]
            },
            'events': {
                'events_today': self.events_triggered_today,
                'last_event': self.last_event_time.isoformat() if self.last_event_time else None,
                'active_cooldowns': {
                    event_type: cooldown.get_remaining_cooldown()
                    for event_type, cooldown in self.event_cooldowns.items()
                    if cooldown.is_on_cooldown()
                }
            },
            'system_health': {
                'overall_health': self.system_health,
                'pressure_stability': self.pressure_stability,
                'calculation_age_seconds': (datetime.now() - self.calculation_timestamp).total_seconds()
            },
            'predictions': {
                'trajectory': self.predicted_trajectory[:12],  # Next 12 hours
                'risk_assessment': self.risk_assessment
            }
        }
    
    def get_regional_chaos_summary(self, region_id: Union[str, UUID]) -> Dict[str, Any]:
        """Get chaos summary for a specific region"""
        region_key = str(region_id)
        
        return {
            'region_id': region_key,
            'chaos_score': self.regional_chaos_scores.get(region_id, 0.0),
            'chaos_level': self.regional_chaos_levels.get(region_id, ChaosLevel.DORMANT).value,
            'regional_cooldowns': {
                event_type: cooldown.get_remaining_cooldown()
                for event_type, cooldown in self.event_cooldowns.items()
                if cooldown.region_id == region_id and cooldown.is_on_cooldown()
            },
            'regional_mitigations': [
                {
                    'type': m.mitigation_type,
                    'effectiveness': m.get_current_effectiveness(),
                    'source': m.source_type
                }
                for m in self.active_mitigations
                if not m.affected_regions or region_id in m.affected_regions
            ]
        }
    
    def calculate_risk_assessment(self) -> Dict[str, float]:
        """Calculate risk assessment for different types of chaos events"""
        base_risk = self.current_chaos_score
        
        # Adjust risk based on trends and velocity
        trend_adjustment = max(0.0, self.chaos_trend * 5.0)  # Positive trends increase risk
        velocity_adjustment = min(0.3, abs(self.chaos_velocity) * 2.0)  # Rapid changes increase risk
        
        # Mitigation reduces risk
        mitigation_reduction = self.total_mitigation_effectiveness * 0.4
        
        adjusted_risk = base_risk + trend_adjustment + velocity_adjustment - mitigation_reduction
        adjusted_risk = max(0.0, min(1.0, adjusted_risk))
        
        # Calculate specific event risks based on source contributions
        event_risks = {}
        for source, contribution in self.pressure_source_contributions.items():
            # Map pressure sources to event types
            source_to_event = {
                'faction_conflict': 'political_upheaval',
                'economic_instability': 'economic_collapse',
                'diplomatic_tension': 'war_outbreak',
                'population_stress': 'social_unrest',
                'military_buildup': 'war_outbreak',
                'environmental_pressure': 'natural_disaster'
            }
            
            if source in source_to_event:
                event_type = source_to_event[source]
                event_risk = adjusted_risk * contribution
                
                # Check cooldowns - reduce risk if event is on cooldown
                if self.is_event_on_cooldown(event_type):
                    cooldown_progress = 0.0
                    for cooldown in self.event_cooldowns.values():
                        if cooldown.event_type == event_type:
                            cooldown_progress = cooldown.get_cooldown_progress()
                            break
                    event_risk *= cooldown_progress  # Reduced risk during cooldown
                
                event_risks[event_type] = event_risk
        
        self.risk_assessment = event_risks
        return event_risks

@dataclass
class ChaosMetrics:
    """Metrics and statistics for the chaos system"""
    total_events_triggered: int = 0
    average_chaos_score: float = 0.0
    peak_chaos_score: float = 0.0
    time_in_high_chaos: timedelta = field(default_factory=lambda: timedelta(0))
    mitigation_effectiveness: float = 0.0
    last_calculated: datetime = field(default_factory=datetime.now)
    
    # Additional metrics
    events_by_type: Dict[str, int] = field(default_factory=dict)
    average_event_severity: float = 0.0
    system_uptime: timedelta = field(default_factory=lambda: timedelta(0))
    calculation_performance: Dict[str, float] = field(default_factory=dict)
    
    def update_metrics(self, chaos_score: float, events_triggered: int = 0, 
                      event_type: Optional[str] = None) -> None:
        """Update metrics with new data"""
        # Update basic metrics
        if chaos_score > self.peak_chaos_score:
            self.peak_chaos_score = chaos_score
        
        # Update average (simple moving average for now)
        self.average_chaos_score = (self.average_chaos_score + chaos_score) / 2.0
        
        # Update event counts
        self.total_events_triggered += events_triggered
        if event_type and events_triggered > 0:
            self.events_by_type[event_type] = self.events_by_type.get(event_type, 0) + events_triggered
        
        self.last_calculated = datetime.now()

@dataclass
class ChaosHistoryEntry:
    """Single entry in chaos history"""
    timestamp: datetime
    chaos_level: ChaosLevel
    chaos_score: float
    dominant_pressure_source: Optional[str] = None
    events_triggered: List[str] = field(default_factory=list)
    mitigation_effectiveness: float = 0.0

@dataclass
class ChaosHistory:
    """Historical tracking of chaos system state"""
    entries: List[ChaosHistoryEntry] = field(default_factory=list)
    max_entries: int = 1000  # Keep last 1000 entries
    
    def add_entry(self, chaos_level: ChaosLevel, chaos_score: float, 
                  timestamp: Optional[datetime] = None, **kwargs) -> None:
        """Add a new history entry"""
        if timestamp is None:
            timestamp = datetime.now()
        
        entry = ChaosHistoryEntry(
            timestamp=timestamp,
            chaos_level=chaos_level,
            chaos_score=chaos_score,
            **kwargs
        )
        
        self.entries.append(entry)
        
        # Trim old entries
        if len(self.entries) > self.max_entries:
            self.entries = self.entries[-self.max_entries:]
    
    def get_trend(self, hours: int = 24) -> str:
        """Get trend over the last N hours"""
        if len(self.entries) < 2:
            return 'stable'
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_entries = [e for e in self.entries if e.timestamp >= cutoff_time]
        
        if len(recent_entries) < 2:
            return 'stable'
        
        # Compare first and last scores
        first_score = recent_entries[0].chaos_score
        last_score = recent_entries[-1].chaos_score
        
        if last_score > first_score * 1.1:
            return 'increasing'
        elif last_score < first_score * 0.9:
            return 'decreasing'
        else:
            return 'stable'
    
    def get_average_score(self, hours: int = 24) -> float:
        """Get average chaos score over the last N hours"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_entries = [e for e in self.entries if e.timestamp >= cutoff_time]
        
        if not recent_entries:
            return 0.0
        
        return sum(e.chaos_score for e in recent_entries) / len(recent_entries)

@dataclass
class ChaosConfiguration:
    """Configuration settings for the chaos system"""
    # Threshold settings
    chaos_thresholds: Dict[ChaosLevel, float] = field(default_factory=lambda: {
        ChaosLevel.DORMANT: 0.0,
        ChaosLevel.STABLE: 0.2,
        ChaosLevel.MODERATE: 0.4,
        ChaosLevel.HIGH: 0.6,
        ChaosLevel.CRITICAL: 0.8,
        ChaosLevel.CATASTROPHIC: 0.95
    })
    
    # Event triggering settings
    max_events_per_hour: int = 3
    max_concurrent_events: int = 5
    event_cooldown_hours: float = 2.0
    cascade_probability: float = 0.3
    
    # Pressure monitoring settings
    pressure_update_interval: int = 600  # seconds
    pressure_decay_rate: float = 0.1
    pressure_buildup_factor: float = 1.2
    
    # Mitigation settings
    max_mitigation_effectiveness: float = 0.8
    mitigation_decay_rate: float = 0.05
    
    # System performance settings
    calculation_timeout: float = 30.0  # seconds
    max_calculation_retries: int = 3
    
    def get_threshold_for_level(self, level: ChaosLevel) -> float:
        """Get threshold value for a chaos level"""
        return self.chaos_thresholds.get(level, 0.0)
    
    def update_threshold(self, level: ChaosLevel, threshold: float) -> None:
        """Update threshold for a chaos level"""
        if 0.0 <= threshold <= 1.0:
            self.chaos_thresholds[level] = threshold 
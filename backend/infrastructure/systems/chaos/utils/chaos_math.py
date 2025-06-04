"""
Chaos Mathematics and Calculations

Mathematical functions and utilities for chaos system calculations.
Implements Bible-compliant pressure weighting, chaos level determination,
and temporal pressure calculations.
"""

import math
import random
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field

from backend.systems.chaos.core.config import ChaosConfig
from backend.infrastructure.systems.chaos.models.chaos_state import ChaosLevel, MitigationFactor
from backend.infrastructure.systems.chaos.models.pressure_data import PressureData

@dataclass
class ChaosCalculationResult:
    """Result of chaos score calculation"""
    chaos_score: float
    chaos_level: ChaosLevel
    pressure_sources: Dict[str, float] = field(default_factory=dict)
    weighted_factors: Dict[str, float] = field(default_factory=dict)
    total_pressure: float = 0.0
    mitigation_effect: float = 0.0
    temporal_factor: float = 0.0
    threshold_exceeded: bool = False
    recommended_events: List[str] = field(default_factory=list)
    calculation_time_ms: float = 0.0

class ChaosMath:
    """
    Mathematical calculations for the chaos system.
    
    Handles Bible-compliant pressure weighting, chaos level determination,
    temporal pressure integration, and mitigation calculations.
    """
    
    def __init__(self, config: ChaosConfig):
        """Initialize with chaos configuration"""
        self.config = config
        self.pressure_weights = config.get_pressure_weights()
        
    def calculate_chaos_score(self, pressure_data: PressureData) -> ChaosCalculationResult:
        """
        Calculate chaos score from pressure data using Bible-compliant formula.
        
        Args:
            pressure_data: Pressure data containing source pressures
            
        Returns:
            ChaosCalculationResult with calculated chaos score and metadata
        """
        start_time = datetime.now()
        
        # Handle empty pressure data
        if not pressure_data.pressure_sources:
            return ChaosCalculationResult(
                chaos_score=0.0,
                chaos_level=ChaosLevel.STABLE,
                calculation_time_ms=0.0
            )
        
        # Calculate weighted pressure from all sources
        weighted_pressure = self._calculate_weighted_pressure(pressure_data.pressure_sources)
        
        # Apply temporal pressure if enabled (Bible 6th pressure type)
        temporal_factor = self._calculate_temporal_factor(pressure_data)
        total_pressure = weighted_pressure + temporal_factor
        
        # Apply mitigation effects if any active mitigations
        mitigation_effect = self._calculate_mitigation_effect(pressure_data)
        mitigated_pressure = total_pressure * (1.0 - mitigation_effect)
        
        # Ensure chaos score stays within Bible bounds (0.0 - 1.0)
        chaos_score = max(0.0, min(1.0, mitigated_pressure))
        
        # Determine chaos level based on Bible thresholds
        chaos_level = self._determine_chaos_level_from_score(chaos_score)
        
        # Check if any thresholds are exceeded
        threshold_exceeded = chaos_score >= self.config.chaos_threshold_low
        
        # Recommend events based on pressure sources and chaos level
        recommended_events = self._recommend_events(pressure_data.pressure_sources, chaos_level)
        
        # Calculate weighted factors for debugging/analysis
        weighted_factors = {}
        for source, value in pressure_data.pressure_sources.items():
            weight = self.pressure_weights.get(source, 1.0)
            weighted_factors[source] = value * weight
        
        calculation_time = (datetime.now() - start_time).total_seconds() * 1000
        
        return ChaosCalculationResult(
            chaos_score=chaos_score,
            chaos_level=chaos_level,
            pressure_sources=pressure_data.pressure_sources.copy(),
            weighted_factors=weighted_factors,
            total_pressure=total_pressure,
            mitigation_effect=mitigation_effect,
            temporal_factor=temporal_factor,
            threshold_exceeded=threshold_exceeded,
            recommended_events=recommended_events,
            calculation_time_ms=calculation_time
        )
    
    def _calculate_weighted_pressure(self, pressure_sources: Dict[str, float]) -> float:
        """
        Calculate weighted pressure using Bible-specified weights.
        
        Bible specifies political pressure should have higher weight (1.2)
        compared to economic (1.0) and other pressure types.
        """
        if not pressure_sources:
            return 0.0
        
        total_weighted = 0.0
        total_weight = 0.0
        
        for source, value in pressure_sources.items():
            # Get Bible-specified weight for this pressure type
            weight = self.pressure_weights.get(source, 1.0)
            
            # Ensure pressure value is within Bible bounds
            normalized_value = max(0.0, min(1.0, float(value)))
            
            total_weighted += normalized_value * weight
            total_weight += weight
        
        # Calculate weighted average
        if total_weight > 0:
            return total_weighted / total_weight
        return 0.0
    
    def _calculate_temporal_factor(self, pressure_data: PressureData) -> float:
        """
        Calculate temporal pressure factor (Bible 6th pressure type).
        
        Temporal pressure affects reality stability and time flow.
        Only applied if temporal pressure is enabled in configuration.
        """
        if not self.config.is_temporal_pressure_enabled():
            return 0.0
        
        temporal_pressure = 0.0
        temporal_sources = self.config.get_temporal_pressure_sources()
        
        # Check for temporal pressure in pressure sources
        for source in temporal_sources:
            if source in pressure_data.pressure_sources:
                temporal_pressure += pressure_data.pressure_sources[source]
        
        # Also check for 'temporal' pressure type directly
        if 'temporal' in pressure_data.pressure_sources:
            temporal_pressure += pressure_data.pressure_sources['temporal']
        
        # Apply temporal weight if configured
        temporal_weight = self.pressure_weights.get('temporal', 0.7)
        
        # Temporal pressure has non-linear effects (Bible requirement)
        if temporal_pressure > 0:
            # Exponential scaling for temporal effects
            temporal_factor = (temporal_pressure ** 1.5) * temporal_weight
            return min(0.3, temporal_factor)  # Cap temporal contribution at 30%
        
        return 0.0
    
    def _calculate_mitigation_effect(self, pressure_data: PressureData) -> float:
        """
        Calculate mitigation effects on pressure (Bible requirement).
        
        Mitigation should reduce pressure values over time with diminishing returns.
        """
        if not self.config.is_mitigation_calculation_enabled():
            return 0.0
        
        # Check if pressure_data has mitigation information
        if not hasattr(pressure_data, 'active_mitigations'):
            return 0.0
        
        total_mitigation = 0.0
        
        # Apply diminishing returns formula for multiple mitigations
        for mitigation in getattr(pressure_data, 'active_mitigations', []):
            if isinstance(mitigation, MitigationFactor):
                effectiveness = mitigation.get_current_effectiveness()
                # Use logarithmic diminishing returns
                mitigation_contribution = effectiveness * (1.0 - total_mitigation)
                total_mitigation += mitigation_contribution
        
        # Cap mitigation at 80% to prevent complete chaos elimination
        return min(0.8, total_mitigation)
    
    def _determine_chaos_level_from_score(self, chaos_score: float) -> ChaosLevel:
        """
        Determine chaos level from score using Bible-specified thresholds.
        
        Bible thresholds: 0.3 (low), 0.6 (medium), 0.8 (high)
        """
        if chaos_score >= self.config.chaos_threshold_high:  # >= 0.8
            return ChaosLevel.HIGH
        elif chaos_score >= self.config.chaos_threshold_medium:  # >= 0.6
            return ChaosLevel.MODERATE
        elif chaos_score >= self.config.chaos_threshold_low:  # >= 0.3
            return ChaosLevel.LOW
        else:  # < 0.3
            return ChaosLevel.STABLE
    
    def _recommend_events(self, pressure_sources: Dict[str, float], chaos_level: ChaosLevel) -> List[str]:
        """
        Recommend event types based on pressure sources and chaos level.
        
        Returns events that are likely to trigger given current pressures.
        """
        recommended = []
        
        # Map pressure sources to potential events
        pressure_to_events = {
            'political': ['political_upheaval', 'diplomatic_crisis'],
            'economic': ['economic_collapse', 'resource_scarcity'],
            'social': ['social_unrest', 'faction_betrayal'],
            'environmental': ['natural_disaster', 'resource_scarcity'],
            'diplomatic': ['diplomatic_crisis', 'faction_betrayal'],
            'temporal': ['temporal_anomaly', 'reality_distortion']  # Bible 6th type
        }
        
        # Recommend events based on high pressure sources
        for source, pressure in pressure_sources.items():
            if pressure >= 0.5:  # High pressure threshold
                events = pressure_to_events.get(source, [])
                for event in events:
                    if event not in recommended:
                        recommended.append(event)
        
        # Filter recommendations based on chaos level
        if chaos_level in [ChaosLevel.STABLE, ChaosLevel.LOW]:
            # Only minor events at low chaos
            recommended = [e for e in recommended if e in ['social_unrest', 'economic_disruption']]
        elif chaos_level == ChaosLevel.MODERATE:
            # Most events available at moderate chaos
            pass  # Keep all recommendations
        else:  # HIGH chaos
            # All events possible, including catastrophic ones
            if any(p >= 0.8 for p in pressure_sources.values()):
                recommended.extend(['chaos_storm', 'reality_breakdown'])
        
        return recommended[:5]  # Limit to top 5 recommendations
    
    def calculate_event_probability(self, event_type: str, pressure_data: PressureData, chaos_level: ChaosLevel) -> float:
        """
        Calculate probability of a specific event triggering.
        
        Takes into account pressure requirements, chaos level, and event configuration.
        """
        event_config = self.config.get_event_config(event_type)
        if not event_config:
            return 0.0
        
        # Check pressure requirements
        requirements_met = True
        for required_source, required_level in event_config.pressure_requirements.items():
            current_level = pressure_data.pressure_sources.get(required_source, 0.0)
            if current_level < required_level:
                requirements_met = False
                break
        
        if not requirements_met:
            return 0.0
        
        # Base probability from configuration
        base_probability = event_config.base_probability
        
        # Scale by chaos level
        chaos_multipliers = {
            ChaosLevel.STABLE: 0.5,
            ChaosLevel.LOW: 1.0,
            ChaosLevel.MODERATE: 1.5,
            ChaosLevel.HIGH: 2.0,
            ChaosLevel.CRITICAL: 3.0,
            ChaosLevel.CATASTROPHIC: 5.0
        }
        
        chaos_multiplier = chaos_multipliers.get(chaos_level, 1.0)
        
        # Apply severity scaling from configuration
        severity_scaling = event_config.severity_scaling
        
        # Calculate final probability
        final_probability = base_probability * chaos_multiplier * severity_scaling
        
        # Ensure probability stays within bounds
        return min(1.0, max(0.0, final_probability))
    
    def calculate_cascade_probability(self, source_event: str, target_event: str, current_chaos: float) -> float:
        """
        Calculate probability of event cascading from source to target.
        
        Bible specifies events should have cascading effects based on relationships.
        """
        if not self.config.is_event_cascading_enabled():
            return 0.0
        
        # Get base cascade probability from configuration
        base_cascade = self.config.get_cascade_probability(source_event, target_event)
        
        if base_cascade == 0.0:
            return 0.0
        
        # Scale cascade probability by current chaos level
        chaos_factor = min(2.0, 1.0 + current_chaos)  # Higher chaos = more cascades
        
        # Apply random variation to prevent predictable cascades
        variation = random.uniform(0.8, 1.2)
        
        final_probability = base_cascade * chaos_factor * variation
        
        return min(0.8, max(0.0, final_probability))  # Cap at 80% cascade chance
    
    def calculate_mitigation_effectiveness(self, mitigation_type: str, base_effectiveness: float, 
                                         time_active_hours: float) -> float:
        """
        Calculate current mitigation effectiveness with time-based decay.
        
        Bible specifies mitigation should reduce pressure over time.
        """
        if not self.config.is_mitigation_calculation_enabled():
            return 0.0
        
        # Different mitigation types have different decay rates
        decay_rates = {
            'diplomatic': 0.01,    # Slow decay - diplomatic solutions last
            'economic': 0.02,      # Medium decay - economic effects fade  
            'religious': 0.005,    # Very slow decay - faith is persistent
            'magical': 0.03        # Fast decay - magic is temporary
        }
        
        decay_rate = decay_rates.get(mitigation_type, 0.02)
        
        # Calculate effectiveness with exponential decay
        time_factor = math.exp(-decay_rate * time_active_hours)
        current_effectiveness = base_effectiveness * time_factor
        
        return max(0.0, current_effectiveness)
    
    def predict_chaos_trajectory(self, current_pressure: PressureData, hours_ahead: int = 24) -> List[float]:
        """
        Predict chaos score trajectory over the next N hours.
        
        Uses current pressure trends and applies Bible pressure decay rates.
        """
        trajectory = []
        current_score = self.calculate_chaos_score(current_pressure).chaos_score
        
        # Simple linear prediction based on pressure decay
        decay_rate = self.config.pressure_decay_rate
        
        for hour in range(hours_ahead):
            # Apply pressure decay
            predicted_pressure = current_score * (1.0 - decay_rate * hour)
            
            # Add some random variation for realism
            variation = random.uniform(-0.05, 0.05)
            predicted_score = max(0.0, min(1.0, predicted_pressure + variation))
            
            trajectory.append(predicted_score)
        
        return trajectory
    
    def calculate_pressure_momentum(self, pressure_history: List[Tuple[datetime, float]]) -> float:
        """
        Calculate pressure momentum (consistency of direction) over time.
        
        Positive momentum = consistently increasing pressure
        Negative momentum = consistently decreasing pressure
        """
        if len(pressure_history) < 3:
            return 0.0
        
        # Sort by timestamp
        sorted_history = sorted(pressure_history, key=lambda x: x[0])
        values = [entry[1] for entry in sorted_history]
        
        # Calculate differences between consecutive readings
        differences = []
        for i in range(1, len(values)):
            diff = values[i] - values[i-1]
            differences.append(diff)
        
        if not differences:
            return 0.0
        
        # Calculate momentum as consistency of direction
        positive_changes = sum(1 for d in differences if d > 0)
        negative_changes = sum(1 for d in differences if d < 0)
        total_changes = len(differences)
        
        if positive_changes > negative_changes:
            momentum = positive_changes / total_changes
        else:
            momentum = -(negative_changes / total_changes)
        
        return momentum
    
    def normalize_pressure_value(self, pressure_value: float) -> float:
        """Normalize pressure value to Bible bounds (0.0 - 1.0)"""
        return max(0.0, min(1.0, float(pressure_value)))
    
    def aggregate_regional_pressure(self, regional_pressures: Dict[str, float], 
                                   regional_weights: Optional[Dict[str, float]] = None) -> float:
        """
        Aggregate pressure from multiple regions using optional weights.
        
        Used for calculating global pressure from regional data.
        """
        if not regional_pressures:
            return 0.0
        
        if regional_weights is None:
            # Equal weighting if no weights provided
            return sum(regional_pressures.values()) / len(regional_pressures)
        
        total_weighted = 0.0
        total_weight = 0.0
        
        for region_id, pressure in regional_pressures.items():
            weight = regional_weights.get(region_id, 1.0)
            total_weighted += pressure * weight
            total_weight += weight
        
        if total_weight > 0:
            return total_weighted / total_weight
        return 0.0 
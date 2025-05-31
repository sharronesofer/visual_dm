"""
Chaos Calculator - Weighted chaos calculation from multiple system inputs
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import math

from backend.systems.chaos.models.pressure_data import PressureData
from backend.systems.chaos.core.config import ChaosConfig

@dataclass
class ChaosCalculationResult:
    """Result of chaos score calculation"""
    chaos_score: float
    pressure_sources: Dict[str, float]
    weighted_factors: Dict[str, float]
    threshold_exceeded: bool
    recommended_events: List[str]
    mitigation_factors: Dict[str, float]

class ChaosCalculator:
    """Calculates composite chaos scores using multiple input metrics"""
    
    def __init__(self, config: ChaosConfig):
        self.config = config
        self.pressure_weights = {
            'economic': 1.2,
            'social': 1.0,
            'political': 1.5,
            'environmental': 0.8,
            'motif': 1.3,
            'faction_tension': 1.4,
            'military': 1.1
        }
    
    def calculate_weighted_chaos(self, pressure_data: PressureData, 
                                region_id: Optional[str] = None) -> ChaosCalculationResult:
        """Calculate composite chaos score with configurable weighting"""
        
        pressure_sources = {}
        weighted_factors = {}
        total_weighted_score = 0.0
        total_weight = 0.0
        
        # Process each pressure source
        for source, value in pressure_data.pressure_sources.items():
            weight = self.pressure_weights.get(source, 1.0)
            weighted_value = value * weight
            
            pressure_sources[source] = value
            weighted_factors[source] = weighted_value
            total_weighted_score += weighted_value
            total_weight += weight
        
        # Calculate normalized chaos score
        chaos_score = total_weighted_score / max(total_weight, 1.0) if total_weight > 0 else 0.0
        
        # Apply temporal factors
        chaos_score = self._apply_temporal_factors(chaos_score, pressure_data)
        
        # Apply regional factors
        if region_id:
            chaos_score = self._apply_regional_factors(chaos_score, region_id)
        
        # Check threshold
        threshold_exceeded = chaos_score >= self.config.chaos_threshold
        
        # Recommend events based on pressure composition
        recommended_events = self._recommend_events(pressure_sources, chaos_score)
        
        # Calculate mitigation factors
        mitigation_factors = self._calculate_mitigation_factors(pressure_data)
        
        return ChaosCalculationResult(
            chaos_score=chaos_score,
            pressure_sources=pressure_sources,
            weighted_factors=weighted_factors,
            threshold_exceeded=threshold_exceeded,
            recommended_events=recommended_events,
            mitigation_factors=mitigation_factors
        )
    
    def _apply_temporal_factors(self, base_score: float, pressure_data: PressureData) -> float:
        """Apply time-based chaos amplification"""
        # Pressure buildup over time increases chaos potential
        if hasattr(pressure_data, 'pressure_duration'):
            duration_factor = min(pressure_data.pressure_duration / 24.0, 2.0)  # Max 2x multiplier over 24 hours
            return base_score * (1.0 + duration_factor * 0.5)
        
        return base_score
    
    def _apply_regional_factors(self, base_score: float, region_id: str) -> float:
        """Apply region-specific chaos modifiers"""
        # Different regions have different chaos susceptibility
        regional_modifiers = {
            'capital': 1.3,      # High-stakes political center
            'frontier': 0.8,     # More resilient to chaos
            'trade_hub': 1.1,    # Economic volatility
            'wilderness': 0.6,   # Isolated from most chaos sources
        }
        
        # Simple region type detection based on region_id
        for region_type, modifier in regional_modifiers.items():
            if region_type in region_id.lower():
                return base_score * modifier
        
        return base_score
    
    def _recommend_events(self, pressure_sources: Dict[str, float], 
                         chaos_score: float) -> List[str]:
        """Recommend chaos events based on pressure composition"""
        recommendations = []
        
        # Determine dominant pressure source
        dominant_source = max(pressure_sources.items(), key=lambda x: x[1])
        
        event_recommendations = {
            'economic': ['market_crash', 'resource_shortage', 'trade_disruption'],
            'political': ['leadership_crisis', 'succession_dispute', 'diplomatic_breakdown'],
            'social': ['population_unrest', 'mass_migration', 'cultural_conflict'],
            'environmental': ['natural_disaster', 'climate_anomaly', 'magical_disturbance'],
            'faction_tension': ['faction_war', 'betrayal', 'alliance_collapse'],
            'motif': ['prophecy_corruption', 'divine_omen', 'artifact_activation']
        }
        
        if dominant_source[1] > 0.6:  # High pressure in dominant source
            source_events = event_recommendations.get(dominant_source[0], [])
            recommendations.extend(source_events[:2])  # Top 2 events for dominant source
        
        # Add severity-based events
        if chaos_score > 0.8:
            recommendations.extend(['assassination', 'catastrophic_failure'])
        elif chaos_score > 0.6:
            recommendations.extend(['major_incident', 'system_breakdown'])
        
        return recommendations[:5]  # Limit to top 5 recommendations
    
    def _calculate_mitigation_factors(self, pressure_data: PressureData) -> Dict[str, float]:
        """Calculate factors that could reduce chaos pressure"""
        mitigation = {}
        
        # Diplomatic mitigation
        if hasattr(pressure_data, 'diplomatic_stability'):
            mitigation['diplomatic'] = pressure_data.diplomatic_stability * 0.3
        
        # Economic mitigation (strong economy reduces chaos)
        if hasattr(pressure_data, 'economic_health'):
            mitigation['economic'] = pressure_data.economic_health * 0.25
        
        # Infrastructure mitigation
        if hasattr(pressure_data, 'infrastructure_quality'):
            mitigation['infrastructure'] = pressure_data.infrastructure_quality * 0.2
        
        # Leadership mitigation
        if hasattr(pressure_data, 'leadership_stability'):
            mitigation['leadership'] = pressure_data.leadership_stability * 0.35
        
        return mitigation
        
    def update_pressure_weights(self, new_weights: Dict[str, float]):
        """Update pressure source weights for chaos calculation"""
        self.pressure_weights.update(new_weights)
        
    def get_chaos_breakdown(self, result: ChaosCalculationResult) -> Dict[str, Any]:
        """Get detailed breakdown of chaos calculation"""
        return {
            'total_score': result.chaos_score,
            'pressure_breakdown': result.pressure_sources,
            'weighted_breakdown': result.weighted_factors,
            'weights_used': self.pressure_weights,
            'threshold_status': 'EXCEEDED' if result.threshold_exceeded else 'NORMAL',
            'recommended_actions': result.recommended_events,
            'mitigation_available': result.mitigation_factors
        }
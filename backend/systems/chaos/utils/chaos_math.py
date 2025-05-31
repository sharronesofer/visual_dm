"""
Chaos Math

Mathematical algorithms for chaos score calculation, weighting, and scaling.
This is the mathematical heart of the chaos system.
"""

import math
import random
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
from dataclasses import dataclass

from backend.systems.chaos.models.pressure_data import (
    PressureData, PressureSource, RegionalPressure, GlobalPressure
)
from backend.systems.chaos.core.config import ChaosLevel, ChaosConfig

@dataclass
class ChaosCalculationResult:
    """Result of chaos calculation with detailed breakdown"""
    chaos_score: float  # Final weighted chaos score (0.0 to 1.0)
    chaos_level: ChaosLevel  # Corresponding chaos level
    regional_scores: Dict[str, float] = None  # Scores by region
    source_contributions: Dict[PressureSource, float] = None  # Contributions by pressure source
    temporal_factors: Dict[str, float] = None  # Temporal adjustments applied
    calculation_metadata: Dict[str, Any] = None  # Additional calculation details

class ChaosMath:
    """
    Core mathematical algorithms for chaos calculation.
    
    This class implements:
    - Weighted chaos score calculation from multiple pressure sources
    - Temporal factor integration (pressure buildup over time)
    - Regional vs global chaos aggregation
    - Chaos level determination and scaling
    - Mathematical models for chaos propagation and decay
    """
    
    def __init__(self, config: ChaosConfig):
        self.config = config
        self._calculation_cache = {}
        self._cache_ttl = 30.0  # Cache calculations for 30 seconds
    
    def calculate_chaos_score(self, pressure_data: PressureData) -> ChaosCalculationResult:
        """
        Calculate weighted chaos score from pressure data.
        
        This is the main chaos calculation algorithm that:
        - Aggregates pressure from all sources with configured weights
        - Applies temporal factors for pressure buildup over time
        - Calculates regional and global chaos scores
        - Determines appropriate chaos level
        """
        # Check cache first
        cache_key = self._generate_cache_key(pressure_data)
        cached_result = self._get_cached_result(cache_key)
        if cached_result:
            return cached_result
        
        # Get pressure source weights
        weights = self._get_pressure_weights()
        
        # Calculate regional chaos scores
        regional_scores = self._calculate_regional_chaos_scores(
            pressure_data.global_pressure.regional_pressures, weights
        )
        
        # Calculate global chaos score
        global_score = self._calculate_global_chaos_score(
            pressure_data.global_pressure, regional_scores, weights
        )
        
        # Apply temporal factors
        temporal_factors = self._calculate_temporal_factors(pressure_data.global_pressure)
        adjusted_score = self._apply_temporal_factors(global_score, temporal_factors)
        
        # Apply chaos momentum and decay
        momentum_adjusted_score = self._apply_chaos_momentum(
            adjusted_score, pressure_data.global_pressure
        )
        
        # Final chaos score with bounds checking
        final_score = max(0.0, min(1.0, momentum_adjusted_score))
        
        # Determine chaos level
        chaos_level = self._determine_chaos_level(final_score)
        
        # Calculate source contributions for analysis
        source_contributions = self._calculate_source_contributions(
            pressure_data.global_pressure, weights
        )
        
        # Create result
        result = ChaosCalculationResult(
            chaos_score=final_score,
            chaos_level=chaos_level,
            regional_scores=regional_scores,
            source_contributions=source_contributions,
            temporal_factors=temporal_factors,
            calculation_metadata={
                'raw_global_score': global_score,
                'temporal_adjusted_score': adjusted_score,
                'momentum_adjusted_score': momentum_adjusted_score,
                'calculation_timestamp': datetime.now().isoformat(),
                'pressure_history_length': len(pressure_data.global_pressure.pressure_history)
            }
        )
        
        # Cache result
        self._cache_result(cache_key, result)
        
        return result
    
    def _get_pressure_weights(self) -> Dict[PressureSource, float]:
        """Get normalized pressure source weights from config"""
        weights = {
            PressureSource.FACTION_CONFLICT: self.config.faction_conflict_weight,
            PressureSource.ECONOMIC_INSTABILITY: self.config.economic_instability_weight,
            PressureSource.POPULATION_STRESS: self.config.population_stress_weight,
            PressureSource.DIPLOMATIC_TENSION: self.config.diplomatic_tension_weight,
            PressureSource.MILITARY_BUILDUP: self.config.military_buildup_weight,
            PressureSource.ENVIRONMENTAL_PRESSURE: self.config.environmental_pressure_weight,
        }
        
        # Normalize weights to sum to 1.0
        total_weight = sum(weights.values())
        if total_weight > 0:
            weights = {source: weight / total_weight for source, weight in weights.items()}
        
        return weights
    
    def _calculate_regional_chaos_scores(self, 
                                       regional_pressures: Dict[str, RegionalPressure],
                                       weights: Dict[PressureSource, float]) -> Dict[str, float]:
        """Calculate chaos scores for each region"""
        regional_scores = {}
        
        for region_id, regional_pressure in regional_pressures.items():
            # Calculate base regional score
            base_score = self._calculate_base_regional_score(regional_pressure, weights)
            
            # Apply regional modifiers
            regional_modifier = regional_pressure.calculate_regional_modifier()
            modified_score = base_score * regional_modifier
            
            # Apply regional chaos propagation from neighboring regions
            propagation_score = self._calculate_regional_propagation(
                region_id, regional_pressures, weights
            )
            
            # Combine base score with propagation
            final_regional_score = self._combine_scores(
                modified_score, propagation_score, 
                base_weight=0.7, propagation_weight=0.3
            )
            
            regional_scores[str(region_id)] = max(0.0, min(1.0, final_regional_score))
        
        return regional_scores
    
    def _calculate_base_regional_score(self, 
                                     regional_pressure: RegionalPressure,
                                     weights: Dict[PressureSource, float]) -> float:
        """Calculate base chaos score for a single region"""
        if not regional_pressure.pressure_readings:
            return 0.0
        
        # Group readings by source and get most recent for each
        source_pressures = {}
        for reading in regional_pressure.pressure_readings:
            if reading.source not in source_pressures:
                source_pressures[reading.source] = []
            source_pressures[reading.source].append(reading)
        
        # Calculate weighted sum
        weighted_sum = 0.0
        total_weight = 0.0
        
        for source, readings in source_pressures.items():
            if source in weights:
                # Use most recent reading for this source
                latest_reading = max(readings, key=lambda r: r.timestamp)
                pressure_value = latest_reading.value * latest_reading.confidence
                weight = weights[source]
                
                weighted_sum += pressure_value * weight
                total_weight += weight
        
        if total_weight > 0:
            return weighted_sum / total_weight
        else:
            return 0.0
    
    def _calculate_regional_propagation(self,
                                      region_id: str,
                                      regional_pressures: Dict[str, RegionalPressure],
                                      weights: Dict[PressureSource, float]) -> float:
        """Calculate chaos propagation from neighboring regions"""
        # TODO: Implement actual regional connectivity/adjacency
        # For now, use simplified model based on all other regions
        
        other_regions = [rp for rid, rp in regional_pressures.items() if str(rid) != region_id]
        
        if not other_regions:
            return 0.0
        
        # Calculate average pressure from other regions with distance decay
        total_propagated_pressure = 0.0
        total_regions = 0
        
        for other_region in other_regions:
            other_score = self._calculate_base_regional_score(other_region, weights)
            
            # Apply distance decay (simplified - assume all regions have some distance factor)
            distance_factor = 0.3  # TODO: Calculate actual regional distance
            propagated_pressure = other_score * distance_factor
            
            total_propagated_pressure += propagated_pressure
            total_regions += 1
        
        if total_regions > 0:
            return total_propagated_pressure / total_regions
        else:
            return 0.0
    
    def _calculate_global_chaos_score(self,
                                    global_pressure: GlobalPressure,
                                    regional_scores: Dict[str, float],
                                    weights: Dict[PressureSource, float]) -> float:
        """Calculate global chaos score from regional scores and global factors"""
        
        # Regional component - weighted average of regional scores
        if regional_scores:
            regional_component = sum(regional_scores.values()) / len(regional_scores)
        else:
            regional_component = 0.0
        
        # Global factors component
        global_factors = [
            global_pressure.global_economic_health,
            global_pressure.international_stability, 
            global_pressure.climate_stability,
            global_pressure.resource_abundance
        ]
        
        # Convert stability factors to pressure factors (inverse)
        global_pressure_factors = [1.0 - factor for factor in global_factors]
        global_component = sum(global_pressure_factors) / len(global_pressure_factors)
        
        # Combine regional and global components
        regional_weight = self.config.regional_chaos_weight
        global_weight = self.config.global_chaos_weight
        
        # Normalize weights
        total_weight = regional_weight + global_weight
        if total_weight > 0:
            regional_weight /= total_weight
            global_weight /= total_weight
        
        combined_score = (regional_component * regional_weight + 
                         global_component * global_weight)
        
        return combined_score
    
    def _calculate_temporal_factors(self, global_pressure: GlobalPressure) -> Dict[str, float]:
        """Calculate temporal adjustment factors based on pressure history"""
        temporal_factors = {
            'buildup_factor': 1.0,
            'momentum_factor': 1.0,
            'acceleration_factor': 1.0,
            'persistence_factor': 1.0
        }
        
        pressure_history = global_pressure.pressure_history
        
        if len(pressure_history) < 3:
            return temporal_factors
        
        # Pressure buildup factor - how pressure has accumulated over time
        recent_history = pressure_history[-10:]  # Last 10 readings
        if len(recent_history) >= 2:
            avg_recent = sum(recent_history) / len(recent_history)
            avg_all = sum(pressure_history) / len(pressure_history)
            
            if avg_all > 0:
                buildup_ratio = avg_recent / avg_all
                temporal_factors['buildup_factor'] = min(self.config.pressure_buildup_multiplier, 
                                                        1.0 + (buildup_ratio - 1.0) * 0.5)
        
        # Momentum factor - consistency of pressure direction
        if len(pressure_history) >= 5:
            momentum = self._calculate_pressure_momentum(pressure_history)
            temporal_factors['momentum_factor'] = 1.0 + (momentum * self.config.chaos_momentum_factor)
        
        # Acceleration factor - rate of pressure increase
        if len(pressure_history) >= 3:
            recent_readings = pressure_history[-3:]
            if recent_readings[-1] > recent_readings[-3]:  # Pressure increasing
                acceleration = (recent_readings[-1] - recent_readings[-3]) / 2.0
                temporal_factors['acceleration_factor'] = 1.0 + min(0.5, acceleration)
        
        # Persistence factor - how long pressure has been elevated
        threshold = 0.5  # Consider pressure "elevated" above this threshold
        elevated_count = sum(1 for p in recent_history if p >= threshold)
        if len(recent_history) > 0:
            persistence_ratio = elevated_count / len(recent_history)
            temporal_factors['persistence_factor'] = 1.0 + (persistence_ratio * 0.3)
        
        return temporal_factors
    
    def _apply_temporal_factors(self, base_score: float, temporal_factors: Dict[str, float]) -> float:
        """Apply temporal factors to base chaos score"""
        adjusted_score = base_score
        
        # Apply each temporal factor
        for factor_name, factor_value in temporal_factors.items():
            adjusted_score *= factor_value
        
        return adjusted_score
    
    def _apply_chaos_momentum(self, score: float, global_pressure: GlobalPressure) -> float:
        """Apply chaos momentum effect (chaos feeds on itself)"""
        if len(global_pressure.pressure_history) < 2:
            return score
        
        # Chaos momentum - high chaos tends to generate more chaos
        current_chaos_level = score
        momentum_multiplier = 1.0 + (current_chaos_level * self.config.chaos_momentum_factor * 0.1)
        
        return score * momentum_multiplier
    
    def _calculate_pressure_momentum(self, pressure_history: List[float]) -> float:
        """Calculate momentum of pressure changes"""
        if len(pressure_history) < 3:
            return 0.0
        
        # Count consistent directional changes
        direction_consistency = 0
        total_changes = 0
        
        for i in range(1, len(pressure_history) - 1):
            prev_change = pressure_history[i] - pressure_history[i-1]
            next_change = pressure_history[i+1] - pressure_history[i]
            
            # Check if directions are consistent (same sign)
            if prev_change * next_change >= 0:
                direction_consistency += 1
            total_changes += 1
        
        if total_changes > 0:
            return direction_consistency / total_changes
        else:
            return 0.0
    
    def _determine_chaos_level(self, chaos_score: float) -> ChaosLevel:
        """Determine chaos level from chaos score"""
        thresholds = self.config.chaos_thresholds
        
        # Sort thresholds by value
        sorted_levels = sorted(thresholds.items(), key=lambda x: x[1])
        
        # Find appropriate level
        for level, threshold in reversed(sorted_levels):
            if chaos_score >= threshold:
                return level
        
        return ChaosLevel.DORMANT
    
    def _calculate_source_contributions(self,
                                      global_pressure: GlobalPressure,
                                      weights: Dict[PressureSource, float]) -> Dict[PressureSource, float]:
        """Calculate how much each pressure source contributes to total chaos"""
        contributions = {}
        total_weighted_pressure = 0.0
        
        # Aggregate pressure by source across all regions
        source_totals = {}
        for regional_pressure in global_pressure.regional_pressures.values():
            for reading in regional_pressure.pressure_readings:
                if reading.source not in source_totals:
                    source_totals[reading.source] = []
                source_totals[reading.source].append(reading.value * reading.confidence)
        
        # Calculate weighted contributions
        for source, values in source_totals.items():
            if source in weights and values:
                avg_pressure = sum(values) / len(values)
                weighted_contribution = avg_pressure * weights[source]
                contributions[source] = weighted_contribution
                total_weighted_pressure += weighted_contribution
        
        # Normalize contributions to percentages
        if total_weighted_pressure > 0:
            contributions = {
                source: (contribution / total_weighted_pressure) 
                for source, contribution in contributions.items()
            }
        
        return contributions
    
    def _combine_scores(self, score1: float, score2: float, 
                       base_weight: float = 0.5, propagation_weight: float = 0.5) -> float:
        """Combine multiple chaos scores with weights"""
        total_weight = base_weight + propagation_weight
        if total_weight > 0:
            return (score1 * base_weight + score2 * propagation_weight) / total_weight
        else:
            return (score1 + score2) / 2.0
    
    # Decay and stabilization methods
    
    def apply_natural_decay(self, current_score: float, time_delta_seconds: float) -> float:
        """Apply natural chaos decay over time"""
        if time_delta_seconds <= 0:
            return current_score
        
        # Exponential decay
        decay_rate = self.config.pressure_decay_rate
        decay_factor = math.exp(-decay_rate * time_delta_seconds / 3600.0)  # per hour
        
        return current_score * decay_factor
    
    def calculate_chaos_intensity_scaling(self, chaos_level: ChaosLevel, base_intensity: float) -> float:
        """Scale event intensity based on chaos level"""
        level_multipliers = {
            ChaosLevel.DORMANT: 0.0,
            ChaosLevel.LOW: 0.3,
            ChaosLevel.MODERATE: 0.6,
            ChaosLevel.HIGH: 0.8,
            ChaosLevel.EXTREME: 1.0,
            ChaosLevel.CATASTROPHIC: 1.2
        }
        
        multiplier = level_multipliers.get(chaos_level, 1.0)
        return base_intensity * multiplier
    
    def predict_chaos_trajectory(self, pressure_data: PressureData, hours_ahead: int = 24) -> List[float]:
        """Predict chaos score trajectory over time"""
        if len(pressure_data.global_pressure.pressure_history) < 5:
            return []
        
        current_score = pressure_data.global_pressure.weighted_pressure
        current_trend = pressure_data.global_pressure.pressure_trend
        
        trajectory = []
        predicted_score = current_score
        
        for hour in range(hours_ahead):
            # Apply trend
            predicted_score += current_trend
            
            # Apply natural decay
            predicted_score = self.apply_natural_decay(predicted_score, 3600.0)  # 1 hour
            
            # Add some random variation
            variation = random.uniform(-0.02, 0.02)
            predicted_score += variation
            
            # Clamp to valid range
            predicted_score = max(0.0, min(1.0, predicted_score))
            
            trajectory.append(predicted_score)
        
        return trajectory
    
    # Caching methods
    
    def _generate_cache_key(self, pressure_data: PressureData) -> str:
        """Generate cache key for pressure data"""
        # Use hash of last update time and total readings for cache key
        key_data = f"{pressure_data.last_calculation}_{pressure_data.readings_processed}"
        return str(hash(key_data))
    
    def _get_cached_result(self, cache_key: str) -> Optional[ChaosCalculationResult]:
        """Get cached calculation result if still valid"""
        if cache_key in self._calculation_cache:
            cached_time, result = self._calculation_cache[cache_key]
            if (datetime.now() - cached_time).total_seconds() < self._cache_ttl:
                return result
        return None
    
    def _cache_result(self, cache_key: str, result: ChaosCalculationResult) -> None:
        """Cache calculation result"""
        self._calculation_cache[cache_key] = (datetime.now(), result)
        
        # Clean up old cache entries
        current_time = datetime.now()
        keys_to_remove = []
        for key, (cache_time, _) in self._calculation_cache.items():
            if (current_time - cache_time).total_seconds() > self._cache_ttl * 2:
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del self._calculation_cache[key] 
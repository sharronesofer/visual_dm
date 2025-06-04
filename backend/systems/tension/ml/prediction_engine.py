"""
Tension Prediction Engine

Provides predictive analytics for tension system using machine learning:
- Tension escalation prediction based on historical patterns
- Conflict outbreak probability modeling
- Regional stability forecasting
- Player behavior impact prediction

This module contains the business logic for ML-driven predictions.
The actual ML infrastructure (training, model serving) would be handled
by dedicated ML services outside the business logic layer.
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import json

logger = logging.getLogger(__name__)


class PredictionConfidence(Enum):
    """Confidence levels for predictions"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


class TensionTrend(Enum):
    """Predicted tension trends"""
    STABLE = "stable"
    RISING = "rising"
    FALLING = "falling"
    VOLATILE = "volatile"
    CRITICAL = "critical"


@dataclass
class TensionPrediction:
    """Represents a tension prediction for a specific location and timeframe"""
    region_id: str
    poi_id: str
    current_tension: float
    predicted_tension: float
    prediction_horizon_hours: int
    confidence: PredictionConfidence
    trend: TensionTrend
    contributing_factors: List[str]
    probability_thresholds: Dict[str, float]  # e.g., {'conflict': 0.3, 'violence': 0.15}
    timestamp: datetime


@dataclass
class ConflictOutbreakPrediction:
    """Predicts likelihood of conflict outbreak"""
    region_id: str
    outbreak_probability: float
    severity_estimate: float
    estimated_timeframe: Optional[timedelta]
    triggering_factors: List[str]
    confidence: PredictionConfidence
    recommended_interventions: List[str]


class TensionPredictionEngine:
    """Core engine for ML-driven tension predictions"""
    
    def __init__(self):
        self.prediction_cache: Dict[str, TensionPrediction] = {}
        self.historical_accuracy: Dict[str, float] = {}
        self.model_weights: Dict[str, float] = self._initialize_default_weights()
        
        # Prediction parameters
        self.max_prediction_horizon = 72  # hours
        self.confidence_threshold = 0.7
        self.trend_sensitivity = 0.1
        
    def _initialize_default_weights(self) -> Dict[str, float]:
        """Initialize default model weights for prediction factors"""
        return {
            'historical_tension': 0.3,
            'recent_events': 0.25,
            'player_actions': 0.2,
            'faction_relationships': 0.15,
            'economic_factors': 0.1,
            'seasonal_patterns': 0.05,
            'external_events': 0.05
        }
    
    def predict_tension_escalation(self, region_id: str, poi_id: str, 
                                 hours_ahead: int = 24) -> TensionPrediction:
        """Predict tension escalation for a specific location"""
        try:
            # Validate prediction horizon
            if hours_ahead > self.max_prediction_horizon:
                hours_ahead = self.max_prediction_horizon
            
            # Get current tension and historical data
            current_tension = self._get_current_tension(region_id, poi_id)
            historical_data = self._get_historical_tension_data(region_id, poi_id)
            
            # Analyze contributing factors
            factors = self._analyze_contributing_factors(region_id, poi_id)
            
            # Calculate prediction using weighted factors
            predicted_tension = self._calculate_tension_prediction(
                current_tension, historical_data, factors, hours_ahead
            )
            
            # Determine confidence and trend
            confidence = self._calculate_prediction_confidence(factors, historical_data)
            trend = self._determine_tension_trend(current_tension, predicted_tension, factors)
            
            # Calculate probability thresholds
            thresholds = self._calculate_probability_thresholds(predicted_tension, factors)
            
            prediction = TensionPrediction(
                region_id=region_id,
                poi_id=poi_id,
                current_tension=current_tension,
                predicted_tension=predicted_tension,
                prediction_horizon_hours=hours_ahead,
                confidence=confidence,
                trend=trend,
                contributing_factors=factors['significant_factors'],
                probability_thresholds=thresholds,
                timestamp=datetime.utcnow()
            )
            
            # Cache prediction
            cache_key = f"{region_id}:{poi_id}:{hours_ahead}"
            self.prediction_cache[cache_key] = prediction
            
            logger.info(f"Generated tension prediction for {region_id}/{poi_id}: "
                       f"{current_tension:.3f} -> {predicted_tension:.3f} ({confidence.value})")
            
            return prediction
            
        except Exception as e:
            logger.error(f"Error predicting tension escalation: {e}")
            # Return fallback prediction
            return self._create_fallback_prediction(region_id, poi_id, hours_ahead)
    
    def predict_conflict_outbreak(self, region_id: str) -> ConflictOutbreakPrediction:
        """Predict likelihood of conflict outbreak in a region"""
        try:
            # Get regional tension data
            regional_data = self._get_regional_tension_data(region_id)
            
            # Analyze conflict risk factors
            risk_factors = self._analyze_conflict_risk_factors(region_id)
            
            # Calculate outbreak probability
            outbreak_probability = self._calculate_outbreak_probability(regional_data, risk_factors)
            
            # Estimate severity and timeframe
            severity = self._estimate_conflict_severity(outbreak_probability, risk_factors)
            timeframe = self._estimate_conflict_timeframe(outbreak_probability, risk_factors)
            
            # Determine confidence
            confidence = self._calculate_outbreak_confidence(risk_factors)
            
            # Generate intervention recommendations
            interventions = self._recommend_interventions(outbreak_probability, risk_factors)
            
            prediction = ConflictOutbreakPrediction(
                region_id=region_id,
                outbreak_probability=outbreak_probability,
                severity_estimate=severity,
                estimated_timeframe=timeframe,
                triggering_factors=risk_factors['high_risk_factors'],
                confidence=confidence,
                recommended_interventions=interventions
            )
            
            logger.info(f"Conflict outbreak prediction for {region_id}: "
                       f"{outbreak_probability:.1%} probability, severity {severity:.2f}")
            
            return prediction
            
        except Exception as e:
            logger.error(f"Error predicting conflict outbreak: {e}")
            return self._create_fallback_outbreak_prediction(region_id)
    
    def get_regional_stability_forecast(self, region_id: str, 
                                      days_ahead: int = 7) -> Dict[str, Any]:
        """Generate comprehensive stability forecast for a region"""
        try:
            forecasts = []
            
            # Generate daily forecasts
            for day in range(1, days_ahead + 1):
                hours_ahead = day * 24
                
                # Get predictions for major POIs in region
                poi_predictions = []
                major_pois = self._get_major_pois_in_region(region_id)
                
                for poi_id in major_pois:
                    prediction = self.predict_tension_escalation(region_id, poi_id, hours_ahead)
                    poi_predictions.append({
                        'poi_id': poi_id,
                        'predicted_tension': prediction.predicted_tension,
                        'trend': prediction.trend.value,
                        'confidence': prediction.confidence.value
                    })
                
                # Calculate regional stability metrics
                avg_tension = sum(p['predicted_tension'] for p in poi_predictions) / len(poi_predictions)
                stability_score = self._calculate_stability_score(poi_predictions)
                
                forecasts.append({
                    'day': day,
                    'average_tension': avg_tension,
                    'stability_score': stability_score,
                    'poi_predictions': poi_predictions,
                    'regional_trend': self._determine_regional_trend(poi_predictions)
                })
            
            # Generate overall assessment
            overall_assessment = self._assess_regional_outlook(forecasts)
            
            return {
                'region_id': region_id,
                'forecast_days': days_ahead,
                'daily_forecasts': forecasts,
                'overall_assessment': overall_assessment,
                'generated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating stability forecast: {e}")
            return {'error': str(e)}
    
    def analyze_player_impact_prediction(self, player_id: str, region_id: str, 
                                       action_type: str) -> Dict[str, Any]:
        """Predict how player actions will impact regional tension"""
        try:
            # Get player behavioral patterns
            player_patterns = self._get_player_behavior_patterns(player_id)
            
            # Analyze historical impact of similar actions
            historical_impact = self._analyze_historical_action_impact(action_type, region_id)
            
            # Factor in player-specific modifiers
            player_modifier = self._calculate_player_impact_modifier(player_patterns, action_type)
            
            # Predict tension change
            predicted_change = historical_impact['average_change'] * player_modifier
            confidence = self._calculate_impact_confidence(historical_impact, player_patterns)
            
            # Estimate secondary effects
            secondary_effects = self._predict_secondary_effects(action_type, predicted_change, region_id)
            
            return {
                'player_id': player_id,
                'action_type': action_type,
                'predicted_tension_change': predicted_change,
                'confidence': confidence.value,
                'secondary_effects': secondary_effects,
                'player_impact_modifier': player_modifier,
                'historical_precedent': historical_impact
            }
            
        except Exception as e:
            logger.error(f"Error predicting player impact: {e}")
            return {'error': str(e)}
    
    def update_prediction_accuracy(self, prediction_id: str, actual_outcome: float) -> None:
        """Update prediction accuracy metrics based on actual outcomes"""
        try:
            # This would typically involve updating ML model weights
            # For now, tracking accuracy in a simple format
            
            prediction_key = prediction_id
            if prediction_key in self.prediction_cache:
                prediction = self.prediction_cache[prediction_key]
                predicted_value = prediction.predicted_tension
                
                # Calculate accuracy
                accuracy = 1.0 - abs(predicted_value - actual_outcome)
                
                # Update historical accuracy
                region_key = f"{prediction.region_id}:{prediction.poi_id}"
                if region_key not in self.historical_accuracy:
                    self.historical_accuracy[region_key] = []
                
                self.historical_accuracy[region_key].append(accuracy)
                
                # Keep only recent accuracy data (last 100 predictions)
                if len(self.historical_accuracy[region_key]) > 100:
                    self.historical_accuracy[region_key] = self.historical_accuracy[region_key][-100:]
                
                logger.info(f"Updated prediction accuracy for {region_key}: {accuracy:.3f}")
            
        except Exception as e:
            logger.error(f"Error updating prediction accuracy: {e}")
    
    def _get_current_tension(self, region_id: str, poi_id: str) -> float:
        """Get current tension level (placeholder - would integrate with tension manager)"""
        # This would integrate with the actual tension manager
        return 0.5  # Placeholder
    
    def _get_historical_tension_data(self, region_id: str, poi_id: str) -> Dict[str, Any]:
        """Get historical tension data for analysis"""
        # This would query historical data storage
        return {
            'daily_averages': [0.3, 0.4, 0.5, 0.6, 0.5],
            'trend_slope': 0.05,
            'volatility': 0.15,
            'peak_periods': ['2024-01-15', '2024-01-22']
        }
    
    def _analyze_contributing_factors(self, region_id: str, poi_id: str) -> Dict[str, Any]:
        """Analyze factors contributing to tension changes"""
        return {
            'recent_events': ['faction_dispute', 'economic_downturn'],
            'player_actions': ['combat_nearby', 'quest_completion'],
            'seasonal_factors': ['winter_hardship'],
            'significant_factors': ['faction_dispute', 'economic_downturn'],
            'factor_weights': {
                'faction_dispute': 0.4,
                'economic_downturn': 0.3,
                'combat_nearby': 0.2,
                'winter_hardship': 0.1
            }
        }
    
    def _calculate_tension_prediction(self, current: float, historical: Dict[str, Any], 
                                    factors: Dict[str, Any], hours_ahead: int) -> float:
        """Calculate predicted tension using weighted factors"""
        # Simple prediction algorithm (would be replaced with actual ML model)
        base_prediction = current + (historical['trend_slope'] * hours_ahead / 24)
        
        # Apply factor weights
        factor_adjustment = 0.0
        for factor, weight in factors['factor_weights'].items():
            if factor in factors['recent_events'] or factor in factors['player_actions']:
                factor_adjustment += weight * 0.1  # Each factor adds 10% of its weight
        
        predicted = base_prediction + factor_adjustment
        return max(0.0, min(1.0, predicted))  # Clamp to [0, 1]
    
    def _calculate_prediction_confidence(self, factors: Dict[str, Any], 
                                       historical: Dict[str, Any]) -> PredictionConfidence:
        """Calculate confidence level for prediction"""
        # Simple confidence calculation
        data_quality = 0.8  # Would be based on actual data completeness
        factor_certainty = len(factors['significant_factors']) / 5.0  # More factors = more certain
        historical_stability = 1.0 - historical['volatility']
        
        confidence_score = (data_quality + factor_certainty + historical_stability) / 3.0
        
        if confidence_score >= 0.8:
            return PredictionConfidence.VERY_HIGH
        elif confidence_score >= 0.6:
            return PredictionConfidence.HIGH
        elif confidence_score >= 0.4:
            return PredictionConfidence.MEDIUM
        else:
            return PredictionConfidence.LOW
    
    def _determine_tension_trend(self, current: float, predicted: float, 
                               factors: Dict[str, Any]) -> TensionTrend:
        """Determine the overall tension trend"""
        change = predicted - current
        
        if abs(change) < self.trend_sensitivity:
            return TensionTrend.STABLE
        elif change > 0.3:
            return TensionTrend.CRITICAL
        elif change > 0.1:
            return TensionTrend.RISING
        elif change < -0.1:
            return TensionTrend.FALLING
        else:
            # Check volatility
            if factors.get('factor_weights', {}).get('volatility', 0) > 0.3:
                return TensionTrend.VOLATILE
            return TensionTrend.STABLE
    
    def _calculate_probability_thresholds(self, predicted_tension: float, 
                                        factors: Dict[str, Any]) -> Dict[str, float]:
        """Calculate probability thresholds for various outcomes"""
        base_conflict_prob = min(0.8, predicted_tension * 0.7)
        base_violence_prob = min(0.6, predicted_tension * 0.5)
        
        # Adjust based on factors
        if 'faction_dispute' in factors.get('recent_events', []):
            base_conflict_prob *= 1.5
            base_violence_prob *= 1.3
        
        return {
            'conflict': min(1.0, base_conflict_prob),
            'violence': min(1.0, base_violence_prob),
            'mass_exodus': min(1.0, predicted_tension * 0.3),
            'economic_disruption': min(1.0, predicted_tension * 0.6)
        }
    
    def _create_fallback_prediction(self, region_id: str, poi_id: str, 
                                  hours_ahead: int) -> TensionPrediction:
        """Create fallback prediction when normal prediction fails"""
        current_tension = self._get_current_tension(region_id, poi_id)
        
        return TensionPrediction(
            region_id=region_id,
            poi_id=poi_id,
            current_tension=current_tension,
            predicted_tension=current_tension,  # Assume no change
            prediction_horizon_hours=hours_ahead,
            confidence=PredictionConfidence.LOW,
            trend=TensionTrend.STABLE,
            contributing_factors=['insufficient_data'],
            probability_thresholds={'conflict': 0.1, 'violence': 0.05},
            timestamp=datetime.utcnow()
        )
    
    # Additional helper methods for conflict prediction and analysis...
    
    def _get_regional_tension_data(self, region_id: str) -> Dict[str, Any]:
        """Get comprehensive regional tension data"""
        return {'average_tension': 0.4, 'hotspots': ['market', 'tavern']}
    
    def _analyze_conflict_risk_factors(self, region_id: str) -> Dict[str, Any]:
        """Analyze factors that increase conflict risk"""
        return {
            'high_risk_factors': ['faction_tension', 'resource_scarcity'],
            'risk_scores': {'faction_tension': 0.8, 'resource_scarcity': 0.6}
        }
    
    def _calculate_outbreak_probability(self, regional_data: Dict[str, Any], 
                                      risk_factors: Dict[str, Any]) -> float:
        """Calculate probability of conflict outbreak"""
        base_prob = regional_data['average_tension'] * 0.5
        risk_modifier = sum(risk_factors['risk_scores'].values()) / len(risk_factors['risk_scores'])
        return min(1.0, base_prob * (1 + risk_modifier))
    
    def _estimate_conflict_severity(self, probability: float, risk_factors: Dict[str, Any]) -> float:
        """Estimate severity of potential conflict"""
        return min(2.0, probability * 1.5)
    
    def _estimate_conflict_timeframe(self, probability: float, 
                                   risk_factors: Dict[str, Any]) -> Optional[timedelta]:
        """Estimate when conflict might occur"""
        if probability > 0.7:
            return timedelta(hours=24)
        elif probability > 0.4:
            return timedelta(days=3)
        elif probability > 0.2:
            return timedelta(weeks=1)
        return None
    
    def _calculate_outbreak_confidence(self, risk_factors: Dict[str, Any]) -> PredictionConfidence:
        """Calculate confidence in outbreak prediction"""
        avg_certainty = sum(risk_factors['risk_scores'].values()) / len(risk_factors['risk_scores'])
        
        if avg_certainty >= 0.8:
            return PredictionConfidence.VERY_HIGH
        elif avg_certainty >= 0.6:
            return PredictionConfidence.HIGH
        elif avg_certainty >= 0.4:
            return PredictionConfidence.MEDIUM
        else:
            return PredictionConfidence.LOW
    
    def _recommend_interventions(self, probability: float, 
                               risk_factors: Dict[str, Any]) -> List[str]:
        """Recommend interventions to prevent conflict"""
        interventions = []
        
        if probability > 0.7:
            interventions.extend(['immediate_mediation', 'security_deployment'])
        elif probability > 0.4:
            interventions.extend(['diplomatic_outreach', 'resource_distribution'])
        else:
            interventions.extend(['monitoring_increase', 'community_engagement'])
        
        return interventions
    
    def _create_fallback_outbreak_prediction(self, region_id: str) -> ConflictOutbreakPrediction:
        """Create fallback outbreak prediction"""
        return ConflictOutbreakPrediction(
            region_id=region_id,
            outbreak_probability=0.1,
            severity_estimate=0.5,
            estimated_timeframe=None,
            triggering_factors=['unknown'],
            confidence=PredictionConfidence.LOW,
            recommended_interventions=['data_collection']
        )
    
    def _get_major_pois_in_region(self, region_id: str) -> List[str]:
        """Get major POIs in region"""
        return ['market', 'tavern', 'guard_post', 'temple']  # Placeholder
    
    def _calculate_stability_score(self, poi_predictions: List[Dict[str, Any]]) -> float:
        """Calculate overall stability score for region"""
        total_tension = sum(p['predicted_tension'] for p in poi_predictions)
        avg_tension = total_tension / len(poi_predictions)
        return max(0.0, 1.0 - avg_tension)  # Higher stability = lower average tension
    
    def _determine_regional_trend(self, poi_predictions: List[Dict[str, Any]]) -> str:
        """Determine overall regional trend"""
        rising_count = sum(1 for p in poi_predictions if p['trend'] in ['rising', 'critical'])
        falling_count = sum(1 for p in poi_predictions if p['trend'] == 'falling')
        
        if rising_count > falling_count:
            return 'deteriorating'
        elif falling_count > rising_count:
            return 'improving'
        else:
            return 'stable'
    
    def _assess_regional_outlook(self, forecasts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Assess overall regional outlook"""
        final_stability = forecasts[-1]['stability_score']
        initial_stability = forecasts[0]['stability_score']
        
        outlook = 'stable'
        if final_stability < initial_stability - 0.2:
            outlook = 'deteriorating'
        elif final_stability > initial_stability + 0.2:
            outlook = 'improving'
        
        return {
            'outlook': outlook,
            'confidence': 'medium',
            'key_concerns': ['faction_tensions'] if final_stability < 0.5 else [],
            'stability_trend': final_stability - initial_stability
        }
    
    def _get_player_behavior_patterns(self, player_id: str) -> Dict[str, Any]:
        """Get player behavioral patterns"""
        return {
            'aggression_tendency': 0.3,
            'diplomatic_preference': 0.7,
            'conflict_escalation_rate': 0.2
        }
    
    def _analyze_historical_action_impact(self, action_type: str, region_id: str) -> Dict[str, Any]:
        """Analyze historical impact of action types"""
        return {
            'average_change': 0.1,
            'variance': 0.05,
            'sample_size': 50
        }
    
    def _calculate_player_impact_modifier(self, patterns: Dict[str, Any], 
                                        action_type: str) -> float:
        """Calculate player-specific impact modifier"""
        base_modifier = 1.0
        
        if action_type == 'combat':
            base_modifier *= (1 + patterns['aggression_tendency'])
        elif action_type == 'diplomacy':
            base_modifier *= (1 + patterns['diplomatic_preference'])
        
        return base_modifier
    
    def _calculate_impact_confidence(self, historical: Dict[str, Any], 
                                   patterns: Dict[str, Any]) -> PredictionConfidence:
        """Calculate confidence in impact prediction"""
        if historical['sample_size'] > 30 and historical['variance'] < 0.1:
            return PredictionConfidence.HIGH
        elif historical['sample_size'] > 10:
            return PredictionConfidence.MEDIUM
        else:
            return PredictionConfidence.LOW
    
    def _predict_secondary_effects(self, action_type: str, primary_change: float, 
                                 region_id: str) -> List[Dict[str, Any]]:
        """Predict secondary effects of actions"""
        effects = []
        
        if abs(primary_change) > 0.2:
            effects.append({
                'type': 'npc_behavior_change',
                'magnitude': abs(primary_change) * 0.5,
                'description': 'NPCs will react to tension change'
            })
        
        if primary_change > 0.3:
            effects.append({
                'type': 'quest_generation',
                'probability': min(1.0, primary_change * 0.8),
                'description': 'High tension may trigger conflict resolution quests'
            })
        
        return effects
    
    def get_prediction_status(self) -> Dict[str, Any]:
        """Get status of prediction engine"""
        return {
            'cached_predictions': len(self.prediction_cache),
            'tracked_regions': len(self.historical_accuracy),
            'average_accuracy': sum(
                sum(accuracies) / len(accuracies) 
                for accuracies in self.historical_accuracy.values()
            ) / max(1, len(self.historical_accuracy)),
            'model_weights': self.model_weights,
            'engine_active': True
        } 
"""
Tension Pattern Analyzer

Provides pattern recognition and anomaly detection for tension system:
- Historical pattern analysis and classification
- Anomaly detection in tension behavior
- Player behavior pattern learning
- Regional tension pattern identification
- Cyclic pattern detection (seasonal, daily, etc.)

This module contains the business logic for pattern analysis.
ML infrastructure for model training/inference would be handled separately.
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import statistics

logger = logging.getLogger(__name__)


class PatternType(Enum):
    """Types of patterns that can be detected"""
    CYCLIC = "cyclic"           # Repeating patterns
    TRENDING = "trending"       # Long-term trends
    SPIKE = "spike"            # Sudden changes
    ANOMALY = "anomaly"        # Unusual behavior
    STABLE = "stable"          # Consistent behavior
    VOLATILE = "volatile"       # High variance behavior


class AnomalyType(Enum):
    """Types of anomalies that can be detected"""
    STATISTICAL = "statistical"     # Statistical outliers
    TEMPORAL = "temporal"           # Time-based anomalies
    CONTEXTUAL = "contextual"       # Context-dependent anomalies
    COLLECTIVE = "collective"       # Group behavior anomalies


@dataclass
class PatternDetection:
    """Represents a detected pattern in tension data"""
    pattern_type: PatternType
    region_id: str
    poi_id: Optional[str]
    confidence: float
    description: str
    detected_at: datetime
    pattern_parameters: Dict[str, Any]
    historical_occurrences: int
    predicted_next_occurrence: Optional[datetime]


@dataclass
class AnomalyDetection:
    """Represents an anomaly in tension behavior"""
    anomaly_type: AnomalyType
    region_id: str
    poi_id: Optional[str]
    severity: float  # 0-1 scale
    confidence: float
    description: str
    detected_at: datetime
    deviation_score: float
    contributing_factors: List[str]
    recommended_actions: List[str]


@dataclass
class PlayerBehaviorProfile:
    """Profile of a player's behavior patterns"""
    player_id: str
    behavior_patterns: Dict[str, float]  # Pattern type -> frequency
    tension_impact_history: List[float]
    preferred_regions: List[str]
    activity_patterns: Dict[str, Any]
    risk_assessment: Dict[str, float]
    last_updated: datetime


class TensionPatternAnalyzer:
    """Analyzes patterns and detects anomalies in tension data"""
    
    def __init__(self):
        self.detected_patterns: Dict[str, List[PatternDetection]] = {}
        self.anomaly_history: List[AnomalyDetection] = []
        self.player_profiles: Dict[str, PlayerBehaviorProfile] = {}
        
        # Analysis parameters
        self.anomaly_threshold = 2.5  # Standard deviations for anomaly detection
        self.pattern_min_occurrences = 3
        self.analysis_window_days = 30
        self.confidence_threshold = 0.7
    
    def analyze_tension_patterns(self, region_id: str, poi_id: Optional[str] = None, 
                               days_back: int = 30) -> List[PatternDetection]:
        """Analyze tension patterns for a location"""
        try:
            # Get historical tension data
            historical_data = self._get_historical_data(region_id, poi_id, days_back)
            
            if not historical_data:
                logger.warning(f"No historical data available for {region_id}/{poi_id}")
                return []
            
            patterns = []
            
            # Detect different types of patterns
            patterns.extend(self._detect_cyclic_patterns(historical_data, region_id, poi_id))
            patterns.extend(self._detect_trending_patterns(historical_data, region_id, poi_id))
            patterns.extend(self._detect_spike_patterns(historical_data, region_id, poi_id))
            patterns.extend(self._detect_stability_patterns(historical_data, region_id, poi_id))
            
            # Filter by confidence threshold
            high_confidence_patterns = [p for p in patterns if p.confidence >= self.confidence_threshold]
            
            # Cache patterns
            location_key = f"{region_id}:{poi_id or 'region'}"
            self.detected_patterns[location_key] = high_confidence_patterns
            
            logger.info(f"Detected {len(high_confidence_patterns)} patterns for {location_key}")
            
            return high_confidence_patterns
            
        except Exception as e:
            logger.error(f"Error analyzing tension patterns: {e}")
            return []
    
    def detect_anomalies(self, region_id: str, poi_id: Optional[str] = None, 
                        current_tension: float = 0.0) -> List[AnomalyDetection]:
        """Detect anomalies in current tension data"""
        try:
            anomalies = []
            
            # Get baseline data for comparison
            baseline_data = self._get_baseline_data(region_id, poi_id)
            
            if not baseline_data:
                logger.warning(f"No baseline data for anomaly detection: {region_id}/{poi_id}")
                return []
            
            # Statistical anomaly detection
            statistical_anomaly = self._detect_statistical_anomaly(
                current_tension, baseline_data, region_id, poi_id
            )
            if statistical_anomaly:
                anomalies.append(statistical_anomaly)
            
            # Temporal anomaly detection
            temporal_anomaly = self._detect_temporal_anomaly(
                current_tension, region_id, poi_id
            )
            if temporal_anomaly:
                anomalies.append(temporal_anomaly)
            
            # Contextual anomaly detection
            contextual_anomaly = self._detect_contextual_anomaly(
                current_tension, region_id, poi_id
            )
            if contextual_anomaly:
                anomalies.append(contextual_anomaly)
            
            # Add to anomaly history
            self.anomaly_history.extend(anomalies)
            
            # Keep only recent anomalies (last 1000)
            if len(self.anomaly_history) > 1000:
                self.anomaly_history = self.anomaly_history[-1000:]
            
            logger.info(f"Detected {len(anomalies)} anomalies for {region_id}/{poi_id}")
            
            return anomalies
            
        except Exception as e:
            logger.error(f"Error detecting anomalies: {e}")
            return []
    
    def analyze_player_behavior(self, player_id: str) -> PlayerBehaviorProfile:
        """Analyze and profile player behavior patterns"""
        try:
            # Get player activity data
            activity_data = self._get_player_activity_data(player_id)
            
            # Analyze behavior patterns
            behavior_patterns = self._analyze_behavior_patterns(activity_data)
            
            # Calculate tension impact history
            impact_history = self._calculate_tension_impact_history(player_id, activity_data)
            
            # Identify preferred regions
            preferred_regions = self._identify_preferred_regions(activity_data)
            
            # Analyze activity patterns (time of day, frequency, etc.)
            activity_patterns = self._analyze_activity_patterns(activity_data)
            
            # Assess risk factors
            risk_assessment = self._assess_player_risk_factors(behavior_patterns, impact_history)
            
            profile = PlayerBehaviorProfile(
                player_id=player_id,
                behavior_patterns=behavior_patterns,
                tension_impact_history=impact_history,
                preferred_regions=preferred_regions,
                activity_patterns=activity_patterns,
                risk_assessment=risk_assessment,
                last_updated=datetime.utcnow()
            )
            
            # Cache player profile
            self.player_profiles[player_id] = profile
            
            logger.info(f"Generated behavior profile for player {player_id}")
            
            return profile
            
        except Exception as e:
            logger.error(f"Error analyzing player behavior: {e}")
            return self._create_default_player_profile(player_id)
    
    def identify_regional_patterns(self, region_id: str) -> Dict[str, Any]:
        """Identify patterns across an entire region"""
        try:
            # Get all POIs in region
            pois = self._get_pois_in_region(region_id)
            
            regional_patterns = {
                'region_id': region_id,
                'poi_patterns': {},
                'regional_trends': {},
                'correlation_analysis': {},
                'collective_behaviors': []
            }
            
            # Analyze patterns for each POI
            for poi_id in pois:
                poi_patterns = self.analyze_tension_patterns(region_id, poi_id)
                regional_patterns['poi_patterns'][poi_id] = poi_patterns
            
            # Analyze regional trends
            regional_patterns['regional_trends'] = self._analyze_regional_trends(region_id, pois)
            
            # Correlation analysis between POIs
            regional_patterns['correlation_analysis'] = self._analyze_poi_correlations(region_id, pois)
            
            # Detect collective behaviors
            regional_patterns['collective_behaviors'] = self._detect_collective_behaviors(region_id, pois)
            
            return regional_patterns
            
        except Exception as e:
            logger.error(f"Error identifying regional patterns: {e}")
            return {'error': str(e)}
    
    def predict_pattern_recurrence(self, pattern: PatternDetection) -> Dict[str, Any]:
        """Predict when a pattern might recur"""
        try:
            prediction = {
                'pattern_id': f"{pattern.region_id}:{pattern.poi_id}:{pattern.pattern_type.value}",
                'next_occurrence_probability': 0.0,
                'estimated_timeframe': None,
                'confidence': 0.0,
                'factors_affecting_recurrence': []
            }
            
            if pattern.pattern_type == PatternType.CYCLIC:
                # For cyclic patterns, use the cycle parameters
                cycle_params = pattern.pattern_parameters
                if 'cycle_length_hours' in cycle_params:
                    next_occurrence = datetime.utcnow() + timedelta(
                        hours=cycle_params['cycle_length_hours']
                    )
                    prediction.update({
                        'next_occurrence_probability': min(0.9, pattern.confidence),
                        'estimated_timeframe': next_occurrence,
                        'confidence': pattern.confidence
                    })
            
            elif pattern.pattern_type == PatternType.TRENDING:
                # For trending patterns, extrapolate based on trend
                trend_params = pattern.pattern_parameters
                if 'trend_slope' in trend_params:
                    # Predict continuation of trend
                    prediction.update({
                        'next_occurrence_probability': 0.6,
                        'estimated_timeframe': datetime.utcnow() + timedelta(days=7),
                        'confidence': pattern.confidence * 0.8
                    })
            
            elif pattern.pattern_type == PatternType.SPIKE:
                # Spikes are harder to predict but may have triggers
                historical_frequency = pattern.historical_occurrences / 30  # per day
                if historical_frequency > 0:
                    avg_interval = 1.0 / historical_frequency
                    prediction.update({
                        'next_occurrence_probability': min(0.5, historical_frequency),
                        'estimated_timeframe': datetime.utcnow() + timedelta(days=avg_interval),
                        'confidence': 0.3
                    })
            
            return prediction
            
        except Exception as e:
            logger.error(f"Error predicting pattern recurrence: {e}")
            return {'error': str(e)}
    
    def get_anomaly_summary(self, region_id: Optional[str] = None, 
                           hours_back: int = 24) -> Dict[str, Any]:
        """Get summary of recent anomalies"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours_back)
            
            # Filter anomalies by time and region
            relevant_anomalies = [
                a for a in self.anomaly_history 
                if a.detected_at >= cutoff_time and (region_id is None or a.region_id == region_id)
            ]
            
            summary = {
                'total_anomalies': len(relevant_anomalies),
                'by_type': {},
                'by_severity': {'low': 0, 'medium': 0, 'high': 0, 'critical': 0},
                'by_region': {},
                'most_recent': None,
                'recommendations': []
            }
            
            for anomaly in relevant_anomalies:
                # Count by type
                anomaly_type = anomaly.anomaly_type.value
                summary['by_type'][anomaly_type] = summary['by_type'].get(anomaly_type, 0) + 1
                
                # Count by severity
                if anomaly.severity < 0.3:
                    severity_level = 'low'
                elif anomaly.severity < 0.6:
                    severity_level = 'medium'
                elif anomaly.severity < 0.8:
                    severity_level = 'high'
                else:
                    severity_level = 'critical'
                summary['by_severity'][severity_level] += 1
                
                # Count by region
                region = anomaly.region_id
                summary['by_region'][region] = summary['by_region'].get(region, 0) + 1
            
            # Get most recent anomaly
            if relevant_anomalies:
                summary['most_recent'] = max(relevant_anomalies, key=lambda a: a.detected_at)
            
            # Generate recommendations
            summary['recommendations'] = self._generate_anomaly_recommendations(relevant_anomalies)
            
            return summary
            
        except Exception as e:
            logger.error(f"Error generating anomaly summary: {e}")
            return {'error': str(e)}
    
    def _get_historical_data(self, region_id: str, poi_id: Optional[str], 
                           days_back: int) -> List[Dict[str, Any]]:
        """Get historical tension data for analysis"""
        # This would query actual historical data storage
        # For now, generating sample data
        sample_data = []
        for i in range(days_back * 24):  # Hourly data
            timestamp = datetime.utcnow() - timedelta(hours=i)
            # Generate sample tension value with some patterns
            base_tension = 0.4
            daily_cycle = 0.1 * abs(1 - (timestamp.hour / 12.0))  # Daily variation
            weekly_cycle = 0.05 * (timestamp.weekday() / 7.0)  # Weekly variation
            noise = (hash(str(timestamp)) % 100) / 1000.0  # Random noise
            
            tension = base_tension + daily_cycle + weekly_cycle + noise
            tension = max(0.0, min(1.0, tension))
            
            sample_data.append({
                'timestamp': timestamp,
                'tension': tension,
                'events': []  # Would include actual events
            })
        
        return sample_data
    
    def _detect_cyclic_patterns(self, data: List[Dict[str, Any]], 
                              region_id: str, poi_id: Optional[str]) -> List[PatternDetection]:
        """Detect cyclic patterns in tension data"""
        patterns = []
        
        try:
            tensions = [d['tension'] for d in data]
            timestamps = [d['timestamp'] for d in data]
            
            # Simple daily cycle detection
            hourly_averages = {}
            for i, tension in enumerate(tensions):
                hour = timestamps[i].hour
                if hour not in hourly_averages:
                    hourly_averages[hour] = []
                hourly_averages[hour].append(tension)
            
            # Calculate hourly variance
            hourly_variance = {}
            for hour, values in hourly_averages.items():
                if len(values) > 1:
                    hourly_variance[hour] = statistics.variance(values)
            
            # If there's significant hourly variation, it's a daily cycle
            if hourly_variance and max(hourly_variance.values()) > 0.01:
                patterns.append(PatternDetection(
                    pattern_type=PatternType.CYCLIC,
                    region_id=region_id,
                    poi_id=poi_id,
                    confidence=0.8,
                    description=f"Daily tension cycle detected with peak variance of {max(hourly_variance.values()):.3f}",
                    detected_at=datetime.utcnow(),
                    pattern_parameters={
                        'cycle_type': 'daily',
                        'cycle_length_hours': 24,
                        'peak_hours': [h for h, v in hourly_variance.items() if v == max(hourly_variance.values())],
                        'variance': max(hourly_variance.values())
                    },
                    historical_occurrences=len(data) // 24,
                    predicted_next_occurrence=datetime.utcnow() + timedelta(hours=24)
                ))
        
        except Exception as e:
            logger.error(f"Error detecting cyclic patterns: {e}")
        
        return patterns
    
    def _detect_trending_patterns(self, data: List[Dict[str, Any]], 
                                region_id: str, poi_id: Optional[str]) -> List[PatternDetection]:
        """Detect trending patterns in tension data"""
        patterns = []
        
        try:
            if len(data) < 10:
                return patterns
            
            tensions = [d['tension'] for d in data]
            
            # Simple linear trend calculation
            x_values = list(range(len(tensions)))
            n = len(tensions)
            
            sum_x = sum(x_values)
            sum_y = sum(tensions)
            sum_xy = sum(x * y for x, y in zip(x_values, tensions))
            sum_x2 = sum(x * x for x in x_values)
            
            # Calculate slope
            slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
            
            # If slope is significant, it's a trend
            if abs(slope) > 0.001:  # Threshold for significant trend
                trend_direction = "increasing" if slope > 0 else "decreasing"
                confidence = min(0.9, abs(slope) * 1000)  # Scale confidence based on slope
                
                patterns.append(PatternDetection(
                    pattern_type=PatternType.TRENDING,
                    region_id=region_id,
                    poi_id=poi_id,
                    confidence=confidence,
                    description=f"{trend_direction.capitalize()} trend detected with slope {slope:.6f}",
                    detected_at=datetime.utcnow(),
                    pattern_parameters={
                        'trend_slope': slope,
                        'trend_direction': trend_direction,
                        'r_squared': 0.5  # Would calculate actual R² in real implementation
                    },
                    historical_occurrences=1,
                    predicted_next_occurrence=None
                ))
        
        except Exception as e:
            logger.error(f"Error detecting trending patterns: {e}")
        
        return patterns
    
    def _detect_spike_patterns(self, data: List[Dict[str, Any]], 
                             region_id: str, poi_id: Optional[str]) -> List[PatternDetection]:
        """Detect spike patterns in tension data"""
        patterns = []
        
        try:
            tensions = [d['tension'] for d in data]
            
            if len(tensions) < 5:
                return patterns
            
            mean_tension = statistics.mean(tensions)
            std_tension = statistics.stdev(tensions) if len(tensions) > 1 else 0
            
            # Find spikes (values more than 2 standard deviations from mean)
            spikes = []
            for i, tension in enumerate(tensions):
                if abs(tension - mean_tension) > 2 * std_tension:
                    spikes.append(i)
            
            if len(spikes) >= 2:  # Need at least 2 spikes to establish a pattern
                patterns.append(PatternDetection(
                    pattern_type=PatternType.SPIKE,
                    region_id=region_id,
                    poi_id=poi_id,
                    confidence=0.7,
                    description=f"Spike pattern detected with {len(spikes)} spikes",
                    detected_at=datetime.utcnow(),
                    pattern_parameters={
                        'spike_threshold': 2 * std_tension,
                        'spike_count': len(spikes),
                        'average_spike_magnitude': statistics.mean([
                            abs(tensions[i] - mean_tension) for i in spikes
                        ])
                    },
                    historical_occurrences=len(spikes),
                    predicted_next_occurrence=None
                ))
        
        except Exception as e:
            logger.error(f"Error detecting spike patterns: {e}")
        
        return patterns
    
    def _detect_stability_patterns(self, data: List[Dict[str, Any]], 
                                 region_id: str, poi_id: Optional[str]) -> List[PatternDetection]:
        """Detect stability/volatility patterns"""
        patterns = []
        
        try:
            tensions = [d['tension'] for d in data]
            
            if len(tensions) < 5:
                return patterns
            
            variance = statistics.variance(tensions)
            
            # Determine if stable or volatile
            if variance < 0.01:  # Low variance = stable
                pattern_type = PatternType.STABLE
                description = f"Stable tension pattern with low variance ({variance:.6f})"
                confidence = 0.9
            elif variance > 0.05:  # High variance = volatile
                pattern_type = PatternType.VOLATILE
                description = f"Volatile tension pattern with high variance ({variance:.6f})"
                confidence = 0.8
            else:
                return patterns  # Normal variance, no pattern
            
            patterns.append(PatternDetection(
                pattern_type=pattern_type,
                region_id=region_id,
                poi_id=poi_id,
                confidence=confidence,
                description=description,
                detected_at=datetime.utcnow(),
                pattern_parameters={
                    'variance': variance,
                    'mean_tension': statistics.mean(tensions),
                    'min_tension': min(tensions),
                    'max_tension': max(tensions)
                },
                historical_occurrences=1,
                predicted_next_occurrence=None
            ))
        
        except Exception as e:
            logger.error(f"Error detecting stability patterns: {e}")
        
        return patterns
    
    def _get_baseline_data(self, region_id: str, poi_id: Optional[str]) -> Dict[str, Any]:
        """Get baseline data for anomaly detection"""
        # This would query historical baseline data
        return {
            'mean_tension': 0.4,
            'std_tension': 0.1,
            'normal_range': (0.2, 0.6),
            'sample_size': 1000
        }
    
    def _detect_statistical_anomaly(self, current_tension: float, baseline: Dict[str, Any],
                                  region_id: str, poi_id: Optional[str]) -> Optional[AnomalyDetection]:
        """Detect statistical anomalies"""
        try:
            mean = baseline['mean_tension']
            std = baseline['std_tension']
            
            # Calculate z-score
            z_score = abs(current_tension - mean) / std
            
            if z_score > self.anomaly_threshold:
                severity = min(1.0, z_score / 5.0)  # Scale severity
                confidence = min(0.95, z_score / 4.0)  # Scale confidence
                
                return AnomalyDetection(
                    anomaly_type=AnomalyType.STATISTICAL,
                    region_id=region_id,
                    poi_id=poi_id,
                    severity=severity,
                    confidence=confidence,
                    description=f"Statistical anomaly: tension {current_tension:.3f} is {z_score:.2f} standard deviations from normal",
                    detected_at=datetime.utcnow(),
                    deviation_score=z_score,
                    contributing_factors=['statistical_outlier'],
                    recommended_actions=['investigate_cause', 'monitor_closely']
                )
        
        except Exception as e:
            logger.error(f"Error detecting statistical anomaly: {e}")
        
        return None
    
    def _detect_temporal_anomaly(self, current_tension: float, 
                               region_id: str, poi_id: Optional[str]) -> Optional[AnomalyDetection]:
        """Detect temporal anomalies (time-based)"""
        try:
            current_hour = datetime.utcnow().hour
            
            # Get expected tension for this time of day
            expected_tension = self._get_expected_tension_for_time(region_id, poi_id, current_hour)
            
            if expected_tension is None:
                return None
            
            deviation = abs(current_tension - expected_tension)
            
            # If deviation is significant for this time
            if deviation > 0.2:  # Threshold for temporal anomaly
                severity = min(1.0, deviation / 0.5)
                confidence = 0.7
                
                return AnomalyDetection(
                    anomaly_type=AnomalyType.TEMPORAL,
                    region_id=region_id,
                    poi_id=poi_id,
                    severity=severity,
                    confidence=confidence,
                    description=f"Temporal anomaly: tension {current_tension:.3f} differs from expected {expected_tension:.3f} for hour {current_hour}",
                    detected_at=datetime.utcnow(),
                    deviation_score=deviation,
                    contributing_factors=['temporal_deviation'],
                    recommended_actions=['check_recent_events', 'verify_data']
                )
        
        except Exception as e:
            logger.error(f"Error detecting temporal anomaly: {e}")
        
        return None
    
    def _detect_contextual_anomaly(self, current_tension: float,
                                 region_id: str, poi_id: Optional[str]) -> Optional[AnomalyDetection]:
        """Detect contextual anomalies"""
        try:
            # Get context (nearby regions, recent events, etc.)
            context = self._get_contextual_data(region_id, poi_id)
            
            # Check if tension is anomalous given context
            if self._is_contextually_anomalous(current_tension, context):
                return AnomalyDetection(
                    anomaly_type=AnomalyType.CONTEXTUAL,
                    region_id=region_id,
                    poi_id=poi_id,
                    severity=0.6,
                    confidence=0.6,
                    description="Contextual anomaly detected based on regional conditions",
                    detected_at=datetime.utcnow(),
                    deviation_score=0.5,
                    contributing_factors=['contextual_mismatch'],
                    recommended_actions=['analyze_regional_context', 'cross_reference_events']
                )
        
        except Exception as e:
            logger.error(f"Error detecting contextual anomaly: {e}")
        
        return None
    
    # Additional helper methods for comprehensive pattern analysis...
    
    def _get_expected_tension_for_time(self, region_id: str, poi_id: Optional[str], 
                                     hour: int) -> Optional[float]:
        """Get expected tension for a specific time"""
        # This would use historical data to determine expected tension
        # Simple implementation: slight variation by hour
        base_tension = 0.4
        hour_modifier = 0.1 * abs(12 - hour) / 12  # Higher tension during "rush hours"
        return base_tension + hour_modifier
    
    def _get_contextual_data(self, region_id: str, poi_id: Optional[str]) -> Dict[str, Any]:
        """Get contextual data for anomaly detection"""
        return {
            'nearby_regions_tension': [0.3, 0.5, 0.4],
            'recent_events': ['faction_dispute'],
            'economic_factors': {'trade_volume': 0.8},
            'weather': 'normal'
        }
    
    def _is_contextually_anomalous(self, tension: float, context: Dict[str, Any]) -> bool:
        """Check if tension is anomalous given context"""
        # Simple contextual check
        nearby_avg = statistics.mean(context.get('nearby_regions_tension', [0.4]))
        return abs(tension - nearby_avg) > 0.3
    
    def _get_player_activity_data(self, player_id: str) -> Dict[str, Any]:
        """Get player activity data for analysis"""
        # This would query actual player activity logs
        return {
            'actions': ['combat', 'trade', 'quest', 'diplomacy'],
            'regions_visited': ['region_1', 'region_2'],
            'tension_changes_caused': [0.1, -0.05, 0.2],
            'activity_times': [datetime.utcnow() - timedelta(hours=i) for i in range(10)]
        }
    
    def _analyze_behavior_patterns(self, activity_data: Dict[str, Any]) -> Dict[str, float]:
        """Analyze player behavior patterns"""
        actions = activity_data.get('actions', [])
        total_actions = len(actions)
        
        if total_actions == 0:
            return {}
        
        # Calculate behavior frequencies
        behavior_counts = {}
        for action in actions:
            behavior_counts[action] = behavior_counts.get(action, 0) + 1
        
        # Convert to frequencies
        return {action: count / total_actions for action, count in behavior_counts.items()}
    
    def _calculate_tension_impact_history(self, player_id: str, 
                                        activity_data: Dict[str, Any]) -> List[float]:
        """Calculate player's historical tension impact"""
        return activity_data.get('tension_changes_caused', [])
    
    def _identify_preferred_regions(self, activity_data: Dict[str, Any]) -> List[str]:
        """Identify player's preferred regions"""
        regions = activity_data.get('regions_visited', [])
        # Count frequency and return most visited
        region_counts = {}
        for region in regions:
            region_counts[region] = region_counts.get(region, 0) + 1
        
        # Sort by frequency
        sorted_regions = sorted(region_counts.items(), key=lambda x: x[1], reverse=True)
        return [region for region, count in sorted_regions[:3]]  # Top 3
    
    def _analyze_activity_patterns(self, activity_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze player activity patterns"""
        activity_times = activity_data.get('activity_times', [])
        
        if not activity_times:
            return {}
        
        # Analyze time patterns
        hours = [dt.hour for dt in activity_times]
        most_active_hour = max(set(hours), key=hours.count) if hours else 12
        
        return {
            'most_active_hour': most_active_hour,
            'activity_frequency': len(activity_times) / 7,  # per week
            'consistency': 0.7  # Would calculate actual consistency metric
        }
    
    def _assess_player_risk_factors(self, patterns: Dict[str, float], 
                                  impact_history: List[float]) -> Dict[str, float]:
        """Assess player risk factors"""
        risk_factors = {}
        
        # Combat frequency risk
        combat_frequency = patterns.get('combat', 0.0)
        risk_factors['combat_risk'] = combat_frequency
        
        # Tension escalation risk
        escalation_events = sum(1 for impact in impact_history if impact > 0.1)
        risk_factors['escalation_risk'] = min(1.0, escalation_events / 10.0)
        
        # Overall unpredictability
        if impact_history:
            impact_variance = statistics.variance(impact_history)
            risk_factors['unpredictability'] = min(1.0, impact_variance * 10)
        else:
            risk_factors['unpredictability'] = 0.0
        
        return risk_factors
    
    def _create_default_player_profile(self, player_id: str) -> PlayerBehaviorProfile:
        """Create default player profile when analysis fails"""
        return PlayerBehaviorProfile(
            player_id=player_id,
            behavior_patterns={},
            tension_impact_history=[],
            preferred_regions=[],
            activity_patterns={},
            risk_assessment={'overall_risk': 0.3},
            last_updated=datetime.utcnow()
        )
    
    def _get_pois_in_region(self, region_id: str) -> List[str]:
        """Get POIs in a region"""
        return ['market', 'tavern', 'guard_post', 'temple']  # Placeholder
    
    def _analyze_regional_trends(self, region_id: str, pois: List[str]) -> Dict[str, Any]:
        """Analyze regional trends"""
        return {
            'overall_trend': 'stable',
            'average_tension': 0.4,
            'volatility': 0.1
        }
    
    def _analyze_poi_correlations(self, region_id: str, pois: List[str]) -> Dict[str, float]:
        """Analyze correlations between POIs"""
        # Would calculate actual correlations
        correlations = {}
        for i, poi1 in enumerate(pois):
            for poi2 in pois[i+1:]:
                correlations[f"{poi1}-{poi2}"] = 0.3  # Placeholder correlation
        
        return correlations
    
    def _detect_collective_behaviors(self, region_id: str, pois: List[str]) -> List[Dict[str, Any]]:
        """Detect collective behaviors across POIs"""
        return [
            {
                'behavior_type': 'synchronized_increase',
                'affected_pois': pois[:2],
                'confidence': 0.7,
                'description': 'Synchronized tension increase across multiple POIs'
            }
        ]
    
    def _generate_anomaly_recommendations(self, anomalies: List[AnomalyDetection]) -> List[str]:
        """Generate recommendations based on anomalies"""
        recommendations = []
        
        if not anomalies:
            return recommendations
        
        # Count high severity anomalies
        high_severity = sum(1 for a in anomalies if a.severity > 0.7)
        
        if high_severity > 0:
            recommendations.append('immediate_investigation')
            recommendations.append('increase_monitoring')
        
        # Check for patterns in anomaly types
        temporal_count = sum(1 for a in anomalies if a.anomaly_type == AnomalyType.TEMPORAL)
        if temporal_count > len(anomalies) * 0.5:
            recommendations.append('review_temporal_patterns')
        
        return recommendations
    
    def get_analysis_status(self) -> Dict[str, Any]:
        """Get status of pattern analyzer"""
        return {
            'detected_patterns_count': sum(len(patterns) for patterns in self.detected_patterns.values()),
            'anomaly_history_size': len(self.anomaly_history),
            'player_profiles_count': len(self.player_profiles),
            'regions_analyzed': len(self.detected_patterns),
            'analyzer_active': True
        } 
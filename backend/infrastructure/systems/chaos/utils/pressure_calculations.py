"""
Pressure Calculations

Mathematical utility functions for pressure analysis and calculations.
"""

import math
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta

from backend.infrastructure.systems.chaos.models.pressure_data import (
    PressureData, PressureReading, PressureSource, RegionalPressure, PressureMetrics
)

class PressureCalculations:
    """
    Utility class containing mathematical functions for pressure analysis.
    
    This class provides:
    - Statistical analysis of pressure data
    - Trend calculations and forecasting
    - Regional pressure aggregation
    - Anomaly detection algorithms
    """
    
    @staticmethod
    def calculate_regional_metrics(regional_pressure: RegionalPressure, weights: Dict[PressureSource, float]) -> None:
        """Calculate aggregated metrics for a regional pressure instance"""
        readings = regional_pressure.pressure_readings
        
        if not readings:
            return
        
        # Initialize metrics
        metrics = PressureMetrics()
        
        # Calculate basic metrics
        total_pressure = 0.0
        weighted_pressure = 0.0
        total_weight = 0.0
        peak_pressure = 0.0
        
        # Group readings by source
        source_readings: Dict[PressureSource, List[PressureReading]] = {}
        for reading in readings:
            if reading.source not in source_readings:
                source_readings[reading.source] = []
            source_readings[reading.source].append(reading)
        
        # Calculate weighted pressure for each source
        for source, source_readings_list in source_readings.items():
            if source in weights:
                weight = weights[source]
                
                # Get most recent reading for this source
                latest_reading = max(source_readings_list, key=lambda r: r.timestamp)
                source_pressure = latest_reading.value * latest_reading.confidence
                
                total_pressure += source_pressure
                weighted_pressure += source_pressure * weight
                total_weight += weight
                peak_pressure = max(peak_pressure, source_pressure)
                
                # Store breakdown
                metrics.source_breakdown[source] = source_pressure
        
        # Finalize calculations
        if total_weight > 0:
            metrics.weighted_pressure = weighted_pressure / total_weight
        else:
            metrics.weighted_pressure = 0.0
        
        metrics.total_pressure = total_pressure
        metrics.peak_pressure = peak_pressure
        
        # Calculate pressure trend
        metrics.pressure_trend = PressureCalculations._calculate_pressure_trend(readings)
        
        # Calculate pressure velocity (rate of change)
        metrics.pressure_velocity = PressureCalculations._calculate_pressure_velocity(readings)
        
        # Calculate time above threshold
        metrics.time_above_threshold = PressureCalculations._calculate_time_above_threshold(
            readings, threshold=0.7
        )
        
        # Store regional breakdown
        metrics.regional_breakdown[regional_pressure.region_id] = metrics.weighted_pressure
        
        # Update regional pressure metrics
        regional_pressure.metrics = metrics
    
    @staticmethod
    def _calculate_pressure_trend(readings: List[PressureReading]) -> float:
        """Calculate pressure trend using linear regression"""
        if len(readings) < 2:
            return 0.0
        
        # Sort readings by timestamp
        sorted_readings = sorted(readings, key=lambda r: r.timestamp)
        
        # Use last 10 readings for trend calculation
        recent_readings = sorted_readings[-10:]
        
        if len(recent_readings) < 2:
            return 0.0
        
        # Convert timestamps to relative time (hours)
        base_time = recent_readings[0].timestamp
        x_values = [(r.timestamp - base_time).total_seconds() / 3600.0 for r in recent_readings]
        y_values = [r.value for r in recent_readings]
        
        # Calculate linear regression slope
        n = len(x_values)
        sum_x = sum(x_values)
        sum_y = sum(y_values)
        sum_xy = sum(x * y for x, y in zip(x_values, y_values))
        sum_x2 = sum(x * x for x in x_values)
        
        denominator = n * sum_x2 - sum_x * sum_x
        if denominator == 0:
            return 0.0
        
        slope = (n * sum_xy - sum_x * sum_y) / denominator
        return slope
    
    @staticmethod
    def _calculate_pressure_velocity(readings: List[PressureReading]) -> float:
        """Calculate instantaneous pressure velocity (rate of change)"""
        if len(readings) < 2:
            return 0.0
        
        # Sort readings by timestamp
        sorted_readings = sorted(readings, key=lambda r: r.timestamp)
        
        # Use last two readings
        last_reading = sorted_readings[-1]
        prev_reading = sorted_readings[-2]
        
        time_diff = (last_reading.timestamp - prev_reading.timestamp).total_seconds()
        if time_diff == 0:
            return 0.0
        
        pressure_diff = last_reading.value - prev_reading.value
        
        # Return pressure change per hour
        return (pressure_diff / time_diff) * 3600.0
    
    @staticmethod
    def _calculate_time_above_threshold(readings: List[PressureReading], threshold: float) -> float:
        """Calculate time (in seconds) that pressure has been above threshold"""
        if not readings:
            return 0.0
        
        # Sort readings by timestamp
        sorted_readings = sorted(readings, key=lambda r: r.timestamp)
        
        time_above = 0.0
        in_threshold_period = False
        threshold_start = None
        
        for i, reading in enumerate(sorted_readings):
            if reading.value >= threshold:
                if not in_threshold_period:
                    # Start of threshold period
                    in_threshold_period = True
                    threshold_start = reading.timestamp
            else:
                if in_threshold_period:
                    # End of threshold period
                    if threshold_start:
                        period_duration = (reading.timestamp - threshold_start).total_seconds()
                        time_above += period_duration
                    in_threshold_period = False
                    threshold_start = None
        
        # Handle case where we're still in a threshold period
        if in_threshold_period and threshold_start:
            current_time = datetime.now()
            period_duration = (current_time - threshold_start).total_seconds()
            time_above += period_duration
        
        return time_above
    
    @staticmethod
    def detect_pressure_anomalies(readings: List[PressureReading], 
                                 sensitivity: float = 2.0) -> List[PressureReading]:
        """Detect anomalous pressure readings using statistical analysis"""
        if len(readings) < 10:  # Need sufficient data for anomaly detection
            return []
        
        # Calculate mean and standard deviation
        values = [r.value for r in readings]
        mean_value = sum(values) / len(values)
        variance = sum((x - mean_value) ** 2 for x in values) / len(values)
        std_dev = math.sqrt(variance)
        
        # Find anomalies (readings outside sensitivity * std_dev)
        anomalies = []
        threshold = sensitivity * std_dev
        
        for reading in readings:
            if abs(reading.value - mean_value) > threshold:
                anomalies.append(reading)
        
        return anomalies
    
    @staticmethod
    def calculate_pressure_forecast(readings: List[PressureReading], 
                                  hours_ahead: int = 24) -> Optional[float]:
        """Forecast pressure level using trend analysis"""
        if len(readings) < 5:
            return None
        
        # Calculate current trend
        trend = PressureCalculations._calculate_pressure_trend(readings)
        
        # Get current pressure
        current_pressure = max(readings, key=lambda r: r.timestamp).value
        
        # Simple linear extrapolation
        forecast = current_pressure + (trend * hours_ahead)
        
        # Clamp to valid range
        return max(0.0, min(1.0, forecast))
    
    @staticmethod
    def calculate_pressure_stability(readings: List[PressureReading]) -> float:
        """Calculate pressure stability metric (0.0 = very unstable, 1.0 = very stable)"""
        if len(readings) < 3:
            return 1.0  # Assume stable if insufficient data
        
        # Calculate coefficient of variation
        values = [r.value for r in readings]
        mean_value = sum(values) / len(values)
        
        if mean_value == 0:
            return 1.0
        
        variance = sum((x - mean_value) ** 2 for x in values) / len(values)
        std_dev = math.sqrt(variance)
        
        coefficient_of_variation = std_dev / mean_value
        
        # Convert to stability metric (inverse relationship)
        stability = 1.0 / (1.0 + coefficient_of_variation)
        
        return stability
    
    @staticmethod
    def calculate_pressure_momentum(readings: List[PressureReading]) -> float:
        """Calculate pressure momentum (tendency to continue in current direction)"""
        if len(readings) < 3:
            return 0.0
        
        # Sort readings by timestamp
        sorted_readings = sorted(readings, key=lambda r: r.timestamp)
        
        # Calculate direction changes
        direction_changes = 0
        total_periods = 0
        
        for i in range(1, len(sorted_readings) - 1):
            prev_reading = sorted_readings[i - 1]
            curr_reading = sorted_readings[i]
            next_reading = sorted_readings[i + 1]
            
            prev_direction = curr_reading.value - prev_reading.value
            next_direction = next_reading.value - curr_reading.value
            
            # Check if direction changed (sign change)
            if prev_direction * next_direction < 0:
                direction_changes += 1
            
            total_periods += 1
        
        if total_periods == 0:
            return 0.0
        
        # Momentum is inverse of direction change frequency
        momentum = 1.0 - (direction_changes / total_periods)
        return momentum
    
    @staticmethod
    def calculate_regional_pressure_correlation(region1: RegionalPressure, 
                                              region2: RegionalPressure) -> float:
        """Calculate correlation between pressure in two regions"""
        readings1 = region1.pressure_readings
        readings2 = region2.pressure_readings
        
        if len(readings1) < 3 or len(readings2) < 3:
            return 0.0
        
        # Align readings by timestamp (take readings close in time)
        aligned_pairs = []
        tolerance = timedelta(minutes=30)  # Allow 30 minute tolerance
        
        for r1 in readings1:
            for r2 in readings2:
                if abs((r1.timestamp - r2.timestamp).total_seconds()) <= tolerance.total_seconds():
                    aligned_pairs.append((r1.value, r2.value))
                    break
        
        if len(aligned_pairs) < 3:
            return 0.0
        
        # Calculate Pearson correlation coefficient
        x_values = [pair[0] for pair in aligned_pairs]
        y_values = [pair[1] for pair in aligned_pairs]
        
        n = len(aligned_pairs)
        sum_x = sum(x_values)
        sum_y = sum(y_values)
        sum_xy = sum(x * y for x, y in aligned_pairs)
        sum_x2 = sum(x * x for x in x_values)
        sum_y2 = sum(y * y for y in y_values)
        
        numerator = n * sum_xy - sum_x * sum_y
        denominator = math.sqrt((n * sum_x2 - sum_x * sum_x) * (n * sum_y2 - sum_y * sum_y))
        
        if denominator == 0:
            return 0.0
        
        correlation = numerator / denominator
        return correlation
    
    @staticmethod
    def calculate_pressure_criticality_score(regional_pressure: RegionalPressure) -> float:
        """Calculate a criticality score combining multiple pressure factors"""
        readings = regional_pressure.pressure_readings
        
        if not readings:
            return 0.0
        
        # Base pressure level
        current_pressure = regional_pressure.metrics.weighted_pressure
        
        # Trend factor (increasing pressure is more critical)
        trend = regional_pressure.metrics.pressure_trend
        trend_factor = max(0.0, trend)  # Only positive trends increase criticality
        
        # Velocity factor (rapid changes are more critical)
        velocity = abs(regional_pressure.metrics.pressure_velocity)
        velocity_factor = min(1.0, velocity * 10)  # Scale velocity impact
        
        # Time above threshold factor
        time_above = regional_pressure.metrics.time_above_threshold
        time_factor = min(1.0, time_above / 3600.0)  # Scale by hours
        
        # Regional modifier
        regional_modifier = regional_pressure.calculate_regional_modifier()
        
        # Combine factors with weights
        criticality = (
            current_pressure * 0.4 +           # 40% current level
            trend_factor * 0.2 +               # 20% trend
            velocity_factor * 0.2 +            # 20% velocity
            time_factor * 0.1 +                # 10% persistence
            (regional_modifier - 1.0) * 0.1    # 10% regional factors
        )
        
        # Clamp to valid range
        return max(0.0, min(1.0, criticality))
    
    @staticmethod
    def identify_pressure_hotspots(pressure_data: PressureData, 
                                 threshold: float = 0.6) -> List[Tuple[str, float]]:
        """Identify regions with the highest pressure levels"""
        hotspots = []
        
        for region_id, regional_pressure in pressure_data.global_pressure.regional_pressures.items():
            criticality = PressureCalculations.calculate_pressure_criticality_score(regional_pressure)
            
            if criticality >= threshold:
                hotspots.append((str(region_id), criticality))
        
        # Sort by criticality score (highest first)
        hotspots.sort(key=lambda x: x[1], reverse=True)
        
        return hotspots
    
    @staticmethod
    def calculate_system_pressure_health(pressure_data: PressureData) -> Dict[str, float]:
        """
        Calculate overall system pressure health metrics.
        
        Args:
            pressure_data: Current pressure data
            
        Returns:
            Dictionary containing health metrics
        """
        health_metrics = {
            'overall_health': 0.0,
            'stability_score': 0.0,
            'risk_level': 0.0,
            'trend_health': 0.0
        }
        
        if not pressure_data.regional_pressures:
            return health_metrics
        
        # Calculate overall health based on regional pressures
        total_pressure = 0.0
        total_regions = len(pressure_data.regional_pressures)
        
        for regional_pressure in pressure_data.regional_pressures.values():
            if regional_pressure.metrics:
                total_pressure += regional_pressure.metrics.weighted_pressure
        
        if total_regions > 0:
            avg_pressure = total_pressure / total_regions
            health_metrics['overall_health'] = max(0.0, 1.0 - avg_pressure)
            health_metrics['risk_level'] = avg_pressure
        
        return health_metrics
    
    @staticmethod
    def calculate_weighted_pressure(
        pressure_sources: Dict[str, float],
        weights: Dict[str, float]
    ) -> Dict[str, float]:
        """Calculate weighted pressure values"""
        weighted = {}
        
        for source, pressure in pressure_sources.items():
            weight = weights.get(source, 1.0)
            weighted[source] = pressure * weight
        
        return weighted
    
    @staticmethod
    def aggregate_pressure_score(weighted_pressures: Dict[str, float]) -> float:
        """Aggregate weighted pressures into a single score"""
        if not weighted_pressures:
            return 0.0
        
        # Calculate average of weighted pressures
        total = sum(weighted_pressures.values())
        count = len(weighted_pressures)
        
        return total / count
    
    @staticmethod
    def calculate_pressure_trend(historical_data: List[Dict[str, any]]) -> float:
        """Calculate pressure trend from historical data"""
        if len(historical_data) < 2:
            return 0.0
        
        # Sort by timestamp
        sorted_data = sorted(historical_data, key=lambda x: x['timestamp'])
        
        # Extract pressure values
        pressures = [data['pressure'] for data in sorted_data]
        
        # Calculate simple linear trend (slope)
        n = len(pressures)
        x_values = list(range(n))
        
        # Calculate linear regression slope
        sum_x = sum(x_values)
        sum_y = sum(pressures)
        sum_xy = sum(x * y for x, y in zip(x_values, pressures))
        sum_x2 = sum(x * x for x in x_values)
        
        denominator = n * sum_x2 - sum_x * sum_x
        if denominator == 0:
            return 0.0
        
        slope = (n * sum_xy - sum_x * sum_y) / denominator
        return slope
    
    @staticmethod
    def normalize_pressure_values(raw_values: Dict[str, float]) -> Dict[str, float]:
        """Normalize pressure values to 0.0-1.0 range"""
        normalized = {}
        
        for key, value in raw_values.items():
            # Clamp to 0.0-1.0 range
            normalized[key] = max(0.0, min(1.0, value))
        
        return normalized
    
    @staticmethod
    def detect_pressure_anomalies(
        pressure_data: Dict[str, float],
        threshold: float = 0.8
    ) -> Dict[str, List[str]]:
        """Detect pressure anomalies based on threshold"""
        anomalies = {
            'high_anomalies': [],
            'low_anomalies': []
        }
        
        for source, pressure in pressure_data.items():
            if pressure >= threshold:
                anomalies['high_anomalies'].append(source)
            elif pressure <= (1.0 - threshold):
                anomalies['low_anomalies'].append(source)
        
        return anomalies 
"""
Pressure Data Models

Models for tracking and calculating pressure across different game systems.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from enum import Enum
from uuid import UUID

@dataclass
class PressureTrend:
    """Analysis of pressure trends over time"""
    direction: str = "stable"  # "increasing", "decreasing", "stable", "volatile"
    magnitude: float = 0.0  # How strong the trend is (0.0 to 1.0)
    confidence: float = 1.0  # Confidence in trend analysis (0.0 to 1.0)
    duration_hours: float = 0.0  # How long this trend has been active
    
    # Trend characteristics
    volatility: float = 0.0  # How much the pressure fluctuates
    acceleration: float = 0.0  # Whether trend is speeding up or slowing down
    peak_value: float = 0.0  # Highest value in trend period
    trough_value: float = 0.0  # Lowest value in trend period
    
    # Predictions
    predicted_next_value: float = 0.0
    predicted_peak_time: Optional[datetime] = None
    trend_reversal_probability: float = 0.0
    
    def get_trend_description(self) -> str:
        """Get human-readable trend description"""
        if self.direction == "stable":
            return "Pressure levels are stable"
        elif self.direction == "increasing":
            if self.magnitude > 0.7:
                return "Pressure is rapidly increasing"
            elif self.magnitude > 0.4:
                return "Pressure is steadily increasing"
            else:
                return "Pressure is slowly increasing"
        elif self.direction == "decreasing":
            if self.magnitude > 0.7:
                return "Pressure is rapidly decreasing"
            elif self.magnitude > 0.4:
                return "Pressure is steadily decreasing"
            else:
                return "Pressure is slowly decreasing"
        else:  # volatile
            return "Pressure levels are highly volatile"

@dataclass
class PressureHistoryEntry:
    """Single entry in pressure history"""
    timestamp: datetime
    pressure_value: float
    dominant_source: Optional['PressureSource'] = None
    regional_breakdown: Dict[Union[str, UUID], float] = field(default_factory=dict)
    source_breakdown: Dict['PressureSource', float] = field(default_factory=dict)
    events_triggered: List[str] = field(default_factory=list)

@dataclass
class PressureHistory:
    """Historical tracking of pressure data"""
    entries: List[PressureHistoryEntry] = field(default_factory=list)
    max_entries: int = 1000  # Keep last 1000 entries
    
    def add_entry(self, pressure_value: float, timestamp: Optional[datetime] = None, **kwargs) -> None:
        """Add a new pressure history entry"""
        if timestamp is None:
            timestamp = datetime.now()
        
        entry = PressureHistoryEntry(
            timestamp=timestamp,
            pressure_value=pressure_value,
            **kwargs
        )
        
        self.entries.append(entry)
        
        # Trim old entries
        if len(self.entries) > self.max_entries:
            self.entries = self.entries[-self.max_entries:]
    
    def get_trend_analysis(self, hours: int = 24) -> PressureTrend:
        """Analyze pressure trends over the last N hours"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_entries = [e for e in self.entries if e.timestamp >= cutoff_time]
        
        if len(recent_entries) < 2:
            return PressureTrend()
        
        # Calculate basic trend metrics
        values = [e.pressure_value for e in recent_entries]
        first_value = values[0]
        last_value = values[-1]
        peak_value = max(values)
        trough_value = min(values)
        
        # Determine trend direction and magnitude
        change = last_value - first_value
        magnitude = abs(change)
        
        if magnitude < 0.05:  # Less than 5% change
            direction = "stable"
        elif change > 0:
            direction = "increasing"
        else:
            direction = "decreasing"
        
        # Calculate volatility
        if len(values) > 2:
            differences = [abs(values[i] - values[i-1]) for i in range(1, len(values))]
            volatility = sum(differences) / len(differences)
            if volatility > 0.1:  # High volatility threshold
                direction = "volatile"
        else:
            volatility = 0.0
        
        # Calculate acceleration (second derivative)
        acceleration = 0.0
        if len(values) >= 3:
            mid_point = len(values) // 2
            first_half_trend = values[mid_point] - values[0]
            second_half_trend = values[-1] - values[mid_point]
            acceleration = second_half_trend - first_half_trend
        
        # Simple prediction (linear extrapolation)
        predicted_next = last_value
        if len(values) >= 2:
            trend_rate = change / len(values)
            predicted_next = last_value + trend_rate
        
        # Trend reversal probability (heuristic)
        reversal_prob = 0.0
        if magnitude > 0.7:  # High magnitude trends are more likely to reverse
            reversal_prob = 0.3
        if volatility > 0.15:  # High volatility increases reversal chance
            reversal_prob += 0.2
        
        return PressureTrend(
            direction=direction,
            magnitude=magnitude,
            confidence=min(1.0, len(recent_entries) / 10.0),  # More data = higher confidence
            duration_hours=hours,
            volatility=volatility,
            acceleration=acceleration,
            peak_value=peak_value,
            trough_value=trough_value,
            predicted_next_value=max(0.0, min(1.0, predicted_next)),
            trend_reversal_probability=min(1.0, reversal_prob)
        )
    
    def get_average_pressure(self, hours: int = 24) -> float:
        """Get average pressure over the last N hours"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_entries = [e for e in self.entries if e.timestamp >= cutoff_time]
        
        if not recent_entries:
            return 0.0
        
        return sum(e.pressure_value for e in recent_entries) / len(recent_entries)
    
    def get_peak_pressure(self, hours: int = 24) -> float:
        """Get peak pressure over the last N hours"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_entries = [e for e in self.entries if e.timestamp >= cutoff_time]
        
        if not recent_entries:
            return 0.0
        
        return max(e.pressure_value for e in recent_entries)
    
    def get_dominant_sources_over_time(self, hours: int = 24) -> Dict[str, float]:
        """Get dominant pressure sources over time"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_entries = [e for e in self.entries if e.timestamp >= cutoff_time]
        
        source_counts = {}
        for entry in recent_entries:
            if entry.dominant_source:
                source_name = entry.dominant_source.value
                source_counts[source_name] = source_counts.get(source_name, 0) + 1
        
        # Convert to percentages
        total_entries = len(recent_entries)
        if total_entries > 0:
            return {
                source: (count / total_entries) * 100
                for source, count in source_counts.items()
            }
        
        return {}

class PressureSource(Enum):
    """Types of pressure sources in the game world"""
    FACTION_CONFLICT = "faction_conflict"
    ECONOMIC_INSTABILITY = "economic_instability"
    POPULATION_STRESS = "population_stress"
    DIPLOMATIC_TENSION = "diplomatic_tension"
    MILITARY_BUILDUP = "military_buildup"
    ENVIRONMENTAL_PRESSURE = "environmental_pressure"
    RESOURCE_SCARCITY = "resource_scarcity"
    TRADE_DISRUPTION = "trade_disruption"
    CORRUPTION = "corruption"
    SOCIAL_UNREST = "social_unrest"

@dataclass
class PressureReading:
    """Individual pressure reading from a specific source and location"""
    source: PressureSource
    value: float  # 0.0 to 1.0
    location_id: Union[str, UUID, None] = None  # region, faction, etc.
    timestamp: datetime = field(default_factory=datetime.now)
    details: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0  # how reliable this reading is
    
    def __post_init__(self):
        """Ensure pressure value is within valid range"""
        self.value = max(0.0, min(1.0, self.value))

@dataclass 
class PressureMetrics:
    """Aggregated pressure metrics for analysis"""
    total_pressure: float = 0.0
    weighted_pressure: float = 0.0
    peak_pressure: float = 0.0
    pressure_trend: float = 0.0  # positive = increasing, negative = decreasing
    time_above_threshold: float = 0.0  # seconds
    pressure_velocity: float = 0.0  # rate of change
    source_breakdown: Dict[PressureSource, float] = field(default_factory=dict)
    regional_breakdown: Dict[Union[str, UUID], float] = field(default_factory=dict)
    
    def get_dominant_source(self) -> Optional[PressureSource]:
        """Get the pressure source contributing the most pressure"""
        if not self.source_breakdown:
            return None
        return max(self.source_breakdown.items(), key=lambda x: x[1])[0]
    
    def get_pressure_level(self) -> str:
        """Get human-readable pressure level"""
        if self.weighted_pressure < 0.2:
            return "Stable"
        elif self.weighted_pressure < 0.4:
            return "Elevated"
        elif self.weighted_pressure < 0.6:
            return "High"
        elif self.weighted_pressure < 0.8:
            return "Critical"
        else:
            return "Extreme"

@dataclass
class RegionalPressure:
    """Pressure data for a specific region"""
    region_id: Union[str, UUID]
    region_name: str
    pressure_readings: List[PressureReading] = field(default_factory=list)
    metrics: PressureMetrics = field(default_factory=PressureMetrics)
    last_updated: datetime = field(default_factory=datetime.now)
    
    # Regional-specific factors
    population_density: float = 0.0
    economic_stability: float = 1.0
    political_stability: float = 1.0
    infrastructure_quality: float = 1.0
    natural_resources: float = 1.0
    strategic_importance: float = 0.5
    
    def add_reading(self, reading: PressureReading) -> None:
        """Add a new pressure reading for this region"""
        reading.location_id = self.region_id
        self.pressure_readings.append(reading)
        self.last_updated = datetime.now()
        
        # Keep only recent readings (configurable)
        max_readings = 100
        if len(self.pressure_readings) > max_readings:
            self.pressure_readings = self.pressure_readings[-max_readings:]
    
    def calculate_regional_modifier(self) -> float:
        """Calculate regional pressure modifier based on regional factors"""
        # Factors that amplify pressure
        density_factor = min(1.5, 1.0 + (self.population_density * 0.5))
        strategic_factor = 1.0 + (self.strategic_importance * 0.3)
        
        # Factors that reduce pressure  
        stability_factor = (self.economic_stability + self.political_stability) / 2.0
        infrastructure_factor = self.infrastructure_quality
        resource_factor = min(1.0, self.natural_resources)
        
        amplifiers = density_factor * strategic_factor
        dampeners = stability_factor * infrastructure_factor * resource_factor
        
        return amplifiers / max(0.1, dampeners)

@dataclass
class GlobalPressure:
    """Global pressure state across the entire world"""
    total_pressure: float = 0.0
    weighted_pressure: float = 0.0
    pressure_trend: float = 0.0
    crisis_level: str = "Stable"
    
    # Global factors
    global_economic_health: float = 1.0
    international_stability: float = 1.0
    climate_stability: float = 1.0
    resource_abundance: float = 1.0
    
    # Pressure sources
    regional_pressures: Dict[Union[str, UUID], RegionalPressure] = field(default_factory=dict)
    system_pressures: Dict[str, float] = field(default_factory=dict)
    
    # Historical data
    pressure_history: List[float] = field(default_factory=list)
    event_history: List[Dict[str, Any]] = field(default_factory=list)
    
    last_updated: datetime = field(default_factory=datetime.now)
    
    def add_regional_pressure(self, regional_pressure: RegionalPressure) -> None:
        """Add or update regional pressure data"""
        self.regional_pressures[regional_pressure.region_id] = regional_pressure
        self.last_updated = datetime.now()
    
    def calculate_global_pressure(self, weights: Dict[PressureSource, float]) -> float:
        """Calculate weighted global pressure from all sources"""
        total_weighted = 0.0
        total_weight = 0.0
        
        for region_pressure in self.regional_pressures.values():
            for reading in region_pressure.pressure_readings:
                if reading.source in weights:
                    weight = weights[reading.source]
                    modifier = region_pressure.calculate_regional_modifier()
                    weighted_value = reading.value * weight * modifier * reading.confidence
                    total_weighted += weighted_value
                    total_weight += weight
        
        if total_weight > 0:
            self.weighted_pressure = total_weighted / total_weight
        else:
            self.weighted_pressure = 0.0
            
        return self.weighted_pressure
    
    def update_pressure_history(self, max_history: int = 100) -> None:
        """Update pressure history for trend analysis"""
        self.pressure_history.append(self.weighted_pressure)
        if len(self.pressure_history) > max_history:
            self.pressure_history = self.pressure_history[-max_history:]
        
        # Calculate trend
        if len(self.pressure_history) >= 2:
            recent = self.pressure_history[-10:]  # last 10 readings
            if len(recent) >= 2:
                trend = (recent[-1] - recent[0]) / len(recent)
                self.pressure_trend = trend
    
    def get_crisis_regions(self, threshold: float = 0.7) -> List[RegionalPressure]:
        """Get regions with pressure above the crisis threshold"""
        crisis_regions = []
        for region in self.regional_pressures.values():
            if region.metrics.weighted_pressure >= threshold:
                crisis_regions.append(region)
        return crisis_regions
    
    def get_pressure_summary(self) -> Dict[str, Any]:
        """Get a summary of current pressure state"""
        return {
            "global_pressure": self.weighted_pressure,
            "pressure_trend": self.pressure_trend,
            "crisis_level": self.crisis_level,
            "total_regions": len(self.regional_pressures),
            "crisis_regions": len(self.get_crisis_regions()),
            "dominant_sources": self._get_dominant_sources(),
            "last_updated": self.last_updated.isoformat()
        }
    
    def _get_dominant_sources(self) -> Dict[str, float]:
        """Get the top pressure sources globally"""
        source_totals: Dict[PressureSource, float] = {}
        
        for region in self.regional_pressures.values():
            for reading in region.pressure_readings:
                if reading.source not in source_totals:
                    source_totals[reading.source] = 0.0
                source_totals[reading.source] += reading.value
        
        # Convert to percentages and return top sources
        total = sum(source_totals.values())
        if total > 0:
            return {
                source.value: (value / total) * 100 
                for source, value in sorted(source_totals.items(), key=lambda x: x[1], reverse=True)[:5]
            }
        return {}

@dataclass
class PressureData:
    """Complete pressure data structure combining global and regional data"""
    global_pressure: GlobalPressure = field(default_factory=GlobalPressure)
    monitoring_active: bool = True
    last_calculation: datetime = field(default_factory=datetime.now)
    
    # Performance metrics
    calculation_time_ms: float = 0.0
    readings_processed: int = 0
    errors_encountered: int = 0
    
    def get_region_pressure(self, region_id: Union[str, UUID]) -> Optional[RegionalPressure]:
        """Get pressure data for a specific region"""
        return self.global_pressure.regional_pressures.get(region_id)
    
    def add_pressure_reading(self, reading: PressureReading) -> None:
        """Add a pressure reading to the appropriate region"""
        if reading.location_id:
            region_id = reading.location_id
            if region_id not in self.global_pressure.regional_pressures:
                # Create new regional pressure data
                self.global_pressure.regional_pressures[region_id] = RegionalPressure(
                    region_id=region_id,
                    region_name=str(region_id)  # TODO: get actual name from region system
                )
            
            self.global_pressure.regional_pressures[region_id].add_reading(reading)
        
        self.readings_processed += 1
        self.last_calculation = datetime.now()
    
    def get_total_readings(self) -> int:
        """Get total number of pressure readings across all regions"""
        total = 0
        for region in self.global_pressure.regional_pressures.values():
            total += len(region.pressure_readings)
        return total
    
    def cleanup_old_readings(self, max_age_hours: int = 24) -> int:
        """Remove pressure readings older than specified hours"""
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        removed_count = 0
        
        for region in self.global_pressure.regional_pressures.values():
            original_count = len(region.pressure_readings)
            region.pressure_readings = [
                reading for reading in region.pressure_readings 
                if reading.timestamp > cutoff_time
            ]
            removed_count += original_count - len(region.pressure_readings)
        
        return removed_count 
"""
Disease System Business Models

Pure business domain models for the disease system following
Development Bible patterns - no infrastructure dependencies.

Disease types, stages, transmission modes, and treatment types are now
configured via JSON files (see data/systems/disease/disease_enums.json).
"""

from typing import Optional, List, Dict, Any, Tuple
from uuid import UUID, uuid4
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import json


# String-based types with JSON validation
DiseaseTypeStr = str  # Validated against disease_enums.json
DiseaseStageStr = str  # Validated against disease_enums.json
TransmissionModeStr = str  # Validated against disease_enums.json
TreatmentTypeStr = str  # Validated against disease_enums.json


@dataclass
class DiseaseProfile:
    """Profile defining characteristics of a specific disease"""
    id: UUID
    name: str
    disease_type: DiseaseTypeStr
    description: str
    
    # Core disease statistics
    mortality_rate: float  # Percentage who die from infection (0.0-1.0)
    transmission_rate: float  # Base transmission rate per day (0.0-1.0)
    incubation_days: int  # Days before symptoms appear
    recovery_days: int  # Days to recovery or death
    immunity_duration_days: int  # Days of immunity after recovery (0 = permanent)
    
    # Transmission characteristics
    transmission_modes: List[TransmissionModeStr] = field(default_factory=list)
    contagious_period_days: int = 7
    
    # Environmental factors (multipliers)
    crowding_factor: float = 1.5  # Multiplier for crowded conditions
    hygiene_factor: float = 1.3  # Multiplier for poor hygiene
    healthcare_factor: float = 0.7  # Multiplier with good healthcare
    temperature_factor: float = 1.0  # Temperature sensitivity
    humidity_factor: float = 1.0  # Humidity sensitivity
    
    # Seasonal preferences
    seasonal_preference: Optional[str] = None  # "winter", "summer", "spring", "autumn"
    seasonal_multiplier: float = 1.5  # Multiplier during preferred season
    
    # Population targeting
    targets_young: bool = False  # Preferentially affects children
    targets_old: bool = False    # Preferentially affects elderly
    targets_weak: bool = False   # Preferentially affects sick/malnourished
    targets_healthy: bool = False  # Targets healthy individuals (rare)
    
    # Complications and symptoms
    symptoms: List[str] = field(default_factory=list)
    complications: List[str] = field(default_factory=list)
    
    # Treatment response
    treatable_with: List[TreatmentTypeStr] = field(default_factory=list)
    treatment_effectiveness: Dict[TreatmentTypeStr, float] = field(default_factory=dict)
    
    # Economic impact
    productivity_impact: float = 0.3  # Reduction in productivity (0.0-1.0)
    treatment_cost_modifier: float = 1.0  # Cost multiplier for treatment
    
    # Magical/supernatural properties
    is_magical: bool = False
    is_cursed: bool = False
    magical_resistance_effective: bool = False
    divine_resistance_effective: bool = False
    
    # Additional properties
    properties: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate disease profile after initialization"""
        if not (0.0 <= self.mortality_rate <= 1.0):
            raise ValueError("Mortality rate must be between 0.0 and 1.0")
        if not (0.0 <= self.transmission_rate <= 1.0):
            raise ValueError("Transmission rate must be between 0.0 and 1.0")
        if self.incubation_days < 0:
            raise ValueError("Incubation days cannot be negative")
        if self.recovery_days <= 0:
            raise ValueError("Recovery days must be positive")


@dataclass
class DiseaseOutbreak:
    """Represents an active disease outbreak"""
    id: UUID
    disease_profile_id: UUID
    region_id: Optional[UUID] = None
    population_id: Optional[UUID] = None
    
    # Outbreak status
    stage: DiseaseStageStr = "emerging"
    is_active: bool = True
    
    # Current statistics
    infected_count: int = 0
    recovered_count: int = 0
    death_count: int = 0
    immune_count: int = 0
    
    # Progression tracking
    days_active: int = 0
    peak_infected: int = 0
    peak_day: Optional[int] = None
    
    # Environmental modifiers currently affecting outbreak
    current_crowding_modifier: float = 1.0
    current_hygiene_modifier: float = 1.0
    current_healthcare_modifier: float = 1.0
    current_seasonal_modifier: float = 1.0
    current_temperature_modifier: float = 1.0
    current_humidity_modifier: float = 1.0
    
    # Treatment efforts
    active_treatments: List[TreatmentTypeStr] = field(default_factory=list)
    treatment_effectiveness: float = 1.0
    quarantine_active: bool = False
    quarantine_effectiveness: float = 0.0
    
    # Economic impact
    economic_damage: float = 0.0
    trade_disruption: float = 0.0
    
    # Timing
    start_date: datetime = field(default_factory=datetime.utcnow)
    end_date: Optional[datetime] = None
    
    # Origin tracking
    origin_source: Optional[str] = None  # "trade_route", "refugee_migration", etc.
    patient_zero_location: Optional[str] = None
    
    # Quest and event generation
    quests_generated: List[UUID] = field(default_factory=list)
    events_triggered: List[str] = field(default_factory=list)
    
    # Additional properties
    properties: Dict[str, Any] = field(default_factory=dict)


@dataclass 
class DiseaseData:
    """Business domain data structure for diseases"""
    id: UUID
    name: str
    description: Optional[str] = None
    disease_type: DiseaseTypeStr = "fever"
    status: str = 'active'
    
    # Disease characteristics
    mortality_rate: float = 0.1
    transmission_rate: float = 0.3
    incubation_days: int = 3
    recovery_days: int = 7
    immunity_duration_days: int = 365
    
    # Environmental factors
    crowding_factor: float = 1.5
    hygiene_factor: float = 1.3
    healthcare_factor: float = 0.7
    
    # Targeting
    targets_young: bool = False
    targets_old: bool = False
    targets_weak: bool = False
    
    # Metadata
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    properties: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CreateDiseaseData:
    """Business domain data for disease creation"""
    name: str
    description: Optional[str] = None
    disease_type: DiseaseTypeStr = "fever"
    status: str = 'active'
    
    # Disease characteristics
    mortality_rate: Optional[float] = None
    transmission_rate: Optional[float] = None
    incubation_days: Optional[int] = None
    recovery_days: Optional[int] = None
    immunity_duration_days: Optional[int] = None
    
    # Environmental factors  
    crowding_factor: Optional[float] = None
    hygiene_factor: Optional[float] = None
    healthcare_factor: Optional[float] = None
    
    # Targeting
    targets_young: Optional[bool] = None
    targets_old: Optional[bool] = None
    targets_weak: Optional[bool] = None
    
    properties: Dict[str, Any] = field(default_factory=dict)


@dataclass
class UpdateDiseaseData:
    """Business domain data for disease updates"""
    update_fields: Dict[str, Any] = field(default_factory=dict)
    
    def get_fields(self) -> Dict[str, Any]:
        return self.update_fields


@dataclass
class DiseaseSimulationState:
    """State data for disease simulation progression"""
    current_day: int = 0
    total_population: int = 0
    susceptible: int = 0
    infected: int = 0
    recovered: int = 0
    dead: int = 0
    immune: int = 0
    
    # Environmental state
    temperature: float = 20.0  # Celsius
    humidity: float = 0.5      # 0.0-1.0
    population_density: float = 1.0
    hygiene_level: float = 1.0  # 0.0-2.0 (poor to excellent)
    healthcare_quality: float = 1.0  # 0.0-2.0 (none to excellent)
    
    # Treatment state
    active_treatments: List[TreatmentTypeStr] = field(default_factory=list)
    treatment_supplies: Dict[TreatmentTypeStr, float] = field(default_factory=dict)
    
    # Economic state
    trade_flow: float = 1.0  # 0.0-2.0 (blocked to thriving)
    resource_availability: float = 1.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'current_day': self.current_day,
            'total_population': self.total_population,
            'susceptible': self.susceptible,
            'infected': self.infected,
            'recovered': self.recovered,
            'dead': self.dead,
            'immune': self.immune,
            'temperature': self.temperature,
            'humidity': self.humidity,
            'population_density': self.population_density,
            'hygiene_level': self.hygiene_level,
            'healthcare_quality': self.healthcare_quality,
            'active_treatments': self.active_treatments,
            'treatment_supplies': self.treatment_supplies,
            'trade_flow': self.trade_flow,
            'resource_availability': self.resource_availability
        }


@dataclass
class DiseaseImpactAssessment:
    """Assessment of disease impact across multiple dimensions"""
    outbreak_id: UUID
    assessment_date: datetime
    
    # Population impact
    population_mortality_rate: float
    population_morbidity_rate: float
    demographic_impact: Dict[str, float]  # by age group, occupation, etc.
    
    # Economic impact
    productivity_loss: float
    trade_disruption: float
    treatment_costs: float
    infrastructure_damage: float
    
    # Social impact
    social_cohesion_impact: float
    migration_pressure: float
    civil_unrest_risk: float
    
    # Political impact
    government_stability_impact: float
    faction_relations_impact: Dict[UUID, float]
    
    # Long-term consequences
    population_trauma: float
    economic_recovery_time: int  # days
    social_recovery_time: int    # days
    
    def total_impact_score(self) -> float:
        """Calculate overall impact score (0.0-10.0)"""
        return min(10.0, (
            self.population_mortality_rate * 3.0 +
            self.economic_impact_score() * 2.0 +
            self.social_impact_score() * 2.0 +
            self.political_impact_score() * 3.0
        ))
    
    def economic_impact_score(self) -> float:
        """Calculate economic impact score (0.0-10.0)"""
        return min(10.0, (
            self.productivity_loss * 3.0 +
            self.trade_disruption * 2.0 +
            (self.treatment_costs / 1000.0) +  # Normalize costs
            self.infrastructure_damage * 4.0
        ))
    
    def social_impact_score(self) -> float:
        """Calculate social impact score (0.0-10.0)"""
        return min(10.0, (
            (1.0 - self.social_cohesion_impact) * 3.0 +
            self.migration_pressure * 2.0 +
            self.civil_unrest_risk * 5.0
        ))
    
    def political_impact_score(self) -> float:
        """Calculate political impact score (0.0-10.0)"""
        faction_avg_impact = sum(abs(impact) for impact in self.faction_relations_impact.values()) / max(1, len(self.faction_relations_impact))
        return min(10.0, (
            (1.0 - self.government_stability_impact) * 6.0 +
            faction_avg_impact * 4.0
        )) 
"""
Disease System API Schemas

Comprehensive Pydantic models for disease system API validation and serialization.
Uses JSON-based configuration for enum validation instead of hard-coded enums.
"""

from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, validator

# Import validation functions from config loader
try:
    from backend.infrastructure.config_loaders.disease_config_loader import (
        validate_disease_type,
        validate_disease_stage, 
        validate_transmission_mode,
        validate_treatment_type,
        get_valid_disease_types,
        get_valid_disease_stages,
        get_valid_transmission_modes,
        get_valid_treatment_types
    )
except ImportError:
    # Fallback validation functions if config loader not available
    def validate_disease_type(value: str) -> bool:
        return True
    def validate_disease_stage(value: str) -> bool:
        return True
    def validate_transmission_mode(value: str) -> bool:
        return True
    def validate_treatment_type(value: str) -> bool:
        return True
    def get_valid_disease_types() -> List[str]:
        return []
    def get_valid_disease_stages() -> List[str]:
        return []
    def get_valid_transmission_modes() -> List[str]:
        return []
    def get_valid_treatment_types() -> List[str]:
        return []


# Base Disease Schemas
class DiseaseBase(BaseModel):
    """Base disease schema with common fields"""
    name: str = Field(..., min_length=1, max_length=200, description="Disease name")
    description: Optional[str] = Field(None, max_length=1000, description="Disease description")
    disease_type: str = Field(..., description="Type of disease (validated against JSON config)")
    status: str = Field(default="active", description="Disease status")
    mortality_rate: float = Field(default=0.1, ge=0.0, le=1.0, description="Mortality rate (0-1)")
    transmission_rate: float = Field(default=0.3, ge=0.0, le=1.0, description="Transmission rate (0-1)")
    incubation_days: int = Field(default=3, ge=1, le=365, description="Incubation period in days")
    recovery_days: int = Field(default=7, ge=1, le=365, description="Recovery period in days")
    immunity_duration_days: int = Field(default=365, ge=0, description="Immunity duration in days")
    crowding_factor: float = Field(default=1.5, ge=0.1, le=10.0, description="Crowding transmission multiplier")
    hygiene_factor: float = Field(default=1.3, ge=0.1, le=10.0, description="Hygiene transmission multiplier")
    healthcare_factor: float = Field(default=0.7, ge=0.1, le=10.0, description="Healthcare effectiveness multiplier")
    targets_young: bool = Field(default=False, description="Preferentially targets young populations")
    targets_old: bool = Field(default=False, description="Preferentially targets old populations")
    targets_weak: bool = Field(default=False, description="Preferentially targets weak populations")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Additional disease properties")

    @validator('disease_type')
    def validate_disease_type_field(cls, v):
        if not validate_disease_type(v):
            valid_types = get_valid_disease_types()
            raise ValueError(f"Invalid disease type '{v}'. Valid types: {valid_types}")
        return v


class DiseaseCreate(DiseaseBase):
    """Schema for creating a new disease"""
    pass


class DiseaseUpdate(BaseModel):
    """Schema for updating an existing disease"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    disease_type: Optional[str] = None
    status: Optional[str] = None
    mortality_rate: Optional[float] = Field(None, ge=0.0, le=1.0)
    transmission_rate: Optional[float] = Field(None, ge=0.0, le=1.0)
    incubation_days: Optional[int] = Field(None, ge=1, le=365)
    recovery_days: Optional[int] = Field(None, ge=1, le=365)
    immunity_duration_days: Optional[int] = Field(None, ge=0)
    crowding_factor: Optional[float] = Field(None, ge=0.1, le=10.0)
    hygiene_factor: Optional[float] = Field(None, ge=0.1, le=10.0)
    healthcare_factor: Optional[float] = Field(None, ge=0.1, le=10.0)
    targets_young: Optional[bool] = None
    targets_old: Optional[bool] = None
    targets_weak: Optional[bool] = None
    properties: Optional[Dict[str, Any]] = None

    @validator('disease_type')
    def validate_disease_type_field(cls, v):
        if v is not None and not validate_disease_type(v):
            valid_types = get_valid_disease_types()
            raise ValueError(f"Invalid disease type '{v}'. Valid types: {valid_types}")
        return v


class DiseaseResponse(DiseaseBase):
    """Schema for disease API responses"""
    id: UUID = Field(..., description="Disease unique identifier")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

    class Config:
        from_attributes = True


class DiseaseListResponse(BaseModel):
    """Schema for paginated disease list responses"""
    diseases: List[DiseaseResponse] = Field(..., description="List of diseases")
    total: int = Field(..., description="Total number of diseases")
    page: int = Field(..., description="Current page number")
    size: int = Field(..., description="Page size")
    pages: int = Field(..., description="Total number of pages")


# Outbreak Schemas
class OutbreakBase(BaseModel):
    """Base outbreak schema with common fields"""
    disease_profile_id: UUID = Field(..., description="Disease profile identifier")
    region_id: Optional[UUID] = Field(None, description="Affected region identifier")
    population_id: Optional[UUID] = Field(None, description="Affected population identifier")
    stage: str = Field(default="emerging", description="Current outbreak stage (validated against JSON config)")
    infected_count: int = Field(default=1, ge=0, description="Number of infected individuals")
    recovered_count: int = Field(default=0, ge=0, description="Number of recovered individuals")
    deceased_count: int = Field(default=0, ge=0, description="Number of deceased individuals")
    immune_count: int = Field(default=0, ge=0, description="Number of immune individuals")
    environmental_factors: Dict[str, float] = Field(default_factory=dict, description="Environmental modifiers")
    is_active: bool = Field(default=True, description="Whether outbreak is active")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Additional outbreak properties")

    @validator('stage')
    def validate_stage_field(cls, v):
        if not validate_disease_stage(v):
            valid_stages = get_valid_disease_stages()
            raise ValueError(f"Invalid disease stage '{v}'. Valid stages: {valid_stages}")
        return v


class OutbreakCreate(OutbreakBase):
    """Schema for creating a new outbreak"""
    pass


class OutbreakUpdate(BaseModel):
    """Schema for updating an existing outbreak"""
    stage: Optional[str] = None
    infected_count: Optional[int] = Field(None, ge=0)
    recovered_count: Optional[int] = Field(None, ge=0)
    deceased_count: Optional[int] = Field(None, ge=0)
    immune_count: Optional[int] = Field(None, ge=0)
    environmental_factors: Optional[Dict[str, float]] = None
    is_active: Optional[bool] = None
    properties: Optional[Dict[str, Any]] = None

    @validator('stage')
    def validate_stage_field(cls, v):
        if v is not None and not validate_disease_stage(v):
            valid_stages = get_valid_disease_stages()
            raise ValueError(f"Invalid disease stage '{v}'. Valid stages: {valid_stages}")
        return v


class OutbreakResponse(OutbreakBase):
    """Schema for outbreak API responses"""
    id: UUID = Field(..., description="Outbreak unique identifier")
    started_at: datetime = Field(..., description="Outbreak start timestamp")
    ended_at: Optional[datetime] = Field(None, description="Outbreak end timestamp")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

    class Config:
        from_attributes = True


class OutbreakListResponse(BaseModel):
    """Schema for paginated outbreak list responses"""
    outbreaks: List[OutbreakResponse] = Field(..., description="List of outbreaks")
    total: int = Field(..., description="Total number of outbreaks")
    page: int = Field(..., description="Current page number")
    size: int = Field(..., description="Page size")
    pages: int = Field(..., description="Total number of pages")


class OutbreakProgressResponse(BaseModel):
    """Schema for outbreak progression results"""
    outbreak_id: UUID = Field(..., description="Outbreak identifier")
    previous_stage: str = Field(..., description="Previous outbreak stage")
    current_stage: str = Field(..., description="Current outbreak stage")
    new_infections: int = Field(..., description="New infections this cycle")
    new_recoveries: int = Field(..., description="New recoveries this cycle")
    new_deaths: int = Field(..., description="New deaths this cycle")
    transmission_rate: float = Field(..., description="Effective transmission rate")
    severity_score: float = Field(..., description="Outbreak severity score")
    stage_changed: bool = Field(..., description="Whether stage changed")
    environmental_impact: Dict[str, float] = Field(..., description="Environmental factor impacts")


# Disease Profile Schemas
class DiseaseProfileResponse(BaseModel):
    """Schema for disease profile responses"""
    id: str = Field(..., description="Profile identifier")
    name: str = Field(..., description="Profile name")
    disease_type: str = Field(..., description="Disease type")
    description: str = Field(..., description="Profile description")
    transmission_modes: List[str] = Field(..., description="Transmission modes")
    base_mortality_rate: float = Field(..., description="Base mortality rate")
    base_transmission_rate: float = Field(..., description="Base transmission rate")
    incubation_period: Dict[str, int] = Field(..., description="Incubation period range")
    recovery_period: Dict[str, int] = Field(..., description="Recovery period range")
    immunity_duration: Dict[str, int] = Field(..., description="Immunity duration range")
    environmental_modifiers: Dict[str, Dict[str, float]] = Field(..., description="Environmental modifiers")
    age_susceptibility: Dict[str, float] = Field(..., description="Age-based susceptibility")
    treatment_effectiveness: Dict[str, float] = Field(..., description="Treatment effectiveness")
    properties: Dict[str, Any] = Field(..., description="Additional properties")

    @validator('disease_type')
    def validate_disease_type_field(cls, v):
        if not validate_disease_type(v):
            valid_types = get_valid_disease_types()
            raise ValueError(f"Invalid disease type '{v}'. Valid types: {valid_types}")
        return v

    @validator('transmission_modes')
    def validate_transmission_modes_field(cls, v):
        for mode in v:
            if not validate_transmission_mode(mode):
                valid_modes = get_valid_transmission_modes()
                raise ValueError(f"Invalid transmission mode '{mode}'. Valid modes: {valid_modes}")
        return v


class DiseaseProfileListResponse(BaseModel):
    """Schema for disease profile list responses"""
    profiles: List[DiseaseProfileResponse] = Field(..., description="List of disease profiles")
    total: int = Field(..., description="Total number of profiles")


# Configuration Schemas
class EnvironmentalFactorsResponse(BaseModel):
    """Schema for environmental factors configuration"""
    temperature_effects: Dict[str, float] = Field(..., description="Temperature impact modifiers")
    humidity_effects: Dict[str, float] = Field(..., description="Humidity impact modifiers")
    crowding_multipliers: Dict[str, float] = Field(..., description="Crowding multipliers")
    hygiene_multipliers: Dict[str, float] = Field(..., description="Hygiene multipliers")
    healthcare_multipliers: Dict[str, float] = Field(..., description="Healthcare multipliers")


class OutbreakParametersResponse(BaseModel):
    """Schema for outbreak parameters configuration"""
    default_initial_infected: int = Field(..., description="Default initial infected count")
    max_outbreak_duration_days: int = Field(..., description="Maximum outbreak duration")
    stage_transition_thresholds: Dict[str, float] = Field(..., description="Stage transition thresholds")
    severity_calculation_weights: Dict[str, float] = Field(..., description="Severity calculation weights")


class InterventionEffectivenessResponse(BaseModel):
    """Schema for intervention effectiveness configuration"""
    quarantine_effectiveness: Dict[str, float] = Field(..., description="Quarantine effectiveness by disease type")
    medicine_effectiveness: Dict[str, float] = Field(..., description="Medicine effectiveness by disease type")
    ritual_effectiveness: Dict[str, float] = Field(..., description="Ritual effectiveness by disease type")
    magical_healing_effectiveness: Dict[str, float] = Field(..., description="Magical healing effectiveness")
    hygiene_improvement_effectiveness: Dict[str, float] = Field(..., description="Hygiene improvement effectiveness")


# Analysis Schemas
class DiseaseImpactResponse(BaseModel):
    """Schema for disease impact assessment responses"""
    outbreak_id: UUID = Field(..., description="Outbreak identifier")
    total_affected: int = Field(..., description="Total affected population")
    mortality_rate: float = Field(..., description="Actual mortality rate")
    economic_impact: float = Field(..., description="Economic impact score")
    social_impact: float = Field(..., description="Social impact score")
    duration_days: int = Field(..., description="Outbreak duration in days")
    peak_infected: int = Field(..., description="Peak infected count")
    severity_classification: str = Field(..., description="Severity classification")
    affected_demographics: Dict[str, int] = Field(..., description="Affected demographics breakdown")


class DiseaseSimulationResponse(BaseModel):
    """Schema for disease simulation responses"""
    simulation_id: str = Field(..., description="Simulation identifier")
    disease_type: str = Field(..., description="Simulated disease type")
    initial_conditions: Dict[str, Any] = Field(..., description="Initial simulation conditions")
    final_results: Dict[str, Any] = Field(..., description="Final simulation results")
    progression_timeline: List[Dict[str, Any]] = Field(..., description="Progression timeline")
    environmental_impacts: Dict[str, float] = Field(..., description="Environmental factor impacts")

    @validator('disease_type')
    def validate_disease_type_field(cls, v):
        if not validate_disease_type(v):
            valid_types = get_valid_disease_types()
            raise ValueError(f"Invalid disease type '{v}'. Valid types: {valid_types}")
        return v


class TreatmentApplicationResponse(BaseModel):
    """Schema for treatment application responses"""
    outbreak_id: UUID = Field(..., description="Outbreak identifier")
    treatment_type: str = Field(..., description="Applied treatment type")
    effectiveness: float = Field(..., description="Treatment effectiveness")
    infected_before: int = Field(..., description="Infected count before treatment")
    infected_after: int = Field(..., description="Infected count after treatment")
    transmission_reduction: float = Field(..., description="Transmission rate reduction")
    mortality_reduction: float = Field(..., description="Mortality rate reduction")
    cost: float = Field(..., description="Treatment cost")
    success: bool = Field(..., description="Whether treatment was successful")

    @validator('treatment_type')
    def validate_treatment_type_field(cls, v):
        if not validate_treatment_type(v):
            valid_types = get_valid_treatment_types()
            raise ValueError(f"Invalid treatment type '{v}'. Valid types: {valid_types}")
        return v


# System Schemas
class DiseaseSystemStatusResponse(BaseModel):
    """Schema for disease system status responses"""
    status: str = Field(..., description="Overall system status")
    active_diseases: int = Field(..., description="Number of active diseases")
    active_outbreaks: int = Field(..., description="Number of active outbreaks")
    configured_profiles: int = Field(..., description="Number of configured disease profiles")
    database_connected: bool = Field(..., description="Database connection status")
    config_loaded: bool = Field(..., description="Configuration loaded status")
    last_updated: datetime = Field(..., description="Last status update timestamp")
    error: Optional[str] = Field(None, description="Error message if system unhealthy")


# Pagination and Filter Schemas
class DiseaseFilters(BaseModel):
    """Schema for disease filtering parameters"""
    disease_type: Optional[str] = None
    status: Optional[str] = None
    min_mortality_rate: Optional[float] = Field(None, ge=0.0, le=1.0)
    max_mortality_rate: Optional[float] = Field(None, ge=0.0, le=1.0)
    targets_young: Optional[bool] = None
    targets_old: Optional[bool] = None
    targets_weak: Optional[bool] = None

    @validator('disease_type')
    def validate_disease_type_field(cls, v):
        if v is not None and not validate_disease_type(v):
            valid_types = get_valid_disease_types()
            raise ValueError(f"Invalid disease type '{v}'. Valid types: {valid_types}")
        return v


class OutbreakFilters(BaseModel):
    """Schema for outbreak filtering parameters"""
    stage: Optional[str] = None
    region_id: Optional[UUID] = None
    population_id: Optional[UUID] = None
    disease_profile_id: Optional[UUID] = None
    is_active: Optional[bool] = None
    min_infected: Optional[int] = Field(None, ge=0)
    max_infected: Optional[int] = Field(None, ge=0)

    @validator('stage')
    def validate_stage_field(cls, v):
        if v is not None and not validate_disease_stage(v):
            valid_stages = get_valid_disease_stages()
            raise ValueError(f"Invalid disease stage '{v}'. Valid stages: {valid_stages}")
        return v


class PaginationParams(BaseModel):
    """Schema for pagination parameters"""
    page: int = Field(default=1, ge=1, description="Page number")
    size: int = Field(default=50, ge=1, le=1000, description="Page size") 
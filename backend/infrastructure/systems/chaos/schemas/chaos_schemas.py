"""
Chaos System Schemas - Pydantic models for API requests and responses
"""

from pydantic import BaseModel, Field, validator, ConfigDict
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum

from backend.infrastructure.systems.chaos.models.chaos_level import ChaosLevel

class EventSeverity(str, Enum):
    """Event severity levels"""
    MINOR = "minor"
    MODERATE = "moderate"
    MAJOR = "major"
    SEVERE = "severe"
    CATASTROPHIC = "catastrophic"

class MitigationType(str, Enum):
    """Mitigation factor types"""
    DIPLOMATIC = "diplomatic"
    ECONOMIC = "economic"
    INFRASTRUCTURE = "infrastructure"
    LEADERSHIP = "leadership"
    MILITARY = "military"

class ChaosStateResponse(BaseModel):
    """Response model for chaos status"""
    chaos_level: ChaosLevel
    chaos_score: float = Field(..., ge=0.0, le=1.0, description="Chaos score between 0.0 and 1.0")
    pressure_sources: Dict[str, float] = Field(default_factory=dict)
    active_events_count: int = Field(default=0, ge=0)
    region_id: Optional[str] = None
    last_updated: datetime
    threshold_exceeded: bool = False
    next_calculation: Optional[datetime] = None
    
    model_config = ConfigDict(json_encoders={
            datetime: lambda v: v.isoformat()
        })

class PressureSourceData(BaseModel):
    """Pressure source information"""
    source_name: str
    current_value: float = Field(..., ge=0.0, le=1.0)
    weighted_value: float = Field(..., ge=0.0)
    weight: float = Field(..., gt=0.0)
    contributors: List[str] = Field(default_factory=list)
    trend: Optional[str] = None  # "increasing", "decreasing", "stable"

class PressureSummaryResponse(BaseModel):
    """Response model for pressure summary"""
    total_pressure_score: float = Field(..., ge=0.0)
    pressure_sources: List[PressureSourceData]
    regional_breakdown: Dict[str, float] = Field(default_factory=dict)
    highest_pressure_region: Optional[str] = None
    lowest_pressure_region: Optional[str] = None
    trending_up: List[str] = Field(default_factory=list)
    trending_down: List[str] = Field(default_factory=list)
    last_updated: datetime
    
    model_config = ConfigDict(json_encoders={
            datetime: lambda v: v.isoformat()
        })

class ChaosEventData(BaseModel):
    """Chaos event information"""
    event_id: str
    event_type: str
    region_id: str
    severity: EventSeverity
    trigger_time: datetime
    duration_hours: float = Field(..., gt=0.0)
    chaos_score: float = Field(..., ge=0.0, le=1.0)
    affected_systems: List[str] = Field(default_factory=list)
    pressure_sources: Dict[str, float] = Field(default_factory=dict)
    status: str = "active"
    cascading_events: List[str] = Field(default_factory=list)
    
    model_config = ConfigDict(json_encoders={
            datetime: lambda v: v.isoformat()
        })

class ActiveEventsResponse(BaseModel):
    """Response model for active events"""
    total_active_events: int = Field(default=0, ge=0)
    events: List[ChaosEventData]
    events_by_region: Dict[str, int] = Field(default_factory=dict)
    events_by_severity: Dict[str, int] = Field(default_factory=dict)
    events_by_type: Dict[str, int] = Field(default_factory=dict)
    most_affected_region: Optional[str] = None
    last_updated: datetime
    
    model_config = ConfigDict(json_encoders={
            datetime: lambda v: v.isoformat()
        })

class MitigationRequest(BaseModel):
    """Request model for applying mitigation"""
    mitigation_type: MitigationType
    effectiveness: float = Field(..., ge=0.0, le=1.0, description="Mitigation effectiveness 0.0 to 1.0")
    duration_hours: float = Field(..., gt=0.0, description="Duration in hours")
    source_id: str = Field(..., min_length=1, description="Source identifier for the mitigation")
    source_type: str = Field(..., min_length=1, description="Type of source applying mitigation")
    description: str = Field(default="", description="Description of the mitigation")
    affected_regions: Optional[List[str]] = Field(default=None, description="Regions affected by mitigation")
    affected_sources: Optional[List[str]] = Field(default=None, description="Pressure sources affected")
    
    @validator('affected_regions')
    def validate_regions(cls, v):
        if v is not None and len(v) == 0:
            return None
        return v
    
    @validator('affected_sources')
    def validate_sources(cls, v):
        if v is not None and len(v) == 0:
            return None
        return v

class MitigationResponse(BaseModel):
    """Response model for mitigation application"""
    success: bool
    mitigation_id: Optional[str] = None
    message: str
    actual_effectiveness: Optional[float] = None
    actual_duration: Optional[float] = None
    affected_pressure_sources: List[str] = Field(default_factory=list)
    expires_at: Optional[datetime] = None
    
    model_config = ConfigDict(json_encoders={
            datetime: lambda v: v.isoformat()
        })

class EventTriggerRequest(BaseModel):
    """Request model for force triggering events"""
    event_type: str = Field(..., min_length=1, description="Type of event to trigger")
    severity: EventSeverity = Field(default=EventSeverity.MODERATE, description="Event severity")
    regions: Optional[List[str]] = Field(default=None, description="Target regions for the event")
    
    @validator('regions')
    def validate_regions(cls, v):
        if v is not None and len(v) == 0:
            return None
        return v

class EventTriggerResponse(BaseModel):
    """Response model for event triggering"""
    success: bool
    message: str
    event_id: Optional[str] = None
    triggered_events: List[str] = Field(default_factory=list)
    affected_regions: List[str] = Field(default_factory=list)
    cascading_events_scheduled: int = Field(default=0, ge=0)

class SystemMetricsResponse(BaseModel):
    """Response model for system metrics"""
    chaos_engine_status: str
    uptime_hours: float = Field(..., ge=0.0)
    calculations_performed: int = Field(default=0, ge=0)
    events_triggered: int = Field(default=0, ge=0)
    average_chaos_score: float = Field(..., ge=0.0, le=1.0)
    peak_chaos_score: float = Field(..., ge=0.0, le=1.0)
    active_mitigations: int = Field(default=0, ge=0)
    system_integrations: int = Field(default=0, ge=0)
    performance_metrics: Dict[str, Any] = Field(default_factory=dict)
    last_updated: datetime
    
    model_config = ConfigDict(json_encoders={
            datetime: lambda v: v.isoformat()
        })

class SystemHealthResponse(BaseModel):
    """Response model for system health"""
    overall_health: str  # "healthy", "degraded", "unhealthy"
    chaos_engine_running: bool
    pressure_monitoring_active: bool
    event_dispatching_healthy: bool
    system_integrations_healthy: Dict[str, bool] = Field(default_factory=dict)
    error_count_last_hour: int = Field(default=0, ge=0)
    warning_count_last_hour: int = Field(default=0, ge=0)
    last_health_check: datetime
    issues: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    
    model_config = ConfigDict(json_encoders={
            datetime: lambda v: v.isoformat()
        })

class ChaosConfigUpdate(BaseModel):
    """Request model for updating chaos configuration"""
    chaos_threshold: Optional[float] = Field(None, ge=0.0, le=1.0)
    region_cooldown_hours: Optional[float] = Field(None, gt=0.0)
    event_cooldown_hours: Optional[float] = Field(None, gt=0.0)
    pressure_weights: Optional[Dict[str, float]] = Field(None)
    monitoring_interval_seconds: Optional[int] = Field(None, gt=0)
    
    @validator('pressure_weights')
    def validate_pressure_weights(cls, v):
        if v is not None:
            for weight in v.values():
                if not isinstance(weight, (int, float)) or weight < 0:
                    raise ValueError("All pressure weights must be non-negative numbers")
        return v

class RegionalChaosData(BaseModel):
    """Regional chaos breakdown"""
    region_id: str
    chaos_score: float = Field(..., ge=0.0, le=1.0)
    chaos_level: ChaosLevel
    pressure_sources: Dict[str, float] = Field(default_factory=dict)
    active_events: int = Field(default=0, ge=0)
    active_mitigations: int = Field(default=0, ge=0)
    last_event_time: Optional[datetime] = None
    next_potential_event: Optional[datetime] = None
    cooldown_active: bool = False
    
    model_config = ConfigDict(json_encoders={
            datetime: lambda v: v.isoformat()
        })

class RegionalAnalysisResponse(BaseModel):
    """Response model for regional chaos analysis"""
    total_regions: int = Field(..., ge=0)
    regions: List[RegionalChaosData]
    highest_chaos_region: Optional[str] = None
    lowest_chaos_region: Optional[str] = None
    regions_in_cooldown: int = Field(default=0, ge=0)
    regions_at_risk: List[str] = Field(default_factory=list)
    last_updated: datetime
    
    model_config = ConfigDict(json_encoders={
            datetime: lambda v: v.isoformat()
        })

# Error response models
class ErrorResponse(BaseModel):
    """Standard error response"""
    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    
    model_config = ConfigDict(json_encoders={
            datetime: lambda v: v.isoformat()
        })

class ValidationErrorResponse(BaseModel):
    """Validation error response"""
    error: str = "Validation Error"
    detail: str
    invalid_fields: List[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.now)
    
    model_config = ConfigDict(json_encoders={
            datetime: lambda v: v.isoformat()
        }) 
"""
Station Schemas

Pydantic models for station-related API requests and responses.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
import uuid

class StationBaseSchema(BaseModel):
    """Base schema for crafting stations."""
    name: str = Field(..., min_length=1, max_length=255, description="Station name")
    description: str = Field(default="", description="Station description")
    station_type: str = Field(..., description="Type of station (smithy, alchemy, etc.)")
    level: int = Field(ge=1, le=100, default=1, description="Station level")
    capacity: int = Field(ge=1, default=1, description="How many can use simultaneously")
    efficiency_bonus: float = Field(ge=0.1, default=1.0, description="Speed multiplier")
    quality_bonus: float = Field(ge=0.0, default=0.0, description="Quality improvement chance")
    is_active: bool = Field(default=True, description="Whether station is active")
    is_public: bool = Field(default=True, description="Whether others can use it")
    location_id: Optional[str] = Field(None, description="Location where station is placed")
    owner_id: Optional[str] = Field(None, description="Owner character ID")

class StationCreateSchema(StationBaseSchema):
    """Schema for creating a new station."""
    upgrade_level: int = Field(ge=0, default=0, description="Upgrade level")
    allowed_categories: List[str] = Field(default_factory=list, description="What can be crafted")
    required_materials: Dict[str, int] = Field(default_factory=dict, description="Materials to build/upgrade")
    special_abilities: List[str] = Field(default_factory=list, description="Special crafting abilities")
    maintenance_cost: Dict[str, int] = Field(default_factory=dict, description="Upkeep requirements")
    station_metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class StationUpdateSchema(BaseModel):
    """Schema for updating a station."""
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Station name")
    description: Optional[str] = Field(None, description="Station description")
    level: Optional[int] = Field(None, ge=1, le=100, description="Station level")
    capacity: Optional[int] = Field(None, ge=1, description="How many can use simultaneously")
    efficiency_bonus: Optional[float] = Field(None, ge=0.1, description="Speed multiplier")
    quality_bonus: Optional[float] = Field(None, ge=0.0, description="Quality improvement chance")
    is_active: Optional[bool] = Field(None, description="Whether station is active")
    is_public: Optional[bool] = Field(None, description="Whether others can use it")
    location_id: Optional[str] = Field(None, description="Location where station is placed")
    owner_id: Optional[str] = Field(None, description="Owner character ID")
    upgrade_level: Optional[int] = Field(None, ge=0, description="Upgrade level")

class StationResponseSchema(StationBaseSchema):
    """Schema for station responses."""
    id: uuid.UUID = Field(..., description="Station ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    upgrade_level: int = Field(default=0, description="Upgrade level")
    allowed_categories: List[str] = Field(default_factory=list, description="What can be crafted")
    required_materials: Dict[str, int] = Field(default_factory=dict, description="Materials to build/upgrade")
    special_abilities: List[str] = Field(default_factory=list, description="Special crafting abilities")
    maintenance_cost: Dict[str, int] = Field(default_factory=dict, description="Upkeep requirements")
    station_metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    # Computed fields
    current_users: int = Field(default=0, description="Current number of users")
    is_available: bool = Field(default=True, description="Whether station is available for use")
    efficiency_multiplier: float = Field(default=1.0, description="Total efficiency multiplier")
    total_quality_bonus: float = Field(default=0.0, description="Total quality bonus")

    model_config = ConfigDict(from_attributes=True)

class StationListResponseSchema(BaseModel):
    """Schema for station list responses."""
    stations: List[StationResponseSchema] = Field(..., description="List of stations")
    total: int = Field(..., description="Total number of stations")
    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Items per page")

class StationSearchSchema(BaseModel):
    """Schema for station search requests."""
    search_term: Optional[str] = Field(None, description="Search term for name/description")
    station_type: Optional[str] = Field(None, description="Filter by station type")
    location_id: Optional[str] = Field(None, description="Filter by location")
    owner_id: Optional[str] = Field(None, description="Filter by owner")
    min_level: Optional[int] = Field(None, ge=1, description="Minimum station level")
    max_level: Optional[int] = Field(None, ge=1, description="Maximum station level")
    min_capacity: Optional[int] = Field(None, ge=1, description="Minimum capacity")
    min_efficiency: Optional[float] = Field(None, ge=0.1, description="Minimum efficiency bonus")
    is_public_only: bool = Field(default=False, description="Show only public stations")
    is_available_only: bool = Field(default=False, description="Show only available stations")
    character_id: Optional[str] = Field(None, description="Character ID for availability check")
    page: int = Field(ge=1, default=1, description="Page number")
    per_page: int = Field(ge=1, le=100, default=20, description="Items per page")

class StationUseSchema(BaseModel):
    """Schema for using a station."""
    character_id: str = Field(..., description="Character ID")
    recipe_id: Optional[uuid.UUID] = Field(None, description="Recipe to craft")
    duration: Optional[int] = Field(None, ge=1, description="Expected usage duration in seconds")
    context: Dict[str, Any] = Field(default_factory=dict, description="Usage context")

class StationUseResponseSchema(BaseModel):
    """Schema for station use responses."""
    station_id: uuid.UUID = Field(..., description="Station ID")
    character_id: str = Field(..., description="Character ID")
    session_id: str = Field(..., description="Usage session ID")
    start_time: datetime = Field(..., description="When usage started")
    estimated_end_time: Optional[datetime] = Field(None, description="Estimated completion time")
    efficiency_multiplier: float = Field(..., description="Applied efficiency multiplier")
    quality_bonus: float = Field(..., description="Applied quality bonus")
    is_active: bool = Field(default=True, description="Whether session is active")

class StationStatusSchema(BaseModel):
    """Schema for station status responses."""
    station_id: uuid.UUID = Field(..., description="Station ID")
    is_active: bool = Field(..., description="Whether station is active")
    is_available: bool = Field(..., description="Whether station is available for use")
    current_users: int = Field(..., description="Current number of users")
    max_capacity: int = Field(..., description="Maximum capacity")
    active_sessions: List[StationUseResponseSchema] = Field(default_factory=list, description="Active usage sessions")
    queue_length: int = Field(default=0, description="Number of characters waiting")
    estimated_wait_time: int = Field(default=0, description="Estimated wait time in seconds")

class StationUpgradeSchema(BaseModel):
    """Schema for station upgrade requests."""
    upgrade_type: str = Field(..., description="Type of upgrade (level, efficiency, quality, capacity)")
    character_id: str = Field(..., description="Character performing the upgrade")
    materials: Dict[str, int] = Field(default_factory=dict, description="Materials being used")
    force: bool = Field(default=False, description="Force upgrade even if requirements not met")

class StationUpgradeResponseSchema(BaseModel):
    """Schema for station upgrade responses."""
    station_id: uuid.UUID = Field(..., description="Station ID")
    upgrade_type: str = Field(..., description="Type of upgrade performed")
    success: bool = Field(..., description="Whether upgrade was successful")
    old_value: Any = Field(..., description="Previous value")
    new_value: Any = Field(..., description="New value after upgrade")
    materials_consumed: Dict[str, int] = Field(default_factory=dict, description="Materials consumed")
    cost: Dict[str, int] = Field(default_factory=dict, description="Total cost of upgrade")
    message: str = Field(default="", description="Result message")

class StationMaintenanceSchema(BaseModel):
    """Schema for station maintenance requests."""
    character_id: str = Field(..., description="Character performing maintenance")
    materials: Dict[str, int] = Field(default_factory=dict, description="Materials being used")
    maintenance_type: str = Field(default="routine", description="Type of maintenance")

class StationMaintenanceResponseSchema(BaseModel):
    """Schema for station maintenance responses."""
    station_id: uuid.UUID = Field(..., description="Station ID")
    maintenance_performed: bool = Field(..., description="Whether maintenance was performed")
    materials_consumed: Dict[str, int] = Field(default_factory=dict, description="Materials consumed")
    efficiency_restored: float = Field(default=0.0, description="Efficiency restored")
    durability_restored: float = Field(default=0.0, description="Durability restored")
    next_maintenance_due: Optional[datetime] = Field(None, description="When next maintenance is due")
    message: str = Field(default="", description="Result message") 
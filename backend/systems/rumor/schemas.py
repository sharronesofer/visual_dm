"""
API schemas for the rumor system.

This module defines the request and response schemas for the rumor system API.
"""
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime

from backend.systems.rumor.models.rumor import RumorCategory, RumorSeverity

# Request Schemas

class CreateRumorRequest(BaseModel):
    """Request for creating a new rumor."""
    originator_id: str = Field(..., description="ID of the entity creating the rumor")
    content: str = Field(..., description="Content of the rumor")
    categories: Optional[List[str]] = Field(default=None, description="Categories for the rumor")
    severity: str = Field(default="minor", description="Severity level of the rumor (trivial, minor, moderate, major, critical)")
    truth_value: float = Field(default=0.5, description="How true the rumor is (0.0 to 1.0)")

class SpreadRumorRequest(BaseModel):
    """Request for spreading a rumor."""
    rumor_id: str = Field(..., description="ID of the rumor to spread")
    from_entity_id: str = Field(..., description="ID of the entity spreading the rumor")
    to_entity_id: str = Field(..., description="ID of the entity receiving the rumor")
    mutation_probability: float = Field(default=0.2, description="Probability of the rumor mutating (0.0 to 1.0)")
    relationship_factor: Optional[float] = Field(default=None, description="Relationship strength (-1.0 to 1.0)")
    receiver_bias_factor: Optional[float] = Field(default=None, description="Additional modifier for believability")

class EntityRumorsRequest(BaseModel):
    """Request for getting all rumors known by an entity."""
    entity_id: str = Field(..., description="ID of the entity")
    min_believability: Optional[float] = Field(default=None, description="Minimum believability threshold")

class DecayRumorsRequest(BaseModel):
    """Request for decaying rumors."""
    days_since_active: int = Field(default=7, description="Days since reinforcement for decay to apply")

# Response Schemas

class RumorVariantResponse(BaseModel):
    """Response schema for a rumor variant."""
    id: str
    content: str
    created_at: str
    parent_variant_id: Optional[str] = None
    entity_id: str
    mutation_metadata: Dict[str, Any] = Field(default_factory=dict)

class RumorSpreadResponse(BaseModel):
    """Response schema for rumor spread information."""
    entity_id: str
    variant_id: str
    heard_from_entity_id: Optional[str] = None
    believability: float
    heard_at: str
    last_reinforced_at: str

class RumorResponse(BaseModel):
    """Response schema for a rumor."""
    id: str
    created_at: str
    originator_id: str
    original_content: str
    categories: List[str]
    severity: str
    truth_value: float
    variants: List[RumorVariantResponse] = Field(default_factory=list)
    spread: List[RumorSpreadResponse] = Field(default_factory=list)

class RumorSummaryResponse(BaseModel):
    """Summary view of a rumor."""
    id: str
    content: str
    categories: List[str]
    severity: str
    believability: Optional[float] = None
    variant_count: int
    spread_count: int

class RumorListResponse(BaseModel):
    """Response schema for a list of rumors."""
    rumors: List[RumorResponse]
    count: int
    total: Optional[int] = None

class EntityRumorsResponse(BaseModel):
    """Response schema for rumors known by an entity."""
    entity_id: str
    rumors: List[RumorResponse]
    count: int

class RumorOperationResponse(BaseModel):
    """Response schema for rumor operations."""
    success: bool
    message: str
    rumor_id: Optional[str] = None
    data: Dict[str, Any] = Field(default_factory=dict) 
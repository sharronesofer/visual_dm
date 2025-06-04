"""
Economic Espionage System Schemas

API schemas for the Economic Espionage System following FastAPI conventions.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field

from backend.systems.espionage.models import (
    EspionageOperationType,
    EspionageOperationStatus,
    IntelligenceType,
    AgentRole,
    NetworkStatus
)


# ============================================================================
# Base Espionage Schemas
# ============================================================================

class EspionageSchema(BaseModel):
    """Base schema for espionage entities"""
    
    id: UUID
    name: str
    description: Optional[str] = None
    status: str
    properties: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: Optional[datetime] = None
    is_active: bool

    class Config:
        from_attributes = True


class EspionageCreateSchema(BaseModel):
    """Schema for creating espionage entities"""
    
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    properties: Optional[Dict[str, Any]] = Field(default_factory=dict)


class EspionageUpdateSchema(BaseModel):
    """Schema for updating espionage entities"""
    
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    status: Optional[str] = None
    properties: Optional[Dict[str, Any]] = None


# ============================================================================
# Espionage Operation Schemas
# ============================================================================

class EspionageOperationSchema(BaseModel):
    """Schema for espionage operations"""
    
    id: UUID
    operation_type: EspionageOperationType
    status: EspionageOperationStatus
    initiator_id: UUID
    initiator_type: str
    target_id: UUID
    target_type: str
    
    # Operation details
    difficulty: int
    success_chance: float
    risk_level: int
    
    # Timeline
    planned_start: datetime
    planned_duration: int
    actual_start: Optional[datetime] = None
    completion_time: Optional[datetime] = None
    
    # Results
    success_level: Optional[float] = None
    intelligence_gained: List[str] = Field(default_factory=list)
    damage_dealt: Dict[str, Any] = Field(default_factory=dict)
    detection_level: Optional[float] = None
    
    # Participants
    agents_assigned: List[UUID] = Field(default_factory=list)
    resources_used: Dict[str, Any] = Field(default_factory=dict)
    
    # Operational security
    cover_story: Optional[str] = None
    contingency_plan: Optional[str] = None
    
    # Effects
    economic_impact: Dict[str, float] = Field(default_factory=dict)
    relationship_changes: Dict[str, float] = Field(default_factory=dict)
    
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class EspionageOperationCreateSchema(BaseModel):
    """Schema for creating espionage operations"""
    
    operation_type: EspionageOperationType
    initiator_id: UUID
    initiator_type: str
    target_id: UUID
    target_type: str
    planned_start: datetime
    planned_duration: int = Field(..., ge=1)
    difficulty: Optional[int] = Field(5, ge=1, le=10)
    agents_assigned: Optional[List[UUID]] = Field(default_factory=list)
    cover_story: Optional[str] = None
    contingency_plan: Optional[str] = None


class EspionageOperationUpdateSchema(BaseModel):
    """Schema for updating espionage operations"""
    
    status: Optional[EspionageOperationStatus] = None
    success_level: Optional[float] = Field(None, ge=0.0, le=1.0)
    detection_level: Optional[float] = Field(None, ge=0.0, le=1.0)
    intelligence_gained: Optional[List[str]] = None
    damage_dealt: Optional[Dict[str, Any]] = None
    economic_impact: Optional[Dict[str, float]] = None
    relationship_changes: Optional[Dict[str, float]] = None


# ============================================================================
# Espionage Agent Schemas
# ============================================================================

class EspionageAgentSchema(BaseModel):
    """Schema for espionage agents"""
    
    id: UUID
    npc_id: UUID
    handler_id: Optional[UUID] = None
    faction_id: Optional[UUID] = None
    
    # Agent attributes
    role: AgentRole
    skill_level: int
    loyalty: float
    trust_level: float
    
    # Cover and identity
    cover_identity: Optional[str] = None
    legitimate_occupation: Optional[str] = None
    access_level: int
    
    # Status and activity
    status: str
    last_contact: Optional[datetime] = None
    current_assignment: Optional[UUID] = None
    
    # Performance tracking
    operations_completed: int
    success_rate: float
    times_compromised: int
    
    # Risk assessment
    burn_risk: float
    heat_level: int
    
    # Capabilities
    specializations: List[str] = Field(default_factory=list)
    languages_known: List[str] = Field(default_factory=list)
    contacts: List[UUID] = Field(default_factory=list)
    
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class EspionageAgentCreateSchema(BaseModel):
    """Schema for creating espionage agents"""
    
    npc_id: UUID
    role: AgentRole
    faction_id: Optional[UUID] = None
    handler_id: Optional[UUID] = None
    skill_level: Optional[int] = Field(1, ge=1, le=10)
    cover_identity: Optional[str] = None
    legitimate_occupation: Optional[str] = None
    specializations: Optional[List[str]] = Field(default_factory=list)
    languages_known: Optional[List[str]] = Field(default_factory=list)


class EspionageAgentUpdateSchema(BaseModel):
    """Schema for updating espionage agents"""
    
    status: Optional[str] = None
    skill_level: Optional[int] = Field(None, ge=1, le=10)
    loyalty: Optional[float] = Field(None, ge=0.0, le=10.0)
    trust_level: Optional[float] = Field(None, ge=0.0, le=10.0)
    burn_risk: Optional[float] = Field(None, ge=0.0, le=1.0)
    heat_level: Optional[int] = Field(None, ge=0, le=10)
    current_assignment: Optional[UUID] = None
    specializations: Optional[List[str]] = None
    contacts: Optional[List[UUID]] = None


# ============================================================================
# Economic Intelligence Schemas
# ============================================================================

class EconomicIntelligenceSchema(BaseModel):
    """Schema for economic intelligence"""
    
    id: UUID
    intelligence_type: IntelligenceType
    source_operation: Optional[UUID] = None
    target_entity: UUID
    target_type: str
    
    # Intelligence content
    data: Dict[str, Any]
    reliability: float
    freshness: float
    
    # Source tracking
    gathered_by: UUID
    gathered_date: datetime
    verification_level: int
    
    # Access and distribution
    classification_level: int
    shared_with: List[UUID] = Field(default_factory=list)
    
    # Value assessment
    strategic_value: int
    economic_value: float
    
    # Expiration and decay
    expiry_date: Optional[datetime] = None
    decay_rate: float
    
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class EconomicIntelligenceCreateSchema(BaseModel):
    """Schema for creating economic intelligence"""
    
    intelligence_type: IntelligenceType
    target_entity: UUID
    target_type: str
    data: Dict[str, Any]
    gathered_by: UUID
    source_operation: Optional[UUID] = None
    reliability: Optional[float] = Field(0.5, ge=0.0, le=1.0)
    strategic_value: Optional[int] = Field(5, ge=1, le=10)
    classification_level: Optional[int] = Field(1, ge=1, le=5)
    expiry_date: Optional[datetime] = None


class EconomicIntelligenceUpdateSchema(BaseModel):
    """Schema for updating economic intelligence"""
    
    data: Optional[Dict[str, Any]] = None
    reliability: Optional[float] = Field(None, ge=0.0, le=1.0)
    freshness: Optional[float] = Field(None, ge=0.0, le=1.0)
    verification_level: Optional[int] = Field(None, ge=1, le=5)
    shared_with: Optional[List[UUID]] = None
    strategic_value: Optional[int] = Field(None, ge=1, le=10)
    economic_value: Optional[float] = None


# ============================================================================
# Spy Network Schemas
# ============================================================================

class SpyNetworkSchema(BaseModel):
    """Schema for spy networks"""
    
    id: UUID
    name: str
    faction_id: UUID
    spymaster_id: Optional[UUID] = None
    
    # Network properties
    status: NetworkStatus
    coverage_area: List[str] = Field(default_factory=list)
    specialization: List[str] = Field(default_factory=list)
    
    # Size and structure
    agent_count: int
    cell_structure: bool
    depth_levels: int
    
    # Capabilities
    intelligence_capacity: int
    sabotage_capacity: int
    infiltration_capacity: int
    
    # Security
    security_level: int
    compromise_risk: float
    
    # Operations
    active_operations: List[UUID] = Field(default_factory=list)
    completed_operations: int
    
    # Resources
    funding_level: int
    equipment_quality: int
    
    # Relationships
    allied_networks: List[UUID] = Field(default_factory=list)
    rival_networks: List[UUID] = Field(default_factory=list)
    
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class SpyNetworkCreateSchema(BaseModel):
    """Schema for creating spy networks"""
    
    name: str = Field(..., min_length=1, max_length=255)
    faction_id: UUID
    spymaster_id: Optional[UUID] = None
    coverage_area: Optional[List[str]] = Field(default_factory=list)
    specialization: Optional[List[str]] = Field(default_factory=list)
    cell_structure: Optional[bool] = True
    depth_levels: Optional[int] = Field(3, ge=1, le=10)


class SpyNetworkUpdateSchema(BaseModel):
    """Schema for updating spy networks"""
    
    status: Optional[NetworkStatus] = None
    agent_count: Optional[int] = Field(None, ge=0)
    security_level: Optional[int] = Field(None, ge=1, le=10)
    funding_level: Optional[int] = Field(None, ge=1, le=10)
    equipment_quality: Optional[int] = Field(None, ge=1, le=10)
    active_operations: Optional[List[UUID]] = None
    allied_networks: Optional[List[UUID]] = None
    rival_networks: Optional[List[UUID]] = None
    compromise_risk: Optional[float] = Field(None, ge=0.0, le=1.0)


# ============================================================================
# List Response Schemas
# ============================================================================

class EspionageListResponseSchema(BaseModel):
    """Schema for paginated espionage entity lists"""
    
    items: List[EspionageSchema]
    total: int
    page: int
    size: int
    has_next: bool
    has_prev: bool


class EspionageOperationListResponseSchema(BaseModel):
    """Schema for paginated espionage operation lists"""
    
    items: List[EspionageOperationSchema]
    total: int
    page: int
    size: int
    has_next: bool
    has_prev: bool


class EspionageAgentListResponseSchema(BaseModel):
    """Schema for paginated espionage agent lists"""
    
    items: List[EspionageAgentSchema]
    total: int
    page: int
    size: int
    has_next: bool
    has_prev: bool


class EconomicIntelligenceListResponseSchema(BaseModel):
    """Schema for paginated economic intelligence lists"""
    
    items: List[EconomicIntelligenceSchema]
    total: int
    page: int
    size: int
    has_next: bool
    has_prev: bool


class SpyNetworkListResponseSchema(BaseModel):
    """Schema for paginated spy network lists"""
    
    items: List[SpyNetworkSchema]
    total: int
    page: int
    size: int
    has_next: bool
    has_prev: bool 
"""
Economic Espionage System Business Models

This module defines the business domain models for the economic espionage system.
Contains business logic models, enums, and domain objects without technical infrastructure.
"""

from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from uuid import UUID, uuid4
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict

# ============================================================================
# Business Enums
# ============================================================================

class EspionageOperationType(str, Enum):
    """Types of espionage operations"""
    TRADE_SECRET_THEFT = "trade_secret_theft"
    PRICE_INTELLIGENCE = "price_intelligence"
    SUPPLIER_INTELLIGENCE = "supplier_intelligence"
    ROUTE_SURVEILLANCE = "route_surveillance"
    FACILITY_SABOTAGE = "facility_sabotage"
    SHIPMENT_SABOTAGE = "shipment_sabotage"
    REPUTATION_SABOTAGE = "reputation_sabotage"
    MARKET_MANIPULATION = "market_manipulation"
    COUNTER_ESPIONAGE = "counter_espionage"
    AGENT_RECRUITMENT = "agent_recruitment"
    NETWORK_INFILTRATION = "network_infiltration"

class EspionageOperationStatus(str, Enum):
    """Status of espionage operations"""
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    COMPROMISED = "compromised"
    ABANDONED = "abandoned"

class IntelligenceType(str, Enum):
    """Types of economic intelligence"""
    PRICING_DATA = "pricing_data"
    SUPPLIER_LIST = "supplier_list"
    TRADE_ROUTE = "trade_route"
    INVENTORY_LEVEL = "inventory_level"
    FINANCIAL_DATA = "financial_data"
    STRATEGIC_PLAN = "strategic_plan"
    WEAKNESS_ANALYSIS = "weakness_analysis"
    MARKET_SHARE = "market_share"

class AgentRole(str, Enum):
    """Roles of espionage agents"""
    SPYMASTER = "spymaster"
    INFILTRATOR = "infiltrator"
    INFORMANT = "informant"
    SABOTEUR = "saboteur"
    COURIER = "courier"
    ANALYST = "analyst"
    HANDLER = "handler"
    SLEEPER = "sleeper"

class NetworkStatus(str, Enum):
    """Status of spy networks"""
    ACTIVE = "active"
    COMPROMISED = "compromised"
    DORMANT = "dormant"
    DISBANDED = "disbanded"
    REBUILDING = "rebuilding"

# ============================================================================
# Base Business Models
# ============================================================================

class EspionageBaseModel(BaseModel):
    """Base model for espionage system with common fields"""
    
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    is_active: bool = Field(default=True)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

class EspionageModel(EspionageBaseModel):
    """Primary model for espionage system"""
    
    name: str = Field(..., description="Name of the espionage entity")
    description: Optional[str] = Field(None, description="Description of the espionage entity")
    status: str = Field(default="active", description="Status of the espionage entity")
    properties: Optional[Dict[str, Any]] = Field(default_factory=dict)

# ============================================================================
# Business Domain Models
# ============================================================================

class EspionageOperation(EspionageBaseModel):
    """Business model for espionage operations"""
    
    operation_type: EspionageOperationType = Field(..., description="Type of espionage operation")
    status: EspionageOperationStatus = Field(default=EspionageOperationStatus.PLANNED)
    initiator_id: UUID = Field(..., description="NPC or faction initiating the operation")
    initiator_type: str = Field(..., description="Type of initiator (npc or faction)")
    target_id: UUID = Field(..., description="Target NPC, faction, or entity")
    target_type: str = Field(..., description="Type of target (npc, faction, business)")
    
    # Operation details
    difficulty: int = Field(default=5, ge=1, le=10, description="Operation difficulty (1-10)")
    success_chance: float = Field(default=0.5, ge=0.0, le=1.0, description="Base success probability")
    risk_level: int = Field(default=5, ge=1, le=10, description="Risk of detection/failure")
    
    # Timeline
    planned_start: datetime = Field(..., description="When operation should begin")
    planned_duration: int = Field(..., description="Expected duration in hours")
    actual_start: Optional[datetime] = Field(None, description="When operation actually started")
    completion_time: Optional[datetime] = Field(None, description="When operation completed")
    
    # Results
    success_level: Optional[float] = Field(None, ge=0.0, le=1.0, description="Level of success (0-1)")
    intelligence_gained: Optional[List[str]] = Field(default_factory=list, description="Intelligence IDs obtained")
    damage_dealt: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Economic damage caused")
    detection_level: Optional[float] = Field(None, ge=0.0, le=1.0, description="How much was detected")
    
    # Participants
    agents_assigned: List[UUID] = Field(default_factory=list, description="Agent IDs assigned to operation")
    resources_used: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Resources consumed")
    
    # Operational security
    cover_story: Optional[str] = Field(None, description="Cover story for the operation")
    contingency_plan: Optional[str] = Field(None, description="Backup plan if compromised")
    
    # Effects and consequences
    economic_impact: Optional[Dict[str, float]] = Field(default_factory=dict, description="Economic impact metrics")
    relationship_changes: Optional[Dict[str, float]] = Field(default_factory=dict, description="Relationship effects")

class EspionageAgent(EspionageBaseModel):
    """Business model for espionage agents"""
    
    npc_id: UUID = Field(..., description="ID of the NPC this agent represents")
    handler_id: Optional[UUID] = Field(None, description="ID of the agent's handler")
    faction_id: Optional[UUID] = Field(None, description="Faction the agent serves")
    
    # Agent attributes
    role: AgentRole = Field(..., description="Primary role of the agent")
    skill_level: int = Field(default=1, ge=1, le=10, description="Agent's skill level")
    loyalty: float = Field(default=5.0, ge=0.0, le=10.0, description="Loyalty to employer")
    trust_level: float = Field(default=5.0, ge=0.0, le=10.0, description="How much they're trusted")
    
    # Cover and identity
    cover_identity: Optional[str] = Field(None, description="Agent's cover identity")
    legitimate_occupation: Optional[str] = Field(None, description="Their day job")
    access_level: int = Field(default=1, ge=1, le=10, description="Access to sensitive information")
    
    # Status and activity
    status: str = Field(default="active", description="Agent status (active, inactive, burned, etc.)")
    last_contact: Optional[datetime] = Field(None, description="Last contact with handler")
    current_assignment: Optional[UUID] = Field(None, description="Current operation ID")
    
    # Performance tracking
    operations_completed: int = Field(default=0, description="Number of completed operations")
    success_rate: float = Field(default=0.0, ge=0.0, le=1.0, description="Historical success rate")
    times_compromised: int = Field(default=0, description="Times the agent was compromised")
    
    # Risk assessment
    burn_risk: float = Field(default=0.0, ge=0.0, le=1.0, description="Risk of being exposed")
    heat_level: int = Field(default=0, ge=0, le=10, description="Current scrutiny level")
    
    # Specializations and capabilities
    specializations: List[str] = Field(default_factory=list, description="Agent's areas of expertise")
    languages_known: List[str] = Field(default_factory=list, description="Languages the agent speaks")
    contacts: List[UUID] = Field(default_factory=list, description="Network of contacts")

class EconomicIntelligence(EspionageBaseModel):
    """Business model for economic intelligence data"""
    
    intelligence_type: IntelligenceType = Field(..., description="Type of intelligence")
    source_operation: Optional[UUID] = Field(None, description="Operation that gathered this intelligence")
    target_entity: UUID = Field(..., description="Entity this intelligence is about")
    target_type: str = Field(..., description="Type of target entity")
    
    # Intelligence content
    data: Dict[str, Any] = Field(..., description="The actual intelligence data")
    reliability: float = Field(default=0.5, ge=0.0, le=1.0, description="Reliability of the information")
    freshness: float = Field(default=1.0, ge=0.0, le=1.0, description="How current the information is")
    
    # Source tracking
    gathered_by: UUID = Field(..., description="Agent or entity that gathered this")
    gathered_date: datetime = Field(default_factory=datetime.utcnow)
    verification_level: int = Field(default=1, ge=1, le=5, description="How well verified this is")
    
    # Access and distribution
    classification_level: int = Field(default=1, ge=1, le=5, description="Security classification")
    shared_with: List[UUID] = Field(default_factory=list, description="Entities this was shared with")
    
    # Value assessment
    strategic_value: int = Field(default=5, ge=1, le=10, description="Strategic importance")
    economic_value: float = Field(default=0.0, description="Estimated economic value")
    
    # Expiration and decay
    expiry_date: Optional[datetime] = Field(None, description="When this intelligence expires")
    decay_rate: float = Field(default=0.1, description="How quickly this loses value")

class SpyNetwork(EspionageBaseModel):
    """Business model for spy networks"""
    
    name: str = Field(..., description="Name of the spy network")
    faction_id: UUID = Field(..., description="Faction that controls this network")
    spymaster_id: Optional[UUID] = Field(None, description="Primary spymaster NPC")
    
    # Network properties
    status: NetworkStatus = Field(default=NetworkStatus.ACTIVE)
    coverage_area: List[str] = Field(default_factory=list, description="Regions where network operates")
    specialization: List[str] = Field(default_factory=list, description="Network's areas of expertise")
    
    # Size and structure
    agent_count: int = Field(default=0, description="Number of active agents")
    cell_structure: bool = Field(default=True, description="Whether network uses cell structure")
    depth_levels: int = Field(default=3, description="Number of operational levels")
    
    # Capabilities
    intelligence_capacity: int = Field(default=5, ge=1, le=10, description="Intelligence gathering capability")
    sabotage_capacity: int = Field(default=5, ge=1, le=10, description="Sabotage capability")
    infiltration_capacity: int = Field(default=5, ge=1, le=10, description="Infiltration capability")
    
    # Security
    security_level: int = Field(default=5, ge=1, le=10, description="Network security rating")
    compromise_risk: float = Field(default=0.1, ge=0.0, le=1.0, description="Risk of compromise")
    
    # Operations
    active_operations: List[UUID] = Field(default_factory=list, description="Current operation IDs")
    completed_operations: int = Field(default=0, description="Number of completed operations")
    
    # Resources
    funding_level: int = Field(default=5, ge=1, le=10, description="Available funding")
    equipment_quality: int = Field(default=5, ge=1, le=10, description="Quality of equipment")
    
    # Relationships
    allied_networks: List[UUID] = Field(default_factory=list, description="Allied network IDs")
    rival_networks: List[UUID] = Field(default_factory=list, description="Rival network IDs")

# ============================================================================
# Request/Response Models
# ============================================================================

class CreateEspionageRequest(BaseModel):
    """Request model for creating espionage entity"""
    
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    properties: Optional[Dict[str, Any]] = Field(default_factory=dict)

class UpdateEspionageRequest(BaseModel):
    """Request model for updating espionage entity"""
    
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    status: Optional[str] = Field(None)
    properties: Optional[Dict[str, Any]] = None

class CreateEspionageOperationRequest(BaseModel):
    """Request model for creating espionage operation"""
    
    operation_type: EspionageOperationType = Field(...)
    initiator_id: UUID = Field(...)
    initiator_type: str = Field(...)
    target_id: UUID = Field(...)
    target_type: str = Field(...)
    planned_start: datetime = Field(...)
    planned_duration: int = Field(..., ge=1)
    difficulty: Optional[int] = Field(5, ge=1, le=10)
    agents_assigned: Optional[List[UUID]] = Field(default_factory=list)
    cover_story: Optional[str] = Field(None)

class UpdateEspionageOperationRequest(BaseModel):
    """Request model for updating espionage operation"""
    
    status: Optional[EspionageOperationStatus] = Field(None)
    success_level: Optional[float] = Field(None, ge=0.0, le=1.0)
    detection_level: Optional[float] = Field(None, ge=0.0, le=1.0)
    intelligence_gained: Optional[List[str]] = Field(None)
    damage_dealt: Optional[Dict[str, Any]] = Field(None)

class CreateEspionageAgentRequest(BaseModel):
    """Request model for creating espionage agent"""
    
    npc_id: UUID = Field(...)
    role: AgentRole = Field(...)
    faction_id: Optional[UUID] = Field(None)
    handler_id: Optional[UUID] = Field(None)
    skill_level: Optional[int] = Field(1, ge=1, le=10)
    cover_identity: Optional[str] = Field(None)
    specializations: Optional[List[str]] = Field(default_factory=list)

class UpdateEspionageAgentRequest(BaseModel):
    """Request model for updating espionage agent"""
    
    status: Optional[str] = Field(None)
    skill_level: Optional[int] = Field(None, ge=1, le=10)
    loyalty: Optional[float] = Field(None, ge=0.0, le=10.0)
    trust_level: Optional[float] = Field(None, ge=0.0, le=10.0)
    burn_risk: Optional[float] = Field(None, ge=0.0, le=1.0)
    heat_level: Optional[int] = Field(None, ge=0, le=10)

class CreateEconomicIntelligenceRequest(BaseModel):
    """Request model for creating economic intelligence"""
    
    intelligence_type: IntelligenceType = Field(...)
    target_entity: UUID = Field(...)
    target_type: str = Field(...)
    data: Dict[str, Any] = Field(...)
    gathered_by: UUID = Field(...)
    reliability: Optional[float] = Field(0.5, ge=0.0, le=1.0)
    strategic_value: Optional[int] = Field(5, ge=1, le=10)

class UpdateEconomicIntelligenceRequest(BaseModel):
    """Request model for updating economic intelligence"""
    
    data: Optional[Dict[str, Any]] = Field(None)
    reliability: Optional[float] = Field(None, ge=0.0, le=1.0)
    freshness: Optional[float] = Field(None, ge=0.0, le=1.0)
    verification_level: Optional[int] = Field(None, ge=1, le=5)
    shared_with: Optional[List[UUID]] = Field(None)

class CreateSpyNetworkRequest(BaseModel):
    """Request model for creating spy network"""
    
    name: str = Field(..., min_length=1, max_length=255)
    faction_id: UUID = Field(...)
    spymaster_id: Optional[UUID] = Field(None)
    coverage_area: Optional[List[str]] = Field(default_factory=list)
    specialization: Optional[List[str]] = Field(default_factory=list)

class UpdateSpyNetworkRequest(BaseModel):
    """Request model for updating spy network"""
    
    status: Optional[NetworkStatus] = Field(None)
    agent_count: Optional[int] = Field(None, ge=0)
    security_level: Optional[int] = Field(None, ge=1, le=10)
    funding_level: Optional[int] = Field(None, ge=1, le=10)
    active_operations: Optional[List[UUID]] = Field(None)

class EspionageResponse(BaseModel):
    """Response model for espionage entity"""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    name: str
    description: Optional[str]
    status: str
    properties: Dict[str, Any]
    created_at: datetime
    updated_at: Optional[datetime]
    is_active: bool

class EspionageListResponse(BaseModel):
    """Response model for espionage lists"""
    
    items: List[EspionageResponse]
    total: int
    page: int
    size: int
    has_next: bool
    has_prev: bool

class EspionageOperationResponse(BaseModel):
    """Response model for espionage operation"""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    operation_type: str
    status: str
    initiator_id: UUID
    target_id: UUID
    difficulty: int
    success_chance: float
    planned_start: datetime
    completion_time: Optional[datetime]
    success_level: Optional[float]
    detection_level: Optional[float]
    agents_assigned: List[UUID]
    created_at: datetime

class EspionageAgentResponse(BaseModel):
    """Response model for espionage agent"""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    npc_id: UUID
    role: str
    skill_level: int
    loyalty: float
    status: str
    operations_completed: int
    success_rate: float
    burn_risk: float
    specializations: List[str]
    created_at: datetime

class EconomicIntelligenceResponse(BaseModel):
    """Response model for economic intelligence"""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    intelligence_type: str
    target_entity: UUID
    reliability: float
    freshness: float
    strategic_value: int
    gathered_date: datetime
    verification_level: int
    created_at: datetime

class SpyNetworkResponse(BaseModel):
    """Response model for spy network"""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    name: str
    faction_id: UUID
    status: str
    agent_count: int
    coverage_area: List[str]
    specialization: List[str]
    intelligence_capacity: int
    sabotage_capacity: int
    security_level: int
    active_operations: List[UUID]
    created_at: datetime 
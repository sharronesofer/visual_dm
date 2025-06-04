"""
Economic Espionage System Database Models

SQLAlchemy database entities for the economic espionage system.
Handles trade secret theft, sabotage operations, market manipulation, and spy networks.
"""

from datetime import datetime
from uuid import UUID, uuid4
from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text, ForeignKey, Float
from sqlalchemy.dialects.postgresql import UUID as SQLAlchemyUUID, JSONB
from sqlalchemy.orm import relationship

from backend.infrastructure.database import Base, UUIDMixin, TimestampMixin

# ============================================================================
# Espionage Operations
# ============================================================================

class EspionageOperationEntity(Base):
    """SQLAlchemy entity for espionage operations"""
    
    __tablename__ = "espionage_operations"
    
    id = Column(SQLAlchemyUUID(as_uuid=True), primary_key=True, default=uuid4)
    operation_type = Column(String(50), nullable=False, index=True)
    status = Column(String(20), default="planned", index=True)
    initiator_id = Column(SQLAlchemyUUID(as_uuid=True), nullable=False, index=True)
    initiator_type = Column(String(20), nullable=False, index=True)
    target_id = Column(SQLAlchemyUUID(as_uuid=True), nullable=False, index=True)
    target_type = Column(String(20), nullable=False, index=True)
    
    # Operation parameters
    difficulty = Column(Integer, default=5)
    success_chance = Column(Float, default=0.5)
    risk_level = Column(Integer, default=5)
    
    # Timeline
    planned_start = Column(DateTime, nullable=False, index=True)
    planned_duration = Column(Integer, nullable=False)  # hours
    actual_start = Column(DateTime, index=True)
    completion_time = Column(DateTime, index=True)
    
    # Results
    success_level = Column(Float)
    intelligence_gained = Column(JSONB, default=list)
    damage_dealt = Column(JSONB, default=dict)
    detection_level = Column(Float)
    
    # Participants and resources
    agents_assigned = Column(JSONB, default=list)
    resources_used = Column(JSONB, default=dict)
    
    # Operational details
    cover_story = Column(Text)
    contingency_plan = Column(Text)
    
    # Impact tracking
    economic_impact = Column(JSONB, default=dict)
    relationship_changes = Column(JSONB, default=dict)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True, index=True)
    entity_metadata = Column(JSONB, default=dict)

    def __repr__(self):
        return f"<EspionageOperation(id={self.id}, type={self.operation_type}, status={self.status})>"

# ============================================================================
# Espionage Agents
# ============================================================================

class EspionageAgentEntity(Base):
    """SQLAlchemy entity for espionage agents"""
    
    __tablename__ = "espionage_agents"
    
    id = Column(SQLAlchemyUUID(as_uuid=True), primary_key=True, default=uuid4)
    npc_id = Column(SQLAlchemyUUID(as_uuid=True), nullable=False, index=True)
    handler_id = Column(SQLAlchemyUUID(as_uuid=True), index=True)
    faction_id = Column(SQLAlchemyUUID(as_uuid=True), index=True)
    
    # Agent attributes
    role = Column(String(20), nullable=False, index=True)
    skill_level = Column(Integer, default=1)
    loyalty = Column(Float, default=5.0)
    trust_level = Column(Float, default=5.0)
    
    # Cover and identity
    cover_identity = Column(String(255))
    legitimate_occupation = Column(String(100))
    access_level = Column(Integer, default=1)
    
    # Status
    status = Column(String(20), default="active", index=True)
    last_contact = Column(DateTime, index=True)
    current_assignment = Column(SQLAlchemyUUID(as_uuid=True), index=True)
    
    # Performance
    operations_completed = Column(Integer, default=0)
    success_rate = Column(Float, default=0.0)
    times_compromised = Column(Integer, default=0)
    
    # Risk
    burn_risk = Column(Float, default=0.0)
    heat_level = Column(Integer, default=0)
    
    # Capabilities
    specializations = Column(JSONB, default=list)
    languages_known = Column(JSONB, default=list)
    contacts = Column(JSONB, default=list)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True, index=True)
    entity_metadata = Column(JSONB, default=dict)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.created_at = datetime.utcnow()
        if 'status' not in kwargs:
            self.status = "active"

    def __repr__(self):
        return f"<EspionageAgent(id={self.id}, npc_id={self.npc_id}, role={self.role})>"

# ============================================================================
# Economic Intelligence
# ============================================================================

class EconomicIntelligenceEntity(Base):
    """SQLAlchemy entity for economic intelligence"""
    
    __tablename__ = "economic_intelligence"
    
    id = Column(SQLAlchemyUUID(as_uuid=True), primary_key=True, default=uuid4)
    intelligence_type = Column(String(50), nullable=False, index=True)
    source_operation = Column(SQLAlchemyUUID(as_uuid=True), index=True)
    target_entity = Column(SQLAlchemyUUID(as_uuid=True), nullable=False, index=True)
    target_type = Column(String(20), nullable=False, index=True)
    
    # Content
    data = Column(JSONB, nullable=False)
    reliability = Column(Float, default=0.5)
    freshness = Column(Float, default=1.0)
    
    # Source
    gathered_by = Column(SQLAlchemyUUID(as_uuid=True), nullable=False, index=True)
    gathered_date = Column(DateTime, default=datetime.utcnow, index=True)
    verification_level = Column(Integer, default=1)
    
    # Distribution
    classification_level = Column(Integer, default=1)
    shared_with = Column(JSONB, default=list)
    
    # Value
    strategic_value = Column(Integer, default=5)
    economic_value = Column(Float, default=0.0)
    
    # Lifecycle
    expiry_date = Column(DateTime, index=True)
    decay_rate = Column(Float, default=0.1)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True, index=True)
    entity_metadata = Column(JSONB, default=dict)

    def __repr__(self):
        return f"<EconomicIntelligence(id={self.id}, type={self.intelligence_type})>"

# ============================================================================
# Spy Networks
# ============================================================================

class SpyNetworkEntity(Base):
    """SQLAlchemy entity for spy networks"""
    
    __tablename__ = "spy_networks"
    
    id = Column(SQLAlchemyUUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(255), nullable=False, index=True)
    faction_id = Column(SQLAlchemyUUID(as_uuid=True), nullable=False, index=True)
    spymaster_id = Column(SQLAlchemyUUID(as_uuid=True), index=True)
    
    # Network properties
    status = Column(String(20), default="active", index=True)
    coverage_area = Column(JSONB, default=list)
    specialization = Column(JSONB, default=list)
    
    # Structure
    agent_count = Column(Integer, default=0)
    cell_structure = Column(Boolean, default=True)
    depth_levels = Column(Integer, default=3)
    
    # Capabilities
    intelligence_capacity = Column(Integer, default=5)
    sabotage_capacity = Column(Integer, default=5)
    infiltration_capacity = Column(Integer, default=5)
    
    # Security
    security_level = Column(Integer, default=5)
    compromise_risk = Column(Float, default=0.1)
    
    # Operations
    active_operations = Column(JSONB, default=list)
    completed_operations = Column(Integer, default=0)
    
    # Resources
    funding_level = Column(Integer, default=5)
    equipment_quality = Column(Integer, default=5)
    
    # Relationships
    allied_networks = Column(JSONB, default=list)
    rival_networks = Column(JSONB, default=list)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True, index=True)
    entity_metadata = Column(JSONB, default=dict)

    def __repr__(self):
        return f"<SpyNetwork(id={self.id}, name={self.name}, faction_id={self.faction_id})>"

# ============================================================================
# General Espionage Entity (for compatibility)
# ============================================================================

class EspionageEntity(Base):
    """Main SQLAlchemy entity for espionage system compatibility"""
    
    __tablename__ = "espionage_entities"
    
    id = Column(SQLAlchemyUUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    status = Column(String(50), default="active", index=True)
    properties = Column(JSONB, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True, index=True)
    entity_metadata = Column(JSONB, default=dict)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.created_at = datetime.utcnow()
        if 'is_active' not in kwargs:
            self.is_active = True
        if 'properties' not in kwargs:
            self.properties = {}

    def __repr__(self):
        return f"<EspionageEntity(id={self.id}, name={self.name}, status={self.status})>"

    def to_dict(self):
        """Convert entity to dictionary"""
        return {
            'id': str(self.id),
            'name': self.name,
            'description': self.description,
            'status': self.status,
            'properties': self.properties,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_active': self.is_active,
            'entity_metadata': self.entity_metadata
        } 
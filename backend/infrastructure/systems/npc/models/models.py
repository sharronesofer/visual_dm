"""
Npc System Models

This module defines the data models for the npc system according to
the Development Bible standards.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text, ForeignKey, Float
from sqlalchemy.dialects.postgresql import UUID as SQLAlchemyUUID, JSONB
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship

from backend.infrastructure.database import Base, UUIDMixin, TimestampMixin

class NpcBaseModel(BaseModel):
    """Base Pydantic model for npc system with common fields"""
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    is_active: bool = Field(default=True)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

    model_config = ConfigDict(from_attributes=True)


class NpcModel(NpcBaseModel):
    """Primary model for npc system"""
    
    name: str = Field(..., description="Name of the npc")
    description: Optional[str] = Field(None, description="Description of the npc")
    status: str = Field(default="active", description="Status of the npc")
    properties: Optional[Dict[str, Any]] = Field(default_factory=dict)


# ============================================================================
# Comprehensive SQLAlchemy Database Models
# ============================================================================

class NpcEntity(UUIDMixin):
    """Complete SQLAlchemy entity for NPCs with all attributes from NPCBuilder"""
    
    __tablename__ = "npc_entities"
    __table_args__ = {'extend_existing': True}
    
    # Basic Information
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    race = Column(String(100), default="Human", index=True)
    status = Column(String(50), default="active", index=True)
    is_active = Column(Boolean, default=True, index=True)
    
    # Attributes (D&D stats)
    strength = Column(Integer, default=10)
    dexterity = Column(Integer, default=10)
    constitution = Column(Integer, default=10)
    intelligence = Column(Integer, default=10)
    wisdom = Column(Integer, default=10)
    charisma = Column(Integer, default=10)
    
    # Character Details
    level = Column(Integer, default=1)
    xp = Column(Integer, default=0)
    alignment = Column(String(50))
    backstory = Column(Text)
    
    # Skills and Features
    skills = Column(JSONB, default=list)  # List of skill names
    tags = Column(JSONB, default=list)   # List of character tags
    features = Column(JSONB, default=list)  # Special features
    inventory = Column(JSONB, default=list)  # Item list
    equipment = Column(JSONB, default=list)  # Equipped items
    gold = Column(Integer, default=0)
    
    # Combat Stats
    dr = Column(Integer, default=0)  # Damage reduction
    status_effects = Column(JSONB, default=list)
    cooldowns = Column(JSONB, default=dict)
    
    # Location and Region
    region_id = Column(String(100), index=True)
    location = Column(String(100))  # Format: "x_y"
    
    # Loyalty System
    loyalty_score = Column(Integer, default=0)
    goodwill = Column(Integer, default=18)
    loyalty_tags = Column(JSONB, default=list)
    loyalty_last_tick = Column(DateTime)
    
    # Faction and Social
    faction_affiliations = Column(JSONB, default=list)
    reputation = Column(Integer, default=0)
    
    # Hidden Personality Traits
    hidden_ambition = Column(Integer, default=0)
    hidden_integrity = Column(Integer, default=0)
    hidden_discipline = Column(Integer, default=0)
    hidden_impulsivity = Column(Integer, default=0)
    hidden_pragmatism = Column(Integer, default=0)
    hidden_resilience = Column(Integer, default=0)
    
    # Motif System
    motif_entropy = Column(Float, default=0.0)
    motif_last_rotated = Column(DateTime)
    
    # Miscellaneous
    known_languages = Column(JSONB, default=["Common"])
    memory_summary = Column(Text)
    rumor_index = Column(JSONB, default=list)
    
    # Additional properties for future extensions
    properties = Column(JSONB, default=dict)

    # Relationships
    memories = relationship("NpcMemory", back_populates="npc", cascade="all, delete-orphan")
    faction_relationships = relationship("NpcFactionAffiliation", back_populates="npc", cascade="all, delete-orphan")
    rumors = relationship("NpcRumor", back_populates="npc", cascade="all, delete-orphan")
    location_history = relationship("NpcLocationHistory", back_populates="npc", cascade="all, delete-orphan")
    motifs = relationship("NpcMotif", back_populates="npc", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<NpcEntity(id={self.id}, name={self.name}, race={self.race})>"

    def to_dict(self) -> Dict[str, Any]:
        """Convert entity to dictionary compatible with NPCBuilder output"""
        return {
            "npc_id": str(self.id),
            "id": str(self.id),
            "name": self.name,
            "description": self.description,
            "race": self.race,
            "status": self.status,
            "attributes": {
                "strength": self.strength,
                "dexterity": self.dexterity,
                "constitution": self.constitution,
                "intelligence": self.intelligence,
                "wisdom": self.wisdom,
                "charisma": self.charisma
            },
            "level": self.level,
            "XP": self.xp,
            "alignment": self.alignment,
            "skills": self.skills or [],
            "tags": self.tags or [],
            "features": self.features or [],
            "inventory": self.inventory or [],
            "equipment": self.equipment or [],
            "gold": self.gold,
            "dr": self.dr,
            "status_effects": self.status_effects or [],
            "cooldowns": self.cooldowns or {},
            "region_id": self.region_id,
            "location": self.location,
            "loyalty": {
                "score": self.loyalty_score,
                "goodwill": self.goodwill,
                "tags": self.loyalty_tags or [],
                "last_tick": self.loyalty_last_tick.isoformat() if self.loyalty_last_tick else None
            },
            "faction_affiliations": self.faction_affiliations or [],
            "reputation": self.reputation,
            "hidden_ambition": self.hidden_ambition,
            "hidden_integrity": self.hidden_integrity,
            "hidden_discipline": self.hidden_discipline,
            "hidden_impulsivity": self.hidden_impulsivity,
            "hidden_pragmatism": self.hidden_pragmatism,
            "hidden_resilience": self.hidden_resilience,
            "motif_entropy": self.motif_entropy,
            "known_languages": self.known_languages or ["Common"],
            "memory_summary": self.memory_summary,
            "rumor_index": self.rumor_index or [],
            "backstory": self.backstory,
            "properties": self.properties or {},
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "is_active": self.is_active
        }

    def update_from_npc_builder(self, npc_data: Dict[str, Any]) -> None:
        """Update entity from NPCBuilder output"""
        # Basic info
        self.name = npc_data.get("name", self.name)
        self.race = npc_data.get("race", self.race)
        self.level = npc_data.get("level", self.level)
        self.xp = npc_data.get("XP", self.xp)
        self.alignment = npc_data.get("alignment", self.alignment)
        self.backstory = npc_data.get("backstory", self.backstory)
        
        # Attributes
        attributes = npc_data.get("attributes", {})
        self.strength = attributes.get("strength", self.strength)
        self.dexterity = attributes.get("dexterity", self.dexterity)
        self.constitution = attributes.get("constitution", self.constitution)
        self.intelligence = attributes.get("intelligence", self.intelligence)
        self.wisdom = attributes.get("wisdom", self.wisdom)
        self.charisma = attributes.get("charisma", self.charisma)
        
        # Arrays and objects
        self.skills = npc_data.get("skills", self.skills)
        self.tags = npc_data.get("tags", self.tags)
        self.features = npc_data.get("features", self.features)
        self.inventory = npc_data.get("inventory", self.inventory)
        self.equipment = npc_data.get("equipment", self.equipment)
        self.gold = npc_data.get("gold", self.gold)
        
        # Location
        self.region_id = npc_data.get("region_id", self.region_id)
        self.location = npc_data.get("location", self.location)
        
        # Loyalty
        loyalty = npc_data.get("loyalty", {})
        self.loyalty_score = loyalty.get("score", self.loyalty_score)
        self.goodwill = loyalty.get("goodwill", self.goodwill)
        self.loyalty_tags = loyalty.get("tags", self.loyalty_tags)
        
        # Hidden traits
        self.hidden_ambition = npc_data.get("hidden_ambition", self.hidden_ambition)
        self.hidden_integrity = npc_data.get("hidden_integrity", self.hidden_integrity)
        self.hidden_discipline = npc_data.get("hidden_discipline", self.hidden_discipline)
        self.hidden_impulsivity = npc_data.get("hidden_impulsivity", self.hidden_impulsivity)
        self.hidden_pragmatism = npc_data.get("hidden_pragmatism", self.hidden_pragmatism)
        self.hidden_resilience = npc_data.get("hidden_resilience", self.hidden_resilience)
        
        # Other fields
        self.faction_affiliations = npc_data.get("faction_affiliations", self.faction_affiliations)
        self.reputation = npc_data.get("reputation", self.reputation)
        self.known_languages = npc_data.get("known_languages", self.known_languages)
        self.memory_summary = npc_data.get("memory_summary", self.memory_summary)
        self.rumor_index = npc_data.get("rumor_index", self.rumor_index)


class NpcMemory(UUIDMixin):
    """NPC memory system for tracking experiences and information"""
    
    __tablename__ = "npc_memories"
    __table_args__ = {'extend_existing': True}
    
    npc_id = Column(SQLAlchemyUUID(as_uuid=True), ForeignKey("npc_entities.id"), nullable=False, index=True)
    memory_id = Column(String(100), nullable=False, index=True)  # Unique memory identifier
    content = Column(Text, nullable=False)
    memory_type = Column(String(50), default="experience")  # experience, information, interaction, etc.
    importance = Column(Float, default=1.0)  # 0-10 scale
    emotion = Column(String(50))  # emotional context
    location = Column(String(100))  # where the memory occurred
    participants = Column(JSONB, default=list)  # other entities involved
    tags = Column(JSONB, default=list)  # memory categorization
    recalled_count = Column(Integer, default=0)  # how often accessed
    last_recalled = Column(DateTime)
    
    # Relationships
    npc = relationship("NpcEntity", back_populates="memories")
    
    def __repr__(self):
        return f"<NpcMemory(id={self.id}, npc_id={self.npc_id}, type={self.memory_type})>"


class NpcFactionAffiliation(UUIDMixin):
    """NPC faction relationships and roles"""
    
    __tablename__ = "npc_faction_affiliations"
    __table_args__ = {'extend_existing': True}
    
    npc_id = Column(SQLAlchemyUUID(as_uuid=True), ForeignKey("npc_entities.id"), nullable=False, index=True)
    faction_id = Column(SQLAlchemyUUID(as_uuid=True), nullable=False, index=True)  # Reference to faction
    role = Column(String(100), default="member")
    loyalty = Column(Float, default=5.0)  # 0-10 scale
    status = Column(String(50), default="active")  # active, inactive, expelled, etc.
    joined_date = Column(DateTime)
    rank = Column(String(100))
    contributions = Column(JSONB, default=list)  # notable contributions
    
    # Relationships
    npc = relationship("NpcEntity", back_populates="faction_relationships")
    
    def __repr__(self):
        return f"<NpcFactionAffiliation(npc_id={self.npc_id}, faction_id={self.faction_id}, role={self.role})>"


class NpcRumor(UUIDMixin):
    """NPC rumor knowledge and propagation"""
    
    __tablename__ = "npc_rumors"
    __table_args__ = {'extend_existing': True}
    
    npc_id = Column(SQLAlchemyUUID(as_uuid=True), ForeignKey("npc_entities.id"), nullable=False, index=True)
    rumor_id = Column(String(100), nullable=False, index=True)  # Unique rumor identifier
    content = Column(Text, nullable=False)
    source = Column(String(255))  # who told them
    credibility = Column(Float, default=5.0)  # 0-10 scale, how much NPC believes it
    spread_chance = Column(Float, default=0.5)  # 0-1 probability of sharing
    times_shared = Column(Integer, default=0)
    last_shared = Column(DateTime)
    learned_date = Column(DateTime)
    
    # Relationships
    npc = relationship("NpcEntity", back_populates="rumors")
    
    def __repr__(self):
        return f"<NpcRumor(id={self.id}, npc_id={self.npc_id}, credibility={self.credibility})>"


class NpcLocationHistory(UUIDMixin):
    """Track NPC movement and location history"""
    
    __tablename__ = "npc_location_history"
    __table_args__ = {'extend_existing': True}
    
    npc_id = Column(SQLAlchemyUUID(as_uuid=True), ForeignKey("npc_entities.id"), nullable=False, index=True)
    region_id = Column(String(100), nullable=False, index=True)
    location = Column(String(100), nullable=False)  # Format: "x_y"
    arrival_time = Column(DateTime, nullable=False)
    departure_time = Column(DateTime)
    travel_motive = Column(String(100))  # why they came here
    activity = Column(String(255))  # what they did here
    
    # Relationships
    npc = relationship("NpcEntity", back_populates="location_history")
    
    def __repr__(self):
        return f"<NpcLocationHistory(npc_id={self.npc_id}, location={self.location})>"


class NpcMotif(UUIDMixin):
    """NPC narrative motifs for autonomous behavior"""
    
    __tablename__ = "npc_motifs"
    __table_args__ = {'extend_existing': True}
    
    npc_id = Column(SQLAlchemyUUID(as_uuid=True), ForeignKey("npc_entities.id"), nullable=False, index=True)
    motif_id = Column(String(100), nullable=False, index=True)
    motif_type = Column(String(100), nullable=False)  # romance, revenge, ambition, etc.
    theme = Column(Integer)  # numeric theme identifier
    strength = Column(Float, default=1.0)  # 0-10 scale
    lifespan = Column(Integer, default=3)  # how long it should last
    entropy_tick = Column(Integer, default=0)  # current age
    weight = Column(Float, default=1.0)  # influence on behavior
    description = Column(Text)
    triggers = Column(JSONB, default=list)  # conditions that activate this motif
    status = Column(String(50), default="active")  # active, dormant, completed, abandoned
    
    # Relationships
    npc = relationship("NpcEntity", back_populates="motifs")
    
    def __repr__(self):
        return f"<NpcMotif(npc_id={self.npc_id}, type={self.motif_type}, strength={self.strength})>"


# ============================================================================
# Request/Response Models
# ============================================================================

class CreateNpcRequest(BaseModel):
    """Request model for creating npc"""
    
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    race: Optional[str] = Field("Human", max_length=100)
    properties: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    # Optional full character data for import from NPCBuilder
    npc_data: Optional[Dict[str, Any]] = Field(None, description="Complete NPC data from NPCBuilder")


class UpdateNpcRequest(BaseModel):
    """Request model for updating npc"""
    
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    status: Optional[str] = Field(None)
    properties: Optional[Dict[str, Any]] = None


class NpcResponse(BaseModel):
    """Response model for npc"""
    
    id: UUID
    name: str
    description: Optional[str]
    race: str
    status: str
    level: int
    attributes: Dict[str, int]
    location: Optional[str]
    region_id: Optional[str]
    properties: Dict[str, Any]
    created_at: datetime
    updated_at: Optional[datetime]
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class NpcListResponse(BaseModel):
    """Response model for npc lists"""
    
    items: List[NpcResponse]
    total: int
    page: int
    size: int
    has_next: bool
    has_prev: bool


# ============================================================================
# Memory System Models
# ============================================================================

class MemoryResponse(BaseModel):
    """Response model for NPC memories"""
    
    id: UUID
    memory_id: str
    content: str
    memory_type: str
    importance: float
    emotion: Optional[str]
    location: Optional[str]
    participants: List[str]
    tags: List[str]
    recalled_count: int
    created_at: datetime
    last_recalled: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Faction System Models
# ============================================================================

class FactionAffiliationResponse(BaseModel):
    """Response model for NPC faction affiliations"""
    
    id: UUID
    faction_id: UUID
    role: str
    loyalty: float
    status: str
    rank: Optional[str]
    joined_date: Optional[datetime]
    
    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Rumor System Models
# ============================================================================

class RumorResponse(BaseModel):
    """Response model for NPC rumors"""
    
    id: UUID
    rumor_id: str
    content: str
    source: Optional[str]
    credibility: float
    spread_chance: float
    times_shared: int
    learned_date: Optional[datetime]
    last_shared: Optional[datetime]
    
    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Motif System Models
# ============================================================================

class MotifResponse(BaseModel):
    """Response model for NPC motifs"""
    
    id: UUID
    motif_id: str
    motif_type: str
    strength: float
    description: Optional[str]
    status: str
    triggers: List[str]
    
    model_config = ConfigDict(from_attributes=True)

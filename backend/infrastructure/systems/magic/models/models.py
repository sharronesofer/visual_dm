"""
Canonical Magic System Infrastructure Models

These models implement the Development Bible's canonical magic system:
- MP-based spellcasting (not spell slots)
- Four magic domains: Nature, Arcane, Occult, Divine
- Permanent spell learning (no daily preparation)
- Concentration mechanics with save requirements
"""

from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON, ForeignKey, Float
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from pydantic import BaseModel, Field

Base = declarative_base()

# === DATABASE MODELS (SQLAlchemy) ===

class Spell(Base):
    """Canonical spell model - MP-based system"""
    __tablename__ = "spells"
    
    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text)
    school = Column(String(50), nullable=False)
    mp_cost = Column(Integer, nullable=False)  # Base MP cost (canonical)
    valid_domains = Column(JSON, nullable=False)  # List of domain names
    concentration = Column(Boolean, default=False)
    save_type = Column(String(20))  # "fortitude", "reflex", "will", or None
    damage_type = Column(String(50))
    duration_rounds = Column(Integer)
    target_type = Column(String(50))
    area_effect_radius = Column(Float)
    effect_data = Column(JSON)  # Spell effect configuration
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class CharacterMP(Base):
    """Character Mana Points tracking (canonical system)"""
    __tablename__ = "character_mp"
    
    character_id = Column(Integer, primary_key=True)
    current_mp = Column(Integer, nullable=False, default=0)
    max_mp = Column(Integer, nullable=False, default=0)
    mp_regeneration_rate = Column(Float, default=1.0)  # Multiplier for rest recovery
    last_rest = Column(DateTime)
    short_rests_taken = Column(Integer, default=0)  # Track short rests since long rest
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class CharacterDomainAccess(Base):
    """Character access to magic domains (canonical system)"""
    __tablename__ = "character_domain_access"
    
    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid4)
    character_id = Column(Integer, nullable=False)
    domain = Column(String(50), nullable=False)  # "arcane", "divine", "nature", "occult"
    mastery_level = Column(Integer, default=1)  # Higher levels = better efficiency
    primary_ability_score = Column(Integer, nullable=False)  # Character's ability in domain's primary
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class LearnedSpells(Base):
    """Permanently learned spells (canonical - no preparation)"""
    __tablename__ = "learned_spells"
    
    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid4)
    character_id = Column(Integer, nullable=False)
    spell_id = Column(PostgresUUID(as_uuid=True), ForeignKey("spells.id"), nullable=False)
    domain_learned = Column(String(50), nullable=False)  # Domain through which spell was learned
    learned_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship to spell
    spell = relationship("Spell")

class ConcentrationTracking(Base):
    """Active concentration effects (canonical system)"""
    __tablename__ = "concentration_tracking"
    
    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid4)
    character_id = Column(Integer, nullable=False)
    spell_id = Column(PostgresUUID(as_uuid=True), ForeignKey("spells.id"), nullable=False)
    target_id = Column(String(255))  # Can be character ID, object ID, or location
    started_at = Column(DateTime, default=datetime.utcnow)
    duration_rounds = Column(Integer)
    save_dc = Column(Integer)  # DC for concentration saves
    effect_data = Column(JSON)  # Current effect parameters
    is_active = Column(Boolean, default=True)
    
    # Relationship to spell
    spell = relationship("Spell")

# === API MODELS (Pydantic) ===

class SpellResponse(BaseModel):
    """Spell information for API responses"""
    id: UUID
    name: str
    description: Optional[str]
    school: str
    mp_cost: int
    valid_domains: List[str]
    concentration: bool
    save_type: Optional[str]
    damage_type: Optional[str]
    duration_rounds: Optional[int]
    target_type: Optional[str]
    area_effect_radius: Optional[float]
    effect_data: Optional[Dict[str, Any]]
    
    class Config:
        from_attributes = True

class CharacterMPResponse(BaseModel):
    """Character MP status for API responses"""
    character_id: int
    current_mp: int
    max_mp: int
    mp_regeneration_rate: float
    last_rest: Optional[datetime]
    short_rests_taken: int
    mp_percentage: float = Field(..., description="Current MP as percentage of max")
    
    class Config:
        from_attributes = True
    
    def __init__(self, **data):
        super().__init__(**data)
        # Calculate MP percentage
        if self.max_mp > 0:
            self.mp_percentage = round((self.current_mp / self.max_mp) * 100, 1)
        else:
            self.mp_percentage = 0.0

class DomainAccessResponse(BaseModel):
    """Character domain access for API responses"""
    id: UUID
    character_id: int
    domain: str
    mastery_level: int
    primary_ability_score: int
    efficiency_bonus: float = Field(..., description="MP cost efficiency from mastery")
    
    class Config:
        from_attributes = True

class LearnedSpellsResponse(BaseModel):
    """Character's learned spells for API responses"""
    character_id: int
    spells: List[SpellResponse]
    domains_available: List[str]
    total_spells_known: int
    
    class Config:
        from_attributes = True

class ConcentrationResponse(BaseModel):
    """Active concentration effect for API responses"""
    id: UUID
    character_id: int
    spell: SpellResponse
    target_id: Optional[str]
    started_at: datetime
    duration_rounds: Optional[int]
    save_dc: Optional[int]
    effect_data: Optional[Dict[str, Any]]
    rounds_remaining: Optional[int] = Field(None, description="Calculated remaining rounds")
    
    class Config:
        from_attributes = True

# === REQUEST MODELS ===

class CastSpellRequest(BaseModel):
    """Request to cast a spell using MP"""
    spell_id: UUID
    domain: str = Field(..., description="Magic domain to cast through")
    target_id: Optional[int] = Field(None, description="Target character/object ID")
    extra_mp: int = Field(0, description="Additional MP to spend for enhanced effects")
    target_location: Optional[str] = Field(None, description="Target location for area spells")

class RestoreMatrixPointsRequest(BaseModel):
    """Request to restore MP through rest"""
    rest_type: str = Field(..., description="'short' or 'long' rest")
    hours_spent: float = Field(..., description="Hours spent resting")
    safe_location: bool = Field(True, description="Whether resting in safe location")

class LearnSpellRequest(BaseModel):
    """Request to learn a new spell permanently"""
    spell_id: UUID
    domain: str = Field(..., description="Domain through which to learn the spell")

class UpdateDomainAccessRequest(BaseModel):
    """Request to update character's domain access"""
    domain: str
    mastery_level: Optional[int] = Field(None, description="New mastery level")
    primary_ability_score: Optional[int] = Field(None, description="Updated ability score")

class MetamagicCastRequest(BaseModel):
    """Request to cast spell with metamagic modifications"""
    spell_id: UUID
    domain: str
    metamagic_types: List[str] = Field(..., description="Types of metamagic to apply")
    target_id: Optional[int] = None
    extra_mp: int = Field(0, description="Additional MP beyond metamagic costs")

class SpellCombinationRequest(BaseModel):
    """Request to cast spell combination"""
    spell_ids: List[UUID] = Field(..., min_items=2, max_items=5)
    combination_name: str = Field(..., description="Name of the combination effect")
    primary_domain: str = Field(..., description="Primary domain for the combination")
    target_id: Optional[int] = None

# === UTILITY MODELS ===

class SpellCastResult(BaseModel):
    """Result of spell casting attempt"""
    success: bool
    mp_spent: int
    effects_applied: List[Dict[str, Any]]
    concentration_required: bool
    concentration_id: Optional[UUID] = None
    error_message: Optional[str] = None
    save_required: bool = False
    save_dc: Optional[int] = None
    damage_dealt: Optional[int] = None

class ConcentrationCheckResult(BaseModel):
    """Result of concentration save check"""
    success: bool
    roll_result: int
    dc_required: int
    concentration_maintained: bool
    effect_id: UUID

class MPRecoveryResult(BaseModel):
    """Result of MP recovery through rest"""
    mp_recovered: int
    new_current_mp: int
    rest_type: str
    hours_spent: float
    short_rests_remaining: int 
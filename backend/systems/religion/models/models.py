"""
Religion System Models

This module defines the data models for the religion system according to
the Development Bible standards.
"""

from typing import Optional, List, Dict, Any
from backend.infrastructure.database import Base, UUIDMixin, TimestampMixin
from datetime import datetime
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text, ForeignKey, Float, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as SQLAlchemyUUID, JSONB

from sqlalchemy.orm import relationship

# Religion Types - Expanded set for diverse world-building
RELIGION_TYPES = [
    # Traditional Categories
    "Monotheistic",      # Single deity worship
    "Polytheistic",      # Multiple deities worship
    "Pantheistic",       # God is everything/universe
    "Panentheistic",     # God contains universe but transcends it
    "Henotheistic",      # One primary god among many
    "Monolatrous",       # Worship one god while acknowledging others exist
    
    # Nature-Based
    "Animistic",         # Spirits in natural objects
    "Shamanistic",       # Spirit world mediation
    "Druidic",          # Nature worship and balance
    "Totemic",          # Animal/plant spirit guides
    "Elemental",        # Worship of natural elements
    
    # Philosophical/Abstract
    "Deistic",          # Creator god who doesn't intervene
    "Agnostic",         # Unknown/unknowable divine
    "Humanistic",       # Human-centered spirituality
    "Rationalistic",    # Reason-based belief system
    "Mystical",         # Direct spiritual experience
    "Esoteric",         # Hidden/secret knowledge
    
    # Structural/Social
    "Ancestor_Worship",  # Veneration of deceased ancestors
    "Imperial_Cult",     # Ruler/state worship
    "Mystery_Religion",  # Secret initiation rites
    "Monastic",         # Communal religious life
    "Evangelical",      # Spreading faith emphasis
    "Orthodox",         # Traditional doctrine adherence
    "Reformed",         # Modified traditional beliefs
    "Syncretic",        # Blended multiple traditions
    
    # Cosmic/Metaphysical
    "Dualistic",        # Good vs evil cosmic forces
    "Trinitarian",      # Three-aspect deity
    "Emanationist",     # Reality flows from divine source
    "Cyclical",         # Eternal cycles of creation/destruction
    "Apocalyptic",      # End times focus
    "Millenarian",      # Thousand-year divine kingdom
    
    # Modern/Fictional
    "Techno_Spiritual", # Technology and spirituality blend
    "Cosmic_Horror",    # Lovecraftian incomprehensible entities
    "Planar",          # Multiple reality planes
    "Dimensional",     # Cross-dimensional beings
    "Artificial",      # Created/constructed religions
    "Hybrid",          # Multiple type combinations
    
    # Cultural Specific
    "Tribal",          # Clan/tribe specific beliefs
    "Urban",           # City-centered worship
    "Nomadic",         # Wandering people's faith
    "Maritime",        # Sea/ocean focused
    "Underground",     # Subterranean/hidden worship
    "Celestial",       # Star/planet worship
    
    # Temporal
    "Ancient",         # Old, traditional ways
    "Emergent",        # Newly formed beliefs
    "Revivalist",      # Restored old traditions
    "Prophetic",       # Future revelation focused
    "Historical",      # Past event commemoration
    
    # Special Categories
    "Forbidden",       # Banned/outlawed religions
    "Cult",           # Small, devoted groups
    "Sect",           # Breakaway movements
    "Heretical",      # Considered false by mainstream
    "Folk",           # Common people's beliefs
    "State",          # Government endorsed
    "Universal",      # Claims to be for everyone
    "Exclusive",      # Limited membership
    "Inclusive",      # Open to all
    "Militant",       # Aggressive expansion
    "Pacifist",       # Non-violence emphasis
    "Ascetic",        # Self-denial practices
    "Hedonistic",     # Pleasure-seeking spiritual path
    "Scholarly",      # Learning/knowledge focused
    "Practical",      # Daily life application
    "Ritualistic",    # Ceremony emphasis
    "Contemplative",  # Meditation/reflection focus
    "Ecstatic",       # Emotional/trance states
    "Legalistic",     # Rule/law emphasis
    "Charismatic",    # Personal spiritual gifts
    "Institutional",  # Formal organization
    "Informal",       # Loose structure
    "Hierarchical",   # Ranked leadership
    "Egalitarian",    # Equal participation
    "Matriarchal",    # Female leadership
    "Patriarchal",    # Male leadership
    "Gnostic",        # Secret knowledge salvation
    "Fundamentalist", # Literal interpretation
    "Liberal",        # Progressive interpretation
    "Conservative",   # Traditional values
    "Radical",        # Extreme change advocacy
]

# Religion Status Types
RELIGION_STATUS = [
    "active",         # Currently practiced
    "dominant",       # Major influence in region
    "minority",       # Small but active
    "declining",      # Losing followers
    "growing",        # Gaining followers
    "established",    # Long-standing tradition
    "emerging",       # Recently formed
    "reformed",       # Recently changed
    "orthodox",       # Traditional unchanged
    "schismatic",     # Split from parent religion
    "syncretic",      # Merged with others
    "persecuted",     # Under oppression
    "protected",      # Government protection
    "state_religion", # Official government religion
    "banned",         # Illegal to practice
    "underground",    # Hidden practice
    "extinct",        # No longer practiced
    "revived",        # Brought back from extinction
    "dormant",        # Temporarily inactive
    "seasonal",       # Practiced at certain times
    "regional",       # Limited to specific areas
    "universal",      # Practiced everywhere
    "militant",       # Aggressive expansion
    "peaceful",       # Non-violent
    "isolationist",   # Avoids outside contact
    "missionary",     # Actively converts others
    "exclusive",      # Membership restrictions
    "inclusive",      # Open to all
    "heretical",      # Considered false by others
    "orthodox_approved", # Approved by mainstream
    "folk_tradition", # Informal cultural practice
    "institutional",  # Formal organization
    "mystical",       # Esoteric practices
    "practical",      # Daily life focused
    "ceremonial",     # Ritual emphasis
    "contemplative",  # Meditation focused
    "scholarly",      # Academic study
    "popular",        # Widely accepted
    "elite",          # Upper class only
    "common",         # Working class
    "rural",          # Countryside practice
    "urban",          # City practice
    "nomadic",        # Traveling peoples
    "settled",        # Fixed location
    "ancient",        # Very old tradition
    "modern",         # Recently developed
    "traditional",    # Unchanged practices
    "progressive",    # Evolving practices
    "conservative",   # Resistant to change
    "liberal",        # Open to change
    "fundamentalist", # Strict interpretation
    "moderate",       # Balanced approach
    "radical",        # Extreme positions
    "mainstream",     # Widely accepted
    "fringe",         # Edge of acceptance
    "cult",           # Small devoted group
    "sect",           # Breakaway movement
    "denomination",   # Organized branch
    "movement",       # Social change focus
    "revival",        # Renewed interest
    "reformation",    # Major changes
    "restoration",    # Return to origins
    "innovation",     # New practices
    "adaptation",     # Changed for circumstances
    "preservation",   # Maintaining traditions
    "transformation", # Major evolution
    "integration",    # Merging with others
    "separation",     # Breaking away
    "unification",    # Coming together
    "diversification", # Splitting into varieties
    "standardization", # Becoming uniform
    "localization",   # Adapting to local culture
    "globalization",  # Spreading worldwide
    "digitalization", # Online/virtual practice
    "modernization",  # Updating for current times
    "secularization", # Becoming less religious
    "spiritualization", # Becoming more spiritual
    "politicization", # Becoming political
    "commercialization", # Becoming commercial
    "academicization", # Becoming scholarly
    "popularization", # Becoming mainstream
    "marginalization", # Being pushed to edges
    "centralization", # Power concentrating
    "decentralization", # Power spreading out
    "formalization",  # Becoming more structured
    "informalization", # Becoming less structured
    "institutionalization", # Becoming organized
    "deinstitutionalization", # Becoming less organized
    "professionalization", # Clergy becoming professional
    "democratization", # Becoming more democratic
    "authoritarianization", # Becoming more authoritarian
    "liberalization", # Becoming more free
    "restriction",    # Becoming more limited
    "expansion",      # Growing in scope
    "contraction",    # Shrinking in scope
    "stabilization",  # Becoming stable
    "destabilization", # Becoming unstable
    "consolidation",  # Strengthening position
    "fragmentation",  # Breaking apart
    "renewal",        # Fresh start
    "decline",        # Weakening
    "resurgence",     # Coming back strong
    "stagnation",     # Not changing
    "evolution",      # Gradual change
    "revolution",     # Rapid change
    "crisis",         # Major problems
    "recovery",       # Overcoming problems
    "transition",     # In process of change
    "stability",      # Not changing
    "flux",           # Constantly changing
    "equilibrium",    # Balanced state
    "disequilibrium", # Unbalanced state
    "harmony",        # Peaceful coexistence
    "conflict",       # Fighting with others
    "cooperation",    # Working with others
    "competition",    # Competing with others
    "collaboration",  # Partnering with others
    "isolation",      # Separate from others
    "integration",    # Joining with others
    "assimilation",   # Absorbing others
    "accommodation",  # Adapting to others
    "resistance",     # Fighting against change
    "acceptance",     # Embracing change
    "tolerance",      # Allowing differences
    "intolerance",    # Not allowing differences
    "pluralism",      # Many beliefs coexist
    "monism",         # One belief dominates
    "diversity",      # Many varieties
    "uniformity",     # All the same
    "heterogeneity",  # Mixed composition
    "homogeneity",    # Same composition
    "complexity",     # Many parts
    "simplicity",     # Few parts
    "sophistication", # Highly developed
    "primitiveness",  # Basic development
    "advancement",    # Moving forward
    "regression",     # Moving backward
    "progress",       # Improving
    "deterioration",  # Getting worse
    "enhancement",    # Getting better
    "degradation",    # Getting worse
    "optimization",   # Best possible
    "suboptimization", # Less than best
    "maximization",   # As much as possible
    "minimization",   # As little as possible
    "intensification", # Becoming stronger
    "attenuation",    # Becoming weaker
    "amplification",  # Becoming louder
    "diminishment",   # Becoming quieter
    "enrichment",     # Becoming richer
    "impoverishment", # Becoming poorer
    "empowerment",    # Gaining power
    "disempowerment", # Losing power
    "strengthening",  # Getting stronger
    "weakening",      # Getting weaker
    "vitalization",   # Becoming more alive
    "devitalization", # Becoming less alive
    "energization",   # Gaining energy
    "enervation",     # Losing energy
    "activation",     # Becoming active
    "deactivation",   # Becoming inactive
    "mobilization",   # Getting organized
    "demobilization", # Becoming disorganized
    "organization",   # Becoming structured
    "disorganization", # Becoming unstructured
    "systematization", # Becoming systematic
    "desystematization", # Becoming unsystematic
    "rationalization", # Becoming logical
    "irrationalization", # Becoming illogical
    "clarification",  # Becoming clear
    "obfuscation",    # Becoming unclear
    "illumination",   # Bringing light
    "obscuration",    # Bringing darkness
    "revelation",     # Revealing truth
    "concealment",    # Hiding truth
    "disclosure",     # Making known
    "secrecy",        # Keeping hidden
    "transparency",   # Open and clear
    "opacity",        # Closed and unclear
    "accessibility",  # Easy to reach
    "inaccessibility", # Hard to reach
    "availability",   # Ready for use
    "unavailability", # Not ready for use
    "presence",       # Being there
    "absence",        # Not being there
    "existence",      # Being real
    "nonexistence",   # Not being real
    "reality",        # What is true
    "unreality",      # What is not true
    "actuality",      # What actually is
    "potentiality",   # What could be
    "possibility",    # What might be
    "impossibility",  # What cannot be
    "probability",    # What is likely
    "improbability",  # What is unlikely
    "certainty",      # What is sure
    "uncertainty",    # What is unsure
    "definiteness",   # What is definite
    "indefiniteness", # What is indefinite
    "specificity",    # What is specific
    "generality",     # What is general
    "particularity",  # What is particular
    "universality",   # What is universal
    "locality",       # What is local
    "globality",      # What is global
    "regionality",    # What is regional
    "nationality",    # What is national
    "internationality", # What is international
    "transnationality", # What crosses nations
    "supranationality", # What is above nations
    "subnationality", # What is below nations
    "ethnicity",      # What is ethnic
    "multiethnicity", # What is multiethnic
    "monoethnicity",  # What is monoethnic
    "interethnicity", # What is interethnic
    "transculturality", # What crosses cultures
    "multiculturality", # What is multicultural
    "monoculturality", # What is monocultural
    "interculturality", # What is intercultural
    "cross_cultural", # What crosses cultures
    "intra_cultural", # What is within culture
    "extra_cultural", # What is outside culture
    "supra_cultural", # What is above culture
    "sub_cultural",   # What is below culture
    "counter_cultural", # What opposes culture
    "pro_cultural",   # What supports culture
    "anti_cultural",  # What is against culture
    "non_cultural",   # What is not cultural
    "pre_cultural",   # What is before culture
    "post_cultural",  # What is after culture
    "meta_cultural",  # What is about culture
    "para_cultural",  # What is beside culture
    "pseudo_cultural", # What seems cultural
    "quasi_cultural", # What is almost cultural
    "semi_cultural",  # What is half cultural
    "proto_cultural", # What is early cultural
    "neo_cultural",   # What is new cultural
    "retro_cultural", # What is old cultural
    "ultra_cultural", # What is extremely cultural
    "hyper_cultural", # What is overly cultural
    "super_cultural", # What is very cultural
    "mega_cultural",  # What is hugely cultural
    "macro_cultural", # What is large cultural
    "micro_cultural", # What is small cultural
    "mini_cultural",  # What is tiny cultural
    "nano_cultural",  # What is minute cultural
    "giga_cultural",  # What is giant cultural
    "tera_cultural",  # What is massive cultural
    "peta_cultural",  # What is enormous cultural
    "exa_cultural",   # What is vast cultural
    "zetta_cultural", # What is immense cultural
    "yotta_cultural", # What is colossal cultural
]

class ReligionBaseModel(BaseModel):
    """Base model for religion system with common fields"""
    
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    is_active: bool = Field(default=True)
    extra_metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)  # Renamed from metadata

class ReligionModel(ReligionBaseModel):
    """Primary model for religion system"""
    
    name: str = Field(..., description="Name of the religion")
    description: Optional[str] = Field(None, description="Description of the religion")
    status: str = Field(default="active", description="Status of the religion")
    properties: Optional[Dict[str, Any]] = Field(default_factory=dict)

class ReligionEntity(Base):
    """SQLAlchemy entity for religion system"""
    
    __tablename__ = f"religion_entities"
    __table_args__ = {'extend_existing': True}
    
    id = Column(SQLAlchemyUUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    status = Column(String(50), default="active", index=True)
    properties = Column(JSONB, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True, index=True)

    def __repr__(self):
        return f"<ReligionEntity(id={self.id}, name={self.name})>"

    def to_dict(self) -> Dict[str, Any]:
        """Convert entity to dictionary"""
        return {
            "id": str(self.id),
            "name": self.name,
            "description": self.description,
            "status": self.status,
            "properties": self.properties or {},
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "is_active": self.is_active
        }

# Request/Response Models with Unity Frontend Compatibility
class CreateReligionRequest(BaseModel):
    """Request model for creating religion - Unity frontend compatible"""
    
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    
    # Unity frontend expected fields
    type: Optional[str] = Field("Monotheistic", description="Religion type (Monotheistic, Polytheistic, etc.)")
    origin_story: Optional[str] = Field(None, description="Origin story of the religion")
    core_beliefs: Optional[List[str]] = Field(default_factory=list, description="Core beliefs")
    tenets: Optional[List[str]] = Field(default_factory=list, description="Religious tenets")
    practices: Optional[List[str]] = Field(default_factory=list, description="Religious practices")
    holy_places: Optional[List[str]] = Field(default_factory=list, description="Holy places")
    sacred_texts: Optional[List[str]] = Field(default_factory=list, description="Sacred texts")
    clergy_structure: Optional[str] = Field(None, description="Clergy organizational structure")
    
    # Legacy field for backward compatibility
    properties: Optional[Dict[str, Any]] = Field(default_factory=dict)

class UpdateReligionRequest(BaseModel):
    """Request model for updating religion - Unity frontend compatible"""
    
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    status: Optional[str] = Field(None)
    
    # Unity frontend expected fields
    type: Optional[str] = Field(None, description="Religion type")
    origin_story: Optional[str] = Field(None, description="Origin story")
    core_beliefs: Optional[List[str]] = Field(None, description="Core beliefs")
    tenets: Optional[List[str]] = Field(None, description="Religious tenets")
    practices: Optional[List[str]] = Field(None, description="Religious practices")
    holy_places: Optional[List[str]] = Field(None, description="Holy places")
    sacred_texts: Optional[List[str]] = Field(None, description="Sacred texts")
    clergy_structure: Optional[str] = Field(None, description="Clergy structure")
    
    # Legacy field for backward compatibility
    properties: Optional[Dict[str, Any]] = None

class ReligionResponse(BaseModel):
    """Response model for religion - Unity frontend compatible"""
    
    model_config = ConfigDict(from_attributes=True)
    
    # Core fields
    id: UUID
    name: str
    description: Optional[str] = None
    status: str = "active"
    created_at: datetime
    updated_at: Optional[datetime] = None
    is_active: bool = True
    
    # Unity frontend expected fields
    type: str = Field(default="Monotheistic", description="Religion type")
    origin_story: Optional[str] = Field(None, description="Origin story")
    core_beliefs: List[str] = Field(default_factory=list, description="Core beliefs")
    practices: List[str] = Field(default_factory=list, description="Religious practices")
    clergy_structure: Optional[str] = Field(None, description="Clergy structure")
    holy_texts: List[str] = Field(default_factory=list, description="Sacred texts")
    deities: List[Dict[str, Any]] = Field(default_factory=list, description="Associated deities")
    followers_count: int = Field(default=0, description="Number of followers")
    influence_regions: List[str] = Field(default_factory=list, description="Regions of influence")
    
    # Legacy field for custom properties
    properties: Dict[str, Any] = Field(default_factory=dict)
    
    @classmethod
    def from_entity(cls, entity: ReligionEntity) -> "ReligionResponse":
        """Create response from SQLAlchemy entity with Unity field mapping"""
        
        # Extract Unity fields from properties or use defaults
        props = entity.properties or {}
        
        return cls(
            id=entity.id,
            name=entity.name,
            description=entity.description,
            status=entity.status,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            is_active=entity.is_active,
            
            # Map Unity fields from properties
            type=props.get("type", "Monotheistic"),
            origin_story=props.get("origin_story"),
            core_beliefs=props.get("core_beliefs", []),
            practices=props.get("practices", []),
            clergy_structure=props.get("clergy_structure"),
            holy_texts=props.get("holy_texts", []),
            deities=props.get("deities", []),
            followers_count=props.get("followers_count", 0),
            influence_regions=props.get("influence_regions", []),
            
            properties=props
        )

class ReligionListResponse(BaseModel):
    """Response model for religion lists"""
    
    items: List[ReligionResponse]
    total: int
    page: int
    size: int
    has_next: bool
    has_prev: bool

# Sub-resource models for Unity frontend compatibility
class DeityRequest(BaseModel):
    """Request model for creating/updating deities"""
    
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    domain: Optional[str] = None
    alignment: Optional[str] = None
    symbols: Optional[List[str]] = Field(default_factory=list)
    holy_days: Optional[List[str]] = Field(default_factory=list)
    powers: Optional[List[str]] = Field(default_factory=list)

class DeityResponse(BaseModel):
    """Response model for deities"""
    
    id: UUID
    name: str
    description: Optional[str]
    domain: Optional[str]
    alignment: Optional[str]
    symbols: List[str]
    holy_days: List[str]
    powers: List[str]
    worshiper_count: int = 0
    religion_id: UUID

class ReligiousPracticeRequest(BaseModel):
    """Request model for religious practices"""
    
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    frequency: Optional[str] = None
    participants: Optional[int] = 0
    location_type: Optional[str] = None
    required_items: Optional[List[str]] = Field(default_factory=list)

class ReligiousPracticeResponse(BaseModel):
    """Response model for religious practices"""
    
    id: UUID
    name: str
    description: Optional[str]
    frequency: Optional[str]
    participants: int
    location_type: Optional[str]
    required_items: List[str]
    religion_id: UUID

class ReligiousEventRequest(BaseModel):
    """Request model for religious events"""
    
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    event_type: Optional[str] = None
    date: Optional[datetime] = None
    duration: Optional[int] = 1
    location: Optional[str] = None
    participants: Optional[List[str]] = Field(default_factory=list)

class ReligiousEventResponse(BaseModel):
    """Response model for religious events"""
    
    id: UUID
    name: str
    description: Optional[str]
    event_type: Optional[str]
    date: datetime
    duration: int
    location: Optional[str]
    participants: List[str]
    religion_id: UUID

class ReligiousInfluenceRequest(BaseModel):
    """Request model for religious influence"""
    
    influence_level: Optional[float] = 0.0
    follower_count: Optional[int] = 0
    temples_count: Optional[int] = 0
    clergy_count: Optional[int] = 0

class ReligiousInfluenceResponse(BaseModel):
    """Response model for religious influence"""
    
    id: UUID
    religion_id: UUID
    region_id: str
    influence_level: float
    follower_count: int
    temples_count: int
    clergy_count: int
    last_updated: datetime

class ReligionMembershipEntity(Base):
    """
    SQLAlchemy model for religion membership with cross-faction support.
    
    Supports the Bible requirement for cross-faction membership by not
    including faction restrictions in the model.
    """
    __tablename__ = 'religion_memberships'
    
    id = Column(SQLAlchemyUUID(as_uuid=True), primary_key=True, default=uuid4)
    entity_id = Column(String, nullable=False, index=True)  # Can be character, NPC, faction, etc.
    religion_id = Column(SQLAlchemyUUID(as_uuid=True), ForeignKey('religions.id'), nullable=False, index=True)
    entity_type = Column(String, nullable=False, default='character')  # character, npc, faction, etc.
    
    # Use float for devotion as per code standards (0.0-1.0 scale)
    devotion = Column(Float, nullable=False, default=0.5)  # 0.0 to 1.0 scale
    
    # Separate status and role fields as per code design
    status = Column(String, nullable=False, default='member')  # member, inactive, expelled, etc.
    role = Column(String, nullable=True)  # priest, acolyte, elder, etc. (optional specific role)
    
    # Timestamps using proper field names
    joined_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    last_activity = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    is_public = Column(Boolean, nullable=False, default=True)  # Whether membership is publicly known
    metadata = Column(JSONB, nullable=True, default=dict)  # Additional flexible data
    
    # Relationship to religion
    religion = relationship("ReligionEntity", back_populates="memberships")
    
    def __repr__(self):
        return f"<ReligionMembership(entity_id='{self.entity_id}', religion_id='{self.religion_id}', devotion={self.devotion})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format matching JSON schema."""
        return {
            'id': str(self.id),
            'entity_id': self.entity_id,
            'religion_id': str(self.religion_id),
            'entity_type': self.entity_type,
            'devotion': self.devotion,  # Float value 0.0-1.0
            'status': self.status,
            'role': self.role,
            'joined_date': self.joined_date.isoformat() if self.joined_date else None,
            'last_activity': self.last_activity.isoformat() if self.last_activity else None,
            'is_public': self.is_public,
            'metadata': self.metadata or {}
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ReligionMembershipEntity':
        """Create instance from dictionary data."""
        return cls(
            id=data.get('id'),
            entity_id=data['entity_id'],
            religion_id=data['religion_id'],
            entity_type=data.get('entity_type', 'character'),
            devotion=float(data.get('devotion', 0.5)),  # Ensure float conversion
            status=data.get('status', 'member'),
            role=data.get('role'),
            joined_date=datetime.fromisoformat(data['joined_date']) if data.get('joined_date') else datetime.utcnow(),
            last_activity=datetime.fromisoformat(data['last_activity']) if data.get('last_activity') else datetime.utcnow(),
            is_public=data.get('is_public', True),
            metadata=data.get('metadata', {})
        )

# Add relationship to ReligionEntity
ReligionEntity.memberships = relationship("ReligionMembershipEntity", back_populates="religion", cascade="all, delete-orphan")

class RegionalInfluenceEntity(Base):
    """SQLAlchemy entity for cached regional influence calculations"""
    
    __tablename__ = "religion_regional_influence"
    __table_args__ = {'extend_existing': True}
    
    id = Column(SQLAlchemyUUID(as_uuid=True), primary_key=True, default=uuid4)
    religion_id = Column(SQLAlchemyUUID(as_uuid=True), ForeignKey('religion_entities.id'), nullable=False, index=True)
    region_id = Column(String(255), nullable=False, index=True)  # Region identifier
    
    # Cached influence metrics
    influence_level = Column(Float, default=0.0, nullable=False)  # 0.0 to 1.0
    follower_count = Column(Integer, default=0, nullable=False)
    temple_count = Column(Integer, default=0, nullable=False)
    clergy_count = Column(Integer, default=0, nullable=False)
    
    # Influence factors
    political_influence = Column(Float, default=0.0)  # Government connections
    economic_influence = Column(Float, default=0.0)   # Economic power
    cultural_influence = Column(Float, default=0.0)   # Cultural impact
    military_influence = Column(Float, default=0.0)   # Military connections
    
    # Cache management
    last_calculated = Column(DateTime, default=datetime.utcnow, nullable=False)
    calculation_version = Column(Integer, default=1)  # For cache invalidation
    is_stale = Column(Boolean, default=False, index=True)  # Needs recalculation
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    extra_metadata = Column(JSONB, default=dict)  # Renamed from metadata to avoid SQLAlchemy conflict
    
    # Relationships
    religion = relationship("ReligionEntity", back_populates="regional_influences")
    
    # Unique constraint
    __table_args__ = (
        UniqueConstraint('religion_id', 'region_id', name='unique_religion_region'),
        {'extend_existing': True}
    )
    
    def __repr__(self):
        return f"<RegionalInfluenceEntity(religion_id={self.religion_id}, region_id={self.region_id}, influence={self.influence_level})>"

    def to_dict(self) -> Dict[str, Any]:
        """Convert regional influence entity to dictionary"""
        return {
            "id": str(self.id),
            "religion_id": str(self.religion_id),
            "region_id": self.region_id,
            "influence_level": self.influence_level,
            "follower_count": self.follower_count,
            "temple_count": self.temple_count,
            "clergy_count": self.clergy_count,
            "political_influence": self.political_influence,
            "economic_influence": self.economic_influence,
            "cultural_influence": self.cultural_influence,
            "military_influence": self.military_influence,
            "last_calculated": self.last_calculated.isoformat() if self.last_calculated else None,
            "calculation_version": self.calculation_version,
            "is_stale": self.is_stale,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "metadata": self.extra_metadata or {}
        }

# Add relationship to ReligionEntity
ReligionEntity.regional_influences = relationship("RegionalInfluenceEntity", back_populates="religion", cascade="all, delete-orphan")

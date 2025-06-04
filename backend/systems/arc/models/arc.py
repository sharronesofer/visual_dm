"""
Arc system - Main Arc models and enums.

This module implements the main Arc model with types, statuses, and priorities
that the repositories expect to import.
"""

from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime
from uuid import UUID, uuid4
from enum import Enum
from pydantic import BaseModel, Field, validator, ConfigDict
from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID as SQLAlchemyUUID, JSONB

from sqlalchemy.orm import relationship
from backend.infrastructure.database import Base, UUIDMixin, TimestampMixin

from backend.infrastructure.shared.models.models import SharedBaseModel

class ArcType(Enum):
    """Types of arcs"""
    GLOBAL = "global"
    REGIONAL = "regional"
    CHARACTER = "character"
    NPC = "npc"
    FACTION = "faction"
    QUEST = "quest"

class ArcStatus(Enum):
    """Status of arcs"""
    PENDING = "pending"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"

class ArcPriority(Enum):
    """Priority levels for arcs"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ArcRelationshipType(Enum):
    """Types of relationships between arcs"""
    SEQUEL = "sequel"                    # Arc B follows Arc A chronologically
    PREQUEL = "prequel"                  # Arc A sets up Arc B  
    PARALLEL = "parallel"                # Arcs run simultaneously and influence each other
    BRANCHING = "branching"              # Arc A outcome determines Arc B variant
    CONFLUENCE = "confluence"            # Multiple arcs merge into one
    THEMATIC_LINK = "thematic_link"      # Arcs share themes but different characters/locations
    CONTINUATION = "continuation"        # Arc B directly continues Arc A story
    CONSEQUENCE = "consequence"          # Arc B deals with consequences of Arc A

class ArcInfluenceLevel(Enum):
    """Level of influence one arc has on another"""
    MINIMAL = "minimal"      # Small references or minor character appearances
    MODERATE = "moderate"    # Shared characters or locations, some plot relevance
    MAJOR = "major"         # Significant plot elements carry over
    CRITICAL = "critical"   # Arc outcome fundamentally changes the follow-up arc

class ArcRelationship(BaseModel):
    """Model for relationships between arcs"""
    
    id: UUID = Field(default_factory=uuid4)
    source_arc_id: UUID = Field(..., description="The arc that influences another")
    target_arc_id: UUID = Field(..., description="The arc that is influenced")
    relationship_type: ArcRelationshipType = Field(..., description="Type of relationship")
    influence_level: ArcInfluenceLevel = Field(default=ArcInfluenceLevel.MODERATE)
    influence_data: Dict[str, Any] = Field(default_factory=dict, description="Specific influence details")
    narrative_connection: Optional[str] = Field(None, description="How the arcs connect narratively")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    @validator('source_arc_id', 'target_arc_id')
    def validate_arc_ids_different(cls, v, values):
        if 'source_arc_id' in values and v == values['source_arc_id']:
            raise ValueError('Arc cannot have relationship with itself')
        return v

class ArcModel(SharedBaseModel):
    """Model for main arc entity"""
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    title: str = Field(..., description="Title of the arc")
    description: Optional[str] = Field(None, description="Description of the arc")
    arc_type: ArcType = Field(..., description="Type of the arc")
    status: ArcStatus = Field(default=ArcStatus.PENDING, description="Current status")
    priority: ArcPriority = Field(default=ArcPriority.MEDIUM, description="Priority level")
    
    # Associated entities
    region_id: Optional[str] = Field(None, description="Associated region ID")
    character_id: Optional[str] = Field(None, description="Associated character ID")
    npc_id: Optional[str] = Field(None, description="Associated NPC ID")
    faction_ids: List[str] = Field(default_factory=list, description="Associated faction IDs")
    
    # Arc content
    narrative_summary: Optional[str] = Field(None, description="Overall narrative summary")
    objectives: List[str] = Field(default_factory=list, description="Main objectives")
    themes: List[str] = Field(default_factory=list, description="Thematic elements")
    
    # Progression tracking
    total_steps: int = Field(default=0, description="Total number of steps")
    completed_steps: int = Field(default=0, description="Number of completed steps")
    progress_percentage: float = Field(default=0.0, description="Overall progress percentage")
    
    # Timing
    estimated_duration_hours: Optional[float] = Field(None, description="Estimated duration in hours")
    actual_duration_hours: Optional[float] = Field(None, description="Actual duration in hours")
    start_date: Optional[datetime] = Field(None, description="When the arc started")
    end_date: Optional[datetime] = Field(None, description="When the arc ended")
    last_activity: Optional[datetime] = Field(None, description="Last activity timestamp")
    
    # Metadata
    tags: List[str] = Field(default_factory=list, description="Tags for categorization")
    difficulty_level: Optional[int] = Field(None, description="Difficulty level 1-10")
    player_impact: Optional[str] = Field(None, description="Expected player impact")
    world_impact: Optional[str] = Field(None, description="Expected world impact")
    
    # Relationships - NEW
    predecessor_arcs: List[UUID] = Field(default_factory=list, description="Arcs that must complete before this one")
    successor_arcs: List[UUID] = Field(default_factory=list, description="Arcs that follow this one")
    related_arcs: List[UUID] = Field(default_factory=list, description="Arcs with thematic or narrative connections")
    
    # LLM Integration for relationships - NEW  
    relationship_generation_prompt: Optional[str] = Field(None, description="Prompt for generating follow-up arcs")
    outcome_influences: Dict[str, Any] = Field(default_factory=dict, description="How different outcomes affect future arcs")
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    arc_metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

    @validator('progress_percentage')
    def validate_progress_percentage(cls, v):
        if v < 0.0 or v > 100.0:
            raise ValueError('Progress percentage must be between 0 and 100')
        return v

    @validator('difficulty_level')
    def validate_difficulty_level(cls, v):
        if v is not None and (v < 1 or v > 10):
            raise ValueError('Difficulty level must be between 1 and 10')
        return v

    @validator('completed_steps')
    def validate_completed_steps(cls, v, values):
        total_steps = values.get('total_steps', 0)
        if v > total_steps:
            raise ValueError('Completed steps cannot exceed total steps')
        return v

    @validator('predecessor_arcs', 'successor_arcs', 'related_arcs')
    def validate_arc_relationships(cls, v):
        if len(v) > 10:  # Reasonable limit
            raise ValueError('Too many arc relationships (max 10 per type)')
        return v

    def validate_business_rules(self) -> List[str]:
        """
        Validate business rules for this arc including relationships.
        
        Returns:
            List of validation errors
        """
        from backend.systems.arc.business_rules import validate_arc_business_rules
        return validate_arc_business_rules(self.dict())
    
    def calculate_relationship_complexity(self) -> Tuple[int, List[str]]:
        """
        Calculate complexity score based on arc relationships.
        
        Returns:
            Tuple of (complexity_score, complexity_factors)
        """
        score = 0
        factors = []
        
        # Predecessor complexity
        if self.predecessor_arcs:
            pred_score = len(self.predecessor_arcs) * 2
            score += pred_score
            factors.append(f"Predecessors: +{pred_score} ({len(self.predecessor_arcs)} arcs)")
        
        # Successor complexity
        if self.successor_arcs:
            succ_score = len(self.successor_arcs) * 3  # More complex to plan
            score += succ_score
            factors.append(f"Successors: +{succ_score} ({len(self.successor_arcs)} arcs)")
        
        # Related arcs complexity
        if self.related_arcs:
            rel_score = len(self.related_arcs)
            score += rel_score
            factors.append(f"Related: +{rel_score} ({len(self.related_arcs)} arcs)")
        
        # Outcome influences complexity
        if self.outcome_influences:
            outcome_score = len(self.outcome_influences) * 2
            score += outcome_score
            factors.append(f"Outcome branches: +{outcome_score} ({len(self.outcome_influences)} outcomes)")
        
        return score, factors
    
    def get_suggested_follow_up_prompt(self) -> str:
        """
        Generate a prompt for LLM to create follow-up arcs based on this arc's completion.
        
        Returns:
            Formatted prompt for LLM
        """
        base_prompt = f"""
Based on the completion of the arc "{self.title}":

Arc Details:
- Type: {self.arc_type.value}
- Themes: {', '.join(self.themes) if self.themes else 'None specified'}
- Objectives: {'; '.join(self.objectives) if self.objectives else 'None specified'}
- Player Impact: {self.player_impact or 'Not specified'}
- World Impact: {self.world_impact or 'Not specified'}
- Involved Factions: {', '.join(self.faction_ids) if self.faction_ids else 'None'}

Current Outcome Influences: {self.outcome_influences if self.outcome_influences else 'None defined'}

Please suggest 2-3 potential follow-up arcs that could naturally emerge from this arc's conclusion. Consider:
1. Immediate consequences and reactions
2. Long-term implications for the world/characters
3. Unresolved plot threads
4. New conflicts or opportunities created

For each suggested arc, provide:
- Title and brief description
- Arc type and estimated complexity
- Relationship type to this arc (sequel, consequence, etc.)
- Key themes and potential objectives
- How it builds upon or responds to this arc's conclusion
"""
        
        if self.relationship_generation_prompt:
            base_prompt += f"\n\nAdditional Context: {self.relationship_generation_prompt}"
        
        return base_prompt
    
    def can_start(self, completed_arc_ids: List[UUID] = None) -> Tuple[bool, str]:
        """
        Check if this arc can start based on predecessor requirements.
        
        Args:
            completed_arc_ids: List of arc IDs that have been completed
            
        Returns:
            Tuple of (can_start, reason)
        """
        if not self.predecessor_arcs:
            return True, "No prerequisites required"
        
        if completed_arc_ids is None:
            completed_arc_ids = []
        
        completed_set = set(completed_arc_ids)
        required_set = set(self.predecessor_arcs)
        
        missing_prerequisites = required_set - completed_set
        
        if missing_prerequisites:
            return False, f"Missing prerequisite arcs: {list(missing_prerequisites)}"
        
        return True, "All prerequisites completed"
    
    def get_relationship_summary(self) -> Dict[str, Any]:
        """
        Get a summary of this arc's relationships with other arcs.
        
        Returns:
            Dictionary with relationship information
        """
        complexity_score, factors = self.calculate_relationship_complexity()
        
        return {
            "has_relationships": bool(self.predecessor_arcs or self.successor_arcs or self.related_arcs),
            "relationship_complexity": complexity_score,
            "complexity_factors": factors,
            "predecessor_count": len(self.predecessor_arcs),
            "successor_count": len(self.successor_arcs),
            "related_count": len(self.related_arcs),
            "has_outcome_branches": bool(self.outcome_influences),
            "outcome_branch_count": len(self.outcome_influences),
            "requires_llm_generation": bool(self.relationship_generation_prompt),
            "can_generate_followups": bool(self.themes and self.objectives)
        }

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class Arc(Base):
    """SQLAlchemy entity for main arc"""
    
    __tablename__ = "arc_entities"
    
    id = Column(SQLAlchemyUUID(as_uuid=True), primary_key=True, default=uuid4)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    arc_type = Column(SQLEnum(ArcType), nullable=False, index=True)
    status = Column(SQLEnum(ArcStatus), default=ArcStatus.PENDING, index=True)
    priority = Column(SQLEnum(ArcPriority), default=ArcPriority.MEDIUM, index=True)
    
    # Associated entities
    region_id = Column(String(255), index=True)
    character_id = Column(String(255), index=True)
    npc_id = Column(String(255), index=True)
    faction_ids = Column(JSONB, default=list)
    
    # Arc content
    narrative_summary = Column(Text)
    objectives = Column(JSONB, default=list)
    themes = Column(JSONB, default=list)
    
    # Progression tracking
    total_steps = Column(Integer, default=0)
    completed_steps = Column(Integer, default=0)
    progress_percentage = Column(Integer, default=0)
    
    # Timing
    estimated_duration_hours = Column(Integer)
    actual_duration_hours = Column(Integer)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    last_activity = Column(DateTime, index=True)
    
    # Metadata
    tags = Column(JSONB, default=list)
    difficulty_level = Column(Integer)
    player_impact = Column(String(255))
    world_impact = Column(String(255))
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    arc_metadata = Column(JSONB, default=dict)

    # Relationships could be added here later
    # steps = relationship("ArcStepEntity", back_populates="arc")
    # progressions = relationship("ArcProgressionEntity", back_populates="arc")
    # completion_records = relationship("ArcCompletionRecordEntity", back_populates="arc")

    def __repr__(self):
        return f"<Arc(id={self.id}, title='{self.title}', type={self.arc_type.value}, status={self.status.value})>"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "arc_type": self.arc_type.value if self.arc_type else None,
            "status": self.status.value if self.status else None,
            "priority": self.priority.value if self.priority else None,
            "region_id": self.region_id,
            "character_id": self.character_id,
            "npc_id": self.npc_id,
            "faction_ids": self.faction_ids,
            "narrative_summary": self.narrative_summary,
            "objectives": self.objectives,
            "themes": self.themes,
            "total_steps": self.total_steps,
            "completed_steps": self.completed_steps,
            "progress_percentage": self.progress_percentage,
            "estimated_duration_hours": self.estimated_duration_hours,
            "actual_duration_hours": self.actual_duration_hours,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "last_activity": self.last_activity,
            "tags": self.tags,
            "difficulty_level": self.difficulty_level,
            "player_impact": self.player_impact,
            "world_impact": self.world_impact,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "arc_metadata": self.arc_metadata
        }

# Request/Response Models
class CreateArcRequest(BaseModel):
    """Request model for creating arc"""
    
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    arc_type: ArcType = Field(..., description="Type of the arc")
    priority: ArcPriority = Field(default=ArcPriority.MEDIUM)
    region_id: Optional[str] = Field(None, max_length=255)
    character_id: Optional[str] = Field(None, max_length=255)
    npc_id: Optional[str] = Field(None, max_length=255)
    faction_ids: Optional[List[str]] = Field(default_factory=list)
    narrative_summary: Optional[str] = Field(None, max_length=5000)
    objectives: Optional[List[str]] = Field(default_factory=list)
    themes: Optional[List[str]] = Field(default_factory=list)
    estimated_duration_hours: Optional[float] = Field(None, ge=0.0)
    tags: Optional[List[str]] = Field(default_factory=list)
    difficulty_level: Optional[int] = Field(None, ge=1, le=10)
    player_impact: Optional[str] = Field(None, max_length=255)
    world_impact: Optional[str] = Field(None, max_length=255)

class UpdateArcRequest(BaseModel):
    """Request model for updating arc"""
    
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    arc_type: Optional[ArcType] = None
    status: Optional[ArcStatus] = None
    priority: Optional[ArcPriority] = None
    region_id: Optional[str] = Field(None, max_length=255)
    character_id: Optional[str] = Field(None, max_length=255)
    npc_id: Optional[str] = Field(None, max_length=255)
    faction_ids: Optional[List[str]] = None
    narrative_summary: Optional[str] = Field(None, max_length=5000)
    objectives: Optional[List[str]] = None
    themes: Optional[List[str]] = None
    estimated_duration_hours: Optional[float] = Field(None, ge=0.0)
    actual_duration_hours: Optional[float] = Field(None, ge=0.0)
    tags: Optional[List[str]] = None
    difficulty_level: Optional[int] = Field(None, ge=1, le=10)
    player_impact: Optional[str] = Field(None, max_length=255)
    world_impact: Optional[str] = Field(None, max_length=255)

class ArcResponse(BaseModel):
    """Response model for arc"""
    
    id: UUID
    title: str
    description: Optional[str]
    arc_type: ArcType
    status: ArcStatus
    priority: ArcPriority
    region_id: Optional[str]
    character_id: Optional[str]
    npc_id: Optional[str]
    faction_ids: List[str]
    narrative_summary: Optional[str]
    objectives: List[str]
    themes: List[str]
    total_steps: int
    completed_steps: int
    progress_percentage: float
    estimated_duration_hours: Optional[float]
    actual_duration_hours: Optional[float]
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    last_activity: Optional[datetime]
    tags: List[str]
    difficulty_level: Optional[int]
    player_impact: Optional[str]
    world_impact: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    arc_metadata: Dict[str, Any]

    model_config = ConfigDict(from_attributes=True)

class ArcListResponse(BaseModel):
    """Response model for arc lists"""
    
    items: List[ArcResponse]
    total: int
    page: int
    size: int
    has_next: bool
    has_prev: bool 
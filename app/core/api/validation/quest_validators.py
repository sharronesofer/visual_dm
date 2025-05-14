"""Validation models for Quest-related API requests."""

from typing import Dict, List, Optional, Union
from pydantic import BaseModel, Field, validator
from enum import Enum
from datetime import datetime

from .base_validators import (
    PaginationValidationMixin,
    SortValidationMixin,
    FilterValidationMixin,
    DateRangeValidationMixin,
    validate_id,
    validate_name,
    validate_description,
    validate_tags,
    validate_metadata
)

class QuestType(str, Enum):
    """Valid quest type values."""
    MAIN = "main"
    SIDE = "side"
    FACTION = "faction"
    DAILY = "daily"
    EVENT = "event"
    HIDDEN = "hidden"

class QuestStatus(str, Enum):
    """Valid quest status values."""
    AVAILABLE = "available"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    HIDDEN = "hidden"

class QuestDifficulty(str, Enum):
    """Valid quest difficulty values."""
    TRIVIAL = "trivial"
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    VERY_HARD = "very_hard"
    EPIC = "epic"

class QuestObjectiveType(str, Enum):
    """Valid quest objective type values."""
    KILL = "kill"
    COLLECT = "collect"
    DELIVER = "deliver"
    ESCORT = "escort"
    EXPLORE = "explore"
    INTERACT = "interact"
    CRAFT = "craft"
    CUSTOM = "custom"

class QuestObjective(BaseModel):
    """Model for quest objectives."""
    
    type: QuestObjectiveType
    description: str = Field(..., min_length=1, max_length=500)
    target_id: Optional[str] = Field(None, min_length=1, max_length=100)
    quantity: Optional[int] = Field(None, ge=1)
    completed: bool = Field(default=False)
    optional: bool = Field(default=False)
    order: Optional[int] = Field(None, ge=0)
    metadata: Optional[Dict] = Field(default_factory=dict)
    
    @validator('target_id')
    def validate_target_id(cls, v):
        """Validate target ID if provided."""
        if v is not None:
            result = validate_id(v)
            if not result.is_valid:
                raise ValueError(f"Invalid target ID: {result.errors[0]['error']}")
        return v
    
    @validator('metadata')
    def validate_metadata_dict(cls, v):
        """Validate metadata if provided."""
        if v:
            result = validate_metadata(v)
            if not result.is_valid:
                raise ValueError(result.errors[0]['error'])
        return v

class QuestCreateRequest(BaseModel):
    """Validation model for quest creation requests."""
    
    name: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1, max_length=2000)
    type: QuestType
    status: QuestStatus = Field(default=QuestStatus.AVAILABLE)
    difficulty: QuestDifficulty
    giver_id: str = Field(..., min_length=1, max_length=100)
    location_id: Optional[str] = Field(None, min_length=1, max_length=100)
    faction_id: Optional[str] = Field(None, min_length=1, max_length=100)
    parent_quest_id: Optional[str] = Field(None, min_length=1, max_length=100)
    prerequisites: Optional[List[str]] = Field(default_factory=list)
    min_level: Optional[int] = Field(None, ge=1)
    objectives: List[QuestObjective]
    rewards: List[QuestReward]
    time_limit: Optional[int] = Field(None, ge=0)  # in seconds, 0 means no limit
    tags: Optional[List[str]] = Field(default_factory=list)
    metadata: Optional[Dict] = Field(default_factory=dict)
    
    @validator('giver_id', 'location_id', 'faction_id', 'parent_quest_id')
    def validate_entity_ids(cls, v, field):
        """Validate entity IDs if provided."""
        if v is not None:
            result = validate_id(v)
            if not result.is_valid:
                raise ValueError(f"Invalid {field.name}: {result.errors[0]['error']}")
        return v
    
    @validator('prerequisites')
    def validate_prerequisites(cls, v):
        """Validate prerequisite quest IDs if provided."""
        if v:
            for quest_id in v:
                result = validate_id(quest_id)
                if not result.is_valid:
                    raise ValueError(f"Invalid prerequisite quest ID: {result.errors[0]['error']}")
        return v
    
    @validator('objectives')
    def validate_objectives(cls, v):
        """Validate that at least one non-optional objective exists."""
        if not any(not obj.optional for obj in v):
            raise ValueError("Quest must have at least one non-optional objective")
        return v
    
    @validator('rewards')
    def validate_rewards(cls, v):
        """Validate that rewards list is not empty."""
        if not v:
            raise ValueError("Quest must have at least one reward")
        return v
    
    @validator('tags')
    def validate_tags_list(cls, v):
        """Validate tags if provided."""
        if v:
            result = validate_tags(v)
            if not result.is_valid:
                raise ValueError(result.errors[0]['error'])
        return v
    
    @validator('metadata')
    def validate_metadata_dict(cls, v):
        """Validate metadata if provided."""
        if v:
            result = validate_metadata(v)
            if not result.is_valid:
                raise ValueError(result.errors[0]['error'])
        return v

class QuestUpdateRequest(BaseModel):
    """Validation model for quest update requests."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=1, max_length=2000)
    type: Optional[QuestType] = None
    status: Optional[QuestStatus] = None
    difficulty: Optional[QuestDifficulty] = None
    giver_id: Optional[str] = None
    location_id: Optional[str] = None
    faction_id: Optional[str] = None
    parent_quest_id: Optional[str] = None
    prerequisites: Optional[List[str]] = None
    min_level: Optional[int] = Field(None, ge=1)
    objectives: Optional[List[QuestObjective]] = None
    rewards: Optional[List[QuestReward]] = None
    time_limit: Optional[int] = Field(None, ge=0)
    tags: Optional[List[str]] = None
    metadata: Optional[Dict] = None
    
    @validator('giver_id', 'location_id', 'faction_id', 'parent_quest_id')
    def validate_entity_ids(cls, v, field):
        """Validate entity IDs if provided."""
        if v is not None:
            result = validate_id(v)
            if not result.is_valid:
                raise ValueError(f"Invalid {field.name}: {result.errors[0]['error']}")
        return v
    
    @validator('prerequisites')
    def validate_prerequisites(cls, v):
        """Validate prerequisite quest IDs if provided."""
        if v is not None:
            for quest_id in v:
                result = validate_id(quest_id)
                if not result.is_valid:
                    raise ValueError(f"Invalid prerequisite quest ID: {result.errors[0]['error']}")
        return v
    
    @validator('objectives')
    def validate_objectives(cls, v):
        """Validate objectives if provided."""
        if v is not None and not any(not obj.optional for obj in v):
            raise ValueError("Quest must have at least one non-optional objective")
        return v
    
    @validator('rewards')
    def validate_rewards(cls, v):
        """Validate rewards if provided."""
        if v is not None and not v:
            raise ValueError("Quest must have at least one reward")
        return v
    
    @validator('tags')
    def validate_tags_list(cls, v):
        """Validate tags if provided."""
        if v is not None:
            result = validate_tags(v)
            if not result.is_valid:
                raise ValueError(result.errors[0]['error'])
        return v
    
    @validator('metadata')
    def validate_metadata_dict(cls, v):
        """Validate metadata if provided."""
        if v is not None:
            result = validate_metadata(v)
            if not result.is_valid:
                raise ValueError(result.errors[0]['error'])
        return v

class QuestQueryParams(BaseModel, PaginationValidationMixin, SortValidationMixin, FilterValidationMixin):
    """Validation model for quest query parameters."""
    
    page: int = Field(1, ge=1)
    per_page: int = Field(20, ge=1, le=100)
    sort_by: str = Field('name')
    order: str = Field('asc')
    filters: Optional[Dict] = None
    type: Optional[QuestType] = None
    status: Optional[QuestStatus] = None
    difficulty: Optional[QuestDifficulty] = None
    giver_id: Optional[str] = None
    location_id: Optional[str] = None
    faction_id: Optional[str] = None
    parent_quest_id: Optional[str] = None
    min_level: Optional[int] = Field(None, ge=1)
    has_time_limit: Optional[bool] = None
    tags: Optional[List[str]] = None
    
    valid_sort_fields = ['name', 'type', 'status', 'difficulty', 'min_level', 'time_limit', 'created_at', 'updated_at']
    valid_filters = {
        'type': QuestType,
        'status': QuestStatus,
        'difficulty': QuestDifficulty,
        'giver_id': str,
        'location_id': str,
        'faction_id': str,
        'parent_quest_id': str,
        'min_level': int,
        'has_time_limit': bool,
        'tags': list
    }
    
    @validator('tags')
    def validate_tags_list(cls, v):
        """Validate tags if provided."""
        if v is not None:
            result = validate_tags(v)
            if not result.is_valid:
                raise ValueError(result.errors[0]['error'])
        return v

class QuestObjectiveUpdateRequest(BaseModel):
    """Validation model for quest objective update requests."""
    
    objective_index: int = Field(..., ge=0)
    completed: bool
    metadata: Optional[Dict] = None
    
    @validator('metadata')
    def validate_metadata_dict(cls, v):
        """Validate metadata if provided."""
        if v is not None:
            result = validate_metadata(v)
            if not result.is_valid:
                raise ValueError(result.errors[0]['error'])
        return v 
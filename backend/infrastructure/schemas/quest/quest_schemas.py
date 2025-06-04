"""
Quest System Schemas
Data validation schemas for quest operations
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict, validator


class QuestStepSchema(BaseModel):
    """Schema for quest steps"""
    id: int = Field(..., description="Step identifier")
    description: str = Field(..., min_length=1, max_length=500, description="Step description")
    type: str = Field(..., description="Step type (kill, explore, dialogue, collect, etc.)")
    completed: bool = Field(default=False, description="Whether step is completed")
    target_location_id: Optional[str] = Field(None, description="Target location for step")
    target_npc_id: Optional[str] = Field(None, description="Target NPC for step")
    data: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional step data")

    model_config = ConfigDict(from_attributes=True)


class QuestRewardSchema(BaseModel):
    """Schema for quest rewards"""
    gold: int = Field(ge=0, description="Gold reward amount")
    experience: int = Field(ge=0, description="Experience reward amount")
    reputation: Optional[Dict[str, Any]] = Field(None, description="Reputation rewards")
    items: Optional[List[str]] = Field(default_factory=list, description="Item rewards")

    model_config = ConfigDict(from_attributes=True)


class CreateQuestSchema(BaseModel):
    """Schema for creating quests"""
    title: str = Field(..., min_length=1, max_length=255, description="Quest title")
    description: str = Field(..., min_length=1, max_length=2000, description="Quest description")
    difficulty: str = Field(..., description="Quest difficulty (easy, medium, hard, epic)")
    theme: str = Field(..., description="Quest theme (combat, exploration, social, mystery)")
    npc_id: Optional[str] = Field(None, description="Associated NPC ID")
    location_id: Optional[str] = Field(None, description="Quest location ID")
    level: int = Field(ge=1, le=100, default=1, description="Required player level")
    steps: List[QuestStepSchema] = Field(..., min_items=1, description="Quest steps")
    rewards: QuestRewardSchema = Field(..., description="Quest rewards")
    is_main_quest: bool = Field(default=False, description="Whether this is a main story quest")
    tags: List[str] = Field(default_factory=list, description="Quest tags")

    @validator('difficulty')
    def validate_difficulty(cls, v):
        allowed = ['easy', 'medium', 'hard', 'epic']
        if v not in allowed:
            raise ValueError(f'Difficulty must be one of: {allowed}')
        return v

    @validator('theme')
    def validate_theme(cls, v):
        allowed = ['combat', 'exploration', 'social', 'mystery', 'crafting', 'trade', 'aid', 'knowledge', 'general']
        if v not in allowed:
            raise ValueError(f'Theme must be one of: {allowed}')
        return v

    model_config = ConfigDict(from_attributes=True)


class UpdateQuestSchema(BaseModel):
    """Schema for updating quests"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, min_length=1, max_length=2000)
    status: Optional[str] = Field(None)
    difficulty: Optional[str] = Field(None)
    steps: Optional[List[QuestStepSchema]] = Field(None)
    rewards: Optional[QuestRewardSchema] = Field(None)

    @validator('difficulty')
    def validate_difficulty(cls, v):
        if v is not None:
            allowed = ['easy', 'medium', 'hard', 'epic']
            if v not in allowed:
                raise ValueError(f'Difficulty must be one of: {allowed}')
        return v

    @validator('status')
    def validate_status(cls, v):
        if v is not None:
            allowed = ['pending', 'active', 'completed', 'failed', 'abandoned', 'expired']
            if v not in allowed:
                raise ValueError(f'Status must be one of: {allowed}')
        return v

    model_config = ConfigDict(from_attributes=True)


class QuestResponseSchema(BaseModel):
    """Schema for quest responses"""
    id: UUID = Field(..., description="Quest ID")
    title: str = Field(..., description="Quest title")
    description: str = Field(..., description="Quest description")
    status: str = Field(..., description="Quest status")
    difficulty: str = Field(..., description="Quest difficulty")
    theme: Optional[str] = Field(None, description="Quest theme")
    npc_id: Optional[str] = Field(None, description="Associated NPC ID")
    npc_name: Optional[str] = Field(None, description="Associated NPC name")
    player_id: Optional[str] = Field(None, description="Assigned player ID")
    location_id: Optional[str] = Field(None, description="Quest location ID")
    level: int = Field(..., description="Required player level")
    steps: List[QuestStepSchema] = Field(..., description="Quest steps")
    rewards: QuestRewardSchema = Field(..., description="Quest rewards")
    is_main_quest: bool = Field(..., description="Whether this is a main story quest")
    tags: List[str] = Field(..., description="Quest tags")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

    model_config = ConfigDict(from_attributes=True)


class QuestListResponseSchema(BaseModel):
    """Schema for paginated quest lists"""
    items: List[QuestResponseSchema] = Field(..., description="Quest items")
    total: int = Field(..., ge=0, description="Total number of quests")
    page: int = Field(..., ge=1, description="Current page number")
    size: int = Field(..., ge=1, description="Page size")
    has_next: bool = Field(..., description="Whether there are more pages")
    has_prev: bool = Field(..., description="Whether there are previous pages")

    model_config = ConfigDict(from_attributes=True)


class QuestActionSchema(BaseModel):
    """Schema for quest actions (accept, abandon, complete, etc.)"""
    quest_id: UUID = Field(..., description="Quest ID")
    player_id: str = Field(..., description="Player ID")
    action: str = Field(..., description="Action to perform")
    reason: Optional[str] = Field(None, description="Reason for action (e.g., failure reason)")

    @validator('action')
    def validate_action(cls, v):
        allowed = ['accept', 'abandon', 'complete', 'fail', 'update_step']
        if v not in allowed:
            raise ValueError(f'Action must be one of: {allowed}')
        return v

    model_config = ConfigDict(from_attributes=True)


class QuestStepUpdateSchema(BaseModel):
    """Schema for updating quest steps"""
    quest_id: UUID = Field(..., description="Quest ID")
    step_id: int = Field(..., ge=1, description="Step ID")
    completed: bool = Field(..., description="Whether step is completed")
    player_id: str = Field(..., description="Player ID")

    model_config = ConfigDict(from_attributes=True) 
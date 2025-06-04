"""
Dialogue System Models

This module defines the data models for the dialogue system according to the
Development Bible standards and WebSocket-first architecture.
"""

from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, validator
from sqlalchemy import Column, String, DateTime, JSON, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID as PostgreSQL_UUID

from backend.systems.shared.models import BaseEntity
from backend.infrastructure.utils import generate_uuid


class DialogueEntity(BaseEntity):
    """Database entity for dialogue conversations"""
    
    __tablename__ = "dialogue_conversations"
    
    # Conversation identification
    conversation_id = Column(String(36), unique=True, nullable=False)
    npc_id = Column(String(36), nullable=False)
    player_id = Column(String(36), nullable=False)
    
    # Conversation details
    interaction_type = Column(String(50), nullable=False, default='casual')
    status = Column(String(20), nullable=False, default='active')
    
    # Context and metadata
    context = Column(JSON, nullable=True, default=dict)
    properties = Column(JSON, nullable=True, default=dict)
    
    # Timestamps
    started_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)
    last_activity = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    def __init__(self, **kwargs):
        """Initialize dialogue entity with proper defaults"""
        if 'conversation_id' not in kwargs:
            kwargs['conversation_id'] = str(uuid4())
        if 'id' not in kwargs:
            kwargs['id'] = kwargs['conversation_id']
        super().__init__(**kwargs)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert entity to dictionary representation"""
        return {
            'id': str(self.id),
            'conversation_id': self.conversation_id,
            'npc_id': self.npc_id,
            'player_id': self.player_id,
            'interaction_type': self.interaction_type,
            'status': self.status,
            'context': self.context or {},
            'properties': self.properties or {},
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'ended_at': self.ended_at.isoformat() if self.ended_at else None,
            'last_activity': self.last_activity.isoformat() if self.last_activity else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class CreateDialogueRequest(BaseModel):
    """Request model for creating new dialogue conversations"""
    
    npc_id: str = Field(..., description="Unique identifier for the NPC")
    player_id: str = Field(..., description="Unique identifier for the player")
    conversation_id: Optional[str] = Field(None, description="Optional conversation ID")
    interaction_type: str = Field('casual', description="Type of interaction")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Conversation context")
    properties: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional properties")
    
    @validator('npc_id', 'player_id')
    def validate_uuid_fields(cls, v):
        """Validate UUID format for ID fields"""
        try:
            UUID(v)
            return v
        except ValueError:
            raise ValueError(f"Invalid UUID format: {v}")
    
    @validator('conversation_id')
    def validate_conversation_id(cls, v):
        """Validate conversation ID format if provided"""
        if v is not None:
            try:
                UUID(v)
                return v
            except ValueError:
                raise ValueError(f"Invalid UUID format for conversation_id: {v}")
        return v
    
    @validator('interaction_type')
    def validate_interaction_type(cls, v):
        """Validate interaction type against allowed values"""
        allowed_types = ['casual', 'quest', 'trading', 'combat', 'social']
        if v not in allowed_types:
            raise ValueError(f"Invalid interaction type: {v}. Must be one of: {', '.join(allowed_types)}")
        return v


class UpdateDialogueRequest(BaseModel):
    """Request model for updating existing dialogue conversations"""
    
    status: Optional[str] = Field(None, description="Conversation status")
    context: Optional[Dict[str, Any]] = Field(None, description="Updated conversation context")
    properties: Optional[Dict[str, Any]] = Field(None, description="Updated properties")
    
    @validator('status')
    def validate_status(cls, v):
        """Validate status values"""
        if v is not None:
            allowed_statuses = ['active', 'paused', 'ended', 'interrupted']
            if v not in allowed_statuses:
                raise ValueError(f"Invalid status: {v}. Must be one of: {', '.join(allowed_statuses)}")
        return v


class DialogueMessageRequest(BaseModel):
    """Request model for dialogue messages"""
    
    conversation_id: str = Field(..., description="Conversation identifier")
    content: str = Field(..., description="Message content")
    speaker: str = Field('npc', description="Who is speaking")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Message metadata")
    
    @validator('conversation_id')
    def validate_conversation_id(cls, v):
        """Validate conversation ID format"""
        try:
            UUID(v)
            return v
        except ValueError:
            raise ValueError(f"Invalid UUID format for conversation_id: {v}")
    
    @validator('speaker')
    def validate_speaker(cls, v):
        """Validate speaker type"""
        allowed_speakers = ['npc', 'player', 'system']
        if v not in allowed_speakers:
            raise ValueError(f"Invalid speaker: {v}. Must be one of: {', '.join(allowed_speakers)}")
        return v
    
    @validator('content')
    def validate_content(cls, v):
        """Validate message content"""
        if not v or not v.strip():
            raise ValueError("Message content cannot be empty")
        if len(v) > 10000:
            raise ValueError("Message content exceeds maximum length of 10000 characters")
        return v.strip()


class NPCInteractionRequest(BaseModel):
    """Request model for NPC interaction validation"""
    
    npc_id: str = Field(..., description="NPC identifier")
    npc_name: Optional[str] = Field(None, description="NPC name")
    npc_type: str = Field('peasant', description="NPC type/class")
    personality: Optional[Dict[str, Union[int, float]]] = Field(default_factory=dict, description="Personality traits")
    relationship_standing: float = Field(0.5, description="Relationship level with player")
    
    @validator('npc_id')
    def validate_npc_id(cls, v):
        """Validate NPC ID format"""
        try:
            UUID(v)
            return v
        except ValueError:
            raise ValueError(f"Invalid UUID format for npc_id: {v}")
    
    @validator('npc_type')
    def validate_npc_type(cls, v):
        """Validate NPC type"""
        allowed_types = ['peasant', 'merchant', 'noble', 'guard', 'artisan', 'scholar']
        if v not in allowed_types:
            raise ValueError(f"Invalid NPC type: {v}. Must be one of: {', '.join(allowed_types)}")
        return v
    
    @validator('relationship_standing')
    def validate_relationship(cls, v):
        """Validate relationship standing"""
        if not (0 <= v <= 1):
            raise ValueError("Relationship standing must be between 0 and 1")
        return v
    
    @validator('personality')
    def validate_personality(cls, v):
        """Validate personality traits"""
        if v:
            for trait, value in v.items():
                if not isinstance(value, (int, float)):
                    raise ValueError(f"Personality trait '{trait}' must be a number")
                if not (0 <= value <= 10):
                    raise ValueError(f"Personality trait '{trait}' must be between 0 and 10")
        return v


class BarteringItemModel(BaseModel):
    """Model for individual bartering items"""
    
    item_id: str = Field(..., description="Unique item identifier")
    name: str = Field(..., description="Item name")
    base_price: float = Field(..., description="Base item price")
    adjusted_price: float = Field(..., description="Price adjusted for NPC and relationship")
    availability_tier: str = Field(..., description="Item availability level")
    price_modifiers: Optional[Dict[str, Union[int, float]]] = Field(default_factory=dict, description="Price adjustment factors")
    
    @validator('item_id')
    def validate_item_id(cls, v):
        """Validate item ID format"""
        try:
            UUID(v)
            return v
        except ValueError:
            raise ValueError(f"Invalid UUID format for item_id: {v}")
    
    @validator('base_price', 'adjusted_price')
    def validate_prices(cls, v):
        """Validate price values"""
        if v < 0:
            raise ValueError("Prices must be non-negative")
        return v
    
    @validator('availability_tier')
    def validate_availability_tier(cls, v):
        """Validate availability tier"""
        allowed_tiers = ['always_available', 'relationship_gated', 'never_available']
        if v not in allowed_tiers:
            raise ValueError(f"Invalid availability tier: {v}. Must be one of: {', '.join(allowed_tiers)}")
        return v


class BarteringRequest(BaseModel):
    """Request model for bartering interactions"""
    
    conversation_id: str = Field(..., description="Conversation identifier")
    npc_id: str = Field(..., description="NPC identifier")
    player_id: str = Field(..., description="Player identifier")
    available_items: List[BarteringItemModel] = Field(..., description="Items available for trade")
    npc_type: str = Field(..., description="NPC type for pricing calculations")
    relationship_standing: float = Field(0.5, description="Current relationship level")
    
    @validator('conversation_id', 'npc_id', 'player_id')
    def validate_uuid_fields(cls, v):
        """Validate UUID format for ID fields"""
        try:
            UUID(v)
            return v
        except ValueError:
            raise ValueError(f"Invalid UUID format: {v}")
    
    @validator('npc_type')
    def validate_npc_type(cls, v):
        """Validate NPC type"""
        allowed_types = ['peasant', 'merchant', 'noble', 'guard', 'artisan', 'scholar']
        if v not in allowed_types:
            raise ValueError(f"Invalid NPC type: {v}. Must be one of: {', '.join(allowed_types)}")
        return v
    
    @validator('relationship_standing')
    def validate_relationship(cls, v):
        """Validate relationship standing"""
        if not (0 <= v <= 1):
            raise ValueError("Relationship standing must be between 0 and 1")
        return v


class WebSocketMessage(BaseModel):
    """Model for WebSocket message format"""
    
    type: str = Field(..., description="Message type")
    payload: Dict[str, Any] = Field(..., description="Message payload")
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat(), description="Message timestamp")
    
    @validator('type')
    def validate_message_type(cls, v):
        """Validate message type"""
        allowed_types = [
            'dialogue_latency_connection_status',
            'dialogue_general_connection_status',
            'dialogue_conversation_connection_status',
            'dialogue_placeholder_message',
            'dialogue_response_ready',
            'dialogue_conversation_start',
            'dialogue_conversation_end',
            'dialogue_context_update',
            'dialogue_npc_interaction',
            'dialogue_bartering_start',
            'dialogue_bartering_update',
            'dialogue_error'
        ]
        if v not in allowed_types:
            raise ValueError(f"Invalid message type: {v}. Must be one of: {', '.join(allowed_types)}")
        return v
    
    @validator('timestamp')
    def validate_timestamp(cls, v):
        """Validate timestamp format"""
        try:
            datetime.fromisoformat(v.replace('Z', '+00:00'))
            return v
        except ValueError:
            raise ValueError(f"Invalid timestamp format: {v}")


class DialogueResponse(BaseModel):
    """Standard response model for dialogue operations"""
    
    success: bool = Field(..., description="Operation success status")
    data: Optional[Dict[str, Any]] = Field(None, description="Response data")
    error: Optional[str] = Field(None, description="Error message if operation failed")
    message: str = Field(..., description="Human-readable response message")
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat(), description="Response timestamp")
    
    @classmethod
    def from_orm(cls, entity: DialogueEntity, message: str = "Operation completed successfully"):
        """Create response from database entity"""
        return cls(
            success=True,
            data={'conversation': entity.to_dict()},
            message=message
        )
    
    @classmethod
    def success_response(cls, data: Any = None, message: str = "Operation completed successfully"):
        """Create success response"""
        return cls(
            success=True,
            data=data,
            message=message
        )
    
    @classmethod
    def error_response(cls, error: str, message: str = "Operation failed"):
        """Create error response"""
        return cls(
            success=False,
            error=error,
            message=message
        )


class ConversationSummary(BaseModel):
    """Summary model for conversation data"""
    
    conversation_id: str
    npc_id: str
    player_id: str
    interaction_type: str
    status: str
    started_at: str
    last_activity: str
    message_count: int
    
    @validator('conversation_id', 'npc_id', 'player_id')
    def validate_uuid_fields(cls, v):
        """Validate UUID format for ID fields"""
        try:
            UUID(v)
            return v
        except ValueError:
            raise ValueError(f"Invalid UUID format: {v}")


class ActiveConversationsResponse(BaseModel):
    """Response model for active conversations list"""
    
    conversations: List[ConversationSummary]
    total_active: int
    filter_applied: bool = False
    
    @validator('total_active')
    def validate_total_count(cls, v):
        """Validate total count is non-negative"""
        if v < 0:
            raise ValueError("Total active conversations cannot be negative")
        return v


# Configuration models for dialogue system settings

class DialogueSystemConfig(BaseModel):
    """Configuration model for dialogue system settings"""
    
    max_message_length: int = Field(10000, description="Maximum message content length")
    max_conversation_duration: int = Field(3600, description="Maximum conversation duration in seconds")
    min_response_time: float = Field(0.1, description="Minimum response time in seconds")
    max_response_time: float = Field(300, description="Maximum response time before timeout")
    enable_bartering: bool = Field(True, description="Enable universal bartering system")
    enable_ai_responses: bool = Field(True, description="Enable AI-powered responses")
    cache_conversations: bool = Field(True, description="Cache conversation history")
    
    @validator('max_message_length', 'max_conversation_duration')
    def validate_positive_integers(cls, v):
        """Validate positive integer values"""
        if v <= 0:
            raise ValueError("Value must be positive")
        return v
    
    @validator('min_response_time', 'max_response_time')
    def validate_positive_floats(cls, v):
        """Validate positive float values"""
        if v <= 0:
            raise ValueError("Value must be positive")
        return v


# Factory functions for model creation

def create_dialogue_entity(**kwargs) -> DialogueEntity:
    """Factory function to create dialogue entity"""
    return DialogueEntity(**kwargs)


def create_websocket_message(message_type: str, payload: Dict[str, Any]) -> WebSocketMessage:
    """Factory function to create WebSocket message"""
    return WebSocketMessage(
        type=message_type,
        payload=payload,
        timestamp=datetime.utcnow().isoformat()
    )

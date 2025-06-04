"""
Dialogue System Extended Models - Models for dialogue latency and conversation management.

This module provides extended data models for dialogue system functionality,
specifically focusing on conversation management, latency tracking, and
real-time communication models.
"""

from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from uuid import UUID, uuid4
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict

from backend.infrastructure.shared.models import SharedBaseModel

class DialogueStatus(str, Enum):
    """Status values for dialogue conversations."""
    WAITING = "waiting"
    PROCESSING = "processing"
    COMPLETED = "completed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"

class DialogueMessageType(str, Enum):
    """Types of dialogue messages."""
    PLAYER = "player"
    NPC = "npc"
    SYSTEM = "system"
    ACTION = "action"
    EMOTE = "emote"
    PLACEHOLDER = "placeholder"

class DialogueContext(str, Enum):
    """Context categories for dialogue situations."""
    BARTERING = "bartering"
    QUEST_RELATED = "quest_related"
    FACTION_RELATED = "faction_related"
    GENERAL = "general"
    LORE = "lore"
    SOCIAL = "social"
    COMBAT = "combat"

class ConversationParticipant(BaseModel):
    """Model for conversation participant information."""
    
    participant_id: str = Field(..., description="Unique identifier for the participant")
    participant_type: str = Field(..., description="Type of participant (player, npc, system)")
    name: Optional[str] = Field(None, description="Display name of the participant")
    role: Optional[str] = Field(None, description="Role in the conversation")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional participant metadata")

    model_config = ConfigDict(from_attributes=True)

class DialogueMessage(BaseModel):
    """Model for individual dialogue messages."""
    
    message_id: str = Field(default_factory=lambda: str(uuid4()), description="Unique message identifier")
    conversation_id: str = Field(..., description="Conversation this message belongs to")
    sender_id: str = Field(..., description="ID of the message sender")
    content: str = Field(..., description="Message content")
    message_type: DialogueMessageType = Field(default=DialogueMessageType.PLAYER, description="Type of message")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When the message was sent")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional message metadata")
    
    # Latency-specific fields
    is_placeholder: bool = Field(default=False, description="Whether this is a placeholder message")
    placeholder_category: Optional[str] = Field(None, description="Category of placeholder if applicable")
    replaced_by: Optional[str] = Field(None, description="ID of message that replaced this placeholder")

    model_config = ConfigDict(from_attributes=True)

class ConversationMetadata(BaseModel):
    """Model for conversation metadata and context."""
    
    location_id: Optional[str] = Field(None, description="Location where conversation takes place")
    dialogue_context: DialogueContext = Field(default=DialogueContext.GENERAL, description="Context of the dialogue")
    npc_type: Optional[str] = Field(None, description="Type of NPC for placeholder formatting")
    faction_member: Optional[str] = Field(None, description="Faction member type for faction-related dialogues")
    quest_context: Optional[Dict[str, Any]] = Field(None, description="Quest-related context information")
    relationship_context: Optional[Dict[str, Any]] = Field(None, description="Relationship context between participants")
    
    # Additional context for AI generation
    personality_traits: List[str] = Field(default_factory=list, description="NPC personality traits")
    current_mood: Optional[str] = Field(None, description="Current mood of the NPC")
    memory_context: List[Dict[str, Any]] = Field(default_factory=list, description="Relevant memories for context")
    rumor_context: List[Dict[str, Any]] = Field(default_factory=list, description="Relevant rumors for context")

    model_config = ConfigDict(from_attributes=True)

class ConversationState(BaseModel):
    """Model for current conversation state."""
    
    conversation_id: str = Field(..., description="Unique conversation identifier")
    status: DialogueStatus = Field(default=DialogueStatus.WAITING, description="Current conversation status")
    participants: List[ConversationParticipant] = Field(..., description="Conversation participants")
    messages: List[DialogueMessage] = Field(default_factory=list, description="Messages in the conversation")
    metadata: ConversationMetadata = Field(..., description="Conversation metadata and context")
    
    # Timing information
    started_at: datetime = Field(default_factory=datetime.utcnow, description="When the conversation started")
    last_activity: datetime = Field(default_factory=datetime.utcnow, description="Last activity timestamp")
    ended_at: Optional[datetime] = Field(None, description="When the conversation ended")
    
    # AI processing information
    current_ai_request_id: Optional[str] = Field(None, description="ID of current AI request")
    ai_processing_start: Optional[datetime] = Field(None, description="When AI processing started")
    total_ai_latency: Optional[float] = Field(None, description="Total AI processing latency")

    model_config = ConfigDict(from_attributes=True)

class DialogueResponse(BaseModel):
    """Model for AI-generated dialogue responses."""
    
    response_id: str = Field(default_factory=lambda: str(uuid4()), description="Unique response identifier")
    conversation_id: str = Field(..., description="Conversation this response belongs to")
    request_id: Optional[str] = Field(None, description="AI request ID that generated this response")
    npc_id: str = Field(..., description="NPC that generated the response")
    
    # Response content
    content: str = Field(..., description="The actual dialogue response")
    emotion: Optional[str] = Field(None, description="Emotional tone of the response")
    actions: List[str] = Field(default_factory=list, description="Associated NPC actions")
    
    # Timing information
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="When the response was generated")
    processing_time: Optional[float] = Field(None, description="Time taken to generate the response")
    
    # Quality and context
    confidence_score: Optional[float] = Field(None, description="AI confidence in the response")
    context_used: Dict[str, Any] = Field(default_factory=dict, description="Context information used")
    
    # Integration data
    memory_updates: List[Dict[str, Any]] = Field(default_factory=list, description="Memory updates to apply")
    rumor_updates: List[Dict[str, Any]] = Field(default_factory=list, description="Rumor updates to apply")
    relationship_changes: Dict[str, Any] = Field(default_factory=dict, description="Relationship changes")

    model_config = ConfigDict(from_attributes=True)

class PlaceholderMessage(BaseModel):
    """Model for placeholder messages during AI processing."""
    
    placeholder_id: str = Field(default_factory=lambda: str(uuid4()), description="Unique placeholder identifier")
    conversation_id: str = Field(..., description="Conversation this placeholder belongs to")
    category: str = Field(..., description="Category of placeholder message")
    content: str = Field(..., description="Placeholder message content")
    context: DialogueContext = Field(..., description="Dialogue context for the placeholder")
    
    # Timing information
    displayed_at: datetime = Field(default_factory=datetime.utcnow, description="When placeholder was displayed")
    elapsed_time: float = Field(..., description="Elapsed time when placeholder was shown")
    
    # State tracking
    is_replaced: bool = Field(default=False, description="Whether this placeholder has been replaced")
    replaced_by_response_id: Optional[str] = Field(None, description="ID of response that replaced this")

    model_config = ConfigDict(from_attributes=True)

# Request/Response models for API endpoints
class StartConversationRequest(BaseModel):
    """Request model for starting a new conversation."""
    
    npc_id: str = Field(..., description="NPC to start conversation with")
    player_id: str = Field(..., description="Player starting the conversation")
    location_id: Optional[str] = Field(None, description="Location where conversation starts")
    context: DialogueContext = Field(default=DialogueContext.GENERAL, description="Initial dialogue context")
    initial_message: Optional[str] = Field(None, description="Optional initial message from player")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional conversation metadata")

    model_config = ConfigDict(from_attributes=True)

class SendMessageRequest(BaseModel):
    """Request model for sending a message in conversation."""
    
    conversation_id: str = Field(..., description="Conversation to send message to")
    sender_id: str = Field(..., description="ID of the message sender")
    content: str = Field(..., max_length=2000, description="Message content")
    message_type: DialogueMessageType = Field(default=DialogueMessageType.PLAYER, description="Type of message")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional message metadata")

    model_config = ConfigDict(from_attributes=True)

class ConversationResponse(BaseModel):
    """Response model for conversation data."""
    
    conversation_id: str
    status: DialogueStatus
    participants: List[ConversationParticipant]
    recent_messages: List[DialogueMessage]
    metadata: ConversationMetadata
    started_at: datetime
    last_activity: datetime
    ended_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)

class LatencyStatusResponse(BaseModel):
    """Response model for latency status updates."""
    
    conversation_id: str
    status: DialogueStatus
    current_placeholder: Optional[PlaceholderMessage]
    elapsed_time: float
    estimated_completion: Optional[float]
    ai_processing: bool

    model_config = ConfigDict(from_attributes=True)

class DialogueAnalytics(BaseModel):
    """Model for dialogue analytics and metrics."""
    
    conversation_id: str
    total_duration: float
    message_count: int
    ai_requests: int
    average_response_time: float
    placeholder_count: int
    timeout_occurrences: int
    participant_satisfaction: Optional[float]
    context_transitions: List[str]

    model_config = ConfigDict(from_attributes=True) 
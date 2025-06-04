"""
Dialogue System Schemas - API schemas for dialogue system endpoints.

This module provides Pydantic schemas for API request/response validation
and serialization for the dialogue system, including latency management
and real-time communication schemas.
"""

import logging
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, validator
from enum import Enum
from uuid import UUID

# Import models for consistency
from backend.infrastructure.dialogue_models.dialogue_models import (
    DialogueStatus,
    DialogueMessageType,
    DialogueContext,
    ConversationParticipant,
    DialogueMessage,
    PlaceholderMessage,
    DialogueResponse,
    ConversationState,
    MessageType,
    InteractionType
)

logger = logging.getLogger(__name__)

# Request Schemas
class CreateConversationSchema(BaseModel):
    """Schema for creating a new conversation."""
    
    npc_id: str = Field(..., min_length=1, description="NPC identifier")
    player_id: str = Field(..., min_length=1, description="Player identifier")
    location_id: Optional[str] = Field(None, description="Location identifier")
    context: DialogueContext = Field(default=DialogueContext.GENERAL, description="Initial dialogue context")
    initial_message: Optional[str] = Field(None, max_length=2000, description="Optional initial player message")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "npc_id": "merchant_001",
                "player_id": "player_123",
                "location_id": "tavern_main",
                "context": "bartering",
                "initial_message": "Hello, what wares do you have?",
                "metadata": {"npc_type": "merchant", "player_level": 5}
            }
        }
    )

class SendMessageSchema(BaseModel):
    """Schema for sending a message in a conversation."""
    
    conversation_id: str = Field(..., min_length=1, description="Conversation identifier")
    sender_id: str = Field(..., min_length=1, description="Message sender identifier")
    content: str = Field(..., min_length=1, max_length=2000, description="Message content")
    message_type: DialogueMessageType = Field(default=DialogueMessageType.PLAYER, description="Type of message")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional message metadata")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "conversation_id": "conv_123",
                "sender_id": "player_123",
                "content": "I'm interested in buying a sword.",
                "message_type": "player",
                "metadata": {"urgency": "normal"}
            }
        }
    )

class UpdateContextSchema(BaseModel):
    """Schema for updating conversation context."""
    
    conversation_id: str = Field(..., min_length=1, description="Conversation identifier")
    new_context: DialogueContext = Field(..., description="New dialogue context")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional context metadata")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "conversation_id": "conv_123",
                "new_context": "quest_related",
                "metadata": {"quest_id": "quest_001", "quest_stage": "investigation"}
            }
        }
    )

# Response Schemas
class ConversationSchema(BaseModel):
    """Schema for conversation data."""
    
    conversation_id: str = Field(..., description="Unique conversation identifier")
    status: DialogueStatus = Field(..., description="Current conversation status")
    participants: List[ConversationParticipant] = Field(..., description="Conversation participants")
    recent_messages: List[DialogueMessage] = Field(..., description="Recent messages in conversation")
    context: DialogueContext = Field(..., description="Current dialogue context")
    started_at: datetime = Field(..., description="When conversation started")
    last_activity: datetime = Field(..., description="Last activity timestamp")
    ended_at: Optional[datetime] = Field(None, description="When conversation ended")
    
    # Latency information
    current_ai_request_id: Optional[str] = Field(None, description="Current AI request ID")
    ai_processing: bool = Field(default=False, description="Whether AI is currently processing")
    ai_processing_start: Optional[datetime] = Field(None, description="When AI processing started")

    model_config = ConfigDict(from_attributes=True)

class MessageSchema(BaseModel):
    """Schema for dialogue messages."""
    
    message_id: str = Field(..., description="Unique message identifier")
    conversation_id: str = Field(..., description="Conversation identifier")
    sender_id: str = Field(..., description="Message sender identifier")
    content: str = Field(..., description="Message content")
    message_type: DialogueMessageType = Field(..., description="Type of message")
    timestamp: datetime = Field(..., description="Message timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Message metadata")
    
    # Placeholder information
    is_placeholder: bool = Field(default=False, description="Whether this is a placeholder")
    placeholder_category: Optional[str] = Field(None, description="Placeholder category")
    replaced_by: Optional[str] = Field(None, description="ID of replacement message")

    model_config = ConfigDict(from_attributes=True)

class PlaceholderSchema(BaseModel):
    """Schema for placeholder messages."""
    
    placeholder_id: str = Field(..., description="Unique placeholder identifier")
    conversation_id: str = Field(..., description="Conversation identifier")
    category: str = Field(..., description="Placeholder category")
    content: str = Field(..., description="Placeholder content")
    context: DialogueContext = Field(..., description="Dialogue context")
    displayed_at: datetime = Field(..., description="When placeholder was displayed")
    elapsed_time: float = Field(..., ge=0, description="Elapsed time when shown")
    is_replaced: bool = Field(default=False, description="Whether replaced")
    replaced_by_response_id: Optional[str] = Field(None, description="Replacement response ID")

    model_config = ConfigDict(from_attributes=True)

class LatencyResponseSchema(BaseModel):
    """Schema for latency management responses."""
    
    conversation_id: str = Field(..., description="Conversation identifier")
    status: DialogueStatus = Field(..., description="Current conversation status")
    current_placeholder: Optional[PlaceholderSchema] = Field(None, description="Current placeholder message")
    elapsed_time: float = Field(..., ge=0, description="Total elapsed time")
    estimated_completion: Optional[float] = Field(None, ge=0, description="Estimated completion time")
    ai_processing: bool = Field(..., description="Whether AI is processing")
    
    # Statistics
    placeholder_count: int = Field(default=0, ge=0, description="Number of placeholders shown")
    last_update: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")

    model_config = ConfigDict(from_attributes=True)

class AIResponseSchema(BaseModel):
    """Schema for AI-generated responses."""
    
    response_id: str = Field(..., description="Unique response identifier")
    conversation_id: str = Field(..., description="Conversation identifier")
    request_id: Optional[str] = Field(None, description="AI request identifier")
    npc_id: str = Field(..., description="NPC identifier")
    content: str = Field(..., description="Response content")
    emotion: Optional[str] = Field(None, description="Emotional tone")
    actions: List[str] = Field(default_factory=list, description="Associated actions")
    generated_at: datetime = Field(..., description="Generation timestamp")
    processing_time: Optional[float] = Field(None, ge=0, description="Processing time in seconds")
    confidence_score: Optional[float] = Field(None, ge=0, le=1, description="AI confidence score")

    model_config = ConfigDict(from_attributes=True)

# WebSocket Schemas
class WebSocketMessageSchema(BaseModel):
    """Schema for WebSocket messages."""
    
    type: str = Field(..., description="Message type")
    conversation_id: Optional[str] = Field(None, description="Conversation identifier")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Message timestamp")
    data: Dict[str, Any] = Field(..., description="Message data")

    model_config = ConfigDict(from_attributes=True)

class LatencyUpdateSchema(BaseModel):
    """Schema for real-time latency updates via WebSocket."""
    
    type: str = Field(default="dialogue_latency_update", description="Message type")
    conversation_id: str = Field(..., description="Conversation identifier")
    npc_id: str = Field(..., description="NPC identifier")
    message: str = Field(..., description="Placeholder message")
    category: str = Field(..., description="Placeholder category")
    context: str = Field(..., description="Dialogue context")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Update timestamp")
    elapsed_time: float = Field(..., ge=0, description="Elapsed time")

    model_config = ConfigDict(from_attributes=True)

class FinalResponseSchema(BaseModel):
    """Schema for final dialogue response via WebSocket."""
    
    type: str = Field(default="dialogue_final_response", description="Message type")
    conversation_id: str = Field(..., description="Conversation identifier")
    npc_id: str = Field(..., description="NPC identifier")
    response: str = Field(..., description="Final dialogue response")
    total_latency: Optional[float] = Field(None, ge=0, description="Total processing latency")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")

    model_config = ConfigDict(from_attributes=True)

# Analytics Schemas
class ConversationAnalyticsSchema(BaseModel):
    """Schema for conversation analytics."""
    
    conversation_id: str = Field(..., description="Conversation identifier")
    total_duration: float = Field(..., ge=0, description="Total conversation duration")
    message_count: int = Field(..., ge=0, description="Total message count")
    ai_requests: int = Field(..., ge=0, description="Number of AI requests")
    average_response_time: float = Field(..., ge=0, description="Average AI response time")
    placeholder_count: int = Field(..., ge=0, description="Total placeholder count")
    timeout_occurrences: int = Field(..., ge=0, description="Number of timeouts")
    participant_satisfaction: Optional[float] = Field(None, ge=0, le=10, description="Satisfaction rating")
    context_transitions: List[str] = Field(default_factory=list, description="Context change history")

    model_config = ConfigDict(from_attributes=True)

class LatencyMetricsSchema(BaseModel):
    """Schema for latency performance metrics."""
    
    time_period: str = Field(..., description="Time period for metrics")
    total_conversations: int = Field(..., ge=0, description="Total conversations")
    average_latency: float = Field(..., ge=0, description="Average AI response latency")
    median_latency: float = Field(..., ge=0, description="Median AI response latency")
    p95_latency: float = Field(..., ge=0, description="95th percentile latency")
    timeout_rate: float = Field(..., ge=0, le=1, description="Timeout rate (0-1)")
    placeholder_effectiveness: float = Field(..., ge=0, le=1, description="Placeholder effectiveness score")
    
    # Context-specific metrics
    context_metrics: Dict[str, Dict[str, float]] = Field(
        default_factory=dict, 
        description="Metrics broken down by dialogue context"
    )

    model_config = ConfigDict(from_attributes=True)

# Error Schemas
class DialogueErrorSchema(BaseModel):
    """Schema for dialogue system errors."""
    
    error_type: str = Field(..., description="Type of error")
    error_code: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    conversation_id: Optional[str] = Field(None, description="Conversation identifier if applicable")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")
    details: Dict[str, Any] = Field(default_factory=dict, description="Additional error details")

    model_config = ConfigDict(from_attributes=True)

# Validation functions
def validate_conversation_id(v: str) -> str:
    """Validate conversation ID format."""
    if not v or len(v.strip()) == 0:
        raise ValueError("Conversation ID cannot be empty")
    return v.strip()

def validate_latency_value(v: float) -> float:
    """Validate latency values."""
    if v < 0:
        raise ValueError("Latency cannot be negative")
    if v > 300:  # 5 minutes max
        raise ValueError("Latency value seems unrealistic (>300 seconds)")
    return v

# Add validators to schemas that need them
ConversationSchema.model_rebuild()
LatencyResponseSchema.model_rebuild()
LatencyUpdateSchema.model_rebuild() 
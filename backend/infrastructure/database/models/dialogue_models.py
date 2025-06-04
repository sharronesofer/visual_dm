"""
Dialogue System Database Models

SQLAlchemy models for the dialogue system according to the Development Bible
database schema with enhanced features for RAG and extended message types.
"""

from sqlalchemy import Column, String, DateTime, JSON, Boolean, Text, Float, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PostgreSQL_UUID
from sqlalchemy.orm import relationship
from datetime import datetime
from uuid import uuid4

from backend.infrastructure.database.base import Base
from backend.infrastructure.shared.models import BaseEntity


class DialogueConversation(BaseEntity):
    """
    Core dialogue conversation table - matches Bible specification
    """
    __tablename__ = "dialogue_conversations"
    
    # Primary identification
    conversation_id = Column(PostgreSQL_UUID(as_uuid=True), unique=True, nullable=False, default=uuid4)
    npc_id = Column(PostgreSQL_UUID(as_uuid=True), nullable=False)
    player_id = Column(PostgreSQL_UUID(as_uuid=True), nullable=False)
    
    # Conversation metadata - Bible spec
    interaction_type = Column(String(50), nullable=False, default='casual')
    status = Column(String(20), nullable=False, default='active')
    context = Column(JSON, default=dict)
    properties = Column(JSON, default=dict)
    
    # Timing information - Bible spec
    started_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)
    last_activity = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Enhanced features for RAG and integrations
    location_id = Column(PostgreSQL_UUID(as_uuid=True), nullable=True)
    dialogue_context = Column(String(50), default='general')
    npc_type = Column(String(50), nullable=True)
    relationship_level = Column(Float, default=0.5)
    
    # RAG and AI processing metadata
    rag_enabled = Column(Boolean, default=True)
    ai_processing_metadata = Column(JSON, default=dict)
    total_ai_latency = Column(Float, nullable=True)
    
    # Relationships
    messages = relationship("DialogueMessage", back_populates="conversation", cascade="all, delete-orphan")
    analytics = relationship("DialogueAnalytics", back_populates="conversation", cascade="all, delete-orphan")


class DialogueMessage(BaseEntity):
    """
    Message history table - Bible specification with extended message types
    """
    __tablename__ = "dialogue_messages"
    
    # Foreign key to conversation
    conversation_id = Column(PostgreSQL_UUID(as_uuid=True), ForeignKey('dialogue_conversations.conversation_id'), nullable=False)
    
    # Message content - Bible spec
    content = Column(Text, nullable=False)
    speaker = Column(String(20), nullable=False)  # 'npc', 'player', 'system'
    metadata = Column(JSON, default=dict)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Extended message types beyond Bible spec
    message_type = Column(String(20), default='dialogue')  # dialogue, action, emote, placeholder
    emotion = Column(String(50), nullable=True)
    
    # Placeholder and latency tracking
    is_placeholder = Column(Boolean, default=False)
    placeholder_category = Column(String(50), nullable=True)
    replaced_by_message_id = Column(PostgreSQL_UUID(as_uuid=True), nullable=True)
    processing_time = Column(Float, nullable=True)
    
    # RAG enhancement tracking
    rag_enhanced = Column(Boolean, default=False)
    context_sources = Column(JSON, default=list)
    confidence_score = Column(Float, nullable=True)
    
    # Relationships
    conversation = relationship("DialogueConversation", back_populates="messages")


class DialogueAnalytics(BaseEntity):
    """
    Conversation analytics table - Bible specification with enhanced metrics
    """
    __tablename__ = "dialogue_analytics"
    
    # Foreign key to conversation
    conversation_id = Column(PostgreSQL_UUID(as_uuid=True), ForeignKey('dialogue_conversations.conversation_id'), nullable=False)
    
    # Bible specification fields
    event_type = Column(String(100), nullable=False)
    event_data = Column(JSON, nullable=False)
    player_id = Column(PostgreSQL_UUID(as_uuid=True), nullable=False)
    npc_id = Column(PostgreSQL_UUID(as_uuid=True), nullable=False)
    session_id = Column(PostgreSQL_UUID(as_uuid=True), nullable=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Enhanced analytics beyond Bible spec
    message_count = Column(Integer, default=0)
    total_duration = Column(Float, nullable=True)
    ai_requests = Column(Integer, default=0)
    average_response_time = Column(Float, nullable=True)
    placeholder_count = Column(Integer, default=0)
    timeout_occurrences = Column(Integer, default=0)
    rag_queries = Column(Integer, default=0)
    context_transitions = Column(JSON, default=list)
    
    # Relationship
    conversation = relationship("DialogueConversation", back_populates="analytics")


class DialogueKnowledgeBase(BaseEntity):
    """
    RAG knowledge base for dialogue enhancement - implementation enhancement
    """
    __tablename__ = "dialogue_knowledge_base"
    
    # Knowledge content
    content = Column(Text, nullable=False)
    category = Column(String(50), nullable=False)  # lore, characters, locations, etc.
    metadata = Column(JSON, default=dict)
    tags = Column(JSON, default=list)
    
    # Vector embedding for semantic search
    embedding_vector = Column(JSON, nullable=True)  # Store as JSON array
    embedding_model = Column(String(100), nullable=True)
    
    # Source tracking
    source_system = Column(String(50), nullable=True)  # memory, faction, quest, etc.
    source_id = Column(PostgreSQL_UUID(as_uuid=True), nullable=True)
    
    # Usage tracking
    usage_count = Column(Integer, default=0)
    last_accessed = Column(DateTime, nullable=True)
    relevance_score = Column(Float, default=0.0)


class DialogueSession(BaseEntity):
    """
    WebSocket session tracking for connection management
    """
    __tablename__ = "dialogue_sessions"
    
    # Session identification
    connection_id = Column(String(100), unique=True, nullable=False)
    player_id = Column(PostgreSQL_UUID(as_uuid=True), nullable=True)
    
    # Connection metadata
    connected_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    last_activity = Column(DateTime, nullable=False, default=datetime.utcnow)
    disconnected_at = Column(DateTime, nullable=True)
    client_info = Column(JSON, default=dict)
    
    # Subscribed conversations
    conversation_subscriptions = Column(JSON, default=list)
    
    # Connection quality metrics
    total_messages_sent = Column(Integer, default=0)
    total_messages_received = Column(Integer, default=0)
    connection_errors = Column(Integer, default=0)


# Indexes for performance (to be added in migration)
"""
CREATE INDEX idx_dialogue_conversations_conversation_id ON dialogue_conversations(conversation_id);
CREATE INDEX idx_dialogue_conversations_player_npc ON dialogue_conversations(player_id, npc_id);
CREATE INDEX idx_dialogue_conversations_status ON dialogue_conversations(status);
CREATE INDEX idx_dialogue_conversations_started_at ON dialogue_conversations(started_at);

CREATE INDEX idx_dialogue_messages_conversation_id ON dialogue_messages(conversation_id);
CREATE INDEX idx_dialogue_messages_timestamp ON dialogue_messages(timestamp);
CREATE INDEX idx_dialogue_messages_speaker ON dialogue_messages(speaker);
CREATE INDEX idx_dialogue_messages_message_type ON dialogue_messages(message_type);

CREATE INDEX idx_dialogue_analytics_conversation_id ON dialogue_analytics(conversation_id);
CREATE INDEX idx_dialogue_analytics_event_type ON dialogue_analytics(event_type);
CREATE INDEX idx_dialogue_analytics_timestamp ON dialogue_analytics(timestamp);

CREATE INDEX idx_dialogue_knowledge_category ON dialogue_knowledge_base(category);
CREATE INDEX idx_dialogue_knowledge_tags ON dialogue_knowledge_base USING gin(tags);
CREATE INDEX idx_dialogue_knowledge_usage ON dialogue_knowledge_base(usage_count, last_accessed);

CREATE INDEX idx_dialogue_sessions_connection_id ON dialogue_sessions(connection_id);
CREATE INDEX idx_dialogue_sessions_player_id ON dialogue_sessions(player_id);
CREATE INDEX idx_dialogue_sessions_connected_at ON dialogue_sessions(connected_at);
""" 
-- Dialogue System Database Migration
-- Implements the complete schema as specified in the Development Bible
-- Version: 2.0.0 - Full implementation with RAG and enhanced features

BEGIN;

-- Create dialogue_conversations table (Bible specification + enhancements)
CREATE TABLE IF NOT EXISTS dialogue_conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID UNIQUE NOT NULL DEFAULT gen_random_uuid(),
    npc_id UUID NOT NULL,
    player_id UUID NOT NULL,
    
    -- Core Bible specification fields
    interaction_type VARCHAR(50) NOT NULL DEFAULT 'casual',
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    context JSONB DEFAULT '{}',
    properties JSONB DEFAULT '{}',
    started_at TIMESTAMP NOT NULL DEFAULT NOW(),
    ended_at TIMESTAMP NULL,
    last_activity TIMESTAMP NOT NULL DEFAULT NOW(),
    
    -- Enhanced features for RAG and integrations
    location_id UUID NULL,
    dialogue_context VARCHAR(50) DEFAULT 'general',
    npc_type VARCHAR(50) NULL,
    relationship_level DECIMAL(3,2) DEFAULT 0.5,
    rag_enabled BOOLEAN DEFAULT TRUE,
    ai_processing_metadata JSONB DEFAULT '{}',
    total_ai_latency DECIMAL(8,3) NULL,
    
    -- Standard audit fields
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT chk_dialogue_conversations_status CHECK (status IN ('active', 'ended', 'paused', 'error')),
    CONSTRAINT chk_dialogue_conversations_interaction_type CHECK (interaction_type IN ('casual', 'quest', 'trading', 'combat', 'social')),
    CONSTRAINT chk_dialogue_conversations_dialogue_context CHECK (dialogue_context IN ('bartering', 'quest_related', 'faction_related', 'general', 'lore', 'social', 'combat')),
    CONSTRAINT chk_dialogue_conversations_relationship_level CHECK (relationship_level >= -1.0 AND relationship_level <= 1.0)
);

-- Create dialogue_messages table (Bible specification + extended message types)
CREATE TABLE IF NOT EXISTS dialogue_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL,
    
    -- Core Bible specification fields
    content TEXT NOT NULL,
    speaker VARCHAR(20) NOT NULL,
    metadata JSONB DEFAULT '{}',
    timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
    
    -- Extended message types beyond Bible spec
    message_type VARCHAR(20) DEFAULT 'dialogue',
    emotion VARCHAR(50) NULL,
    
    -- Placeholder and latency tracking
    is_placeholder BOOLEAN DEFAULT FALSE,
    placeholder_category VARCHAR(50) NULL,
    replaced_by_message_id UUID NULL,
    processing_time DECIMAL(6,3) NULL,
    
    -- RAG enhancement tracking
    rag_enhanced BOOLEAN DEFAULT FALSE,
    context_sources JSONB DEFAULT '[]',
    confidence_score DECIMAL(3,2) NULL,
    
    -- Standard audit fields
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    
    -- Foreign key constraints
    CONSTRAINT fk_dialogue_messages_conversation_id FOREIGN KEY (conversation_id) REFERENCES dialogue_conversations(conversation_id) ON DELETE CASCADE,
    
    -- Check constraints
    CONSTRAINT chk_dialogue_messages_speaker CHECK (speaker IN ('npc', 'player', 'system')),
    CONSTRAINT chk_dialogue_messages_message_type CHECK (message_type IN ('dialogue', 'action', 'emote', 'placeholder', 'system')),
    CONSTRAINT chk_dialogue_messages_placeholder_category CHECK (placeholder_category IS NULL OR placeholder_category IN ('thinking', 'processing', 'analyzing', 'remembering', 'consulting')),
    CONSTRAINT chk_dialogue_messages_confidence_score CHECK (confidence_score IS NULL OR (confidence_score >= 0.0 AND confidence_score <= 1.0))
);

-- Create dialogue_analytics table (Bible specification + enhanced metrics)
CREATE TABLE IF NOT EXISTS dialogue_analytics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL,
    
    -- Bible specification fields
    event_type VARCHAR(100) NOT NULL,
    event_data JSONB NOT NULL,
    player_id UUID NOT NULL,
    npc_id UUID NOT NULL,
    session_id UUID NULL,
    timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
    
    -- Enhanced analytics beyond Bible spec
    message_count INTEGER DEFAULT 0,
    total_duration DECIMAL(8,3) NULL,
    ai_requests INTEGER DEFAULT 0,
    average_response_time DECIMAL(6,3) NULL,
    placeholder_count INTEGER DEFAULT 0,
    timeout_occurrences INTEGER DEFAULT 0,
    rag_queries INTEGER DEFAULT 0,
    context_transitions JSONB DEFAULT '[]',
    
    -- Foreign key constraints
    CONSTRAINT fk_dialogue_analytics_conversation_id FOREIGN KEY (conversation_id) REFERENCES dialogue_conversations(conversation_id) ON DELETE CASCADE,
    
    -- Check constraints
    CONSTRAINT chk_dialogue_analytics_message_count CHECK (message_count >= 0),
    CONSTRAINT chk_dialogue_analytics_ai_requests CHECK (ai_requests >= 0),
    CONSTRAINT chk_dialogue_analytics_placeholder_count CHECK (placeholder_count >= 0),
    CONSTRAINT chk_dialogue_analytics_timeout_occurrences CHECK (timeout_occurrences >= 0),
    CONSTRAINT chk_dialogue_analytics_rag_queries CHECK (rag_queries >= 0)
);

-- Create dialogue_knowledge_base table (RAG enhancement - implementation enhancement)
CREATE TABLE IF NOT EXISTS dialogue_knowledge_base (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Knowledge content
    content TEXT NOT NULL,
    category VARCHAR(50) NOT NULL,
    metadata JSONB DEFAULT '{}',
    tags JSONB DEFAULT '[]',
    
    -- Vector embedding for semantic search
    embedding_vector JSONB NULL,
    embedding_model VARCHAR(100) NULL,
    
    -- Source tracking
    source_system VARCHAR(50) NULL,
    source_id UUID NULL,
    
    -- Usage tracking
    usage_count INTEGER DEFAULT 0,
    last_accessed TIMESTAMP NULL,
    relevance_score DECIMAL(3,2) DEFAULT 0.0,
    
    -- Standard audit fields
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    
    -- Check constraints
    CONSTRAINT chk_dialogue_knowledge_base_category CHECK (category IN ('lore', 'characters', 'locations', 'faction_interaction', 'quest_context', 'memory', 'personality', 'reputation')),
    CONSTRAINT chk_dialogue_knowledge_base_usage_count CHECK (usage_count >= 0),
    CONSTRAINT chk_dialogue_knowledge_base_relevance_score CHECK (relevance_score >= 0.0 AND relevance_score <= 1.0)
);

-- Create dialogue_sessions table (WebSocket session tracking for connection management)
CREATE TABLE IF NOT EXISTS dialogue_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Session identification
    connection_id VARCHAR(100) UNIQUE NOT NULL,
    player_id UUID NULL,
    
    -- Connection metadata
    connected_at TIMESTAMP NOT NULL DEFAULT NOW(),
    last_activity TIMESTAMP NOT NULL DEFAULT NOW(),
    disconnected_at TIMESTAMP NULL,
    client_info JSONB DEFAULT '{}',
    
    -- Subscribed conversations
    conversation_subscriptions JSONB DEFAULT '[]',
    
    -- Connection quality metrics
    total_messages_sent INTEGER DEFAULT 0,
    total_messages_received INTEGER DEFAULT 0,
    connection_errors INTEGER DEFAULT 0,
    
    -- Standard audit fields
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    
    -- Check constraints
    CONSTRAINT chk_dialogue_sessions_total_messages_sent CHECK (total_messages_sent >= 0),
    CONSTRAINT chk_dialogue_sessions_total_messages_received CHECK (total_messages_received >= 0),
    CONSTRAINT chk_dialogue_sessions_connection_errors CHECK (connection_errors >= 0)
);

-- Performance indexes as specified in the Bible
CREATE INDEX IF NOT EXISTS idx_dialogue_conversations_conversation_id ON dialogue_conversations(conversation_id);
CREATE INDEX IF NOT EXISTS idx_dialogue_conversations_player_npc ON dialogue_conversations(player_id, npc_id);
CREATE INDEX IF NOT EXISTS idx_dialogue_conversations_status ON dialogue_conversations(status);
CREATE INDEX IF NOT EXISTS idx_dialogue_conversations_started_at ON dialogue_conversations(started_at);
CREATE INDEX IF NOT EXISTS idx_dialogue_conversations_location_id ON dialogue_conversations(location_id);
CREATE INDEX IF NOT EXISTS idx_dialogue_conversations_dialogue_context ON dialogue_conversations(dialogue_context);

CREATE INDEX IF NOT EXISTS idx_dialogue_messages_conversation_id ON dialogue_messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_dialogue_messages_timestamp ON dialogue_messages(timestamp);
CREATE INDEX IF NOT EXISTS idx_dialogue_messages_speaker ON dialogue_messages(speaker);
CREATE INDEX IF NOT EXISTS idx_dialogue_messages_message_type ON dialogue_messages(message_type);
CREATE INDEX IF NOT EXISTS idx_dialogue_messages_is_placeholder ON dialogue_messages(is_placeholder);
CREATE INDEX IF NOT EXISTS idx_dialogue_messages_rag_enhanced ON dialogue_messages(rag_enhanced);

CREATE INDEX IF NOT EXISTS idx_dialogue_analytics_conversation_id ON dialogue_analytics(conversation_id);
CREATE INDEX IF NOT EXISTS idx_dialogue_analytics_event_type ON dialogue_analytics(event_type);
CREATE INDEX IF NOT EXISTS idx_dialogue_analytics_timestamp ON dialogue_analytics(timestamp);
CREATE INDEX IF NOT EXISTS idx_dialogue_analytics_player_id ON dialogue_analytics(player_id);
CREATE INDEX IF NOT EXISTS idx_dialogue_analytics_npc_id ON dialogue_analytics(npc_id);

CREATE INDEX IF NOT EXISTS idx_dialogue_knowledge_category ON dialogue_knowledge_base(category);
CREATE INDEX IF NOT EXISTS idx_dialogue_knowledge_source ON dialogue_knowledge_base(source_system, source_id);
CREATE INDEX IF NOT EXISTS idx_dialogue_knowledge_usage ON dialogue_knowledge_base(usage_count, last_accessed);
-- GIN index for tags array for efficient array searching
CREATE INDEX IF NOT EXISTS idx_dialogue_knowledge_tags ON dialogue_knowledge_base USING gin(tags);

CREATE INDEX IF NOT EXISTS idx_dialogue_sessions_connection_id ON dialogue_sessions(connection_id);
CREATE INDEX IF NOT EXISTS idx_dialogue_sessions_player_id ON dialogue_sessions(player_id);
CREATE INDEX IF NOT EXISTS idx_dialogue_sessions_connected_at ON dialogue_sessions(connected_at);
CREATE INDEX IF NOT EXISTS idx_dialogue_sessions_last_activity ON dialogue_sessions(last_activity);

-- Update triggers for automatic timestamp updates
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply update triggers to tables that have updated_at columns
CREATE TRIGGER update_dialogue_conversations_updated_at 
    BEFORE UPDATE ON dialogue_conversations 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_dialogue_knowledge_base_updated_at 
    BEFORE UPDATE ON dialogue_knowledge_base 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create a function to automatically update last_activity on dialogue_conversations
CREATE OR REPLACE FUNCTION update_conversation_last_activity()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE dialogue_conversations 
    SET last_activity = NOW() 
    WHERE conversation_id = NEW.conversation_id;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger to update conversation last_activity when new messages are added
CREATE TRIGGER update_conversation_activity_on_message 
    AFTER INSERT ON dialogue_messages 
    FOR EACH ROW EXECUTE FUNCTION update_conversation_last_activity();

-- Comments for documentation
COMMENT ON TABLE dialogue_conversations IS 'Core dialogue conversation tracking - Bible specification with RAG enhancements';
COMMENT ON TABLE dialogue_messages IS 'Message history with extended types for actions, emotes, and placeholders';
COMMENT ON TABLE dialogue_analytics IS 'Comprehensive conversation analytics and performance metrics';
COMMENT ON TABLE dialogue_knowledge_base IS 'RAG knowledge base for context-aware dialogue enhancement';
COMMENT ON TABLE dialogue_sessions IS 'WebSocket session tracking for connection management';

COMMENT ON COLUMN dialogue_conversations.rag_enabled IS 'Whether RAG enhancement is enabled for this conversation';
COMMENT ON COLUMN dialogue_messages.rag_enhanced IS 'Whether this message was enhanced using RAG';
COMMENT ON COLUMN dialogue_messages.context_sources IS 'JSON array of knowledge sources used for RAG enhancement';
COMMENT ON COLUMN dialogue_knowledge_base.embedding_vector IS 'JSON array containing vector embedding for semantic search';

COMMIT;

-- Verify the migration completed successfully
SELECT 'Dialogue System Migration Completed Successfully' AS status; 
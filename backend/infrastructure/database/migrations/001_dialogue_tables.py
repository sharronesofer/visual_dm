"""Create dialogue system tables

Revision ID: 001_dialogue_tables
Revises: 
Create Date: 2024-01-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_dialogue_tables'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create dialogue_conversations table
    op.create_table('dialogue_conversations',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('conversation_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('npc_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('player_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('interaction_type', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('context', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('properties', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('started_at', sa.DateTime(), nullable=False),
        sa.Column('ended_at', sa.DateTime(), nullable=True),
        sa.Column('last_activity', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('conversation_id')
    )
    op.create_index(op.f('ix_dialogue_conversations_npc_id'), 'dialogue_conversations', ['npc_id'], unique=False)
    op.create_index(op.f('ix_dialogue_conversations_player_id'), 'dialogue_conversations', ['player_id'], unique=False)

    # Create dialogue_messages table
    op.create_table('dialogue_messages',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('conversation_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('speaker', sa.String(length=20), nullable=False),
        sa.Column('metadata', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.CheckConstraint("speaker IN ('npc', 'player', 'system')", name='check_speaker_type'),
        sa.ForeignKeyConstraint(['conversation_id'], ['dialogue_conversations.conversation_id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_dialogue_messages_conversation_id'), 'dialogue_messages', ['conversation_id'], unique=False)

    # Create dialogue_analytics table
    op.create_table('dialogue_analytics',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('conversation_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('event_type', sa.String(length=100), nullable=False),
        sa.Column('event_data', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('player_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('npc_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['conversation_id'], ['dialogue_conversations.conversation_id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_dialogue_analytics_conversation_id'), 'dialogue_analytics', ['conversation_id'], unique=False)
    op.create_index(op.f('ix_dialogue_analytics_npc_id'), 'dialogue_analytics', ['npc_id'], unique=False)
    op.create_index(op.f('ix_dialogue_analytics_player_id'), 'dialogue_analytics', ['player_id'], unique=False)

    # Create dialogue_conversation_cache table
    op.create_table('dialogue_conversation_cache',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('conversation_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('cache_key', sa.String(length=255), nullable=False),
        sa.Column('cache_data', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_dialogue_conversation_cache_cache_key'), 'dialogue_conversation_cache', ['cache_key'], unique=False)
    op.create_index(op.f('ix_dialogue_conversation_cache_conversation_id'), 'dialogue_conversation_cache', ['conversation_id'], unique=False)

    # Create dialogue_npc_personalities table
    op.create_table('dialogue_npc_personalities',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('npc_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('personality_traits', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('conversation_style', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('background_context', sa.Text(), nullable=True),
        sa.Column('relationship_modifiers', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('bartering_preferences', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('npc_id')
    )
    op.create_index(op.f('ix_dialogue_npc_personalities_npc_id'), 'dialogue_npc_personalities', ['npc_id'], unique=False)

    # Create dialogue_context_windows table
    op.create_table('dialogue_context_windows',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('conversation_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('window_data', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('window_size', sa.Integer(), nullable=False),
        sa.Column('last_message_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_dialogue_context_windows_conversation_id'), 'dialogue_context_windows', ['conversation_id'], unique=False)

    # Create dialogue_performance_metrics table
    op.create_table('dialogue_performance_metrics',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('conversation_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('metric_type', sa.String(length=50), nullable=False),
        sa.Column('metric_value', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('response_time_ms', sa.Integer(), nullable=True),
        sa.Column('ai_processing_time_ms', sa.Integer(), nullable=True),
        sa.Column('websocket_latency_ms', sa.Integer(), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_dialogue_performance_metrics_conversation_id'), 'dialogue_performance_metrics', ['conversation_id'], unique=False)


def downgrade():
    op.drop_table('dialogue_performance_metrics')
    op.drop_table('dialogue_context_windows')
    op.drop_table('dialogue_npc_personalities')
    op.drop_table('dialogue_conversation_cache')
    op.drop_table('dialogue_analytics')
    op.drop_table('dialogue_messages')
    op.drop_table('dialogue_conversations') 
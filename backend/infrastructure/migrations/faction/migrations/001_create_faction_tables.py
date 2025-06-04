"""
Migration: Create Faction System Tables

This migration creates the base tables for the faction system including
faction entities, alliances, and betrayals.

Revision ID: 001
Revises: None
Create Date: 2024-01-14
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    """Create faction system tables."""
    
    # Create faction_entities table
    op.create_table(
        'faction_entities',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('status', sa.String(50), default='active'),
        sa.Column('properties', JSONB, default=dict),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('is_active', sa.Boolean, default=True, nullable=False),
    )
    
    # Create indexes for faction_entities
    op.create_index('idx_faction_entities_name', 'faction_entities', ['name'])
    op.create_index('idx_faction_entities_status', 'faction_entities', ['status'])
    op.create_index('idx_faction_entities_active', 'faction_entities', ['is_active'])
    op.create_index('idx_faction_entities_created', 'faction_entities', ['created_at'])
    
    # Create alliances table
    op.create_table(
        'alliances',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('alliance_type', sa.String(50), nullable=False),
        sa.Column('status', sa.String(50), default='proposed'),
        sa.Column('description', sa.Text),
        sa.Column('leader_faction_id', UUID(as_uuid=True), nullable=False),
        sa.Column('member_faction_ids', ARRAY(UUID(as_uuid=True)), default=[], nullable=False),
        sa.Column('terms', JSONB, default=dict),
        sa.Column('mutual_obligations', ARRAY(sa.Text), default=[]),
        sa.Column('shared_enemies', ARRAY(UUID(as_uuid=True)), default=[]),
        sa.Column('shared_goals', ARRAY(sa.Text), default=[]),
        sa.Column('start_date', sa.DateTime),
        sa.Column('end_date', sa.DateTime),
        sa.Column('auto_renew', sa.Boolean, default=False),
        sa.Column('trust_levels', JSONB, default=dict),
        sa.Column('betrayal_risks', JSONB, default=dict),
        sa.Column('reliability_history', JSONB, default=dict),
        sa.Column('triggers', JSONB, default=dict),
        sa.Column('threat_level', sa.Float, default=0.0),
        sa.Column('benefits_shared', JSONB, default=dict),
        sa.Column('military_support_provided', JSONB, default=dict),
        sa.Column('economic_support_provided', JSONB, default=dict),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('is_active', sa.Boolean, default=True, nullable=False),
        sa.Column('entity_metadata', JSONB, default=dict),
    )
    
    # Create indexes for alliances
    op.create_index('idx_alliances_name', 'alliances', ['name'])
    op.create_index('idx_alliances_type', 'alliances', ['alliance_type'])
    op.create_index('idx_alliances_status', 'alliances', ['status'])
    op.create_index('idx_alliances_leader', 'alliances', ['leader_faction_id'])
    op.create_index('idx_alliances_active', 'alliances', ['is_active'])
    op.create_index('idx_alliances_created', 'alliances', ['created_at'])
    
    # Create betrayals table
    op.create_table(
        'betrayals',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('alliance_id', UUID(as_uuid=True), nullable=False),
        sa.Column('betrayer_faction_id', UUID(as_uuid=True), nullable=False),
        sa.Column('victim_faction_ids', ARRAY(UUID(as_uuid=True)), default=[], nullable=False),
        sa.Column('betrayal_reason', sa.String(50), nullable=False),
        sa.Column('betrayal_type', sa.String(100), nullable=False),
        sa.Column('description', sa.Text, nullable=False),
        sa.Column('hidden_attributes_influence', JSONB, default=dict),
        sa.Column('external_pressure', JSONB),
        sa.Column('opportunity_details', JSONB),
        sa.Column('damage_dealt', JSONB, default=dict),
        sa.Column('trust_impact', JSONB, default=dict),
        sa.Column('reputation_impact', sa.Float, default=0.0),
        sa.Column('detected_immediately', sa.Boolean, default=True),
        sa.Column('detection_delay', sa.Integer),
        sa.Column('response_actions', JSONB, default=list),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('is_active', sa.Boolean, default=True, nullable=False),
        sa.Column('entity_metadata', JSONB, default=dict),
    )
    
    # Create indexes for betrayals
    op.create_index('idx_betrayals_alliance', 'betrayals', ['alliance_id'])
    op.create_index('idx_betrayals_betrayer', 'betrayals', ['betrayer_faction_id'])
    op.create_index('idx_betrayals_reason', 'betrayals', ['betrayal_reason'])
    op.create_index('idx_betrayals_active', 'betrayals', ['is_active'])
    op.create_index('idx_betrayals_created', 'betrayals', ['created_at'])


def downgrade():
    """Drop faction system tables."""
    
    # Drop tables in reverse order (to handle any potential foreign keys)
    op.drop_table('betrayals')
    op.drop_table('alliances')
    op.drop_table('faction_entities') 
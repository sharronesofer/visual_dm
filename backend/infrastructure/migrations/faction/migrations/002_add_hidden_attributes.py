"""
Migration: Add Hidden Attributes to Faction Entities

This migration adds the 6 hidden personality attributes to the faction_entities table
to support autonomous faction behavior patterns similar to NPCs.

Revision ID: 002_add_hidden_attributes
Revises: 001
Create Date: 2024-01-15
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '002_add_hidden_attributes'
down_revision = '001'
branch_labels = None
depends_on = None

def upgrade():
    """Add hidden personality attributes to faction entities table."""
    
    # Add the 6 hidden personality attribute columns
    with op.batch_alter_table('faction_entities') as batch_op:
        batch_op.add_column(sa.Column('hidden_ambition', sa.Integer(), nullable=False, default=3,
                                    comment='How aggressively the faction pursues growth, power, and territorial expansion (0-6)'))
        batch_op.add_column(sa.Column('hidden_integrity', sa.Integer(), nullable=False, default=3,
                                    comment='How honorable and trustworthy the faction is in treaties and dealings (0-6)'))
        batch_op.add_column(sa.Column('hidden_discipline', sa.Integer(), nullable=False, default=3,
                                    comment='How organized, methodical, and strategic the faction\'s operations are (0-6)'))
        batch_op.add_column(sa.Column('hidden_impulsivity', sa.Integer(), nullable=False, default=3,
                                    comment='How quickly the faction reacts to events without careful planning (0-6)'))
        batch_op.add_column(sa.Column('hidden_pragmatism', sa.Integer(), nullable=False, default=3,
                                    comment='How willing the faction is to compromise principles for practical gains (0-6)'))
        batch_op.add_column(sa.Column('hidden_resilience', sa.Integer(), nullable=False, default=3,
                                    comment='How well the faction handles setbacks, defeats, and crises (0-6)'))
    
    # Add check constraints to ensure attribute values are between 0 and 6
    op.create_check_constraint(
        'ck_faction_hidden_ambition',
        'faction_entities', 
        'hidden_ambition >= 0 AND hidden_ambition <= 6'
    )
    
    op.create_check_constraint(
        'ck_faction_hidden_integrity',
        'faction_entities', 
        'hidden_integrity >= 0 AND hidden_integrity <= 6'
    )
    
    op.create_check_constraint(
        'ck_faction_hidden_discipline',
        'faction_entities', 
        'hidden_discipline >= 0 AND hidden_discipline <= 6'
    )
    
    op.create_check_constraint(
        'ck_faction_hidden_impulsivity',
        'faction_entities', 
        'hidden_impulsivity >= 0 AND hidden_impulsivity <= 6'
    )
    
    op.create_check_constraint(
        'ck_faction_hidden_pragmatism',
        'faction_entities', 
        'hidden_pragmatism >= 0 AND hidden_pragmatism <= 6'
    )
    
    op.create_check_constraint(
        'ck_faction_hidden_resilience',
        'faction_entities', 
        'hidden_resilience >= 0 AND hidden_resilience <= 6'
    )
    
    # Create indexes for potential queries on hidden attributes
    op.create_index('idx_faction_hidden_ambition', 'faction_entities', ['hidden_ambition'])
    op.create_index('idx_faction_hidden_integrity', 'faction_entities', ['hidden_integrity'])
    op.create_index('idx_faction_hidden_discipline', 'faction_entities', ['hidden_discipline'])
    op.create_index('idx_faction_hidden_impulsivity', 'faction_entities', ['hidden_impulsivity'])
    op.create_index('idx_faction_hidden_pragmatism', 'faction_entities', ['hidden_pragmatism'])
    op.create_index('idx_faction_hidden_resilience', 'faction_entities', ['hidden_resilience'])


def downgrade():
    """Remove hidden personality attributes from faction entities table."""
    
    # Drop indexes first
    op.drop_index('idx_faction_hidden_resilience', 'faction_entities')
    op.drop_index('idx_faction_hidden_pragmatism', 'faction_entities')
    op.drop_index('idx_faction_hidden_impulsivity', 'faction_entities')
    op.drop_index('idx_faction_hidden_discipline', 'faction_entities')
    op.drop_index('idx_faction_hidden_integrity', 'faction_entities')
    op.drop_index('idx_faction_hidden_ambition', 'faction_entities')
    
    # Drop check constraints
    op.drop_constraint('ck_faction_hidden_resilience', 'faction_entities', type_='check')
    op.drop_constraint('ck_faction_hidden_pragmatism', 'faction_entities', type_='check')
    op.drop_constraint('ck_faction_hidden_impulsivity', 'faction_entities', type_='check')
    op.drop_constraint('ck_faction_hidden_discipline', 'faction_entities', type_='check')
    op.drop_constraint('ck_faction_hidden_integrity', 'faction_entities', type_='check')
    op.drop_constraint('ck_faction_hidden_ambition', 'faction_entities', type_='check')
    
    # Drop columns
    with op.batch_alter_table('faction_entities') as batch_op:
        batch_op.drop_column('hidden_resilience')
        batch_op.drop_column('hidden_pragmatism')
        batch_op.drop_column('hidden_impulsivity')
        batch_op.drop_column('hidden_discipline')
        batch_op.drop_column('hidden_integrity')
        batch_op.drop_column('hidden_ambition') 
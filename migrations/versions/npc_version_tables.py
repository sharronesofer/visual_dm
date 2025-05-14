"""
Database migration for NPC version control tables.
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy import inspect

# revision identifiers, used by Alembic
revision = '001_npc_version_tables'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    bind = op.get_bind()
    inspector = inspect(bind)

    # Create referenced tables if they do not exist
    if 'npcs' not in inspector.get_table_names():
        op.create_table(
            'npcs',
            sa.Column('id', sa.Integer(), primary_key=True),
            sa.Column('name', sa.String(100), nullable=False)
        )
    if 'code_versions' not in inspector.get_table_names():
        op.create_table(
            'code_versions',
            sa.Column('id', sa.Integer(), primary_key=True),
            sa.Column('version', sa.String(50), nullable=False)
        )
    if 'locations' not in inspector.get_table_names():
        op.create_table(
            'locations',
            sa.Column('id', sa.Integer(), primary_key=True),
            sa.Column('name', sa.String(100), nullable=False)
        )

    # Create npc_versions table
    if 'npc_versions' not in inspector.get_table_names():
        op.create_table(
            'npc_versions',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('npc_id', sa.Integer(), nullable=False),
            sa.Column('version_number', sa.Integer(), nullable=False),
            sa.Column('code_version_id', sa.Integer(), nullable=True),
            
            # Version data
            sa.Column('name', sa.String(100), nullable=False),
            sa.Column('type', sa.String(50), nullable=False),
            sa.Column('level', sa.Integer(), nullable=True),
            sa.Column('disposition', sa.String(20), nullable=True),
            sa.Column('base_disposition', sa.Float(), nullable=True),
            sa.Column('level_requirement', sa.Integer(), nullable=True),
            sa.Column('interaction_cooldown', sa.Integer(), nullable=True),
            sa.Column('current_location_id', sa.Integer(), nullable=True),
            sa.Column('home_location_id', sa.Integer(), nullable=True),
            
            # JSON fields
            sa.Column('schedule', postgresql.JSON(), nullable=True),
            sa.Column('dialogue_options', postgresql.JSON(), nullable=True),
            sa.Column('behavior_flags', postgresql.JSON(), nullable=True),
            sa.Column('inventory', postgresql.JSON(), nullable=True),
            sa.Column('trade_inventory', postgresql.JSON(), nullable=True),
            sa.Column('available_quests', postgresql.JSON(), nullable=True),
            sa.Column('completed_quests', postgresql.JSON(), nullable=True),
            sa.Column('goals', postgresql.JSON(), nullable=True),
            sa.Column('relationships', postgresql.JSON(), nullable=True),
            sa.Column('memories', postgresql.JSON(), nullable=True),
            
            # Change tracking
            sa.Column('change_type', sa.String(20), nullable=False),
            sa.Column('change_description', sa.Text(), nullable=False),
            sa.Column('changed_fields', postgresql.JSON(), nullable=False),
            sa.Column('created_at', sa.DateTime(), nullable=False),
            sa.Column('updated_at', sa.DateTime(), nullable=False),
            
            # Constraints
            sa.PrimaryKeyConstraint('id'),
            sa.ForeignKeyConstraint(['npc_id'], ['npcs.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['code_version_id'], ['code_versions.id'], ondelete='SET NULL'),
            sa.ForeignKeyConstraint(['current_location_id'], ['locations.id'], ondelete='SET NULL'),
            sa.ForeignKeyConstraint(['home_location_id'], ['locations.id'], ondelete='SET NULL')
        )
        
        # Create indexes
        op.create_index('ix_npc_versions_npc_id', 'npc_versions', ['npc_id'])
        op.create_index('ix_npc_versions_version_number', 'npc_versions', ['version_number'])
        op.create_unique_constraint('uq_npc_versions_npc_version', 'npc_versions', ['npc_id', 'version_number'])

def downgrade():
    # Drop indexes first
    op.drop_index('ix_npc_versions_version_number')
    op.drop_index('ix_npc_versions_npc_id')
    
    # Drop the table
    op.drop_table('npc_versions') 
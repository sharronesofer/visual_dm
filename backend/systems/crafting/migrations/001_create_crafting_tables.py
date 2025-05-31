"""
Migration: Create Crafting System Tables

This migration creates all the necessary tables for the crafting system.
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '001_crafting_tables'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    """Create crafting system tables."""
    
    # Create crafting_recipes table
    op.create_table(
        'crafting_recipes',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.String(), default=""),
        sa.Column('skill_required', sa.String(), nullable=True),
        sa.Column('min_skill_level', sa.Integer(), default=1),
        sa.Column('crafting_time', sa.Integer(), default=0),
        sa.Column('base_experience', sa.Integer(), default=10),
        sa.Column('station_required', sa.String(), nullable=True),
        sa.Column('station_level', sa.Integer(), default=0),
        sa.Column('is_hidden', sa.Boolean(), default=False),
        sa.Column('is_enabled', sa.Boolean(), default=True),
        sa.Column('recipe_metadata', sa.JSON(), default=dict),
        sa.Column('discovery_methods', sa.JSON(), default=list)
    )
    
    # Create indexes for recipes table
    op.create_index('idx_recipes_name', 'crafting_recipes', ['name'])
    op.create_index('idx_recipes_skill', 'crafting_recipes', ['skill_required'])
    op.create_index('idx_recipes_station', 'crafting_recipes', ['station_required'])
    op.create_index('idx_recipes_enabled', 'crafting_recipes', ['is_enabled'])
    op.create_index('idx_recipes_hidden', 'crafting_recipes', ['is_hidden'])
    
    # Create crafting_stations table
    op.create_table(
        'crafting_stations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.String(), default=""),
        sa.Column('station_type', sa.String(), nullable=False),
        sa.Column('level', sa.Integer(), default=1),
        sa.Column('capacity', sa.Integer(), default=1),
        sa.Column('efficiency_bonus', sa.Float(), default=1.0),
        sa.Column('quality_bonus', sa.Float(), default=0.0),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('is_public', sa.Boolean(), default=True),
        sa.Column('location_id', sa.String(), nullable=True),
        sa.Column('owner_id', sa.String(), nullable=True),
        sa.Column('upgrade_level', sa.Integer(), default=0),
        sa.Column('allowed_categories', sa.JSON(), default=list),
        sa.Column('required_materials', sa.JSON(), default=dict),
        sa.Column('special_abilities', sa.JSON(), default=list),
        sa.Column('maintenance_cost', sa.JSON(), default=dict),
        sa.Column('station_metadata', sa.JSON(), default=dict)
    )
    
    # Create indexes for stations table
    op.create_index('idx_stations_name', 'crafting_stations', ['name'])
    op.create_index('idx_stations_type', 'crafting_stations', ['station_type'])
    op.create_index('idx_stations_level', 'crafting_stations', ['level'])
    op.create_index('idx_stations_location', 'crafting_stations', ['location_id'])
    op.create_index('idx_stations_owner', 'crafting_stations', ['owner_id'])
    
    # Create crafting_ingredients table
    op.create_table(
        'crafting_ingredients',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.Column('recipe_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('crafting_recipes.id'), nullable=False),
        sa.Column('item_id', sa.String(), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False, default=1),
        sa.Column('is_consumed', sa.Boolean(), default=True),
        sa.Column('is_tool', sa.Boolean(), default=False),
        sa.Column('substitution_groups', sa.JSON(), default=dict),
        sa.Column('quality_requirement', sa.String(), nullable=True)
    )
    
    # Create indexes for ingredients table
    op.create_index('idx_ingredients_recipe', 'crafting_ingredients', ['recipe_id'])
    op.create_index('idx_ingredients_item', 'crafting_ingredients', ['item_id'])
    
    # Create crafting_results table
    op.create_table(
        'crafting_results',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.Column('recipe_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('crafting_recipes.id'), nullable=False),
        sa.Column('item_id', sa.String(), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False, default=1),
        sa.Column('probability', sa.Float(), nullable=False, default=1.0),
        sa.Column('quality_range', sa.JSON(), default=dict),
        sa.Column('bonus_conditions', sa.JSON(), default=dict),
        sa.Column('result_metadata', sa.JSON(), default=dict)
    )
    
    # Create indexes for results table
    op.create_index('idx_results_recipe', 'crafting_results', ['recipe_id'])
    op.create_index('idx_results_item', 'crafting_results', ['item_id'])

def downgrade():
    """Drop crafting system tables."""
    op.drop_table('crafting_results')
    op.drop_table('crafting_ingredients') 
    op.drop_table('crafting_stations')
    op.drop_table('crafting_recipes') 
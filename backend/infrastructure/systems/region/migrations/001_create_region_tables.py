"""
Create region and continent tables

Migration: 001_create_region_tables
Created: 2024-01-01
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB


def upgrade():
    """Create region and continent tables"""
    
    # Create regions table
    op.create_table(
        'regions',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        
        # Basic information
        sa.Column('name', sa.String(255), nullable=False, index=True),
        sa.Column('description', sa.Text),
        sa.Column('continent_id', sa.String(255), index=True),
        
        # Spatial data
        sa.Column('hex_q', sa.Integer, default=0),
        sa.Column('hex_r', sa.Integer, default=0),
        sa.Column('hex_s', sa.Integer, default=0),
        sa.Column('cartesian_x', sa.Float, default=0.0),
        sa.Column('cartesian_y', sa.Float, default=0.0),
        sa.Column('latitude', sa.Float),
        sa.Column('longitude', sa.Float),
        
        # Classification
        sa.Column('biome_type', sa.String(50), default='plains', index=True),
        sa.Column('climate_type', sa.String(50), default='temperate'),
        sa.Column('size', sa.Integer, default=50),
        sa.Column('area_sq_km', sa.Float, default=39.0),
        sa.Column('hex_count', sa.Integer, default=225),
        
        # Population and development
        sa.Column('total_population', sa.Integer, default=0),
        sa.Column('civilization_level', sa.Float, default=0.5),
        
        # Status and metadata
        sa.Column('status', sa.String(50), default='active', index=True),
        sa.Column('is_active', sa.Boolean, default=True, index=True),
        
        # JSON data fields
        sa.Column('profile_data', JSONB, default={}),
        sa.Column('environmental_data', JSONB, default={}),
        sa.Column('political_data', JSONB, default={}),
        sa.Column('economic_data', JSONB, default={}),
        sa.Column('geographic_data', JSONB, default={}),
        sa.Column('pois_data', JSONB, default={}),
        sa.Column('extra_metadata', JSONB, default={}),
    )
    
    # Create continents table
    op.create_table(
        'continents',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        
        # Basic information
        sa.Column('name', sa.String(255), nullable=False, index=True),
        sa.Column('description', sa.Text),
        
        # Generation data
        sa.Column('world_seed', sa.String(255)),
        sa.Column('generation_algorithm', sa.String(100), default='default'),
        
        # Scale and composition
        sa.Column('size', sa.Integer, default=30),
        sa.Column('total_population', sa.Integer, default=0),
        
        # Status
        sa.Column('status', sa.String(50), default='active', index=True),
        sa.Column('is_active', sa.Boolean, default=True, index=True),
        
        # JSON data fields
        sa.Column('region_data', JSONB, default={}),
        sa.Column('boundary_data', JSONB, default={}),
        sa.Column('climate_data', JSONB, default={}),
        sa.Column('political_data', JSONB, default={}),
        sa.Column('economic_data', JSONB, default={}),
        sa.Column('generation_parameters', JSONB, default={}),
        sa.Column('extra_metadata', JSONB, default={}),
    )
    
    # Create indexes for better performance
    op.create_index('idx_regions_coordinates', 'regions', ['hex_q', 'hex_r', 'hex_s'])
    op.create_index('idx_regions_continent_biome', 'regions', ['continent_id', 'biome_type'])
    op.create_index('idx_regions_population', 'regions', ['total_population'])
    op.create_index('idx_continents_name', 'continents', ['name'])


def downgrade():
    """Drop region and continent tables"""
    
    # Drop indexes
    op.drop_index('idx_continents_name')
    op.drop_index('idx_regions_population')
    op.drop_index('idx_regions_continent_biome')
    op.drop_index('idx_regions_coordinates')
    
    # Drop tables
    op.drop_table('continents')
    op.drop_table('regions') 
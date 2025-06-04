"""
Create region system tables

Migration for setting up the core region system database tables:
- continents: Main continent entities
- regions: Region entities with geographic and political data  
- resource_nodes: Resource entities linked to regions

Uses strings for all type fields per Development Bible.
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, ARRAY, JSON
from datetime import datetime


# Revision identifiers
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    """Create region system tables"""
    
    # Create continents table
    op.create_table(
        'continents',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        
        # Basic identification
        sa.Column('name', sa.String(255), nullable=False, index=True),
        sa.Column('description', sa.Text),
        
        # Geographic data
        sa.Column('total_area_square_km', sa.Float, default=0.0),
        sa.Column('climate_zones', ARRAY(sa.String), default=[]),  # Array of climate type strings
        sa.Column('major_biomes', ARRAY(sa.String), default=[]),   # Array of biome type strings
        
        # Political data
        sa.Column('major_powers', ARRAY(sa.String), default=[]),   # Array of faction UUIDs as strings
        sa.Column('political_situation', sa.String(50), default='stable'),
        
        # Generation data
        sa.Column('generation_seed', sa.Integer),
        sa.Column('generation_parameters', JSON, default={}),
        
        # Additional properties for extensibility
        sa.Column('properties', JSON, default={}),
    )
    
    # Create unique constraint on continent name
    op.create_unique_constraint('continents_name_key', 'continents', ['name'])
    
    # Create regions table
    op.create_table(
        'regions',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        
        # Basic identification
        sa.Column('name', sa.String(255), nullable=False, index=True),
        sa.Column('description', sa.Text),
        sa.Column('region_type', sa.String(50), nullable=False, default='wilderness'),
        sa.Column('status', sa.String(20), nullable=False, default='active'),
        
        # Geographic data (using strings per Bible)
        sa.Column('dominant_biome', sa.String(50), nullable=False, default='temperate_forest'),
        sa.Column('climate', sa.String(50), nullable=False, default='temperate'),
        sa.Column('hex_coordinates', JSON, default=[]),  # List of hex coordinate dicts
        sa.Column('center_coordinate', JSON),  # Single hex coordinate dict
        sa.Column('area_square_km', sa.Float, default=0.0),
        sa.Column('perimeter_km', sa.Float, default=0.0),
        sa.Column('elevation', sa.Float, default=0.0),
        sa.Column('elevation_variance', sa.Float, default=0.0),
        
        # Environmental data
        sa.Column('temperature_range', JSON),  # [min, max] tuple
        sa.Column('precipitation', sa.Float, default=500.0),
        sa.Column('humidity', sa.Float, default=0.5),
        sa.Column('wind_patterns', JSON),
        sa.Column('seasonal_variations', JSON),
        sa.Column('natural_hazards', ARRAY(sa.String)),
        sa.Column('soil_fertility', sa.Float, default=0.5),
        sa.Column('water_availability', sa.Float, default=0.5),
        
        # Political data
        sa.Column('controlling_faction_id', UUID(as_uuid=True)),
        sa.Column('government_type', sa.String(50), default='none'),
        sa.Column('political_stability', sa.Float, default=0.5),
        sa.Column('law_level', sa.Integer, default=5),
        
        # Economic data
        sa.Column('wealth_level', sa.Float, default=0.5),
        sa.Column('trade_routes', ARRAY(sa.String)),
        sa.Column('primary_industries', ARRAY(sa.String)),
        
        # Demographic data
        sa.Column('population', sa.Integer, default=0),
        sa.Column('population_density', sa.Float, default=0.0),
        sa.Column('major_settlements', ARRAY(sa.String)),
        
        # Gameplay data
        sa.Column('danger_level', sa.Integer, default=2),
        sa.Column('exploration_status', sa.Float, default=0.0),
        sa.Column('discovery_date', sa.String),  # ISO date string
        
        # Connections
        sa.Column('neighboring_region_ids', ARRAY(sa.String)),
        sa.Column('continent_id', UUID(as_uuid=True), sa.ForeignKey('continents.id')),
        
        # Dynamic state
        sa.Column('current_events', ARRAY(sa.String)),
        sa.Column('historical_events', ARRAY(sa.String)),
        
        # Resource nodes (stored as JSON for now)
        sa.Column('resource_nodes', JSON, default=[]),
        sa.Column('poi_ids', ARRAY(sa.String)),
        
        # Additional properties for extensibility
        sa.Column('properties', JSON, default={}),
    )
    
    # Create unique constraint on region name
    op.create_unique_constraint('regions_name_key', 'regions', ['name'])
    
    # Create indexes for common queries
    op.create_index('idx_regions_continent_id', 'regions', ['continent_id'])
    op.create_index('idx_regions_region_type', 'regions', ['region_type'])
    op.create_index('idx_regions_dominant_biome', 'regions', ['dominant_biome'])
    op.create_index('idx_regions_climate', 'regions', ['climate'])
    op.create_index('idx_regions_danger_level', 'regions', ['danger_level'])
    op.create_index('idx_regions_population', 'regions', ['population'])
    
    # Create resource_nodes table
    op.create_table(
        'resource_nodes',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        
        # Resource identification (using strings per Bible)
        sa.Column('resource_type', sa.String(50), nullable=False),
        
        # Resource properties
        sa.Column('abundance', sa.Float, nullable=False),
        sa.Column('quality', sa.Float, nullable=False),
        sa.Column('accessibility', sa.Float, nullable=False),
        sa.Column('depletion_rate', sa.Float, default=0.0),
        sa.Column('current_reserves', sa.Float, default=1.0),
        
        # Location data
        sa.Column('region_id', UUID(as_uuid=True), sa.ForeignKey('regions.id'), nullable=False),
        sa.Column('hex_coordinate', JSON),  # Optional specific location within region
        
        # Additional properties
        sa.Column('properties', JSON, default={}),
    )
    
    # Create indexes for resource queries
    op.create_index('idx_resource_nodes_region_id', 'resource_nodes', ['region_id'])
    op.create_index('idx_resource_nodes_resource_type', 'resource_nodes', ['resource_type'])
    op.create_index('idx_resource_nodes_abundance', 'resource_nodes', ['abundance'])
    
    # Create foreign key constraints
    op.create_foreign_key(
        'fk_regions_continent_id', 
        'regions', 
        'continents',
        ['continent_id'], 
        ['id'],
        ondelete='SET NULL'
    )
    
    op.create_foreign_key(
        'fk_resource_nodes_region_id', 
        'resource_nodes', 
        'regions',
        ['region_id'], 
        ['id'],
        ondelete='CASCADE'
    )


def downgrade():
    """Drop region system tables"""
    
    # Drop tables in reverse order due to foreign key constraints
    op.drop_table('resource_nodes')
    op.drop_table('regions')  
    op.drop_table('continents') 
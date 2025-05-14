"""
Migration script to create loot system database tables.
"""

from datetime import datetime, timedelta
from sqlalchemy import (
    create_engine, MetaData, Table, Column, Integer, String, Float, JSON,
    DateTime, ForeignKey, Text, Enum, Boolean, Interval
)
from app.core.database import db
from app.loot.models import (
    ItemType, RarityTier, LocationType, ContainerType,
    ShopType, LootSourceType, MetricType
)

def upgrade():
    """Create loot system tables."""
    # Create loot_items table
    Table('loot_items', db.metadata,
        Column('id', Integer, primary_key=True),
        Column('name', String(100), nullable=False),
        Column('description', Text),
        Column('item_type', Enum(ItemType), nullable=False),
        Column('rarity', Enum(RarityTier), default=RarityTier.COMMON),
        Column('weight', Float, default=0.0),
        Column('value', Integer, default=0),
        Column('base_stats', JSON, default=dict),
        Column('thematic_tags', JSON, default=list),
        Column('created_at', DateTime, default=datetime.utcnow),
        Column('updated_at', DateTime, default=datetime.utcnow, onupdate=datetime.utcnow),
        extend_existing=True
    )

    # Create loot_locations table
    Table('loot_locations', db.metadata,
        Column('id', Integer, primary_key=True),
        Column('name', String(100), nullable=False),
        Column('location_type', Enum(LocationType), nullable=False),
        Column('description', Text),
        Column('danger_level', Integer, default=1),
        Column('base_loot_multiplier', Float, default=1.0),
        Column('thematic_tags', JSON, default=list),
        Column('created_at', DateTime, default=datetime.utcnow),
        Column('updated_at', DateTime, default=datetime.utcnow, onupdate=datetime.utcnow),
        extend_existing=True
    )

    # Create loot_containers table
    Table('loot_containers', db.metadata,
        Column('id', Integer, primary_key=True),
        Column('container_type', Enum(ContainerType), nullable=False),
        Column('location_id', Integer, ForeignKey('loot_locations.id'), nullable=False),
        Column('name', String(100)),
        Column('description', Text),
        Column('danger_level', Integer),
        Column('is_locked', Boolean, default=False),
        Column('is_trapped', Boolean, default=False),
        Column('is_opened', Boolean, default=False),
        Column('respawn_time', Integer),
        Column('created_at', DateTime, default=datetime.utcnow),
        Column('opened_at', DateTime),
        Column('expires_at', DateTime),
        Column('updated_at', DateTime, default=datetime.utcnow, onupdate=datetime.utcnow),
        extend_existing=True
    )

    # Create loot_container_contents table
    Table('loot_container_contents', db.metadata,
        Column('id', Integer, primary_key=True),
        Column('container_id', Integer, ForeignKey('loot_containers.id'), nullable=False),
        Column('item_id', Integer, ForeignKey('loot_items.id'), nullable=False),
        Column('quantity', Integer, default=1),
        Column('is_claimed', Boolean, default=False),
        Column('created_at', DateTime, default=datetime.utcnow),
        Column('claimed_at', DateTime),
        Column('updated_at', DateTime, default=datetime.utcnow, onupdate=datetime.utcnow),
        extend_existing=True
    )

    # Create loot_shops table
    Table('loot_shops', db.metadata,
        Column('id', Integer, primary_key=True),
        Column('name', String(100), nullable=False),
        Column('shop_type', Enum(ShopType), nullable=False),
        Column('location_id', Integer, ForeignKey('loot_locations.id'), nullable=False),
        Column('description', Text),
        Column('refresh_interval', Interval, default=timedelta(days=1)),
        Column('base_markup', Float, default=1.5),
        Column('reputation_requirement', Integer, default=0),
        Column('last_refresh', DateTime, default=datetime.utcnow),
        Column('next_refresh', DateTime),
        Column('created_at', DateTime, default=datetime.utcnow),
        Column('updated_at', DateTime, default=datetime.utcnow, onupdate=datetime.utcnow),
        extend_existing=True
    )

    # Create loot_shop_inventory table
    Table('loot_shop_inventory', db.metadata,
        Column('id', Integer, primary_key=True),
        Column('shop_id', Integer, ForeignKey('loot_shops.id'), nullable=False),
        Column('item_id', Integer, ForeignKey('loot_items.id'), nullable=False),
        Column('quantity', Integer, default=1),
        Column('price', Integer, nullable=False),
        Column('is_special', Boolean, default=False),
        Column('restock_quantity', Integer),
        Column('min_quantity', Integer, default=0),
        Column('max_quantity', Integer),
        Column('created_at', DateTime, default=datetime.utcnow),
        Column('expires_at', DateTime),
        Column('updated_at', DateTime, default=datetime.utcnow, onupdate=datetime.utcnow),
        extend_existing=True
    )

    # Create loot_history table
    Table('loot_history', db.metadata,
        Column('id', Integer, primary_key=True),
        Column('source_type', Enum(LootSourceType), nullable=False),
        Column('source_id', String(50)),
        Column('item_id', Integer, ForeignKey('loot_items.id'), nullable=False),
        Column('quantity', Integer, default=1),
        Column('player_id', Integer, ForeignKey('users.id')),
        Column('character_id', Integer, ForeignKey('characters.id')),
        Column('location_id', Integer, ForeignKey('loot_locations.id')),
        Column('danger_level', Integer),
        Column('player_level', Integer),
        Column('value', Integer),
        Column('context', JSON, default=dict),
        Column('created_at', DateTime, default=datetime.utcnow),
        extend_existing=True
    )

    # Create loot_analytics table
    Table('loot_analytics', db.metadata,
        Column('id', Integer, primary_key=True),
        Column('metric_type', Enum(MetricType), nullable=False),
        Column('time_bucket', DateTime, nullable=False),
        Column('location_id', Integer, ForeignKey('loot_locations.id')),
        Column('danger_level', Integer),
        Column('player_level_range', String(20)),
        Column('metric_value', Float, nullable=False),
        Column('sample_size', Integer, nullable=False),
        Column('context', JSON, default=dict),
        Column('created_at', DateTime, default=datetime.utcnow),
        extend_existing=True
    )

    # Create indices
    db.Index('idx_loot_items_type_rarity', 'loot_items.item_type', 'loot_items.rarity')
    db.Index('idx_loot_locations_type_danger', 'loot_locations.location_type', 'loot_locations.danger_level')
    db.Index('idx_loot_containers_location', 'loot_containers.location_id')
    db.Index('idx_loot_containers_type', 'loot_containers.container_type')
    db.Index('idx_loot_container_contents_container', 'loot_container_contents.container_id')
    db.Index('idx_loot_container_contents_item', 'loot_container_contents.item_id')
    db.Index('idx_loot_shops_location', 'loot_shops.location_id')
    db.Index('idx_loot_shops_type', 'loot_shops.shop_type')
    db.Index('idx_loot_shop_inventory_shop', 'loot_shop_inventory.shop_id')
    db.Index('idx_loot_shop_inventory_item', 'loot_shop_inventory.item_id')
    db.Index('idx_loot_history_source', 'loot_history.source_type', 'loot_history.source_id')
    db.Index('idx_loot_history_item', 'loot_history.item_id')
    db.Index('idx_loot_history_player', 'loot_history.player_id')
    db.Index('idx_loot_history_character', 'loot_history.character_id')
    db.Index('idx_loot_history_location', 'loot_history.location_id')
    db.Index('idx_loot_analytics_metric_time', 'loot_analytics.metric_type', 'loot_analytics.time_bucket')
    db.Index('idx_loot_analytics_location', 'loot_analytics.location_id')

def downgrade():
    """Remove loot system tables."""
    tables = [
        'loot_analytics',
        'loot_history',
        'loot_shop_inventory',
        'loot_shops',
        'loot_container_contents',
        'loot_containers',
        'loot_locations',
        'loot_items'
    ]
    
    for table in tables:
        if table in db.metadata.tables:
            db.metadata.tables[table].drop() 
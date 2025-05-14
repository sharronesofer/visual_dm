"""
Isolated schema validation for the loot system.
"""
import pytest
from sqlalchemy import create_engine, Table, MetaData, Column, Integer, inspect, text
from sqlalchemy.orm import sessionmaker, clear_mappers, DeclarativeMeta
import os

from loot_models.base import LootBase
from loot_models.base_item import BaseItem, ItemType, RarityTier
from loot_models.location import Location, LocationType, Container, ContainerType, ContainerContent
from loot_models.shop import Shop, ShopType, ShopInventory
from loot_models.history import LootHistory, LootSourceType, LootAnalytics, MetricType

@pytest.fixture(scope="module")
def in_memory_db():
    engine = create_engine("sqlite:///:memory:")
    conn = engine.connect()
    # Register loot model tables with metadata (no-op if already registered)
    for model in [
        BaseItem, Location, Container, ContainerContent, Shop, ShopInventory, LootHistory, LootAnalytics
    ]:
        if isinstance(model, DeclarativeMeta):
            pass  # Table is already registered with LootBase.metadata
    # Create minimal stub tables for referenced FKs using LootBase.metadata (after loot model imports)
    users = Table('users', LootBase.metadata, Column('id', Integer, primary_key=True))
    characters = Table('characters', LootBase.metadata, Column('id', Integer, primary_key=True))
    # Create all tables (stubs + loot models) in one call
    LootBase.metadata.create_all(conn)
    # Debug: print all table names in metadata and in the database
    print('LootBase.metadata.tables:', list(LootBase.metadata.tables.keys()))
    print('Tables in SQLite:', [row[0] for row in conn.execute(text("SELECT name FROM sqlite_master WHERE type='table';")).fetchall()])
    yield conn
    clear_mappers()
    engine.dispose()

def test_loot_schema_tables(in_memory_db):
    # Table creation is now handled in the fixture
    assert in_memory_db is not None

def test_loot_schema_tables_exist(in_memory_db):
    inspector = inspect(in_memory_db)
    expected_tables = {
        'loot_items', 'loot_locations', 'loot_containers', 'loot_container_contents',
        'loot_shops', 'loot_shop_inventory', 'loot_history', 'loot_analytics'
    }
    actual_tables = set(inspector.get_table_names())
    missing = expected_tables - actual_tables
    assert not missing, f"Missing tables: {missing}"

def test_loot_items_columns(in_memory_db):
    inspector = inspect(in_memory_db)
    columns = {col['name'] for col in inspector.get_columns('loot_items')}
    required = {'id', 'name', 'item_type', 'rarity', 'weight', 'value', 'base_stats', 'thematic_tags', 'created_at', 'updated_at'}
    assert required.issubset(columns), f"Missing columns in loot_items: {required - columns}"

def test_loot_history_foreign_keys(in_memory_db):
    inspector = inspect(in_memory_db)
    fks = inspector.get_foreign_keys('loot_history')
    fk_columns = {fk['constrained_columns'][0] for fk in fks}
    required = {'item_id', 'player_id', 'character_id', 'location_id'}
    assert required.issubset(fk_columns), f"Missing FKs in loot_history: {required - fk_columns}" 
"""Database migration to add performance-optimizing indexes."""

from alembic import op
import sqlalchemy as sa

def upgrade():
    """Add performance-optimizing indexes."""
    
    # Character-Related Indexes
    op.create_index('ix_relationships_character_id', 'relationships', ['character_id'])
    op.create_index('ix_events_character_id', 'events', ['character_id'])
    op.create_index('ix_characters_party_id', 'characters', ['party_id'])
    op.create_index('ix_characters_region_id', 'characters', ['region_id'])
    
    # Quest-Related Indexes
    op.create_index('ix_quests_status', 'quests', ['status'])
    op.create_index('ix_quests_region_id', 'quests', ['region_id'])
    op.create_index('ix_character_quests_composite', 'character_quests', 
                    ['character_id', 'quest_id'])
    
    # Social/Relationship Indexes
    op.create_index('ix_character_relationships_composite', 'character_relationships',
                    ['character_id', 'related_character_id'])
    op.create_index('ix_faction_relationships_composite', 'faction_relationships',
                    ['faction_id', 'related_faction_id'])
    op.create_index('ix_relationships_type', 'relationships', ['relationship_type'])
    
    # Region/Location Indexes
    op.create_index('ix_regions_type', 'regions', ['type'])
    op.create_index('ix_locations_region_id', 'locations', ['region_id'])
    op.create_index('ix_party_region_composite', 'party_region',
                    ['party_id', 'region_id'])
    
    # Item/Inventory Indexes
    op.create_index('ix_inventory_items_type', 'inventory_items', ['item_type'])
    op.create_index('ix_inventory_items_rarity', 'inventory_items', ['rarity'])
    op.create_index('ix_inventory_items_owner_id', 'inventory_items', ['owner_id'])

def downgrade():
    """Remove performance-optimizing indexes."""
    
    # Character-Related Indexes
    op.drop_index('ix_relationships_character_id')
    op.drop_index('ix_events_character_id')
    op.drop_index('ix_characters_party_id')
    op.drop_index('ix_characters_region_id')
    
    # Quest-Related Indexes
    op.drop_index('ix_quests_status')
    op.drop_index('ix_quests_region_id')
    op.drop_index('ix_character_quests_composite')
    
    # Social/Relationship Indexes
    op.drop_index('ix_character_relationships_composite')
    op.drop_index('ix_faction_relationships_composite')
    op.drop_index('ix_relationships_type')
    
    # Region/Location Indexes
    op.drop_index('ix_regions_type')
    op.drop_index('ix_locations_region_id')
    op.drop_index('ix_party_region_composite')
    
    # Item/Inventory Indexes
    op.drop_index('ix_inventory_items_type')
    op.drop_index('ix_inventory_items_rarity')
    op.drop_index('ix_inventory_items_owner_id') 
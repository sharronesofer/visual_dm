"""
Test suite for the Loot Generation System.
"""

import pytest
from app.combat.loot_generator import (
    LootGenerator, 
    LootTableEntry, 
    ItemRarity, 
    Currency, 
    LootResult
)

@pytest.fixture
def loot_generator():
    """Create a LootGenerator instance with some test data."""
    generator = LootGenerator()
    
    # Register some enemy types
    generator.register_enemy_type("goblin_1", "goblin")
    generator.register_enemy_type("dragon_1", "dragon")
    
    # Create test loot tables
    goblin_loot = [
        LootTableEntry(
            item_id="rusty_sword",
            rarity=ItemRarity.COMMON,
            drop_chance=0.5,
            level_requirement=1,
            quantity_range=(1, 1)
        ),
        LootTableEntry(
            item_id="leather_scraps",
            rarity=ItemRarity.COMMON,
            drop_chance=0.8,
            level_requirement=1,
            quantity_range=(1, 3)
        )
    ]
    
    dragon_loot = [
        LootTableEntry(
            item_id="dragon_scale",
            rarity=ItemRarity.RARE,
            drop_chance=1.0,
            level_requirement=5,
            quantity_range=(2, 5)
        ),
        LootTableEntry(
            item_id="dragon_heart",
            rarity=ItemRarity.LEGENDARY,
            drop_chance=0.1,
            level_requirement=10,
            quantity_range=(1, 1),
            boss_only=True
        )
    ]
    
    generator.register_loot_table("goblin", goblin_loot)
    generator.register_loot_table("dragon", dragon_loot)
    
    return generator

def test_currency_conversion():
    """Test currency conversion methods."""
    # Test conversion to copper
    currency = Currency(copper=5, silver=3, gold=2, platinum=1)
    assert currency.total_in_copper() == 1325  # 1000 + 200 + 30 + 5
    
    # Test conversion from copper
    currency = Currency.from_copper(1325)
    assert currency.platinum == 1
    assert currency.gold == 2
    assert currency.silver == 3
    assert currency.copper == 5

def test_base_currency_calculation(loot_generator):
    """Test base currency calculation for different enemy levels."""
    # Test normal enemy
    base_copper = loot_generator._calculate_base_currency(enemy_level=1, is_boss=False)
    assert 8 <= base_copper <= 12  # Level 1: ~10 copper ±20%
    
    # Test boss multiplier
    boss_copper = loot_generator._calculate_base_currency(enemy_level=1, is_boss=True)
    assert 24 <= boss_copper <= 60  # 3-5x multiplier on base
    
    # Test higher level scaling
    high_level = loot_generator._calculate_base_currency(enemy_level=10, is_boss=False)
    assert high_level > base_copper  # Should scale with level

def test_party_level_multiplier(loot_generator):
    """Test loot quality multiplier based on party vs enemy level."""
    # Test equal levels
    assert loot_generator._calculate_party_level_multiplier(10, 10) == 1.0
    
    # Test high level party vs low level enemy
    assert loot_generator._calculate_party_level_multiplier(15, 10) < 1.0
    
    # Test low level party vs high level enemy
    assert loot_generator._calculate_party_level_multiplier(5, 10) > 1.0

def test_item_generation(loot_generator):
    """Test item generation from loot tables."""
    # Test goblin loot (non-boss)
    items = loot_generator._roll_for_items("goblin", enemy_level=1, party_level=1, is_boss=False)
    for item_id, quantity in items:
        assert item_id in ["rusty_sword", "leather_scraps"]
        if item_id == "rusty_sword":
            assert quantity == 1
        elif item_id == "leather_scraps":
            assert 1 <= quantity <= 3
    
    # Test dragon loot (boss)
    items = loot_generator._roll_for_items("dragon", enemy_level=10, party_level=10, is_boss=True)
    for item_id, quantity in items:
        assert item_id in ["dragon_scale", "dragon_heart"]
        if item_id == "dragon_scale":
            assert 2 <= quantity <= 5
        elif item_id == "dragon_heart":
            assert quantity == 1

def test_special_item_generation(loot_generator):
    """Test special item generation for bosses."""
    # Test non-boss enemy (should get no special items)
    special_items = loot_generator._generate_special_items("goblin", enemy_level=1, is_boss=False)
    assert len(special_items) == 0
    
    # Test boss enemy (should get at least one special item)
    special_items = loot_generator._generate_special_items("dragon", enemy_level=10, is_boss=True)
    assert len(special_items) >= 1
    assert special_items[0] == "unique_dragon_drop_10"

def test_complete_loot_generation(loot_generator):
    """Test complete loot generation for an enemy."""
    # Test invalid enemy ID
    with pytest.raises(ValueError):
        loot_generator.generate_loot("unknown_enemy", 1, 1)
    
    # Test normal goblin
    loot = loot_generator.generate_loot("goblin_1", enemy_level=1, party_level=1)
    assert isinstance(loot, LootResult)
    assert isinstance(loot.currency, Currency)
    assert isinstance(loot.items, list)
    assert isinstance(loot.special_items, list)
    
    # Test boss dragon
    loot = loot_generator.generate_loot("dragon_1", enemy_level=10, party_level=10, is_boss=True)
    assert any(item_id == "dragon_heart" for item_id, _ in loot.items)
    assert len(loot.special_items) >= 1
    assert loot.currency.total_in_copper() > 0

def test_group_loot_distribution(loot_generator):
    """Test loot distribution among party members."""
    # Generate some test loot
    loot = LootResult(
        items=[("test_item", 1)],
        currency=Currency(gold=5),  # 500 copper
        special_items=["unique_item"]
    )
    
    # Test invalid player count
    with pytest.raises(ValueError):
        loot_generator.distribute_group_loot(loot, 0)
    
    # Test even distribution
    shares = loot_generator.distribute_group_loot(loot, 4)
    assert len(shares) == 4
    total_copper = sum(share.currency.total_in_copper() for share in shares.values())
    assert total_copper == 500  # Original amount
    
    # Test uneven distribution (should handle remainder)
    shares = loot_generator.distribute_group_loot(loot, 3)
    copper_counts = [share.currency.total_in_copper() for share in shares.values()]
    assert sum(copper_counts) == 500
    assert max(copper_counts) - min(copper_counts) <= 1  # Difference should be at most 1 
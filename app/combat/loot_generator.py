"""
Loot Generation System for the Combat Management System.

This module handles the generation and distribution of loot from defeated enemies,
including items, currency, and special rewards based on encounter difficulty,
enemy types, and party levels.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Tuple
import random
import math

class ItemRarity(Enum):
    COMMON = 1
    UNCOMMON = 2
    RARE = 3
    VERY_RARE = 4
    LEGENDARY = 5
    UNIQUE = 6

@dataclass
class LootTableEntry:
    item_id: str
    rarity: ItemRarity
    drop_chance: float  # 0.0 to 1.0
    level_requirement: int
    quantity_range: Tuple[int, int]  # (min, max)
    boss_only: bool = False

@dataclass
class Currency:
    copper: int = 0
    silver: int = 0
    gold: int = 0
    platinum: int = 0

    def total_in_copper(self) -> int:
        """Convert all currency to copper pieces."""
        return (self.copper + 
                self.silver * 10 + 
                self.gold * 100 + 
                self.platinum * 1000)

    @classmethod
    def from_copper(cls, copper: int) -> 'Currency':
        """Create a Currency object from total copper pieces, automatically converting to higher denominations."""
        platinum = copper // 1000
        copper %= 1000
        gold = copper // 100
        copper %= 100
        silver = copper // 10
        copper %= 10
        return cls(copper=copper, silver=silver, gold=gold, platinum=platinum)

@dataclass
class LootResult:
    items: List[Tuple[str, int]]  # List of (item_id, quantity)
    currency: Currency
    special_items: List[str]  # Unique or quest items

class LootGenerator:
    def __init__(self):
        self.loot_tables: Dict[str, List[LootTableEntry]] = {}
        self.enemy_types: Dict[str, str] = {}  # Maps enemy IDs to their type (e.g., "goblin", "dragon")
        self.rarity_weights = {
            ItemRarity.COMMON: 100,
            ItemRarity.UNCOMMON: 60,
            ItemRarity.RARE: 30,
            ItemRarity.VERY_RARE: 15,
            ItemRarity.LEGENDARY: 5,
            ItemRarity.UNIQUE: 1
        }

    def register_loot_table(self, enemy_type: str, entries: List[LootTableEntry]) -> None:
        """Register a loot table for a specific enemy type."""
        self.loot_tables[enemy_type] = entries

    def register_enemy_type(self, enemy_id: str, enemy_type: str) -> None:
        """Register an enemy's type for loot table lookup."""
        self.enemy_types[enemy_id] = enemy_type

    def _calculate_base_currency(self, enemy_level: int, is_boss: bool = False) -> int:
        """Calculate base currency drops in copper pieces."""
        # Base formula: (level^1.5 * 10) copper pieces
        base = math.floor(pow(enemy_level, 1.5) * 10)
        
        # Add randomness (±20%)
        variation = random.uniform(0.8, 1.2)
        base = math.floor(base * variation)

        # Bosses get 3-5x multiplier
        if is_boss:
            boss_multiplier = random.uniform(3, 5)
            base = math.floor(base * boss_multiplier)

        return max(1, base)  # Ensure at least 1 copper piece

    def _calculate_party_level_multiplier(self, party_level: int, enemy_level: int) -> float:
        """Calculate loot quality multiplier based on party level vs enemy level."""
        level_diff = party_level - enemy_level
        if level_diff <= -5:
            return 1.5  # Bonus for challenging higher-level enemies
        elif level_diff >= 5:
            return 0.5  # Reduced rewards for farming lower-level enemies
        else:
            return 1.0 + (level_diff * 0.1)  # Small scaling based on level difference

    def _roll_for_items(self, 
                       enemy_type: str, 
                       enemy_level: int, 
                       party_level: int, 
                       is_boss: bool = False) -> List[Tuple[str, int]]:
        """Roll for item drops based on loot tables and conditions."""
        if enemy_type not in self.loot_tables:
            return []

        items = []
        loot_table = self.loot_tables[enemy_type]
        quality_multiplier = self._calculate_party_level_multiplier(party_level, enemy_level)

        for entry in loot_table:
            # Skip boss-only items for non-boss enemies
            if entry.boss_only and not is_boss:
                continue

            # Skip items above level requirement
            if entry.level_requirement > enemy_level:
                continue

            # Adjust drop chance based on conditions
            adjusted_chance = entry.drop_chance * quality_multiplier
            if is_boss:
                adjusted_chance *= 2  # Double drop chance for bosses

            # Roll for item
            if random.random() < adjusted_chance:
                quantity = random.randint(*entry.quantity_range)
                if quantity > 0:
                    items.append((entry.item_id, quantity))

        return items

    def _generate_special_items(self, 
                              enemy_type: str, 
                              enemy_level: int, 
                              is_boss: bool) -> List[str]:
        """Generate special or unique items based on enemy type and conditions."""
        special_items = []
        
        # Example special item generation logic
        if is_boss:
            # Guaranteed special item for bosses
            special_items.append(f"unique_{enemy_type}_drop_{enemy_level}")
            
            # Small chance for additional special item
            if random.random() < 0.1:  # 10% chance
                special_items.append(f"bonus_unique_{enemy_type}_drop_{enemy_level}")

        return special_items

    def generate_loot(self, 
                     enemy_id: str, 
                     enemy_level: int, 
                     party_level: int, 
                     is_boss: bool = False) -> LootResult:
        """Generate loot for a defeated enemy."""
        if enemy_id not in self.enemy_types:
            raise ValueError(f"Unknown enemy ID: {enemy_id}")

        enemy_type = self.enemy_types[enemy_id]
        
        # Generate currency
        base_currency = self._calculate_base_currency(enemy_level, is_boss)
        currency = Currency.from_copper(base_currency)

        # Generate items
        items = self._roll_for_items(enemy_type, enemy_level, party_level, is_boss)

        # Generate special items
        special_items = self._generate_special_items(enemy_type, enemy_level, is_boss)

        return LootResult(
            items=items,
            currency=currency,
            special_items=special_items
        )

    def distribute_group_loot(self, 
                            loot: LootResult, 
                            player_count: int) -> Dict[int, LootResult]:
        """Distribute loot among party members."""
        if player_count <= 0:
            raise ValueError("Player count must be positive")

        # Split currency evenly
        total_copper = loot.currency.total_in_copper()
        copper_per_player = total_copper // player_count
        copper_remainder = total_copper % player_count

        # Create individual shares
        shares = {}
        for player_index in range(player_count):
            # Add base share plus any remainder
            player_copper = copper_per_player
            if player_index < copper_remainder:
                player_copper += 1

            shares[player_index] = LootResult(
                items=[],  # Items will be distributed individually
                currency=Currency.from_copper(player_copper),
                special_items=[]  # Special items need manual distribution
            )

        return shares 
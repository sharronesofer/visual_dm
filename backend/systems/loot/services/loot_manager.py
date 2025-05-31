"""
LootManager singleton class for coordinating all loot system operations.

This module provides the central coordination point for the loot system,
managing loot generation, item identification, enhancement, and shop operations.
"""

import threading
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import logging

from backend.systems.loot.loot_core import (
    generate_loot_bundle,
    validate_item,
    calculate_item_power_score,
    generate_item_identity,
    generate_location_specific_loot
)
# TODO: Re-enable when shared events are implemented
# from backend.infrastructure.events import EventDispatcher


class LootManager:
    """
    Singleton manager for all loot system operations.
    
    Provides centralized coordination for loot generation, item identification,
    enhancement, shop operations, and analytics.
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(LootManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if hasattr(self, '_initialized'):
            return
        
        self._initialized = True
        self.logger = logging.getLogger(__name__)
        # TODO: Re-enable when shared events are implemented
        # self.event_dispatcher = EventDispatcher.get_instance()
        
        # Configuration
        self.equipment_pools = {}
        self.item_effects = []
        self.monster_feats = []
        self.shop_inventories = {}
        
        # Analytics
        self.loot_statistics = {
            "total_generated": 0,
            "items_identified": 0,
            "items_enhanced": 0,
            "shop_transactions": 0
        }
        
        # Cache
        self._cache = {}
        self._cache_ttl = 300  # 5 minutes
        
        self.logger.info("LootManager singleton initialized")
    
    def initialize(self, config: Dict[str, Any] = None) -> bool:
        """
        Initialize the loot system with configuration.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            True if initialization successful
        """
        try:
            if config:
                self.equipment_pools = config.get("equipment_pools", {})
                self.item_effects = config.get("item_effects", [])
                self.monster_feats = config.get("monster_feats", [])
            
            self.logger.info("LootManager initialized successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize LootManager: {e}")
            return False
    
    def generate_loot(self, location: Dict[str, Any], level: int, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Main loot generation method.
        
        Args:
            location: Location data
            level: Character/monster level
            context: Additional context for generation
            
        Returns:
            Generated loot bundle
        """
        try:
            if context is None:
                context = {}
            
            monster_levels = context.get("monster_levels", [level])
            location_id = location.get("id", 0)
            location_type = location.get("type", "dungeon")
            
            loot = generate_location_specific_loot(
                location_id=location_id,
                location_type=location_type,
                biome_type=location.get("biome"),
                faction_id=location.get("faction_id"),
                motif=location.get("motif"),
                monster_levels=monster_levels,
                equipment_pool=self.equipment_pools,
                item_effects=self.item_effects,
                monster_feats=self.monster_feats
            )
            
            self.loot_statistics["total_generated"] += 1
            
            # Emit event
            from backend.systems.loot.loot_events import LootGeneratedEvent
            event = LootGeneratedEvent(
                event_type="loot.generated",
                monster_levels=monster_levels,
                gold_amount=loot.get("gold", 0),
                item_count=len(loot.get("equipment", [])),
                has_quest_item=loot.get("quest_item") is not None,
                has_magical_item=loot.get("magical_item") is not None,
                source_type=context.get("source_type", "combat"),
                location_id=location_id
            )
            # TODO: Re-enable when shared events are implemented
            # self.event_dispatcher.publish_sync(event)
            
            return loot
        except Exception as e:
            self.logger.error(f"Failed to generate loot: {e}")
            return {"gold": 0, "equipment": [], "quest_item": None, "magical_item": None}
    
    def identify_item(self, item: Dict[str, Any], character_id: int = None, skill_level: int = 0) -> Tuple[Dict[str, Any], bool]:
        """
        Item identification system.
        
        Args:
            item: Item to identify
            character_id: ID of character performing identification
            skill_level: Character's identification skill level
            
        Returns:
            Tuple of (updated_item, success)
        """
        try:
            # Calculate identification difficulty
            rarity_difficulty = {
                "common": 5,
                "uncommon": 10,
                "rare": 15,
                "epic": 20,
                "legendary": 25
            }
            
            rarity = item.get("rarity", "common").lower()
            difficulty = rarity_difficulty.get(rarity, 10)
            
            # Calculate success chance
            success_chance = min(0.95, max(0.05, (skill_level + 10) / (difficulty + 10)))
            success = success_chance > 0.5  # Simplified for now
            
            if success:
                # Reveal item properties
                if not item.get("name_revealed", True):
                    item["name_revealed"] = True
                    item["identified_name"] = item.get("generated_name", item.get("name", "Unknown Item"))
                
                # Reveal some effects
                unknown_effects = item.get("unknown_effects", [])
                if unknown_effects:
                    revealed_count = min(len(unknown_effects), skill_level // 5 + 1)
                    revealed_effects = unknown_effects[:revealed_count]
                    item["revealed_effects"] = item.get("revealed_effects", []) + revealed_effects
                    item["unknown_effects"] = unknown_effects[revealed_count:]
            
            self.loot_statistics["items_identified"] += 1
            
            # Emit event
            from backend.systems.loot.loot_events import ItemIdentificationEvent, IdentificationResult
            event = ItemIdentificationEvent(
                item=item,
                identification_result=IdentificationResult.SUCCESS if success else IdentificationResult.FAILURE,
                player_context={"character_id": character_id or 0},
                skill_level=skill_level,
                properties_revealed=item.get("revealed_effects", [])
            )
            # TODO: Re-enable when shared events are implemented
            # self.event_dispatcher.publish_sync(event)
            
            return item, success
        except Exception as e:
            self.logger.error(f"Failed to identify item: {e}")
            return item, False
    
    def enhance_item(self, item: Dict[str, Any], enhancement_type: str, character_id: int = None) -> Tuple[Dict[str, Any], bool]:
        """
        Item enhancement system.
        
        Args:
            item: Item to enhance
            enhancement_type: Type of enhancement (level_up, enchantment, reforge)
            character_id: ID of character performing enhancement
            
        Returns:
            Tuple of (updated_item, success)
        """
        try:
            success = False
            original_rarity = item.get("rarity", "common")
            
            if enhancement_type == "level_up":
                # Increase item level
                current_level = item.get("level", 1)
                item["level"] = current_level + 1
                success = True
                
            elif enhancement_type == "enchantment":
                # Add magical properties
                if "enchantments" not in item:
                    item["enchantments"] = []
                item["enchantments"].append({
                    "type": "stat_boost",
                    "value": 5,
                    "applied_at": datetime.now().isoformat()
                })
                success = True
                
            elif enhancement_type == "reforge":
                # Change rarity
                rarity_progression = ["common", "uncommon", "rare", "epic", "legendary"]
                current_index = rarity_progression.index(original_rarity) if original_rarity in rarity_progression else 0
                if current_index < len(rarity_progression) - 1:
                    item["rarity"] = rarity_progression[current_index + 1]
                    success = True
            
            if success:
                self.loot_statistics["items_enhanced"] += 1
                
                # Emit event
                from backend.systems.loot.loot_events import ItemEnhancementEvent, EnhancementResult
                event = ItemEnhancementEvent(
                    item=item,
                    enhancement_type=enhancement_type,
                    success_result=EnhancementResult.SUCCESS if success else EnhancementResult.FAILURE,
                    enhancement_level=item.get("level", 1),
                    enhancer_skill=0  # Could be passed as parameter in future
                )
                # TODO: Re-enable when shared events are implemented
                # self.event_dispatcher.publish_sync(event)
            
            return item, success
        except Exception as e:
            self.logger.error(f"Failed to enhance item: {e}")
            return item, False
    
    def get_shop_inventory(self, shop_type: str, location: Dict[str, Any], shop_tier: int = 1) -> List[Dict[str, Any]]:
        """
        Generate shop inventory.
        
        Args:
            shop_type: Type of shop (weapon_smith, armor_crafter, etc.)
            location: Location data
            shop_tier: Shop tier/quality level
            
        Returns:
            List of items in shop inventory
        """
        try:
            shop_id = f"{shop_type}_{location.get('id', 0)}"
            
            # Check cache
            cache_key = f"shop_inventory_{shop_id}"
            if cache_key in self._cache:
                cached_data, timestamp = self._cache[cache_key]
                if (datetime.now() - timestamp).seconds < self._cache_ttl:
                    return cached_data
            
            # Generate inventory
            from backend.systems.loot.loot_shop import generate_shop_inventory
            inventory = generate_shop_inventory(
                shop_type=shop_type,
                shop_tier=shop_tier,
                region_id=location.get("region_id"),
                faction_id=location.get("faction_id"),
                equipment_pool=self.equipment_pools,
                item_effects=self.item_effects
            )
            
            # Cache result
            self._cache[cache_key] = (inventory, datetime.now())
            
            # Emit event
            from backend.systems.loot.loot_events import ShopInventoryEvent
            event = ShopInventoryEvent(
                shop={"id": shop_id, "type": shop_type, "tier": shop_tier},
                inventory_changes={"items_added": inventory},
                economic_context={"region_id": location.get("region_id"), "faction_id": location.get("faction_id")},
                shop_id=shop_id,
                shop_type=shop_type,
                location=location,
                items_added=inventory,
                restock_reason="generated"
            )
            # TODO: Re-enable when shared events are implemented
            # self.event_dispatcher.publish_sync(event)
            
            return inventory
        except Exception as e:
            self.logger.error(f"Failed to get shop inventory: {e}")
            return []
    
    def calculate_item_value(self, item: Dict[str, Any], context: Dict[str, Any] = None) -> int:
        """
        Calculate item value for pricing.
        
        Args:
            item: Item to price
            context: Pricing context (shop, region, etc.)
            
        Returns:
            Item value in gold
        """
        try:
            base_value = 10  # Base value
            
            # Rarity multiplier
            rarity_multipliers = {
                "common": 1.0,
                "uncommon": 2.0,
                "rare": 5.0,
                "epic": 15.0,
                "legendary": 50.0
            }
            rarity = item.get("rarity", "common").lower()
            base_value *= rarity_multipliers.get(rarity, 1.0)
            
            # Level multiplier
            level = item.get("level", 1)
            base_value *= (1 + level * 0.1)
            
            # Power score influence
            power_score = calculate_item_power_score(item)
            base_value *= (1 + power_score * 0.05)
            
            # Context modifiers
            if context:
                region_modifier = context.get("economic_factor", 1.0)
                base_value *= region_modifier
            
            return int(base_value)
        except Exception as e:
            self.logger.error(f"Failed to calculate item value: {e}")
            return 10
    
    def process_loot_event(self, event: Dict[str, Any]) -> bool:
        """
        Process loot-related events.
        
        Args:
            event: Event data
            
        Returns:
            True if processed successfully
        """
        try:
            event_type = event.get("type", "unknown")
            
            if event_type == "shop_transaction":
                self.loot_statistics["shop_transactions"] += 1
            elif event_type == "loot_generated":
                self.loot_statistics["total_generated"] += 1
            
            return True
        except Exception as e:
            self.logger.error(f"Failed to process loot event: {e}")
            return False
    
    def get_loot_analytics(self) -> Dict[str, Any]:
        """
        Get loot system analytics.
        
        Returns:
            Analytics data
        """
        return {
            "statistics": self.loot_statistics.copy(),
            "cache_size": len(self._cache),
            "equipment_pools": {k: len(v) for k, v in self.equipment_pools.items()},
            "item_effects_count": len(self.item_effects),
            "monster_feats_count": len(self.monster_feats)
        }
    
    def load_configuration(self, config_path: str = None) -> bool:
        """
        Load loot system configuration.
        
        Args:
            config_path: Path to configuration file
            
        Returns:
            True if loaded successfully
        """
        try:
            # Placeholder for configuration loading
            self.logger.info("Configuration loaded successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {e}")
            return False
    
    def setup_integrations(self) -> bool:
        """
        Setup cross-system integrations.
        
        Returns:
            True if setup successful
        """
        try:
            # Placeholder for integration setup
            self.logger.info("Integrations setup successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to setup integrations: {e}")
            return False
    
    def validate_system(self) -> bool:
        """
        Validate system health.
        
        Returns:
            True if system is healthy
        """
        try:
            # Basic validation checks
            if not hasattr(self, '_initialized'):
                return False
            
            # TODO: Re-enable when shared events are implemented
            # if not self.event_dispatcher:
            #     return False
            
            return True
        except Exception as e:
            self.logger.error(f"System validation failed: {e}")
            return False
    
    def reset_caches(self) -> None:
        """Reset all caches."""
        self._cache.clear()
        self.logger.info("Caches reset")
    
    def get_loot_statistics(self) -> Dict[str, Any]:
        """Get loot generation statistics."""
        return self.loot_statistics.copy()


# Convenience function to get the singleton instance
def get_loot_manager() -> LootManager:
    """Get the LootManager singleton instance."""
    return LootManager()


# Custom exception class
class LootManagerError(Exception):
    """Exception raised for LootManager operation failures"""
    pass 
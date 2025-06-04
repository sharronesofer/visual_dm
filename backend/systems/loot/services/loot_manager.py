"""
Loot Manager - Pure Business Logic

This module provides the central business logic coordinator for the loot system,
managing loot generation, item identification, enhancement, and shop operations
without technical dependencies.
"""

from typing import Dict, List, Any, Optional, Tuple, Protocol
from datetime import datetime

from backend.systems.loot.utils.loot_core import (
    generate_loot_bundle,
    validate_item,
    calculate_item_power_score,
    generate_item_identity,
    generate_location_specific_loot
)


# Business Logic Protocols
class LootEventPublisher(Protocol):
    """Protocol for publishing loot-related events"""
    
    def publish_loot_generated_event(self, event_data: Dict[str, Any]) -> None:
        """Publish loot generation event"""
        ...
    
    def publish_item_identification_event(self, event_data: Dict[str, Any]) -> None:
        """Publish item identification event"""
        ...
    
    def publish_item_enhancement_event(self, event_data: Dict[str, Any]) -> None:
        """Publish item enhancement event"""
        ...


class LootConfigProvider(Protocol):
    """Protocol for loot configuration access"""
    
    def get_equipment_pools(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get equipment pools for generation"""
        ...
    
    def get_item_effects(self) -> List[Dict[str, Any]]:
        """Get available item effects"""
        ...
    
    def get_monster_abilities(self) -> List[Dict[str, Any]]:
        """Get monster abilities for legendary items"""
        ...
    
    def get_shop_inventories(self) -> Dict[str, Any]:
        """Get shop inventory configurations"""
        ...


class LootBusinessManager:
    """
    Business logic manager for all loot system operations.
    
    Provides centralized coordination for loot generation, item identification,
    enhancement, shop operations, and analytics using pure business logic.
    """
    
    def __init__(self, 
                 config_provider: LootConfigProvider,
                 event_publisher: Optional[LootEventPublisher] = None):
        """
        Initialize the loot business manager.
        
        Args:
            config_provider: Provider for loot configuration
            event_publisher: Optional event publisher for notifications
        """
        self.config_provider = config_provider
        self.event_publisher = event_publisher
        
        # Analytics tracking
        self.loot_statistics = {
            "total_generated": 0,
            "items_identified": 0,
            "items_enhanced": 0,
            "shop_transactions": 0
        }
    
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
        if context is None:
            context = {}
        
        monster_levels = context.get("monster_levels", [level])
        location_id = location.get("id", 0)
        location_type = location.get("type", "dungeon")
        
        # Get configuration from provider
        equipment_pools = self.config_provider.get_equipment_pools()
        item_effects = self.config_provider.get_item_effects()
        monster_abilities = self.config_provider.get_monster_abilities()
        
        loot = generate_location_specific_loot(
            location_id=location_id,
            location_type=location_type,
            biome_type=location.get("biome"),
            faction_id=location.get("faction_id"),
            motif=location.get("motif"),
            monster_levels=monster_levels,
            equipment_pool=equipment_pools,
            item_effects=item_effects,
            monster_abilities=monster_abilities
        )
        
        self.loot_statistics["total_generated"] += 1
        
        # Publish event if publisher available
        if self.event_publisher:
            event_data = {
                "event_type": "loot.generated",
                "monster_levels": monster_levels,
                "gold_amount": loot.get("gold", 0),
                "item_count": len(loot.get("equipment", [])),
                "has_quest_item": loot.get("quest_item") is not None,
                "has_magical_item": loot.get("magical_item") is not None,
                "source_type": context.get("source_type", "combat"),
                "location_id": location_id
            }
            self.event_publisher.publish_loot_generated_event(event_data)
        
        return loot
    
    def identify_item(self, 
                     item: Dict[str, Any], 
                     character_id: int = None, 
                     skill_level: int = 0, 
                     character_level: int = 1, 
                     method: str = "skill_check", 
                     **kwargs) -> Tuple[Dict[str, Any], bool]:
        """
        Item identification system using business logic.
        
        Args:
            item: Item to identify
            character_id: ID of character performing identification
            skill_level: Character's identification skill level
            character_level: Character's level
            method: Identification method to use
            **kwargs: Additional parameters based on method
            
        Returns:
            Tuple of (updated_item, success)
        """
        # Basic business logic for identification
        success = False
        updated_item = item.copy()
        
        # Determine success based on business rules
        rarity = item.get("rarity", "common").lower()
        
        if method == "auto_level":
            # Auto-identification based on character level
            auto_identify_levels = {
                "common": 1,
                "uncommon": 5,
                "rare": 15,
                "epic": 25,
                "legendary": 40
            }
            required_level = auto_identify_levels.get(rarity, 1)
            success = character_level >= required_level
        
        elif method == "skill_check":
            # Skill-based identification
            difficulty_modifiers = {
                "common": 0,
                "uncommon": 5,
                "rare": 10,
                "epic": 15,
                "legendary": 20
            }
            difficulty = difficulty_modifiers.get(rarity, 0)
            success = skill_level >= difficulty
        
        elif method == "shop_payment":
            # Always succeeds if payment is made
            success = kwargs.get("payment_amount", 0) > 0
        
        elif method == "magic":
            # Magical identification has high success rate
            success = True
        
        if success:
            # Apply identification results
            updated_item["identified"] = True
            updated_item["name_revealed"] = True
            updated_item["identified_name"] = updated_item.get("generated_name", updated_item.get("name"))
            
            # Reveal properties based on success level
            if "unknown_effects" in updated_item:
                updated_item["effects"] = updated_item.pop("unknown_effects")
            
            self.loot_statistics["items_identified"] += 1
            
            # Publish event if publisher available
            if self.event_publisher:
                event_data = {
                    "event_type": "item.identified",
                    "item_id": updated_item.get("id"),
                    "item_name": updated_item.get("name"),
                    "method": method,
                    "character_id": character_id,
                    "skill_level": skill_level,
                    "success": success
                }
                self.event_publisher.publish_item_identification_event(event_data)
        
        return updated_item, success
    
    def enhance_item(self, 
                    item: Dict[str, Any], 
                    enhancement_type: str, 
                    character_id: int = None) -> Tuple[Dict[str, Any], bool]:
        """
        Item enhancement system using business logic.
        
        Args:
            item: Item to enhance
            enhancement_type: Type of enhancement
            character_id: ID of character performing enhancement
            
        Returns:
            Tuple of (updated_item, success)
        """
        success = False
        updated_item = item.copy()
        
        # Business logic for enhancement
        current_enhancement = item.get("enhancement_level", 0)
        max_enhancement = 10  # Business rule: max enhancement level
        
        if current_enhancement < max_enhancement:
            # Calculate success rate based on current level
            success_rate = max(0.1, 1.0 - (current_enhancement * 0.1))
            
            # Simulate enhancement attempt (in real system would use proper RNG)
            import random
            success = random.random() < success_rate
            
            if success:
                updated_item["enhancement_level"] = current_enhancement + 1
                
                # Apply enhancement effects based on business rules
                if enhancement_type == "damage":
                    damage_bonus = updated_item.get("damage_bonus", 0) + 1
                    updated_item["damage_bonus"] = damage_bonus
                elif enhancement_type == "defense":
                    defense_bonus = updated_item.get("defense_bonus", 0) + 1
                    updated_item["defense_bonus"] = defense_bonus
                
                self.loot_statistics["items_enhanced"] += 1
                
                # Publish event if publisher available
                if self.event_publisher:
                    event_data = {
                        "event_type": "item.enhanced",
                        "item_id": updated_item.get("id"),
                        "item_name": updated_item.get("name"),
                        "enhancement_type": enhancement_type,
                        "new_level": updated_item["enhancement_level"],
                        "character_id": character_id,
                        "success": success
                    }
                    self.event_publisher.publish_item_enhancement_event(event_data)
        
        return updated_item, success
    
    def get_shop_inventory(self, 
                          shop_type: str, 
                          location: Dict[str, Any], 
                          shop_tier: int = 1) -> List[Dict[str, Any]]:
        """
        Generate shop inventory using business logic.
        
        Args:
            shop_type: Type of shop
            location: Location data
            shop_tier: Quality tier of the shop
            
        Returns:
            List of items available in the shop
        """
        # Get shop configurations
        shop_inventories = self.config_provider.get_shop_inventories()
        shop_config = shop_inventories.get(shop_type, {})
        
        # Business logic for inventory generation
        inventory = []
        base_item_count = shop_config.get("base_item_count", 10)
        item_count = base_item_count + (shop_tier - 1) * 2
        
        # Get equipment pools for inventory
        equipment_pools = self.config_provider.get_equipment_pools()
        
        for _ in range(item_count):
            # Select random item type based on shop specialization
            if shop_type == "weapon_shop" and "weapon" in equipment_pools:
                items = equipment_pools["weapon"]
            elif shop_type == "armor_shop" and "armor" in equipment_pools:
                items = equipment_pools["armor"]
            elif shop_type == "general_store":
                # Mix of all types
                all_items = []
                for category_items in equipment_pools.values():
                    all_items.extend(category_items)
                items = all_items
            else:
                items = equipment_pools.get("gear", [])
            
            if items:
                import random
                base_item = random.choice(items).copy()
                
                # Apply shop tier modifiers
                if shop_tier > 1:
                    # Higher tier shops have better quality items
                    quality_bonus = (shop_tier - 1) * 0.1
                    if "value" in base_item:
                        base_item["value"] = int(base_item["value"] * (1 + quality_bonus))
                
                inventory.append(base_item)
        
        return inventory
    
    def calculate_item_value(self, item: Dict[str, Any], context: Dict[str, Any] = None) -> int:
        """
        Calculate item value using business logic.
        
        Args:
            item: Item to calculate value for
            context: Additional context for calculation
            
        Returns:
            Calculated item value
        """
        base_value = item.get("value", 1)
        
        # Apply business logic modifiers
        rarity_multipliers = {
            "common": 1.0,
            "uncommon": 2.0,
            "rare": 5.0,
            "epic": 15.0,
            "legendary": 50.0
        }
        
        rarity = item.get("rarity", "common").lower()
        rarity_multiplier = rarity_multipliers.get(rarity, 1.0)
        
        # Enhancement bonus
        enhancement_level = item.get("enhancement_level", 0)
        enhancement_multiplier = 1.0 + (enhancement_level * 0.2)
        
        # Condition modifier
        condition = item.get("condition", 100)  # 0-100 scale
        condition_multiplier = condition / 100.0
        
        final_value = int(base_value * rarity_multiplier * enhancement_multiplier * condition_multiplier)
        return max(1, final_value)
    
    def get_loot_analytics(self) -> Dict[str, Any]:
        """
        Get loot system analytics.
        
        Returns:
            Analytics data
        """
        return {
            "statistics": self.loot_statistics.copy(),
            "timestamp": datetime.utcnow().isoformat(),
            "system_status": "operational"
        }
    
    def validate_system(self) -> bool:
        """
        Validate that the loot system is properly configured.
        
        Returns:
            True if system is valid
        """
        try:
            equipment_pools = self.config_provider.get_equipment_pools()
            item_effects = self.config_provider.get_item_effects()
            
            # Basic validation
            if not equipment_pools:
                return False
            
            if not item_effects:
                return False
            
            return True
        except Exception:
            return False


def create_loot_business_manager(
    config_provider: LootConfigProvider,
    event_publisher: Optional[LootEventPublisher] = None
) -> LootBusinessManager:
    """Factory function to create loot business manager"""
    return LootBusinessManager(config_provider, event_publisher) 
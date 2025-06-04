"""
Tiered Item Identification System - Pure Business Logic

This module implements the tiered access approach for item identification,
providing different methods and requirements based on item rarity.
Pure business logic with no technical dependencies.

Key Features:
- Common/Uncommon: Easy identification via multiple methods
- Rare+: Requires skill investment OR expensive services
- Epic/Legendary: Requires specialization AND resources
- Progressive revelation based on skill level and method used
"""

from typing import Dict, List, Any, Tuple, Optional, Protocol
import random
from enum import Enum
from datetime import datetime

from backend.systems.loot.utils.config_loader import config_loader


class IdentificationMethod(Enum):
    """Available identification methods"""
    AUTO_LEVEL = "auto_level"
    SHOP_PAYMENT = "shop_payment"
    SKILL_CHECK = "skill_check" 
    MAGIC = "magic"
    SPECIAL_NPC = "special_npc"
    QUEST_COMPLETION = "quest_completion"


class IdentificationResult(Enum):
    """Identification attempt results"""
    SUCCESS = "success"
    PARTIAL_SUCCESS = "partial_success"
    FAILURE = "failure"
    INSUFFICIENT_SKILL = "insufficient_skill"
    INSUFFICIENT_PAYMENT = "insufficient_payment"
    METHOD_UNAVAILABLE = "method_unavailable"
    REQUIRES_SPECIALIZATION = "requires_specialization"


class IdentificationLevel(Enum):
    """Progressive revelation levels"""
    LEVEL_1 = 1  # Basic name and category
    LEVEL_2 = 2  # Stats and requirements
    LEVEL_3 = 3  # Enchantments and special properties
    LEVEL_4 = 4  # Lore and history
    LEVEL_5 = 5  # True name and full power


# Business Logic Protocols
class IdentificationEventPublisher(Protocol):
    """Protocol for publishing identification events"""
    
    def publish_identification_event(self, event_data: Dict[str, Any]) -> None:
        """Publish identification event"""
        ...


class EconomicCalculator(Protocol):
    """Protocol for economic price calculations"""
    
    def apply_economic_factors_to_price(self, cost: int, region_id: int, item_name: str) -> int:
        """Apply economic factors to identification cost"""
        ...


class TieredIdentificationSystem:
    """
    Implements the tiered access approach for item identification.
    
    This system provides different identification paths based on item rarity:
    - Common/Uncommon: Multiple easy methods available
    - Rare: Requires skill OR payment
    - Epic: Requires high skill AND/OR expensive services
    - Legendary: Requires specialization and rare resources
    
    Pure business logic with dependency injection for technical concerns.
    """
    
    def __init__(self, 
                 event_publisher: Optional[IdentificationEventPublisher] = None,
                 economic_calculator: Optional[EconomicCalculator] = None):
        self.config = config_loader.get_rarity_config()
        self.identification_rules = self.config.get("identification_rules", {})
        self.event_publisher = event_publisher
        self.economic_calculator = economic_calculator
        
    def can_identify_automatically(self, item: Dict[str, Any], character_level: int) -> Tuple[bool, str]:
        """
        Check if an item can be automatically identified based on character level.
        
        Args:
            item: Item to check
            character_level: Character's current level
            
        Returns:
            Tuple of (can_identify, reason)
        """
        rarity = item.get("rarity", "common").lower()
        rules = self.identification_rules.get(rarity, {})
        
        auto_level = rules.get("auto_identify_level")
        if auto_level is None:
            return False, f"{rarity.title()} items cannot be auto-identified"
            
        if character_level >= auto_level:
            return True, f"Auto-identified at character level {character_level}"
        else:
            return False, f"Requires character level {auto_level} for auto-identification"
    
    def calculate_shop_identification_cost(
        self, 
        item: Dict[str, Any], 
        character_skill: int = 0,
        shop_tier: int = 1,
        region_id: Optional[int] = None
    ) -> Tuple[int, bool, str]:
        """
        Calculate the cost to identify an item at a shop.
        
        Args:
            item: Item to identify
            character_skill: Character's identification skill level
            shop_tier: Quality tier of the shop (1-5)
            region_id: Region for economic factors
            
        Returns:
            Tuple of (cost, available, reason)
        """
        rarity = item.get("rarity", "common").lower()
        rules = self.identification_rules.get(rarity, {})
        
        # Check if shop identification is available for this rarity
        methods_available = rules.get("methods_available", [])
        if "shop_payment" not in methods_available:
            return 0, False, f"{rarity.title()} items cannot be identified at shops"
        
        # Check special requirements
        if rules.get("shop_service_requires_quest"):
            return 0, False, "Requires quest completion to access shop identification"
            
        if rules.get("shop_service_requires_skill", 0) > character_skill:
            required_skill = rules.get("shop_service_requires_skill", 0)
            return 0, False, f"Shop requires {required_skill} identification skill"
        
        # Calculate base cost
        base_cost = rules.get("shop_cost_base", 50)
        
        # Apply shop tier modifier
        tier_multiplier = 1.0 - ((shop_tier - 1) * 0.1)  # Better shops charge less
        cost = int(base_cost * tier_multiplier)
        
        # Apply skill discount for high-tier items
        skill_threshold = rules.get("skill_threshold_for_discount", 0)
        if character_skill >= skill_threshold:
            cost = int(cost * 0.7)  # 30% discount for skilled identifiers
        
        # Apply regional economic factors via dependency injection
        if region_id and self.economic_calculator:
            try:
                cost = self.economic_calculator.apply_economic_factors_to_price(
                    cost, region_id, item.get("name", "Unknown Item")
                )
            except Exception:
                # Fallback to original cost if economic calculation fails
                pass
        
        return cost, True, f"Shop identification available for {cost} gold"
    
    def attempt_skill_identification(
        self,
        item: Dict[str, Any],
        character_skill: int,
        character_level: int = 1,
        use_tools: bool = False,
        tool_bonus: int = 0
    ) -> Tuple[IdentificationResult, Dict[str, Any], str]:
        """
        Attempt to identify an item using character skills.
        
        Args:
            item: Item to identify
            character_skill: Character's identification skill level
            character_level: Character's level
            use_tools: Whether using identification tools
            tool_bonus: Bonus from identification tools
            
        Returns:
            Tuple of (result, revealed_info, message)
        """
        rarity = item.get("rarity", "common").lower()
        rules = self.identification_rules.get(rarity, {})
        
        # Check if skill identification is available
        methods_available = rules.get("methods_available", [])
        if "skill_check" not in methods_available:
            return IdentificationResult.METHOD_UNAVAILABLE, {}, f"{rarity.title()} items cannot be identified via skills"
        
        # Check minimum skill requirements
        min_skill = rules.get("minimum_skill_for_attempt", 0)
        if character_skill < min_skill:
            return IdentificationResult.INSUFFICIENT_SKILL, {}, f"Requires {min_skill} identification skill"
        
        # Determine what can be revealed based on progressive revelation
        progressive_rules = rules.get("progressive_revelation", {})
        revealed_info = {}
        highest_level_achieved = 0
        
        total_skill = character_skill + (tool_bonus if use_tools else 0)
        
        for level_key, level_rules in progressive_rules.items():
            required_skill = level_rules.get("required_skill", 0)
            required_level = level_rules.get("required_level")
            
            # Check if requirements are met
            skill_met = total_skill >= required_skill
            level_met = required_level is None or character_level >= required_level
            
            if skill_met and level_met:
                reveals = level_rules.get("reveals", [])
                for reveal in reveals:
                    revealed_info[reveal] = True
                
                highest_level_achieved = max(highest_level_achieved, int(level_key.split('_')[1]))
        
        if highest_level_achieved > 0:
            result = IdentificationResult.SUCCESS if highest_level_achieved >= 3 else IdentificationResult.PARTIAL_SUCCESS
            message = f"Identified at level {highest_level_achieved}"
        else:
            result = IdentificationResult.FAILURE
            message = "Identification failed - insufficient skill"
        
        return result, revealed_info, message
    
    def identify_item_comprehensive(
        self,
        item: Dict[str, Any],
        method: IdentificationMethod,
        character_id: int,
        character_level: int = 1,
        character_skill: int = 0,
        payment_amount: int = 0,
        shop_tier: int = 1,
        region_id: Optional[int] = None,
        special_components: Optional[List[str]] = None
    ) -> Tuple[Dict[str, Any], IdentificationResult, str]:
        """
        Comprehensive item identification using the specified method.
        
        Args:
            item: Item to identify
            method: Method to use for identification
            character_id: ID of character performing identification
            character_level: Character's level
            character_skill: Character's identification skill
            payment_amount: Amount paid (for shop method)
            shop_tier: Shop quality tier (for shop method)
            region_id: Region ID (for economic factors)
            special_components: Special components (for magic method)
            
        Returns:
            Tuple of (updated_item, result, message)
        """
        updated_item = item.copy()
        
        if method == IdentificationMethod.AUTO_LEVEL:
            can_identify, reason = self.can_identify_automatically(item, character_level)
            if can_identify:
                updated_item = self._apply_auto_identification(updated_item, character_level)
                result = IdentificationResult.SUCCESS
                message = reason
            else:
                result = IdentificationResult.INSUFFICIENT_SKILL
                message = reason
        
        elif method == IdentificationMethod.SHOP_PAYMENT:
            cost, available, reason = self.calculate_shop_identification_cost(
                item, character_skill, shop_tier, region_id
            )
            if available and payment_amount >= cost:
                updated_item = self._apply_shop_identification(updated_item, shop_tier)
                result = IdentificationResult.SUCCESS
                message = f"Successfully identified at shop for {cost} gold"
            else:
                result = IdentificationResult.INSUFFICIENT_PAYMENT if available else IdentificationResult.METHOD_UNAVAILABLE
                message = reason if not available else f"Requires {cost} gold (paid {payment_amount})"
        
        elif method == IdentificationMethod.SKILL_CHECK:
            result, revealed_info, message = self.attempt_skill_identification(
                item, character_skill, character_level
            )
            if result in [IdentificationResult.SUCCESS, IdentificationResult.PARTIAL_SUCCESS]:
                updated_item = self._apply_skill_identification(updated_item, revealed_info, character_skill)
        
        elif method == IdentificationMethod.MAGIC:
            result, updated_item, message = self._attempt_magical_identification(
                updated_item, character_skill, special_components or []
            )
        
        else:
            result = IdentificationResult.METHOD_UNAVAILABLE
            message = f"Method {method.value} not implemented"
        
        # Publish event if publisher available
        if self.event_publisher:
            event_data = {
                "event_type": "item.identified",
                "item_id": str(item.get("id", 0)),
                "item_name": item.get("name", "Unknown Item"),
                "item_rarity": item.get("rarity", "common"),
                "identification_method": method.value,
                "identification_result": result.value,
                "identification_level": updated_item.get("identification_level", 0),
                "character_id": character_id,
                "skill_level": character_skill,
                "cost_paid": payment_amount,
                "properties_revealed": self._get_revealed_properties(updated_item),
                "timestamp": datetime.utcnow().isoformat()
            }
            self.event_publisher.publish_identification_event(event_data)
        
        return updated_item, result, message
    
    def _apply_auto_identification(self, item: Dict[str, Any], character_level: int) -> Dict[str, Any]:
        """Apply automatic identification based on character level."""
        item["identified"] = True
        item["identification_method"] = "auto_level"
        item["identification_level"] = 2  # Basic identification
        item["name_revealed"] = True
        item["category_revealed"] = True
        item["stats_revealed"] = True
        
        if "generated_name" in item:
            item["revealed_name"] = item["generated_name"]
        
        return item
    
    def _apply_shop_identification(self, item: Dict[str, Any], shop_tier: int) -> Dict[str, Any]:
        """Apply shop-based identification."""
        item["identified"] = True
        item["identification_method"] = "shop_payment"
        
        # Shop tier affects identification quality
        identification_level = min(4, 2 + shop_tier)  # Level 2-5 based on shop tier
        item["identification_level"] = identification_level
        
        # Reveal properties based on shop quality
        item["name_revealed"] = True
        item["category_revealed"] = True
        item["stats_revealed"] = True
        item["requirements_revealed"] = True
        
        if shop_tier >= 3:
            item["enchantments_revealed"] = True
        if shop_tier >= 4:
            item["special_properties_revealed"] = True
        if shop_tier >= 5:
            item["lore_revealed"] = True
        
        return item
    
    def _apply_skill_identification(
        self, 
        item: Dict[str, Any], 
        revealed_info: Dict[str, Any], 
        skill_level: int
    ) -> Dict[str, Any]:
        """Apply skill-based identification results."""
        item["identified"] = True
        item["identification_method"] = "skill_check"
        item["identification_level"] = len(revealed_info)
        
        # Apply revealed properties
        for property_name, revealed in revealed_info.items():
            if revealed:
                item[f"{property_name}_revealed"] = True
        
        return item
    
    def _attempt_magical_identification(
        self,
        item: Dict[str, Any],
        character_skill: int,
        special_components: List[str]
    ) -> Tuple[IdentificationResult, Dict[str, Any], str]:
        """Attempt magical identification."""
        rarity = item.get("rarity", "common").lower()
        rules = self.identification_rules.get(rarity, {})
        
        # Check if magical identification is available
        methods_available = rules.get("methods_available", [])
        if "magic" not in methods_available:
            return IdentificationResult.METHOD_UNAVAILABLE, item, f"{rarity.title()} items cannot be magically identified"
        
        # Magical identification can reveal more than normal methods
        # but requires special components for higher tier items
        if rarity in ["epic", "legendary"] and not special_components:
            return IdentificationResult.INSUFFICIENT_PAYMENT, item, "Requires magical components"
        
        # Magical identification success is based on character skill and components
        base_chance = 0.8
        skill_bonus = character_skill * 0.02
        component_bonus = len(special_components) * 0.1
        
        success_chance = min(0.95, base_chance + skill_bonus + component_bonus)
        
        if random.random() < success_chance:
            # Magical identification reveals all properties
            progressive_rules = rules.get("progressive_revelation", {})
            for level_key, level_rules in progressive_rules.items():
                reveals = level_rules.get("reveals", [])
                item = self._reveal_item_properties(item, reveals)
            
            item["identification_level"] = len(progressive_rules)
            item["identification_method"] = "magic"
            item["magical_components_used"] = special_components
            
            return IdentificationResult.SUCCESS, item, "Magically identified completely"
        else:
            return IdentificationResult.FAILURE, item, "Magical identification failed"
    
    def _reveal_item_properties(self, item: Dict[str, Any], reveals: List[str]) -> Dict[str, Any]:
        """Reveal specific item properties."""
        if "name" in reveals:
            item["name_revealed"] = True
            if "generated_name" in item:
                item["revealed_name"] = item["generated_name"]
        
        if "category" in reveals:
            item["category_revealed"] = True
        
        if "basic_stats" in reveals:
            item["stats_revealed"] = True
        
        if "requirements" in reveals:
            item["requirements_revealed"] = True
        
        if "enchantments" in reveals:
            item["enchantments_revealed"] = True
            # Reveal hidden effects
            if "unknown_effects" in item:
                item["revealed_effects"] = item.get("revealed_effects", []) + item.get("unknown_effects", [])
                item["unknown_effects"] = []
        
        if "special_properties" in reveals:
            item["special_properties_revealed"] = True
        
        if "lore" in reveals:
            item["lore_revealed"] = True
        
        if "history" in reveals:
            item["history_revealed"] = True
        
        if "hidden_abilities" in reveals:
            item["hidden_abilities_revealed"] = True
        
        if "true_name" in reveals:
            item["true_name_revealed"] = True
        
        if "full_power" in reveals:
            item["full_power_revealed"] = True
        
        if "awakened_abilities" in reveals:
            item["awakened_abilities_revealed"] = True
        
        return item
    
    def _get_revealed_properties(self, item: Dict[str, Any]) -> List[str]:
        """Get list of revealed properties for event logging."""
        revealed = []
        
        if item.get("name_revealed"):
            revealed.append("name")
        if item.get("category_revealed"):
            revealed.append("category")
        if item.get("stats_revealed"):
            revealed.append("stats")
        if item.get("requirements_revealed"):
            revealed.append("requirements")
        if item.get("enchantments_revealed"):
            revealed.append("enchantments")
        if item.get("special_properties_revealed"):
            revealed.append("special_properties")
        if item.get("lore_revealed"):
            revealed.append("lore")
        if item.get("history_revealed"):
            revealed.append("history")
        if item.get("hidden_abilities_revealed"):
            revealed.append("hidden_abilities")
        if item.get("true_name_revealed"):
            revealed.append("true_name")
        if item.get("full_power_revealed"):
            revealed.append("full_power")
        if item.get("awakened_abilities_revealed"):
            revealed.append("awakened_abilities")
        
        return revealed


# Convenience functions for backwards compatibility
def identify_item_by_skill(
    item: Dict[str, Any],
    character_id: int,
    skill_level: int,
    character_level: int = 1
) -> Tuple[Dict[str, Any], bool, str]:
    """
    Identify an item using character skills (backwards compatible).
    
    Returns:
        Tuple of (updated_item, success, message)
    """
    system = TieredIdentificationSystem()
    updated_item, result, message = system.identify_item_comprehensive(
        item=item,
        method=IdentificationMethod.SKILL_CHECK,
        character_id=character_id,
        character_level=character_level,
        character_skill=skill_level
    )
    
    success = result in [IdentificationResult.SUCCESS, IdentificationResult.PARTIAL_SUCCESS]
    return updated_item, success, message


def identify_item_at_shop(
    item: Dict[str, Any],
    character_id: int,
    payment_amount: int,
    shop_tier: int = 1,
    region_id: Optional[int] = None
) -> Tuple[Dict[str, Any], bool, str]:
    """
    Identify an item at a shop (backwards compatible).
    
    Returns:
        Tuple of (updated_item, success, message)
    """
    system = TieredIdentificationSystem()
    updated_item, result, message = system.identify_item_comprehensive(
        item=item,
        method=IdentificationMethod.SHOP_PAYMENT,
        character_id=character_id,
        payment_amount=payment_amount,
        shop_tier=shop_tier,
        region_id=region_id
    )
    
    success = result == IdentificationResult.SUCCESS
    return updated_item, success, message


def can_auto_identify(item: Dict[str, Any], character_level: int) -> bool:
    """
    Check if an item can be auto-identified at the character's level.
    
    Returns:
        True if auto-identification is possible
    """
    system = TieredIdentificationSystem()
    can_identify, _ = system.can_identify_automatically(item, character_level)
    return can_identify 
"""
Enchanting system models for Visual DM equipment system.

Implements the learn-by-disenchanting system where players must sacrifice items
to learn enchantments, with progression through rarity tiers and integration
with the Arcane Manipulation ability system.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Set
from uuid import UUID, uuid4

class EnchantmentRarity(Enum):
    """Enchantment rarity levels that determine learning requirements and power."""
    BASIC = "basic"          # Learn from Basic quality items
    MILITARY = "military"    # Learn from Military quality items
    MASTERCRAFT = "mastercraft"     # Learn from Mastercraft quality items
    LEGENDARY = "legendary"   # Learn from Legendary quality items

class EnchantmentSchool(Enum):
    """Schools of enchantment that categorize different types of magical effects."""
    PROTECTION = "protection"     # Defensive enchantments
    ENHANCEMENT = "enhancement"   # Stat and ability boosts
    ELEMENTAL = "elemental"      # Fire, ice, lightning effects
    UTILITY = "utility"          # Convenience and quality-of-life effects
    COMBAT = "combat"            # Offensive enchantments
    RESTORATION = "restoration"   # Healing and repair effects

class DisenchantmentOutcome(Enum):
    """Possible outcomes when disenchanting an item."""
    SUCCESS_LEARNED = "success_learned"        # Successfully learned enchantment
    SUCCESS_KNOWN = "success_known"           # Already known, item still destroyed
    PARTIAL_SUCCESS = "partial_success"       # Learned weaker version
    FAILURE_SAFE = "failure_safe"            # Failed but item preserved
    FAILURE_DESTROYED = "failure_destroyed"   # Failed and item destroyed
    CRITICAL_FAILURE = "critical_failure"    # Failed with additional consequences

@dataclass
class EnchantmentDefinition:
    """Defines an enchantment that can be learned and applied to equipment."""
    # Required fields first
    id: str
    name: str
    description: str
    rarity: EnchantmentRarity
    school: EnchantmentSchool
    min_arcane_manipulation: int  # Minimum Arcane Manipulation ability level
    base_cost: int  # Base gold cost to apply
    min_item_quality: str  # "basic", "military", "noble"
    
    # Optional fields with defaults  
    prerequisite_enchantments: Set[str] = field(default_factory=set)
    compatible_item_types: Set[str] = field(default_factory=set)
    stat_bonuses: Dict[str, int] = field(default_factory=dict)
    special_abilities: List[str] = field(default_factory=list)
    duration_hours: Optional[int] = None  # None = permanent
    thematic_tags: Set[str] = field(default_factory=set)
    motif_alignment: Optional[str] = None  # Aligns with motif system
    exclusive_with: Set[str] = field(default_factory=set)  # Cannot coexist
    max_per_item: int = 1  # How many of this enchantment per item

@dataclass
class LearnedEnchantment:
    """Represents an enchantment that a character has learned."""
    # Required fields first
    character_id: UUID
    enchantment_id: str
    learned_at: datetime
    learned_from_item: str  # Name/description of item disenchanted
    
    # Optional fields with defaults
    mastery_level: int = 1  # 1-5, affects success rate and power
    times_applied: int = 0  # Tracks usage for mastery progression
    
    def can_apply_to_item(self, item_quality: str, item_type: str, 
                         current_enchantments: List[str]) -> tuple[bool, str]:
        """Check if this enchantment can be applied to a specific item."""
        enchantment = get_enchantment_definition(self.enchantment_id)
        
        # Quality check
        quality_order = ["basic", "military", "mastercraft", "legendary"]
        if quality_order.index(item_quality) < quality_order.index(enchantment.min_item_quality):
            return False, f"Item quality too low (need {enchantment.min_item_quality})"
        
        # Item type compatibility
        if enchantment.compatible_item_types and item_type not in enchantment.compatible_item_types:
            return False, f"Incompatible with {item_type}"
        
        # Exclusivity conflicts
        for existing_enchant in current_enchantments:
            if existing_enchant in enchantment.exclusive_with:
                return False, f"Conflicts with existing enchantment: {existing_enchant}"
        
        # Max per item limit
        existing_count = sum(1 for e in current_enchantments if e == self.enchantment_id)
        if existing_count >= enchantment.max_per_item:
            return False, f"Maximum {enchantment.max_per_item} per item"
        
        return True, "Compatible"

@dataclass
class DisenchantmentAttempt:
    """Records an attempt to disenchant an item for learning."""
    # Required fields first
    character_id: UUID
    item_id: UUID
    item_name: str
    item_quality: str
    item_enchantments: List[str]
    arcane_manipulation_level: int
    character_level: int
    
    # Optional fields with defaults
    id: UUID = field(default_factory=uuid4)
    attempted_at: datetime = field(default_factory=datetime.now)
    target_enchantment: Optional[str] = None  # Specific enchantment sought
    outcome: Optional[DisenchantmentOutcome] = None
    enchantment_learned: Optional[str] = None
    item_destroyed: bool = False
    additional_consequences: List[str] = field(default_factory=list)
    experience_gained: int = 0
    mastery_increased: bool = False

@dataclass
class EnchantmentApplication:
    """Records the application of an enchantment to an item."""
    # Required fields first
    character_id: UUID
    item_id: UUID
    enchantment_id: str
    cost_paid: int
    success: bool
    
    # Optional fields with defaults
    id: UUID = field(default_factory=uuid4)
    applied_at: datetime = field(default_factory=datetime.now)
    materials_consumed: Dict[str, int] = field(default_factory=dict)
    final_power_level: int = 100  # 1-100, affects strength of enchantment
    duration_remaining: Optional[int] = None  # Hours remaining for temporary enchantments
    failure_reason: Optional[str] = None
    materials_lost: bool = False

@dataclass
class CharacterEnchantingProfile:
    """Complete enchanting profile for a character."""
    # Required fields first
    character_id: UUID
    
    # Optional fields with defaults
    learned_enchantments: Dict[str, LearnedEnchantment] = field(default_factory=dict)
    total_items_disenchanted: int = 0
    successful_applications: int = 0
    failed_applications: int = 0
    preferred_school: Optional[EnchantmentSchool] = None
    school_bonuses: Dict[EnchantmentSchool, int] = field(default_factory=dict)
    research_notes: List[str] = field(default_factory=list)
    discovered_combinations: Set[tuple] = field(default_factory=set)
    
    def get_learning_success_rate(self, enchantment_rarity: EnchantmentRarity,
                                item_quality: str, arcane_manipulation: int) -> float:
        """Calculate success rate for learning an enchantment."""
        base_rates = {
            EnchantmentRarity.BASIC: 0.7,
            EnchantmentRarity.MILITARY: 0.5,
            EnchantmentRarity.MASTERCRAFT: 0.3,
            EnchantmentRarity.LEGENDARY: 0.1
        }
        
        # Base rate by rarity
        success_rate = base_rates[enchantment_rarity]
        
        # Arcane Manipulation bonus (major factor)
        success_rate += (arcane_manipulation * 0.05)
        
        # Item quality bonus (higher quality = easier to learn from)
        quality_bonuses = {"basic": 0.0, "military": 0.1, "mastercraft": 0.2, "legendary": 0.3}
        success_rate += quality_bonuses.get(item_quality, 0.0)
        
        # Experience bonus
        experience_bonus = min(self.total_items_disenchanted * 0.01, 0.2)
        success_rate += experience_bonus
        
        # School specialization bonus
        enchantment_def = get_enchantment_definition(enchantment_rarity.value)
        if enchantment_def and enchantment_def.school in self.school_bonuses:
            success_rate += (self.school_bonuses[enchantment_def.school] * 0.02)
        
        return min(success_rate, 0.95)  # Cap at 95% to maintain risk

# Registry of all available enchantments
_enchantment_registry: Dict[str, EnchantmentDefinition] = {}

def register_enchantment(enchantment: EnchantmentDefinition):
    """Register an enchantment in the global registry."""
    _enchantment_registry[enchantment.id] = enchantment

def get_enchantment_definition(enchantment_id: str) -> Optional[EnchantmentDefinition]:
    """Get enchantment definition by ID."""
    return _enchantment_registry.get(enchantment_id)

def get_enchantments_by_school(school: EnchantmentSchool) -> List[EnchantmentDefinition]:
    """Get all enchantments in a specific school."""
    return [e for e in _enchantment_registry.values() if e.school == school]

def get_enchantments_by_rarity(rarity: EnchantmentRarity) -> List[EnchantmentDefinition]:
    """Get all enchantments of a specific rarity."""
    return [e for e in _enchantment_registry.values() if e.rarity == rarity]

# Example enchantments to populate the system
def register_default_enchantments():
    """Register a set of default enchantments for the system."""
    
    # Basic Protection Enchantments
    register_enchantment(EnchantmentDefinition(
        id="armor_basic",
        name="Iron Skin",
        description="Hardens the wearer's skin, providing basic protection against physical attacks",
        rarity=EnchantmentRarity.BASIC,
        school=EnchantmentSchool.PROTECTION,
        min_arcane_manipulation=1,
        base_cost=500,
        min_item_quality="basic",
        compatible_item_types={"armor", "clothing"},
        stat_bonuses={"armor_class": 1},
        thematic_tags={"metallic", "hardening", "basic_defense"}
    ))
    
    # Military Combat Enchantments
    register_enchantment(EnchantmentDefinition(
        id="weapon_sharpness",
        name="Keen Edge",
        description="Supernaturally sharpens a weapon's edge, improving its cutting ability",
        rarity=EnchantmentRarity.MILITARY,
        school=EnchantmentSchool.COMBAT,
        min_arcane_manipulation=3,
        base_cost=1500,
        min_item_quality="military",
        compatible_item_types={"weapon", "blade"},
        stat_bonuses={"damage": 2, "critical_chance": 5},
        thematic_tags={"sharpness", "precision", "military_grade"}
    ))
    
    # Noble Elemental Enchantments
    register_enchantment(EnchantmentDefinition(
        id="flame_wreath",
        name="Wreath of Flames",
        description="Surrounds the item with controlled flames that do not harm the wielder",
        rarity=EnchantmentRarity.LEGENDARY,
        school=EnchantmentSchool.ELEMENTAL,
        min_arcane_manipulation=5,
        base_cost=5000,
        min_item_quality="mastercraft",
        compatible_item_types={"weapon", "armor", "accessory"},
        stat_bonuses={"fire_damage": 8},
        special_abilities=["flame_aura", "fire_resistance_minor"],
        exclusive_with={"ice_enchantments"},
        thematic_tags={"fire", "nobility", "dramatic_effect"}
    ))

# Initialize default enchantments
register_default_enchantments() 
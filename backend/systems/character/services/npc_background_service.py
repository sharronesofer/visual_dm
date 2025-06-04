"""
NPC Background Service

Implements the comprehensive background system for NPCs that affects their material
circumstances, social standing, wealth, housing, and relationships.
"""

import random
from typing import Dict, Any, List, Optional, Tuple
from uuid import UUID
from dataclasses import dataclass

from backend.infrastructure.utils.json_utils import load_json
from backend.infrastructure.config_loaders.character_config_loader import config_loader


@dataclass
class NPCMaterialCircumstances:
    """Represents an NPC's material living conditions"""
    housing_type: str
    wealth_amount: int
    possessions: List[str]
    business_assets: Optional[List[str]] = None
    employees: Optional[int] = None
    servants: Optional[int] = None
    property_ownership: Optional[List[str]] = None


@dataclass
class NPCSocialStanding:
    """Represents an NPC's social position and relationships"""
    social_tier: str
    reputation_level: str
    access_privileges: List[str]
    authority_level: str
    default_relationships: Dict[str, str]


class NPCBackgroundService:
    """
    Service for applying background effects to NPCs including material circumstances,
    social standing, wealth generation, and relationship initialization.
    """
    
    def __init__(self):
        self.background_config = self._load_background_config()
        
    def _load_background_config(self) -> Dict[str, Any]:
        """Load the background system configuration"""
        try:
            return load_json("data/systems/character/background_system.json")
        except Exception:
            # Fallback configuration
            return {"npc_backgrounds": {}, "social_tier_definitions": {}}
    
    def apply_npc_background(self, npc_data: Dict[str, Any], background_name: str) -> Dict[str, Any]:
        """
        Apply comprehensive background effects to an NPC
        
        Args:
            npc_data: Base NPC character data
            background_name: Background to apply
            
        Returns:
            Enhanced NPC data with background effects applied
        """
        background = self.background_config.get("npc_backgrounds", {}).get(background_name)
        if not background:
            raise ValueError(f"Unknown NPC background: {background_name}")
        
        # Apply all background effects
        enhanced_npc = npc_data.copy()
        
        # 1. Apply material circumstances
        circumstances = self._generate_material_circumstances(background)
        enhanced_npc["material_circumstances"] = circumstances.__dict__
        
        # 2. Apply social standing
        social_standing = self._generate_social_standing(background)
        enhanced_npc["social_standing"] = social_standing.__dict__
        
        # 3. Apply skill and attribute bonuses
        self._apply_mechanical_bonuses(enhanced_npc, background)
        
        # 4. Apply behavioral modifiers
        self._apply_behavioral_modifiers(enhanced_npc, background)
        
        # 5. Set AI personality parameters
        self._apply_ai_personality(enhanced_npc, background)
        
        # 6. Apply background-specific metadata
        enhanced_npc["background"] = background_name
        enhanced_npc["social_tier"] = background.get("social_tier", "working_class")
        
        return enhanced_npc
    
    def _generate_material_circumstances(self, background: Dict[str, Any]) -> NPCMaterialCircumstances:
        """Generate material circumstances based on background"""
        material_config = background.get("material_circumstances", {})
        
        # Generate wealth within range
        wealth_range = material_config.get("starting_wealth_range", [10, 100])
        wealth = random.randint(wealth_range[0], wealth_range[1])
        
        # Apply social tier multiplier
        social_tier = background.get("social_tier", "working_class")
        tier_config = self.background_config.get("social_tier_definitions", {}).get(social_tier, {})
        wealth_multiplier = tier_config.get("wealth_multiplier", 1.0)
        wealth = int(wealth * wealth_multiplier)
        
        # Generate other material aspects
        housing_type = material_config.get("housing_type", "basic_dwelling")
        possessions = material_config.get("possessions", [])
        
        # Generate employees/servants if applicable
        employees = None
        if "employees" in material_config:
            emp_range = material_config["employees"]
            employees = random.randint(emp_range[0], emp_range[1])
        
        servants = None
        if "servants" in material_config:
            serv_range = material_config["servants"] 
            servants = random.randint(serv_range[0], serv_range[1])
        
        return NPCMaterialCircumstances(
            housing_type=housing_type,
            wealth_amount=wealth,
            possessions=possessions.copy(),
            business_assets=material_config.get("business_assets", []).copy() if "business_assets" in material_config else None,
            employees=employees,
            servants=servants,
            property_ownership=material_config.get("property_ownership", []).copy() if "property_ownership" in material_config else None
        )
    
    def _generate_social_standing(self, background: Dict[str, Any]) -> NPCSocialStanding:
        """Generate social standing based on background"""
        social_config = background.get("social_standing", {})
        
        return NPCSocialStanding(
            social_tier=background.get("social_tier", "working_class"),
            reputation_level=social_config.get("reputation_level", "moderate"),
            access_privileges=social_config.get("access_privileges", []).copy(),
            authority_level=social_config.get("authority_level", "none"),
            default_relationships=social_config.get("default_relationships", {}).copy()
        )
    
    def _apply_mechanical_bonuses(self, npc_data: Dict[str, Any], background: Dict[str, Any]) -> None:
        """Apply skill and attribute bonuses from background"""
        # Apply attribute bonuses
        attribute_bonuses = background.get("attribute_bonuses", {})
        for attr, bonus in attribute_bonuses.items():
            if "attributes" not in npc_data:
                npc_data["attributes"] = {}
            current_value = npc_data["attributes"].get(attr, 0)
            npc_data["attributes"][attr] = current_value + bonus
        
        # Apply skill bonuses
        skill_bonuses = background.get("skill_bonuses", {})
        if skill_bonuses:
            if "skill_bonuses" not in npc_data:
                npc_data["skill_bonuses"] = {}
            npc_data["skill_bonuses"].update(skill_bonuses)
        
        # Add special abilities
        special_abilities = background.get("special_abilities", [])
        if special_abilities:
            if "special_abilities" not in npc_data:
                npc_data["special_abilities"] = []
            npc_data["special_abilities"].extend(special_abilities)
    
    def _apply_behavioral_modifiers(self, npc_data: Dict[str, Any], background: Dict[str, Any]) -> None:
        """Apply behavioral modifiers that affect AI decision making"""
        behavioral_modifiers = background.get("behavioral_modifiers", {})
        if behavioral_modifiers:
            npc_data["behavioral_modifiers"] = behavioral_modifiers.copy()
    
    def _apply_ai_personality(self, npc_data: Dict[str, Any], background: Dict[str, Any]) -> None:
        """Apply AI personality configuration from background"""
        ai_personality = background.get("ai_personality", {})
        if ai_personality:
            npc_data["ai_personality"] = ai_personality.copy()
    
    def get_spawn_location_type(self, background_name: str) -> str:
        """
        Get the appropriate spawn location type for an NPC background
        
        Args:
            background_name: NPC background name
            
        Returns:
            Location type where this NPC should spawn
        """
        background = self.background_config.get("npc_backgrounds", {}).get(background_name)
        if not background:
            return "common_area"
        
        housing_type = background.get("material_circumstances", {}).get("housing_type", "basic_dwelling")
        
        # Map housing types to spawn locations
        location_mapping = {
            "manor_or_castle": "noble_quarter",
            "comfortable_house_with_shop": "merchant_quarter", 
            "workshop_with_living_quarters": "artisan_quarter",
            "temple_quarters_or_modest_house": "temple_district",
            "barracks_or_modest_house": "guard_district",
            "small_cottage_or_tenement": "lower_district",
            "hideouts_safe_houses_or_slums": "slums_or_underground"
        }
        
        return location_mapping.get(housing_type, "common_area")
    
    def check_access_permission(self, npc_background: str, location_type: str) -> bool:
        """
        Check if an NPC with given background has access to a location type
        
        Args:
            npc_background: NPC's background name
            location_type: Type of location to check access for
            
        Returns:
            True if access is permitted, False otherwise
        """
        background = self.background_config.get("npc_backgrounds", {}).get(npc_background)
        if not background:
            return True  # Default allow
        
        access_privileges = background.get("social_standing", {}).get("access_privileges", [])
        
        # Map location types to required privileges
        privilege_requirements = {
            "noble_quarters": ["noble_quarters", "royal_court"],
            "royal_court": ["royal_court"],
            "exclusive_establishments": ["exclusive_establishments"],
            "private_clubs": ["private_clubs"],
            "guard_posts": ["guard_posts"],
            "restricted_areas": ["restricted_areas"],
            "armories": ["armories"],
            "official_buildings": ["official_buildings"],
            "criminal_underworld": ["criminal_underworld"],
            "black_markets": ["black_markets"]
        }
        
        required_privileges = privilege_requirements.get(location_type, [])
        
        # Check if NPC has any of the required privileges
        return any(privilege in access_privileges for privilege in required_privileges)
    
    def calculate_interaction_modifier(self, npc1_background: str, npc2_background: str) -> float:
        """
        Calculate relationship modifier between two NPCs based on their backgrounds
        
        Args:
            npc1_background: First NPC's background
            npc2_background: Second NPC's background
            
        Returns:
            Relationship modifier (-1.0 to 1.0)
        """
        bg1 = self.background_config.get("npc_backgrounds", {}).get(npc1_background)
        bg2 = self.background_config.get("npc_backgrounds", {}).get(npc2_background)
        
        if not bg1 or not bg2:
            return 0.0  # Neutral
        
        # Get relationship defaults
        bg1_relationships = bg1.get("social_standing", {}).get("default_relationships", {})
        
        # Look for specific relationship rules
        for relationship_target, attitude in bg1_relationships.items():
            if self._background_matches_category(npc2_background, relationship_target):
                return self._attitude_to_modifier(attitude)
        
        # Check social tier compatibility
        tier1 = bg1.get("social_tier", "working_class")
        tier2 = bg2.get("social_tier", "working_class")
        
        return self._calculate_tier_compatibility(tier1, tier2)
    
    def _background_matches_category(self, background: str, category: str) -> bool:
        """Check if a background matches a relationship category"""
        category_mappings = {
            "other_nobles": ["nobility"],
            "merchants": ["merchant"],
            "commoners": ["laborer", "artisan"],
            "clergy": ["priest"],
            "guards": ["guard"],
            "criminals": ["criminal"],
            "law_enforcement": ["guard"],
            "law_abiding_citizens": ["merchant", "artisan", "priest", "laborer", "nobility"]
        }
        
        matching_backgrounds = category_mappings.get(category, [])
        return background in matching_backgrounds
    
    def _attitude_to_modifier(self, attitude: str) -> float:
        """Convert attitude string to numerical modifier"""
        attitude_modifiers = {
            "hostile": -0.8,
            "unfriendly": -0.4,
            "dismissive": -0.3,
            "wary": -0.2,
            "suspicious": -0.2,
            "neutral": 0.0,
            "professional": 0.1,
            "cooperative": 0.2,
            "respectful": 0.3,
            "friendly": 0.4,
            "fraternal": 0.5,
            "beloved": 0.8,
            "commanding": 0.3,
            "superior": 0.2,
            "deferential": -0.1
        }
        
        return attitude_modifiers.get(attitude, 0.0)
    
    def _calculate_tier_compatibility(self, tier1: str, tier2: str) -> float:
        """Calculate compatibility between social tiers"""
        tier_hierarchy = {
            "upper_class": 4,
            "middle_class": 3, 
            "working_class": 2,
            "lower_class": 1,
            "outcast": 0
        }
        
        value1 = tier_hierarchy.get(tier1, 2)
        value2 = tier_hierarchy.get(tier2, 2)
        
        difference = abs(value1 - value2)
        
        # Large tier differences create social friction
        if difference >= 3:
            return -0.3  # Significant discomfort
        elif difference == 2:
            return -0.1  # Mild discomfort
        elif difference == 1:
            return 0.0   # Neutral
        else:
            return 0.1   # Same tier comfort
    
    def get_available_backgrounds(self) -> List[str]:
        """Get list of available NPC backgrounds"""
        return list(self.background_config.get("npc_backgrounds", {}).keys())
    
    def get_background_summary(self, background_name: str) -> Dict[str, Any]:
        """Get a summary of background effects for documentation/debugging"""
        background = self.background_config.get("npc_backgrounds", {}).get(background_name)
        if not background:
            return {}
        
        return {
            "name": background.get("name", background_name),
            "social_tier": background.get("social_tier", "unknown"),
            "housing_type": background.get("material_circumstances", {}).get("housing_type", "unknown"),
            "wealth_range": background.get("material_circumstances", {}).get("starting_wealth_range", [0, 0]),
            "reputation_level": background.get("social_standing", {}).get("reputation_level", "unknown"),
            "access_privileges": background.get("social_standing", {}).get("access_privileges", []),
            "special_abilities": background.get("special_abilities", [])
        } 
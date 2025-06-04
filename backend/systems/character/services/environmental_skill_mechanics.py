"""
Environmental Skill Mechanics
-----------------------------
Advanced environmental and situational mechanics for noncombat skills.
Integrates with Visual DM's existing location, weather, and time systems.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from dataclasses import dataclass
from datetime import datetime, timedelta

from backend.systems.character.models.character import Character
from backend.systems.character.services.skill_check_service import (
    skill_check_service, SkillCheckModifiers, SkillCheckDifficulty
)
from backend.systems.character.services.noncombat_skills import (
    noncombat_skill_service, PerceptionType, StealthContext
)

logger = logging.getLogger(__name__)

class EnvironmentalCondition(Enum):
    """Environmental conditions that affect skill checks."""
    BRIGHT_LIGHT = "bright_light"
    DIM_LIGHT = "dim_light"
    DARKNESS = "darkness"
    HEAVY_RAIN = "heavy_rain"
    LIGHT_RAIN = "light_rain"
    FOG = "fog"
    SNOW = "snow"
    WIND = "wind"
    EXTREME_HEAT = "extreme_heat"
    EXTREME_COLD = "extreme_cold"
    LOUD_ENVIRONMENT = "loud_environment"
    QUIET_ENVIRONMENT = "quiet_environment"
    CROWDED = "crowded"
    ISOLATED = "isolated"
    FAMILIAR_TERRAIN = "familiar_terrain"
    UNFAMILIAR_TERRAIN = "unfamiliar_terrain"

class TerrainType(Enum):
    """Types of terrain with different skill modifiers."""
    URBAN = "urban"
    FOREST = "forest"
    MOUNTAIN = "mountain"
    SWAMP = "swamp"
    DESERT = "desert"
    PLAINS = "plains"
    UNDERGROUND = "underground"
    WATER = "water"
    RUINS = "ruins"
    SACRED_GROUND = "sacred_ground"

@dataclass
class EnvironmentalContext:
    """Complete environmental context for skill checks."""
    terrain_type: TerrainType
    conditions: List[EnvironmentalCondition]
    time_of_day: str  # "day", "night", "dawn", "dusk"
    season: str       # "spring", "summer", "autumn", "winter"
    weather_severity: int  # 1-5 scale
    familiarity_level: int  # 0-5, how well known the area is
    population_density: str  # "uninhabited", "sparse", "moderate", "dense"
    magical_presence: bool = False
    threat_level: int = 0  # 0-5, how dangerous the area is

@dataclass
class SkillEnvironmentBonus:
    """Bonuses and penalties for skills in specific environments."""
    skill_name: str
    terrain_bonus: int = 0
    condition_bonus: int = 0
    time_bonus: int = 0
    familiarity_bonus: int = 0
    total_modifier: int = 0

class EnvironmentalSkillService:
    """Service for handling environmental effects on skills."""
    
    def __init__(self):
        # Base terrain modifiers for different skills
        self.terrain_modifiers = {
            TerrainType.URBAN: {
                "gather_information": 3,
                "diplomacy": 2,
                "sleight_of_hand": 2,
                "survival": -3,
                "nature": -2,
                "stealth": -1,  # Harder to hide in cities
                "perception": -1  # Noise and distractions
            },
            TerrainType.FOREST: {
                "survival": 3,
                "nature": 3,
                "stealth": 2,
                "perception": 1,
                "gather_information": -2,
                "diplomacy": -1,
                "investigation": -1
            },
            TerrainType.MOUNTAIN: {
                "survival": 2,
                "athletics": 1,
                "perception": 2,  # Good visibility
                "nature": 2,
                "diplomacy": -1,
                "gather_information": -3,
                "stealth": -1
            },
            TerrainType.SWAMP: {
                "survival": 1,
                "nature": 2,
                "medicine": 1,  # Medicinal plants
                "stealth": 1,
                "perception": -2,  # Poor visibility
                "athletics": -2,
                "diplomacy": -2
            },
            TerrainType.UNDERGROUND: {
                "search": 2,
                "investigation": 2,
                "survival": -1,
                "perception": -2,  # Limited light
                "stealth": 1,
                "nature": -3,
                "gather_information": -2
            },
            TerrainType.RUINS: {
                "search": 3,
                "investigation": 3,
                "history": 2,
                "arcana": 2,
                "perception": 1,
                "survival": -1,
                "diplomacy": -3
            }
        }
        
        # Condition-specific modifiers
        self.condition_modifiers = {
            EnvironmentalCondition.DARKNESS: {
                "perception": -8,
                "search": -6,
                "investigation": -4,
                "stealth": 4,
                "sleight_of_hand": -3
            },
            EnvironmentalCondition.FOG: {
                "perception": -6,
                "search": -4,
                "stealth": 3,
                "survival": -2,
                "athletics": -1
            },
            EnvironmentalCondition.HEAVY_RAIN: {
                "perception": -4,
                "stealth": 2,  # Sound masking
                "survival": -1,
                "athletics": -2,
                "search": -3
            },
            EnvironmentalCondition.CROWDED: {
                "gather_information": 2,
                "stealth": 3,  # Easier to blend in
                "sleight_of_hand": 3,
                "perception": -2,  # Distractions
                "diplomacy": -1
            },
            EnvironmentalCondition.QUIET_ENVIRONMENT: {
                "perception": 3,
                "stealth": -2,  # Sounds carry
                "investigation": 2,
                "diplomacy": 1
            },
            EnvironmentalCondition.FAMILIAR_TERRAIN: {
                "survival": 3,
                "perception": 2,
                "stealth": 2,
                "gather_information": 2,
                "investigation": 1
            }
        }
        
        # Time of day modifiers
        self.time_modifiers = {
            "night": {
                "stealth": 3,
                "perception": -5,
                "search": -4,
                "investigation": -3,
                "gather_information": -2,
                "diplomacy": -1
            },
            "dawn": {
                "perception": -1,
                "stealth": 1,
                "survival": 1
            },
            "dusk": {
                "perception": -2,
                "stealth": 2,
                "diplomacy": 1  # Romantic/mysterious atmosphere
            }
        }
    
    def calculate_environmental_modifiers(
        self,
        skill_name: str,
        environmental_context: EnvironmentalContext,
        character: Character = None
    ) -> SkillEnvironmentBonus:
        """
        Calculate comprehensive environmental modifiers for a skill check.
        
        Args:
            skill_name: Name of the skill being checked
            environmental_context: Complete environmental information
            character: Character making the check (for personalized bonuses)
            
        Returns:
            SkillEnvironmentBonus with detailed modifier breakdown
        """
        terrain_bonus = self.terrain_modifiers.get(environmental_context.terrain_type, {}).get(skill_name, 0)
        
        # Calculate condition bonuses
        condition_bonus = 0
        for condition in environmental_context.conditions:
            condition_bonus += self.condition_modifiers.get(condition, {}).get(skill_name, 0)
        
        # Time of day bonus
        time_bonus = self.time_modifiers.get(environmental_context.time_of_day, {}).get(skill_name, 0)
        
        # Familiarity bonus
        familiarity_bonus = 0
        if environmental_context.familiarity_level > 0:
            # +1 for every 2 points of familiarity
            familiarity_bonus = environmental_context.familiarity_level // 2
            
            # Certain skills benefit more from familiarity
            if skill_name in ["survival", "gather_information", "stealth", "perception"]:
                familiarity_bonus = environmental_context.familiarity_level
        
        # Weather severity modifier
        weather_modifier = 0
        if environmental_context.weather_severity > 3:
            # Severe weather penalizes most skills
            if skill_name not in ["survival", "nature"]:
                weather_modifier = -(environmental_context.weather_severity - 3)
        
        # Character-specific bonuses
        character_bonus = 0
        if character:
            character_bonus = self._calculate_character_environmental_bonus(
                character, skill_name, environmental_context
            )
        
        total_modifier = (
            terrain_bonus + 
            condition_bonus + 
            time_bonus + 
            familiarity_bonus + 
            weather_modifier + 
            character_bonus
        )
        
        return SkillEnvironmentBonus(
            skill_name=skill_name,
            terrain_bonus=terrain_bonus,
            condition_bonus=condition_bonus,
            time_bonus=time_bonus,
            familiarity_bonus=familiarity_bonus,
            total_modifier=total_modifier
        )
    
    def _calculate_character_environmental_bonus(
        self,
        character: Character,
        skill_name: str,
        environmental_context: EnvironmentalContext
    ) -> int:
        """Calculate character-specific environmental bonuses."""
        bonus = 0
        
        # Race-based bonuses (simplified)
        race = getattr(character, 'race', '').lower()
        
        if race == 'elf':
            if skill_name == "perception" and environmental_context.terrain_type == TerrainType.FOREST:
                bonus += 2
            if EnvironmentalCondition.DIM_LIGHT in environmental_context.conditions:
                bonus += 1
        elif race == 'dwarf':
            if environmental_context.terrain_type in [TerrainType.MOUNTAIN, TerrainType.UNDERGROUND]:
                if skill_name in ["survival", "search", "investigation"]:
                    bonus += 2
        elif race == 'halfling':
            if environmental_context.terrain_type == TerrainType.PLAINS:
                if skill_name in ["stealth", "survival"]:
                    bonus += 1
        
        # Background-based bonuses
        background = getattr(character, 'background', '').lower()
        
        if 'criminal' in background or 'rogue' in background:
            if environmental_context.terrain_type == TerrainType.URBAN:
                if skill_name in ["stealth", "sleight_of_hand", "gather_information"]:
                    bonus += 2
        elif 'ranger' in background or 'outlander' in background:
            if environmental_context.terrain_type in [TerrainType.FOREST, TerrainType.MOUNTAIN]:
                if skill_name in ["survival", "nature", "perception"]:
                    bonus += 2
        
        return bonus
    
    def get_enhanced_stealth_mechanics(
        self,
        character: Character,
        environmental_context: EnvironmentalContext,
        observers: List[Character],
        stealth_context: StealthContext
    ) -> Dict[str, Any]:
        """
        Enhanced stealth mechanics with environmental considerations.
        
        Args:
            character: Character attempting stealth
            environmental_context: Environmental conditions
            observers: Potential observers
            stealth_context: Type of stealth attempt
            
        Returns:
            Enhanced stealth result with environmental factors
        """
        # Convert environmental conditions to condition strings
        condition_strings = [condition.value for condition in environmental_context.conditions]
        
        # Calculate base stealth result
        stealth_result = noncombat_skill_service.make_stealth_check(
            character=character,
            stealth_context=stealth_context,
            observers=observers,
            environmental_conditions=condition_strings
        )
        
        # Apply environmental modifiers
        env_bonus = self.calculate_environmental_modifiers("stealth", environmental_context, character)
        
        # Adjust stealth level based on environment
        adjusted_stealth_level = stealth_result.stealth_level + env_bonus.total_modifier
        
        # Special environmental effects
        special_effects = []
        
        if EnvironmentalCondition.FOG in environmental_context.conditions:
            special_effects.append("fog_concealment")
            # Reduce detection range
            adjusted_stealth_level += 5
        
        if EnvironmentalCondition.CROWDED in environmental_context.conditions:
            special_effects.append("crowd_concealment")
            # Easier to blend in
            adjusted_stealth_level += 3
        
        if environmental_context.terrain_type == TerrainType.FOREST and stealth_context == StealthContext.HIDING:
            special_effects.append("natural_cover")
            adjusted_stealth_level += 2
        
        return {
            "base_stealth_result": stealth_result,
            "environmental_bonus": env_bonus,
            "adjusted_stealth_level": max(0, adjusted_stealth_level),
            "special_effects": special_effects,
            "detection_difficulty": self._calculate_detection_difficulty(environmental_context),
            "recommended_duration": self._calculate_stealth_duration(environmental_context, stealth_context)
        }
    
    def get_enhanced_perception_mechanics(
        self,
        character: Character,
        environmental_context: EnvironmentalContext,
        perception_type: PerceptionType,
        hidden_objects: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Enhanced perception mechanics with environmental considerations.
        
        Args:
            character: Character making perception check
            environmental_context: Environmental conditions
            perception_type: Type of perception check
            hidden_objects: Objects that might be perceived
            
        Returns:
            Enhanced perception result
        """
        if hidden_objects is None:
            hidden_objects = []
        
        # Convert environmental conditions
        condition_strings = [condition.value for condition in environmental_context.conditions]
        
        # Calculate environmental modifiers
        env_bonus = self.calculate_environmental_modifiers("perception", environmental_context, character)
        
        # Make enhanced perception check
        perception_result = noncombat_skill_service.make_perception_check(
            character=character,
            perception_type=perception_type,
            hidden_objects=hidden_objects,
            environmental_conditions=condition_strings
        )
        
        # Apply environmental enhancements
        enhanced_detection = []
        environmental_hints = []
        
        # Terrain-specific perception bonuses
        if environmental_context.terrain_type == TerrainType.MOUNTAIN:
            environmental_hints.append("excellent_visibility")
            # Can see much farther
            enhanced_detection.append("distant_objects")
        
        if environmental_context.terrain_type == TerrainType.FOREST:
            environmental_hints.append("natural_sounds")
            # Better at detecting movement through sounds
            if perception_type == PerceptionType.AUDITORY:
                enhanced_detection.append("movement_detection")
        
        # Weather effects
        if EnvironmentalCondition.QUIET_ENVIRONMENT in environmental_context.conditions:
            environmental_hints.append("enhanced_hearing")
            if perception_type == PerceptionType.AUDITORY:
                enhanced_detection.append("subtle_sounds")
        
        return {
            "base_perception_result": perception_result,
            "environmental_bonus": env_bonus,
            "enhanced_detection": enhanced_detection,
            "environmental_hints": environmental_hints,
            "effective_range": self._calculate_perception_range(environmental_context, perception_type),
            "auto_success_objects": self._get_auto_success_objects(
                hidden_objects, environmental_context, character
            )
        }
    
    def _calculate_detection_difficulty(self, environmental_context: EnvironmentalContext) -> int:
        """Calculate how hard it is to detect hidden things in this environment."""
        base_difficulty = 15
        
        # Terrain effects
        if environmental_context.terrain_type == TerrainType.URBAN:
            base_difficulty -= 2  # Lots of distractions
        elif environmental_context.terrain_type == TerrainType.FOREST:
            base_difficulty += 2  # Natural cover
        
        # Condition effects
        for condition in environmental_context.conditions:
            if condition == EnvironmentalCondition.DARKNESS:
                base_difficulty += 5
            elif condition == EnvironmentalCondition.FOG:
                base_difficulty += 3
            elif condition == EnvironmentalCondition.CROWDED:
                base_difficulty -= 2
        
        return max(5, min(30, base_difficulty))
    
    def _calculate_stealth_duration(
        self, 
        environmental_context: EnvironmentalContext, 
        stealth_context: StealthContext
    ) -> int:
        """Calculate recommended stealth duration in minutes."""
        base_duration = 10
        
        # Context effects
        if stealth_context == StealthContext.HIDING:
            base_duration = 60  # Can hide for longer
        elif stealth_context == StealthContext.MOVING_SILENTLY:
            base_duration = 5   # Harder to maintain while moving
        
        # Environmental effects
        if EnvironmentalCondition.CROWDED in environmental_context.conditions:
            base_duration *= 2  # Easier to stay hidden in crowds
        
        if EnvironmentalCondition.QUIET_ENVIRONMENT in environmental_context.conditions:
            base_duration //= 2  # Sounds carry more
        
        return max(1, base_duration)
    
    def _calculate_perception_range(
        self, 
        environmental_context: EnvironmentalContext, 
        perception_type: PerceptionType
    ) -> str:
        """Calculate effective perception range."""
        if perception_type == PerceptionType.VISUAL:
            if environmental_context.terrain_type == TerrainType.MOUNTAIN:
                return "very_long"  # Can see for miles
            elif EnvironmentalCondition.FOG in environmental_context.conditions:
                return "very_short"  # Limited by fog
            elif EnvironmentalCondition.DARKNESS in environmental_context.conditions:
                return "short"  # Limited by darkness
            else:
                return "normal"
        
        elif perception_type == PerceptionType.AUDITORY:
            if EnvironmentalCondition.QUIET_ENVIRONMENT in environmental_context.conditions:
                return "long"  # Sounds carry far
            elif EnvironmentalCondition.LOUD_ENVIRONMENT in environmental_context.conditions:
                return "short"  # Masked by noise
            else:
                return "normal"
        
        return "normal"
    
    def _get_auto_success_objects(
        self,
        hidden_objects: List[Dict[str, Any]],
        environmental_context: EnvironmentalContext,
        character: Character
    ) -> List[Dict[str, Any]]:
        """Get objects that are automatically detected due to environmental factors."""
        auto_success = []
        
        # Characters with high familiarity auto-detect certain things
        if environmental_context.familiarity_level >= 4:
            for obj in hidden_objects:
                if obj.get("familiar_landmark", False):
                    auto_success.append(obj)
        
        # Certain terrain types make some things obvious
        if environmental_context.terrain_type == TerrainType.MOUNTAIN:
            for obj in hidden_objects:
                if obj.get("type") == "distant_landmark":
                    auto_success.append(obj)
        
        return auto_success

# Global service instance
environmental_skill_service = EnvironmentalSkillService() 
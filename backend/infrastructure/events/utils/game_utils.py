import logging
import random
from typing import Dict, Any, List, Optional, Tuple
from backend.infrastructure.shared.utils.config_utils import get_config
from backend.infrastructure.shared.utils.constants import (
    DIFFICULTY_MULTIPLIERS,
    LEVEL_SCALING,
    BASE_XP,
    BASE_GOLD,
    BASE_DAMAGE,
    BASE_HEALTH,
    ATTRIBUTE_LIMITS,
    VALID_RACES,
    VALID_ARCHETYPES,
    VALID_DIFFICULTIES,
    VALID_BACKGROUNDS,
    VALID_ATTRIBUTES
)

logger = logging.getLogger(__name__)

class GameCalculator:
    """Calculator for game-specific mechanics"""
    
    def __init__(self) -> None:
        self.config = get_config()
    
    def calculate_xp_gain(
        self,
        base_xp: int,
        level_difference: int,
        difficulty_multiplier: float = 1.0
    ) -> int:
        """Calculate XP gain based on level difference and difficulty"""
        try:
            # Base XP modified by level difference
            if level_difference > 0:
                xp = base_xp * (1 + (level_difference * LEVEL_SCALING['xp']))
            else:
                xp = base_xp * (1 + (level_difference * LEVEL_SCALING['xp'] * 0.5))
            
            # Apply difficulty multiplier
            xp = int(xp * difficulty_multiplier)
            
            # Ensure minimum XP
            xp = max(1, xp)
            
            logger.debug(f"Calculated XP gain: {xp}")
            return xp
            
        except Exception as e:
            logger.error(f"Failed to calculate XP gain: {str(e)}")
            return base_xp
    
    def calculate_level_up_xp(self, current_level: int) -> int:
        """Calculate XP required for next level"""
        try:
            # Exponential growth formula
            xp_required = int(BASE_XP * (LEVEL_SCALING['xp'] ** (current_level - 1)))
            
            logger.debug(f"XP required for level {current_level + 1}: {xp_required}")
            return xp_required
            
        except Exception as e:
            logger.error(f"Failed to calculate level up XP: {str(e)}")
            return BASE_XP
    
    def calculate_combat_damage(
        self,
        attacker_level: int,
        defender_level: int,
        base_damage: int,
        attack_bonus: float = 1.0,
        defense_bonus: float = 1.0
    ) -> int:
        """Calculate combat damage"""
        try:
            # Level difference modifier
            level_diff = attacker_level - defender_level
            level_modifier = 1 + (level_diff * LEVEL_SCALING['damage'])
            
            # Calculate final damage
            damage = int(base_damage * level_modifier * attack_bonus / defense_bonus)
            
            # Ensure minimum damage
            damage = max(1, damage)
            
            logger.debug(f"Calculated combat damage: {damage}")
            return damage
            
        except Exception as e:
            logger.error(f"Failed to calculate combat damage: {str(e)}")
            return base_damage
    
    def calculate_loot_drop(
        self,
        monster_level: int,
        player_level: int,
        base_chance: float,
        luck_bonus: float = 1.0
    ) -> bool:
        """Calculate if loot should drop"""
        try:
            # Level difference modifier
            level_diff = player_level - monster_level
            level_modifier = 1 + (level_diff * LEVEL_SCALING['drop_chance'])
            
            # Calculate final drop chance
            drop_chance = base_chance * level_modifier * luck_bonus
            
            # Ensure chance is between 0 and 1
            drop_chance = max(0, min(1, drop_chance))
            
            # Roll for drop
            should_drop = random.random() < drop_chance
            
            logger.debug(f"Loot drop chance: {drop_chance}, dropped: {should_drop}")
            return should_drop
            
        except Exception as e:
            logger.error(f"Failed to calculate loot drop: {str(e)}")
            return False
    
    def calculate_quest_reward(
        self,
        quest_level: int,
        quest_difficulty: str,
        player_level: int
    ) -> Dict[str, int]:
        """Calculate quest rewards"""
        try:
            # Base rewards
            base_xp = BASE_XP * quest_level
            base_gold = BASE_GOLD * quest_level
            
            # Get difficulty multiplier
            multiplier = DIFFICULTY_MULTIPLIERS.get(quest_difficulty, 1.0)
            
            # Level difference modifier
            level_diff = player_level - quest_level
            level_modifier = 1 + (level_diff * LEVEL_SCALING['gold'])
            
            # Calculate final rewards
            xp = int(base_xp * multiplier * level_modifier)
            gold = int(base_gold * multiplier * level_modifier)
            
            # Ensure minimum rewards
            xp = max(1, xp)
            gold = max(1, gold)
            
            rewards = {
                'xp': xp,
                'gold': gold
            }
            
            logger.debug(f"Calculated quest rewards: {rewards}")
            return rewards
            
        except Exception as e:
            logger.error(f"Failed to calculate quest rewards: {str(e)}")
            return {'xp': BASE_XP, 'gold': BASE_GOLD}

class GameValidator:
    """Validator for game-specific rules"""
    
    def validate_character_creation(
        self,
        attributes: Dict[str, int],
        race: str,
        abilities: List[str] = None
    ) -> Tuple[bool, List[str]]:
        """Validate character creation parameters"""
        errors = []
        
        try:
            # Validate attributes
            total_points = sum(attributes.values())
            if total_points > ATTRIBUTE_LIMITS['total']:
                errors.append("Total attribute points exceed maximum")
            
            # Validate individual attributes
            for attr, value in attributes.items():
                if value < ATTRIBUTE_LIMITS['min'] or value > ATTRIBUTE_LIMITS['max']:
                    errors.append(f"Invalid {attr} value: {value}")
            
            # Validate race
            if race.lower() not in VALID_RACES:
                errors.append(f"Invalid race: {race}")
            
            # Validate abilities (if provided)
            if abilities:
                # Basic ability validation - could be expanded with actual ability list
                for ability in abilities:
                    if not isinstance(ability, str) or len(ability.strip()) == 0:
                        errors.append(f"Invalid ability: {ability}")
            
            return len(errors) == 0, errors
            
        except Exception as e:
            logger.error(f"Failed to validate character creation: {str(e)}")
            return False, ["Validation error occurred"]
    
    def validate_quest_parameters(
        self,
        level: int,
        difficulty: str,
        rewards: Dict[str, int]
    ) -> Tuple[bool, List[str]]:
        """Validate quest parameters"""
        errors = []
        
        try:
            # Validate level
            if level < 1 or level > 100:
                errors.append("Invalid quest level")
            
            # Validate difficulty
            if difficulty.lower() not in VALID_DIFFICULTIES:
                errors.append(f"Invalid difficulty: {difficulty}")
            
            # Validate rewards
            if 'xp' not in rewards or rewards['xp'] < 1:
                errors.append("Invalid XP reward")
            if 'gold' not in rewards or rewards['gold'] < 0:
                errors.append("Invalid gold reward")
            
            return len(errors) == 0, errors
            
        except Exception as e:
            logger.error(f"Failed to validate quest parameters: {str(e)}")
            return False, ["Validation error occurred"]

    def validate_character_data(
        self,
        name: str,
        race: str,
        background: str,
        attributes: Dict[str, int]
    ) -> List[str]:
        """Validate character data.
        
        Args:
            name: Character name
            race: Character race
            background: Character background
            attributes: Character attributes
            
        Returns:
            List of validation errors
        """
        errors = []
        
        # Validate name
        if not name or len(name) < 2:
            errors.append("Name must be at least 2 characters long")
        
        # Validate race
        if race.lower() not in VALID_RACES:
            errors.append(f"Invalid race: {race}")
        
        # Validate background
        if background.lower() not in VALID_BACKGROUNDS:
            errors.append(f"Invalid background: {background}")
        
        # Validate attributes
        for attr, value in attributes.items():
            if attr not in VALID_ATTRIBUTES:
                errors.append(f"Invalid attribute: {attr}")
            if not isinstance(value, int) or value < 8 or value > 20:
                errors.append(f"Invalid value for {attr}: {value}")
        
        return errors 
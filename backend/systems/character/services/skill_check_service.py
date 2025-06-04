"""
Skill Check Service
------------------
Core skill check mechanics for the Visual DM noncombat skills system.
Handles d20-based skill checks with modifiers, advantage/disadvantage, and caching.
"""

import random
import logging
import time
from typing import Dict, List, Optional, Any, Union, Tuple
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime, timedelta

from backend.systems.character.models.character import Character
from backend.infrastructure.config_loaders.skill_config_loader import skill_config

logger = logging.getLogger(__name__)

class SkillCheckDifficulty(Enum):
    """Standard skill check difficulty classes."""
    TRIVIAL = 5
    EASY = 10
    MEDIUM = 15
    HARD = 20
    VERY_HARD = 25
    NEARLY_IMPOSSIBLE = 30

class SkillCheckType(Enum):
    """Types of skill checks."""
    STANDARD = "standard"      # Single roll against DC
    OPPOSED = "opposed"        # Roll against another character's roll
    EXTENDED = "extended"      # Multiple checks to accumulate successes
    GROUP = "group"           # Multiple characters working together
    PASSIVE = "passive"       # No roll, just score comparison

class AdvantageType(Enum):
    """Advantage/disadvantage states."""
    NORMAL = "normal"
    ADVANTAGE = "advantage"
    DISADVANTAGE = "disadvantage"

@dataclass
class SkillCheckModifiers:
    """Container for skill check modifiers."""
    circumstance_bonus: int = 0
    equipment_bonus: int = 0
    magic_bonus: int = 0
    environmental_modifier: int = 0
    synergy_bonus: int = 0
    time_modifier: int = 0
    
    def total_modifier(self) -> int:
        """Calculate total modifier."""
        return (
            self.circumstance_bonus + 
            self.equipment_bonus + 
            self.magic_bonus + 
            self.environmental_modifier + 
            self.synergy_bonus + 
            self.time_modifier
        )

@dataclass
class SkillCheckResult:
    """Result of a skill check."""
    skill_name: str
    character_id: str
    base_roll: Union[int, List[int]]
    skill_modifier: int
    final_modifiers: int
    total_roll: int
    dc: Optional[int] = None
    success: Optional[bool] = None
    degree_of_success: int = 0
    critical_success: bool = False
    critical_failure: bool = False
    advantage_type: AdvantageType = AdvantageType.NORMAL
    description: str = ""
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class PassiveSkillResult:
    """Result of a passive skill calculation."""
    skill_name: str
    character_id: str
    passive_score: int
    skill_modifier: int
    modifiers: int
    advantage_bonus: int = 0

@dataclass
class GroupSkillResult:
    """Result of a group skill check."""
    skill_name: str
    description: str
    individual_results: List[SkillCheckResult]
    group_success: bool
    success_count: int
    failure_count: int
    average_roll: float
    best_roll: int
    worst_roll: int

class SkillCheckService:
    """Service for handling skill checks and related mechanics."""
    
    def __init__(self):
        # Cache for recent skill checks (for synergy bonuses)
        self.recent_checks: Dict[str, List[SkillCheckResult]] = {}
        self.cache_duration_minutes = 10
        
        # Load configuration
        self.passive_formulas = skill_config.get_passive_skill_formulas()
        self.group_mechanics = skill_config.get_group_check_mechanics()
        self.critical_effects = skill_config.get_critical_effects()
    
    def _get_skill_modifier(self, character: Character, skill_name: str) -> int:
        """Calculate skill modifier for a character."""
        # Get skill info
        skill_info = character.skills.get(skill_name, {})
        
        # Get ability score modifier
        ability_map = {
            # Physical skills
            "athletics": "strength",
            "acrobatics": "dexterity",
            "stealth": "dexterity",
            "sleight_of_hand": "dexterity",
            
            # Mental skills
            "investigation": "intelligence",
            "arcana": "intelligence",
            "history": "intelligence",
            "nature": "intelligence",
            "religion": "intelligence",
            
            # Wisdom skills
            "perception": "wisdom",
            "insight": "wisdom",
            "medicine": "wisdom",
            "survival": "wisdom",
            "animal_handling": "wisdom",
            
            # Social skills
            "persuasion": "charisma",
            "deception": "charisma",
            "intimidation": "charisma",
            "performance": "charisma",
            
            # Other
            "use_magic_device": "charisma",
        }
        
        ability_name = ability_map.get(skill_name, "dexterity")
        ability_score = character.stats.get(ability_name, 10)
        ability_modifier = (ability_score - 10) // 2
        
        # Get proficiency bonus
        proficiency_bonus = (character.level - 1) // 4 + 2
        
        # Calculate skill modifier
        skill_modifier = ability_modifier
        
        if skill_info.get("proficient", False):
            skill_modifier += proficiency_bonus
            
        if skill_info.get("expertise", False):
            skill_modifier += proficiency_bonus  # Double proficiency
            
        # Add any flat bonuses
        skill_modifier += skill_info.get("bonus", 0)
        
        return skill_modifier
    
    def _roll_d20(self, advantage_type: AdvantageType = AdvantageType.NORMAL) -> Union[int, List[int]]:
        """Roll a d20 with advantage/disadvantage."""
        if advantage_type == AdvantageType.ADVANTAGE:
            rolls = [random.randint(1, 20), random.randint(1, 20)]
            return rolls
        elif advantage_type == AdvantageType.DISADVANTAGE:
            rolls = [random.randint(1, 20), random.randint(1, 20)]
            return rolls
        else:
            return random.randint(1, 20)
    
    def _get_effective_roll(self, rolls: Union[int, List[int]], advantage_type: AdvantageType) -> int:
        """Get the effective roll value considering advantage/disadvantage."""
        if isinstance(rolls, int):
            return rolls
        elif advantage_type == AdvantageType.ADVANTAGE:
            return max(rolls)
        elif advantage_type == AdvantageType.DISADVANTAGE:
            return min(rolls)
        else:
            return rolls[0] if rolls else 20
    
    def _calculate_synergy_bonus(self, character: Character, skill_name: str) -> int:
        """Calculate synergy bonus from recent skill uses."""
        # Get synergies from configuration
        synergies = skill_config.get_skill_synergies(skill_name)
        if not synergies:
            return 0
        
        character_id = character.uuid
        if character_id not in self.recent_checks:
            return 0
        
        # Check recent skill checks for synergy
        cutoff_time = datetime.now() - timedelta(minutes=self.cache_duration_minutes)
        recent_skills = []
        
        for check in self.recent_checks[character_id]:
            if check.timestamp > cutoff_time and check.success:
                recent_skills.append(check.skill_name)
        
        # Count synergy bonuses
        synergy_count = 0
        for synergy_skill in synergies:
            if synergy_skill in recent_skills:
                synergy_count += 1
        
        # Cap synergy bonus
        return min(synergy_count * 2, 4)  # +2 per synergy, max +4
    
    def _cache_skill_check(self, character: Character, result: SkillCheckResult) -> None:
        """Cache a skill check result for synergy calculations."""
        character_id = character.uuid
        
        if character_id not in self.recent_checks:
            self.recent_checks[character_id] = []
        
        self.recent_checks[character_id].append(result)
        
        # Clean old entries
        cutoff_time = datetime.now() - timedelta(minutes=self.cache_duration_minutes)
        self.recent_checks[character_id] = [
            check for check in self.recent_checks[character_id]
            if check.timestamp > cutoff_time
        ]
    
    def make_skill_check(
        self,
        character: Character,
        skill_name: str,
        dc: Optional[int] = None,
        modifiers: Optional[SkillCheckModifiers] = None,
        advantage_type: AdvantageType = AdvantageType.NORMAL,
        description: str = ""
    ) -> SkillCheckResult:
        """
        Make a skill check for a character.
        
        Args:
            character: Character making the check
            skill_name: Name of the skill being checked
            dc: Difficulty class (if None, just returns roll info)
            modifiers: Additional modifiers to apply
            advantage_type: Advantage/disadvantage state
            description: Description of the check
            
        Returns:
            SkillCheckResult with all check information
        """
        if modifiers is None:
            modifiers = SkillCheckModifiers()
        
        # Get base skill modifier
        skill_modifier = self._get_skill_modifier(character, skill_name)
        
        # Calculate synergy bonus
        synergy_bonus = self._calculate_synergy_bonus(character, skill_name)
        modifiers.synergy_bonus = synergy_bonus
        
        # Roll the dice
        base_roll = self._roll_d20(advantage_type)
        effective_roll = self._get_effective_roll(base_roll, advantage_type)
        
        # Calculate total
        total_modifiers = modifiers.total_modifier()
        total_roll = effective_roll + skill_modifier + total_modifiers
        
        # Determine success
        success = None
        degree_of_success = 0
        critical_success = False
        critical_failure = False
        
        if dc is not None:
            success = total_roll >= dc
            degree_of_success = total_roll - dc
            
            # Check for critical results using configuration
            critical_config = skill_config.get_critical_effects()
            if effective_roll == 20:
                critical_success = True
                if "natural_20_effects" in critical_config:
                    nat20_effects = critical_config["natural_20_effects"]
                    min_bonus = nat20_effects.get("minimum_degree_bonus", 10)
                    degree_of_success = max(degree_of_success, min_bonus)
                    success = True  # Natural 20 always succeeds
            elif effective_roll == 1:
                critical_failure = True
                if "natural_1_effects" in critical_config:
                    nat1_effects = critical_config["natural_1_effects"]
                    min_penalty = nat1_effects.get("minimum_degree_penalty", -10)
                    degree_of_success = min(degree_of_success, min_penalty)
        
        # Create result
        result = SkillCheckResult(
            skill_name=skill_name,
            character_id=character.uuid,
            base_roll=base_roll,
            skill_modifier=skill_modifier,
            final_modifiers=total_modifiers,
            total_roll=total_roll,
            dc=dc,
            success=success,
            degree_of_success=degree_of_success,
            critical_success=critical_success,
            critical_failure=critical_failure,
            advantage_type=advantage_type,
            description=description or f"{skill_name.title()} check"
        )
        
        # Cache the result
        self._cache_skill_check(character, result)
        
        return result
    
    def get_passive_skill_score(
        self,
        character: Character,
        skill_name: str,
        modifiers: Optional[SkillCheckModifiers] = None,
        advantage_type: AdvantageType = AdvantageType.NORMAL
    ) -> PassiveSkillResult:
        """
        Calculate passive skill score.
        
        Args:
            character: Character whose passive skill to calculate
            skill_name: Name of the skill
            modifiers: Additional modifiers
            advantage_type: Advantage state affects passive scores
            
        Returns:
            PassiveSkillResult with passive score information
        """
        if modifiers is None:
            modifiers = SkillCheckModifiers()
        
        # Get base passive score from configuration
        formulas = skill_config.get_passive_skill_formulas()
        base_passive = formulas.get("base_passive", 10)
        
        # Get skill modifier
        skill_modifier = self._get_skill_modifier(character, skill_name)
        
        # Calculate advantage bonus from configuration
        advantage_bonus = 0
        if advantage_type == AdvantageType.ADVANTAGE:
            advantage_bonus = formulas.get("advantage_bonus", 5)
        elif advantage_type == AdvantageType.DISADVANTAGE:
            advantage_bonus = formulas.get("disadvantage_penalty", -5)
        
        # Calculate total passive score
        total_modifiers = modifiers.total_modifier()
        passive_score = base_passive + skill_modifier + total_modifiers + advantage_bonus
        
        return PassiveSkillResult(
            skill_name=skill_name,
            character_id=character.uuid,
            passive_score=passive_score,
            skill_modifier=skill_modifier,
            modifiers=total_modifiers,
            advantage_bonus=advantage_bonus
        )
    
    def make_opposed_skill_check(
        self,
        character1: Character,
        character2: Character,
        skill1: str,
        skill2: str = None,
        modifiers1: Optional[SkillCheckModifiers] = None,
        modifiers2: Optional[SkillCheckModifiers] = None,
        description: str = ""
    ) -> Tuple[SkillCheckResult, SkillCheckResult, bool]:
        """
        Make an opposed skill check between two characters.
        
        Args:
            character1: First character
            character2: Second character  
            skill1: Skill for first character
            skill2: Skill for second character (defaults to skill1)
            modifiers1: Modifiers for first character
            modifiers2: Modifiers for second character
            description: Description of the contest
            
        Returns:
            Tuple of (char1_result, char2_result, char1_wins)
        """
        if skill2 is None:
            skill2 = skill1
        
        # Make both checks
        check1 = self.make_skill_check(
            character=character1,
            skill_name=skill1,
            modifiers=modifiers1,
            description=f"{description} ({character1.name})"
        )
        
        check2 = self.make_skill_check(
            character=character2,
            skill_name=skill2,
            modifiers=modifiers2,
            description=f"{description} ({character2.name})"
        )
        
        # Determine winner
        char1_wins = check1.total_roll > check2.total_roll
        
        # If tied, higher skill modifier wins
        if check1.total_roll == check2.total_roll:
            char1_wins = check1.skill_modifier > check2.skill_modifier
        
        # Update success status
        check1.success = char1_wins
        check2.success = not char1_wins
        
        return check1, check2, char1_wins
    
    def make_group_skill_check(
        self,
        characters: List[Character],
        skill_name: str,
        dc: int,
        modifiers: Optional[List[SkillCheckModifiers]] = None,
        description: str = "",
        cooperation: bool = True
    ) -> GroupSkillResult:
        """
        Make a group skill check where multiple characters work together.
        
        Args:
            characters: List of characters participating
            skill_name: Skill being used
            dc: Difficulty class
            modifiers: List of modifiers for each character
            description: Description of the group effort
            cooperation: Whether characters can help each other
            
        Returns:
            GroupSkillResult with group and individual results
        """
        if modifiers is None:
            modifiers = [SkillCheckModifiers() for _ in characters]
        
        # Pad modifiers list if needed
        while len(modifiers) < len(characters):
            modifiers.append(SkillCheckModifiers())
        
        # Get group mechanics from configuration
        group_config = skill_config.get_group_check_mechanics()
        min_participants = group_config.get("minimum_participants", 2)
        max_participants = group_config.get("maximum_participants", 8)
        success_threshold = group_config.get("success_threshold_percentage", 0.5)
        leader_bonus = group_config.get("leader_bonus", 2)
        cooperation_bonus = group_config.get("cooperation_bonus_per_helper", 1)
        max_cooperation = group_config.get("maximum_cooperation_bonus", 4)
        
        # Limit participants
        if len(characters) > max_participants:
            characters = characters[:max_participants]
            modifiers = modifiers[:max_participants]
        
        individual_results = []
        
        # Find the leader (highest skill modifier)
        leader_idx = 0
        best_skill_mod = -999
        for i, char in enumerate(characters):
            skill_mod = self._get_skill_modifier(char, skill_name)
            if skill_mod > best_skill_mod:
                best_skill_mod = skill_mod
                leader_idx = i
        
        # Make individual checks
        for i, (character, char_modifiers) in enumerate(zip(characters, modifiers)):
            # Apply leader bonus
            if i == leader_idx:
                char_modifiers.circumstance_bonus += leader_bonus
            
            # Apply cooperation bonus for helpers
            if cooperation and i != leader_idx:
                helpers = len(characters) - 1  # Everyone except this character
                coop_bonus = min(helpers * cooperation_bonus, max_cooperation)
                char_modifiers.circumstance_bonus += coop_bonus
            
            result = self.make_skill_check(
                character=character,
                skill_name=skill_name,
                dc=dc,
                modifiers=char_modifiers,
                description=f"{description} - {character.name}"
            )
            
            individual_results.append(result)
        
        # Calculate group results
        success_count = sum(1 for result in individual_results if result.success)
        failure_count = len(individual_results) - success_count
        
        # Group succeeds if enough individuals succeed
        required_successes = max(1, int(len(characters) * success_threshold))
        group_success = success_count >= required_successes
        
        # Calculate statistics
        total_rolls = [result.total_roll for result in individual_results]
        average_roll = sum(total_rolls) / len(total_rolls)
        best_roll = max(total_rolls)
        worst_roll = min(total_rolls)
        
        return GroupSkillResult(
            skill_name=skill_name,
            description=description,
            individual_results=individual_results,
            group_success=group_success,
            success_count=success_count,
            failure_count=failure_count,
            average_roll=average_roll,
            best_roll=best_roll,
            worst_roll=worst_roll
        )

# Global service instance
skill_check_service = SkillCheckService() 
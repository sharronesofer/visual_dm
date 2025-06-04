"""
Noncombat Skills Service
-----------------------
Complete implementation of noncombat skill mechanics for Visual DM.
This service handles all skill checks and their environmental, social, 
and contextual modifiers while maintaining separation of concerns.
"""

import logging
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass
from enum import Enum
import random
import math

# Import system-specific models and services
from backend.systems.character.models.character import Character
from backend.systems.character.services.skill_check_service import SkillCheckService, SkillCheckResult, AdvantageType
from backend.infrastructure.config_loaders.skill_config_loader import skill_config

logger = logging.getLogger(__name__)

class PerceptionType(Enum):
    """Types of perception checks."""
    VISUAL = "visual"           # Spot checks, noticing visual details
    AUDITORY = "auditory"       # Listen checks, hearing sounds
    TACTILE = "tactile"         # Touch, feeling vibrations
    SEARCH = "search"           # Active searching for hidden things
    INSIGHT = "insight"         # Reading people, sensing motives
    INVESTIGATION = "investigation"  # Detailed examination and analysis

class StealthContext(Enum):
    """Types of stealth checks."""
    HIDING = "hiding"                    # Staying hidden while stationary
    MOVING_SILENTLY = "moving_silently"  # Moving without making noise
    SHADOWING = "shadowing"              # Following someone undetected
    INFILTRATION = "infiltration"        # Sneaking into a location
    PICKPOCKETING = "pickpocketing"      # Stealing from someone
    SLEIGHT_OF_HAND = "sleight_of_hand"  # Concealing actions

class SocialInteractionType(Enum):
    """Types of social interactions."""
    PERSUASION = "persuasion"       # Convincing with logic and charm
    DECEPTION = "deception"         # Lying or misleading
    INTIMIDATION = "intimidation"   # Using fear or threats
    DIPLOMACY = "diplomacy"         # Formal negotiation
    GATHER_INFO = "gather_information"  # Seeking information
    PERFORMANCE = "performance"     # Entertainment or distraction

@dataclass
class PerceptionResult:
    """Result of a perception check."""
    check_result: SkillCheckResult
    perception_type: PerceptionType
    detected_objects: List[Dict[str, Any]]
    missed_objects: List[Dict[str, Any]]
    additional_info: Dict[str, str]

@dataclass
class StealthResult:
    """Result of a stealth check."""
    check_result: SkillCheckResult
    stealth_context: StealthContext
    detected_by: List[str]  # UUIDs of characters who detected the attempt
    stealth_level: int      # How well hidden (0-30+)
    duration: Optional[int] = None  # Duration in minutes if applicable

@dataclass
class SocialResult:
    """Result of a social interaction."""
    check_result: SkillCheckResult
    interaction_type: SocialInteractionType
    target_reaction: str
    attitude_change: int    # Change in target's attitude toward character
    information_gained: List[str]
    consequences: List[str]

class NoncombatSkillService:
    """Service for handling specific noncombat skill mechanics."""
    
    def __init__(self):
        # Load modifiers from configuration
        self.perception_modifiers = skill_config.get_perception_modifiers()
        self.stealth_modifiers = skill_config.get_stealth_modifiers()
        self.social_modifiers = skill_config.get_social_modifiers()
        
        # Environmental modifiers for perception
        self.environmental_modifiers = skill_config.get_environmental_modifiers()
    
    # === PERCEPTION MECHANICS ===
    
    def make_perception_check(
        self,
        character: Character,
        perception_type: PerceptionType,
        hidden_objects: List[Dict[str, Any]],
        environmental_conditions: List[str] = None,
        dc_override: Optional[int] = None
    ) -> PerceptionResult:
        """
        Make a perception check to notice hidden objects or details.
        
        Args:
            character: Character making the check
            perception_type: Type of perception being used
            hidden_objects: List of objects that might be noticed
            environmental_conditions: List of environmental condition keys
            dc_override: Override the DC calculation
            
        Returns:
            PerceptionResult with detected and missed objects
        """
        if environmental_conditions is None:
            environmental_conditions = []
        
        # Calculate environmental modifiers using configuration
        env_modifier = skill_config.calculate_modifier_from_conditions("lighting", environmental_conditions)
        env_modifier += skill_config.calculate_modifier_from_conditions("weather", environmental_conditions)
        env_modifier += skill_config.calculate_modifier_from_conditions("terrain", environmental_conditions)
        env_modifier += skill_config.calculate_modifier_from_conditions("sound", environmental_conditions)
        
        modifiers = SkillCheckModifiers(environmental_modifier=env_modifier)
        
        # Determine base skill for perception type
        skill_map = {
            PerceptionType.VISUAL: "perception",
            PerceptionType.AUDITORY: "perception", 
            PerceptionType.TACTILE: "perception",
            PerceptionType.SEARCH: "search",
            PerceptionType.INSIGHT: "insight",
            PerceptionType.INVESTIGATION: "investigation"
        }
        
        skill_name = skill_map.get(perception_type, "perception")
        
        detected_objects = []
        missed_objects = []
        additional_info = {}
        
        # Check each hidden object
        for obj in hidden_objects:
            obj_dc = dc_override or obj.get("dc", skill_config.get_difficulty_dc("medium"))
            
            # Apply object-specific modifiers
            obj_modifiers = SkillCheckModifiers(
                environmental_modifier=env_modifier + obj.get("modifier", 0)
            )
            
            check_result = skill_check_service.make_skill_check(
                character=character,
                skill_name=skill_name,
                dc=obj_dc,
                modifiers=obj_modifiers,
                description=f"Perception check to notice {obj.get('name', 'hidden object')}"
            )
            
            if check_result.success:
                detected_objects.append(obj)
                
                # Add details based on degree of success
                if check_result.degree_of_success >= 10:
                    additional_info[obj.get("id", "unknown")] = obj.get("detailed_info", "You notice additional details")
                elif check_result.degree_of_success >= 5:
                    additional_info[obj.get("id", "unknown")] = obj.get("basic_info", "You notice something interesting")
            else:
                missed_objects.append(obj)
        
        # Make one representative check for the overall result
        if hidden_objects:
            avg_dc = sum(obj.get("dc", skill_config.get_difficulty_dc("medium")) for obj in hidden_objects) / len(hidden_objects)
        else:
            avg_dc = skill_config.get_difficulty_dc("medium")
            
        overall_check = skill_check_service.make_skill_check(
            character=character,
            skill_name=skill_name,
            dc=int(avg_dc),
            modifiers=modifiers,
            description=f"{perception_type.value.title()} perception check"
        )
        
        return PerceptionResult(
            check_result=overall_check,
            perception_type=perception_type,
            detected_objects=detected_objects,
            missed_objects=missed_objects,
            additional_info=additional_info
        )
    
    def get_passive_perception(
        self,
        character: Character,
        environmental_conditions: List[str] = None
    ) -> int:
        """Get character's passive perception score."""
        if environmental_conditions is None:
            environmental_conditions = []
        
        # Calculate environmental modifiers using configuration
        env_modifier = skill_config.calculate_modifier_from_conditions("lighting", environmental_conditions)
        env_modifier += skill_config.calculate_modifier_from_conditions("weather", environmental_conditions)
        env_modifier += skill_config.calculate_modifier_from_conditions("terrain", environmental_conditions)
        
        modifiers = SkillCheckModifiers(environmental_modifier=env_modifier)
        
        passive_score = skill_check_service.get_passive_skill_score(
            character=character,
            skill_name="perception",
            modifiers=modifiers
        )
        
        return passive_score.passive_score
    
    # === STEALTH MECHANICS ===
    
    def make_stealth_check(
        self,
        character: Character,
        stealth_context: StealthContext,
        observers: List[Character],
        environmental_conditions: List[str] = None,
        duration_minutes: Optional[int] = None
    ) -> StealthResult:
        """
        Make a stealth check against one or more observers.
        
        Args:
            character: Character attempting stealth
            stealth_context: Type of stealth being attempted
            observers: Characters who might detect the attempt
            environmental_conditions: Environmental condition keys
            duration_minutes: How long to maintain stealth
            
        Returns:
            StealthResult with detection information
        """
        if environmental_conditions is None:
            environmental_conditions = []
        
        # Calculate stealth modifiers from configuration
        stealth_config = skill_config.get_stealth_modifiers()
        env_modifier = 0
        
        for condition in environmental_conditions:
            for category, modifiers in stealth_config.items():
                if condition in modifiers:
                    env_modifier += modifiers[condition]
                    break
        
        modifiers = SkillCheckModifiers(environmental_modifier=env_modifier)
        
        # Determine skill based on context
        skill_map = {
            StealthContext.HIDING: "stealth",
            StealthContext.MOVING_SILENTLY: "stealth",
            StealthContext.SHADOWING: "stealth",
            StealthContext.INFILTRATION: "stealth",
            StealthContext.PICKPOCKETING: "sleight_of_hand",
            StealthContext.SLEIGHT_OF_HAND: "sleight_of_hand"
        }
        
        skill_name = skill_map.get(stealth_context, "stealth")
        
        # Make stealth check
        stealth_check = skill_check_service.make_skill_check(
            character=character,
            skill_name=skill_name,
            modifiers=modifiers,
            description=f"{stealth_context.value.replace('_', ' ').title()} attempt"
        )
        
        detected_by = []
        
        # Check against each observer
        for observer in observers:
            # Observers use passive perception by default
            observer_perception = self.get_passive_perception(observer, environmental_conditions)
            
            # Special cases for active perception
            if stealth_context in [StealthContext.PICKPOCKETING, StealthContext.SLEIGHT_OF_HAND]:
                # These require opposed checks
                observer_check = skill_check_service.make_skill_check(
                    character=observer,
                    skill_name="perception",
                    description=f"Noticing {character.name}'s {stealth_context.value}"
                )
                observer_perception = observer_check.total_roll
            
            # Compare stealth vs perception
            if stealth_check.total_roll < observer_perception:
                detected_by.append(observer.uuid)
        
        # Determine stealth level based on roll
        stealth_level = max(0, stealth_check.total_roll - 10)  # Base 10, higher is better
        
        # Apply duration modifiers
        if duration_minutes and duration_minutes > 10:
            # Long-term stealth is harder
            time_penalty = (duration_minutes // 10) * 2
            stealth_level = max(0, stealth_level - time_penalty)
        
        return StealthResult(
            check_result=stealth_check,
            stealth_context=stealth_context,
            detected_by=detected_by,
            stealth_level=stealth_level,
            duration=duration_minutes
        )
    
    # === SOCIAL INTERACTION MECHANICS ===
    
    def make_social_check(
        self,
        character: Character,
        target: Character,
        interaction_type: SocialInteractionType,
        goal: str,
        social_conditions: List[str] = None,
        dc_override: Optional[int] = None
    ) -> SocialResult:
        """
        Make a social interaction check.
        
        Args:
            character: Character making the social attempt
            target: Target of the social interaction
            interaction_type: Type of social interaction
            goal: What the character is trying to accomplish
            social_conditions: Social condition modifiers
            dc_override: Override the DC calculation
            
        Returns:
            SocialResult with interaction outcome
        """
        if social_conditions is None:
            social_conditions = []
        
        # Calculate social modifiers from configuration
        social_config = skill_config.get_social_modifiers()
        social_modifier = 0
        
        for condition in social_conditions:
            for category, modifiers in social_config.items():
                if condition in modifiers:
                    social_modifier += modifiers[condition]
                    break
        
        modifiers = SkillCheckModifiers(circumstance_bonus=social_modifier)
        
        # Determine skill and base DC
        skill_map = {
            SocialInteractionType.PERSUASION: "persuasion",
            SocialInteractionType.DECEPTION: "deception",
            SocialInteractionType.INTIMIDATION: "intimidation",
            SocialInteractionType.DIPLOMACY: "diplomacy",
            SocialInteractionType.GATHER_INFO: "gather_information",
            SocialInteractionType.PERFORMANCE: "performance"
        }
        
        skill_name = skill_map.get(interaction_type, "persuasion")
        
        # Calculate DC based on target's wisdom and the difficulty of the request
        if dc_override:
            dc = dc_override
        else:
            # Use configuration for DC calculation
            dc_rules = skill_config.get_dc_calculation_rules("base_social_dc")
            base_dc = 10 + target.stats.get("wisdom", 10) // 2  # Base on target's wisdom
            
            # Adjust based on what's being asked
            goal_modifiers = {
                "simple_request": 0,
                "reasonable_favor": 5,
                "significant_favor": 10,
                "dangerous_request": 15,
                "betrayal": 20,
                "suicidal": 25
            }
            
            goal_difficulty = 0
            for goal_type, modifier in goal_modifiers.items():
                if goal_type in goal.lower():
                    goal_difficulty = modifier
                    break
            
            dc = base_dc + goal_difficulty
        
        # Make the social check
        social_check = skill_check_service.make_skill_check(
            character=character,
            skill_name=skill_name,
            dc=dc,
            modifiers=modifiers,
            description=f"{interaction_type.value.title()} attempt: {goal}"
        )
        
        # Determine results based on success/failure and degree
        attitude_change = 0
        information_gained = []
        consequences = []
        
        if social_check.success:
            # Success - positive outcome
            if social_check.degree_of_success >= 10:
                target_reaction = "Very Positive - Enthusiastic agreement"
                attitude_change = 20
                information_gained.append("Gained valuable additional information")
            elif social_check.degree_of_success >= 5:
                target_reaction = "Positive - Willing agreement" 
                attitude_change = 10
                information_gained.append("Gained some extra information")
            else:
                target_reaction = "Neutral - Reluctant agreement"
                attitude_change = 5
            
            # Special success outcomes by interaction type
            if interaction_type == SocialInteractionType.GATHER_INFO:
                information_gained.extend([
                    "Local rumors and gossip",
                    "Information about local personalities",
                    "Directions and local knowledge"
                ])
            elif interaction_type == SocialInteractionType.INTIMIDATION:
                consequences.append("Target may harbor resentment")
                attitude_change = max(0, attitude_change - 5)  # Intimidation can reduce long-term attitude
        
        else:
            # Failure - negative outcome
            if social_check.degree_of_success <= -10:
                target_reaction = "Very Negative - Hostile response"
                attitude_change = -20
                consequences.append("Target becomes actively hostile")
            elif social_check.degree_of_success <= -5:
                target_reaction = "Negative - Annoyed refusal"
                attitude_change = -10
                consequences.append("Target is annoyed and less helpful")
            else:
                target_reaction = "Neutral - Polite refusal"
                attitude_change = -5
            
            # Special failure outcomes
            if interaction_type == SocialInteractionType.DECEPTION and social_check.critical_failure:
                consequences.append("Target realizes you were lying")
                attitude_change -= 10
            elif interaction_type == SocialInteractionType.INTIMIDATION and not social_check.success:
                consequences.append("Target sees through intimidation attempt")
                attitude_change -= 5
        
        return SocialResult(
            check_result=social_check,
            interaction_type=interaction_type,
            target_reaction=target_reaction,
            attitude_change=attitude_change,
            information_gained=information_gained,
            consequences=consequences
        )
    
    # === INVESTIGATION AND KNOWLEDGE MECHANICS ===
    
    def make_investigation_check(
        self,
        character: Character,
        investigation_target: str,
        time_spent_minutes: int = 10,
        available_clues: List[Dict[str, Any]] = None,
        environmental_conditions: List[str] = None
    ) -> Tuple[SkillCheckResult, List[Dict[str, Any]]]:
        """
        Make an investigation check to gather information and clues.
        
        Args:
            character: Character investigating
            investigation_target: What's being investigated
            time_spent_minutes: Time spent on investigation
            available_clues: Clues that can potentially be found
            environmental_conditions: Environmental modifiers
            
        Returns:
            Tuple of (check result, discovered clues)
        """
        if available_clues is None:
            available_clues = []
        if environmental_conditions is None:
            environmental_conditions = []
        
        # Time modifiers from configuration
        time_factors = skill_config.get_environmental_modifiers("time_factors")
        time_modifier = 0
        if time_spent_minutes >= 60:
            time_modifier = time_factors.get("careful", 2)  # Thorough investigation
        elif time_spent_minutes >= 30:
            time_modifier = time_factors.get("careful", 2) // 2  # Careful investigation
        elif time_spent_minutes < 5:
            time_modifier = time_factors.get("rushed", -5)  # Rushed investigation
        
        env_modifier = skill_config.calculate_modifier_from_conditions("lighting", environmental_conditions)
        env_modifier += skill_config.calculate_modifier_from_conditions("weather", environmental_conditions)
        
        modifiers = SkillCheckModifiers(
            time_modifier=time_modifier,
            environmental_modifier=env_modifier
        )
        
        # Base DC depends on complexity of investigation
        base_dc = skill_config.get_difficulty_dc("medium")
        
        investigation_check = skill_check_service.make_skill_check(
            character=character,
            skill_name="investigation",
            dc=base_dc,
            modifiers=modifiers,
            description=f"Investigating {investigation_target}"
        )
        
        discovered_clues = []
        
        # Determine which clues are found based on roll result
        for clue in available_clues:
            clue_dc = clue.get("dc", base_dc)
            if investigation_check.total_roll >= clue_dc:
                discovered_clues.append(clue)
        
        # Add bonus clues for exceptional success
        if investigation_check.critical_success or investigation_check.degree_of_success >= 15:
            discovered_clues.append({
                "id": "bonus_insight",
                "name": "Additional Insight",
                "description": "Your thorough investigation reveals subtle details others might miss",
                "type": "insight"
            })
        
        return investigation_check, discovered_clues
    
    # === UTILITY METHODS ===
    
    def calculate_sneak_attack_viability(
        self,
        attacker: Character,
        target: Character,
        environmental_conditions: List[str] = None
    ) -> Tuple[bool, str]:
        """
        Determine if a character can perform a sneak attack.
        
        Args:
            attacker: Character attempting sneak attack
            target: Target of the attack
            environmental_conditions: Environmental conditions
            
        Returns:
            Tuple of (can_sneak_attack, reason)
        """
        # Check if attacker is hidden
        stealth_result = self.make_stealth_check(
            character=attacker,
            stealth_context=StealthContext.HIDING,
            observers=[target],
            environmental_conditions=environmental_conditions
        )
        
        if target.uuid in stealth_result.detected_by:
            return False, "Target is aware of your presence"
        
        # Check if target is distracted or unaware
        target_perception = self.get_passive_perception(target, environmental_conditions)
        
        if stealth_result.check_result.total_roll >= target_perception + 5:
            return True, "Target is completely unaware - sneak attack possible"
        elif stealth_result.check_result.total_roll >= target_perception:
            return True, "Target is distracted - sneak attack possible"
        else:
            return False, "Target is too alert for a sneak attack"

# Global service instance
noncombat_skill_service = NoncombatSkillService() 
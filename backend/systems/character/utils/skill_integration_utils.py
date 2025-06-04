"""
Skill Integration Utilities
---------------------------
Utilities for integrating noncombat skills with other game systems.
Connects skills to dialogue, quests, exploration, NPC interactions, and world events.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple, Union
from enum import Enum
from dataclasses import dataclass

from backend.systems.character.models.character import Character
from backend.systems.character.services.skill_check_service import skill_check_service, SkillCheckDifficulty
from backend.systems.character.services.noncombat_skills import (
    noncombat_skill_service, PerceptionType, StealthContext, SocialInteractionType
)

logger = logging.getLogger(__name__)

class SkillCheckTrigger(Enum):
    """When skill checks can be triggered."""
    AUTOMATIC = "automatic"      # Triggered automatically by the system
    PLAYER_INITIATED = "player_initiated"  # Player chooses to make the check
    DIALOGUE_OPTION = "dialogue_option"    # Available as dialogue option
    EXPLORATION = "exploration"   # During exploration/movement
    QUEST_OBJECTIVE = "quest_objective"    # Required for quest progression
    ENVIRONMENTAL = "environmental"        # Triggered by environmental conditions

@dataclass
class SkillCheckOpportunity:
    """Represents an opportunity to use a skill."""
    skill_name: str
    trigger_type: SkillCheckTrigger
    context: str
    description: str
    dc: int
    success_outcome: str
    failure_outcome: str
    prerequisites: List[str] = None
    rewards: Dict[str, Any] = None
    consequences: Dict[str, Any] = None

@dataclass
class DialogueSkillOption:
    """A skill-based dialogue option."""
    skill_name: str
    option_text: str
    dc: int
    success_response: str
    failure_response: str
    attitude_change_success: int = 0
    attitude_change_failure: int = 0
    unlocks_information: List[str] = None
    requires_previous_success: bool = False

@dataclass
class ExplorationSkillEvent:
    """A skill-based exploration event."""
    event_id: str
    trigger_skill: str
    trigger_dc: int
    location_context: str
    description: str
    success_outcome: Dict[str, Any]
    failure_outcome: Dict[str, Any]
    repeatable: bool = False
    cooldown_hours: int = 0

class SkillIntegrationService:
    """Service for integrating skills with other game systems."""
    
    def __init__(self):
        # Cache for recently triggered skill events
        self.recent_skill_events = {}
        
        # Predefined skill opportunities for common scenarios
        self.common_skill_opportunities = {
            "tavern_information_gathering": SkillCheckOpportunity(
                skill_name="gather_information",
                trigger_type=SkillCheckTrigger.PLAYER_INITIATED,
                context="tavern",
                description="Mingle with locals to gather rumors and information",
                dc=SkillCheckDifficulty.EASY.value,
                success_outcome="Learn local rumors, trade routes, and political gossip",
                failure_outcome="Pick up only common knowledge or misinformation",
                rewards={"information": "local_rumors", "xp": 25}
            ),
            
            "picklock_door": SkillCheckOpportunity(
                skill_name="open_lock",
                trigger_type=SkillCheckTrigger.PLAYER_INITIATED,
                context="locked_door",
                description="Attempt to pick the lock",
                dc=SkillCheckDifficulty.MEDIUM.value,
                success_outcome="The lock clicks open quietly",
                failure_outcome="The lock resists your efforts",
                consequences={"failure": {"noise": "lockpicking_noise", "time_spent": 10}}
            ),
            
            "search_room": SkillCheckOpportunity(
                skill_name="search",
                trigger_type=SkillCheckTrigger.PLAYER_INITIATED,
                context="exploration",
                description="Thoroughly search the area for hidden items or clues",
                dc=SkillCheckDifficulty.MEDIUM.value,
                success_outcome="Discover hidden items, secret compartments, or clues",
                failure_outcome="Find only obvious items or miss important details",
                rewards={"xp": 15}
            )
        }
    
    # === DIALOGUE INTEGRATION ===
    
    def get_dialogue_skill_options(
        self,
        character: Character,
        npc_data: Dict[str, Any],
        conversation_context: str
    ) -> List[DialogueSkillOption]:
        """
        Generate skill-based dialogue options for a conversation.
        
        Args:
            character: Character in the conversation
            npc_data: NPC data including personality, attitude, etc.
            conversation_context: Context of the conversation
            
        Returns:
            List of available skill-based dialogue options
        """
        options = []
        
        # Base DC calculation from NPC data
        npc_wisdom = npc_data.get("attributes", {}).get("wisdom", 10)
        base_dc = 10 + (npc_wisdom - 10) // 2
        
        # Current attitude affects DC
        attitude = npc_data.get("attitude_towards_player", 0)
        attitude_modifier = -attitude // 10  # -1 DC per 10 attitude points
        
        # Persuasion option (usually available)
        if character.get_skill_proficiency("persuasion").get("proficient", False):
            options.append(DialogueSkillOption(
                skill_name="persuasion",
                option_text="[Persuasion] Try to convince them with logical arguments",
                dc=base_dc + attitude_modifier,
                success_response="They seem convinced by your reasoning",
                failure_response="They remain unconvinced by your arguments",
                attitude_change_success=10,
                attitude_change_failure=-5,
                unlocks_information=["reasoning_based_info"]
            ))
        
        # Deception option (if relevant to context)
        if "lie" in conversation_context or "deceive" in conversation_context:
            if character.get_skill_proficiency("deception").get("proficient", False):
                options.append(DialogueSkillOption(
                    skill_name="deception",
                    option_text="[Deception] Lie to get what you want",
                    dc=base_dc + attitude_modifier + 5,  # Lies are harder
                    success_response="They believe your story completely",
                    failure_response="You can tell they don't believe you",
                    attitude_change_success=5,
                    attitude_change_failure=-15,
                    unlocks_information=["deception_based_info"]
                ))
        
        # Intimidation option (if character has relevant skills/reputation)
        if character.get_skill_proficiency("intimidation").get("proficient", False):
            strength_mod = (character.stats.get("strength", 10) - 10) // 2
            intimidation_dc = base_dc + attitude_modifier - strength_mod
            
            options.append(DialogueSkillOption(
                skill_name="intimidation",
                option_text="[Intimidation] Threaten them into compliance",
                dc=intimidation_dc,
                success_response="They submit to your demands out of fear",
                failure_response="They see through your intimidation attempt",
                attitude_change_success=-5,  # Fear-based compliance hurts relationship
                attitude_change_failure=-20,
                unlocks_information=["intimidation_based_info"]
            ))
        
        # Insight option (reading motives)
        if character.get_skill_proficiency("insight").get("proficient", False):
            options.append(DialogueSkillOption(
                skill_name="insight",
                option_text="[Insight] Try to read their true intentions",
                dc=base_dc + 5,
                success_response="You sense their true feelings about the matter",
                failure_response="You can't get a clear read on their intentions",
                attitude_change_success=0,
                attitude_change_failure=0,
                unlocks_information=["true_motivations", "hidden_agenda"]
            ))
        
        # Information gathering option
        if character.get_skill_proficiency("gather_information").get("proficient", False):
            options.append(DialogueSkillOption(
                skill_name="gather_information",
                option_text="[Gather Information] Ask about local happenings",
                dc=base_dc - 5,  # Easier than persuasion
                success_response="They share interesting local information",
                failure_response="They only tell you things everyone knows",
                attitude_change_success=5,
                attitude_change_failure=0,
                unlocks_information=["local_events", "rumors", "gossip"]
            ))
        
        return options
    
    def execute_dialogue_skill_check(
        self,
        character: Character,
        target_npc: Dict[str, Any],
        dialogue_option: DialogueSkillOption
    ) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Execute a skill check from a dialogue option.
        
        Args:
            character: Character making the check
            target_npc: NPC being interacted with
            dialogue_option: The dialogue option being executed
            
        Returns:
            Tuple of (success, response_text, consequences)
        """
        # Convert to social interaction type
        skill_to_social_type = {
            "persuasion": SocialInteractionType.PERSUASION,
            "deception": SocialInteractionType.DECEPTION,
            "intimidation": SocialInteractionType.INTIMIDATION,
            "diplomacy": SocialInteractionType.DIPLOMACY,
            "gather_information": SocialInteractionType.GATHER_INFO
        }
        
        interaction_type = skill_to_social_type.get(dialogue_option.skill_name, SocialInteractionType.PERSUASION)
        
        # Create target character object for the social check
        target_char = Character()
        target_char.name = target_npc.get("name", "Unknown")
        target_char.stats = target_npc.get("attributes", {"wisdom": 10})
        target_char.uuid = target_npc.get("id", "npc_temp")
        
        # Determine social conditions
        social_conditions = []
        
        # Add conditions based on NPC attitude and context
        attitude = target_npc.get("attitude_towards_player", 0)
        if attitude > 20:
            social_conditions.append("good_reputation")
        elif attitude < -20:
            social_conditions.append("hostile_reputation")
        
        # Make the social check
        social_result = noncombat_skill_service.make_social_check(
            character=character,
            target=target_char,
            interaction_type=interaction_type,
            goal=dialogue_option.option_text,
            social_conditions=social_conditions,
            dc_override=dialogue_option.dc
        )
        
        # Determine outcome
        success = social_result.check_result.success
        
        if success:
            response_text = dialogue_option.success_response
            attitude_change = dialogue_option.attitude_change_success
            information = dialogue_option.unlocks_information or []
        else:
            response_text = dialogue_option.failure_response
            attitude_change = dialogue_option.attitude_change_failure
            information = []
        
        consequences = {
            "attitude_change": attitude_change,
            "information_gained": information,
            "skill_used": dialogue_option.skill_name,
            "roll_result": social_result.check_result.total_roll,
            "dc": dialogue_option.dc
        }
        
        return success, response_text, consequences
    
    # === EXPLORATION INTEGRATION ===
    
    def check_for_exploration_skill_events(
        self,
        character: Character,
        location_id: str,
        movement_type: str = "walking"
    ) -> List[ExplorationSkillEvent]:
        """
        Check for skill-based events during exploration.
        
        Args:
            character: Character exploring
            location_id: ID of the current location
            movement_type: How the character is moving (walking, running, sneaking)
            
        Returns:
            List of available exploration skill events
        """
        events = []
        
        # Passive perception checks for noticing things
        passive_perception = noncombat_skill_service.get_passive_perception(character)
        
        # Example events based on location and skills
        if location_id.startswith("forest"):
            # Forest-specific events
            if character.get_skill_proficiency("survival").get("proficient", False):
                events.append(ExplorationSkillEvent(
                    event_id=f"forest_tracking_{location_id}",
                    trigger_skill="survival",
                    trigger_dc=SkillCheckDifficulty.MEDIUM.value,
                    location_context="forest",
                    description="You notice animal tracks that might lead to interesting discoveries",
                    success_outcome={
                        "discovery": "animal_den",
                        "loot": ["animal_hide", "herbs"],
                        "xp": 50
                    },
                    failure_outcome={
                        "consequence": "get_lost",
                        "time_penalty": 30
                    },
                    repeatable=True,
                    cooldown_hours=24
                ))
            
            if passive_perception >= 15:
                events.append(ExplorationSkillEvent(
                    event_id=f"hidden_grove_{location_id}",
                    trigger_skill="perception",
                    trigger_dc=SkillCheckDifficulty.HARD.value,
                    location_context="forest",
                    description="Something seems unusual about this part of the forest",
                    success_outcome={
                        "discovery": "hidden_grove",
                        "loot": ["rare_herbs", "magic_spring"],
                        "xp": 100
                    },
                    failure_outcome={"consequence": "nothing_found"},
                    repeatable=False
                ))
        
        elif location_id.startswith("city") or location_id.startswith("town"):
            # Urban events
            if character.get_skill_proficiency("gather_information").get("proficient", False):
                events.append(ExplorationSkillEvent(
                    event_id=f"street_rumors_{location_id}",
                    trigger_skill="gather_information",
                    trigger_dc=SkillCheckDifficulty.EASY.value,
                    location_context="urban",
                    description="The locals seem chatty - you might learn something interesting",
                    success_outcome={
                        "information": ["local_politics", "trade_opportunities", "quest_leads"],
                        "xp": 25
                    },
                    failure_outcome={"consequence": "misinformation"},
                    repeatable=True,
                    cooldown_hours=8
                ))
        
        elif location_id.startswith("dungeon") or location_id.startswith("ruins"):
            # Dungeon/ruins events
            if character.get_skill_proficiency("search").get("proficient", False):
                events.append(ExplorationSkillEvent(
                    event_id=f"secret_door_{location_id}",
                    trigger_skill="search",
                    trigger_dc=SkillCheckDifficulty.HARD.value,
                    location_context="dungeon",
                    description="The architecture here seems unusual - there might be hidden passages",
                    success_outcome={
                        "discovery": "secret_passage",
                        "access": "hidden_area",
                        "xp": 75
                    },
                    failure_outcome={"consequence": "nothing_found"},
                    repeatable=False
                ))
        
        return events
    
    def execute_exploration_skill_event(
        self,
        character: Character,
        event: ExplorationSkillEvent
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Execute an exploration skill event.
        
        Args:
            character: Character triggering the event
            event: The exploration event to execute
            
        Returns:
            Tuple of (success, outcome_data)
        """
        # Check cooldown
        cooldown_key = f"{character.uuid}_{event.event_id}"
        if cooldown_key in self.recent_skill_events:
            last_trigger = self.recent_skill_events[cooldown_key]
            # Check if cooldown has passed (simplified)
            # In real implementation, would check actual time
            pass
        
        # Make the skill check
        result = skill_check_service.make_skill_check(
            character=character,
            skill_name=event.trigger_skill,
            dc=event.trigger_dc,
            description=f"Exploration event: {event.description}"
        )
        
        # Determine outcome
        if result.success:
            outcome_data = event.success_outcome.copy()
        else:
            outcome_data = event.failure_outcome.copy()
        
        # Add check details to outcome
        outcome_data.update({
            "skill_check_result": result,
            "event_id": event.event_id,
            "trigger_skill": event.trigger_skill
        })
        
        # Update cooldown
        if event.cooldown_hours > 0:
            self.recent_skill_events[cooldown_key] = datetime.utcnow()
        
        return result.success, outcome_data
    
    # === QUEST INTEGRATION ===
    
    def get_quest_skill_requirements(
        self,
        quest_data: Dict[str, Any]
    ) -> List[SkillCheckOpportunity]:
        """
        Extract skill check opportunities from quest data.
        
        Args:
            quest_data: Quest information including objectives and requirements
            
        Returns:
            List of skill check opportunities for the quest
        """
        opportunities = []
        
        # Parse quest objectives for skill requirements
        objectives = quest_data.get("objectives", [])
        
        for objective in objectives:
            obj_type = objective.get("type", "")
            
            if obj_type == "stealth_infiltration":
                opportunities.append(SkillCheckOpportunity(
                    skill_name="stealth",
                    trigger_type=SkillCheckTrigger.QUEST_OBJECTIVE,
                    context="quest_stealth",
                    description=objective.get("description", "Infiltrate the location undetected"),
                    dc=objective.get("difficulty", SkillCheckDifficulty.MEDIUM.value),
                    success_outcome="Successfully infiltrate without detection",
                    failure_outcome="Detected during infiltration attempt",
                    consequences={"failure": {"combat_encounter": True, "alarm_raised": True}}
                ))
            
            elif obj_type == "gather_information":
                opportunities.append(SkillCheckOpportunity(
                    skill_name="gather_information",
                    trigger_type=SkillCheckTrigger.QUEST_OBJECTIVE,
                    context="quest_investigation",
                    description=objective.get("description", "Gather information about the target"),
                    dc=objective.get("difficulty", SkillCheckDifficulty.MEDIUM.value),
                    success_outcome="Acquire detailed intelligence",
                    failure_outcome="Gain only basic information",
                    rewards={"information": objective.get("information_type", "general")}
                ))
            
            elif obj_type == "social_persuasion":
                opportunities.append(SkillCheckOpportunity(
                    skill_name="persuasion",
                    trigger_type=SkillCheckTrigger.QUEST_OBJECTIVE,
                    context="quest_social",
                    description=objective.get("description", "Convince the target through social means"),
                    dc=objective.get("difficulty", SkillCheckDifficulty.MEDIUM.value),
                    success_outcome="Successfully persuade the target",
                    failure_outcome="Fail to convince the target",
                    consequences={"failure": {"alternative_required": True}}
                ))
        
        return opportunities
    
    # === UTILITY METHODS ===
    
    def get_environmental_skill_modifiers(
        self,
        location_data: Dict[str, Any],
        weather_conditions: List[str] = None,
        time_of_day: str = "day"
    ) -> Dict[str, int]:
        """
        Calculate environmental modifiers for skills based on location and conditions.
        
        Args:
            location_data: Information about the current location
            weather_conditions: Current weather conditions
            time_of_day: Time of day (day, night, dawn, dusk)
            
        Returns:
            Dictionary of skill modifiers
        """
        modifiers = {}
        
        # Location-based modifiers
        location_type = location_data.get("type", "")
        
        if location_type == "forest":
            modifiers["survival"] = 2
            modifiers["stealth"] = 2
            modifiers["perception"] = -2  # Dense foliage
        elif location_type == "urban":
            modifiers["gather_information"] = 2
            modifiers["diplomacy"] = 1
            modifiers["survival"] = -5
        elif location_type == "dungeon":
            modifiers["search"] = 2
            modifiers["perception"] = -1  # Dim lighting
            modifiers["stealth"] = -2  # Echoing sounds
        
        # Weather modifiers
        if weather_conditions:
            for condition in weather_conditions:
                if condition == "rain":
                    modifiers["perception"] = modifiers.get("perception", 0) - 2
                    modifiers["stealth"] = modifiers.get("stealth", 0) + 1  # Rain covers sounds
                elif condition == "fog":
                    modifiers["perception"] = modifiers.get("perception", 0) - 5
                    modifiers["stealth"] = modifiers.get("stealth", 0) + 3
                elif condition == "storm":
                    modifiers["perception"] = modifiers.get("perception", 0) - 8
                    modifiers["stealth"] = modifiers.get("stealth", 0) + 2
        
        # Time of day modifiers
        if time_of_day == "night":
            modifiers["perception"] = modifiers.get("perception", 0) - 5
            modifiers["stealth"] = modifiers.get("stealth", 0) + 3
        elif time_of_day in ["dawn", "dusk"]:
            modifiers["perception"] = modifiers.get("perception", 0) - 2
            modifiers["stealth"] = modifiers.get("stealth", 0) + 1
        
        return modifiers

# Global service instance
skill_integration_service = SkillIntegrationService() 
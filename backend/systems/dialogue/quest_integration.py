"""
Quest integration for the dialogue system.

This module provides functionality for connecting dialogue with the Quest system,
allowing dialogue to reference quest states, provide quest information, and 
progress quest objectives through conversation.
"""

from typing import Dict, Any, List, Optional, Set
import logging

# Import quest system components
from backend.systems.quests.quest_manager import QuestManager

# Configure logger
logger = logging.getLogger(__name__)


class DialogueQuestIntegration:
    """
    Integration between dialogue and quest systems.
    
    Allows dialogue to reference and influence quest states, progress objectives,
    and provide contextual information about available and active quests.
    """
    
    def __init__(self, quest_manager=None):
        """
        Initialize the dialogue quest integration.
        
        Args:
            quest_manager: Optional quest manager instance
        """
        self.quest_manager = quest_manager or QuestManager.get_instance()
    
    def add_quest_context_to_dialogue(
        self,
        context: Dict[str, Any],
        character_id: str,
        player_id: Optional[str] = None,
        include_available: bool = True,
        include_active: bool = True,
        include_completed: bool = False
    ) -> Dict[str, Any]:
        """
        Add quest information to dialogue context.
        
        Args:
            context: The existing dialogue context
            character_id: ID of the NPC character
            player_id: Optional player ID for player-specific quest state
            include_available: Whether to include available quests
            include_active: Whether to include active quests
            include_completed: Whether to include completed quests
            
        Returns:
            Updated context with quest information added
        """
        # Create a copy of the context
        updated_context = dict(context)
        
        # Create quest context if it doesn't exist
        if "quest_context" not in updated_context:
            updated_context["quest_context"] = {}
        
        quest_context = updated_context["quest_context"]
        
        # Get quests associated with this character
        if include_available:
            available_quests = self._get_available_quests_for_character(character_id, player_id)
            if available_quests:
                quest_context["available_quests"] = available_quests
        
        if include_active:
            active_quests = self._get_active_quests_for_character(character_id, player_id)
            if active_quests:
                quest_context["active_quests"] = active_quests
        
        if include_completed:
            completed_quests = self._get_completed_quests_for_character(character_id, player_id)
            if completed_quests:
                quest_context["completed_quests"] = completed_quests
        
        # Add quest-giving status
        quest_context["can_give_quests"] = self._character_can_give_quests(character_id)
        quest_context["quest_giver_type"] = self._get_quest_giver_type(character_id)
        
        return updated_context
    
    def get_quest_dialogue_options(
        self,
        character_id: str,
        player_id: Optional[str] = None,
        quest_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get quest-specific dialogue options for a character.
        
        Args:
            character_id: ID of the NPC character
            player_id: Optional player ID for personalized options
            quest_type: Optional quest type filter
            
        Returns:
            List of quest-related dialogue options
        """
        dialogue_options = []
        
        try:
            # Available quest options
            available_quests = self._get_available_quests_for_character(character_id, player_id)
            for quest in available_quests:
                if quest_type and quest.get("type") != quest_type:
                    continue
                
                dialogue_options.append({
                    "type": "quest_offer",
                    "quest_id": quest["id"],
                    "text": f"I have a task for you: {quest['title']}",
                    "option_text": f"Tell me about '{quest['title']}'",
                    "consequence": "start_quest",
                    "metadata": {"quest_data": quest}
                })
            
            # Active quest options
            active_quests = self._get_active_quests_for_character(character_id, player_id)
            for quest in active_quests:
                if quest_type and quest.get("type") != quest_type:
                    continue
                
                # Check if quest can be progressed through dialogue
                if self._quest_can_progress_via_dialogue(quest["id"]):
                    dialogue_options.append({
                        "type": "quest_progress",
                        "quest_id": quest["id"],
                        "text": f"About {quest['title']}...",
                        "option_text": f"I want to discuss {quest['title']}",
                        "consequence": "progress_quest",
                        "metadata": {"quest_data": quest}
                    })
                
                # Check if quest can be completed through dialogue
                if self._quest_can_complete_via_dialogue(quest["id"]):
                    dialogue_options.append({
                        "type": "quest_completion",
                        "quest_id": quest["id"],
                        "text": f"I've completed {quest['title']}",
                        "option_text": f"I finished {quest['title']}",
                        "consequence": "complete_quest",
                        "metadata": {"quest_data": quest}
                    })
            
            # General quest inquiry options
            if self._character_can_give_quests(character_id):
                dialogue_options.append({
                    "type": "quest_inquiry",
                    "text": "Do you have any work for me?",
                    "option_text": "Are there any tasks I can help with?",
                    "consequence": "show_available_quests"
                })
            
        except Exception as e:
            logger.error(f"Error getting quest dialogue options for character {character_id}: {e}")
        
        return dialogue_options
    
    def progress_quest_from_dialogue(
        self,
        quest_id: str,
        player_id: str,
        dialogue_choice: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Progress a quest based on dialogue choice.
        
        Args:
            quest_id: ID of the quest to progress
            player_id: ID of the player
            dialogue_choice: The dialogue choice that triggered progression
            metadata: Optional additional metadata
            
        Returns:
            Dictionary with progression results
        """
        try:
            # Get quest details
            quest = self.quest_manager.get_quest(quest_id)
            if not quest:
                return {"success": False, "error": "Quest not found"}
            
            # Check if dialogue can progress this quest
            if not self._quest_can_progress_via_dialogue(quest_id):
                return {"success": False, "error": "Quest cannot be progressed via dialogue"}
            
            # Determine progression based on dialogue choice
            progression_data = self._analyze_dialogue_for_progression(
                quest, dialogue_choice, metadata
            )
            
            # Apply quest progression
            if progression_data["can_progress"]:
                result = self.quest_manager.progress_quest(
                    quest_id=quest_id,
                    player_id=player_id,
                    progress_data=progression_data["progress_data"]
                )
                
                return {
                    "success": True,
                    "quest_id": quest_id,
                    "progression_type": progression_data["type"],
                    "new_state": result.get("new_state"),
                    "rewards": result.get("rewards", []),
                    "next_objectives": result.get("next_objectives", [])
                }
            
            return {
                "success": False,
                "error": "Dialogue choice doesn't progress quest",
                "suggestion": progression_data.get("suggestion")
            }
            
        except Exception as e:
            logger.error(f"Error progressing quest {quest_id} from dialogue: {e}")
            return {"success": False, "error": str(e)}
    
    def get_quest_specific_responses(
        self,
        character_id: str,
        quest_id: str,
        dialogue_context: Dict[str, Any]
    ) -> List[str]:
        """
        Get character responses specific to a quest context.
        
        Args:
            character_id: ID of the NPC character
            quest_id: ID of the relevant quest
            dialogue_context: Current dialogue context
            
        Returns:
            List of quest-specific response options
        """
        responses = []
        
        try:
            quest = self.quest_manager.get_quest(quest_id)
            if not quest:
                return responses
            
            quest_state = quest.get("state", "available")
            character_role = self._get_character_role_in_quest(character_id, quest_id)
            
            # Generate responses based on quest state and character role
            if character_role == "quest_giver":
                if quest_state == "available":
                    responses.extend(self._get_quest_offer_responses(quest))
                elif quest_state == "active":
                    responses.extend(self._get_quest_progress_responses(quest))
                elif quest_state == "completed":
                    responses.extend(self._get_quest_completion_responses(quest))
            
            elif character_role == "quest_helper":
                responses.extend(self._get_quest_helper_responses(quest, quest_state))
            
            elif character_role == "quest_target":
                responses.extend(self._get_quest_target_responses(quest, quest_state))
            
            # Add context-aware responses
            context_responses = self._get_context_aware_quest_responses(
                quest, dialogue_context
            )
            responses.extend(context_responses)
            
        except Exception as e:
            logger.error(f"Error getting quest responses for {character_id}, quest {quest_id}: {e}")
        
        return responses[:5]  # Limit to 5 most relevant responses
    
    def _get_available_quests_for_character(
        self,
        character_id: str,
        player_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get quests that this character can offer."""
        try:
            # Get all quests where this character is the quest giver
            character_quests = self.quest_manager.get_quests_by_giver(character_id)
            
            # Filter for available quests
            available_quests = []
            for quest in character_quests:
                quest_state = quest.get("state", "available")
                if quest_state == "available":
                    # Check if player meets requirements
                    if not player_id or self._player_meets_quest_requirements(player_id, quest):
                        available_quests.append(quest)
            
            return available_quests
        except Exception as e:
            logger.error(f"Error getting available quests for character {character_id}: {e}")
            return []
    
    def _get_active_quests_for_character(
        self,
        character_id: str,
        player_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get active quests involving this character."""
        try:
            # Get all active quests involving this character
            active_quests = []
            
            if player_id:
                player_quests = self.quest_manager.get_player_quests(player_id, state="active")
                for quest in player_quests:
                    # Check if character is involved in this quest
                    if self._character_involved_in_quest(character_id, quest):
                        active_quests.append(quest)
            
            return active_quests
        except Exception as e:
            logger.error(f"Error getting active quests for character {character_id}: {e}")
            return []
    
    def _get_completed_quests_for_character(
        self,
        character_id: str,
        player_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get completed quests involving this character."""
        try:
            completed_quests = []
            
            if player_id:
                player_quests = self.quest_manager.get_player_quests(player_id, state="completed")
                for quest in player_quests:
                    if self._character_involved_in_quest(character_id, quest):
                        completed_quests.append(quest)
            
            return completed_quests
        except Exception as e:
            logger.error(f"Error getting completed quests for character {character_id}: {e}")
            return []
    
    def _character_can_give_quests(self, character_id: str) -> bool:
        """Check if character can give quests."""
        try:
            # Check if character has any quests to give
            character_quests = self.quest_manager.get_quests_by_giver(character_id)
            return len(character_quests) > 0
        except Exception:
            return False
    
    def _get_quest_giver_type(self, character_id: str) -> str:
        """Get the type of quest giver this character is."""
        try:
            # This could be enhanced with character data
            character_quests = self.quest_manager.get_quests_by_giver(character_id)
            
            if not character_quests:
                return "none"
            
            # Analyze quest types to determine giver type
            quest_types = [quest.get("type", "general") for quest in character_quests]
            
            if "main_story" in quest_types:
                return "story_critical"
            elif "faction" in quest_types:
                return "faction_representative"
            elif "merchant" in quest_types:
                return "merchant"
            else:
                return "general"
        except Exception:
            return "general"
    
    def _quest_can_progress_via_dialogue(self, quest_id: str) -> bool:
        """Check if quest can be progressed through dialogue."""
        try:
            quest = self.quest_manager.get_quest(quest_id)
            if not quest:
                return False
            
            # Check quest metadata for dialogue progression flags
            quest_meta = quest.get("metadata", {})
            return quest_meta.get("dialogue_progression", False)
        except Exception:
            return False
    
    def _quest_can_complete_via_dialogue(self, quest_id: str) -> bool:
        """Check if quest can be completed through dialogue."""
        try:
            quest = self.quest_manager.get_quest(quest_id)
            if not quest:
                return False
            
            quest_meta = quest.get("metadata", {})
            return quest_meta.get("dialogue_completion", False)
        except Exception:
            return False
    
    def _analyze_dialogue_for_progression(
        self,
        quest: Dict[str, Any],
        dialogue_choice: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Analyze dialogue choice for quest progression potential."""
        # Simplified analysis - in production this would be more sophisticated
        progression_keywords = quest.get("progression_keywords", [])
        
        choice_words = set(dialogue_choice.lower().split())
        keyword_matches = sum(1 for keyword in progression_keywords if keyword in choice_words)
        
        can_progress = keyword_matches > 0
        
        return {
            "can_progress": can_progress,
            "type": "dialogue_choice" if can_progress else "no_progression",
            "confidence": min(keyword_matches / len(progression_keywords), 1.0) if progression_keywords else 0.0,
            "progress_data": {
                "dialogue_choice": dialogue_choice,
                "matched_keywords": [kw for kw in progression_keywords if kw in choice_words]
            } if can_progress else {},
            "suggestion": "Try mentioning specific quest objectives" if not can_progress else None
        }
    
    def _get_character_role_in_quest(self, character_id: str, quest_id: str) -> str:
        """Determine character's role in a specific quest."""
        try:
            quest = self.quest_manager.get_quest(quest_id)
            if not quest:
                return "none"
            
            if quest.get("quest_giver_id") == character_id:
                return "quest_giver"
            
            quest_npcs = quest.get("involved_npcs", [])
            for npc_data in quest_npcs:
                if npc_data.get("npc_id") == character_id:
                    return npc_data.get("role", "quest_helper")
            
            return "none"
        except Exception:
            return "none"
    
    def _player_meets_quest_requirements(self, player_id: str, quest: Dict[str, Any]) -> bool:
        """Check if player meets quest requirements."""
        # Simplified check - in production this would check actual player data
        requirements = quest.get("requirements", {})
        
        # For now, assume player meets requirements
        # In production, this would check player level, completed quests, etc.
        return True
    
    def _character_involved_in_quest(self, character_id: str, quest: Dict[str, Any]) -> bool:
        """Check if character is involved in the quest."""
        if quest.get("quest_giver_id") == character_id:
            return True
        
        involved_npcs = quest.get("involved_npcs", [])
        return any(npc.get("npc_id") == character_id for npc in involved_npcs)
    
    def _get_quest_offer_responses(self, quest: Dict[str, Any]) -> List[str]:
        """Get responses for offering a quest."""
        return [
            f"I have a task that needs doing: {quest.get('title', 'an important mission')}",
            f"Are you interested in {quest.get('description', 'helping out')}?",
            f"This job pays well, but it's {quest.get('difficulty', 'challenging')}"
        ]
    
    def _get_quest_progress_responses(self, quest: Dict[str, Any]) -> List[str]:
        """Get responses for quest in progress."""
        return [
            f"How goes {quest.get('title', 'your task')}?",
            f"Any progress on what I asked you to do?",
            f"I hope you're making headway with that {quest.get('type', 'mission')}"
        ]
    
    def _get_quest_completion_responses(self, quest: Dict[str, Any]) -> List[str]:
        """Get responses for completed quest."""
        return [
            f"Thank you for completing {quest.get('title', 'that task')}",
            f"Excellent work on {quest.get('title', 'the mission')}",
            f"I knew I could count on you for {quest.get('title', 'that job')}"
        ]
    
    def _get_quest_helper_responses(self, quest: Dict[str, Any], quest_state: str) -> List[str]:
        """Get responses for quest helper characters."""
        if quest_state == "active":
            return [
                f"Need help with {quest.get('title', 'your quest')}?",
                f"I can offer advice about {quest.get('title', 'what you're doing')}",
                f"That {quest.get('type', 'task')} can be tricky"
            ]
        return []
    
    def _get_quest_target_responses(self, quest: Dict[str, Any], quest_state: str) -> List[str]:
        """Get responses for quest target characters."""
        return [
            f"I know why you're here",
            f"You're here about {quest.get('title', 'that business')}, aren't you?",
            f"I've been expecting someone like you"
        ]
    
    def _get_context_aware_quest_responses(
        self,
        quest: Dict[str, Any],
        dialogue_context: Dict[str, Any]
    ) -> List[str]:
        """Get context-aware quest responses."""
        responses = []
        
        # Check if location is relevant to quest
        location_id = dialogue_context.get("location_id")
        quest_locations = quest.get("locations", [])
        
        if location_id in quest_locations:
            responses.append(f"This place is important for {quest.get('title', 'your quest')}")
        
        # Check if other participants are mentioned
        participants = dialogue_context.get("participants", {})
        quest_npcs = quest.get("involved_npcs", [])
        
        for npc_data in quest_npcs:
            npc_id = npc_data.get("npc_id")
            if npc_id in participants:
                responses.append(f"You should speak with them about {quest.get('title', 'the quest')}")
        
        return responses

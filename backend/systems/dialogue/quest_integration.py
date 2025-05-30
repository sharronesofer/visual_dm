"""
Arc & Quest integration for the dialogue system.

This module provides functionality for connecting dialogue with the Arc & Quest systems,
allowing dialogue to reference and be influenced by the player's current quests, arcs,
and narrative elements.
"""

from typing import Dict, Any, List, Optional, Set
import logging

# Import arc and quest system components
from backend.systems.quests.quest_manager import QuestManager
from backend.systems.arcs.arc_manager import ArcManager

# Configure logger
logger = logging.getLogger(__name__)


class DialogueQuestIntegration:
    """
    Integration between dialogue and arc/quest systems.
    
    Allows dialogue to reference and be influenced by the state of
    quests, narrative arcs, and story progression.
    """
    
    def __init__(self, quest_manager=None, arc_manager=None):
        """
        Initialize the dialogue quest integration.
        
        Args:
            quest_manager: Optional quest manager instance
            arc_manager: Optional arc manager instance
        """
        self.quest_manager = quest_manager or QuestManager.get_instance()
        self.arc_manager = arc_manager or ArcManager.get_instance()
    
    def add_quest_context_to_dialogue(
        self,
        context: Dict[str, Any],
        character_id: str,
        quest_id: Optional[str] = None,
        location_id: Optional[str] = None,
        include_completed: bool = False,
        max_quests: int = 3
    ) -> Dict[str, Any]:
        """
        Add quest information to dialogue context.
        
        Args:
            context: The existing dialogue context
            character_id: ID of the character for dialogue
            quest_id: Optional specific quest ID to include
            location_id: Optional location ID for relevant quests
            include_completed: Whether to include completed quests
            max_quests: Maximum number of quests to include
            
        Returns:
            Updated context with quest information added
        """
        # Create a copy of the context
        updated_context = dict(context)
        
        # Create quest context if it doesn't exist
        if "quests" not in updated_context:
            updated_context["quests"] = {}
            
        # Add the specified quest if provided
        if quest_id:
            quest = self._get_quest_info(quest_id, character_id)
            if quest:
                updated_context["quests"]["current"] = quest
        
        # Add character-relevant quests
        relevant_quests = self._get_character_relevant_quests(
            character_id=character_id,
            location_id=location_id,
            include_completed=include_completed,
            limit=max_quests
        )
        
        if relevant_quests:
            updated_context["quests"]["relevant"] = relevant_quests
            
        # Add active arcs if available
        active_arcs = self._get_active_arcs(character_id)
        if active_arcs:
            updated_context["quests"]["active_arcs"] = active_arcs
            
        return updated_context
    
    def get_quest_dialogue_options(
        self,
        character_id: str,
        quest_id: str,
        dialogue_type: str = "quest_offer",
        player_history: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Get dialogue options relevant to a specific quest.
        
        Args:
            character_id: ID of the character for dialogue
            quest_id: ID of the quest
            dialogue_type: Type of quest dialogue ('quest_offer', 'progress', 'completion', etc.)
            player_history: Optional player history for context
            
        Returns:
            List of quest-relevant dialogue options
        """
        try:
            # Get the quest
            quest = self.quest_manager.get_quest(quest_id)
            
            if not quest:
                logger.warning(f"Quest not found: {quest_id}")
                return []
                
            # Get character connection to quest
            character_role = self._get_character_quest_role(character_id, quest_id)
            
            # Get dialogue options based on type
            options = []
            
            if dialogue_type == "quest_offer" and character_role == "giver":
                # Quest offer dialogue
                options = self._get_quest_offer_dialogue(quest, character_id, player_history)
                
            elif dialogue_type == "progress" and character_role in ["giver", "involved"]:
                # Quest progress dialogue
                options = self._get_quest_progress_dialogue(quest, character_id, player_history)
                
            elif dialogue_type == "completion" and character_role in ["giver", "receiver"]:
                # Quest completion dialogue
                options = self._get_quest_completion_dialogue(quest, character_id, player_history)
                
            elif dialogue_type == "hint":
                # Quest hint dialogue
                options = self._get_quest_hint_dialogue(quest, character_id, player_history)
            
            return options
            
        except Exception as e:
            logger.error(f"Error getting quest dialogue options for '{quest_id}': {e}")
            return []
    
    def get_arc_dialogue_context(
        self,
        arc_id: str,
        character_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get dialogue context for a specific narrative arc.
        
        Args:
            arc_id: ID of the narrative arc
            character_id: Optional character ID for perspective
            
        Returns:
            Arc context for dialogue
        """
        try:
            # Get the arc
            arc = self.arc_manager.get_arc(arc_id)
            
            if not arc:
                logger.warning(f"Arc not found: {arc_id}")
                return {}
                
            # Format for dialogue
            arc_context = {
                "id": arc.get("id"),
                "name": arc.get("name"),
                "description": arc.get("description"),
                "progress": arc.get("progress", 0.0),
                "state": arc.get("state", "inactive"),
                "related_themes": arc.get("themes", []),
                "current_act": arc.get("current_act", ""),
                "main_characters": arc.get("main_characters", [])
            }
            
            # Add character perspective if provided
            if character_id:
                char_perspective = self._get_character_arc_perspective(character_id, arc_id)
                if char_perspective:
                    arc_context["character_perspective"] = char_perspective
            
            # Add current quests in this arc
            current_quests = self._get_arc_active_quests(arc_id)
            if current_quests:
                arc_context["active_quests"] = current_quests
            
            return arc_context
            
        except Exception as e:
            logger.error(f"Error getting arc dialogue context for '{arc_id}': {e}")
            return {}
    
    def get_quest_narrative_description(
        self,
        quest_id: str,
        character_id: Optional[str] = None,
        include_history: bool = True
    ) -> str:
        """
        Get a narrative description of a quest suitable for dialogue.
        
        Args:
            quest_id: ID of the quest
            character_id: Optional character ID for perspective
            include_history: Whether to include quest history
            
        Returns:
            Narrative description of the quest
        """
        try:
            # Get the quest
            quest = self.quest_manager.get_quest(quest_id)
            
            if not quest:
                logger.warning(f"Quest not found: {quest_id}")
                return "This quest is unknown."
                
            # Basic description
            title = quest.get("title", "")
            basic_desc = quest.get("description", "")
            state = quest.get("state", "inactive")
            state_desc = self._get_quest_state_description(state)
            
            # Include quest history if requested
            history_desc = ""
            if include_history:
                history = quest.get("history", [])
                if history:
                    # Format latest history entries
                    latest_entries = history[-2:] if len(history) > 1 else history
                    history_points = [f"{entry.get('event')}" for entry in latest_entries]
                    history_desc = " Recently, " + ". ".join(history_points) + "."
            
            # Different perspective based on character
            perspective_desc = ""
            if character_id:
                char_role = self._get_character_quest_role(character_id, quest_id)
                
                if char_role == "giver":
                    perspective_desc = quest.get("giver_perspective", "")
                elif char_role == "receiver":
                    perspective_desc = quest.get("receiver_perspective", "")
                elif char_role == "involved":
                    perspective_desc = quest.get("involved_perspective", "")
                elif char_role == "antagonist":
                    perspective_desc = quest.get("antagonist_perspective", "")
            
            # Build the narrative description
            narrative = f"The quest '{title}' involves {basic_desc} {perspective_desc} {state_desc} {history_desc}".strip()
            return narrative
            
        except Exception as e:
            logger.error(f"Error getting quest narrative description for '{quest_id}': {e}")
            return "Information about this quest is unavailable."
    
    def _get_quest_info(
        self, 
        quest_id: str, 
        character_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get information about a quest for dialogue context.
        
        Args:
            quest_id: ID of the quest
            character_id: Optional character ID for quest perspective
            
        Returns:
            Dictionary with quest information
        """
        try:
            # Get the quest
            quest = self.quest_manager.get_quest(quest_id)
            
            if not quest:
                logger.warning(f"Quest not found: {quest_id}")
                return {}
                
            # Basic quest info
            quest_info = {
                "id": quest.get("id"),
                "title": quest.get("title"),
                "description": quest.get("description"),
                "state": quest.get("state", "inactive"),
                "progress": quest.get("progress", 0.0),
                "arc_id": quest.get("arc_id"),
                "priority": quest.get("priority", "normal"),
                "location": quest.get("location"),
                "giver": quest.get("giver"),
                "deadline": quest.get("deadline")
            }
            
            # Add character perspective if provided
            if character_id:
                char_role = self._get_character_quest_role(character_id, quest_id)
                quest_info["character_role"] = char_role
                
                if char_role:
                    quest_info["perspective"] = quest.get(f"{char_role}_perspective", "")
            
            # Add objectives if available
            objectives = quest.get("objectives", [])
            if objectives:
                quest_info["objectives"] = [
                    {
                        "description": obj.get("description"),
                        "completed": obj.get("completed", False)
                    }
                    for obj in objectives
                ]
            
            return quest_info
            
        except Exception as e:
            logger.error(f"Error getting quest info for '{quest_id}': {e}")
            return {}
    
    def _get_character_relevant_quests(
        self,
        character_id: str,
        location_id: Optional[str] = None,
        include_completed: bool = False,
        limit: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Get quests relevant to a character for dialogue.
        
        Args:
            character_id: ID of the character
            location_id: Optional location ID for relevance filtering
            include_completed: Whether to include completed quests
            limit: Maximum number of quests to return
            
        Returns:
            List of relevant quests
        """
        try:
            # Query conditions
            conditions = {
                "character_id": character_id,
                "include_completed": include_completed,
                "limit": limit
            }
            
            if location_id:
                conditions["location_id"] = location_id
                
            # Get quests
            quests = self.quest_manager.get_quests_by_conditions(conditions)
            
            # Format for dialogue
            formatted_quests = []
            for quest in quests:
                # Get character's role in this quest
                char_role = self._get_character_quest_role(character_id, quest.get("id"))
                
                quest_info = {
                    "id": quest.get("id"),
                    "title": quest.get("title"),
                    "description": quest.get("description"),
                    "state": quest.get("state", "inactive"),
                    "character_role": char_role,
                    "relevance": quest.get("relevance_reason", "")
                }
                formatted_quests.append(quest_info)
            
            return formatted_quests
            
        except Exception as e:
            logger.error(f"Error getting relevant quests for character '{character_id}': {e}")
            return []
    
    def _get_active_arcs(
        self, 
        character_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get active narrative arcs for dialogue context.
        
        Args:
            character_id: Optional character ID for relevance
            
        Returns:
            List of active arcs
        """
        try:
            # Query for active arcs
            conditions = {"state": "active"}
            
            if character_id:
                conditions["character_id"] = character_id
                
            # Get arcs
            arcs = self.arc_manager.get_arcs_by_conditions(conditions)
            
            # Format for dialogue
            formatted_arcs = []
            for arc in arcs:
                arc_info = {
                    "id": arc.get("id"),
                    "name": arc.get("name"),
                    "description": arc.get("description"),
                    "progress": arc.get("progress", 0.0),
                    "current_act": arc.get("current_act", "")
                }
                
                # Add character perspective if provided
                if character_id:
                    char_perspective = self._get_character_arc_perspective(character_id, arc.get("id"))
                    if char_perspective:
                        arc_info["character_perspective"] = char_perspective
                
                formatted_arcs.append(arc_info)
            
            return formatted_arcs
            
        except Exception as e:
            logger.error(f"Error getting active arcs: {e}")
            return []
    
    def _get_character_quest_role(
        self, 
        character_id: str, 
        quest_id: str
    ) -> Optional[str]:
        """
        Get a character's role in a quest.
        
        Args:
            character_id: ID of the character
            quest_id: ID of the quest
            
        Returns:
            Character's role ('giver', 'receiver', 'involved', 'antagonist', None)
        """
        try:
            # Get the quest
            quest = self.quest_manager.get_quest(quest_id)
            
            if not quest:
                return None
                
            # Check character roles
            if quest.get("giver") == character_id:
                return "giver"
            elif quest.get("receiver") == character_id:
                return "receiver"
            elif character_id in quest.get("involved_characters", []):
                return "involved"
            elif character_id in quest.get("antagonists", []):
                return "antagonist"
                
            return None
            
        except Exception as e:
            logger.error(f"Error getting character quest role for '{character_id}' in quest '{quest_id}': {e}")
            return None
    
    def _get_character_arc_perspective(
        self, 
        character_id: str, 
        arc_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get a character's perspective on a narrative arc.
        
        Args:
            character_id: ID of the character
            arc_id: ID of the arc
            
        Returns:
            Character's perspective on the arc
        """
        try:
            # Get the arc
            arc = self.arc_manager.get_arc(arc_id)
            
            if not arc:
                return None
                
            # Check character's perspective
            perspectives = arc.get("character_perspectives", {})
            perspective = perspectives.get(character_id)
            
            if not perspective:
                # Check for character role-based perspectives
                roles = arc.get("character_roles", {})
                for role, chars in roles.items():
                    if character_id in chars:
                        perspective = arc.get("role_perspectives", {}).get(role)
                        break
            
            return perspective
            
        except Exception as e:
            logger.error(f"Error getting character arc perspective for '{character_id}' in arc '{arc_id}': {e}")
            return None
    
    def _get_arc_active_quests(
        self, 
        arc_id: str
    ) -> List[Dict[str, Any]]:
        """
        Get active quests in a narrative arc.
        
        Args:
            arc_id: ID of the arc
            
        Returns:
            List of active quests
        """
        try:
            # Query for active quests in this arc
            conditions = {
                "arc_id": arc_id,
                "state": "active"
            }
            
            # Get quests
            quests = self.quest_manager.get_quests_by_conditions(conditions)
            
            # Format for dialogue
            formatted_quests = []
            for quest in quests:
                quest_info = {
                    "id": quest.get("id"),
                    "title": quest.get("title"),
                    "description": quest.get("description"),
                    "progress": quest.get("progress", 0.0)
                }
                formatted_quests.append(quest_info)
            
            return formatted_quests
            
        except Exception as e:
            logger.error(f"Error getting active quests for arc '{arc_id}': {e}")
            return []
    
    def _get_quest_state_description(
        self, 
        state: str
    ) -> str:
        """
        Get a description for a quest state.
        
        Args:
            state: The quest state
            
        Returns:
            Description of the state
        """
        descriptions = {
            "inactive": "The quest has not yet begun.",
            "active": "The quest is currently underway.",
            "complete": "The quest has been completed successfully.",
            "failed": "The quest has failed.",
            "expired": "The quest is no longer available.",
            "pending": "The quest is waiting to begin."
        }
        
        return descriptions.get(state, "The quest's state is unclear.")
    
    def _get_quest_offer_dialogue(
        self,
        quest: Dict[str, Any],
        character_id: str,
        player_history: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Get dialogue options for offering a quest.
        
        Args:
            quest: The quest data
            character_id: ID of the character offering the quest
            player_history: Optional player history for context
            
        Returns:
            List of dialogue options
        """
        # In a real implementation, this would pull from a dialogue database
        # with quest offer templates, or generate context-specific dialogue
        
        # Sample dialogue options
        title = quest.get("title", "")
        options = [
            {
                "text": f"I have a task that needs attention. {quest.get('offer_dialogue', '')}",
                "quest_action": "offer",
                "quest_id": quest.get("id")
            },
            {
                "text": f"Would you be interested in helping with something? It involves {quest.get('description', '')}",
                "quest_action": "offer",
                "quest_id": quest.get("id")
            }
        ]
        
        # Add refusal option if the player has previously refused
        if player_history and player_history.get("previously_refused"):
            options.append({
                "text": f"Have you reconsidered helping with the task I mentioned earlier? About {title}?",
                "quest_action": "re_offer",
                "quest_id": quest.get("id")
            })
        
        return options
    
    def _get_quest_progress_dialogue(
        self,
        quest: Dict[str, Any],
        character_id: str,
        player_history: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Get dialogue options for discussing quest progress.
        
        Args:
            quest: The quest data
            character_id: ID of the character discussing the quest
            player_history: Optional player history for context
            
        Returns:
            List of dialogue options
        """
        # Determine progress state
        progress = quest.get("progress", 0.0)
        objectives = quest.get("objectives", [])
        completed_objectives = sum(1 for obj in objectives if obj.get("completed", False))
        total_objectives = len(objectives)
        
        # Sample dialogue options
        options = []
        
        if progress < 0.25:
            # Early stage
            options.append({
                "text": "Have you made any progress on the task I gave you?",
                "quest_action": "check_progress",
                "quest_id": quest.get("id")
            })
        elif progress < 0.75:
            # Mid stage
            options.append({
                "text": f"How is the work coming along? You've completed {completed_objectives} of {total_objectives} objectives.",
                "quest_action": "check_progress",
                "quest_id": quest.get("id")
            })
        else:
            # Late stage
            options.append({
                "text": "You're making good progress. Just a bit more to finish the task.",
                "quest_action": "encourage",
                "quest_id": quest.get("id")
            })
        
        # Add hint option
        options.append({
            "text": "Do you need any advice on how to proceed?",
            "quest_action": "hint",
            "quest_id": quest.get("id")
        })
        
        return options
    
    def _get_quest_completion_dialogue(
        self,
        quest: Dict[str, Any],
        character_id: str,
        player_history: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Get dialogue options for completing a quest.
        
        Args:
            quest: The quest data
            character_id: ID of the character completing the quest
            player_history: Optional player history for context
            
        Returns:
            List of dialogue options
        """
        # Check if quest is ready for completion
        all_objectives_complete = all(obj.get("completed", False) for obj in quest.get("objectives", []))
        
        # Sample dialogue options
        options = []
        
        if all_objectives_complete:
            options.append({
                "text": "Excellent work! You've successfully completed all that I asked of you.",
                "quest_action": "complete",
                "quest_id": quest.get("id")
            })
            
            options.append({
                "text": f"Thank you for your help with {quest.get('title')}. Here's your reward.",
                "quest_action": "reward",
                "quest_id": quest.get("id")
            })
        else:
            options.append({
                "text": "You haven't quite finished everything I asked for yet.",
                "quest_action": "incomplete",
                "quest_id": quest.get("id")
            })
            
            options.append({
                "text": "Let me know when you've finished the task completely.",
                "quest_action": "reminder",
                "quest_id": quest.get("id")
            })
        
        return options
    
    def _get_quest_hint_dialogue(
        self,
        quest: Dict[str, Any],
        character_id: str,
        player_history: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Get dialogue options for providing hints about a quest.
        
        Args:
            quest: The quest data
            character_id: ID of the character giving hints
            player_history: Optional player history for context
            
        Returns:
            List of dialogue options
        """
        # Get incomplete objectives
        incomplete_objectives = [
            obj for obj in quest.get("objectives", [])
            if not obj.get("completed", False)
        ]
        
        # Sample dialogue options
        options = []
        
        # General hint
        options.append({
            "text": quest.get("general_hint", "Let me give you some advice about this task."),
            "quest_action": "general_hint",
            "quest_id": quest.get("id")
        })
        
        # Hints for specific objectives
        for i, obj in enumerate(incomplete_objectives):
            if i >= 2:  # Limit to 2 specific hints
                break
                
            hint = obj.get("hint", f"For the objective to {obj.get('description', '')}, you should look into it carefully.")
            options.append({
                "text": hint,
                "quest_action": "objective_hint",
                "quest_id": quest.get("id"),
                "objective_id": obj.get("id")
            })
        
        return options 
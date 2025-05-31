"""
Quest state management.
Handles quest status transitions and operations.
"""

import logging
from typing import Dict, Any, List, Optional

from backend.systems.quest.repositories import QuestRepository
from backend.systems.quest.models import Quest, QuestStep
from backend.infrastructure.utils import ValidationError, NotFoundError

logger = logging.getLogger(__name__)

class QuestStateManager:
    """
    Manages quest state transitions and operations.
    Handles the business logic for quest progress, completion, and other state changes.
    """
    
    def __init__(self):
        """Initialize the quest state manager."""

    def update_step_status(self, quest_id: str, step_id: int, completed: bool) -> Dict[str, Any]:
        """
        Update the completion status of a quest step and handle any 
        resulting state changes in the quest.
        
        Args:
            quest_id: ID of the quest to update
            step_id: Index of the step to update
            completed: Whether the step is completed
            
        Returns:
            Updated quest data
            
        Raises:
            NotFoundError: If quest or step not found
            ValidationError: If invalid status transition
        """
        # Get the quest
        quest_data = QuestRepository.get_quest(quest_id)
        if not quest_data:
            raise NotFoundError(f"Quest {quest_id} not found")
        
        # Validate step ID
        if not quest_data.get("steps") or len(quest_data["steps"]) <= step_id:
            raise ValidationError(f"Invalid step ID {step_id} for quest {quest_id}")
        
        # Update step status
        quest_data["steps"][step_id]["completed"] = completed
        
        # Check if all steps are completed
        all_completed = all(step.get("completed", False) for step in quest_data["steps"])
        
        # Update quest status if all steps completed
        if all_completed and quest_data.get("status") != "completed":
            quest_data["status"] = "completed"
            logger.info(f"Quest {quest_id} marked as completed")
        
        # If a step is marked as incomplete and quest was completed,
        # revert quest to in-progress
        if not completed and quest_data.get("status") == "completed":
            quest_data["status"] = "in-progress"
            logger.info(f"Quest {quest_id} reverted to in-progress")
        
        # Update the quest in the database
        QuestRepository.update_quest(quest_id, quest_data)
        
        return quest_data
    
    def accept_quest(self, quest_id: str, player_id: str) -> Dict[str, Any]:
        """
        Mark a quest as accepted by a player.
        
        Args:
            quest_id: ID of the quest
            player_id: ID of the player accepting the quest
            
        Returns:
            Updated quest data
            
        Raises:
            NotFoundError: If quest not found
            ValidationError: If quest already accepted or invalid state
        """
        # Get the quest
        quest_data = QuestRepository.get_quest(quest_id)
        if not quest_data:
            raise NotFoundError(f"Quest {quest_id} not found")
        
        # Validate current status
        if quest_data.get("status") not in ["available", "offered"]:
            raise ValidationError(
                f"Cannot accept quest in status '{quest_data.get('status')}'. "
                f"Quest must be 'available' or 'offered'."
            )
        
        # Update quest status and player
        quest_data["status"] = "in-progress"
        quest_data["player_id"] = player_id
        
        # Update the quest in the database
        QuestRepository.update_quest(quest_id, quest_data)
        
        # Create a journal entry for quest acceptance
        journal_entry = {
            "player_id": player_id,
            "quest_id": quest_id,
            "quest_title": quest_data.get("title", "Unknown Quest"),
            "event_type": "quest_accepted",
            "description": f"Accepted quest: {quest_data.get('title', 'Unknown Quest')}",
            "location": quest_data.get("location", "Unknown Location")
        }
        
        QuestRepository.create_journal_entry(journal_entry)
        
        return quest_data
    
    def abandon_quest(self, quest_id: str, player_id: str) -> Dict[str, Any]:
        """
        Mark a quest as abandoned by a player.
        
        Args:
            quest_id: ID of the quest
            player_id: ID of the player abandoning the quest
            
        Returns:
            Updated quest data
            
        Raises:
            NotFoundError: If quest not found
            ValidationError: If quest not accepted by player or invalid state
        """
        # Get the quest
        quest_data = QuestRepository.get_quest(quest_id)
        if not quest_data:
            raise NotFoundError(f"Quest {quest_id} not found")
        
        # Validate player
        if quest_data.get("player_id") != player_id:
            raise ValidationError(
                f"Player {player_id} cannot abandon quest {quest_id} "
                f"assigned to player {quest_data.get('player_id')}"
            )
        
        # Validate current status
        if quest_data.get("status") not in ["in-progress", "completed"]:
            raise ValidationError(
                f"Cannot abandon quest in status '{quest_data.get('status')}'. "
                f"Quest must be 'in-progress' or 'completed'."
            )
        
        # Update quest status
        quest_data["status"] = "abandoned"
        
        # Update the quest in the database
        QuestRepository.update_quest(quest_id, quest_data)
        
        # Create a journal entry for quest abandonment
        journal_entry = {
            "player_id": player_id,
            "quest_id": quest_id,
            "quest_title": quest_data.get("title", "Unknown Quest"),
            "event_type": "quest_abandoned",
            "description": f"Abandoned quest: {quest_data.get('title', 'Unknown Quest')}",
            "location": quest_data.get("location", "Unknown Location")
        }
        
        QuestRepository.create_journal_entry(journal_entry)
        
        return quest_data
    
    def complete_quest(self, quest_id: str, player_id: str) -> Dict[str, Any]:
        """
        Mark a quest as completed by a player, regardless of step completion.
        Used for quests that may be completed through alternative means.
        
        Args:
            quest_id: ID of the quest
            player_id: ID of the player completing the quest
            
        Returns:
            Updated quest data
            
        Raises:
            NotFoundError: If quest not found
            ValidationError: If quest not accepted by player or invalid state
        """
        # Get the quest
        quest_data = QuestRepository.get_quest(quest_id)
        if not quest_data:
            raise NotFoundError(f"Quest {quest_id} not found")
        
        # Validate player
        if quest_data.get("player_id") != player_id:
            raise ValidationError(
                f"Player {player_id} cannot complete quest {quest_id} "
                f"assigned to player {quest_data.get('player_id')}"
            )
        
        # Validate current status
        if quest_data.get("status") != "in-progress":
            raise ValidationError(
                f"Cannot complete quest in status '{quest_data.get('status')}'. "
                f"Quest must be 'in-progress'."
            )
        
        # Update quest status
        quest_data["status"] = "completed"
        
        # Mark all steps as completed
        if quest_data.get("steps"):
            for step in quest_data["steps"]:
                step["completed"] = True
        
        # Update the quest in the database
        QuestRepository.update_quest(quest_id, quest_data)
        
        # Create a journal entry for quest completion
        journal_entry = {
            "player_id": player_id,
            "quest_id": quest_id,
            "quest_title": quest_data.get("title", "Unknown Quest"),
            "event_type": "quest_completed",
            "description": f"Completed quest: {quest_data.get('title', 'Unknown Quest')}",
            "location": quest_data.get("location", "Unknown Location")
        }
        
        QuestRepository.create_journal_entry(journal_entry)
        
        return quest_data
    
    def fail_quest(self, quest_id: str, player_id: str, reason: str = None) -> Dict[str, Any]:
        """
        Mark a quest as failed by a player.
        
        Args:
            quest_id: ID of the quest
            player_id: ID of the player who failed the quest
            reason: Optional reason for failure
            
        Returns:
            Updated quest data
            
        Raises:
            NotFoundError: If quest not found
            ValidationError: If quest not accepted by player or invalid state
        """
        # Get the quest
        quest_data = QuestRepository.get_quest(quest_id)
        if not quest_data:
            raise NotFoundError(f"Quest {quest_id} not found")
        
        # Validate player
        if quest_data.get("player_id") != player_id:
            raise ValidationError(
                f"Player {player_id} cannot fail quest {quest_id} "
                f"assigned to player {quest_data.get('player_id')}"
            )
        
        # Validate current status
        if quest_data.get("status") != "in-progress":
            raise ValidationError(
                f"Cannot fail quest in status '{quest_data.get('status')}'. "
                f"Quest must be 'in-progress'."
            )
        
        # Update quest status
        quest_data["status"] = "failed"
        if reason:
            quest_data["failure_reason"] = reason
        
        # Update the quest in the database
        QuestRepository.update_quest(quest_id, quest_data)
        
        # Create a journal entry for quest failure
        journal_entry = {
            "player_id": player_id,
            "quest_id": quest_id,
            "quest_title": quest_data.get("title", "Unknown Quest"),
            "event_type": "quest_failed",
            "description": f"Failed quest: {quest_data.get('title', 'Unknown Quest')}"
                           + (f" - {reason}" if reason else ""),
            "location": quest_data.get("location", "Unknown Location")
        }
        
        QuestRepository.create_journal_entry(journal_entry)
        
        return quest_data 
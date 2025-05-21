"""
Goal Service
-----------
Service for managing character goals.
Provides methods for creating, updating, and tracking character goals.
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Union, Any
from uuid import UUID
import json
import os

from backend.systems.events.event_dispatcher import EventDispatcher
from backend.systems.character.models.goal import (
    Goal, GoalType, GoalPriority, GoalStatus,
    GoalCreated, GoalCompleted, GoalFailed, GoalAbandoned, GoalProgressUpdated
)

logger = logging.getLogger(__name__)

class GoalService:
    """
    Service for managing character goals.
    Follows the repository pattern for data access.
    """
    
    def __init__(self, data_dir: str = './data/goals'):
        """
        Initialize the service with a data directory.
        
        Args:
            data_dir: Directory where goal data is stored
        """
        self.data_dir = data_dir
        self.goals: Dict[str, Dict[str, Goal]] = {}  # character_id -> {goal_id -> Goal}
        self.event_dispatcher = EventDispatcher.get_instance()
        
        # Ensure data directory exists
        os.makedirs(data_dir, exist_ok=True)
    
    def _get_character_goal_file(self, character_id: str) -> str:
        """
        Get the file path for a character's goals.
        
        Args:
            character_id: UUID of the character
            
        Returns:
            File path
        """
        return os.path.join(self.data_dir, f"{character_id}_goals.json")
    
    def _load_character_goals(self, character_id: str) -> Dict[str, Goal]:
        """
        Load a character's goals from disk.
        
        Args:
            character_id: UUID of the character
            
        Returns:
            Dictionary of goal_id -> Goal
        """
        file_path = self._get_character_goal_file(character_id)
        
        # If file doesn't exist, return empty dict
        if not os.path.exists(file_path):
            return {}
            
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                
                # Create goals from data
                goals = {}
                for goal_data in data.get("goals", []):
                    goal = Goal.from_dict(goal_data)
                    goals[goal.goal_id] = goal
                    
                return goals
        except Exception as e:
            logger.error(f"Error loading goals for character {character_id}: {str(e)}")
            return {}
    
    def _save_character_goals(self, character_id: str) -> bool:
        """
        Save a character's goals to disk.
        
        Args:
            character_id: UUID of the character
            
        Returns:
            True if successful, False otherwise
        """
        character_id_str = str(character_id)
        
        # If goals aren't in memory, nothing to save
        if character_id_str not in self.goals:
            logger.warning(f"No goals in memory for character {character_id_str}")
            return False
            
        file_path = self._get_character_goal_file(character_id_str)
        
        try:
            # Get goals data
            goals_dict = self.goals[character_id_str]
            
            # Prepare data for serialization
            data = {
                "character_id": character_id_str,
                "goals": [goal.to_dict() for goal in goals_dict.values()]
            }
            
            # Save to file
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
                
            logger.info(f"Saved {len(goals_dict)} goals for character {character_id_str}")
            return True
        except Exception as e:
            logger.error(f"Error saving goals for character {character_id_str}: {str(e)}")
            return False
    
    def get_character_goals(self, 
                           character_id: Union[str, UUID], 
                           goal_type: Optional[Union[str, GoalType]] = None,
                           status: Optional[Union[str, GoalStatus]] = None,
                           priority: Optional[Union[str, GoalPriority]] = None,
                           load_if_needed: bool = True) -> List[Goal]:
        """
        Get a character's goals, optionally filtered.
        
        Args:
            character_id: UUID of the character
            goal_type: Optional filter by goal type
            status: Optional filter by status
            priority: Optional filter by priority
            load_if_needed: Whether to load from disk if not in memory
            
        Returns:
            List of goals
        """
        character_id_str = str(character_id)
        
        # Load goals if needed
        if character_id_str not in self.goals and load_if_needed:
            self.goals[character_id_str] = self._load_character_goals(character_id_str)
            
        # If no goals, return empty list
        if character_id_str not in self.goals:
            return []
            
        # Get goals
        goals = list(self.goals[character_id_str].values())
        
        # Filter by type if specified
        if goal_type is not None:
            if isinstance(goal_type, str):
                goal_type = GoalType(goal_type)
            goals = [g for g in goals if g.goal_type == goal_type]
            
        # Filter by status if specified
        if status is not None:
            if isinstance(status, str):
                status = GoalStatus(status)
            goals = [g for g in goals if g.status == status]
            
        # Filter by priority if specified
        if priority is not None:
            if isinstance(priority, str):
                priority = GoalPriority(priority)
            goals = [g for g in goals if g.priority == priority]
            
        return goals
    
    def get_goal(self, 
                character_id: Union[str, UUID], 
                goal_id: Union[str, UUID],
                load_if_needed: bool = True) -> Optional[Goal]:
        """
        Get a specific goal.
        
        Args:
            character_id: UUID of the character
            goal_id: UUID of the goal
            load_if_needed: Whether to load from disk if not in memory
            
        Returns:
            Goal object or None if not found
        """
        character_id_str = str(character_id)
        goal_id_str = str(goal_id)
        
        # Load goals if needed
        if character_id_str not in self.goals and load_if_needed:
            self.goals[character_id_str] = self._load_character_goals(character_id_str)
            
        # Return goal if found
        if character_id_str in self.goals:
            return self.goals[character_id_str].get(goal_id_str)
            
        return None
    
    def add_goal(self, 
               character_id: Union[str, UUID], 
               description: str, 
               goal_type: Union[str, GoalType] = GoalType.PERSONAL,
               priority: Union[str, GoalPriority] = GoalPriority.MEDIUM,
               metadata: Optional[Dict[str, Any]] = None) -> Goal:
        """
        Add a new goal for a character.
        
        Args:
            character_id: UUID of the character
            description: Text description of the goal
            goal_type: Type of goal
            priority: Priority level
            metadata: Additional goal-specific data
            
        Returns:
            The created goal
        """
        character_id_str = str(character_id)
        
        # Ensure goals dict exists
        if character_id_str not in self.goals:
            self.goals[character_id_str] = self._load_character_goals(character_id_str)
            
        # Create goal
        goal = Goal(
            character_id=character_id_str,
            description=description,
            goal_type=goal_type,
            priority=priority,
            metadata=metadata
        )
        
        # Store goal
        self.goals[character_id_str][goal.goal_id] = goal
        
        # Save to disk
        self._save_character_goals(character_id_str)
        
        # Emit event
        self.event_dispatcher.emit(GoalCreated(
            character_id=character_id_str,
            goal_id=goal.goal_id,
            goal_type=str(goal.goal_type),
            description=goal.description,
            priority=str(goal.priority)
        ))
        
        logger.info(f"Added goal for character {character_id_str}: {description}")
        return goal
    
    def add_subgoal(self, 
                  character_id: Union[str, UUID], 
                  parent_goal_id: Union[str, UUID],
                  description: str, 
                  goal_type: Union[str, GoalType] = None,
                  priority: Union[str, GoalPriority] = None,
                  metadata: Optional[Dict[str, Any]] = None) -> Optional[Goal]:
        """
        Add a subgoal to an existing goal.
        
        Args:
            character_id: UUID of the character
            parent_goal_id: UUID of the parent goal
            description: Text description of the subgoal
            goal_type: Type of subgoal (defaults to parent type)
            priority: Priority level (defaults to parent priority)
            metadata: Additional subgoal-specific data
            
        Returns:
            The created subgoal or None if parent not found
        """
        # Get parent goal
        parent_goal = self.get_goal(character_id, parent_goal_id)
        if not parent_goal:
            logger.error(f"Parent goal {parent_goal_id} not found for character {character_id}")
            return None
            
        # Use parent's goal type if none specified
        if goal_type is None:
            goal_type = parent_goal.goal_type
            
        # Add subgoal
        subgoal = parent_goal.add_subgoal(
            description=description,
            goal_type=goal_type,
            priority=priority,
            metadata=metadata
        )
        
        # Save to disk
        self._save_character_goals(str(character_id))
        
        logger.info(f"Added subgoal to goal {parent_goal_id} for character {character_id}: {description}")
        return subgoal
    
    def update_goal_progress(self, 
                           character_id: Union[str, UUID], 
                           goal_id: Union[str, UUID],
                           progress: float) -> bool:
        """
        Update a goal's progress value.
        
        Args:
            character_id: UUID of the character
            goal_id: UUID of the goal
            progress: New progress value (0.0 to 1.0)
            
        Returns:
            True if successful, False if goal not found
        """
        # Get goal
        goal = self.get_goal(character_id, goal_id)
        if not goal:
            logger.error(f"Goal {goal_id} not found for character {character_id}")
            return False
            
        # Update progress
        goal.update_progress(progress)
        
        # Save to disk
        self._save_character_goals(str(character_id))
        
        return True
    
    def complete_goal(self, 
                    character_id: Union[str, UUID], 
                    goal_id: Union[str, UUID]) -> bool:
        """
        Mark a goal as completed.
        
        Args:
            character_id: UUID of the character
            goal_id: UUID of the goal
            
        Returns:
            True if successful, False if goal not found
        """
        # Get goal
        goal = self.get_goal(character_id, goal_id)
        if not goal:
            logger.error(f"Goal {goal_id} not found for character {character_id}")
            return False
            
        # Complete goal
        goal.complete()
        
        # Save to disk
        self._save_character_goals(str(character_id))
        
        return True
    
    def fail_goal(self, 
                character_id: Union[str, UUID], 
                goal_id: Union[str, UUID],
                reason: Optional[str] = None) -> bool:
        """
        Mark a goal as failed.
        
        Args:
            character_id: UUID of the character
            goal_id: UUID of the goal
            reason: Optional reason for failure
            
        Returns:
            True if successful, False if goal not found
        """
        # Get goal
        goal = self.get_goal(character_id, goal_id)
        if not goal:
            logger.error(f"Goal {goal_id} not found for character {character_id}")
            return False
            
        # Fail goal
        goal.fail(reason)
        
        # Save to disk
        self._save_character_goals(str(character_id))
        
        return True
    
    def abandon_goal(self, 
                   character_id: Union[str, UUID], 
                   goal_id: Union[str, UUID],
                   reason: Optional[str] = None) -> bool:
        """
        Mark a goal as abandoned.
        
        Args:
            character_id: UUID of the character
            goal_id: UUID of the goal
            reason: Optional reason for abandonment
            
        Returns:
            True if successful, False if goal not found
        """
        # Get goal
        goal = self.get_goal(character_id, goal_id)
        if not goal:
            logger.error(f"Goal {goal_id} not found for character {character_id}")
            return False
            
        # Abandon goal
        goal.abandon(reason)
        
        # Save to disk
        self._save_character_goals(str(character_id))
        
        return True
    
    def update_goal_priority(self, 
                           character_id: Union[str, UUID], 
                           goal_id: Union[str, UUID],
                           priority: Union[str, GoalPriority]) -> bool:
        """
        Update a goal's priority.
        
        Args:
            character_id: UUID of the character
            goal_id: UUID of the goal
            priority: New priority level
            
        Returns:
            True if successful, False if goal not found
        """
        # Get goal
        goal = self.get_goal(character_id, goal_id)
        if not goal:
            logger.error(f"Goal {goal_id} not found for character {character_id}")
            return False
            
        # Update priority
        goal.update_priority(priority)
        
        # Save to disk
        self._save_character_goals(str(character_id))
        
        return True
    
    def remove_goal(self, 
                  character_id: Union[str, UUID], 
                  goal_id: Union[str, UUID]) -> bool:
        """
        Remove a goal.
        
        Args:
            character_id: UUID of the character
            goal_id: UUID of the goal
            
        Returns:
            True if successful, False if goal not found
        """
        character_id_str = str(character_id)
        goal_id_str = str(goal_id)
        
        # Check if character has goals
        if character_id_str not in self.goals:
            logger.error(f"No goals found for character {character_id_str}")
            return False
            
        # Check if goal exists
        if goal_id_str not in self.goals[character_id_str]:
            logger.error(f"Goal {goal_id_str} not found for character {character_id_str}")
            return False
            
        # Get goal for event
        goal = self.goals[character_id_str][goal_id_str]
        
        # Remove goal
        del self.goals[character_id_str][goal_id_str]
        
        # Save to disk
        self._save_character_goals(character_id_str)
        
        logger.info(f"Removed goal {goal_id_str} for character {character_id_str}")
        return True
    
    def get_active_goals(self, character_id: Union[str, UUID]) -> List[Goal]:
        """
        Get all active goals for a character.
        
        Args:
            character_id: UUID of the character
            
        Returns:
            List of active goals
        """
        return self.get_character_goals(character_id, status=GoalStatus.ACTIVE)
    
    def get_completed_goals(self, character_id: Union[str, UUID]) -> List[Goal]:
        """
        Get all completed goals for a character.
        
        Args:
            character_id: UUID of the character
            
        Returns:
            List of completed goals
        """
        return self.get_character_goals(character_id, status=GoalStatus.COMPLETED)
    
    def get_highest_priority_goals(self, 
                                 character_id: Union[str, UUID], 
                                 status: Union[str, GoalStatus] = GoalStatus.ACTIVE,
                                 limit: int = 5) -> List[Goal]:
        """
        Get a character's highest priority goals.
        
        Args:
            character_id: UUID of the character
            status: Filter by status
            limit: Maximum number of goals to return
            
        Returns:
            List of goals sorted by priority
        """
        # Get goals with specified status
        goals = self.get_character_goals(character_id, status=status)
        
        # Create priority order map
        priority_order = {
            GoalPriority.CRITICAL: 0,
            GoalPriority.HIGH: 1,
            GoalPriority.MEDIUM: 2,
            GoalPriority.LOW: 3
        }
        
        # Sort by priority (higher priority first)
        sorted_goals = sorted(goals, key=lambda g: priority_order.get(g.priority, 999))
        
        # Return limited number
        return sorted_goals[:limit]
    
    def get_goal_progress_summary(self, character_id: Union[str, UUID]) -> Dict[str, Any]:
        """
        Get a summary of goal progress for a character.
        
        Args:
            character_id: UUID of the character
            
        Returns:
            Dictionary with progress summary
        """
        # Get all goals
        all_goals = self.get_character_goals(character_id)
        
        # Get counts by status
        active_count = sum(1 for g in all_goals if g.status == GoalStatus.ACTIVE)
        completed_count = sum(1 for g in all_goals if g.status == GoalStatus.COMPLETED)
        failed_count = sum(1 for g in all_goals if g.status == GoalStatus.FAILED)
        abandoned_count = sum(1 for g in all_goals if g.status == GoalStatus.ABANDONED)
        
        # Calculate overall progress
        total_progress = 0.0
        goal_count = len(all_goals)
        
        for goal in all_goals:
            if goal.status == GoalStatus.COMPLETED:
                total_progress += 1.0
            elif goal.status == GoalStatus.ACTIVE:
                total_progress += goal.progress
                
        overall_progress = total_progress / max(1, goal_count)
        
        # Return summary
        return {
            "character_id": str(character_id),
            "total_goals": goal_count,
            "active_goals": active_count,
            "completed_goals": completed_count,
            "failed_goals": failed_count,
            "abandoned_goals": abandoned_count,
            "overall_progress": overall_progress
        } 
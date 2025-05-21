"""
Quest utility functions and validators.
Handles quest validation and general utility functions.
"""

import logging
import re
from datetime import datetime
from typing import Dict, List, Optional, Any

from backend.core.utils.firebase_utils import (
    get_firestore_client,
    get_document,
    set_document,
    update_document,
    get_collection
)
from backend.core.utils.error import ValidationError, NotFoundError, DatabaseError
from backend.core.database import db
from .generator import QuestGenerator

logger = logging.getLogger(__name__)


class QuestValidator:
    """Validates quest-related input data."""
    
    @staticmethod
    def validate_quest_id(quest_id: str) -> None:
        """Validate quest ID format."""
        if not quest_id:
            raise ValidationError("Quest ID is required")
            
        # Quest ID should be alphanumeric with optional underscores and hyphens
        if not re.match(r'^[a-zA-Z0-9_-]+$', quest_id):
            raise ValidationError("Invalid quest ID format")
            
    @staticmethod
    def validate_player_id(player_id: str) -> None:
        """Validate player ID format."""
        if not player_id:
            raise ValidationError("Player ID is required")
            
        # Player ID should be alphanumeric with optional underscores
        if not re.match(r'^[a-zA-Z0-9_]+$', player_id):
            raise ValidationError("Invalid player ID format")
            
    @staticmethod
    def validate_quest_data(data: Dict[str, Any]) -> None:
        """Validate quest creation/update data."""
        if not data:
            raise ValidationError("No quest data provided")
            
        required_fields = ['title', 'description', 'level', 'type']
        for field in required_fields:
            if field not in data:
                raise ValidationError(f"Missing required field: {field}")
                
        # Validate title
        if not isinstance(data['title'], str) or len(data['title']) < 3:
            raise ValidationError("Title must be at least 3 characters long")
            
        # Validate description
        if not isinstance(data['description'], str) or len(data['description']) < 10:
            raise ValidationError("Description must be at least 10 characters long")
            
        # Validate level
        if not isinstance(data['level'], int) or data['level'] < 1 or data['level'] > 100:
            raise ValidationError("Level must be between 1 and 100")
            
        # Validate type
        valid_types = ['main', 'side', 'daily', 'event']
        if data['type'] not in valid_types:
            raise ValidationError(f"Invalid quest type. Must be one of: {', '.join(valid_types)}")
            
        # Validate optional fields if present
        if 'rewards' in data:
            QuestValidator._validate_rewards(data['rewards'])
            
        if 'requirements' in data:
            QuestValidator._validate_requirements(data['requirements'])
            
        if 'steps' in data:
            QuestValidator._validate_steps(data['steps'])
    
    @staticmethod
    def _validate_rewards(rewards: Dict[str, Any]) -> None:
        """Validate quest rewards."""
        if not isinstance(rewards, dict):
            raise ValidationError("Rewards must be a dictionary")
            
        valid_reward_types = ['gold', 'items', 'experience', 'reputation']
        for reward_type in rewards:
            if reward_type not in valid_reward_types:
                raise ValidationError(f"Invalid reward type: {reward_type}")
                
            if reward_type == 'gold':
                if not isinstance(rewards[reward_type], int) or rewards[reward_type] < 0:
                    raise ValidationError("Gold reward must be a positive integer")
                    
            elif reward_type == 'experience':
                if not isinstance(rewards[reward_type], int) or rewards[reward_type] < 0:
                    raise ValidationError("Experience reward must be a positive integer")
                    
            elif reward_type == 'reputation':
                if not isinstance(rewards[reward_type], int):
                    raise ValidationError("Reputation reward must be an integer")
                    
            elif reward_type == 'items':
                if not isinstance(rewards[reward_type], list):
                    raise ValidationError("Items reward must be a list")
    
    @staticmethod
    def _validate_requirements(requirements: Dict[str, Any]) -> None:
        """Validate quest requirements."""
        if not isinstance(requirements, dict):
            raise ValidationError("Requirements must be a dictionary")
            
        valid_requirement_types = ['level', 'quests', 'items', 'faction']
        for req_type in requirements:
            if req_type not in valid_requirement_types:
                raise ValidationError(f"Invalid requirement type: {req_type}")
                
            if req_type == 'level':
                if not isinstance(requirements[req_type], int) or requirements[req_type] < 1:
                    raise ValidationError("Level requirement must be a positive integer")
                    
            elif req_type in ['quests', 'items']:
                if not isinstance(requirements[req_type], list):
                    raise ValidationError(f"{req_type} requirements must be a list")
                    
            elif req_type == 'faction':
                if not isinstance(requirements[req_type], dict):
                    raise ValidationError("Faction requirements must be a dictionary")
    
    @staticmethod
    def _validate_steps(steps: List[Dict[str, Any]]) -> None:
        """Validate quest steps."""
        if not isinstance(steps, list):
            raise ValidationError("Steps must be a list")
            
        if not steps:
            raise ValidationError("Quest must have at least one step")
            
        for step in steps:
            if not isinstance(step, dict):
                raise ValidationError("Each step must be a dictionary")
                
            required_fields = ['id', 'description', 'type']
            for field in required_fields:
                if field not in step:
                    raise ValidationError(f"Step missing required field: {field}")
                    
            if not isinstance(step['id'], int) or step['id'] < 0:
                raise ValidationError("Step ID must be a non-negative integer")
                
            if not isinstance(step['description'], str) or len(step['description']) < 5:
                raise ValidationError("Step description must be at least 5 characters long")
                
            valid_step_types = ['kill', 'collect', 'explore', 'talk', 'craft']
            if step['type'] not in valid_step_types:
                raise ValidationError(f"Invalid step type. Must be one of: {', '.join(valid_step_types)}")
    
    @staticmethod
    def validate_journal_entry(data: Dict[str, Any]) -> None:
        """Validate journal entry data."""
        if not data:
            raise ValidationError("No journal entry data provided")
            
        required_fields = ['player_id', 'quest_id', 'content']
        for field in required_fields:
            if field not in data:
                raise ValidationError(f"Missing required field: {field}")
                
        QuestValidator.validate_player_id(data['player_id'])
        QuestValidator.validate_quest_id(data['quest_id'])
        
        if not isinstance(data['content'], str) or len(data['content']) < 5:
            raise ValidationError("Journal entry content must be at least 5 characters long")
            
        if 'timestamp' in data:
            try:
                datetime.fromisoformat(data['timestamp'])
            except ValueError:
                raise ValidationError("Invalid timestamp format")


class QuestUtils:
    """Utility functions for quest management."""
    
    @staticmethod
    def create_quest(data: Dict[str, Any]) -> str:
        """
        Create a new quest in the database.
        
        Args:
            data: Dict containing quest data
            
        Returns:
            str: ID of the created quest
            
        Raises:
            ValidationError: If data is invalid
            DatabaseError: If database operation fails
        """
        try:
            # Validate quest data
            QuestValidator.validate_quest_data(data)
            
            # Generate a unique ID if not provided
            quest_id = data.get('id', f"quest_{str(uuid.uuid4())}")
            
            # Add timestamps if not present
            if 'created_at' not in data:
                data['created_at'] = datetime.utcnow().isoformat()
            if 'updated_at' not in data:
                data['updated_at'] = data['created_at']
                
            # Save to database
            set_document(f"quests/{quest_id}", data)
            
            return quest_id
        except ValidationError as e:
            logger.error(f"Validation error creating quest: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error creating quest: {str(e)}")
            raise DatabaseError(f"Failed to create quest: {str(e)}")
    
    @staticmethod
    def get_quest(quest_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a quest from the database by ID.
        
        Args:
            quest_id: ID of the quest to retrieve
            
        Returns:
            Optional[Dict[str, Any]]: Quest data or None if not found
            
        Raises:
            ValidationError: If quest_id is invalid
            DatabaseError: If database operation fails
        """
        try:
            QuestValidator.validate_quest_id(quest_id)
            return get_document(f"quests/{quest_id}")
        except ValidationError as e:
            logger.error(f"Validation error getting quest: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error getting quest: {str(e)}")
            raise DatabaseError(f"Failed to get quest: {str(e)}")
    
    @staticmethod
    def update_quest_progress(quest_id: str, step_id: int) -> bool:
        """
        Update progress on a quest step.
        
        Args:
            quest_id: ID of the quest
            step_id: ID of the step to mark as completed
            
        Returns:
            bool: True if the quest is now complete, False otherwise
            
        Raises:
            ValidationError: If quest_id is invalid
            NotFoundError: If quest or step not found
            DatabaseError: If database operation fails
        """
        try:
            QuestValidator.validate_quest_id(quest_id)
            
            # Get the quest
            quest_data = get_document(f"quests/{quest_id}")
            if not quest_data:
                raise NotFoundError(f"Quest {quest_id} not found")
                
            # Check if the step exists
            if not QuestUtils.is_valid_step(quest_data, step_id):
                raise NotFoundError(f"Step {step_id} not found in quest {quest_id}")
                
            # Update the step status
            steps = quest_data.get('steps', [])
            for i, step in enumerate(steps):
                if step.get('id') == step_id:
                    steps[i]['completed'] = True
                    break
                    
            # Check if all steps are complete
            all_complete = all(step.get('completed', False) for step in steps)
            
            # Update the quest status if all steps are complete
            if all_complete and quest_data.get('status') != 'completed':
                quest_data['status'] = 'completed'
                quest_data['completed_at'] = datetime.utcnow().isoformat()
                
            # Update the quest
            quest_data['updated_at'] = datetime.utcnow().isoformat()
            quest_data['steps'] = steps
            update_document(f"quests/{quest_id}", quest_data)
            
            return all_complete
        except ValidationError as e:
            logger.error(f"Validation error updating quest progress: {str(e)}")
            raise
        except NotFoundError as e:
            logger.error(f"Not found error updating quest progress: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error updating quest progress: {str(e)}")
            raise DatabaseError(f"Failed to update quest progress: {str(e)}")
    
    @staticmethod
    def create_journal_entry(data: Dict[str, Any]) -> str:
        """
        Create a new journal entry for a quest.
        
        Args:
            data: Dict containing journal entry data
            
        Returns:
            str: ID of the created journal entry
            
        Raises:
            ValidationError: If data is invalid
            DatabaseError: If database operation fails
        """
        try:
            # Validate journal entry data
            QuestValidator.validate_journal_entry(data)
            
            # Generate a unique ID
            entry_id = f"journal_{str(uuid.uuid4())}"
            
            # Add timestamp if not present
            if 'timestamp' not in data:
                data['timestamp'] = datetime.utcnow().isoformat()
                
            # Save to database
            set_document(f"journal_entries/{entry_id}", data)
            
            return entry_id
        except ValidationError as e:
            logger.error(f"Validation error creating journal entry: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error creating journal entry: {str(e)}")
            raise DatabaseError(f"Failed to create journal entry: {str(e)}")
    
    @staticmethod
    def get_player_journal_entries(player_id: str) -> List[Dict[str, Any]]:
        """
        Get all journal entries for a player.
        
        Args:
            player_id: ID of the player
            
        Returns:
            List[Dict[str, Any]]: List of journal entries
            
        Raises:
            ValidationError: If player_id is invalid
            DatabaseError: If database operation fails
        """
        try:
            # Validate player ID
            QuestValidator.validate_player_id(player_id)
            
            # Query the database
            entries = get_collection("journal_entries", 
                                     where=[("player_id", "==", player_id)],
                                     order_by=[("timestamp", "desc")])
            
            return entries
        except ValidationError as e:
            logger.error(f"Validation error getting player journal entries: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error getting player journal entries: {str(e)}")
            raise DatabaseError(f"Failed to get player journal entries: {str(e)}")
    
    @staticmethod
    def is_valid_step(quest_data: Dict[str, Any], step_id: int) -> bool:
        """
        Check if a step ID is valid for a quest.
        
        Args:
            quest_data: Quest data
            step_id: Step ID to check
            
        Returns:
            bool: True if step ID is valid, False otherwise
        """
        steps = quest_data.get('steps', [])
        return any(step.get('id') == step_id for step in steps) 
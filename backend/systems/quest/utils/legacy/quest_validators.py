"""
Quest input validation utilities.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import re
from app.core.utils.error_utils import ValidationError

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

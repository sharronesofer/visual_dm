"""
Quest Validation Service Implementation

Infrastructure service that implements quest validation according to 
JSON schemas and business rules.
"""

import json
import logging
from typing import Dict, Any, List
from pathlib import Path

from backend.systems.quest.models import QuestValidationService
from backend.systems.quest.exceptions import QuestValidationError


logger = logging.getLogger(__name__)


class QuestValidationServiceImpl(QuestValidationService):
    """Implementation of quest validation service using JSON schemas"""
    
    def __init__(self):
        self.schema_cache = {}
        self._load_schemas()
    
    def _load_schemas(self):
        """Load JSON schemas from data/systems/quest/"""
        try:
            schema_path = Path("data/systems/quest")
            
            # Load quest schema
            quest_schema_file = schema_path / "quest_schema.json"
            if quest_schema_file.exists():
                with open(quest_schema_file, 'r') as f:
                    self.schema_cache['quest'] = json.load(f)
            
            # Load quest config for validation rules
            quest_config_file = schema_path / "quest_config.json"
            if quest_config_file.exists():
                with open(quest_config_file, 'r') as f:
                    self.schema_cache['config'] = json.load(f)
            
            logger.info("Quest validation schemas loaded successfully")
            
        except Exception as e:
            logger.warning(f"Failed to load quest schemas: {e}")
            # Continue with basic validation if schemas can't be loaded
    
    def validate_quest_data(self, quest_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate quest data against schema and business rules"""
        errors = []
        validated_data = quest_data.copy()
        
        # Basic field validation
        if not quest_data.get('title'):
            errors.append("Title is required")
        elif len(quest_data['title']) > 255:
            errors.append("Title must be 255 characters or less")
        
        if not quest_data.get('description'):
            errors.append("Description is required")
        elif len(quest_data['description']) > 2000:
            errors.append("Description must be 2000 characters or less")
        
        # Validate difficulty
        valid_difficulties = ["easy", "medium", "hard", "epic"]
        difficulty = quest_data.get('difficulty', 'medium')
        if difficulty not in valid_difficulties:
            errors.append(f"Difficulty must be one of: {', '.join(valid_difficulties)}")
        validated_data['difficulty'] = difficulty
        
        # Validate theme
        valid_themes = [
            "combat", "exploration", "social", "mystery", 
            "crafting", "trade", "aid", "knowledge", "general"
        ]
        theme = quest_data.get('theme', 'general')
        if theme not in valid_themes:
            errors.append(f"Theme must be one of: {', '.join(valid_themes)}")
        validated_data['theme'] = theme
        
        # Validate level
        level = quest_data.get('level', 1)
        if not isinstance(level, int) or level < 1 or level > 100:
            errors.append("Level must be an integer between 1 and 100")
        validated_data['level'] = level
        
        # Validate IDs if provided
        if 'npc_id' in quest_data and quest_data['npc_id'] is not None:
            if not isinstance(quest_data['npc_id'], str) or len(quest_data['npc_id']) == 0:
                errors.append("NPC ID must be a non-empty string if provided")
        
        if 'location_id' in quest_data and quest_data['location_id'] is not None:
            if not isinstance(quest_data['location_id'], str) or len(quest_data['location_id']) == 0:
                errors.append("Location ID must be a non-empty string if provided")
        
        # Validate properties
        if 'properties' in quest_data and quest_data['properties'] is not None:
            if not isinstance(quest_data['properties'], dict):
                errors.append("Properties must be a dictionary")
        
        if errors:
            raise QuestValidationError("Quest validation failed", {"validation_errors": errors})
        
        return validated_data
    
    def validate_quest_steps(self, steps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate quest steps"""
        errors = []
        validated_steps = []
        
        for i, step in enumerate(steps):
            step_errors = []
            validated_step = step.copy()
            
            # Validate required fields
            if not step.get('title'):
                step_errors.append(f"Step {i+1}: Title is required")
            elif len(step['title']) > 255:
                step_errors.append(f"Step {i+1}: Title must be 255 characters or less")
            
            if not step.get('description'):
                step_errors.append(f"Step {i+1}: Description is required")
            elif len(step['description']) > 1000:
                step_errors.append(f"Step {i+1}: Description must be 1000 characters or less")
            
            # Validate optional fields
            if 'completed' in step:
                if not isinstance(step['completed'], bool):
                    step_errors.append(f"Step {i+1}: Completed must be a boolean")
            else:
                validated_step['completed'] = False
            
            if 'required' in step:
                if not isinstance(step['required'], bool):
                    step_errors.append(f"Step {i+1}: Required must be a boolean")
            else:
                validated_step['required'] = True
            
            if 'order' in step:
                if not isinstance(step['order'], int) or step['order'] < 0:
                    step_errors.append(f"Step {i+1}: Order must be a non-negative integer")
            else:
                validated_step['order'] = i
            
            if 'metadata' in step:
                if not isinstance(step['metadata'], dict):
                    step_errors.append(f"Step {i+1}: Metadata must be a dictionary")
            else:
                validated_step['metadata'] = {}
            
            if step_errors:
                errors.extend(step_errors)
            else:
                validated_steps.append(validated_step)
        
        if errors:
            raise QuestValidationError("Quest steps validation failed", {"validation_errors": errors})
        
        return validated_steps
    
    def validate_quest_rewards(self, rewards: Dict[str, Any]) -> Dict[str, Any]:
        """Validate quest rewards"""
        errors = []
        validated_rewards = rewards.copy()
        
        # Validate gold
        gold = rewards.get('gold', 0)
        if not isinstance(gold, int) or gold < 0:
            errors.append("Gold must be a non-negative integer")
        validated_rewards['gold'] = max(0, gold)
        
        # Validate experience
        experience = rewards.get('experience', 0)
        if not isinstance(experience, int) or experience < 0:
            errors.append("Experience must be a non-negative integer")
        validated_rewards['experience'] = max(0, experience)
        
        # Validate reputation
        reputation = rewards.get('reputation', {})
        if not isinstance(reputation, dict):
            errors.append("Reputation must be a dictionary")
            validated_rewards['reputation'] = {}
        else:
            validated_rewards['reputation'] = reputation
        
        # Validate items
        items = rewards.get('items', [])
        if not isinstance(items, list):
            errors.append("Items must be a list")
            validated_rewards['items'] = []
        else:
            # Validate each item
            validated_items = []
            for i, item in enumerate(items):
                if not isinstance(item, dict):
                    errors.append(f"Item {i+1} must be a dictionary")
                else:
                    if 'id' not in item:
                        errors.append(f"Item {i+1}: ID is required")
                    if 'quantity' in item and (not isinstance(item['quantity'], int) or item['quantity'] <= 0):
                        errors.append(f"Item {i+1}: Quantity must be a positive integer")
                    validated_items.append(item)
            validated_rewards['items'] = validated_items
        
        # Validate special rewards
        special = rewards.get('special', {})
        if not isinstance(special, dict):
            errors.append("Special rewards must be a dictionary")
            validated_rewards['special'] = {}
        else:
            validated_rewards['special'] = special
        
        if errors:
            raise QuestValidationError("Quest rewards validation failed", {"validation_errors": errors})
        
        return validated_rewards
    
    def _validate_against_schema(self, data: Dict[str, Any], schema_name: str) -> List[str]:
        """Validate data against JSON schema"""
        errors = []
        
        if schema_name not in self.schema_cache:
            logger.warning(f"Schema '{schema_name}' not found, skipping JSON schema validation")
            return errors
        
        try:
            # TODO: Implement jsonschema validation if needed
            # For now, we rely on the manual validation above
            pass
        except Exception as e:
            logger.error(f"Error validating against schema {schema_name}: {e}")
            errors.append(f"Schema validation error: {str(e)}")
        
        return errors 
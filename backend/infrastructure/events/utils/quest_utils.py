"""
Quest utilities for managing quest-related operations.
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass
from functools import lru_cache
import json
import os

from backend.systems.quest import Quest, QuestStatus, QuestType
from backend.systems.character import Character
from backend.systems.npc import NPC
from backend.infrastructure.utils import ValidationError

logger = logging.getLogger(__name__)

@dataclass
class QuestTemplate:
    """Immutable quest template for efficient quest generation."""
    name: str
    description: str
    quest_type: QuestType
    level: int
    rewards: Dict[str, Any]
    requirements: Dict[str, Any]
    objectives: List[Dict[str, Any]]
    time_limit: Optional[timedelta] = None

class QuestUtils:
    """Utility class for quest-related operations."""
    
    def __init__(self):
        self._quest_templates = self._init_quest_templates()
        self._quest_cache = {}
        
    def _init_quest_templates(self) -> Dict[str, QuestTemplate]:
        """Initialize quest templates."""
        return {
            'fetch': QuestTemplate(
                name="Item Retrieval",
                description="Retrieve a specific item from a location",
                quest_type=QuestType.FETCH,
                level=1,
                rewards={'gold': 100, 'xp': 50},
                requirements={'level': 1},
                objectives=[{'type': 'fetch', 'item': 'artifact', 'location': 'dungeon'}]
            ),
            'kill': QuestTemplate(
                name="Monster Hunt",
                description="Defeat a specific monster or group of monsters",
                quest_type=QuestType.KILL,
                level=2,
                rewards={'gold': 200, 'xp': 100},
                requirements={'level': 2},
                objectives=[{'type': 'kill', 'monster': 'goblin', 'count': 5}]
            ),
            'escort': QuestTemplate(
                name="Escort Mission",
                description="Safely escort an NPC to a destination",
                quest_type=QuestType.ESCORT,
                level=3,
                rewards={'gold': 300, 'xp': 150},
                requirements={'level': 3},
                objectives=[{'type': 'escort', 'npc': 'merchant', 'destination': 'town'}],
                time_limit=timedelta(hours=2)
            )
        }
    
    @lru_cache(maxsize=128)
    def generate_quest(
        self,
        quest_type: str,
        level: int,
        region: str,
        giver: Optional[NPC] = None
    ) -> Quest:
        """Generate a new quest with caching."""
        try:
            template = self._quest_templates.get(quest_type)
            if not template:
                raise ValidationError(f"Invalid quest type: {quest_type}")
                
            # Adjust quest based on level
            adjusted_rewards = {
                k: v * level for k, v in template.rewards.items()
            }
            
            # Create quest
            quest = Quest(
                name=f"{template.name} (Level {level})",
                description=template.description,
                quest_type=template.quest_type,
                level=level,
                region=region,
                status=QuestStatus.AVAILABLE,
                rewards=adjusted_rewards,
                requirements=template.requirements,
                objectives=template.objectives,
                time_limit=template.time_limit,
                giver_id=giver.id if giver else None
            )
            
            return quest
            
        except Exception as e:
            logger.error(f"Failed to generate quest: {str(e)}")
            raise
    
    def update_quest_progress(
        self,
        quest: Quest,
        character: Character,
        progress_data: Dict[str, Any]
    ) -> Tuple[bool, Dict[str, Any]]:
        """Update quest progress and check completion."""
        try:
            # Update objectives
            for objective in quest.objectives:
                if objective['type'] == progress_data.get('type'):
                    if 'count' in objective:
                        objective['current'] = min(
                            objective.get('current', 0) + progress_data.get('count', 1),
                            objective['count']
                        )
                    elif 'completed' not in objective:
                        objective['completed'] = True
            
            # Check completion
            is_completed = all(
                objective.get('completed', False) or
                objective.get('current', 0) >= objective.get('count', 1)
                for objective in quest.objectives
            )
            
            if is_completed:
                quest.status = QuestStatus.COMPLETED
                self._apply_quest_rewards(character, quest.rewards)
            
            return is_completed, {
                'quest_id': quest.id,
                'status': quest.status,
                'objectives': quest.objectives
            }
            
        except Exception as e:
            logger.error(f"Failed to update quest progress: {str(e)}")
            raise
    
    def _apply_quest_rewards(self, character: Character, rewards: Dict[str, Any]) -> None:
        """Apply quest rewards to character."""
        try:
            if 'gold' in rewards:
                character.gold += rewards['gold']
            if 'xp' in rewards:
                character.experience += rewards['xp']
            if 'items' in rewards:
                for item in rewards['items']:
                    character.inventory.add_item(item)
                    
        except Exception as e:
            logger.error(f"Failed to apply quest rewards: {str(e)}")
            raise
    
    def validate_quest_requirements(
        self,
        quest: Quest,
        character: Character
    ) -> Tuple[bool, List[str]]:
        """Validate if character meets quest requirements."""
        try:
            requirements = quest.requirements
            failures = []
            
            if 'level' in requirements and character.level < requirements['level']:
                failures.append(f"Level {requirements['level']} required")
                
            if 'items' in requirements:
                for item in requirements['items']:
                    if not character.inventory.has_item(item):
                        failures.append(f"Item {item} required")
                        
            if 'quests' in requirements:
                for required_quest in requirements['quests']:
                    if not any(q.id == required_quest for q in character.completed_quests):
                        failures.append(f"Quest {required_quest} must be completed")
            
            return len(failures) == 0, failures
            
        except Exception as e:
            logger.error(f"Failed to validate quest requirements: {str(e)}")
            raise
    
    def get_available_quests(
        self,
        character: Character,
        region: str
    ) -> List[Quest]:
        """Get available quests for character in region."""
        try:
            available_quests = []
            
            for quest_type, template in self._quest_templates.items():
                quest = self.generate_quest(quest_type, character.level, region)
                is_valid, _ = self.validate_quest_requirements(quest, character)
                
                if is_valid:
                    available_quests.append(quest)
            
            return available_quests
            
        except Exception as e:
            logger.error(f"Failed to get available quests: {str(e)}")
            raise

class QuestTemplateManager:
    """Manages loading and retrieval of quest templates from configuration files."""
    def __init__(self, template_dir: str = "app/core/quest_templates"):
        self.template_dir = template_dir
        self.templates = self._load_templates()

    def _load_templates(self) -> dict:
        templates = {}
        if not os.path.isdir(self.template_dir):
            return templates
        for filename in os.listdir(self.template_dir):
            if filename.endswith(".json"):
                with open(os.path.join(self.template_dir, filename), "r") as f:
                    data = json.load(f)
                    templates[data["type"]] = data
        return templates

    def get_template(self, quest_type: str) -> dict:
        return self.templates.get(quest_type, {})

    def all_templates(self) -> dict:
        return self.templates

class QuestGenerator:
    """Generates quests dynamically based on templates, player, and world context."""
    def __init__(self, template_manager: QuestTemplateManager):
        self.template_manager = template_manager

    def generate_quest(self, quest_type: str, player_level: int, world_state: dict, faction_relations: dict = None) -> dict:
        template = self.template_manager.get_template(quest_type)
        if not template:
            raise ValueError(f"No template found for quest type: {quest_type}")
        quest_data = template.copy()
        # Scale difficulty and rewards
        quest_data["level_requirement"] = max(template.get("level_requirement", 1), player_level)
        quest_data["experience_reward"] = template.get("experience_reward", 0) * player_level
        quest_data["gold_reward"] = template.get("gold_reward", 0) * player_level
        # Optionally adjust based on world_state or faction_relations
        # ... (custom logic can be added here)
        return quest_data

    def generate_for_player(self, player, world_state: dict) -> list:
        quests = []
        for quest_type in self.template_manager.all_templates():
            quest = self.generate_quest(quest_type, player.level, world_state)
            quests.append(quest)
        return quests 
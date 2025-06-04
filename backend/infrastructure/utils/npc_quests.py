"""
NPC quest management.
Handles NPC-generated quests, personal quests, and related NPC quest interactions.
This module contains business logic for NPC quest generation and management.
"""

import logging
import random
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from uuid import UUID

# Import infrastructure components
from backend.infrastructure.systems.quest.repositories.npc_quest_repository import NPCQuestRepository
from backend.infrastructure.utils import ValidationError, NotFoundError, DatabaseError
from backend.systems.npc import NPCManager
from backend.systems.quest.models import QuestData, QuestDifficulty, QuestTheme, QuestStatus
from backend.systems.quest.services.generator import QuestGenerationBusinessService
from backend.systems.quest.utils import QuestBusinessUtils

logger = logging.getLogger(__name__)

class NPCQuestManager:
    """Manages NPC-initiated quests and related interactions."""
    
    def __init__(self):
        """Initialize the NPC quest manager."""
        self.repository = NPCQuestRepository()
    
    def generate_journal_entry(self, quest_data: Dict[str, Any], player_id: str) -> Dict[str, Any]:
        """
        Generate a journal entry for an NPC quest.
        
        Args:
            quest_data: Dict containing quest data
            player_id: ID of the player
            
        Returns:
            Dict[str, Any]: Journal entry data
            
        Raises:
            ValidationError: If player_id is invalid or quest_data is invalid
        """
        try:
            QuestValidator.validate_player_id(player_id)
            
            # Ensure required quest data is present
            required_fields = ['id', 'title']
            for field in required_fields:
                if field not in quest_data:
                    raise ValidationError(f"Missing required field in quest data: {field}")
                    
            return {
                'region': quest_data.get('region', 'unknown'),
                'poi': quest_data.get('poi', 'unknown'),
                'quest_id': quest_data['id'],
                'player_id': player_id,
                'content': f"Started quest: {quest_data['title']}",
                'tags': ['quest', quest_data.get('difficulty', 'unknown'), quest_data.get('reward_type', 'none')],
                'timestamp': datetime.utcnow().isoformat()
            }
        except ValidationError as e:
            logger.error(f"Validation error generating journal entry: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error generating journal entry: {str(e)}")
            raise ValidationError(f"Failed to generate journal entry: {str(e)}")
    
    def should_generate_personal_quest(self, npc_data: Dict[str, Any]) -> bool:
        """
        Determine if an NPC should generate a personal quest based on business rules.
        
        Args:
            npc_data: NPC data
            
        Returns:
            bool: Whether a personal quest should be generated
        """
        # Check if NPC has any active personal quests
        active_quests = self.repository.get_npc_active_quests(npc_data.get('id'))
        
        # Skip if already has an active personal quest
        if active_quests and len(active_quests) > 0:
            return False
        
        # Business rule: 10% chance to generate a new personal quest
        return random.random() < 0.1
    
    def generate_quest_parameters(self, npc_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate quest parameters based on NPC characteristics.
        
        Args:
            npc_data: NPC data
            
        Returns:
            Dict[str, Any]: Quest parameters
        """
        npc_profession = npc_data.get('profession', 'commoner')
        npc_personality = npc_data.get('personality', {})
        npc_location = npc_data.get('location', {})
        
        # Choose theme based on profession
        theme_map = {
            'blacksmith': 'crafting',
            'merchant': 'trade',
            'guard': 'combat',
            'healer': 'aid',
            'scholar': 'knowledge',
            'farmer': 'gathering',
            'noble': 'social'
        }
        theme = theme_map.get(npc_profession, 'general')
        
        # Choose difficulty based on importance
        importance = npc_data.get('importance', 1)
        difficulty_map = {
            1: 'easy',
            2: 'easy',
            3: 'medium',
            4: 'medium',
            5: 'hard'
        }
        difficulty = difficulty_map.get(importance, 'easy')
        
        return {
            'theme': theme,
            'difficulty': difficulty,
            'npc_profession': npc_profession,
            'npc_location': npc_location,
            'importance': importance
        }
    
    def create_personal_quest_data(self, npc_data: Dict[str, Any], quest_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create quest data for a personal quest.
        
        Args:
            npc_data: NPC data
            quest_params: Quest parameters
            
        Returns:
            Dict[str, Any]: Complete quest data
        """
        theme = quest_params['theme']
        difficulty = quest_params['difficulty']
        
        # Generate quest data
        title = generate_quest_title(theme, difficulty)
        description = f"A personal quest from {npc_data.get('name', 'an NPC')}"
        
        quest_data = {
            'title': title,
            'description': description,
            'npc_id': npc_data.get('id'),
            'npc_name': npc_data.get('name', 'Unknown'),
            'type': 'personal',
            'theme': theme,
            'difficulty': difficulty,
            'level': max(1, npc_data.get('level', 1)),
            'location': quest_params['npc_location'],
            'status': 'pending',
            'steps': generate_quest_steps(theme, difficulty),
            'rewards': {
                'gold': calculate_quest_reward(difficulty, 'gold'),
                'experience': calculate_quest_reward(difficulty, 'experience'),
                'reputation': {
                    'amount': calculate_quest_reward(difficulty, 'reputation')['amount'],
                    'faction': npc_data.get('faction', 'none')
                }
            },
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        }
        
        return quest_data
    
    def npc_personal_quest_tick(self, npc_id: str) -> Optional[Dict[str, Any]]:
        """
        Check if an NPC should generate a personal quest during world tick.
        
        Args:
            npc_id: ID of the NPC
            
        Returns:
            Optional[Dict[str, Any]]: Generated quest data or None if no quest was generated
            
        Raises:
            ValidationError: If npc_id is invalid
        """
        try:
            # Basic validation
            if not npc_id:
                raise ValidationError("NPC ID is required")
                
            # Check if NPC exists
            npc_data = NPCManager.get_npc(npc_id)
            if not npc_data:
                return None
            
            # Check business rules for quest generation
            if not self.should_generate_personal_quest(npc_data):
                return None
            
            # Generate quest parameters
            quest_params = self.generate_quest_parameters(npc_data)
            
            # Create quest data
            quest_data = self.create_personal_quest_data(npc_data, quest_params)
            
            # Save the quest to the database via repository
            quest_id = self.repository.create_quest(quest_data)
            
            # Return the complete quest data with ID
            return {**quest_data, 'id': quest_id}
                
        except ValidationError as e:
            logger.error(f"Validation error in NPC personal quest tick: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error in NPC personal quest tick: {str(e)}")
            return None
    
    def get_npc_quests(self, npc_id: str) -> List[Dict[str, Any]]:
        """
        Get all quests associated with an NPC.
        
        Args:
            npc_id: ID of the NPC
            
        Returns:
            List[Dict[str, Any]]: List of quests associated with the NPC
            
        Raises:
            ValidationError: If npc_id is invalid
        """
        try:
            if not npc_id:
                raise ValidationError("NPC ID is required")
            
            return self.repository.get_all_npc_quests(npc_id)
        except ValidationError as e:
            logger.error(f"Validation error getting NPC quests: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error getting NPC quests: {str(e)}")
            return []
    
    def assign_quest_to_player(self, quest_id: str, player_id: str) -> Dict[str, Any]:
        """
        Assign a quest to a player.
        
        Args:
            quest_id: ID of the quest
            player_id: ID of the player
            
        Returns:
            Dict[str, Any]: Updated quest data
            
        Raises:
            ValidationError: If quest_id or player_id is invalid
        """
        try:
            if not quest_id:
                raise ValidationError("Quest ID is required")
            if not player_id:
                raise ValidationError("Player ID is required")
            
            # Validate player exists (business rule)
            QuestValidator.validate_player_id(player_id)
            
            # Use repository to assign quest
            quest_data = self.repository.assign_quest_to_player(quest_id, player_id)
            
            # Generate journal entry for quest assignment
            journal_entry = self.generate_journal_entry(quest_data, player_id)
            self.repository.create_journal_entry(journal_entry)
            
            return quest_data
        except ValidationError as e:
            logger.error(f"Validation error assigning quest to player: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error assigning quest to player: {str(e)}")
            raise ValidationError(f"Failed to assign quest to player: {str(e)}")
    
    def generate_npc_quests_for_region(self, region_id: str, count: int = 3) -> List[Dict[str, Any]]:
        """
        Generate NPC quests for a region.
        
        Args:
            region_id: ID of the region
            count: Number of quests to generate
            
        Returns:
            List[Dict[str, Any]]: List of generated quests
            
        Raises:
            ValidationError: If region_id is invalid
        """
        try:
            if not region_id:
                raise ValidationError("Region ID is required")
            
            generated_quests = []
            
            # Get NPCs in the region
            npcs_in_region = NPCManager.get_npcs_in_region(region_id)
            
            if not npcs_in_region:
                logger.warning(f"No NPCs found in region {region_id}")
                return []
            
            # Generate quests from random NPCs
            for _ in range(min(count, len(npcs_in_region))):
                npc = random.choice(npcs_in_region)
                quest_data = self.npc_personal_quest_tick(npc.get('id'))
                
                if quest_data:
                    generated_quests.append(quest_data)
            
            return generated_quests
        except ValidationError as e:
            logger.error(f"Validation error generating NPC quests for region: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error generating NPC quests for region: {str(e)}")
            return [] 
"""
NPC quest management.
Handles NPC-generated quests, personal quests, and related NPC quest interactions.
"""

import logging
import random
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any

from backend.infrastructure.utils import (
    get_firestore_client,
    get_document,
    set_document,
    update_document,
    get_collection
)
from backend.infrastructure.utils import ValidationError, NotFoundError, DatabaseError
from backend.systems.npc import NPCManager
from backend.systems.quest.utils import QuestValidator, QuestUtils
from backend.systems.quest.generator import QuestGenerator

logger = logging.getLogger(__name__)

class NPCQuestManager:
    """Manages NPC-initiated quests and related interactions."""
    
    @staticmethod
    def generate_journal_entry(quest_data: Dict[str, Any], player_id: str) -> Dict[str, Any]:
        """
        Generate a journal entry for an NPC quest.
        
        Args:
            quest_data: Dict containing quest data
            player_id: ID of the player
            
        Returns:
            Dict[str, Any]: Journal entry data
            
        Raises:
            ValidationError: If player_id is invalid or quest_data is invalid
            DatabaseError: If operation fails
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
            raise DatabaseError(f"Failed to generate journal entry: {str(e)}")
    
    @staticmethod
    def npc_personal_quest_tick(npc_id: str) -> Optional[Dict[str, Any]]:
        """
        Check if an NPC should generate a personal quest during world tick.
        
        Args:
            npc_id: ID of the NPC
            
        Returns:
            Optional[Dict[str, Any]]: Generated quest data or None if no quest was generated
            
        Raises:
            ValidationError: If npc_id is invalid
            DatabaseError: If operation fails
        """
        try:
            # Basic validation
            if not npc_id:
                raise ValidationError("NPC ID is required")
                
            # Check if NPC exists
            npc_data = NPCManager.get_npc(npc_id)
            if not npc_data:
                return None
                
            # Check if NPC has any active personal quests
            active_quests = get_collection(
                "quests", 
                where=[
                    ("npc_id", "==", npc_id),
                    ("type", "==", "personal"),
                    ("status", "in", ["pending", "active"])
                ]
            )
            
            # Skip if already has an active personal quest
            if active_quests and len(active_quests) > 0:
                return None
            
            # 10% chance to generate a new personal quest
            if random.random() < 0.1:
                # Determine quest parameters based on NPC characteristics
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
                
                # Generate quest data
                title = QuestGenerator.generate_quest_title(theme, difficulty)
                description = f"A personal quest from {npc_data.get('name', 'an NPC')}"
                
                quest_data = {
                    'title': title,
                    'description': description,
                    'npc_id': npc_id,
                    'npc_name': npc_data.get('name', 'Unknown'),
                    'type': 'personal',
                    'theme': theme,
                    'difficulty': difficulty,
                    'level': max(1, npc_data.get('level', 1)),
                    'location': npc_location,
                    'status': 'pending',
                    'steps': QuestGenerator.generate_quest_steps(theme, difficulty),
                    'rewards': {
                        'gold': QuestGenerator.calculate_quest_reward(difficulty, 'gold'),
                        'experience': QuestGenerator.calculate_quest_reward(difficulty, 'experience'),
                        'reputation': {
                            'amount': QuestGenerator.calculate_quest_reward(difficulty, 'reputation')['amount'],
                            'faction': npc_data.get('faction', 'none')
                        }
                    },
                    'created_at': datetime.utcnow().isoformat(),
                    'updated_at': datetime.utcnow().isoformat()
                }
                
                # Save the quest to the database
                quest_id = QuestUtils.create_quest(quest_data)
                
                # Return the complete quest data with ID
                return {**quest_data, 'id': quest_id}
                
            return None
        except ValidationError as e:
            logger.error(f"Validation error in NPC personal quest tick: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error in NPC personal quest tick: {str(e)}")
            return None
    
    @staticmethod
    def get_npc_quests(npc_id: str) -> List[Dict[str, Any]]:
        """
        Get all quests associated with an NPC.
        
        Args:
            npc_id: ID of the NPC
            
        Returns:
            List[Dict[str, Any]]: List of quests associated with the NPC
            
        Raises:
            ValidationError: If npc_id is invalid
            DatabaseError: If operation fails
        """
        try:
            # Basic validation
            if not npc_id:
                raise ValidationError("NPC ID is required")
                
            # Query for quests by NPC ID
            quests = get_collection(
                "quests", 
                where=[("npc_id", "==", npc_id)]
            )
            
            return quests if quests else []
        except ValidationError as e:
            logger.error(f"Validation error getting NPC quests: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error getting NPC quests: {str(e)}")
            raise DatabaseError(f"Failed to get NPC quests: {str(e)}")
    
    @staticmethod
    def assign_quest_to_player(quest_id: str, player_id: str) -> Dict[str, Any]:
        """
        Assign an NPC quest to a player.
        
        Args:
            quest_id: ID of the quest
            player_id: ID of the player
            
        Returns:
            Dict[str, Any]: Updated quest data
            
        Raises:
            ValidationError: If quest_id or player_id is invalid
            NotFoundError: If quest not found
            DatabaseError: If operation fails
        """
        try:
            QuestValidator.validate_quest_id(quest_id)
            QuestValidator.validate_player_id(player_id)
            
            # Get the quest
            quest_data = QuestUtils.get_quest(quest_id)
            if not quest_data:
                raise NotFoundError(f"Quest {quest_id} not found")
                
            # Update the quest with player information
            quest_data['player_id'] = player_id
            quest_data['status'] = 'active'
            quest_data['assigned_at'] = datetime.utcnow().isoformat()
            quest_data['updated_at'] = datetime.utcnow().isoformat()
            
            # Save the updated quest
            update_document(f"quests/{quest_id}", quest_data)
            
            # Create a journal entry for the player
            journal_entry = NPCQuestManager.generate_journal_entry(quest_data, player_id)
            QuestUtils.create_journal_entry(journal_entry)
            
            return quest_data
        except ValidationError as e:
            logger.error(f"Validation error assigning quest to player: {str(e)}")
            raise
        except NotFoundError as e:
            logger.error(f"Not found error assigning quest to player: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error assigning quest to player: {str(e)}")
            raise DatabaseError(f"Failed to assign quest to player: {str(e)}")
    
    @staticmethod
    def generate_npc_quests_for_region(region_id: str, count: int = 3) -> List[Dict[str, Any]]:
        """
        Generate a batch of NPC quests for a specific region.
        
        Args:
            region_id: ID of the region
            count: Number of quests to generate (default: 3)
            
        Returns:
            List[Dict[str, Any]]: List of generated quest data
            
        Raises:
            ValidationError: If region_id is invalid
            DatabaseError: If operation fails
        """
        try:
            # Basic validation
            if not region_id:
                raise ValidationError("Region ID is required")
                
            if count < 1:
                raise ValidationError("Count must be at least 1")
                
            # Get NPCs in the region
            npcs = NPCManager.get_npcs_in_region(region_id)
            if not npcs:
                return []
                
            # Filter NPCs that could give quests (importance > 1)
            potential_quest_givers = [
                npc for npc in npcs 
                if npc.get('importance', 0) > 1
            ]
            
            # If no suitable NPCs found, return empty list
            if not potential_quest_givers:
                return []
                
            # Generate quests using random NPCs from the region
            generated_quests = []
            for _ in range(min(count, len(potential_quest_givers))):
                # Select a random NPC from the filtered list
                npc = random.choice(potential_quest_givers)
                
                # Try to generate a quest for this NPC
                quest = NPCQuestManager.npc_personal_quest_tick(npc['id'])
                if quest:
                    generated_quests.append(quest)
                    
            return generated_quests
        except ValidationError as e:
            logger.error(f"Validation error generating NPC quests for region: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error generating NPC quests for region: {str(e)}")
            raise DatabaseError(f"Failed to generate NPC quests for region: {str(e)}") 
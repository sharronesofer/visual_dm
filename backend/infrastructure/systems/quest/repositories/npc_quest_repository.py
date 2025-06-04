"""
NPC Quest Repository

Handles database operations for NPC-related quests.
This module contains technical database access concerns separated from business logic.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from backend.infrastructure.utils import (
    get_firestore_client,
    get_document,
    set_document,
    update_document,
    get_collection
)
from backend.infrastructure.utils import ValidationError, NotFoundError, DatabaseError

logger = logging.getLogger(__name__)

class NPCQuestRepository:
    """Repository for NPC quest database operations."""
    
    @staticmethod
    def create_journal_entry(journal_entry: Dict[str, Any]) -> str:
        """
        Create a journal entry in the database.
        
        Args:
            journal_entry: Journal entry data
            
        Returns:
            str: ID of the created journal entry
            
        Raises:
            DatabaseError: If operation fails
        """
        try:
            # Add timestamp if not present
            if 'timestamp' not in journal_entry:
                journal_entry['timestamp'] = datetime.utcnow().isoformat()
            
            # TODO: Implement actual database save
            # For now, return a placeholder ID
            return f"journal_{datetime.utcnow().timestamp()}"
        except Exception as e:
            logger.error(f"Error creating journal entry: {str(e)}")
            raise DatabaseError(f"Failed to create journal entry: {str(e)}")
    
    @staticmethod
    def get_npc_active_quests(npc_id: str) -> List[Dict[str, Any]]:
        """
        Get all active quests associated with an NPC.
        
        Args:
            npc_id: ID of the NPC
            
        Returns:
            List[Dict[str, Any]]: List of active quests
            
        Raises:
            DatabaseError: If operation fails
        """
        try:
            active_quests = get_collection(
                "quests", 
                where=[
                    ("npc_id", "==", npc_id),
                    ("type", "==", "personal"),
                    ("status", "in", ["pending", "active"])
                ]
            )
            return active_quests or []
        except Exception as e:
            logger.error(f"Error getting NPC active quests: {str(e)}")
            raise DatabaseError(f"Failed to get NPC active quests: {str(e)}")
    
    @staticmethod
    def create_quest(quest_data: Dict[str, Any]) -> str:
        """
        Create a quest in the database.
        
        Args:
            quest_data: Quest data to save
            
        Returns:
            str: ID of the created quest
            
        Raises:
            DatabaseError: If operation fails
        """
        try:
            # Add ID if not present
            if 'id' not in quest_data:
                quest_data['id'] = f"quest_{datetime.utcnow().timestamp()}"
            
            # TODO: Implement actual database save
            # For now, return the quest ID
            return quest_data['id']
        except Exception as e:
            logger.error(f"Error creating quest: {str(e)}")
            raise DatabaseError(f"Failed to create quest: {str(e)}")
    
    @staticmethod
    def get_all_npc_quests(npc_id: str) -> List[Dict[str, Any]]:
        """
        Get all quests associated with an NPC.
        
        Args:
            npc_id: ID of the NPC
            
        Returns:
            List[Dict[str, Any]]: List of quests associated with the NPC
            
        Raises:
            DatabaseError: If operation fails
        """
        try:
            quests = get_collection(
                "quests",
                where=[("npc_id", "==", npc_id)]
            )
            return quests or []
        except Exception as e:
            logger.error(f"Error getting NPC quests: {str(e)}")
            raise DatabaseError(f"Failed to get NPC quests: {str(e)}")
    
    @staticmethod
    def assign_quest_to_player(quest_id: str, player_id: str) -> Dict[str, Any]:
        """
        Assign a quest to a player in the database.
        
        Args:
            quest_id: ID of the quest
            player_id: ID of the player
            
        Returns:
            Dict[str, Any]: Updated quest data
            
        Raises:
            DatabaseError: If operation fails
        """
        try:
            # Get the quest
            quest_data = get_document("quests", quest_id)
            if not quest_data:
                raise NotFoundError(f"Quest {quest_id} not found")
            
            # Update quest with player assignment
            quest_data["player_id"] = player_id
            quest_data["status"] = "assigned"
            quest_data["assigned_at"] = datetime.utcnow().isoformat()
            quest_data["updated_at"] = datetime.utcnow().isoformat()
            
            # Save updated quest
            update_document("quests", quest_id, quest_data)
            
            return quest_data
        except Exception as e:
            logger.error(f"Error assigning quest to player: {str(e)}")
            raise DatabaseError(f"Failed to assign quest to player: {str(e)}")
    
    @staticmethod
    def get_region_quests(region_id: str, quest_type: str = None) -> List[Dict[str, Any]]:
        """
        Get quests for a specific region.
        
        Args:
            region_id: ID of the region
            quest_type: Optional quest type filter
            
        Returns:
            List[Dict[str, Any]]: List of quests in the region
            
        Raises:
            DatabaseError: If operation fails
        """
        try:
            where_conditions = [("region_id", "==", region_id)]
            if quest_type:
                where_conditions.append(("type", "==", quest_type))
            
            quests = get_collection("quests", where=where_conditions)
            return quests or []
        except Exception as e:
            logger.error(f"Error getting region quests: {str(e)}")
            raise DatabaseError(f"Failed to get region quests: {str(e)}") 
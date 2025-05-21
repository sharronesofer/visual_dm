"""
Quest repository for database operations.
Provides a centralized interface for quest data storage and retrieval.
"""

import logging
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional

from backend.core.utils.firebase_utils import (
    get_firestore_client,
    get_document,
    set_document,
    update_document,
    get_collection,
    delete_document
)
from backend.core.utils.error import ValidationError, NotFoundError, DatabaseError
from backend.core.database import db

logger = logging.getLogger(__name__)


class QuestRepository:
    """Repository for quest-related database operations."""
    
    @staticmethod
    def get_quests_by_player(player_id: str) -> List[Dict[str, Any]]:
        """
        Get all quests for a specific player.
        
        Args:
            player_id: ID of the player
            
        Returns:
            List of quest dictionaries
            
        Raises:
            DatabaseError: If database operation fails
        """
        try:
            quests = get_collection(
                "quests", 
                where=[("player_id", "==", player_id)]
            )
            return quests if quests else []
        except Exception as e:
            logger.error(f"Error getting quests for player {player_id}: {str(e)}")
            raise DatabaseError(f"Failed to get quests: {str(e)}")
    
    @staticmethod
    def get_quests_by_npc(npc_id: str) -> List[Dict[str, Any]]:
        """
        Get all quests associated with a specific NPC.
        
        Args:
            npc_id: ID of the NPC
            
        Returns:
            List of quest dictionaries
            
        Raises:
            DatabaseError: If database operation fails
        """
        try:
            quests = get_collection(
                "quests", 
                where=[("npc_id", "==", npc_id)]
            )
            return quests if quests else []
        except Exception as e:
            logger.error(f"Error getting quests for NPC {npc_id}: {str(e)}")
            raise DatabaseError(f"Failed to get quests: {str(e)}")
    
    @staticmethod
    def get_active_quests_by_status(status: str) -> List[Dict[str, Any]]:
        """
        Get all quests with a specific status.
        
        Args:
            status: Quest status to filter by
            
        Returns:
            List of quest dictionaries
            
        Raises:
            DatabaseError: If database operation fails
        """
        try:
            quests = get_collection(
                "quests", 
                where=[("status", "==", status)]
            )
            return quests if quests else []
        except Exception as e:
            logger.error(f"Error getting quests with status {status}: {str(e)}")
            raise DatabaseError(f"Failed to get quests: {str(e)}")
    
    @staticmethod
    def get_quest(quest_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific quest by ID.
        
        Args:
            quest_id: ID of the quest
            
        Returns:
            Quest dictionary or None if not found
            
        Raises:
            DatabaseError: If database operation fails
        """
        try:
            return get_document(f"quests/{quest_id}")
        except Exception as e:
            logger.error(f"Error getting quest {quest_id}: {str(e)}")
            raise DatabaseError(f"Failed to get quest: {str(e)}")
    
    @staticmethod
    def create_quest(quest_data: Dict[str, Any]) -> str:
        """
        Create a new quest.
        
        Args:
            quest_data: Quest data dictionary
            
        Returns:
            ID of the created quest
            
        Raises:
            DatabaseError: If database operation fails
        """
        try:
            # Generate ID if not provided
            quest_id = quest_data.get("id", f"quest_{str(uuid.uuid4())}")
            
            # Add timestamps
            now = datetime.utcnow().isoformat()
            if "created_at" not in quest_data:
                quest_data["created_at"] = now
            if "updated_at" not in quest_data:
                quest_data["updated_at"] = now
            
            # Store in database
            set_document(f"quests/{quest_id}", quest_data)
            
            return quest_id
        except Exception as e:
            logger.error(f"Error creating quest: {str(e)}")
            raise DatabaseError(f"Failed to create quest: {str(e)}")
    
    @staticmethod
    def update_quest(quest_id: str, quest_data: Dict[str, Any]) -> None:
        """
        Update an existing quest.
        
        Args:
            quest_id: ID of the quest to update
            quest_data: Updated quest data
            
        Raises:
            NotFoundError: If quest not found
            DatabaseError: If database operation fails
        """
        try:
            # Check if quest exists
            existing_quest = QuestRepository.get_quest(quest_id)
            if not existing_quest:
                raise NotFoundError(f"Quest {quest_id} not found")
            
            # Update timestamp
            quest_data["updated_at"] = datetime.utcnow().isoformat()
            
            # Update in database
            update_document(f"quests/{quest_id}", quest_data)
        except NotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error updating quest {quest_id}: {str(e)}")
            raise DatabaseError(f"Failed to update quest: {str(e)}")
    
    @staticmethod
    def delete_quest(quest_id: str) -> None:
        """
        Delete a quest.
        
        Args:
            quest_id: ID of the quest to delete
            
        Raises:
            NotFoundError: If quest not found
            DatabaseError: If database operation fails
        """
        try:
            # Check if quest exists
            existing_quest = QuestRepository.get_quest(quest_id)
            if not existing_quest:
                raise NotFoundError(f"Quest {quest_id} not found")
            
            # Delete from database
            delete_document(f"quests/{quest_id}")
        except NotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error deleting quest {quest_id}: {str(e)}")
            raise DatabaseError(f"Failed to delete quest: {str(e)}")
    
    @staticmethod
    def get_journal_entries(player_id: str) -> List[Dict[str, Any]]:
        """
        Get all journal entries for a player.
        
        Args:
            player_id: ID of the player
            
        Returns:
            List of journal entry dictionaries
            
        Raises:
            DatabaseError: If database operation fails
        """
        try:
            entries = get_collection(
                "journal_entries", 
                where=[("player_id", "==", player_id)],
                order_by=[("timestamp", "desc")]
            )
            return entries if entries else []
        except Exception as e:
            logger.error(f"Error getting journal entries for player {player_id}: {str(e)}")
            raise DatabaseError(f"Failed to get journal entries: {str(e)}")
    
    @staticmethod
    def create_journal_entry(entry_data: Dict[str, Any]) -> str:
        """
        Create a new journal entry.
        
        Args:
            entry_data: Journal entry data
            
        Returns:
            ID of the created journal entry
            
        Raises:
            DatabaseError: If database operation fails
        """
        try:
            # Generate ID
            entry_id = f"journal_{str(uuid.uuid4())}"
            
            # Add timestamp if not present
            if "timestamp" not in entry_data:
                entry_data["timestamp"] = datetime.utcnow().isoformat()
            
            # Store in database
            set_document(f"journal_entries/{entry_id}", entry_data)
            
            return entry_id
        except Exception as e:
            logger.error(f"Error creating journal entry: {str(e)}")
            raise DatabaseError(f"Failed to create journal entry: {str(e)}")
    
    @staticmethod
    def get_player_arc(player_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a player's story arc.
        
        Args:
            player_id: ID of the player
            
        Returns:
            Player arc dictionary or None if not found
            
        Raises:
            DatabaseError: If database operation fails
        """
        try:
            return get_document(f"player_arcs/{player_id}")
        except Exception as e:
            logger.error(f"Error getting arc for player {player_id}: {str(e)}")
            raise DatabaseError(f"Failed to get player arc: {str(e)}")
    
    @staticmethod
    def save_player_arc(player_id: str, arc_data: Dict[str, Any]) -> None:
        """
        Save a player's story arc.
        
        Args:
            player_id: ID of the player
            arc_data: Arc data to save
            
        Raises:
            DatabaseError: If database operation fails
        """
        try:
            # Add timestamp
            arc_data["updated_at"] = datetime.utcnow().isoformat()
            
            # Store in database
            set_document(f"player_arcs/{player_id}", arc_data)
        except Exception as e:
            logger.error(f"Error saving arc for player {player_id}: {str(e)}")
            raise DatabaseError(f"Failed to save player arc: {str(e)}") 
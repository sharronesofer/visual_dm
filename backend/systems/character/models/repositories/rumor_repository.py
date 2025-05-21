"""
Repository layer for the rumor system handling data persistence.
"""
from typing import List, Optional, Dict, Any
import os
import json
import logging
import asyncio
from datetime import datetime

from backend.systems.rumor.models.rumor import Rumor

logger = logging.getLogger(__name__)

class RumorRepository:
    """
    Repository for storing and retrieving rumors.
    Handles persistence of rumor data to disk.
    """
    
    def __init__(self, storage_path: str = "data/rumors/"):
        """
        Initialize the rumor repository.
        
        Args:
            storage_path: Directory for rumor storage
        """
        self.storage_path = storage_path
        self._rumor_cache = {}  # id -> Rumor
        os.makedirs(storage_path, exist_ok=True)
        
        logger.info(f"RumorRepository initialized with storage at {storage_path}")
    
    async def save_rumor(self, rumor: Rumor) -> None:
        """
        Save a rumor to persistent storage.
        
        Args:
            rumor: The rumor to save
        """
        # Update cache
        self._rumor_cache[rumor.id] = rumor
        
        # Serialize to file
        rumor_path = os.path.join(self.storage_path, f"{rumor.id}.json")
        
        # Ensure the rumor dir exists
        os.makedirs(os.path.dirname(rumor_path), exist_ok=True)
        
        # Convert to dictionary, handling datetime objects
        rumor_dict = rumor.model_dump(mode='json')
        
        # Write to file
        async with asyncio.Lock():
            with open(rumor_path, 'w') as f:
                json.dump(rumor_dict, f, indent=2)
        
        logger.debug(f"Saved rumor {rumor.id} to {rumor_path}")
    
    async def get_rumor(self, rumor_id: str) -> Optional[Rumor]:
        """
        Retrieve a rumor by ID.
        
        Args:
            rumor_id: ID of the rumor to retrieve
            
        Returns:
            The rumor if found, None otherwise
        """
        # Check cache first
        if rumor_id in self._rumor_cache:
            return self._rumor_cache[rumor_id]
        
        # Try to load from file
        rumor_path = os.path.join(self.storage_path, f"{rumor_id}.json")
        if not os.path.exists(rumor_path):
            logger.warning(f"Rumor {rumor_id} not found at {rumor_path}")
            return None
        
        try:
            with open(rumor_path, 'r') as f:
                rumor_dict = json.load(f)
            
            # Convert to Rumor object
            rumor = Rumor.model_validate(rumor_dict)
            
            # Update cache
            self._rumor_cache[rumor_id] = rumor
            
            return rumor
        except Exception as e:
            logger.error(f"Error loading rumor {rumor_id}: {e}")
            return None
    
    async def get_all_rumors(self) -> List[Rumor]:
        """
        Retrieve all rumors from storage.
        
        Returns:
            List of all rumors
        """
        rumors = []
        
        # List all json files in storage directory
        if not os.path.exists(self.storage_path):
            return []
            
        for filename in os.listdir(self.storage_path):
            if filename.endswith('.json'):
                rumor_id = filename[:-5]  # Remove .json extension
                rumor = await self.get_rumor(rumor_id)
                if rumor:
                    rumors.append(rumor)
        
        return rumors
    
    async def delete_rumor(self, rumor_id: str) -> bool:
        """
        Delete a rumor from storage.
        
        Args:
            rumor_id: ID of the rumor to delete
            
        Returns:
            True if deleted, False if not found
        """
        # Remove from cache
        if rumor_id in self._rumor_cache:
            del self._rumor_cache[rumor_id]
        
        # Remove from disk
        rumor_path = os.path.join(self.storage_path, f"{rumor_id}.json")
        if not os.path.exists(rumor_path):
            return False
        
        try:
            os.remove(rumor_path)
            logger.info(f"Deleted rumor {rumor_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting rumor {rumor_id}: {e}")
            return False 

"""
Region system repository layer.

This module contains the repository layer for the region system.
"""

from typing import Dict, List, Optional, Any, Union
import uuid
import json
from pathlib import Path
import os
from datetime import datetime
import logging

from backend.core.config import Settings
from backend.core.db.base_repository import BaseRepository

logger = logging.getLogger(__name__)

class RegionRepository(BaseRepository):
    """Repository for the region system."""
    
    def __init__(self, data_dir: Optional[str] = None):
        """
        Initialize the repository.
        
        Args:
            data_dir: Directory where region data is stored
        """
        super().__init__()
        self.data_dir = data_dir or os.path.join(
            Settings().data_dir, "regions"
        )
        self.maps_dir = os.path.join(
            Settings().data_dir, "region_maps"
        )
        self.questlogs_dir = os.path.join(
            Settings().data_dir, "questlogs"
        )
        
        # Ensure directories exist
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.maps_dir, exist_ok=True)
        os.makedirs(self.questlogs_dir, exist_ok=True)
    
    def get_region_by_id(self, region_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a region by ID.
        
        Args:
            region_id: The ID of the region to get
            
        Returns:
            The region, or None if not found
        """
        try:
            region_path = os.path.join(self.data_dir, f"{region_id}.json")
            if not os.path.exists(region_path):
                return None
                
            with open(region_path, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error getting region {region_id}: {str(e)}")
            return None
    
    def list_all_regions(self) -> List[Dict[str, Any]]:
        """
        List all regions.
        
        Returns:
            List of all regions
        """
        regions = []
        try:
            for file_name in os.listdir(self.data_dir):
                if file_name.endswith(".json"):
                    with open(os.path.join(self.data_dir, file_name), "r") as f:
                        region = json.load(f)
                        regions.append(region)
            return regions
        except Exception as e:
            logger.error(f"Error listing regions: {str(e)}")
            return []
    
    def get_regions_by_continent(self, continent_id: str) -> List[Dict[str, Any]]:
        """
        Get all regions in a continent.
        
        Args:
            continent_id: The ID of the continent
            
        Returns:
            List of regions in the continent
        """
        regions = []
        try:
            for file_name in os.listdir(self.data_dir):
                if file_name.endswith(".json"):
                    with open(os.path.join(self.data_dir, file_name), "r") as f:
                        region = json.load(f)
                        if region.get("continent_id") == continent_id:
                            regions.append(region)
            return regions
        except Exception as e:
            logger.error(f"Error listing regions by continent: {str(e)}")
            return []
    
    def create_region(self, region_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new region.
        
        Args:
            region_data: The data for the new region
            
        Returns:
            The created region
        """
        try:
            # Ensure region has an ID
            if "id" not in region_data:
                region_data["id"] = f"r_{uuid.uuid4().hex[:8]}"
            
            # Add timestamps if not present
            if "created_at" not in region_data:
                region_data["created_at"] = datetime.utcnow().isoformat()
            if "last_updated" not in region_data:
                region_data["last_updated"] = datetime.utcnow().isoformat()
            
            # Save the region
            region_path = os.path.join(self.data_dir, f"{region_data['id']}.json")
            with open(region_path, "w") as f:
                json.dump(region_data, f, indent=2)
                
            return region_data
        except Exception as e:
            logger.error(f"Error creating region: {str(e)}")
            raise
    
    def update_region(self, region_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update a region.
        
        Args:
            region_id: The ID of the region to update
            data: The updated region data
            
        Returns:
            The updated region, or None if not found
        """
        try:
            # Get existing region
            existing_region = self.get_region_by_id(region_id)
            if not existing_region:
                return None
            
            # Update region data
            updated_region = {**existing_region, **data}
            updated_region["last_updated"] = datetime.utcnow().isoformat()
            
            # Save the updated region
            region_path = os.path.join(self.data_dir, f"{region_id}.json")
            with open(region_path, "w") as f:
                json.dump(updated_region, f, indent=2)
                
            return updated_region
        except Exception as e:
            logger.error(f"Error updating region {region_id}: {str(e)}")
            return None
    
    def delete_region(self, region_id: str) -> bool:
        """
        Delete a region.
        
        Args:
            region_id: The ID of the region to delete
            
        Returns:
            True if the region was deleted, False if not found
        """
        try:
            region_path = os.path.join(self.data_dir, f"{region_id}.json")
            if not os.path.exists(region_path):
                return False
                
            os.remove(region_path)
            
            # Also delete region map if it exists
            map_dir = os.path.join(self.maps_dir, region_id)
            if os.path.exists(map_dir) and os.path.isdir(map_dir):
                import shutil
                shutil.rmtree(map_dir)
                
            return True
        except Exception as e:
            logger.error(f"Error deleting region {region_id}: {str(e)}")
            return False
    
    def get_region_map_tiles(self, region_id: str) -> Dict[str, Any]:
        """
        Get the tiles for a region map.
        
        Args:
            region_id: The ID of the region
            
        Returns:
            A dictionary of tiles keyed by coordinate string
            
        Raises:
            Exception: If there is an error fetching the map
        """
        try:
            tiles_path = os.path.join(self.maps_dir, region_id, "tiles.json")
            if not os.path.exists(tiles_path):
                return {}
                
            with open(tiles_path, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error getting region map tiles for {region_id}: {str(e)}")
            return {}
    
    def save_region_map_tiles(self, region_id: str, tiles: Dict[str, Any]) -> bool:
        """
        Save tiles for a region map.
        
        Args:
            region_id: The ID of the region
            tiles: A dictionary of tiles keyed by coordinate string
            
        Returns:
            True if the tiles were saved successfully
            
        Raises:
            Exception: If there is an error saving the map
        """
        try:
            # Ensure the region map directory exists
            region_map_dir = os.path.join(self.maps_dir, region_id)
            os.makedirs(region_map_dir, exist_ok=True)
            
            # Save the tiles
            tiles_path = os.path.join(region_map_dir, "tiles.json")
            with open(tiles_path, "w") as f:
                json.dump(tiles, f, indent=2)
                
            return True
        except Exception as e:
            logger.error(f"Error saving region map tiles for {region_id}: {str(e)}")
            raise
    
    def get_character_questlog(self, character_id: str) -> List[Dict[str, Any]]:
        """
        Get a character's questlog.
        
        Args:
            character_id: The ID of the character
            
        Returns:
            The character's questlog
        """
        try:
            questlog_path = os.path.join(self.questlogs_dir, f"{character_id}.json")
            if not os.path.exists(questlog_path):
                return []
                
            with open(questlog_path, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error getting questlog for character {character_id}: {str(e)}")
            return []
    
    def add_quest_to_character(self, character_id: str, quest_entry: Dict[str, Any]) -> bool:
        """
        Add a quest to a character's questlog.
        
        Args:
            character_id: The ID of the character
            quest_entry: The quest to add
            
        Returns:
            True if the quest was added successfully
        """
        try:
            # Get existing questlog
            questlog = self.get_character_questlog(character_id)
            
            # Add timestamp if not present
            if "timestamp" not in quest_entry:
                quest_entry["timestamp"] = datetime.utcnow().isoformat()
                
            # Add the new quest
            questlog.append(quest_entry)
            
            # Save the updated questlog
            questlog_path = os.path.join(self.questlogs_dir, f"{character_id}.json")
            with open(questlog_path, "w") as f:
                json.dump(questlog, f, indent=2)
                
            return True
        except Exception as e:
            logger.error(f"Error adding quest for character {character_id}: {str(e)}")
            return False 
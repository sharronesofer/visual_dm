"""
Data access repositories for factions and faction relationships.

This module provides repository classes for faction data persistence.
"""

import json
from typing import List, Dict, Optional, Any, Union
from pathlib import Path
from datetime import datetime

from backend.systems.faction.models.faction import Faction, FactionRelationship, FactionMembership
from backend.systems.faction.schemas.faction_types import FactionType, FactionAlignment, DiplomaticStance

class FactionRepository:
    """Repository for faction data persistence."""
    
    def __init__(self, data_dir: str = "data/factions"):
        """
        Initialize the faction repository.
        
        Args:
            data_dir: Directory path for faction data files
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.factions_file = self.data_dir / "factions.json"
        self._ensure_files_exist()
        
    def _ensure_files_exist(self):
        """Ensure necessary data files exist, creating them if needed."""
        if not self.factions_file.exists():
            with open(self.factions_file, 'w') as f:
                json.dump({"factions": [], "version": 1}, f)
    
    def get_all_factions(self) -> List[Dict[str, Any]]:
        """
        Get all factions.
        
        Returns:
            List of faction data dictionaries
        """
        with open(self.factions_file, 'r') as f:
            data = json.load(f)
            return data.get("factions", [])
    
    def get_faction_by_id(self, faction_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a faction by ID.
        
        Args:
            faction_id: ID of the faction to retrieve
            
        Returns:
            Faction data dictionary or None if not found
        """
        factions = self.get_all_factions()
        for faction in factions:
            if faction.get("id") == faction_id:
                return faction
        return None
    
    def get_faction_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get a faction by name.
        
        Args:
            name: Name of the faction to retrieve
            
        Returns:
            Faction data dictionary or None if not found
        """
        factions = self.get_all_factions()
        for faction in factions:
            if faction.get("name") == name:
                return faction
        return None
    
    def create_faction(self, faction_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new faction.
        
        Args:
            faction_data: Faction data to save
            
        Returns:
            Created faction data with generated ID
            
        Raises:
            ValueError: If faction with same name already exists
        """
        if self.get_faction_by_name(faction_data.get("name")):
            raise ValueError(f"Faction with name '{faction_data.get('name')}' already exists")
            
        # Read existing data
        with open(self.factions_file, 'r') as f:
            data = json.load(f)
            
        # Generate ID if not provided
        if "id" not in faction_data:
            faction_data["id"] = self._generate_faction_id()
            
        # Set timestamps
        now = datetime.utcnow().isoformat()
        faction_data["created_at"] = now
        faction_data["updated_at"] = now
        
        # Set default values if not provided
        if "is_active" not in faction_data:
            faction_data["is_active"] = True
            
        # Add to list and save
        data["factions"].append(faction_data)
        
        with open(self.factions_file, 'w') as f:
            json.dump(data, f, indent=2)
            
        return faction_data
    
    def update_faction(self, faction_id: str, faction_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update an existing faction.
        
        Args:
            faction_id: ID of faction to update
            faction_data: New faction data
            
        Returns:
            Updated faction data or None if not found
            
        Raises:
            ValueError: If updating name to one that already exists
        """
        with open(self.factions_file, 'r') as f:
            data = json.load(f)
            
        found = False
        
        # Check if updating to an existing name
        if "name" in faction_data:
            existing = self.get_faction_by_name(faction_data["name"])
            if existing and existing.get("id") != faction_id:
                raise ValueError(f"Faction with name '{faction_data['name']}' already exists")
            
        # Update faction
        for i, faction in enumerate(data["factions"]):
            if faction.get("id") == faction_id:
                # Update fields
                for key, value in faction_data.items():
                    faction[key] = value
                
                # Update timestamp
                faction["updated_at"] = datetime.utcnow().isoformat()
                
                # Save
                with open(self.factions_file, 'w') as f:
                    json.dump(data, f, indent=2)
                    
                found = True
                return faction
                
        return None if not found else faction
    
    def delete_faction(self, faction_id: str) -> bool:
        """
        Delete a faction.
        
        Args:
            faction_id: ID of faction to delete
            
        Returns:
            True if faction was deleted, False if not found
        """
        with open(self.factions_file, 'r') as f:
            data = json.load(f)
            
        initial_count = len(data["factions"])
        data["factions"] = [f for f in data["factions"] if f.get("id") != faction_id]
        
        if len(data["factions"]) < initial_count:
            with open(self.factions_file, 'w') as f:
                json.dump(data, f, indent=2)
            return True
            
        return False
        
    def _generate_faction_id(self) -> str:
        """
        Generate a unique faction ID.
        
        Returns:
            New unique faction ID
        """
        factions = self.get_all_factions()
        existing_ids = set(f.get("id") for f in factions if "id" in f)
        
        # Start with fac_1, fac_2, etc.
        i = 1
        while f"fac_{i}" in existing_ids:
            i += 1
            
        return f"fac_{i}"

class FactionRelationshipRepository:
    """Repository for faction relationship data persistence."""
    
    def __init__(self, data_dir: str = "data/factions"):
        """
        Initialize the faction relationship repository.
        
        Args:
            data_dir: Directory path for faction data files
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.relationships_file = self.data_dir / "faction_relationships.json"
        self._ensure_files_exist()
        
    def _ensure_files_exist(self):
        """Ensure necessary data files exist, creating them if needed."""
        if not self.relationships_file.exists():
            with open(self.relationships_file, 'w') as f:
                json.dump({"relationships": [], "version": 1}, f)
    
    def get_all_relationships(self) -> List[Dict[str, Any]]:
        """
        Get all faction relationships.
        
        Returns:
            List of relationship data dictionaries
        """
        with open(self.relationships_file, 'r') as f:
            data = json.load(f)
            return data.get("relationships", [])
    
    def get_relationship(self, faction_id: str, other_faction_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a relationship between two factions.
        
        Args:
            faction_id: ID of the first faction
            other_faction_id: ID of the second faction
            
        Returns:
            Relationship data dictionary or None if not found
        """
        relationships = self.get_all_relationships()
        for rel in relationships:
            if rel.get("faction_id") == faction_id and rel.get("other_faction_id") == other_faction_id:
                return rel
        return None
    
    def get_faction_relationships(self, faction_id: str) -> List[Dict[str, Any]]:
        """
        Get all relationships for a faction.
        
        Args:
            faction_id: ID of the faction
            
        Returns:
            List of relationship data dictionaries
        """
        relationships = self.get_all_relationships()
        return [rel for rel in relationships if rel.get("faction_id") == faction_id]
    
    def create_or_update_relationship(self, relationship_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create or update a faction relationship.
        
        Args:
            relationship_data: Relationship data to save
            
        Returns:
            Created/updated relationship data
            
        Raises:
            ValueError: If required fields are missing
        """
        if "faction_id" not in relationship_data or "other_faction_id" not in relationship_data:
            raise ValueError("faction_id and other_faction_id are required fields")
            
        faction_id = relationship_data["faction_id"]
        other_faction_id = relationship_data["other_faction_id"]
        
        # Read existing data
        with open(self.relationships_file, 'r') as f:
            data = json.load(f)
            
        # Set timestamps
        now = datetime.utcnow().isoformat()
        relationship_data["updated_at"] = now
        
        # Check if relationship already exists
        existing_idx = None
        for i, rel in enumerate(data["relationships"]):
            if rel.get("faction_id") == faction_id and rel.get("other_faction_id") == other_faction_id:
                existing_idx = i
                break
                
        if existing_idx is not None:
            # Update existing relationship
            if "created_at" not in relationship_data and "created_at" in data["relationships"][existing_idx]:
                relationship_data["created_at"] = data["relationships"][existing_idx]["created_at"]
            else:
                relationship_data["created_at"] = now
                
            data["relationships"][existing_idx] = relationship_data
        else:
            # Create new relationship
            relationship_data["created_at"] = now
            data["relationships"].append(relationship_data)
            
        # Save
        with open(self.relationships_file, 'w') as f:
            json.dump(data, f, indent=2)
            
        return relationship_data
    
    def delete_relationship(self, faction_id: str, other_faction_id: str) -> bool:
        """
        Delete a faction relationship.
        
        Args:
            faction_id: ID of the first faction
            other_faction_id: ID of the second faction
            
        Returns:
            True if relationship was deleted, False if not found
        """
        with open(self.relationships_file, 'r') as f:
            data = json.load(f)
            
        initial_count = len(data["relationships"])
        
        data["relationships"] = [
            rel for rel in data["relationships"] 
            if not (rel.get("faction_id") == faction_id and rel.get("other_faction_id") == other_faction_id)
        ]
        
        if len(data["relationships"]) < initial_count:
            with open(self.relationships_file, 'w') as f:
                json.dump(data, f, indent=2)
            return True
            
        return False
    
    def delete_all_faction_relationships(self, faction_id: str) -> int:
        """
        Delete all relationships involving a faction.
        
        Args:
            faction_id: ID of the faction
            
        Returns:
            Number of relationships deleted
        """
        with open(self.relationships_file, 'r') as f:
            data = json.load(f)
            
        initial_count = len(data["relationships"])
        
        data["relationships"] = [
            rel for rel in data["relationships"] 
            if rel.get("faction_id") != faction_id and rel.get("other_faction_id") != faction_id
        ]
        
        deleted_count = initial_count - len(data["relationships"])
        
        if deleted_count > 0:
            with open(self.relationships_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        return deleted_count 
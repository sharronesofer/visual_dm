"""
Repository for continent data persistence.

This module provides data access layer for continent-related operations.
"""
from typing import Dict, Optional, List
from uuid import uuid4

from backend.systems.world_generation.models import ContinentSchema

class ContinentRepository:
    """
    Repository for continent data persistence.
    Currently uses in-memory storage, but could be extended to use a database.
    """
    _continents: Dict[str, ContinentSchema] = {}

    def create_continent(self, continent_schema: ContinentSchema) -> ContinentSchema:
        """
        Creates a new continent in the repository.
        
        Args:
            continent_schema: The continent to create
            
        Returns:
            The created continent with assigned ID
        """
        # Assumes continent_id is already set in the schema by the service
        if not continent_schema.continent_id:
            continent_schema.continent_id = str(uuid4())  # Fallback, but service should handle this
        
        self._continents[continent_schema.continent_id] = continent_schema
        return continent_schema

    def get_continent_by_id(self, continent_id: str) -> Optional[ContinentSchema]:
        """
        Retrieves a continent by its ID.
        
        Args:
            continent_id: The ID of the continent to retrieve
            
        Returns:
            The continent if found, None otherwise
        """
        return self._continents.get(continent_id)

    def list_all_continents(self) -> List[ContinentSchema]:
        """
        Lists all continents in the repository.
        
        Returns:
            List of all continents
        """
        return list(self._continents.values())
    
    def update_continent(self, continent_id: str, continent_data: ContinentSchema) -> Optional[ContinentSchema]:
        """
        Updates an existing continent.
        
        Args:
            continent_id: The ID of the continent to update
            continent_data: The new continent data
            
        Returns:
            The updated continent if found, None otherwise
        """
        if continent_id in self._continents:
            if continent_data.continent_id != continent_id:
                # Ensure IDs match
                continent_data.continent_id = continent_id
            self._continents[continent_id] = continent_data
            return continent_data
        return None
    
    def delete_continent(self, continent_id: str) -> bool:
        """
        Deletes a continent from the repository.
        
        Args:
            continent_id: The ID of the continent to delete
            
        Returns:
            True if the continent was deleted, False otherwise
        """
        if continent_id in self._continents:
            del self._continents[continent_id]
            return True
        return False

# Singleton instance
continent_repository = ContinentRepository() 
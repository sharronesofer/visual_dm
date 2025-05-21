"""
World State system integration for the dialogue system.

This module provides functionality for connecting dialogue with the World State system,
allowing dialogue to reference and be influenced by the current state of the world.
"""

from typing import Dict, Any, List, Optional, Set
import logging
from datetime import datetime

# Import world state system components
from backend.systems.world.world_state_manager import WorldStateManager

# Configure logger
logger = logging.getLogger(__name__)


class DialogueWorldStateIntegration:
    """
    Integration between dialogue and world state systems.
    
    Allows dialogue to reference, be influenced by, and potentially update
    the current state of the world and its variables.
    """
    
    def __init__(self, world_state_manager=None):
        """
        Initialize the dialogue world state integration.
        
        Args:
            world_state_manager: Optional world state manager instance
        """
        self.world_state_manager = world_state_manager or WorldStateManager.get_instance()
    
    def add_world_state_to_context(
        self,
        context: Dict[str, Any],
        region_id: Optional[str] = None,
        categories: Optional[List[str]] = None,
        max_vars: int = 10
    ) -> Dict[str, Any]:
        """
        Add relevant world state variables to dialogue context.
        
        Args:
            context: The existing dialogue context
            region_id: Optional ID of the region to get state for
            categories: Optional list of state variable categories to include
            max_vars: Maximum number of state variables to add
            
        Returns:
            Updated context with world state information added
        """
        # Create a copy of the context
        updated_context = dict(context)
        
        # Get relevant world state variables
        state_vars = self._get_relevant_state_variables(region_id, categories, max_vars)
        
        if state_vars:
            # Add the state variables to the context
            if "world_state" not in updated_context:
                updated_context["world_state"] = {}
                
            for category, vars_by_category in state_vars.items():
                if category not in updated_context["world_state"]:
                    updated_context["world_state"][category] = {}
                    
                for key, value in vars_by_category.items():
                    updated_context["world_state"][category][key] = value
            
            logger.debug(f"Added world state variables to context")
        
        return updated_context
    
    def get_state_variable_for_dialogue(
        self,
        variable_key: str,
        region_id: Optional[str] = None,
        default_value: Any = None
    ) -> Any:
        """
        Get a specific world state variable for use in dialogue.
        
        Args:
            variable_key: Key of the state variable to retrieve
            region_id: Optional ID of the region to get state for
            default_value: Default value to return if variable doesn't exist
            
        Returns:
            Value of the state variable
        """
        try:
            # Get the state variable
            value = self.world_state_manager.get_state(
                key=variable_key,
                region=region_id
            )
            
            return value if value is not None else default_value
            
        except Exception as e:
            logger.error(f"Error getting world state variable '{variable_key}': {e}")
            return default_value
    
    def get_state_history_for_dialogue(
        self,
        variable_key: str,
        region_id: Optional[str] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Get historical values of a world state variable for use in dialogue.
        
        Args:
            variable_key: Key of the state variable to retrieve history for
            region_id: Optional ID of the region to get state for
            limit: Maximum number of historical entries to retrieve
            
        Returns:
            List of historical state variable entries
        """
        try:
            # Get the state variable history
            history = self.world_state_manager.get_history(
                key=variable_key,
                region=region_id,
                limit=limit
            )
            
            # Format for dialogue context
            formatted_history = []
            for entry in history:
                formatted_entry = {
                    "value": entry.get("value"),
                    "timestamp": entry.get("timestamp"),
                    "version": entry.get("version")
                }
                formatted_history.append(formatted_entry)
            
            return formatted_history
            
        except Exception as e:
            logger.error(f"Error getting world state history for '{variable_key}': {e}")
            return []
    
    def update_world_state_from_dialogue(
        self,
        variable_key: str,
        new_value: Any,
        region_id: Optional[str] = None,
        category: Optional[str] = None,
        source: str = "dialogue"
    ) -> bool:
        """
        Update a world state variable based on dialogue context.
        
        Args:
            variable_key: Key of the state variable to update
            new_value: New value to set
            region_id: Optional ID of the region to set state for
            category: Optional category for the state variable
            source: Source of the update (default: 'dialogue')
            
        Returns:
            True if update was successful, False otherwise
        """
        try:
            # Update the state variable
            self.world_state_manager.set_state(
                key=variable_key,
                value=new_value,
                region=region_id,
                category=category,
                metadata={"source": source, "timestamp": datetime.utcnow().isoformat()}
            )
            
            logger.debug(f"Updated world state variable '{variable_key}' to '{new_value}'")
            return True
            
        except Exception as e:
            logger.error(f"Error updating world state variable '{variable_key}': {e}")
            return False
    
    def _get_relevant_state_variables(
        self,
        region_id: Optional[str] = None,
        categories: Optional[List[str]] = None,
        max_vars: int = 10
    ) -> Dict[str, Dict[str, Any]]:
        """
        Get relevant world state variables for dialogue context.
        
        Args:
            region_id: Optional ID of the region to get state for
            categories: Optional list of state variable categories to include
            max_vars: Maximum number of state variables to add
            
        Returns:
            Dictionary of relevant state variables by category
        """
        result = {}
        
        try:
            # Get state variables
            query = {
                "region": region_id,
                "categories": categories,
                "limit": max_vars
            }
            
            # In a real implementation, this would use more sophisticated relevance matching
            state_vars = self.world_state_manager.query_state(query)
            
            # Organize by category
            for var in state_vars:
                category = var.get("category", "general")
                
                if category not in result:
                    result[category] = {}
                    
                key = var.get("key")
                value = var.get("value")
                
                if key:
                    result[category][key] = value
                    
            return result
            
        except Exception as e:
            logger.error(f"Error getting relevant world state variables: {e}")
            return result 
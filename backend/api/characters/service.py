"""
Character Service

This module provides the service layer for character resources.
"""

from typing import Dict, List, Optional, Any, Union
from fastapi import HTTPException
import logging
import uuid
from datetime import datetime
from .schemas import Character, CharacterCreate, CharacterUpdate

# Configure logger
logger = logging.getLogger(__name__)

# Mock database for demonstration
# In a real application, this would use a proper database
_characters_db: Dict[str, Dict[str, Any]] = {}


class CharacterService:
    """Service for character-related operations"""
    
    async def get_all(
        self,
        offset: int = 0,
        limit: int = 20,
        cursor: Optional[str] = None,
        search_query: Optional[str] = None,
        sort_field: Optional[str] = None,
        sort_order: str = "asc",
        fields: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
        user_id: Optional[str] = None,
        campaign_id: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Get all characters with filtering and pagination
        
        Args:
            offset: Number of records to skip
            limit: Maximum number of records to return
            cursor: Cursor for pagination
            search_query: Text search query
            sort_field: Field to sort by
            sort_order: Sort order ('asc' or 'desc')
            fields: Fields to include in the response
            expand: Related entities to expand
            user_id: Filter by user ID
            campaign_id: Filter by campaign ID
            
        Returns:
            Dictionary with items and total count
        """
        try:
            # Start with all characters
            characters = list(_characters_db.values())
            
            # Apply filters
            if search_query:
                characters = [
                    c for c in characters 
                    if search_query.lower() in c.get("name", "").lower()
                ]
                
            if user_id:
                characters = [c for c in characters if c.get("user_id") == user_id]
                
            if campaign_id:
                characters = [c for c in characters if c.get("campaign_id") == campaign_id]
            
            # Get total count before pagination
            total = len(characters)
            
            # Apply sorting
            if sort_field:
                characters.sort(
                    key=lambda x: x.get(sort_field, ""),
                    reverse=(sort_order.lower() == "desc")
                )
            
            # Apply pagination
            characters = characters[offset:offset + limit]
            
            # Convert to Character models
            character_models = [Character(**c) for c in characters]
            
            return {
                "items": character_models,
                "total": total
            }
            
        except Exception as e:
            logger.exception(f"Error getting characters: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error getting characters: {str(e)}")
    
    async def get_by_id(
        self,
        id: str,
        fields: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
        **kwargs
    ) -> Optional[Character]:
        """
        Get a character by ID
        
        Args:
            id: Character ID
            fields: Fields to include in the response
            expand: Related entities to expand
            
        Returns:
            Character object or None if not found
        """
        try:
            character_data = _characters_db.get(id)
            
            if not character_data:
                return None
                
            return Character(**character_data)
            
        except Exception as e:
            logger.exception(f"Error getting character {id}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error getting character: {str(e)}")
    
    async def create(
        self,
        data: CharacterCreate,
        **kwargs
    ) -> Character:
        """
        Create a new character
        
        Args:
            data: Character creation data
            
        Returns:
            Created character
        """
        try:
            # Generate ID and timestamps
            character_id = str(uuid.uuid4())
            now = datetime.utcnow()
            
            # Create the character
            character_data = {
                "id": character_id,
                "created_at": now,
                "updated_at": now,
                **data.dict(exclude_unset=True),
            }
            
            # If user_id is not provided, use the current user ID from kwargs
            if not character_data.get("user_id") and "current_user_id" in kwargs:
                character_data["user_id"] = kwargs["current_user_id"]
                
            # Validate that user_id is provided
            if not character_data.get("user_id"):
                raise HTTPException(
                    status_code=400,
                    detail="User ID is required but not provided"
                )
            
            # Store in our mock database
            _characters_db[character_id] = character_data
            
            # Return as a Character model
            return Character(**character_data)
            
        except HTTPException:
            raise
        except Exception as e:
            logger.exception(f"Error creating character: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error creating character: {str(e)}")
    
    async def update(
        self,
        id: str,
        data: CharacterUpdate,
        **kwargs
    ) -> Optional[Character]:
        """
        Update a character
        
        Args:
            id: Character ID
            data: Character update data
            
        Returns:
            Updated character or None if not found
        """
        try:
            # Check if character exists
            character_data = _characters_db.get(id)
            if not character_data:
                return None
                
            # Check ownership if current_user_id is provided
            if "current_user_id" in kwargs and character_data.get("user_id") != kwargs["current_user_id"]:
                raise HTTPException(
                    status_code=403,
                    detail="You don't have permission to update this character"
                )
                
            # Update the character data
            update_data = data.dict(exclude_unset=True)
            character_data.update(update_data)
            
            # Update the timestamp
            character_data["updated_at"] = datetime.utcnow()
            
            # Save back to our mock database
            _characters_db[id] = character_data
            
            # Return as a Character model
            return Character(**character_data)
            
        except HTTPException:
            raise
        except Exception as e:
            logger.exception(f"Error updating character {id}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error updating character: {str(e)}")
    
    async def patch(
        self,
        id: str,
        data: Dict[str, Any],
        **kwargs
    ) -> Optional[Character]:
        """
        Partially update a character
        
        Args:
            id: Character ID
            data: Dictionary of fields to update
            
        Returns:
            Updated character or None if not found
        """
        try:
            # Check if character exists
            character_data = _characters_db.get(id)
            if not character_data:
                return None
                
            # Check ownership if current_user_id is provided
            if "current_user_id" in kwargs and character_data.get("user_id") != kwargs["current_user_id"]:
                raise HTTPException(
                    status_code=403,
                    detail="You don't have permission to update this character"
                )
                
            # Update only the provided fields
            for key, value in data.items():
                if key in character_data:
                    character_data[key] = value
            
            # Update the timestamp
            character_data["updated_at"] = datetime.utcnow()
            
            # Save back to our mock database
            _characters_db[id] = character_data
            
            # Return as a Character model
            return Character(**character_data)
            
        except HTTPException:
            raise
        except Exception as e:
            logger.exception(f"Error patching character {id}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error patching character: {str(e)}")
    
    async def delete(
        self,
        id: str,
        **kwargs
    ) -> bool:
        """
        Delete a character
        
        Args:
            id: Character ID
            
        Returns:
            True if deleted, False if not found
        """
        try:
            # Check if character exists
            character_data = _characters_db.get(id)
            if not character_data:
                return False
                
            # Check ownership if current_user_id is provided
            if "current_user_id" in kwargs and character_data.get("user_id") != kwargs["current_user_id"]:
                raise HTTPException(
                    status_code=403,
                    detail="You don't have permission to delete this character"
                )
                
            # Remove from our mock database
            del _characters_db[id]
            
            return True
            
        except HTTPException:
            raise
        except Exception as e:
            logger.exception(f"Error deleting character {id}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error deleting character: {str(e)}")

# Create a singleton instance
character_service = CharacterService() 
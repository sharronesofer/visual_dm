"""
Character Routes

This module defines the API routes for character resources.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body, status
from typing import Optional, List, Dict

from ..core.base_router import create_api_router, PaginationParams, FilterParams
from ..core.base_router import create_resource_router
from ..core.dependencies import verify_token, get_current_user_id
from ..models.base import APIResponse, PaginatedList
from .schemas import Character, CharacterCreate, CharacterUpdate
from .service import character_service

# Create router with authentication
router = create_api_router(
    prefix="/characters",
    tags=["Characters"],
)

# Add standard CRUD endpoints with proper authentication
character_router = create_resource_router(
    router=router,
    prefix="/characters",
    resource_name="character",
    service=character_service,
    response_model=Character,
    create_model=CharacterCreate,
    update_model=CharacterUpdate,
)

# Add custom routes beyond the standard CRUD

@router.get(
    "/characters/me",
    response_model=APIResponse[PaginatedList[Character]],
    operation_id="get_my_characters",
    summary="Get Current User's Characters",
    description="Retrieve all characters belonging to the currently authenticated user."
)
async def get_my_characters(
    pagination: PaginationParams = Depends(),
    filters: FilterParams = Depends(),
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Get characters for the current authenticated user
    
    This endpoint retrieves all characters owned by the currently
    authenticated user with pagination and optional filtering.
    
    Args:
        pagination: Pagination parameters
        filters: Filtering and sorting parameters
        current_user_id: ID of the current user (from auth token)
        
    Returns:
        Paginated list of characters belonging to the current user
    """
    # Calculate offset
    offset = (pagination.page - 1) * pagination.page_size
    
    # Call service with current user ID filter
    result = await character_service.get_all(
        offset=offset,
        limit=pagination.page_size,
        user_id=current_user_id,
        search_query=filters.q,
        sort_field=filters.sort_field,
        sort_order=filters.sort_order,
        fields=filters.fields,
        expand=filters.expand
    )
    
    # Create pagination metadata
    next_page = None
    prev_page = None
    if pagination.page * pagination.page_size < result.get("total", 0):
        next_page = f"/api/v1/characters/me?page={pagination.page + 1}&page_size={pagination.page_size}"
    if pagination.page > 1:
        prev_page = f"/api/v1/characters/me?page={pagination.page - 1}&page_size={pagination.page_size}"
    
    # Construct response
    pagination_data = {
        "items": result.get("items", []),
        "total": result.get("total", 0),
        "page": pagination.page,
        "page_size": pagination.page_size,
        "next_page": next_page,
        "prev_page": prev_page
    }
    
    return {"data": pagination_data, "meta": {}}


@router.get(
    "/characters/campaign/{campaign_id}",
    response_model=APIResponse[PaginatedList[Character]],
    operation_id="get_campaign_characters",
    summary="Get Characters in a Campaign",
    description="Retrieve all characters associated with a specific campaign."
)
async def get_campaign_characters(
    campaign_id: str = Path(..., description="Campaign ID"),
    pagination: PaginationParams = Depends(),
    filters: FilterParams = Depends(),
    _: Dict = Depends(verify_token)  # Ensure authentication but discard result
):
    """
    Get all characters for a specific campaign
    
    This endpoint retrieves all characters associated with a specific
    campaign with pagination and optional filtering.
    
    Args:
        campaign_id: ID of the campaign
        pagination: Pagination parameters
        filters: Filtering and sorting parameters
        
    Returns:
        Paginated list of characters in the specified campaign
    """
    # Calculate offset
    offset = (pagination.page - 1) * pagination.page_size
    
    # Call service with campaign filter
    result = await character_service.get_all(
        offset=offset,
        limit=pagination.page_size,
        campaign_id=campaign_id,
        search_query=filters.q,
        sort_field=filters.sort_field,
        sort_order=filters.sort_order,
        fields=filters.fields,
        expand=filters.expand
    )
    
    # Create pagination metadata
    next_page = None
    prev_page = None
    if pagination.page * pagination.page_size < result.get("total", 0):
        next_page = f"/api/v1/characters/campaign/{campaign_id}?page={pagination.page + 1}&page_size={pagination.page_size}"
    if pagination.page > 1:
        prev_page = f"/api/v1/characters/campaign/{campaign_id}?page={pagination.page - 1}&page_size={pagination.page_size}"
    
    # Construct response
    pagination_data = {
        "items": result.get("items", []),
        "total": result.get("total", 0),
        "page": pagination.page,
        "page_size": pagination.page_size,
        "next_page": next_page,
        "prev_page": prev_page
    }
    
    return {"data": pagination_data, "meta": {}}


@router.post(
    "/characters/{character_id}/level-up",
    response_model=APIResponse[Character],
    operation_id="level_up_character",
    summary="Level Up Character",
    description="Increase a character's level in a specified class."
)
async def level_up_character(
    character_id: str = Path(..., description="Character ID"),
    class_name: str = Body(..., description="The class to level up in"),
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Level up a character in a specified class
    
    This endpoint handles the logic for increasing a character's level
    in a specified class, updating relevant stats accordingly.
    
    Args:
        character_id: ID of the character to level up
        class_name: Name of the class to level up in
        current_user_id: ID of the current user (from auth token)
        
    Returns:
        Updated character data
        
    Raises:
        HTTPException: If character not found or not owned by current user
    """
    # Get the character
    character = await character_service.get_by_id(character_id)
    
    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Character with ID {character_id} not found"
        )
        
    # Check ownership
    if character.user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to modify this character"
        )
        
    # Find the class to level up
    class_found = False
    for class_level in character.classes:
        if class_level.class_type.value == class_name:
            # Check if already at max level (20)
            if class_level.level >= 20:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Character already at maximum level (20) in {class_name}"
                )
                
            # Level up the class
            class_level.level += 1
            class_found = True
            break
            
    # If class not found, add it at level 1
    if not class_found:
        # Calculate total current level
        total_level = sum(c.level for c in character.classes)
        if total_level >= 20:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Character cannot exceed maximum level (20) across all classes"
            )
            
        # Add new class at level 1
        # This would be implemented properly with validation
        # For now, just returning a message
        return {
            "data": character,
            "meta": {
                "message": f"Adding new class {class_name} at level 1 not implemented yet"
            }
        }
        
    # Update character with new level
    updated_character = await character_service.update(
        id=character_id,
        data=CharacterUpdate(classes=character.classes)
    )
    
    return {"data": updated_character, "meta": {}} 
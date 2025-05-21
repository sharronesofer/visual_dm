"""
Authentication relationship router.

This module provides the FastAPI router for managing user-character authentication relationships.
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, UUID4

from backend.systems.auth_user.services import get_current_active_user
from backend.systems.auth_user.utils import (
    # Basic relationship management
    create_auth_relationship,
    update_auth_relationship,
    remove_auth_relationship,
    get_auth_relationship,
    
    # Permission management
    check_permission,
    add_permission,
    remove_permission,
    set_ownership,
    
    # Query functions
    get_user_characters,
    get_character_users,
    
    # Bulk operations
    bulk_create_auth_relationships,
    bulk_remove_auth_relationships,
    
    # Advanced functions
    transfer_character_ownership,
    check_multi_character_permission,
    get_permission_matrix,
    
    # New admin access functions
    check_admin_access,
    
    # New relationship group functions
    create_relationship_group,
    get_relationship_group_members,
    add_to_relationship_group,
    
    # New history and API functions
    get_relationship_history,
    validate_api_key_access,
    generate_character_api_key,
    
    # New cache-related functions
    cache_user_permissions,
    lookup_cached_permission,
    invalidate_permission_cache
)

# Pydantic models for request/response
class AuthRelationshipBase(BaseModel):
    permissions: List[str] = []
    is_owner: bool = False

class AuthRelationshipCreate(AuthRelationshipBase):
    target_id: UUID4

class AuthRelationshipUpdate(AuthRelationshipBase):
    pass

class AuthRelationshipResponse(AuthRelationshipBase):
    source_id: str
    target_id: str
    type: str = "auth"
    data: Dict[str, Any]

class PermissionRequest(BaseModel):
    permission: str

class OwnershipRequest(BaseModel):
    is_owner: bool

class TransferOwnershipRequest(BaseModel):
    to_user_id: UUID4
    keep_original_permissions: bool = True

class MultiCharacterPermissionRequest(BaseModel):
    character_ids: List[UUID4]
    permission: str
    require_all: bool = True

class PermissionMatrixRequest(BaseModel):
    user_ids: List[UUID4]
    character_ids: List[UUID4]

class AdminAccessRequest(BaseModel):
    character_ids: List[UUID4]

class RelationshipGroupCreate(BaseModel):
    name: str
    character_ids: List[UUID4]
    permissions: List[str] = []
    is_owner: bool = False

class RelationshipGroupAddRequest(BaseModel):
    user_ids: Optional[List[UUID4]] = None
    character_ids: Optional[List[UUID4]] = None
    permissions: Optional[List[str]] = None

class ApiKeyCreateRequest(BaseModel):
    character_id: UUID4
    permissions: List[str]
    expires_in_days: Optional[int] = 30

class ApiKeyValidateRequest(BaseModel):
    api_key: str
    character_id: UUID4
    required_permission: str

# Create router
router = APIRouter(
    prefix="/auth-relationships",
    tags=["auth-relationships"],
    responses={404: {"description": "Not found"}}
)

# Routes
@router.post("", response_model=AuthRelationshipResponse)
async def create_relationship(
    relationship: AuthRelationshipCreate,
    current_user = Depends(get_current_active_user)
):
    """Create a new auth relationship between the current user and a character."""
    result = await create_auth_relationship(
        current_user["id"], 
        relationship.target_id,
        relationship.permissions,
        relationship.is_owner
    )
    return result

@router.get("/{character_id}", response_model=AuthRelationshipResponse)
async def get_relationship(
    character_id: UUID4,
    current_user = Depends(get_current_active_user)
):
    """Get the auth relationship between the current user and a character."""
    result = await get_auth_relationship(current_user["id"], character_id)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Relationship not found"
        )
    return result

@router.put("/{character_id}", response_model=AuthRelationshipResponse)
async def update_relationship(
    character_id: UUID4,
    relationship: AuthRelationshipUpdate,
    current_user = Depends(get_current_active_user)
):
    """Update the auth relationship between the current user and a character."""
    try:
        result = await update_auth_relationship(
            current_user["id"],
            character_id,
            permissions=relationship.permissions,
            is_owner=relationship.is_owner
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.delete("/{character_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_relationship(
    character_id: UUID4,
    current_user = Depends(get_current_active_user)
):
    """Delete the auth relationship between the current user and a character."""
    success = await remove_auth_relationship(current_user["id"], character_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Relationship not found"
        )
    return None

@router.get("/check/{character_id}/{permission}", response_model=Dict[str, bool])
async def check_user_permission(
    character_id: UUID4,
    permission: str,
    current_user = Depends(get_current_active_user)
):
    """Check if the current user has a specific permission for a character."""
    has_permission = await check_permission(current_user["id"], character_id, permission)
    return {"has_permission": has_permission}

@router.post("/{character_id}/permissions", response_model=AuthRelationshipResponse)
async def add_user_permission(
    character_id: UUID4,
    permission_request: PermissionRequest,
    current_user = Depends(get_current_active_user)
):
    """Add a permission to the current user's relationship with a character."""
    result = await add_permission(
        current_user["id"],
        character_id,
        permission_request.permission
    )
    return result

@router.delete("/{character_id}/permissions/{permission}", response_model=AuthRelationshipResponse)
async def remove_user_permission(
    character_id: UUID4,
    permission: str,
    current_user = Depends(get_current_active_user)
):
    """Remove a permission from the current user's relationship with a character."""
    try:
        result = await remove_permission(
            current_user["id"],
            character_id,
            permission
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.put("/{character_id}/ownership", response_model=AuthRelationshipResponse)
async def set_character_ownership(
    character_id: UUID4,
    ownership_request: OwnershipRequest,
    current_user = Depends(get_current_active_user)
):
    """Set ownership for the current user's relationship with a character."""
    result = await set_ownership(
        current_user["id"],
        character_id,
        ownership_request.is_owner
    )
    return result

@router.post("/{character_id}/transfer-ownership", response_model=AuthRelationshipResponse)
async def transfer_ownership(
    character_id: UUID4,
    transfer_request: TransferOwnershipRequest,
    current_user = Depends(get_current_active_user)
):
    """Transfer ownership of a character from the current user to another user."""
    try:
        result = await transfer_character_ownership(
            character_id,
            current_user["id"],
            transfer_request.to_user_id,
            transfer_request.keep_original_permissions
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/user/characters", response_model=List[Dict[str, Any]])
async def list_user_characters(
    include_permissions: Optional[bool] = False,
    current_user = Depends(get_current_active_user)
):
    """Get all characters that the current user has access to."""
    result = await get_user_characters(current_user["id"], include_permissions)
    return result

@router.get("/character/{character_id}/users", response_model=List[Dict[str, Any]])
async def list_character_users(
    character_id: UUID4,
    include_permissions: Optional[bool] = False,
    current_user = Depends(get_current_active_user)
):
    """Get all users that have access to a character."""
    # First check if current user has access to this character
    has_access = await check_permission(current_user["id"], character_id, "view_users")
    if not has_access and not current_user.get("is_admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view users for this character"
        )
    
    result = await get_character_users(character_id, include_permissions)
    return result

@router.post("/check-multi", response_model=Dict[str, Any])
async def check_permission_for_multiple_characters(
    request: MultiCharacterPermissionRequest,
    current_user = Depends(get_current_active_user)
):
    """Check if the current user has a specific permission for multiple characters."""
    result = await check_multi_character_permission(
        current_user["id"],
        request.character_ids,
        request.permission,
        request.require_all
    )
    return result

@router.post("/permission-matrix", response_model=Dict[str, Dict[str, Any]])
async def get_permissions_matrix(
    request: PermissionMatrixRequest,
    current_user = Depends(get_current_active_user)
):
    """Get a matrix of permissions between multiple users and characters."""
    # Check if current user is admin or has appropriate permissions
    if not current_user.get("is_admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can access the permission matrix"
        )
    
    result = await get_permission_matrix(request.user_ids, request.character_ids)
    return result 

@router.post("/check-admin-access", response_model=Dict[str, Any])
async def check_admin_access_to_characters(
    request: AdminAccessRequest,
    current_user = Depends(get_current_active_user)
):
    """Check if the current user has admin access to all specified characters."""
    result = await check_admin_access(current_user["id"], request.character_ids)
    return result

@router.post("/groups", response_model=Dict[str, Any])
async def create_new_relationship_group(
    request: RelationshipGroupCreate,
    current_user = Depends(get_current_active_user)
):
    """Create a new relationship group with the current user and specified characters."""
    # Use only the current user for this endpoint for security reasons
    result = await create_relationship_group(
        name=request.name,
        user_ids=[current_user["id"]],
        character_ids=request.character_ids,
        permissions=request.permissions,
        is_owner=request.is_owner
    )
    return result

@router.get("/groups/{group_name}", response_model=Dict[str, Any])
async def get_group_members(
    group_name: str,
    current_user = Depends(get_current_active_user)
):
    """Get members of a relationship group."""
    # In a real implementation, you'd check if the user has permission to view this group
    result = await get_relationship_group_members(group_name)
    return result

@router.post("/groups/{group_name}/add", response_model=Dict[str, Any])
async def add_members_to_group(
    group_name: str,
    request: RelationshipGroupAddRequest,
    current_user = Depends(get_current_active_user)
):
    """Add users and/or characters to an existing relationship group."""
    # In a real implementation, you'd check if the user has permission to modify this group
    result = await add_to_relationship_group(
        group_name=group_name,
        user_ids=request.user_ids,
        character_ids=request.character_ids,
        permissions=request.permissions
    )
    return result

@router.get("/history", response_model=List[Dict[str, Any]])
async def get_auth_relationship_history(
    limit: Optional[int] = 100,
    offset: Optional[int] = 0,
    character_id: Optional[UUID4] = None,
    current_user = Depends(get_current_active_user)
):
    """Get the history of changes to auth relationships for the current user."""
    # You can filter by character_id optionally
    result = await get_relationship_history(
        source_id=current_user["id"],
        target_id=character_id,
        limit=limit,
        offset=offset
    )
    return result

@router.post("/api-keys", response_model=Dict[str, Any])
async def create_character_api_key(
    request: ApiKeyCreateRequest,
    current_user = Depends(get_current_active_user)
):
    """Generate a new API key for accessing a character."""
    # In a real implementation, you'd verify the user has permission to generate keys for this character
    result = await generate_character_api_key(
        user_id=current_user["id"],
        character_id=request.character_id,
        permissions=request.permissions,
        expires_in_days=request.expires_in_days
    )
    return result

@router.post("/api-keys/validate", response_model=Dict[str, Any])
async def validate_api_key(
    request: ApiKeyValidateRequest
):
    """Validate if an API key has access to a character with the required permission."""
    # This endpoint is intentionally not requiring authentication
    result = await validate_api_key_access(
        api_key=request.api_key,
        character_id=request.character_id,
        required_permission=request.required_permission
    )
    return result

@router.post("/cache/permissions", response_model=Dict[str, Any])
async def cache_current_user_permissions(
    force_refresh: Optional[bool] = False,
    current_user = Depends(get_current_active_user)
):
    """Cache all permission data for the current user for faster lookup."""
    result = await cache_user_permissions(
        user_id=current_user["id"],
        force_refresh=force_refresh
    )
    return result

@router.post("/cache/invalidate", response_model=Dict[str, bool])
async def invalidate_permission_caches(
    character_id: Optional[UUID4] = None,
    current_user = Depends(get_current_active_user)
):
    """Invalidate the permission cache for the current user, optionally for a specific character."""
    result = await invalidate_permission_cache(
        user_id=current_user["id"],
        character_id=character_id
    )
    return result

@router.post("/admin/cache/invalidate", response_model=Dict[str, bool])
async def admin_invalidate_all_caches(
    current_user = Depends(get_current_active_user)
):
    """Invalidate all permission caches (admin only)."""
    # Check if user is admin
    if not current_user.get("is_admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can perform this action"
        )
    
    result = await invalidate_permission_cache()
    return result 
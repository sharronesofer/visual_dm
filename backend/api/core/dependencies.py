"""
API Dependencies

This module defines common dependencies for API endpoints.
"""

from fastapi import Depends, HTTPException, Header, status
from typing import Optional, List, Dict, Any, Union
from .base_router import PaginationParams, FilterParams
from ..models.base import APIResponse

# Common dependencies

async def verify_token(
    authorization: Optional[str] = Header(None, description="Bearer token")
) -> Dict[str, Any]:
    """
    Verify that the request has a valid bearer token.
    
    Args:
        authorization: Authorization header containing the bearer token
        
    Returns:
        Dictionary containing user details from the token
        
    Raises:
        HTTPException: If token is missing or invalid
    """
    # This is a placeholder for actual token verification logic
    # In a real application, you would:
    # 1. Check if the Authorization header is present
    # 2. Verify that it starts with "Bearer "
    # 3. Validate the token (signature, expiration, etc.)
    # 4. Extract and return user information from the token
    
    if authorization is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token",
            headers={"WWW-Authenticate": "Bearer"}
        )
        
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication scheme",
            headers={"WWW-Authenticate": "Bearer"}
        )
        
    token = authorization.replace("Bearer ", "")
    
    # TODO: Implement actual token validation and data extraction
    # For now, we'll return dummy data
    return {
        "user_id": "dummy-user-id",
        "username": "dummy-user",
        "roles": ["user"]
    }

async def verify_admin_token(
    token_data: Dict[str, Any] = Depends(verify_token)
) -> Dict[str, Any]:
    """
    Verify that the user has admin privileges.
    
    Args:
        token_data: Data from the token verification
        
    Returns:
        The token data if the user is an admin
        
    Raises:
        HTTPException: If the user is not an admin
    """
    if "admin" not in token_data.get("roles", []):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
        
    return token_data

# Request parameter dependencies

def get_current_user_id(
    token_data: Dict[str, Any] = Depends(verify_token)
) -> str:
    """
    Extract the current user ID from the token data.
    
    Args:
        token_data: Data from the token verification
        
    Returns:
        The user ID from the token
    """
    return token_data["user_id"]

def get_pagination_params(
    page: int = 1,
    page_size: int = 20,
    max_page_size: int = 100
) -> PaginationParams:
    """
    Create pagination parameters with validation.
    
    Args:
        page: Page number (min: 1)
        page_size: Items per page (min: 1, max: max_page_size)
        max_page_size: Maximum allowed page size
        
    Returns:
        PaginationParams object
        
    Raises:
        HTTPException: If pagination parameters are invalid
    """
    if page < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Page number must be greater than or equal to 1"
        )
        
    if page_size < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Page size must be greater than or equal to 1"
        )
        
    if page_size > max_page_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Page size must be less than or equal to {max_page_size}"
        )
        
    return PaginationParams(page=page, page_size=page_size)

# Response wrappers

def wrap_response(data: Any, meta: Dict[str, Any] = None) -> APIResponse:
    """
    Wrap API response data in the standard format.
    
    Args:
        data: Response data
        meta: Optional metadata
        
    Returns:
        Formatted API response
    """
    if meta is None:
        meta = {}
        
    return {
        "data": data,
        "meta": meta
    } 
"""
API router for world generation endpoints.

This module provides FastAPI router for world generation related operations.
"""
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, status, Body, Query

from backend.systems.world_generation.models import ContinentSchema, ContinentCreationRequestSchema
from backend.systems.world_generation.continent_service import continent_service

router = APIRouter(
    prefix="/world",
    tags=["World Generation"],
)

@router.post("/continents", response_model=ContinentSchema, status_code=status.HTTP_201_CREATED)
async def create_continent_endpoint(creation_request: ContinentCreationRequestSchema = Body(...)):
    """
    Creates a new continent with procedurally generated regions.
    
    Args:
        creation_request: Parameters for continent creation
        
    Returns:
        The created continent with all generated regions
        
    Raises:
        HTTPException: If continent creation fails
    """
    try:
        continent = continent_service.create_new_continent(creation_request)
        return continent
    except Exception as e:
        # In production, log the exception
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Failed to create continent: {str(e)}"
        )

@router.get("/continents/{continent_id}", response_model=ContinentSchema)
async def get_continent_endpoint(continent_id: str):
    """
    Retrieves details of a continent by ID.
    
    Args:
        continent_id: The ID of the continent to retrieve
        
    Returns:
        The continent details
        
    Raises:
        HTTPException: If continent not found
    """
    continent = continent_service.get_continent_details(continent_id)
    if not continent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Continent not found"
        )
    return continent

@router.get("/continents", response_model=List[ContinentSchema])
async def list_all_continents_endpoint(
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of continents to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination")
):
    """
    Lists all continents with pagination support.
    
    Args:
        limit: Maximum number of continents to return
        offset: Offset for pagination
        
    Returns:
        List of continents
    """
    all_continents = continent_service.list_all_continents()
    return all_continents[offset:offset+limit]

@router.patch("/continents/{continent_id}/metadata", response_model=ContinentSchema)
async def update_continent_metadata_endpoint(
    continent_id: str, 
    metadata: Dict[str, Any] = Body(..., description="Metadata to update")
):
    """
    Updates metadata for a continent.
    
    Args:
        continent_id: The ID of the continent to update
        metadata: The metadata to update
        
    Returns:
        The updated continent
        
    Raises:
        HTTPException: If continent not found
    """
    updated_continent = continent_service.update_continent_metadata(continent_id, metadata)
    if not updated_continent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Continent not found"
        )
    return updated_continent

@router.delete("/continents/{continent_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_continent_endpoint(continent_id: str):
    """
    Deletes a continent.
    
    Args:
        continent_id: The ID of the continent to delete
        
    Raises:
        HTTPException: If continent not found
    """
    success = continent_service.delete_continent(continent_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Continent not found"
        )
    return None 
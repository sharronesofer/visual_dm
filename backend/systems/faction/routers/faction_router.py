"""
Faction API router module.

This module provides API routes for faction system access.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.systems.faction.faction_manager import FactionManager
from backend.systems.faction.models.faction import Faction
from backend.systems.faction.schemas.faction_types import FactionSchema, FactionType
from backend.systems.faction.services.faction_service import FactionNotFoundError, DuplicateFactionError

# Create router
faction_router = APIRouter(
    prefix="/factions",
    tags=["factions"],
    responses={404: {"description": "Not found"}},
)

# Dependency to get database session
def get_db():
    # This would be implemented to get actual DB session
    # For example integration with SQLAlchemy
    db = None
    try:
        yield db
    finally:
        if db:
            db.close()

# Dependency to get faction manager
def get_faction_manager(db: Session = Depends(get_db)):
    return FactionManager(db)


@faction_router.get("/", response_model=List[FactionSchema])
async def get_factions(
    manager: FactionManager = Depends(get_faction_manager),
    faction_type: Optional[str] = None,
    is_active: Optional[bool] = None,
    min_influence: Optional[float] = None
):
    """Get all factions with optional filters."""
    filters = {}
    if faction_type:
        filters["faction_type"] = faction_type
    if is_active is not None:
        filters["is_active"] = is_active
    if min_influence is not None:
        filters["min_influence"] = min_influence
    
    return manager.get_factions(**filters)


@faction_router.get("/{faction_id}", response_model=FactionSchema)
async def get_faction(
    faction_id: int,
    manager: FactionManager = Depends(get_faction_manager)
):
    """Get a specific faction by ID."""
    faction = manager.get_faction(faction_id)
    if not faction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Faction with ID {faction_id} not found"
        )
    return faction


@faction_router.post("/", response_model=FactionSchema, status_code=status.HTTP_201_CREATED)
async def create_faction(
    faction_data: FactionSchema,
    manager: FactionManager = Depends(get_faction_manager)
):
    """Create a new faction."""
    try:
        faction = manager.create_faction(
            name=faction_data.name,
            description=faction_data.description,
            faction_type=faction_data.faction_type,
            alignment=faction_data.alignment,
            influence=faction_data.influence,
            resources=faction_data.resources,
            territory=faction_data.territory,
            leader_id=faction_data.leader_id,
            headquarters_id=faction_data.headquarters_id,
            parent_faction_id=faction_data.parent_faction_id,
        )
        return faction
    except DuplicateFactionError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )


@faction_router.put("/{faction_id}", response_model=FactionSchema)
async def update_faction(
    faction_id: int,
    faction_data: FactionSchema,
    manager: FactionManager = Depends(get_faction_manager)
):
    """Update an existing faction."""
    try:
        updates = faction_data.dict(exclude_unset=True)
        faction = manager.update_faction(faction_id, **updates)
        return faction
    except FactionNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except DuplicateFactionError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )


@faction_router.delete("/{faction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_faction(
    faction_id: int,
    manager: FactionManager = Depends(get_faction_manager)
):
    """Delete a faction."""
    try:
        manager.delete_faction(faction_id)
    except FactionNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    return None 
"""
Economic Espionage System Router

FastAPI router for the Economic Espionage System endpoints.
"""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.infrastructure.services.espionage_service import EspionageInfrastructureService
from backend.infrastructure.schemas.espionage_schemas import (
    EspionageSchema,
    EspionageCreateSchema,
    EspionageUpdateSchema,
    EspionageListResponseSchema
)
from backend.infrastructure.database import get_db_session

router = APIRouter(prefix="/espionage", tags=["espionage"])


@router.post("/", response_model=EspionageSchema)
async def create_espionage_entity(
    request: EspionageCreateSchema,
    db: Session = Depends(get_db_session)
):
    """Create a new espionage entity"""
    service = EspionageInfrastructureService(db)
    try:
        return await service.create_espionage_entity(request)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{entity_id}", response_model=EspionageSchema)
async def get_espionage_entity(
    entity_id: UUID,
    db: Session = Depends(get_db_session)
):
    """Get an espionage entity by ID"""
    service = EspionageInfrastructureService(db)
    entity = await service.get_espionage_entity(entity_id)
    if not entity:
        raise HTTPException(status_code=404, detail="Espionage entity not found")
    return entity


@router.put("/{entity_id}", response_model=EspionageSchema)
async def update_espionage_entity(
    entity_id: UUID,
    request: EspionageUpdateSchema,
    db: Session = Depends(get_db_session)
):
    """Update an espionage entity"""
    service = EspionageInfrastructureService(db)
    entity = await service.update_espionage_entity(entity_id, request)
    if not entity:
        raise HTTPException(status_code=404, detail="Espionage entity not found")
    return entity


@router.delete("/{entity_id}")
async def delete_espionage_entity(
    entity_id: UUID,
    db: Session = Depends(get_db_session)
):
    """Delete an espionage entity"""
    service = EspionageInfrastructureService(db)
    success = await service.delete_espionage_entity(entity_id)
    if not success:
        raise HTTPException(status_code=404, detail="Espionage entity not found")
    return {"message": "Espionage entity deleted successfully"}


@router.get("/", response_model=List[EspionageSchema])
async def list_espionage_entities(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db_session)
):
    """List espionage entities with optional filtering"""
    service = EspionageInfrastructureService(db)
    return await service.list_espionage_entities(skip, limit, status)

# TODO: The following endpoints require business logic integration
# These should be moved to a higher-level service that coordinates
# between the business logic service and infrastructure service

# @router.get("/faction/{faction_id}/capabilities")
# @router.get("/threat-assessment/{target_id}")
# @router.get("/statistics") 
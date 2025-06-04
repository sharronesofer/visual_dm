"""
Inventory System API Router

This module provides FastAPI endpoints for the inventory system
according to the Development Bible infrastructure standards.
"""

from typing import Optional, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from backend.infrastructure.database import get_db
from backend.infrastructure.repositories.inventory_repository import SQLAlchemyInventoryRepository
from backend.infrastructure.utils.inventory.config_loader import ConfigurableInventoryService
from backend.infrastructure.utils.inventory.character_integration import create_character_service
from backend.systems.inventory.models import (
    CreateInventoryRequest,
    UpdateInventoryRequest,
    InventoryResponse,
    InventoryListResponse,
    InventoryCapacityInfo,
    InventoryFilterOptions,
    InventoryStatistics,
    InventoryType,
    InventoryStatus
)
from backend.systems.inventory.services import create_inventory_service

# Create router
router = APIRouter(prefix="/api/v1/inventory", tags=["inventory"])


def get_inventory_service(db: Session = Depends(get_db)):
    """Dependency to create inventory service"""
    repository = SQLAlchemyInventoryRepository(db)
    config_service = ConfigurableInventoryService()
    character_service = create_character_service(db, use_mock=True)  # Use mock for now
    
    return create_inventory_service(
        repository=repository,
        config_service=config_service,
        character_service=character_service
    )


@router.post("/", response_model=InventoryResponse, status_code=status.HTTP_201_CREATED)
async def create_inventory(
    request: CreateInventoryRequest,
    service = Depends(get_inventory_service)
):
    """Create a new inventory"""
    try:
        return await service.create_inventory(request)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/{inventory_id}", response_model=InventoryResponse)
async def get_inventory(
    inventory_id: UUID,
    service = Depends(get_inventory_service)
):
    """Get inventory by ID"""
    try:
        inventory = await service.get_inventory_by_id(inventory_id)
        if not inventory:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inventory not found")
        return inventory
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.put("/{inventory_id}", response_model=InventoryResponse)
async def update_inventory(
    inventory_id: UUID,
    request: UpdateInventoryRequest,
    service = Depends(get_inventory_service)
):
    """Update inventory"""
    try:
        return await service.update_inventory(inventory_id, request)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.delete("/{inventory_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_inventory(
    inventory_id: UUID,
    service = Depends(get_inventory_service)
):
    """Delete inventory"""
    try:
        success = await service.delete_inventory(inventory_id)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inventory not found")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/", response_model=InventoryListResponse)
async def list_inventories(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(50, ge=1, le=100, description="Page size"),
    status: Optional[InventoryStatus] = Query(None, description="Filter by status"),
    inventory_type: Optional[InventoryType] = Query(None, description="Filter by type"),
    owner_id: Optional[UUID] = Query(None, description="Filter by owner"),
    player_id: Optional[UUID] = Query(None, description="Filter by player"),
    search: Optional[str] = Query(None, description="Search in name/description"),
    service = Depends(get_inventory_service)
):
    """List inventories with filtering and pagination"""
    try:
        # Build filters
        filters = InventoryFilterOptions()
        if status:
            filters.status = [status]
        if inventory_type:
            filters.inventory_type = [inventory_type]
        if owner_id:
            filters.owner_id = owner_id
        if player_id:
            filters.player_id = player_id
        if search:
            filters.search = search
        
        return await service.list_inventories(page, size, filters)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/{inventory_id}/capacity", response_model=InventoryCapacityInfo)
async def get_inventory_capacity(
    inventory_id: UUID,
    service = Depends(get_inventory_service)
):
    """Get detailed capacity information for inventory"""
    try:
        return await service.get_inventory_capacity_info(inventory_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/statistics/overview", response_model=InventoryStatistics)
async def get_inventory_statistics(
    service = Depends(get_inventory_service)
):
    """Get inventory system statistics"""
    try:
        return await service.get_inventory_statistics()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.post("/{inventory_id}/validate-addition")
async def validate_item_addition(
    inventory_id: UUID,
    item_weight: float = Query(..., description="Weight of item to add"),
    quantity: int = Query(1, ge=1, description="Quantity to add"),
    service = Depends(get_inventory_service)
):
    """Validate if item can be added to inventory"""
    try:
        return await service.validate_item_addition(inventory_id, item_weight, quantity)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


# Player-specific endpoints
@router.get("/player/{player_id}/inventories", response_model=List[InventoryResponse])
async def get_player_inventories(
    player_id: UUID,
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(50, ge=1, le=100, description="Page size"),
    db: Session = Depends(get_db)
):
    """Get all inventories for a player"""
    try:
        repository = SQLAlchemyInventoryRepository(db)
        inventories, total = await repository.list_by_player(player_id, page, size)
        
        # Convert to response models
        responses = [InventoryResponse.from_model(inv) for inv in inventories]
        return responses
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


# Character-specific endpoints
@router.get("/character/{character_id}/inventories", response_model=List[InventoryResponse])
async def get_character_inventories(
    character_id: UUID,
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(50, ge=1, le=100, description="Page size"),
    db: Session = Depends(get_db)
):
    """Get all inventories for a character"""
    try:
        repository = SQLAlchemyInventoryRepository(db)
        inventories, total = await repository.list_by_owner(character_id, page, size)
        
        # Convert to response models
        responses = [InventoryResponse.from_model(inv) for inv in inventories]
        return responses
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/character/{character_id}/capacity-info")
async def get_character_capacity_info(
    character_id: UUID,
    db: Session = Depends(get_db)
):
    """Get capacity information for a character"""
    try:
        from backend.infrastructure.utils.inventory.character_integration import (
            create_character_service,
            create_character_integration
        )
        
        character_service = create_character_service(db, use_mock=True)
        integration = create_character_integration(character_service)
        
        return await integration.calculate_character_inventory_capacity(character_id)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


# Configuration endpoints
@router.get("/config/types")
async def get_inventory_types():
    """Get available inventory types and their configurations"""
    try:
        config_service = ConfigurableInventoryService()
        return config_service.config_loader.get_inventory_types()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/config/statuses")
async def get_inventory_statuses():
    """Get available inventory statuses and transitions"""
    try:
        config_service = ConfigurableInventoryService()
        return config_service.config_loader.get_inventory_statuses()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/config/rules")
async def get_inventory_rules():
    """Get inventory business rules configuration"""
    try:
        config_service = ConfigurableInventoryService()
        return config_service.config_loader.get_inventory_rules()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


# Health check endpoint
@router.get("/health")
async def health_check():
    """Health check for inventory system"""
    return {
        "status": "healthy",
        "system": "inventory",
        "version": "1.0.0",
        "timestamp": "2024-01-01T00:00:00Z"
    } 
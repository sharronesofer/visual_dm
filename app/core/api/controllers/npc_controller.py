"""
NPC controller with standardized response formatting and pagination.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.api.decorators import validate_response
from app.core.api.pagination import PaginationParams, get_pagination_params, paginate_query
from app.core.api.responses import APIResponse, APIStatus
from app.core.database import get_db
from app.models.npc import NPC, NPCCreate, NPCUpdate, NPCResponse
from app.services.npc_service import NPCService

router = APIRouter(prefix="/npcs", tags=["NPCs"])

@router.get("/")
@validate_response(response_model=List[NPCResponse])
async def list_npcs(
    session: AsyncSession = Depends(get_db),
    pagination: PaginationParams = Depends(get_pagination_params),
    faction_id: Optional[int] = Query(None, description="Filter by faction ID"),
    location_id: Optional[int] = Query(None, description="Filter by location ID"),
    status: Optional[str] = Query(None, description="Filter by NPC status")
) -> APIResponse:
    """
    List NPCs with pagination and optional filtering.
    """
    try:
        service = NPCService(session)
        query = service.build_list_query(
            faction_id=faction_id,
            location_id=location_id,
            status=status
        )
        
        # Get paginated results
        page = await paginate_query(query, pagination)
        
        # Convert to response models
        response_items = [NPCResponse.from_orm(item) for item in page.items]
        
        return APIResponse.success(
            data=response_items,
            metadata={"filters_applied": {
                "faction_id": faction_id,
                "location_id": location_id,
                "status": status
            }},
            pagination=page.page_info
        )
        
    except Exception as e:
        return APIResponse.server_error(
            message="Failed to list NPCs",
            details={"error": str(e)}
        )

@router.get("/{npc_id}")
@validate_response(response_model=NPCResponse)
async def get_npc(
    npc_id: int,
    session: AsyncSession = Depends(get_db)
) -> APIResponse:
    """
    Get a specific NPC by ID.
    """
    try:
        service = NPCService(session)
        npc = await service.get_by_id(npc_id)
        
        if not npc:
            return APIResponse.not_found(
                message=f"NPC with ID {npc_id} not found"
            )
            
        return APIResponse.success(
            data=NPCResponse.from_orm(npc)
        )
        
    except Exception as e:
        return APIResponse.server_error(
            message="Failed to get NPC",
            details={"error": str(e)}
        )

@router.post("/")
@validate_response(response_model=NPCResponse)
async def create_npc(
    npc_data: NPCCreate,
    session: AsyncSession = Depends(get_db)
) -> APIResponse:
    """
    Create a new NPC.
    """
    try:
        service = NPCService(session)
        
        # Check for duplicate name
        if await service.exists_by_name(npc_data.name):
            return APIResponse.conflict(
                message=f"NPC with name '{npc_data.name}' already exists",
                details={"field": "name"}
            )
            
        # Validate faction if provided
        if npc_data.faction_id and not await service.faction_exists(npc_data.faction_id):
            return APIResponse.bad_request(
                message=f"Faction with ID {npc_data.faction_id} not found",
                details={"field": "faction_id"}
            )
            
        # Validate location if provided
        if npc_data.location_id and not await service.location_exists(npc_data.location_id):
            return APIResponse.bad_request(
                message=f"Location with ID {npc_data.location_id} not found",
                details={"field": "location_id"}
            )
            
        # Create NPC
        npc = await service.create(npc_data)
        await session.commit()
        
        return APIResponse.created(
            data=NPCResponse.from_orm(npc)
        )
        
    except Exception as e:
        await session.rollback()
        return APIResponse.server_error(
            message="Failed to create NPC",
            details={"error": str(e)}
        )

@router.put("/{npc_id}")
@validate_response(response_model=NPCResponse)
async def update_npc(
    npc_id: int,
    npc_data: NPCUpdate,
    session: AsyncSession = Depends(get_db)
) -> APIResponse:
    """
    Update an existing NPC.
    """
    try:
        service = NPCService(session)
        
        # Check if NPC exists
        npc = await service.get_by_id(npc_id)
        if not npc:
            return APIResponse.not_found(
                message=f"NPC with ID {npc_id} not found"
            )
            
        # Check for name conflict if name is being updated
        if npc_data.name and npc_data.name != npc.name:
            if await service.exists_by_name(npc_data.name):
                return APIResponse.conflict(
                    message=f"NPC with name '{npc_data.name}' already exists",
                    details={"field": "name"}
                )
                
        # Validate faction if being updated
        if npc_data.faction_id and not await service.faction_exists(npc_data.faction_id):
            return APIResponse.bad_request(
                message=f"Faction with ID {npc_data.faction_id} not found",
                details={"field": "faction_id"}
            )
            
        # Validate location if being updated
        if npc_data.location_id and not await service.location_exists(npc_data.location_id):
            return APIResponse.bad_request(
                message=f"Location with ID {npc_data.location_id} not found",
                details={"field": "location_id"}
            )
            
        # Update NPC
        updated_npc = await service.update(npc_id, npc_data)
        await session.commit()
        
        return APIResponse.success(
            data=NPCResponse.from_orm(updated_npc)
        )
        
    except Exception as e:
        await session.rollback()
        return APIResponse.server_error(
            message="Failed to update NPC",
            details={"error": str(e)}
        )

@router.delete("/{npc_id}")
@validate_response()
async def delete_npc(
    npc_id: int,
    session: AsyncSession = Depends(get_db)
) -> APIResponse:
    """
    Delete an NPC.
    """
    try:
        service = NPCService(session)
        
        # Check if NPC exists
        if not await service.exists(npc_id):
            return APIResponse.not_found(
                message=f"NPC with ID {npc_id} not found"
            )
            
        # Check for dependencies
        dependencies = await service.get_dependencies(npc_id)
        if dependencies:
            return APIResponse.conflict(
                message="Cannot delete NPC due to existing dependencies",
                details={"dependencies": dependencies}
            )
            
        # Delete NPC
        await service.delete(npc_id)
        await session.commit()
        
        return APIResponse.success(
            data={"message": f"NPC with ID {npc_id} deleted successfully"}
        )
        
    except Exception as e:
        await session.rollback()
        return APIResponse.server_error(
            message="Failed to delete NPC",
            details={"error": str(e)}
        ) 
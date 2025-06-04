"""
NPC Barter Router

FastAPI router for NPC bartering operations.
Handles barter sessions, item exchanges, and economic interactions.
"""

import logging
from typing import List, Dict, Any, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body, status
from pydantic import BaseModel, Field

# Import business logic services from systems
from backend.systems.npc.services.npc_barter_service import NPCBarterService, get_npc_barter_service

# Use local infrastructure imports for schemas
from backend.infrastructure.systems.npc.schemas.barter_schemas import (
    BarterInitiateRequest,
    BarterCompleteRequest,
    BarterInventoryResponse,
    BarterPriceResponse,
    BarterInitiateResponse,
    BarterCompleteResponse,
    BarterErrorResponse
)
from backend.infrastructure.shared.exceptions import (
    NpcNotFoundError,
    NpcValidationError
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/npc", tags=["npc-barter"])


@router.get(
    "/{npc_id}/barter/inventory",
    response_model=BarterInventoryResponse,
    summary="Get NPC's tradeable inventory",
    description="Get all items that an NPC is willing to trade, organized by availability tier"
)
async def get_npc_tradeable_inventory(
    npc_id: UUID = Path(..., description="UUID of the NPC"),
    character_id: Optional[str] = Query(None, description="Character ID for relationship calculation"),
    barter_service: NPCBarterService = Depends(get_npc_barter_service)
):
    """Get all items that an NPC is willing to trade"""
    try:
        result = await barter_service.get_tradeable_items(npc_id, character_id)
        return BarterInventoryResponse(**result)
        
    except NpcNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"NPC not found: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error getting tradeable inventory: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while retrieving inventory"
        )


@router.get(
    "/{npc_id}/barter/price/{item_id}",
    response_model=BarterPriceResponse,
    summary="Get item barter price",
    description="Get the barter price for a specific item from an NPC"
)
async def get_item_barter_price(
    npc_id: UUID = Path(..., description="UUID of the NPC"),
    item_id: str = Path(..., description="ID or name of the item"),
    character_id: Optional[str] = Query(None, description="Character ID for relationship calculation"),
    barter_service: NPCBarterService = Depends(get_npc_barter_service)
):
    """Get the barter price for a specific item"""
    try:
        result = await barter_service.get_item_barter_price(npc_id, item_id, character_id)
        return BarterPriceResponse(**result)
        
    except NpcNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"NPC not found: {str(e)}"
        )
    except NpcValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error getting item price: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while calculating price"
        )


@router.post(
    "/{npc_id}/barter/initiate",
    response_model=BarterInitiateResponse,
    summary="Initiate barter transaction",
    description="Initiate a bartering transaction with an NPC by proposing an exchange"
)
async def initiate_barter(
    npc_id: UUID = Path(..., description="UUID of the NPC"),
    request: BarterInitiateRequest = ...,
    barter_service: NPCBarterService = Depends(get_npc_barter_service)
):
    """Initiate a bartering transaction with an NPC"""
    try:
        # Convert Pydantic models to dict for service layer
        offer_items = [item.model_dump() for item in request.offer_items]
        request_items = [item.model_dump() for item in request.request_items]
        
        result = await barter_service.initiate_barter(
            npc_id, 
            request.character_id, 
            offer_items, 
            request_items
        )
        
        return BarterInitiateResponse(**result)
        
    except NpcNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"NPC not found: {str(e)}"
        )
    except NpcValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error initiating barter: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while initiating barter"
        )


@router.post(
    "/{npc_id}/barter/complete",
    response_model=BarterCompleteResponse,
    summary="Complete barter transaction",
    description="Complete a previously validated bartering transaction"
)
async def complete_barter(
    npc_id: UUID = Path(..., description="UUID of the NPC"),
    request: BarterCompleteRequest = ...,
    barter_service: NPCBarterService = Depends(get_npc_barter_service)
):
    """Complete a bartering transaction"""
    try:
        result = await barter_service.complete_barter(
            npc_id, 
            request.character_id, 
            request.transaction_data
        )
        
        return BarterCompleteResponse(**result)
        
    except NpcNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"NPC not found: {str(e)}"
        )
    except NpcValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error completing barter: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while completing barter"
        )


@router.get(
    "/{npc_id}/barter/status",
    summary="Get NPC barter status",
    description="Get general information about an NPC's willingness and ability to trade"
)
async def get_npc_barter_status(
    npc_id: UUID = Path(..., description="UUID of the NPC"),
    character_id: Optional[str] = Query(None, description="Character ID for relationship calculation"),
    barter_service: NPCBarterService = Depends(get_npc_barter_service)
):
    """Get general barter status for an NPC"""
    try:
        # Get basic tradeable inventory summary
        inventory_result = await barter_service.get_tradeable_items(npc_id, character_id)
        
        # Calculate summary statistics
        total_items = inventory_result.get("total_items", 0)
        available_items = len(inventory_result.get("items", {}).get("always_available", []))
        high_trust_items = len(inventory_result.get("items", {}).get("high_trust_required", []))
        unavailable_items = len(inventory_result.get("items", {}).get("not_available", []))
        
        return {
            "npc_id": str(npc_id),
            "npc_name": inventory_result.get("npc_name"),
            "can_trade": total_items > 0,
            "relationship_trust": inventory_result.get("relationship_trust", 0.0),
            "inventory_summary": {
                "total_items": total_items,
                "available_items": available_items,
                "high_trust_items": high_trust_items,
                "unavailable_items": unavailable_items
            },
            "trading_tips": [
                "Every NPC can participate in bartering",
                "Build trust to access valuable items",
                "Some items are never available (equipped, role-essential)",
                "Fair trades improve relationships"
            ]
        }
        
    except NpcNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"NPC not found: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error getting barter status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while getting barter status"
        ) 
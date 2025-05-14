"""Item controller implementation.

This module provides the API controller for Item entities, implementing standard CRUD
operations and item-specific endpoints.
"""

from typing import Dict, Any, List
from fastapi import APIRouter, Depends, Path, Query, HTTPException
from pydantic import BaseModel

from .base_controller import BaseController
from ...middleware.rate_limit import RateLimiter
from ...middleware.cache import APICache
from ...services.item import ItemService
from ....search.entities import ItemModel
from ..patterns import BaseResponse, PaginatedResponse

class ItemTransferRequest(BaseModel):
    """Request model for transferring an item."""
    target_id: str  # Can be NPC ID, player ID, or location ID
    target_type: str  # 'npc', 'player', or 'location'
    quantity: int = 1
    reason: str

class ItemController(BaseController[ItemModel]):
    """Controller for Item-related endpoints."""
    
    def __init__(
        self,
        service: ItemService,
        router: APIRouter,
        rate_limiter: RateLimiter,
        cache: APICache
    ):
        """Initialize the Item controller."""
        super().__init__(service, router, "item", rate_limiter, cache)
        self._register_item_routes()
        
    def _register_item_routes(self) -> None:
        """Register Item-specific routes."""
        # Transfer item endpoint
        self.router.add_api_route(
            "/items/{id}/transfer",
            self.transfer_item,
            methods=["POST"],
            response_model=BaseResponse[ItemModel],
            summary="Transfer an item",
            description="Transfer an item to an NPC, player, or location"
        )
        
        # Get items by owner endpoint
        self.router.add_api_route(
            "/items/by-owner/{owner_id}",
            self.get_by_owner,
            methods=["GET"],
            response_model=PaginatedResponse[ItemModel],
            summary="Get items by owner",
            description="Get all items owned by a specific NPC, player, or stored at a location"
        )
        
        # Get items by type endpoint
        self.router.add_api_route(
            "/items/by-type/{item_type}",
            self.get_by_type,
            methods=["GET"],
            response_model=PaginatedResponse[ItemModel],
            summary="Get items by type",
            description="Get all items of a specific type"
        )
        
        # Get items by rarity endpoint
        self.router.add_api_route(
            "/items/by-rarity/{rarity}",
            self.get_by_rarity,
            methods=["GET"],
            response_model=PaginatedResponse[ItemModel],
            summary="Get items by rarity",
            description="Get all items of a specific rarity level"
        )
        
    async def transfer_item(
        self,
        id: str = Path(..., description="The ID of the item"),
        request: ItemTransferRequest = None
    ) -> BaseResponse[ItemModel]:
        """Transfer an item to a new owner or location."""
        try:
            item = await self.service.transfer_item(
                id,
                request.target_id,
                request.target_type,
                request.quantity,
                request.reason
            )
            if not item:
                raise HTTPException(status_code=404, detail="Item not found")
            return BaseResponse[ItemModel](
                data=item,
                message="Item transferred successfully"
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
            
    async def get_by_owner(
        self,
        owner_id: str = Path(..., description="The ID of the owner (NPC, player, or location)"),
        owner_type: str = Query(..., description="Type of owner ('npc', 'player', or 'location')"),
        page: int = Query(1, ge=1, description="Page number"),
        per_page: int = Query(20, ge=1, le=100, description="Items per page")
    ) -> PaginatedResponse[ItemModel]:
        """Get all items owned by a specific entity."""
        try:
            items, total = await self.service.get_by_owner(owner_id, owner_type, page, per_page)
            return PaginatedResponse[ItemModel](
                data=items,
                meta={
                    "page": page,
                    "per_page": per_page,
                    "total_items": total,
                    "total_pages": (total + per_page - 1) // per_page
                }
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
            
    async def get_by_type(
        self,
        item_type: str = Path(..., description="The type of items to get"),
        page: int = Query(1, ge=1, description="Page number"),
        per_page: int = Query(20, ge=1, le=100, description="Items per page")
    ) -> PaginatedResponse[ItemModel]:
        """Get all items of a specific type."""
        try:
            items, total = await self.service.get_by_type(item_type, page, per_page)
            return PaginatedResponse[ItemModel](
                data=items,
                meta={
                    "page": page,
                    "per_page": per_page,
                    "total_items": total,
                    "total_pages": (total + per_page - 1) // per_page
                }
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
            
    async def get_by_rarity(
        self,
        rarity: str = Path(..., description="The rarity level of items to get"),
        page: int = Query(1, ge=1, description="Page number"),
        per_page: int = Query(20, ge=1, le=100, description="Items per page")
    ) -> PaginatedResponse[ItemModel]:
        """Get all items of a specific rarity level."""
        try:
            items, total = await self.service.get_by_rarity(rarity, page, per_page)
            return PaginatedResponse[ItemModel](
                data=items,
                meta={
                    "page": page,
                    "per_page": per_page,
                    "total_items": total,
                    "total_pages": (total + per_page - 1) // per_page
                }
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e)) 
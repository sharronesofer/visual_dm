"""
Crafting Router

FastAPI router for core crafting operations.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, status
from fastapi.responses import JSONResponse
import uuid

from backend.systems.crafting.schemas import (
    CraftingStartSchema,
    CraftingStartResponseSchema,
    CraftingStatusResponseSchema,
    CraftingCompleteSchema,
    CraftingCompleteResponseSchema,
    CraftingCancelSchema,
    CraftingCancelResponseSchema,
    CraftingQueueSchema,
    CraftingQueueResponseSchema,
    CraftingBatchSchema,
    CraftingBatchResponseSchema,
    RecipeListResponseSchema
)
from backend.systems.crafting.services import CraftingService
from backend.systems.crafting.repositories import RecipeRepository

router = APIRouter(prefix="/crafting", tags=["crafting"])

# Dependency to get crafting service
def get_crafting_service() -> CraftingService:
    """Get crafting service instance."""
    return CraftingService()

# Dependency to get recipe repository
def get_recipe_repository() -> RecipeRepository:
    """Get recipe repository instance."""
    return RecipeRepository()

@router.post("/start", response_model=CraftingStartResponseSchema, status_code=status.HTTP_201_CREATED)
async def start_crafting(
    crafting_request: CraftingStartSchema,
    service: CraftingService = Depends(get_crafting_service)
):
    """
    Start a new crafting operation.
    
    This endpoint initiates the crafting process for a specific recipe,
    reserves required ingredients and tools, and returns operation details.
    """
    try:
        # TODO: Implement crafting start logic in CraftingService
        # For now, create a mock response
        crafting_id = f"craft_{crafting_request.recipe_id}_{crafting_request.character_id}_{uuid.uuid4().hex[:8]}"
        
        # Validate recipe exists
        recipe_repo = RecipeRepository()
        recipe = recipe_repo.get_by_id(str(crafting_request.recipe_id))
        if not recipe:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Recipe with ID {crafting_request.recipe_id} not found"
            )
        
        # TODO: Validate character has required skills and ingredients
        # TODO: Reserve station if required
        # TODO: Start crafting process
        
        from datetime import datetime, timedelta
        start_time = datetime.now()
        estimated_duration = recipe.crafting_time * crafting_request.quantity
        
        return CraftingStartResponseSchema(
            crafting_id=crafting_id,
            recipe_id=crafting_request.recipe_id,
            character_id=crafting_request.character_id,
            station_id=crafting_request.station_id,
            quantity=crafting_request.quantity,
            status="in_progress",
            start_time=start_time,
            estimated_completion=start_time + timedelta(seconds=estimated_duration),
            estimated_duration=estimated_duration,
            efficiency_multiplier=1.0,  # TODO: Calculate from station/skills
            quality_bonus=0.0,  # TODO: Calculate from station/skills
            experience_multiplier=1.0,  # TODO: Calculate from bonuses
            ingredients_consumed=crafting_request.ingredients,
            tools_used=crafting_request.tools
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start crafting: {str(e)}"
        )

@router.get("/{crafting_id}/status", response_model=CraftingStatusResponseSchema)
async def get_crafting_status(
    crafting_id: str,
    service: CraftingService = Depends(get_crafting_service)
):
    """
    Get the current status of a crafting operation.
    
    Returns detailed progress information including completion percentage,
    current step, and estimated time remaining.
    """
    try:
        # TODO: Implement status tracking in CraftingService
        # For now, return mock status
        from datetime import datetime
        from backend.systems.crafting.schemas import CraftingProgressSchema
        
        # Mock progress data
        progress = CraftingProgressSchema(
            crafting_id=crafting_id,
            progress_percentage=75.0,  # 75% complete
            current_step="Assembling components",
            steps_completed=3,
            total_steps=4,
            time_elapsed=180,  # 3 minutes
            time_remaining=60,  # 1 minute
            quality_indicators={"stability": "good", "precision": "excellent"},
            events=["Started crafting", "Prepared materials", "Began assembly"]
        )
        
        return CraftingStatusResponseSchema(
            crafting_id=crafting_id,
            recipe_id=uuid.uuid4(),  # TODO: Get from actual operation
            character_id="mock_character",  # TODO: Get from actual operation
            station_id=None,
            quantity=1,
            status="in_progress",
            start_time=datetime.now(),
            completion_time=None,
            progress=progress,
            results=None,
            error_message=None
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get crafting status: {str(e)}"
        )

@router.post("/{crafting_id}/complete", response_model=CraftingCompleteResponseSchema)
async def complete_crafting(
    crafting_id: str,
    complete_request: CraftingCompleteSchema,
    service: CraftingService = Depends(get_crafting_service)
):
    """
    Complete a crafting operation.
    
    This endpoint finalizes the crafting process, calculates results,
    awards experience, and returns the crafted items.
    """
    try:
        # Validate crafting operation exists and belongs to character
        if complete_request.crafting_id != crafting_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Crafting ID mismatch"
            )
        
        # TODO: Implement completion logic in CraftingService
        # For now, return mock completion
        from datetime import datetime
        from backend.systems.crafting.schemas import CraftingResultItemSchema
        
        # Mock crafted item
        crafted_item = CraftingResultItemSchema(
            item_id="iron_sword",
            quantity=1,
            quality="good",
            durability=100.0,
            enchantments=[],
            properties={"damage": 25, "weight": 3.5},
            crafted_by=complete_request.character_id,
            crafted_at=datetime.now(),
            recipe_used=uuid.uuid4(),  # TODO: Get from actual operation
            station_used=None
        )
        
        return CraftingCompleteResponseSchema(
            crafting_id=crafting_id,
            success=True,
            status="completed",
            completion_time=datetime.now(),
            total_duration=240,  # 4 minutes
            items_produced=[crafted_item],
            experience_gained={"smithing": 50, "crafting": 25},
            achievements_unlocked=["First Sword"],
            recipes_discovered=[],
            materials_returned={},
            tools_durability={"hammer": 95.0, "anvil": 99.8},
            message="Crafting completed successfully!"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to complete crafting: {str(e)}"
        )

@router.post("/{crafting_id}/cancel", response_model=CraftingCancelResponseSchema)
async def cancel_crafting(
    crafting_id: str,
    cancel_request: CraftingCancelSchema,
    service: CraftingService = Depends(get_crafting_service)
):
    """
    Cancel a crafting operation.
    
    This endpoint stops the crafting process, optionally returns materials,
    and may provide partial results if the operation was partially complete.
    """
    try:
        # Validate crafting operation exists and belongs to character
        if cancel_request.crafting_id != crafting_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Crafting ID mismatch"
            )
        
        # TODO: Implement cancellation logic in CraftingService
        # For now, return mock cancellation
        from datetime import datetime
        
        materials_returned = {}
        if cancel_request.return_materials:
            materials_returned = {"iron_ingot": 2, "wood": 1}
        
        return CraftingCancelResponseSchema(
            crafting_id=crafting_id,
            cancelled=True,
            cancellation_time=datetime.now(),
            materials_returned=materials_returned,
            partial_results=[],  # No partial results in this case
            experience_gained={"crafting": 5},  # Small amount for attempt
            message="Crafting operation cancelled successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel crafting: {str(e)}"
        )

@router.get("/queue/{character_id}", response_model=CraftingQueueResponseSchema)
async def get_crafting_queue(
    character_id: str,
    include_completed: bool = Query(False, description="Include completed operations"),
    include_failed: bool = Query(False, description="Include failed operations"),
    limit: int = Query(20, ge=1, le=100, description="Maximum operations to return"),
    service: CraftingService = Depends(get_crafting_service)
):
    """
    Get the crafting queue for a character.
    
    Returns all active, queued, and optionally completed/failed crafting operations.
    """
    try:
        # TODO: Implement queue retrieval in CraftingService
        # For now, return empty queue
        return CraftingQueueResponseSchema(
            character_id=character_id,
            active_operations=[],
            queued_operations=[],
            completed_operations=[],
            total_active=0,
            total_queued=0,
            estimated_queue_time=0
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get crafting queue: {str(e)}"
        )

@router.post("/batch", response_model=CraftingBatchResponseSchema, status_code=status.HTTP_201_CREATED)
async def start_batch_crafting(
    batch_request: CraftingBatchSchema,
    service: CraftingService = Depends(get_crafting_service)
):
    """
    Start a batch crafting operation.
    
    This endpoint allows crafting multiple recipes in sequence or parallel,
    with automatic resource management and optimization.
    """
    try:
        # TODO: Implement batch crafting in CraftingService
        # For now, return mock batch
        from datetime import datetime
        
        batch_id = f"batch_{batch_request.character_id}_{uuid.uuid4().hex[:8]}"
        
        # Mock individual operations
        operations = []
        total_time = 0
        
        for i, recipe_request in enumerate(batch_request.recipes):
            operation = CraftingStartResponseSchema(
                crafting_id=f"{batch_id}_op_{i}",
                recipe_id=recipe_request.recipe_id,
                character_id=recipe_request.character_id,
                station_id=recipe_request.station_id,
                quantity=recipe_request.quantity,
                status="pending",
                start_time=datetime.now(),
                estimated_completion=datetime.now(),
                estimated_duration=300,  # 5 minutes per operation
                efficiency_multiplier=1.0,
                quality_bonus=0.0,
                experience_multiplier=1.0,
                ingredients_consumed=recipe_request.ingredients,
                tools_used=recipe_request.tools
            )
            operations.append(operation)
            total_time += 300
        
        return CraftingBatchResponseSchema(
            batch_id=batch_id,
            character_id=batch_request.character_id,
            crafting_operations=operations,
            total_operations=len(operations),
            estimated_total_time=total_time,
            sequential=batch_request.sequential,
            status="pending",
            created_at=datetime.now()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start batch crafting: {str(e)}"
        )

@router.get("/recipes", response_model=RecipeListResponseSchema)
async def get_available_recipes(
    character_id: str = Query(..., description="Character ID"),
    skill_filter: Optional[str] = Query(None, description="Filter by skill type"),
    station_filter: Optional[str] = Query(None, description="Filter by station type"),
    craftable_only: bool = Query(False, description="Show only craftable recipes"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    repository: RecipeRepository = Depends(get_recipe_repository)
):
    """
    Get recipes available for crafting by a character.
    
    This is a convenience endpoint that filters recipes based on character
    skills, available stations, and other criteria.
    """
    try:
        # Calculate offset
        offset = (page - 1) * per_page
        
        # Get recipes based on filters
        if skill_filter:
            recipes = repository.get_recipes_by_skill(skill_filter)
        elif station_filter:
            recipes = repository.get_recipes_by_station(station_filter)
        else:
            recipes = repository.get_all(limit=per_page, offset=offset)
        
        # Filter by craftability if requested
        if craftable_only:
            # TODO: Implement craftability check based on character skills/inventory
            pass
        
        # Apply pagination
        total = len(recipes)
        paginated_recipes = recipes[offset:offset + per_page]
        
        # Convert to response schemas
        from backend.systems.crafting.schemas import RecipeResponseSchema
        recipe_responses = [
            RecipeResponseSchema.from_orm(recipe) for recipe in paginated_recipes
        ]
        
        return RecipeListResponseSchema(
            recipes=recipe_responses,
            total=total,
            page=page,
            per_page=per_page
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get available recipes: {str(e)}"
        ) 
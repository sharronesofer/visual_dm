"""
Recipe Router

FastAPI router for recipe management endpoints.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, status
from fastapi.responses import JSONResponse
import uuid

from backend.systems.crafting.schemas import (
    RecipeResponseSchema,
    RecipeListResponseSchema,
    RecipeSearchSchema,
    RecipeDiscoverySchema,
    RecipeDiscoveryResponseSchema,
    CraftabilityCheckSchema,
    CraftabilityResponseSchema,
    RecipeCreateSchema,
    RecipeUpdateSchema
)
from backend.systems.crafting.repositories import RecipeRepository
from backend.systems.crafting.services import CraftingService

router = APIRouter(prefix="/recipes", tags=["recipes"])

# Dependency to get recipe repository
def get_recipe_repository() -> RecipeRepository:
    """Get recipe repository instance."""
    return RecipeRepository()

# Dependency to get crafting service
def get_crafting_service() -> CraftingService:
    """Get crafting service instance."""
    return CraftingService()

@router.get("/", response_model=RecipeListResponseSchema)
async def list_recipes(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    skill_type: Optional[str] = Query(None, description="Filter by skill type"),
    station_type: Optional[str] = Query(None, description="Filter by station type"),
    include_hidden: bool = Query(False, description="Include hidden recipes"),
    repository: RecipeRepository = Depends(get_recipe_repository)
):
    """
    List all recipes with optional filtering and pagination.
    
    Returns a paginated list of recipes that can be filtered by various criteria.
    """
    try:
        # Calculate offset
        offset = (page - 1) * per_page
        
        # Get recipes based on filters
        if skill_type:
            recipes = repository.get_recipes_by_skill(skill_type)
        elif station_type:
            recipes = repository.get_recipes_by_station(station_type)
        else:
            recipes = repository.get_all(limit=per_page, offset=offset)
        
        # Filter out hidden recipes if not requested
        if not include_hidden:
            recipes = [r for r in recipes if not r.is_hidden]
        
        # Apply pagination to filtered results
        total = len(recipes)
        paginated_recipes = recipes[offset:offset + per_page]
        
        # Convert to response schemas
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
            detail=f"Failed to retrieve recipes: {str(e)}"
        )

@router.get("/{recipe_id}", response_model=RecipeResponseSchema)
async def get_recipe(
    recipe_id: uuid.UUID,
    repository: RecipeRepository = Depends(get_recipe_repository)
):
    """
    Get detailed information about a specific recipe.
    
    Returns complete recipe details including ingredients and results.
    """
    try:
        recipe = repository.get_with_ingredients_and_results(str(recipe_id))
        
        if not recipe:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Recipe with ID {recipe_id} not found"
            )
        
        return RecipeResponseSchema.from_orm(recipe)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve recipe: {str(e)}"
        )

@router.post("/search", response_model=RecipeListResponseSchema)
async def search_recipes(
    search_request: RecipeSearchSchema,
    repository: RecipeRepository = Depends(get_recipe_repository)
):
    """
    Search recipes based on various criteria.
    
    Supports searching by name, description, ingredients, results, and other filters.
    """
    try:
        recipes = []
        
        # Search by term if provided
        if search_request.search_term:
            recipes = repository.search_recipes(
                search_request.search_term,
                limit=search_request.per_page * 2  # Get more to account for filtering
            )
        else:
            # Get all recipes for filtering
            recipes = repository.get_all()
        
        # Apply filters
        if search_request.skill_type:
            skill_recipes = repository.get_recipes_by_skill(
                search_request.skill_type,
                search_request.max_skill_level
            )
            recipes = [r for r in recipes if r in skill_recipes]
        
        if search_request.station_type:
            station_recipes = repository.get_recipes_by_station(search_request.station_type)
            recipes = [r for r in recipes if r in station_recipes]
        
        if search_request.ingredient_id:
            ingredient_recipes = repository.get_recipes_requiring_ingredient(search_request.ingredient_id)
            recipes = [r for r in recipes if r in ingredient_recipes]
        
        if search_request.result_id:
            result_recipes = repository.get_recipes_producing_item(search_request.result_id)
            recipes = [r for r in recipes if r in result_recipes]
        
        # Filter hidden recipes
        if not search_request.include_hidden:
            recipes = [r for r in recipes if not r.is_hidden]
        
        # Apply pagination
        total = len(recipes)
        offset = (search_request.page - 1) * search_request.per_page
        paginated_recipes = recipes[offset:offset + search_request.per_page]
        
        # Convert to response schemas
        recipe_responses = [
            RecipeResponseSchema.from_orm(recipe) for recipe in paginated_recipes
        ]
        
        return RecipeListResponseSchema(
            recipes=recipe_responses,
            total=total,
            page=search_request.page,
            per_page=search_request.per_page
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search recipes: {str(e)}"
        )

@router.post("/discover", response_model=RecipeDiscoveryResponseSchema)
async def discover_recipes(
    discovery_request: RecipeDiscoverySchema,
    service: CraftingService = Depends(get_crafting_service)
):
    """
    Discover new recipes based on character actions and context.
    
    This endpoint handles recipe discovery through various methods like experimentation,
    learning from NPCs, finding recipe books, etc.
    """
    try:
        # TODO: Implement recipe discovery logic in CraftingService
        # For now, return empty discovery
        return RecipeDiscoveryResponseSchema(
            discovered_recipes=[],
            total_discovered=0,
            experience_gained=0
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to discover recipes: {str(e)}"
        )

@router.post("/check-craftability", response_model=List[CraftabilityResponseSchema])
async def check_recipe_craftability(
    craftability_request: CraftabilityCheckSchema,
    repository: RecipeRepository = Depends(get_recipe_repository)
):
    """
    Check which recipes can be crafted with current character skills and available stations.
    
    Returns craftability status for all recipes or specific recipes.
    """
    try:
        # Get craftable recipes
        craftable_recipes = repository.get_craftable_recipes(
            craftability_request.character_skills,
            craftability_request.available_stations
        )
        
        # Build response for each recipe
        responses = []
        for recipe in craftable_recipes:
            missing_requirements = []
            
            # Check skill requirements
            if recipe.skill_required:
                if recipe.skill_required not in craftability_request.character_skills:
                    missing_requirements.append(f"Skill: {recipe.skill_required}")
                elif craftability_request.character_skills[recipe.skill_required] < recipe.min_skill_level:
                    missing_requirements.append(
                        f"Skill level: {recipe.skill_required} level {recipe.min_skill_level}"
                    )
            
            # Check station requirements
            if recipe.station_required and recipe.station_required not in craftability_request.available_stations:
                missing_requirements.append(f"Station: {recipe.station_required}")
            
            # Get required ingredients
            required_ingredients = recipe.get_required_ingredients()
            
            response = CraftabilityResponseSchema(
                recipe_id=recipe.id,
                is_craftable=len(missing_requirements) == 0,
                missing_requirements=missing_requirements,
                required_ingredients=required_ingredients,
                estimated_time=recipe.crafting_time,
                estimated_experience=recipe.base_experience
            )
            responses.append(response)
        
        return responses
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to check recipe craftability: {str(e)}"
        )

@router.post("/", response_model=RecipeResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_recipe(
    recipe_data: RecipeCreateSchema,
    repository: RecipeRepository = Depends(get_recipe_repository)
):
    """
    Create a new recipe.
    
    This endpoint is typically used by administrators or through recipe discovery systems.
    """
    try:
        # Convert schema to dict for repository
        recipe_dict = recipe_data.dict()
        
        # Create the recipe
        recipe = repository.create(**recipe_dict)
        
        # Add ingredients and results
        for ingredient_data in recipe_data.ingredients:
            recipe.add_ingredient(**ingredient_data.dict())
        
        for result_data in recipe_data.results:
            recipe.add_result(**result_data.dict())
        
        # Get the complete recipe with relationships
        complete_recipe = repository.get_with_ingredients_and_results(str(recipe.id))
        
        return RecipeResponseSchema.from_orm(complete_recipe)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create recipe: {str(e)}"
        )

@router.put("/{recipe_id}", response_model=RecipeResponseSchema)
async def update_recipe(
    recipe_id: uuid.UUID,
    recipe_data: RecipeUpdateSchema,
    repository: RecipeRepository = Depends(get_recipe_repository)
):
    """
    Update an existing recipe.
    
    Only provided fields will be updated, others remain unchanged.
    """
    try:
        # Check if recipe exists
        existing_recipe = repository.get_by_id(str(recipe_id))
        if not existing_recipe:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Recipe with ID {recipe_id} not found"
            )
        
        # Update only provided fields
        update_data = recipe_data.dict(exclude_unset=True)
        updated_recipe = repository.update(str(recipe_id), **update_data)
        
        return RecipeResponseSchema.from_orm(updated_recipe)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update recipe: {str(e)}"
        )

@router.delete("/{recipe_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_recipe(
    recipe_id: uuid.UUID,
    repository: RecipeRepository = Depends(get_recipe_repository)
):
    """
    Delete a recipe.
    
    This will also delete all associated ingredients and results.
    """
    try:
        success = repository.delete(str(recipe_id))
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Recipe with ID {recipe_id} not found"
            )
        
        return JSONResponse(
            status_code=status.HTTP_204_NO_CONTENT,
            content=None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete recipe: {str(e)}"
        ) 
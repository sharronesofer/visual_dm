"""
Recipe Schemas

Pydantic models for recipe-related API requests and responses.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
import uuid

class IngredientSchema(BaseModel):
    """Schema for recipe ingredients."""
    item_id: str = Field(..., description="ID of the required item")
    quantity: int = Field(ge=1, description="Quantity required")
    is_consumed: bool = Field(default=True, description="Whether the ingredient is consumed")
    is_tool: bool = Field(default=False, description="Whether this is a tool requirement")
    substitution_groups: Dict[str, Any] = Field(default_factory=dict, description="Alternative ingredients")
    quality_requirement: Optional[str] = Field(None, description="Minimum quality required")

class ResultSchema(BaseModel):
    """Schema for recipe results."""
    item_id: str = Field(..., description="ID of the produced item")
    quantity: int = Field(ge=1, description="Quantity produced")
    probability: float = Field(ge=0.0, le=1.0, description="Probability of getting this result")
    quality_range: Dict[str, Any] = Field(default_factory=dict, description="Quality range configuration")
    bonus_conditions: Dict[str, Any] = Field(default_factory=dict, description="Conditions for bonus results")

class RecipeBaseSchema(BaseModel):
    """Base schema for recipes."""
    name: str = Field(..., min_length=1, max_length=255, description="Recipe name")
    description: str = Field(default="", description="Recipe description")
    skill_required: Optional[str] = Field(None, description="Required skill type")
    min_skill_level: int = Field(ge=1, le=100, default=1, description="Minimum skill level")
    crafting_time: int = Field(ge=0, default=0, description="Crafting time in seconds")
    base_experience: int = Field(ge=0, default=10, description="Base experience gained")
    station_required: Optional[str] = Field(None, description="Required station type")
    station_level: int = Field(ge=0, default=0, description="Minimum station level")
    is_hidden: bool = Field(default=False, description="Whether recipe is hidden")
    is_enabled: bool = Field(default=True, description="Whether recipe is enabled")

class RecipeCreateSchema(RecipeBaseSchema):
    """Schema for creating a new recipe."""
    ingredients: List[IngredientSchema] = Field(default_factory=list, description="Recipe ingredients")
    results: List[ResultSchema] = Field(default_factory=list, description="Recipe results")
    recipe_metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    discovery_methods: List[str] = Field(default_factory=list, description="How recipe can be discovered")

class RecipeUpdateSchema(BaseModel):
    """Schema for updating a recipe."""
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Recipe name")
    description: Optional[str] = Field(None, description="Recipe description")
    skill_required: Optional[str] = Field(None, description="Required skill type")
    min_skill_level: Optional[int] = Field(None, ge=1, le=100, description="Minimum skill level")
    crafting_time: Optional[int] = Field(None, ge=0, description="Crafting time in seconds")
    base_experience: Optional[int] = Field(None, ge=0, description="Base experience gained")
    station_required: Optional[str] = Field(None, description="Required station type")
    station_level: Optional[int] = Field(None, ge=0, description="Minimum station level")
    is_hidden: Optional[bool] = Field(None, description="Whether recipe is hidden")
    is_enabled: Optional[bool] = Field(None, description="Whether recipe is enabled")

class RecipeResponseSchema(RecipeBaseSchema):
    """Schema for recipe responses."""
    id: uuid.UUID = Field(..., description="Recipe ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    ingredients: List[IngredientSchema] = Field(default_factory=list, description="Recipe ingredients")
    results: List[ResultSchema] = Field(default_factory=list, description="Recipe results")
    recipe_metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    discovery_methods: List[str] = Field(default_factory=list, description="How recipe can be discovered")

    model_config = ConfigDict(from_attributes=True)

class RecipeListResponseSchema(BaseModel):
    """Schema for recipe list responses."""
    recipes: List[RecipeResponseSchema] = Field(..., description="List of recipes")
    total: int = Field(..., description="Total number of recipes")
    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Items per page")

class RecipeSearchSchema(BaseModel):
    """Schema for recipe search requests."""
    search_term: Optional[str] = Field(None, description="Search term for name/description")
    skill_type: Optional[str] = Field(None, description="Filter by skill type")
    max_skill_level: Optional[int] = Field(None, ge=1, le=100, description="Maximum skill level")
    station_type: Optional[str] = Field(None, description="Filter by station type")
    ingredient_id: Optional[str] = Field(None, description="Filter by required ingredient")
    result_id: Optional[str] = Field(None, description="Filter by produced item")
    is_craftable: Optional[bool] = Field(None, description="Filter by craftability")
    include_hidden: bool = Field(default=False, description="Include hidden recipes")
    page: int = Field(ge=1, default=1, description="Page number")
    per_page: int = Field(ge=1, le=100, default=20, description="Items per page")

class RecipeDiscoverySchema(BaseModel):
    """Schema for recipe discovery requests."""
    character_id: str = Field(..., description="Character ID")
    discovery_method: str = Field(..., description="Method of discovery")
    context: Dict[str, Any] = Field(default_factory=dict, description="Discovery context")

class RecipeDiscoveryResponseSchema(BaseModel):
    """Schema for recipe discovery responses."""
    discovered_recipes: List[RecipeResponseSchema] = Field(..., description="Newly discovered recipes")
    total_discovered: int = Field(..., description="Total recipes discovered")
    experience_gained: int = Field(default=0, description="Experience gained from discovery")

class CraftabilityCheckSchema(BaseModel):
    """Schema for checking recipe craftability."""
    character_id: str = Field(..., description="Character ID")
    available_stations: List[str] = Field(default_factory=list, description="Available station types")
    character_skills: Dict[str, int] = Field(default_factory=dict, description="Character skill levels")

class CraftabilityResponseSchema(BaseModel):
    """Schema for craftability check responses."""
    recipe_id: uuid.UUID = Field(..., description="Recipe ID")
    is_craftable: bool = Field(..., description="Whether recipe can be crafted")
    missing_requirements: List[str] = Field(default_factory=list, description="Missing requirements")
    required_ingredients: List[IngredientSchema] = Field(default_factory=list, description="Required ingredients")
    estimated_time: int = Field(default=0, description="Estimated crafting time in seconds")
    estimated_experience: int = Field(default=0, description="Estimated experience gain") 
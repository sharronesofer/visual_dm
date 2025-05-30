"""
Crafting System Module

This module provides the crafting system functionality for the game.
"""
from backend.systems.crafting.models.recipe import CraftingRecipe
from backend.systems.crafting.models.ingredient import CraftingIngredient
from backend.systems.crafting.models.result import CraftingResult
from backend.systems.crafting.models.station import CraftingStation
from backend.systems.crafting.services.crafting_service import CraftingService

# Create a singleton instance of the crafting service
_crafting_service = None

def get_crafting_service() -> CraftingService:
    """
    Get the singleton instance of the crafting service.
    
    Returns:
        CraftingService: The crafting service instance
    """
    global _crafting_service
    if _crafting_service is None:
        _crafting_service = CraftingService()
    return _crafting_service

# API functions that expose crafting functionality

def craft(character_id: str, recipe_id: str, inventory_id: str, station_id=None, skills=None):
    """
    Craft an item using a recipe.
    
    Args:
        character_id: The ID of the character doing the crafting
        recipe_id: The ID of the recipe to craft
        inventory_id: The ID of the inventory to use for ingredients and results
        station_id: The ID of the crafting station to use (if required)
        skills: Dictionary of skill names to levels
        
    Returns:
        Dict: Result of the crafting operation
    """
    service = get_crafting_service()
    return service.craft(character_id, recipe_id, inventory_id, station_id, skills)

def get_available_recipes(character_id: str, skills=None):
    """
    Get recipes available to a character based on their skills.
    
    Args:
        character_id: The ID of the character
        skills: Dictionary of skill names to levels
        
    Returns:
        List[Dict]: List of available recipes
    """
    service = get_crafting_service()
    return service.get_available_recipes(character_id, skills)

def can_craft(character_id: str, recipe_id: str, inventory_id: str, station_id=None, skills=None):
    """
    Check if a character can craft a recipe.
    
    Args:
        character_id: The ID of the character
        recipe_id: The ID of the recipe to craft
        inventory_id: The ID of the inventory to use for ingredients
        station_id: The ID of the crafting station to use (if required)
        skills: Dictionary of skill names to levels
        
    Returns:
        Tuple[bool, str]: Whether the character can craft the recipe and reason if not
    """
    service = get_crafting_service()
    return service.can_craft(character_id, recipe_id, inventory_id, station_id, skills)

def learn_recipe(character_id: str, recipe_id: str):
    """
    Learn a recipe.
    
    Args:
        character_id: The ID of the character
        recipe_id: The ID of the recipe to learn
        
    Returns:
        Tuple[bool, str]: Whether the recipe was learned and message
    """
    service = get_crafting_service()
    return service.learn_recipe(character_id, recipe_id)

def discover_recipe(character_id: str, discovery_method: str, context_data=None):
    """
    Discover a new recipe through various means.
    
    Args:
        character_id: The ID of the character
        discovery_method: How the recipe was discovered (e.g., "exploration", "quest")
        context_data: Additional context for discovery
        
    Returns:
        Tuple[bool, str, str]: Success, message, and discovered recipe ID if successful
    """
    service = get_crafting_service()
    return service.discover_recipe(character_id, discovery_method, context_data)

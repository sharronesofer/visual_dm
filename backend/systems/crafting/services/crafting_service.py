"""
Crafting Service Module

Provides crafting system functionality for the game.
"""

from typing import Dict, List, Optional, Any, Tuple, Union
import random
import logging
from datetime import datetime
import os
import json
from pathlib import Path
import time
from backend.systems.crafting.models.recipe import CraftingRecipe
from backend.systems.crafting.models.ingredient import CraftingIngredient
from backend.systems.crafting.models.result import CraftingResult
from backend.systems.crafting.models.station import CraftingStation

# Optional imports to avoid circular dependencies
try:
    from backend.systems.inventory.models import Inventory, InventoryItem
from backend.systems.inventory.repositories import InventoryItemRepository
    INVENTORY_AVAILABLE = True
except ImportError:
    INVENTORY_AVAILABLE = False

try:
    from backend.infrastructure.database import db
    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False

try:
    from backend.infrastructure.events.event_dispatcher import EventDispatcher
    EVENTS_AVAILABLE = True
except ImportError:
    EVENTS_AVAILABLE = False

class CraftingService:
    """
    Service for managing crafting operations.
    
    Handles recipe lookup, crafting validation, crafting execution,
    and integration with inventory and character systems.
    """
    
    def __init__(self):
        """Initialize the crafting service."""
        # These will be set up when the corresponding systems are available
        self._recipes = {}  # Dictionary of recipe_id -> CraftingRecipe
        self._stations = {}  # Dictionary of station_id -> CraftingStation
        
        # Optional event dispatcher
        if EVENTS_AVAILABLE:
            try:
                self._event_dispatcher = EventDispatcher.get_instance()
            except Exception:
                self._event_dispatcher = None
        else:
            self._event_dispatcher = None
            
        self._logger = logging.getLogger(__name__)
        
        # Character knowledge tracking
        self._known_recipes = {}  # Dictionary of character_id -> set of recipe_ids
        
        # Load recipes and stations on initialization
        self._load_recipes()
        self._load_stations()
    
    # Recipe and Station Loading Methods
    
    def _load_recipes(self) -> None:
        """
        Load recipes from data files.
        """
        recipe_dir = Path(os.environ.get("RECIPE_DIR", "data/recipes"))
        
        if not recipe_dir.exists():
            self._logger.warning(f"Recipe directory not found: {recipe_dir}")
            return
            
        for recipe_file in recipe_dir.glob("*.json"):
            try:
                with open(recipe_file, "r") as f:
                    recipe_data = json.load(f)
                    
                for recipe_id, recipe_info in recipe_data.items():
                    recipe = self._construct_recipe(recipe_id, recipe_info)
                    if recipe:
                        self._recipes[recipe_id] = recipe
                        
            except Exception as e:
                self._logger.error(f"Error loading recipe file {recipe_file}: {str(e)}")
                
        self._logger.info(f"Loaded {len(self._recipes)} recipes")
    
    def _load_stations(self) -> None:
        """
        Load crafting stations from data files.
        """
        station_dir = Path(os.environ.get("STATION_DIR", "data/stations"))
        
        if not station_dir.exists():
            self._logger.warning(f"Station directory not found: {station_dir}")
            return
            
        for station_file in station_dir.glob("*.json"):
            try:
                with open(station_file, "r") as f:
                    station_data = json.load(f)
                    
                for station_id, station_info in station_data.items():
                    station = self._construct_station(station_id, station_info)
                    if station:
                        self._stations[station_id] = station
                        
            except Exception as e:
                self._logger.error(f"Error loading station file {station_file}: {str(e)}")
                
        self._logger.info(f"Loaded {len(self._stations)} crafting stations")
    
    def _construct_recipe(self, recipe_id: str, recipe_info: Dict[str, Any]) -> Optional[CraftingRecipe]:
        """
        Construct a CraftingRecipe object from recipe data.
        
        Args:
            recipe_id: The ID of the recipe
            recipe_info: The recipe data
            
        Returns:
            CraftingRecipe or None if invalid data
        """
        try:
            # Required fields
            name = recipe_info.get("name", recipe_id)
            description = recipe_info.get("description", "")
            
            # Skill requirements
            skill_required = recipe_info.get("skill_required")
            min_skill_level = recipe_info.get("min_skill_level", 0)
            
            # Station requirements
            station_required = recipe_info.get("station_required")
            station_level = recipe_info.get("station_level", 0)
            
            # Ingredient construction
            ingredients = []
            for ing_data in recipe_info.get("ingredients", []):
                ingredient = CraftingIngredient(
                    item_id=ing_data["item_id"],
                    quantity=ing_data["quantity"],
                    is_consumed=ing_data.get("is_consumed", True)
                )
                
                # Add substitution groups if present
                if "substitution_groups" in ing_data:
                    ingredient.substitution_groups = ing_data["substitution_groups"]
                    
                ingredients.append(ingredient)
                
            # Result construction
            results = []
            for res_data in recipe_info.get("results", []):
                result = CraftingResult(
                    item_id=res_data["item_id"],
                    quantity=res_data["quantity"],
                    probability=res_data.get("probability", 1.0)
                )
                results.append(result)
                
            # Recipe visibility and discoverability
            is_hidden = recipe_info.get("is_hidden", False)
            is_enabled = recipe_info.get("is_enabled", True)
            discovery_methods = recipe_info.get("discovery_methods", [])
            
            # Create the recipe object
            recipe = CraftingRecipe(
                id=recipe_id,
                name=name,
                description=description,
                skill_required=skill_required,
                min_skill_level=min_skill_level,
                station_required=station_required,
                station_level=station_level,
                ingredients=ingredients,
                results=results,
                is_hidden=is_hidden,
                is_enabled=is_enabled
            )
            
            # Add metadata
            recipe.metadata = recipe_info.get("metadata", {})
            recipe.discovery_methods = discovery_methods
            
            return recipe
            
        except Exception as e:
            self._logger.error(f"Error constructing recipe {recipe_id}: {str(e)}")
            return None
    
    def _construct_station(self, station_id: str, station_info: Dict[str, Any]) -> Optional[CraftingStation]:
        """
        Construct a CraftingStation object from station data.
        
        Args:
            station_id: The ID of the station
            station_info: The station data
            
        Returns:
            CraftingStation or None if invalid data
        """
        try:
            # Required fields
            name = station_info.get("name", station_id)
            description = station_info.get("description", "")
            station_type = station_info.get("type", "basic")
            level = station_info.get("level", 1)
            
            # Create the station object
            station = CraftingStation(
                id=station_id,
                name=name,
                description=description,
                station_type=station_type,
                level=level
            )
            
            # Add metadata
            station.metadata = station_info.get("metadata", {})
            
            return station
            
        except Exception as e:
            self._logger.error(f"Error constructing station {station_id}: {str(e)}")
            return None
    
    # Recipe Management Methods
    
    def add_recipe(self, recipe: CraftingRecipe) -> None:
        """
        Add a recipe to the system.
        
        Args:
            recipe: The recipe to add
        """
        self._recipes[recipe.id] = recipe
        self._logger.info(f"Added recipe: {recipe.id}")
        
    def remove_recipe(self, recipe_id: str) -> bool:
        """
        Remove a recipe from the system.
        
        Args:
            recipe_id: The ID of the recipe to remove
            
        Returns:
            bool: True if removed, False if not found
        """
        if recipe_id in self._recipes:
            del self._recipes[recipe_id]
            self._logger.info(f"Removed recipe: {recipe_id}")
            return True
        return False
        
    def get_recipe(self, recipe_id: str) -> Optional[CraftingRecipe]:
        """
        Get a recipe by ID.
        
        Args:
            recipe_id: The ID of the recipe
            
        Returns:
            CraftingRecipe or None if not found
        """
        return self._recipes.get(recipe_id)
        
    def get_all_recipes(self) -> Dict[str, CraftingRecipe]:
        """
        Get all recipes.
        
        Returns:
            Dict[str, CraftingRecipe]: Dictionary of recipe_id -> CraftingRecipe
        """
        return self._recipes.copy()
        
    def get_available_recipes(self, character_id: str, skills: Dict[str, int] = None) -> Dict[str, CraftingRecipe]:
        """
        Get recipes available to a character based on their known recipes and skills.
        
        Args:
            character_id: The ID of the character
            skills: Dictionary of skill names to levels
            
        Returns:
            Dict[str, CraftingRecipe]: Dictionary of recipe_id -> CraftingRecipe
        """
        result = {}
        
        for recipe_id, recipe in self._recipes.items():
            # Skip disabled recipes
            if not recipe.is_enabled:
                continue
                
            # Skip hidden recipes not known to the character
            if recipe.is_hidden and not self._is_recipe_known(character_id, recipe_id):
                continue
                
            # Include recipe if it's visible or known
            result[recipe_id] = recipe
            
        return result
    
    # Character Recipe Knowledge Methods
    
    def _is_recipe_known(self, character_id: str, recipe_id: str) -> bool:
        """
        Check if a character knows a recipe.
        
        Args:
            character_id: The ID of the character
            recipe_id: The ID of the recipe
            
        Returns:
            bool: True if known, False otherwise
        """
        if character_id not in self._known_recipes:
            return False
            
        return recipe_id in self._known_recipes[character_id]
        
    def _discover_recipe(self, character_id: str, discovery_method: str, context: Dict[str, Any] = None) -> List[str]:
        """
        Discover recipes based on a specific method.
        
        Args:
            character_id: The ID of the character
            discovery_method: The method of discovery (e.g., "item_found", "location_visited")
            context: Additional context for the discovery
            
        Returns:
            List[str]: List of discovered recipe IDs
        """
        discovered = []
        context = context or {}
        
        for recipe_id, recipe in self._recipes.items():
            # Skip if recipe is not hidden or already known
            if not recipe.is_hidden or self._is_recipe_known(character_id, recipe_id):
                continue
                
            # Check if this discovery method applies to this recipe
            if discovery_method in recipe.discovery_methods:
                # Check if context matches any required conditions
                conditions_met = True
                
                if "discovery_conditions" in recipe.metadata:
                    conditions = recipe.metadata["discovery_conditions"].get(discovery_method, {})
                    
                    for condition_key, condition_value in conditions.items():
                        if condition_key not in context or context[condition_key] != condition_value:
                            conditions_met = False
                            break
                
                if conditions_met:
                    # Add recipe to known recipes
                    if character_id not in self._known_recipes:
                        self._known_recipes[character_id] = set()
                        
                    self._known_recipes[character_id].add(recipe_id)
                    discovered.append(recipe_id)
                    
                    # Emit recipe discovered event
                    self._emit_recipe_discovered_event(character_id, recipe_id, discovery_method)
        
        return discovered
        
    def get_known_recipes(self, character_id: str) -> List[str]:
        """
        Get recipes known to a character.
        
        Args:
            character_id: The ID of the character
            
        Returns:
            List[str]: List of known recipe IDs
        """
        if character_id not in self._known_recipes:
            return []
            
        return list(self._known_recipes[character_id])
        
    def save_recipe_knowledge(self, file_path: Path = None) -> bool:
        """
        Save character recipe knowledge to a file.
        
        Args:
            file_path: Path to save file (default: data/system/runtime/character_recipes.json)
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not file_path:
            file_path = Path("data/system/runtime/character_recipes.json")
            
        try:
            # Convert sets to lists for JSON serialization
            save_data = {
                character_id: list(recipes)
                for character_id, recipes in self._known_recipes.items()
            }
            
            # Create parent directory if it doesn't exist
            os.makedirs(file_path.parent, exist_ok=True)
            
            with open(file_path, "w") as f:
                json.dump(save_data, f, indent=2)
                
            self._logger.info(f"Saved character recipe knowledge to {file_path}")
            return True
            
        except Exception as e:
            self._logger.error(f"Error saving character recipe knowledge: {str(e)}")
            return False
            
    def load_recipe_knowledge(self, file_path: Path = None) -> bool:
        """
        Load character recipe knowledge from a file.
        
        Args:
            file_path: Path to load file (default: data/system/runtime/character_recipes.json)
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not file_path:
            file_path = Path("data/system/runtime/character_recipes.json")
            
        if not file_path.exists():
            self._logger.warning(f"Character recipe knowledge file not found: {file_path}")
            return False
            
        try:
            with open(file_path, "r") as f:
                load_data = json.load(f)
                
            # Convert lists back to sets
            self._known_recipes = {
                character_id: set(recipes)
                for character_id, recipes in load_data.items()
            }
            
            self._logger.info(f"Loaded character recipe knowledge from {file_path}")
            return True
            
        except Exception as e:
            self._logger.error(f"Error loading character recipe knowledge: {str(e)}")
            return False
            
    # Event Emission Methods
    
    def _emit_recipe_discovered_event(self, character_id: str, recipe_id: str, discovery_method: str) -> None:
        """
        Emit a recipe discovered event.
        
        Args:
            character_id: The ID of the character
            recipe_id: The ID of the recipe
            discovery_method: How the recipe was discovered
        """
        if self._event_dispatcher:
            recipe = self._recipes.get(recipe_id)
            
            event_data = {
                "character_id": character_id,
                "recipe_id": recipe_id,
                "recipe_name": recipe.name if recipe else "Unknown Recipe",
                "discovery_method": discovery_method,
                "timestamp": time.time()
            }
            
            self._event_dispatcher.dispatch("crafting.recipe_discovered", event_data)
    
    # Recipe Management Methods
    
    def get_recipes_for_character(
        self, 
        character_id: str, 
        skills: Dict[str, int] = None
    ) -> List[dict]:
        """
        Get all recipes available to a character based on their skills.
        
        Args:
            character_id: The ID of the character
            skills: Dictionary of skill names to levels
            
        Returns:
            List[dict]: List of available recipes
        """
        skills = skills or {}
        available_recipes = []
        
        for recipe_id, recipe in self._recipes.items():
            if self._is_recipe_available_to_character(recipe, skills):
                available_recipes.append(self.get_recipe(recipe_id))
            
        return available_recipes
    
    def _is_recipe_available_to_character(self, recipe, skills: Dict[str, int]) -> bool:
        """
        Check if a recipe is available to a character based on skills and visibility.
        
        Args:
            recipe: The recipe object
            skills: Dictionary of skill names to levels
            
        Returns:
            bool: True if the recipe is available, False otherwise
        """
        # Skip hidden recipes
        if recipe.is_hidden:
            return False
                
        # Skip disabled recipes
        if not recipe.is_enabled:
            return False
                
        # If the recipe requires a skill, check if the character has it
        if recipe.skill_required and recipe.skill_required in skills:
            if skills[recipe.skill_required] < recipe.min_skill_level:
                return False
        elif recipe.skill_required:
            # If the character doesn't have the required skill, skip
            return False
                
        return True
    
    # Crafting Validation Methods
    
    def can_craft(
        self, 
        character_id: str, 
        recipe_id: str,
        inventory_id: str,
        station_id: Optional[str] = None,
        skills: Dict[str, int] = None
    ) -> Tuple[bool, str]:
        """
        Check if a character can craft a recipe.
        
        Args:
            character_id: The ID of the character
            recipe_id: The ID of the recipe
            inventory_id: The ID of the inventory to use
            station_id: The ID of the crafting station to use (if required)
            skills: Dictionary of skill names to levels
            
        Returns:
            Tuple[bool, str]: (Can craft, reason if can't)
        """
        # Check if recipe exists
        if recipe_id not in self._recipes:
            return False, f"Recipe {recipe_id} does not exist"
            
        recipe = self._recipes[recipe_id]
        
        # Check if recipe is known to the character
        if not self._is_recipe_known(character_id, recipe_id):
            return False, f"Character does not know recipe {recipe_id}"
            
        # Check skill requirements
        skill_check_result = self._check_skill_requirements(recipe, skills)
        if not skill_check_result[0]:
            return skill_check_result
            
        # Check station requirements
        station_check_result = self._check_station_requirements(recipe, station_id)
        if not station_check_result[0]:
            return station_check_result
            
        # Check inventory for required ingredients
        inventory_check_result = self._validate_inventory(recipe, inventory_id)
        if not inventory_check_result[0]:
            return inventory_check_result
            
        return True, "Can craft recipe"
    
    def _check_station_requirements(
        self, 
        recipe: CraftingRecipe, 
        station_id: Optional[str]
    ) -> Tuple[bool, str]:
        """
        Check if the provided station meets the recipe requirements.
        
        Args:
            recipe: The recipe to check
            station_id: The ID of the crafting station to use
            
        Returns:
            Tuple[bool, str]: (Meets requirements, reason if not)
        """
        # If recipe doesn't require a station
        if not recipe.station_required:
            return True, "No station required"
            
        # If recipe requires a station but none provided
        if not station_id:
            return False, f"Recipe requires a crafting station of type: {recipe.station_required}"
            
        # Check if station exists
        if station_id not in self._stations:
            return False, f"Crafting station {station_id} does not exist"
            
        station = self._stations[station_id]
        
        # Check if station is of the required type
        if station.station_type != recipe.station_required:
            return False, f"Recipe requires station type {recipe.station_required}, but {station.station_type} was provided"
            
        # Check if station has the required level
        if recipe.station_level and station.level < recipe.station_level:
            return False, f"Recipe requires station level {recipe.station_level}, but station is only level {station.level}"
            
        return True, "Station meets requirements"

    def _validate_inventory(
        self, 
        recipe: CraftingRecipe, 
        inventory_id: str,
        allow_substitutions: bool = True
    ) -> Tuple[bool, str]:
        """
        Validate that the inventory has the required ingredients.
        
        Args:
            recipe: The recipe to validate against
            inventory_id: The ID of the inventory to check
            allow_substitutions: Whether to allow material substitutions
            
        Returns:
            Tuple[bool, str]: (Has ingredients, reason if not)
        """
        # Get inventory items
        inventory_items = InventoryItemRepository.get_items_by_inventory_id(inventory_id)
        
        if not inventory_items:
            return False, "Inventory is empty"
            
        # Convert to dictionary for easier lookup
        inventory_dict = {item.item_id: item.quantity for item in inventory_items}
        
        # Check each ingredient
        missing_ingredients = []
        for ingredient in recipe.ingredients:
            # Check if inventory has the ingredient
            if ingredient.item_id in inventory_dict and inventory_dict[ingredient.item_id] >= ingredient.quantity:
                continue
                
            # If direct match not found or insufficient quantity, check for substitutions
            if allow_substitutions and self._check_substitutions(ingredient, inventory_dict):
                continue
                
            # If we got here, ingredient requirement not met
            required = ingredient.quantity
            available = inventory_dict.get(ingredient.item_id, 0)
            missing_ingredients.append(
                f"{ingredient.item_id} (need {required}, have {available})"
            )
            
        if missing_ingredients:
            return False, f"Missing ingredients: {', '.join(missing_ingredients)}"
            
        return True, "All ingredients available"
        
    def _check_substitutions(
        self, 
        ingredient: CraftingIngredient, 
        inventory_dict: Dict[str, int]
    ) -> bool:
        """
        Check if the inventory has valid substitutions for an ingredient.
        
        Args:
            ingredient: The ingredient to check for substitutions
            inventory_dict: Dictionary of item_id to quantity in inventory
            
        Returns:
            bool: True if substitution is available, False otherwise
        """
        # If no substitution groups defined, no substitution possible
        if not hasattr(ingredient, 'substitution_groups') or not ingredient.substitution_groups:
            return False
            
        # Check each substitution group
        for group in ingredient.substitution_groups:
            # All items in group must be present with sufficient quantities
            group_satisfied = True
            
            for sub_item_id, sub_quantity in group.items():
                # Calculate actual quantity needed (ingredient quantity * substitution ratio)
                needed_quantity = ingredient.quantity * sub_quantity
                
                # Check if inventory has enough
                if sub_item_id not in inventory_dict or inventory_dict[sub_item_id] < needed_quantity:
                    group_satisfied = False
                    break
                    
            # If any group is fully satisfied, return True
            if group_satisfied:
                return True
                
        return False
        
    def _process_ingredients(
        self, 
        recipe: CraftingRecipe, 
        inventory_id: str,
        allow_substitutions: bool = True
    ) -> None:
        """
        Process and consume ingredients from inventory.
        
        Args:
            recipe: The recipe being crafted
            inventory_id: The ID of the inventory to use
            allow_substitutions: Whether to allow material substitutions
        """
        # Get inventory items
        inventory_items = InventoryItemRepository.get_items_by_inventory_id(inventory_id)
        
        # Convert to dictionary for easier lookup
        inventory_dict = {item.item_id: item.quantity for item in inventory_items}
        
        # Process each ingredient
        for ingredient in recipe.ingredients:
            # Try direct consumption first
            if ingredient.item_id in inventory_dict and inventory_dict[ingredient.item_id] >= ingredient.quantity:
                # Remove from inventory
                InventoryItemRepository.remove_item(
                    inventory_id,
                    ingredient.item_id,
                    ingredient.quantity
                )
                continue
                
            # If direct match not available or insufficient, use substitutions
            if allow_substitutions and hasattr(ingredient, 'substitution_groups') and ingredient.substitution_groups:
                for group in ingredient.substitution_groups:
                    # Check if this group can be fully satisfied
                    group_satisfied = True
                    
                    for sub_item_id, sub_quantity in group.items():
                        needed_quantity = ingredient.quantity * sub_quantity
                        if sub_item_id not in inventory_dict or inventory_dict[sub_item_id] < needed_quantity:
                            group_satisfied = False
                            break
                            
                    # If group can be satisfied, consume these items
                    if group_satisfied:
                        for sub_item_id, sub_quantity in group.items():
                            needed_quantity = ingredient.quantity * sub_quantity
                            InventoryItemRepository.remove_item(
                                inventory_id,
                                sub_item_id,
                                needed_quantity
                            )
                        break
    
    def _determine_craft_results(self, recipe, skills: Dict[str, int] = None) -> List[Dict[str, Any]]:
        """
        Determine the results of a crafting operation.
        
        Args:
            recipe: The recipe object
            skills: Optional dictionary of skill names to levels (for quality calculation)
            
        Returns:
            List[Dict[str, Any]]: List of crafting results
        """
        skills = skills or {}
        results = []
        
        # Calculate quality factors
        quality_level, is_critical_success, is_critical_failure = self._calculate_quality_factors(recipe, skills)
        
        # Handle critical failure
        if is_critical_failure:
            # Critical failure might result in no items or damaged items
            if random.random() < 0.7:
                # No items produced
                return []
            else:
                # Damaged version of main item at reduced quantity
                for result in recipe.results:
                    if result.probability >= 0.8:  # Main result item
                        results.append({
                            "item_id": result.item_id,
                            "quantity": max(1, result.quantity // 2),
                            "quality": "DAMAGED",
                            "is_damaged": True
                        })
                return results
        
        # Process each potential result
        for result in recipe.results:
            # Critical success guarantees all items
            success_chance = 1.0 if is_critical_success else result.probability
            
            # Check probability
            if random.random() <= success_chance:
                # Calculate quantity
                quantity = result.quantity
                
                # On critical success, bonus quantity for some items
                if is_critical_success and random.random() < 0.5:
                    quantity += random.randint(1, max(1, quantity // 2))
                
                # Create result with quality
                result_item = {
                    "item_id": result.item_id,
                    "quantity": quantity,
                    "quality": self._quality_level_to_string(quality_level)
                }
                
                # Add quality-specific properties
                if quality_level > 0:  # FINE or better
                    result_item["quality_level"] = quality_level
                    
                    # Add quality modifiers
                    if "quality_modifiers" in recipe.metadata:
                        modifiers = recipe.metadata["quality_modifiers"]
                        if modifiers and isinstance(modifiers, dict):
                            result_item["modifiers"] = {
                                key: value * quality_level 
                                for key, value in modifiers.items()
                            }
                
                results.append(result_item)
        
        return results
    
    def _calculate_quality_factors(self, recipe, skills: Dict[str, int]) -> Tuple[int, bool, bool]:
        """
        Calculate quality level and critical success/failure.
        
        Args:
            recipe: The recipe object
            skills: Dictionary of skill names to levels
            
        Returns:
            Tuple[int, bool, bool]: (Quality level, is critical success, is critical failure)
        """
        # Default values
        quality_level = 0  # 0=normal, 1=fine, 2=superior, 3=masterwork, 4=legendary
        is_critical_success = False
        is_critical_failure = False
        
        # If no skill required, always normal quality
        if not recipe.skill_required:
            return quality_level, is_critical_success, is_critical_failure
            
        # Get skill level or default to 0
        skill_name = recipe.skill_required
        skill_level = skills.get(skill_name, 0)
        
        # Calculate skill difference
        skill_diff = skill_level - recipe.min_skill_level
        
        # Critical failure chance (higher when skill is below requirement)
        failure_chance = 0.0
        if skill_diff < 0:
            failure_chance = min(0.5, abs(skill_diff) * 0.1)  # 10% per level below, max 50%
        elif skill_diff == 0:
            failure_chance = 0.05  # 5% at exact skill level
        else:
            failure_chance = max(0.01, 0.05 - (skill_diff * 0.01))  # Decreases with higher skill, min 1%
            
        # Critical success chance (higher with higher skill)
        success_chance = 0.0
        if skill_diff <= 0:
            success_chance = 0.01  # 1% at or below requirement
        else:
            success_chance = min(0.25, 0.01 + (skill_diff * 0.02))  # 1% + 2% per level, max 25%
            
        # Roll for critical success/failure
        if random.random() < failure_chance:
            is_critical_failure = True
            quality_level = 0
        elif random.random() < success_chance:
            is_critical_success = True
            # Legendary has a small chance with very high skill
            if skill_diff >= 15 and random.random() < 0.1:
                quality_level = 4  # Legendary
            else:
                quality_level = 3  # Masterwork
        else:
            # Normal quality calculation
            if skill_diff <= 0:
                quality_level = 0  # Normal
            elif skill_diff < 5:
                quality_level = 1 if random.random() < 0.3 else 0  # 30% chance of Fine
            elif skill_diff < 10:
                # 60% Fine, 20% Superior, 20% Normal
                roll = random.random()
                quality_level = 2 if roll < 0.2 else (1 if roll < 0.8 else 0)
            else:
                # 50% Fine, 40% Superior, 10% Masterwork
                roll = random.random()
                quality_level = 3 if roll < 0.1 else (2 if roll < 0.5 else 1)
                
        return quality_level, is_critical_success, is_critical_failure
    
    def _quality_level_to_string(self, quality_level: int) -> str:
        """
        Convert quality level to string representation.
        
        Args:
            quality_level: Quality level (0-4)
            
        Returns:
            str: Quality string
        """
        quality_strings = {
            0: "NORMAL",
            1: "FINE",
            2: "SUPERIOR",
            3: "MASTERWORK",
            4: "LEGENDARY"
        }
        return quality_strings.get(quality_level, "NORMAL")
    
    def _process_results(self, results: List[Dict[str, Any]], inventory_id: str) -> None:
        """
        Process the results of a crafting operation.
        
        Args:
            results: List of crafting results
            inventory_id: The ID of the inventory
        """
        for result in results:
            # Add to inventory
            success, error, _ = InventoryItemRepository.add_item_to_inventory(
                inventory_id=inventory_id,
                item_id=result["item_id"],
                quantity=result["quantity"],
                is_equipped=False,
                merge_with_existing=True
            )
            
            if not success:
                raise Exception(f"Failed to add result item to inventory: {error}")
    
    def _emit_crafting_started_event(self, character_id: str, recipe_id: str, inventory_id: str) -> None:
        """
        Emit a crafting started event.
        
        Args:
            character_id: The ID of the character
            recipe_id: The ID of the recipe
            inventory_id: The ID of the inventory
        """
        self._event_dispatcher.publish_sync(
            "CRAFTING_STARTED",
            {
                "character_id": character_id,
                "recipe_id": recipe_id,
                "inventory_id": inventory_id,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    
    def _emit_crafting_completed_event(self, character_id: str, recipe_id: str, results: List[Dict[str, Any]]) -> None:
        """
        Emit a crafting completed event.
        
        Args:
            character_id: The ID of the character
            recipe_id: The ID of the recipe
            results: List of crafting results
        """
        self._event_dispatcher.publish_sync(
            "CRAFTING_COMPLETED",
            {
                "character_id": character_id,
                "recipe_id": recipe_id,
                "results": results,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    
    def _emit_crafting_failed_event(self, character_id: str, recipe_id: str, reason: str) -> None:
        """
        Emit a crafting failed event.
        
        Args:
            character_id: The ID of the character
            recipe_id: The ID of the recipe
            reason: The reason crafting failed
        """
        self._event_dispatcher.publish_sync(
            "CRAFTING_FAILED",
            {
                "character_id": character_id,
                "recipe_id": recipe_id,
                "reason": reason,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    
    def _create_failed_craft_result(self, character_id: str, recipe_id: str, reason: str) -> Dict[str, Any]:
        """
        Create a result object for a failed crafting operation.
        
        Args:
            character_id: The ID of the character
            recipe_id: The ID of the recipe
            reason: The reason crafting failed
            
        Returns:
            Dict[str, Any]: Result object
        """
        return {
            "success": False,
            "message": reason,
            "recipe_id": recipe_id,
            "character_id": character_id
        }
    
    def _create_successful_craft_result(self, character_id: str, recipe_id: str, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Create a result object for a successful crafting operation.
        
        Args:
            character_id: The ID of the character
            recipe_id: The ID of the recipe
            results: List of crafting results
            
        Returns:
            Dict[str, Any]: Result object
        """
        return {
            "success": True,
            "message": "Crafting successful",
            "recipe_id": recipe_id,
            "character_id": character_id,
            "results": results
        }
    
    def _calculate_crafting_experience(self, recipe, results: List[Dict[str, Any]], skills: Dict[str, int]) -> Tuple[Optional[str], int]:
        """
        Calculate experience gained from crafting.
        
        Args:
            recipe: The recipe object
            results: The crafting results
            skills: The character's skills
            
        Returns:
            Tuple[Optional[str], int]: (Skill name, experience points gained)
        """
        # If no skill required, no experience gained
        if not recipe.skill_required:
            return None, 0
            
        # Base experience formula
        base_exp = recipe.metadata.get("base_experience", 10)
        
        # Calculate difficulty modifier
        skill_level = skills.get(recipe.skill_required, 0)
        level_diff = recipe.min_skill_level - skill_level
        difficulty_modifier = 1.0
        
        if level_diff > 0:
            # Crafting above skill level (should be rare due to validation)
            difficulty_modifier = 1.5
        elif level_diff == 0:
            # Crafting at skill level
            difficulty_modifier = 1.2
        elif level_diff > -5:
            # Slightly below skill level
            difficulty_modifier = 1.0
        elif level_diff > -10:
            # Moderately below skill level
            difficulty_modifier = 0.5
        else:
            # Far below skill level
            difficulty_modifier = 0.1
        
        # Calculate result quality modifier (more valuable/rare items give more exp)
        quality_modifier = 1.0
        result_count = len(results)
        
        if result_count > 0:
            # Add bonus for multiple successful results
            quality_modifier += (result_count - 1) * 0.1
            
            # Add bonus for rare results (low probability)
            for result in results:
                item_id = result["item_id"]
                for recipe_result in recipe.results:
                    if recipe_result.item_id == item_id and recipe_result.probability < 1.0:
                        quality_modifier += (1.0 - recipe_result.probability)
        
        # Calculate final experience
        total_exp = int(base_exp * difficulty_modifier * quality_modifier)
        
        # Cap minimum experience at 1
        total_exp = max(1, total_exp)
        
        return recipe.skill_required, total_exp
    
    def _apply_crafting_experience(self, character_id: str, skill_name: str, experience: int) -> None:
        """
        Apply crafting experience to a character's skill.
        
        Args:
            character_id: The ID of the character
            skill_name: The name of the skill
            experience: The amount of experience to apply
        """
        # Emit an event for the character system to handle
        self._event_dispatcher.publish_sync(
            "SKILL_EXPERIENCE_GAINED",
            {
                "character_id": character_id,
                "skill": skill_name,
                "experience": experience,
                "source": "crafting",
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    
    # Recipe Learning and Discovery Methods
    
    def learn_recipe(self, character_id: str, recipe_id: str) -> Tuple[bool, str]:
        """
        Learn a recipe for a character.
        
        Args:
            character_id: The ID of the character
            recipe_id: The ID of the recipe to learn
            
        Returns:
            Tuple[bool, str]: (Success, message)
        """
        # Check if the recipe exists
        if recipe_id not in self._recipes:
            return False, f"Recipe {recipe_id} not found"
            
        # Get the recipe
        recipe = self._recipes[recipe_id]
        
        # Check if the recipe is hidden (can't learn hidden recipes directly)
        if recipe.is_hidden:
            return False, "Recipe is hidden and cannot be learned directly"
            
        # Check if the recipe is enabled
        if not recipe.is_enabled:
            return False, "Recipe is disabled and cannot be learned"
            
        # Store the learned recipe for the character
        # Will be implemented with character system integration
        # For now, emit an event for other systems to handle
        self._event_dispatcher.publish_sync(
            "RECIPE_LEARNED",
            {
                "character_id": character_id,
                "recipe_id": recipe_id,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        
        return True, f"Recipe {recipe.name} learned successfully"
    
    def discover_recipe(self, character_id: str, discovery_method: str, context_data: Dict[str, Any] = None) -> Tuple[bool, str, Optional[str]]:
        """
        Discover a new recipe through various means.
        
        Args:
            character_id: The ID of the character
            discovery_method: How the recipe was discovered (e.g., "exploration", "quest", "mentor")
            context_data: Additional context for discovery (e.g., location, quest ID)
            
        Returns:
            Tuple[bool, str, Optional[str]]: (Success, message, discovered recipe ID if successful)
        """
        context_data = context_data or {}
        
        # Find candidate recipes that match the discovery criteria
        candidate_recipes = self._find_discoverable_recipes(discovery_method, context_data)
        
        if not candidate_recipes:
            return False, "No recipes available to discover", None
            
        # Select a random recipe from the candidates
        recipe_id = random.choice(candidate_recipes)
        recipe = self._recipes[recipe_id]
        
        # Emit discovery event
        self._event_dispatcher.publish_sync(
            "RECIPE_DISCOVERED",
            {
                "character_id": character_id,
                "recipe_id": recipe_id,
                "discovery_method": discovery_method,
                "context_data": context_data,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        
        # Automatically learn the recipe
        success, message = self.learn_recipe(character_id, recipe_id)
        if not success:
            return False, f"Discovered recipe but couldn't learn it: {message}", recipe_id
            
        return True, f"Discovered and learned recipe: {recipe.name}", recipe_id
    
    def _find_discoverable_recipes(self, discovery_method: str, context_data: Dict[str, Any]) -> List[str]:
        """
        Find recipes that can be discovered based on method and context.
        
        Args:
            discovery_method: How recipes are being discovered
            context_data: Additional context data
            
        Returns:
            List[str]: List of recipe IDs that can be discovered
        """
        discoverable_recipes = []
        
        for recipe_id, recipe in self._recipes.items():
            # Skip already learned recipes (would need integration with character system)
            # Skip non-hidden recipes for certain discovery methods
            if discovery_method in ["exploration", "quest"] and not recipe.is_hidden:
                continue
                
            # Skip disabled recipes
            if not recipe.is_enabled:
                continue
                
            # Apply method-specific filters
            if discovery_method == "exploration" and context_data.get("location_type") in recipe.metadata.get("discovery_locations", []):
                discoverable_recipes.append(recipe_id)
            elif discovery_method == "quest" and context_data.get("quest_id") in recipe.metadata.get("discovery_quests", []):
                discoverable_recipes.append(recipe_id)
            elif discovery_method == "mentor" and recipe.metadata.get("mentor_teachable", False):
                discoverable_recipes.append(recipe_id)
            elif discovery_method == "random" and recipe.metadata.get("random_discoverable", False):
                discoverable_recipes.append(recipe_id)
                
        return discoverable_recipes
    
    def get_known_recipes(self, character_id: str) -> List[dict]:
        """
        Get all recipes known to a character.
        
        Args:
            character_id: The ID of the character
            
        Returns:
            List[dict]: List of known recipes
        """
        # Will be implemented with character system integration
        # For now, return all non-hidden recipes
        known_recipes = []
        
        for recipe_id, recipe in self._recipes.items():
            if not recipe.is_hidden and recipe.is_enabled:
                known_recipes.append(self.get_recipe(recipe_id))
                
        return known_recipes
    
    def craft(
        self, 
        character_id: str, 
        recipe_id: str,
        inventory_id: str,
        station_id: Optional[str] = None,
        skills: Dict[str, int] = None
    ) -> Dict[str, Any]:
        """
        Craft a recipe.
        
        Args:
            character_id: The ID of the character
            recipe_id: The ID of the recipe
            inventory_id: The ID of the inventory to use
            station_id: The ID of the crafting station to use (if required)
            skills: Dictionary of skill names to levels
            
        Returns:
            Dict[str, Any]: Result of crafting operation
        """
        can_craft, reason = self.can_craft(
            character_id, recipe_id, inventory_id, station_id, skills
        )
        
        if not can_craft:
            self._logger.info(f"Crafting failed: {reason} (character: {character_id}, recipe: {recipe_id})")
            fail_result = self._create_failed_craft_result(character_id, recipe_id, reason)
            self._emit_crafting_failed_event(character_id, recipe_id, reason)
            return fail_result
        
        recipe = self._recipes[recipe_id]
        
        # Process ingredients
        try:
            with db.session.begin():
                # Emit crafting start event
                self._emit_crafting_started_event(character_id, recipe_id, inventory_id)
                
                self._process_ingredients(recipe, inventory_id)
                
                # Determine and process results
                results = self._determine_craft_results(recipe, skills)
                self._process_results(results, inventory_id)
                
                # Calculate and grant skill experience
                skill_name, skill_exp = self._calculate_crafting_experience(recipe, results, skills)
                
                # Apply skill experience
                if skill_name and skill_exp > 0:
                    self._apply_crafting_experience(character_id, skill_name, skill_exp)
                
                # Emit crafting completed event
                self._emit_crafting_completed_event(character_id, recipe_id, results)
                
                self._logger.info(f"Crafting successful (character: {character_id}, recipe: {recipe_id})")
                success_result = self._create_successful_craft_result(character_id, recipe_id, results)
                
                # Add experience info to result
                if skill_name and skill_exp > 0:
                    success_result["skill_experience"] = {
                        "skill": skill_name,
                        "experience_gained": skill_exp
                    }
                
                return success_result
        except Exception as e:
            self._logger.error(f"Error during crafting: {str(e)}")
            db.session.rollback()
            self._emit_crafting_failed_event(character_id, recipe_id, str(e))
            return self._create_failed_craft_result(character_id, recipe_id, f"Crafting error: {str(e)}")
            
    def _check_skill_requirements(self, recipe: CraftingRecipe, skills: Dict[str, int] = None) -> Tuple[bool, str]:
        """
        Check if the provided skills meet the recipe requirements.
        
        Args:
            recipe: The recipe to check
            skills: Dictionary of skill names to levels
            
        Returns:
            Tuple[bool, str]: (Meets requirements, reason if not)
        """
        skills = skills or {}
        
        if recipe.skill_required:
            if recipe.skill_required not in skills:
                return False, f"Missing required skill: {recipe.skill_required}"
                
            if skills[recipe.skill_required] < recipe.min_skill_level:
                return False, f"Skill level too low: {recipe.skill_required} ({skills[recipe.skill_required]}/{recipe.min_skill_level})"
        
        return True, "Skill requirements met"
    
    def _track_crafting_achievement(self, character_id: str, recipe_id: str, results: List[Dict[str, Any]]) -> None:
        """
        Track crafting achievements and milestones for a character.
        
        Args:
            character_id: The ID of the character
            recipe_id: The ID of the recipe
            results: The crafting results
        """
        recipe = self._recipes.get(recipe_id)
        if not recipe:
            return
            
        # Get achievement data
        achievement_data = {
            "character_id": character_id,
            "recipe_id": recipe_id,
            "recipe_name": recipe.name,
            "timestamp": datetime.utcnow().isoformat(),
            "quality_crafted": [result.get("quality", "NORMAL") for result in results],
            "skill_name": recipe.skill_required
        }
        
        # Add high-quality item achievement if applicable
        highest_quality = None
        for result in results:
            quality = result.get("quality", "NORMAL")
            if highest_quality is None or self._get_quality_rank(quality) > self._get_quality_rank(highest_quality):
                highest_quality = quality
                
        if highest_quality and highest_quality != "NORMAL":
            achievement_data["highest_quality"] = highest_quality
            
            # Emit special achievement for masterwork or legendary items
            if highest_quality in ["MASTERWORK", "LEGENDARY"]:
                self._event_dispatcher.publish_sync(
                    "ACHIEVEMENT_UNLOCKED",
                    {
                        "character_id": character_id,
                        "achievement_id": f"craft_{highest_quality.lower()}",
                        "achievement_name": f"Crafter of {highest_quality}",
                        "description": f"Crafted a {highest_quality} quality item",
                        "timestamp": datetime.utcnow().isoformat()
                    }
                )
        
        # Track crafting milestones
        self._track_crafting_milestones(character_id, recipe)
        
        # Emit generic crafting event for achievement tracking
        self._event_dispatcher.publish_sync(
            "CRAFTING_TRACKED",
            achievement_data
        )
    
    def _get_quality_rank(self, quality: str) -> int:
        """
        Get numeric rank for a quality string.
        
        Args:
            quality: Quality string
            
        Returns:
            int: Numeric rank
        """
        quality_ranks = {
            "DAMAGED": -1,
            "NORMAL": 0,
            "FINE": 1,
            "SUPERIOR": 2,
            "MASTERWORK": 3,
            "LEGENDARY": 4
        }
        return quality_ranks.get(quality, 0)
    
    def _track_crafting_milestones(self, character_id: str, recipe: CraftingRecipe) -> None:
        """
        Track crafting milestones for a character.
        
        Args:
            character_id: The ID of the character
            recipe: The crafted recipe
        """
        # In a full implementation, this would query a persistent store 
        # to track total items crafted, unique recipes crafted, etc.
        # For now, we'll just emit a milestone event if this is a special recipe
        
        if recipe.metadata.get("is_milestone", False):
            milestone_data = {
                "character_id": character_id,
                "milestone_id": f"recipe_{recipe.id}",
                "milestone_name": f"Crafted: {recipe.name}",
                "description": f"Successfully crafted {recipe.name}",
                "timestamp": datetime.utcnow().isoformat()
            }
            
            if "milestone_rewards" in recipe.metadata:
                milestone_data["rewards"] = recipe.metadata["milestone_rewards"]
                
            self._event_dispatcher.publish_sync(
                "MILESTONE_COMPLETED",
                milestone_data
            )
            
    def update_craft_method(self, craft_method=None):
        """Update the craft method in the CraftingService class."""
        if not craft_method:
            return  # Implement default behavior
            
        # Modify the craft method to include tracking
        original_craft = self.craft
        
        def enhanced_craft(self, character_id, recipe_id, inventory_id, station_id=None, skills=None):
            result = original_craft(character_id, recipe_id, inventory_id, station_id, skills)
            
            # If crafting was successful, track achievements
            if result.get("success") and "results" in result:
                self._track_crafting_achievement(character_id, recipe_id, result["results"])
                
            return result
            
        # Replace the craft method
        self.craft = enhanced_craft.__get__(self, type(self)) 

# Module-level code
"""
Crafting Service

Main service for crafting operations in the game.
"""

# Uncomment these imports
# Add inventory system imports

# Will uncomment when events are implemented


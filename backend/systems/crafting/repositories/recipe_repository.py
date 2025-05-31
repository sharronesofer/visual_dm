"""
Recipe Repository

Provides database operations for crafting recipes.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_

from backend.systems.crafting.models.recipe import CraftingRecipe
from backend.systems.crafting.repositories.base_repository import BaseRepository

class RecipeRepository(BaseRepository[CraftingRecipe]):
    """
    Repository for crafting recipe operations.
    """
    
    def __init__(self):
        """Initialize the recipe repository."""
        super().__init__(CraftingRecipe)
    
    def get_with_ingredients_and_results(self, recipe_id: str) -> Optional[CraftingRecipe]:
        """
        Get a recipe with its ingredients and results loaded.
        
        Args:
            recipe_id: The ID of the recipe
            
        Returns:
            The recipe with relationships loaded, or None if not found
        """
        session = self._get_session()
        try:
            return session.query(self.model)\
                .options(joinedload(CraftingRecipe.ingredients))\
                .options(joinedload(CraftingRecipe.results))\
                .filter(self.model.id == recipe_id)\
                .first()
        finally:
            session.close()
    
    def get_recipes_by_skill(self, skill_type: str, max_level: Optional[int] = None) -> List[CraftingRecipe]:
        """
        Get recipes that require a specific skill.
        
        Args:
            skill_type: The skill type required
            max_level: Maximum skill level to filter by
            
        Returns:
            List of recipes requiring the skill
        """
        session = self._get_session()
        try:
            query = session.query(self.model)\
                .filter(self.model.skill_required == skill_type)\
                .filter(self.model.is_enabled == True)
            
            if max_level is not None:
                query = query.filter(self.model.min_skill_level <= max_level)
                
            return query.order_by(self.model.min_skill_level).all()
        finally:
            session.close()
    
    def get_recipes_by_station(self, station_type: str) -> List[CraftingRecipe]:
        """
        Get recipes that can be crafted at a specific station type.
        
        Args:
            station_type: The station type
            
        Returns:
            List of recipes for the station
        """
        session = self._get_session()
        try:
            return session.query(self.model)\
                .filter(or_(
                    self.model.station_required == station_type,
                    self.model.station_required.is_(None)
                ))\
                .filter(self.model.is_enabled == True)\
                .order_by(self.model.min_skill_level)\
                .all()
        finally:
            session.close()
    
    def get_craftable_recipes(self, character_skills: Dict[str, int], available_stations: List[str]) -> List[CraftingRecipe]:
        """
        Get recipes that can be crafted with current skills and stations.
        
        Args:
            character_skills: Dictionary of skill_name -> level
            available_stations: List of available station types
            
        Returns:
            List of craftable recipes
        """
        session = self._get_session()
        try:
            query = session.query(self.model)\
                .filter(self.model.is_enabled == True)\
                .filter(self.model.is_hidden == False)
            
            # Filter by available stations
            if available_stations:
                query = query.filter(or_(
                    self.model.station_required.in_(available_stations),
                    self.model.station_required.is_(None)
                ))
            
            recipes = query.all()
            
            # Filter by skills
            craftable = []
            for recipe in recipes:
                if recipe.skill_required:
                    if recipe.skill_required in character_skills:
                        if character_skills[recipe.skill_required] >= recipe.min_skill_level:
                            craftable.append(recipe)
                else:
                    # No skill requirement
                    craftable.append(recipe)
            
            return craftable
        finally:
            session.close()
    
    def search_recipes(self, search_term: str, limit: int = 50) -> List[CraftingRecipe]:
        """
        Search recipes by name or description.
        
        Args:
            search_term: Term to search for
            limit: Maximum number of results
            
        Returns:
            List of matching recipes
        """
        session = self._get_session()
        try:
            search_pattern = f"%{search_term}%"
            return session.query(self.model)\
                .filter(or_(
                    self.model.name.ilike(search_pattern),
                    self.model.description.ilike(search_pattern)
                ))\
                .filter(self.model.is_enabled == True)\
                .limit(limit)\
                .all()
        finally:
            session.close()
    
    def get_hidden_recipes(self) -> List[CraftingRecipe]:
        """
        Get all hidden recipes.
        
        Returns:
            List of hidden recipes
        """
        return self.find_by(is_hidden=True, is_enabled=True)
    
    def get_recipes_by_experience_range(self, min_exp: int, max_exp: int) -> List[CraftingRecipe]:
        """
        Get recipes that give experience within a range.
        
        Args:
            min_exp: Minimum experience
            max_exp: Maximum experience
            
        Returns:
            List of recipes in experience range
        """
        session = self._get_session()
        try:
            return session.query(self.model)\
                .filter(and_(
                    self.model.base_experience >= min_exp,
                    self.model.base_experience <= max_exp
                ))\
                .filter(self.model.is_enabled == True)\
                .order_by(self.model.base_experience)\
                .all()
        finally:
            session.close()
    
    def get_recipes_requiring_ingredient(self, item_id: str) -> List[CraftingRecipe]:
        """
        Get recipes that require a specific ingredient.
        
        Args:
            item_id: The ingredient item ID
            
        Returns:
            List of recipes using the ingredient
        """
        session = self._get_session()
        try:
            return session.query(self.model)\
                .join(self.model.ingredients)\
                .filter(self.model.ingredients.any(item_id=item_id))\
                .filter(self.model.is_enabled == True)\
                .all()
        finally:
            session.close()
    
    def get_recipes_producing_item(self, item_id: str) -> List[CraftingRecipe]:
        """
        Get recipes that produce a specific item.
        
        Args:
            item_id: The result item ID
            
        Returns:
            List of recipes producing the item
        """
        session = self._get_session()
        try:
            return session.query(self.model)\
                .join(self.model.results)\
                .filter(self.model.results.any(item_id=item_id))\
                .filter(self.model.is_enabled == True)\
                .all()
        finally:
            session.close()
    
    def enable_recipe(self, recipe_id: str) -> bool:
        """
        Enable a recipe.
        
        Args:
            recipe_id: The recipe ID
            
        Returns:
            True if enabled, False if not found
        """
        return self.update(recipe_id, is_enabled=True) is not None
    
    def disable_recipe(self, recipe_id: str) -> bool:
        """
        Disable a recipe.
        
        Args:
            recipe_id: The recipe ID
            
        Returns:
            True if disabled, False if not found
        """
        return self.update(recipe_id, is_enabled=False) is not None
    
    def hide_recipe(self, recipe_id: str) -> bool:
        """
        Hide a recipe from normal discovery.
        
        Args:
            recipe_id: The recipe ID
            
        Returns:
            True if hidden, False if not found
        """
        return self.update(recipe_id, is_hidden=True) is not None
    
    def reveal_recipe(self, recipe_id: str) -> bool:
        """
        Reveal a hidden recipe.
        
        Args:
            recipe_id: The recipe ID
            
        Returns:
            True if revealed, False if not found
        """
        return self.update(recipe_id, is_hidden=False) is not None 
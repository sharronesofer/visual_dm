"""
Standalone test for the crafting system models.
"""

from backend.systems.crafting.models.ingredient import CraftingIngredient
from backend.systems.crafting.models.result import CraftingResult
from backend.systems.crafting.models.station import CraftingStation
from backend.systems.crafting.models.recipe import CraftingRecipe

def test_crafting_ingredient():
    """Test CraftingIngredient functionality."""
    print("Testing CraftingIngredient...")
    
    # Test basic initialization
    ingredient = CraftingIngredient("iron_ingot", 3, is_consumed=True)
    assert ingredient.item_id == "iron_ingot"
    assert ingredient.quantity == 3
    assert ingredient.is_consumed is True
    assert len(ingredient.substitution_groups) == 0
    
    # Test with substitutions
    subs = {"low_quality": {"scrap_metal": 5}}
    ingredient = CraftingIngredient("iron_ingot", 3, is_consumed=True, substitution_groups=subs)
    assert ingredient.substitution_groups == subs
    
    # Test to_dict
    data = ingredient.to_dict()
    assert data["item_id"] == "iron_ingot"
    assert data["quantity"] == 3
    assert data["is_consumed"] is True
    assert data["substitution_groups"] == subs
    
    print("CraftingIngredient tests passed!")

def test_crafting_result():
    """Test CraftingResult functionality."""
    print("Testing CraftingResult...")
    
    # Test basic initialization
    result = CraftingResult("iron_sword", 1, 1.0)
    assert result.item_id == "iron_sword"
    assert result.quantity == 1
    assert result.probability == 1.0
    assert len(result.metadata) == 0
    
    # Test metadata
    result.set_metadata("quality", "high")
    assert result.metadata["quality"] == "high"
    assert result.get_metadata("quality") == "high"
    assert result.get_metadata("nonexistent", "default") == "default"
    
    # Test to_dict
    data = result.to_dict()
    assert data["item_id"] == "iron_sword"
    assert data["quantity"] == 1
    assert data["probability"] == 1.0
    assert data["metadata"]["quality"] == "high"
    
    print("CraftingResult tests passed!")

def test_crafting_station():
    """Test CraftingStation functionality."""
    print("Testing CraftingStation...")
    
    # Test basic initialization
    station = CraftingStation("basic_smithy", "Basic Smithy", "A simple forge", "smithy", level=1)
    assert station.id == "basic_smithy"
    assert station.name == "Basic Smithy"
    assert station.description == "A simple forge"
    assert station.station_type == "smithy"
    assert station.type == "smithy"  # Backward compatibility
    assert station.level == 1
    assert len(station.metadata) == 0
    
    # Test with type parameter (for backward compatibility)
    station = CraftingStation("basic_smithy", "Basic Smithy", "A simple forge", station_type="smithy", type="forge", level=1)
    assert station.station_type == "forge"  # Should use type parameter if provided
    assert station.type == "forge"  # Backward compatibility
    
    # Test with metadata
    metadata = {"required_space": 4}
    station = CraftingStation("basic_smithy", "Basic Smithy", "A simple forge", "smithy", level=1, metadata=metadata)
    assert station.metadata == metadata
    
    # Test can_craft_recipe
    assert station.can_craft_recipe("smithy", 1) is True
    assert station.can_craft_recipe("smithy", 2) is False
    assert station.can_craft_recipe("alchemy", 1) is False
    
    # Test to_dict
    data = station.to_dict()
    assert data["id"] == "basic_smithy"
    assert data["name"] == "Basic Smithy"
    assert data["description"] == "A simple forge"
    assert data["station_type"] == "smithy"
    assert data["type"] == "smithy"  # Backward compatibility
    assert data["level"] == 1
    assert data["metadata"] == metadata
    
    print("CraftingStation tests passed!")

def test_crafting_recipe():
    """Test CraftingRecipe functionality."""
    print("Testing CraftingRecipe...")
    
    # Create test ingredients and results
    ingredient1 = CraftingIngredient("iron_ingot", 3, is_consumed=True)
    ingredient2 = CraftingIngredient("leather_strip", 2, is_consumed=True)
    result = CraftingResult("iron_sword", 1, 1.0)
    
    # Test basic initialization
    recipe = CraftingRecipe(
        "iron_sword",
        "Iron Sword",
        "A basic iron sword",
        skill_required="smithing",
        min_skill_level=2,
        station_required="smithy",
        station_level=1,
        ingredients=[ingredient1, ingredient2],
        results=[result],
        is_hidden=False,
        is_enabled=True,
    )
    
    assert recipe.id == "iron_sword"
    assert recipe.name == "Iron Sword"
    assert recipe.description == "A basic iron sword"
    assert recipe.skill_required == "smithing"
    assert recipe.min_skill_level == 2
    assert recipe.station_required == "smithy"
    assert recipe.station_level == 1
    assert len(recipe.ingredients) == 2
    assert len(recipe.results) == 1
    assert recipe.is_hidden is False
    assert recipe.is_enabled is True
    
    # Test with metadata and discovery methods
    metadata = {"base_experience": 15}
    discovery_methods = ["smith_mentor"]
    recipe = CraftingRecipe(
        "iron_sword",
        "Iron Sword",
        "A basic iron sword",
        skill_required="smithing",
        min_skill_level=2,
        station_required="smithy",
        station_level=1,
        ingredients=[ingredient1, ingredient2],
        results=[result],
        is_hidden=False,
        is_enabled=True,
        metadata=metadata,
        discovery_methods=discovery_methods,
    )
    
    assert recipe.metadata == metadata
    assert recipe.discovery_methods == discovery_methods
    
    # Test add_ingredient and add_result
    ingredient3 = CraftingIngredient("coal", 1, is_consumed=True)
    result2 = CraftingResult("iron_sword_hilt", 1, 0.1)
    recipe.add_ingredient(ingredient3)
    recipe.add_result(result2)
    
    assert len(recipe.ingredients) == 3
    assert len(recipe.results) == 2
    
    # Test to_dict
    data = recipe.to_dict()
    assert data["id"] == "iron_sword"
    assert data["name"] == "Iron Sword"
    assert data["description"] == "A basic iron sword"
    assert data["skill_required"] == "smithing"
    assert data["min_skill_level"] == 2
    assert data["station_required"] == "smithy"
    assert data["station_level"] == 1
    assert len(data["ingredients"]) == 3
    assert len(data["results"]) == 2
    assert data["is_hidden"] is False
    assert data["is_enabled"] is True
    assert data["metadata"] == metadata
    assert data["discovery_methods"] == discovery_methods
    
    print("CraftingRecipe tests passed!")

if __name__ == "__main__":
    print("Running crafting model tests...")
    test_crafting_ingredient()
    test_crafting_result()
    test_crafting_station()
    test_crafting_recipe()
    print("All tests passed!") 
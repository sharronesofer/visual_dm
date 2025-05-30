# Crafting System

The crafting system provides a comprehensive framework for crafting items in the game. It handles recipes, ingredients, crafting stations, and the crafting process itself, including inventory integration, quality-based results, and skill progression.

## Features

- **Recipe Management**: Load and manage recipes from data files
- **Crafting Station Integration**: Different recipes require different stations with level requirements
- **Material Substitution**: Support for using alternative materials
- **Quality-Based Results**: Quality of crafted items depends on skill level
- **Critical Success/Failure**: Chance for exceptional results or failures
- **Skill Experience**: Gain experience in crafting skills
- **Recipe Learning and Discovery**: Learn and discover new recipes through various means
- **Achievements and Milestones**: Track crafting achievements and milestones
- **Inventory Integration**: Consumes ingredients and produces results in character inventories
- **Event System Integration**: Emits events for crafting operations

## Usage

```python
from backend.systems.crafting import craft, get_available_recipes, can_craft

# Check available recipes for a character
recipes = get_available_recipes(character_id="character1", skills={"smithing": 5})

# Check if a character can craft a recipe
can_craft_result, reason = can_craft(
    character_id="character1",
    recipe_id="iron_sword",
    inventory_id="inventory1",
    station_id="basic_smithy",
    skills={"smithing": 5}
)

# Craft an item
result = craft(
    character_id="character1",
    recipe_id="iron_sword",
    inventory_id="inventory1",
    station_id="basic_smithy",
    skills={"smithing": 5}
)

# Process the crafting result
if result["success"]:
    print(f"Crafted items: {result['results']}")
    if "skill_experience" in result:
        skill = result["skill_experience"]["skill"]
        exp = result["skill_experience"]["experience_gained"]
        print(f"Gained {exp} experience in {skill}")
else:
    print(f"Crafting failed: {result['message']}")
```

## Data Files

### Recipes

Recipe data is stored in JSON files in the `data/recipes/` directory. Each file contains multiple recipes organized by category (e.g., weapons.json, alchemy.json).

Example recipe structure:
```json
{
  "iron_sword": {
    "name": "Iron Sword",
    "description": "A basic iron sword, effective in combat.",
    "skill_required": "smithing",
    "min_skill_level": 2,
    "station_required": "smithy",
    "station_level": 1,
    "ingredients": [
      {
        "item_id": "iron_ingot",
        "quantity": 3,
        "is_consumed": true,
        "substitution_groups": {
          "low_quality": {
            "scrap_metal": 5
          }
        }
      },
      {
        "item_id": "leather_strip",
        "quantity": 2,
        "is_consumed": true
      }
    ],
    "results": [
      {
        "item_id": "iron_sword",
        "quantity": 1,
        "probability": 1.0
      }
    ],
    "is_hidden": false,
    "is_enabled": true,
    "discovery_methods": ["smith_mentor"],
    "metadata": {
      "base_experience": 15,
      "quality_modifiers": {
        "damage": 2,
        "durability": 5
      }
    }
  }
}
```

### Crafting Stations

Crafting station data is stored in JSON files in the `data/stations/` directory.

Example station structure:
```json
{
  "basic_smithy": {
    "name": "Basic Smithy",
    "description": "A simple forge for basic metalworking.",
    "type": "smithy",
    "level": 1,
    "metadata": {
      "required_space": 4,
      "build_materials": {
        "stone": 10,
        "iron": 5,
        "wood": 15
      },
      "allowed_categories": ["weapons", "armor", "tools"]
    }
  }
}
```

## Quality System

The quality of crafted items is determined by:
1. Character skill level vs. recipe requirement
2. Critical success/failure chance
3. Quality calculation based on skill difference

Quality levels:
- DAMAGED: Item with reduced stats (failure result)
- NORMAL: Standard quality
- FINE: Better than normal
- SUPERIOR: High quality
- MASTERWORK: Exceptional quality
- LEGENDARY: Best possible quality (rare)

## Recipe Discovery

Recipes can be discovered through various methods:
- Learning from a mentor or teacher
- Finding in books or scrolls
- Through quests
- Exploration
- Random discovery

Hidden recipes require specific discovery methods and may have discovery conditions.

## Integration with Event System

The crafting system emits the following events:
- `CRAFTING_STARTED`: When crafting begins
- `CRAFTING_COMPLETED`: When crafting is successful
- `CRAFTING_FAILED`: When crafting fails
- `RECIPE_LEARNED`: When a character learns a recipe
- `RECIPE_DISCOVERED`: When a character discovers a recipe
- `ACHIEVEMENT_UNLOCKED`: For crafting achievements
- `MILESTONE_COMPLETED`: For crafting milestones
- `SKILL_EXPERIENCE_GAINED`: For skill experience from crafting

## Dependencies

- Inventory System (for ingredient consumption and result placement)
- Event System (for crafting events)
- Character System (for skill progression integration)

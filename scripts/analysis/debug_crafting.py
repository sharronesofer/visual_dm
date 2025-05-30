#!/usr/bin/env python3
import os
import sys
import tempfile
import json
from pathlib import Path

# Add the backend to the path
sys.path.insert(0, 'backend')

from backend.systems.crafting import get_recipe_service, learn_recipe

def test_recipe_loading():
    # Set up test environment
    temp_dir = tempfile.TemporaryDirectory()
    recipe_dir = Path(temp_dir.name) / 'recipes'
    recipe_dir.mkdir()

    recipe_data = {
        'iron_sword': {
            'name': 'Iron Sword',
            'description': 'A basic iron sword',
            'skill_required': 'smithing',
            'min_skill_level': 2,
            'station_required': 'smithy',
            'station_level': 1,
            'ingredients': [],
            'results': [{'item_id': 'iron_sword', 'quantity': 1, 'probability': 1.0}],
            'is_hidden': False,
            'is_enabled': True
        }
    }

    with open(recipe_dir / 'test_recipes.json', 'w') as f:
        json.dump(recipe_data, f)

    os.environ['RECIPE_DIR'] = str(recipe_dir)

    # Test recipe loading
    recipe_service = get_recipe_service()
    all_recipes = recipe_service.get_all_recipes()
    print(f'Loaded recipes: {list(all_recipes.keys())}')

    # Test learning
    result = learn_recipe('test_char', 'iron_sword')
    print(f'Learn result: {result}')

    temp_dir.cleanup()

if __name__ == '__main__':
    test_recipe_loading() 
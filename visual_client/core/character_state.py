# visual_client/core/character_state.py

from core.config_creation import LEVEL, ATTRIBUTES

# Initial blank character object
def initialize_character():
    return {
        "name": "",
        "race": None,
        "level": LEVEL,
        "base_stats": {},
        "stats": {},
        "racial_modifiers": {},
        "racial_traits": {},
        "racial_description": "",
        "skills": {},
        "feats": [],
        "starting_kit": None,
        "background": "",
        "remaining_skill_points": 0,
        "skill_points_total": 0,
        "max_skill_rank": LEVEL + 3,
        "dr": 0,
        "step": 0,
        "player": "PlayerPlaceholder"
    }

# List of creation steps (matches screen flow)
steps = ["Race", "Stats", "Skills", "Feats", "Name", "Background", "Kit", "Summary"]

# Stat UI state
def get_initial_ui_state():
    return {
        "selected_index": 0,
        "scroll_offset": 0,
        "name_input": "",
        "background_input": "",
        "stats_phase": "pointbuy",
        "assigned_stats": {attr: -2 for attr in ATTRIBUTES},
        "selected_attribute_index": 0
    }

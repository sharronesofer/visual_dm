"""
Combat encounter generation utilities for the Visual DM combat system.

This module provides tools for generating scaled combat encounters based on
player level, location danger, and other factors.
"""

import math
import random
from firebase_admin import db

def generate_scaled_encounter(character_id, location, danger_level):
    """
    Generate a combat encounter scaled by player level, location danger, and distance from (0,0).
    
    Args:
        character_id: ID of the character to scale against
        location: Location string (format: "x_y")
        danger_level: Danger level of the location (1-10)
        
    Returns:
        dict: Encounter data with enemies and scaling factors
    """
    try:
        # Pull player data
        char_ref = db.reference(f"/players/{character_id}")
        player = char_ref.get()
        if not player:
            return {"error": "Character not found."}

        # Distance from center
        x, y = map(int, location.split("_"))
        dist = math.sqrt(x**2 + y**2)
        distance_factor = max(1.0, min(dist / 20.0, 2.5))  # 1.0–2.5x scaling

        # Base CR from player level
        level = player.get("level", 1)
        base_cr = max(0.25, level * 0.25)

        # Danger adjustment
        cr_adjustment = (danger_level / 10.0) * 0.5  # adds up to +0.5 CR at danger 10
        effective_cr = base_cr + cr_adjustment

        # Distance adjustment
        effective_cr *= distance_factor

        # Load all monsters
        all_monsters = db.reference("/rules/monsters").get() or {}
        valid_monsters = [m for m in all_monsters.values()
                        if abs(m.get("challenge_rating", 0) - effective_cr) <= 1.0]

        if not valid_monsters:
            return {"error": "No suitable monsters found."}

        # Randomize small group
        enemy_group = random.sample(valid_monsters, min(2, len(valid_monsters)))

        # Final enemy party
        enemy_party = []
        for m in enemy_group:
            enemy_party.append({
                "id": f"enemy_{random.randint(1000, 9999)}",
                "name": m.get("name", "Unknown"),
                "HP": m.get("hp", 20),
                "AC": m.get("ac", 12),
                "DEX": m.get("dex", 10),
                "team": "hostile"
            })

        # (Optional) Start Firebase battle record here if desired
        return {
            "enemies": enemy_party,
            "effective_cr": effective_cr,
            "danger_level": danger_level,
            "distance_factor": distance_factor,
            "location": location
        }

    except Exception as e:
        return {"error": str(e)}


def generate_location_appropriate_encounter(region_id, poi_id, party_level):
    """
    Generate an encounter appropriate for a specific region and POI.
    
    Args:
        region_id: ID of the region
        poi_id: ID of the POI
        party_level: Average level of the party
        
    Returns:
        dict: Encounter data with enemies and theme information
    """
    # Get region and POI data
    region_ref = db.reference(f"/regions/{region_id}")
    region = region_ref.get() or {}
    
    poi_ref = db.reference(f"/poi_state/{region_id}/{poi_id}")
    poi = poi_ref.get() or {}
    
    # Get theme and biome information
    biome = region.get("biome", "plains")
    theme = poi.get("theme", "neutral")
    danger = poi.get("danger_level", 5)
    
    # Select monsters by biome and theme
    monster_ref = db.reference("/rules/monsters")
    all_monsters = monster_ref.get() or {}
    
    # Filter by region/biome
    biome_monsters = [m for m in all_monsters.values() if biome in m.get("habitats", [])]
    if not biome_monsters:
        biome_monsters = list(all_monsters.values())  # Fallback
    
    # Filter by theme
    themed_monsters = [m for m in biome_monsters if theme in m.get("themes", [])]
    if not themed_monsters:
        themed_monsters = biome_monsters  # Fallback
    
    # Filter by level range
    level_range = 2 if party_level < 5 else 3  # Wider range at higher levels
    level_appropriate = [
        m for m in themed_monsters 
        if abs(m.get("challenge_rating", 0) - (party_level * 0.25)) <= level_range
    ]
    
    if not level_appropriate:
        # Fallback: Sort by closest CR
        all_sorted = sorted(
            themed_monsters, 
            key=lambda m: abs(m.get("challenge_rating", 0) - (party_level * 0.25))
        )
        level_appropriate = all_sorted[:5]  # Take 5 closest
    
    # Build encounter
    group_size = random.randint(1, 3)
    selected_monsters = random.sample(level_appropriate, min(group_size, len(level_appropriate)))
    
    enemy_party = []
    for m in selected_monsters:
        enemy_party.append({
            "id": f"enemy_{random.randint(1000, 9999)}",
            "name": m.get("name", "Unknown"),
            "HP": m.get("hp", 20),
            "AC": m.get("ac", 12),
            "DEX": m.get("dex", 10),
            "STR": m.get("str", 10),
            "type": m.get("type", "unknown"),
            "challenge_rating": m.get("challenge_rating", 0.5),
            "team": "hostile"
        })
    
    return {
        "enemies": enemy_party,
        "region": region_id,
        "poi": poi_id,
        "biome": biome,
        "theme": theme,
        "danger_level": danger
    } 
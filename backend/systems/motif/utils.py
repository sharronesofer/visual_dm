from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json
import random

from .models import (
    Motif, MotifCategory, MotifScope, MotifLifecycle,
    MotifEffect, LocationInfo
)

# ===== Chaos Utility Functions (Migrated from chaos_utils.py) =====

# Define the chaos table here to avoid circular imports with manager.py
NARRATIVE_CHAOS_TABLE = [
    "NPC betrays a faction or personal goal",
    "Player receives a divine omen",
    "NPC vanishes mysteriously",
    "Corrupted prophecy appears in a temple or vision",
    "Artifact or item changes hands unexpectedly",
    "NPC's child arrives with a claim",
    "Villain resurfaces (real or false)",
    "Time skip or memory blackout (~5 minutes)",
    "PC is blamed for a crime in a new city",
    "Ally requests an impossible favor",
    "Magical item begins to misbehave",
    "Enemy faction completes objective offscreen",
    "False flag sent from another region",
    "NPC becomes hostile based on misinformation",
    "Rumor spreads about a player betrayal",
    "PC has a surreal dream altering perception",
    "Secret faction is revealed through slip-up",
    "NPC becomes obsessed with the PC",
    "Town leader is assassinated",
    "Prophecy misidentifies the chosen one"
]

def generate_motif_name(category: MotifCategory, scope: MotifScope) -> str:
    """Generate a descriptive name for a motif based on category and scope."""
    # Adjectives grouped by category
    category_adjectives = {
        MotifCategory.ASCENSION: ["rising", "uplifting", "elevating", "transcendent"],
        MotifCategory.BETRAYAL: ["treacherous", "faithless", "deceiving", "duplicitous"],
        MotifCategory.CHAOS: ["unpredictable", "disordered", "tumultuous", "wild"],
        MotifCategory.COLLAPSE: ["crumbling", "falling", "declining", "ruinous"],
        MotifCategory.COMPULSION: ["driving", "compelling", "irresistible", "forcing"],
        # Add more categories as needed
    }
    
    # Nouns grouped by scope
    scope_nouns = {
        MotifScope.GLOBAL: ["world", "era", "age", "cosmos"],
        MotifScope.REGIONAL: ["lands", "realm", "territory", "domain"],
        MotifScope.LOCAL: ["sanctuary", "grounds", "vicinity", "territory"],
    }
    
    # Get random adjective and noun, or use defaults
    adjective = random.choice(
        category_adjectives.get(category, ["mysterious"]) 
    )
    noun = random.choice(
        scope_nouns.get(scope, ["domain"])
    )
    
    return f"The {adjective.capitalize()} {noun.capitalize()}"

def generate_motif_description(category: MotifCategory, scope: MotifScope, intensity: float) -> str:
    """Generate a descriptive text for a motif based on category, scope, and intensity."""
    intensity_desc = "overwhelming" if intensity >= 7 else (
        "powerful" if intensity >= 5 else (
        "moderate" if intensity >= 3 else "subtle"
    ))
    
    # Descriptions by category
    category_descriptions = {
        MotifCategory.ASCENSION: f"A {intensity_desc} sense of rising toward something greater.",
        MotifCategory.BETRAYAL: f"A {intensity_desc} atmosphere of broken trust and deception.",
        MotifCategory.CHAOS: f"A {intensity_desc} period of disorder and unpredictability.",
        MotifCategory.COLLAPSE: f"A {intensity_desc} feeling of decline and deterioration.",
        MotifCategory.COMPULSION: f"A {intensity_desc} force driving actions beyond control.",
        # Add more categories as needed
    }
    
    # Scope modifiers
    scope_modifiers = {
        MotifScope.GLOBAL: "across the entire world",
        MotifScope.REGIONAL: "throughout this region",
        MotifScope.LOCAL: "in this immediate area",
    }
    
    description = category_descriptions.get(
        category, 
        f"A {intensity_desc} manifestation of {category.value}."
    )
    
    scope_desc = scope_modifiers.get(scope, "")
    if scope_desc:
        description += f" This influence is felt {scope_desc}."
    
    return description

def estimate_motif_compatibility(motif1: Motif, motif2: Motif) -> float:
    """
    Estimate compatibility between two motifs on a scale of -1.0 to 1.0.
    Negative values suggest conflict, positive values suggest harmony.
    """
    # Define compatibility matrix between categories
    # This is a simplified example; a complete implementation would map all categories
    compatibility_matrix = {
        # Format: (category1, category2): compatibility_score
        (MotifCategory.HOPE, MotifCategory.FEAR): -0.8,
        (MotifCategory.HOPE, MotifCategory.DESPAIR): -0.9,
        (MotifCategory.HOPE, MotifCategory.REBIRTH): 0.7,
        (MotifCategory.FEAR, MotifCategory.PARANOIA): 0.6,
        (MotifCategory.BETRAYAL, MotifCategory.LOYALTY): -1.0,
        (MotifCategory.BETRAYAL, MotifCategory.VENGEANCE): 0.5,
        (MotifCategory.CHAOS, MotifCategory.ORDER): -0.9,
        (MotifCategory.CHAOS, MotifCategory.DESTRUCTION): 0.6,
        # Add more pairs as needed
    }
    
    # Check if the pair exists in the matrix
    pair1 = (motif1.category, motif2.category)
    pair2 = (motif2.category, motif1.category)
    
    if pair1 in compatibility_matrix:
        return compatibility_matrix[pair1]
    elif pair2 in compatibility_matrix:
        return compatibility_matrix[pair2]
    
    # Default compatibility based on a basic heuristic
    # Same category motifs are highly compatible
    if motif1.category == motif2.category:
        return 0.8
    
    # Otherwise, assume neutral compatibility
    return 0.0

def generate_realistic_duration(scope: MotifScope, intensity: float) -> int:
    """
    Generate a realistic duration in days for a motif based on scope and intensity.
    Global motifs last longer than regional ones, which last longer than local ones.
    Higher intensity often means longer duration.
    """
    base_duration = 0
    
    if scope == MotifScope.GLOBAL:
        # Global motifs: 28 ±10 days
        base_duration = 28
        variation = random.randint(-10, 10)
    elif scope == MotifScope.REGIONAL:
        # Regional motifs: intensity * (3-6) days
        base_duration = intensity * random.randint(3, 6)
        variation = random.randint(-2, 2)
    else:  # LOCAL
        # Local motifs: intensity * (1-3) days
        base_duration = intensity * random.randint(1, 3)
        variation = random.randint(-1, 1)
    
    # Ensure duration is at least 1 day
    return max(1, int(base_duration + variation))

def motif_to_narrative_context(motif: Motif) -> Dict[str, Any]:
    """
    Convert a motif to a narrative context dictionary for use in text generation.
    This is useful for providing context to LLMs for narrative generation.
    """
    # Extract narrative themes based on category
    themes = []
    if motif.category == MotifCategory.BETRAYAL:
        themes.append("trust is fragile")
    elif motif.category == MotifCategory.CHAOS:
        themes.append("unpredictability and disorder")
    elif motif.category == MotifCategory.DEATH:
        themes.append("mortality and loss")
    elif motif.category == MotifCategory.HOPE:
        themes.append("optimism despite adversity")
    # Add more mappings as needed
    
    # Use intensity to determine the strength of the theme
    if motif.intensity >= 7:
        themes.append(f"overwhelming {motif.category.value}")
    elif motif.intensity >= 4:
        themes.append(f"prominent {motif.category.value}")
    
    # Extract effect descriptions
    effect_descriptions = []
    for effect in motif.effects:
        if effect.effect_type == "npc_behavior":
            effect_descriptions.append(
                f"NPCs are more likely to exhibit {motif.category.value}-related behavior"
            )
        elif effect.effect_type == "event_frequency":
            effect_descriptions.append(
                f"Events related to {motif.category.value} occur more frequently"
            )
        # Add more effect type mappings
    
    # Estimate remaining duration
    remaining_days = 0
    if motif.end_time:
        now = datetime.now()
        if motif.end_time > now:
            remaining_days = (motif.end_time - now).days
    
    # Build the context dictionary
    context = {
        "name": motif.name,
        "description": motif.description,
        "category": motif.category.value,
        "scope": motif.scope.value,
        "intensity": motif.intensity,
        "lifecycle": motif.lifecycle.value,
        "themes": themes,
        "effects": effect_descriptions,
        "remaining_days": remaining_days,
        "is_dominant": motif.intensity >= 7,
    }
    
    return context

def calculate_motif_spread(
    origin_motif: Motif, 
    distance: float,
    max_distance: float = 100.0
) -> Optional[Dict[str, Any]]:
    """
    Calculate how a motif spreads out from its origin point, weakening with distance.
    Returns None if beyond effective range, otherwise a dict with modified parameters.
    """
    if not origin_motif.location:
        return None
    
    # Check if we're beyond the maximum effective range
    if distance > max_distance:
        return None
    
    # Calculate intensity decay based on distance
    # Linear decay: intensity = original * (1 - distance/max_distance)
    intensity_multiplier = max(0.0, 1.0 - (distance / max_distance))
    new_intensity = origin_motif.intensity * intensity_multiplier
    
    # If intensity is too low, no effect
    if new_intensity < 1.0:
        return None
    
    # Create spread parameters
    spread = {
        "original_id": origin_motif.id,
        "original_intensity": origin_motif.intensity,
        "new_intensity": new_intensity,
        "distance": distance,
        "decay_factor": intensity_multiplier,
        "category": origin_motif.category.value,
        "is_significant": new_intensity >= 3.0,  # Threshold for "significant" influence
    }
    
    return spread

def motif_effect_to_text(effect: MotifEffect) -> str:
    """Convert a motif effect to a human-readable text description."""
    intensity_text = (
        "strongly" if effect.intensity >= 7.0 else
        "moderately" if effect.intensity >= 4.0 else
        "mildly"
    )
    
    if effect.effect_type == "npc_behavior":
        if effect.target == "general":
            return f"NPCs are {intensity_text} influenced in their general behavior."
        else:
            return f"NPCs are {intensity_text} influenced in their {effect.target} behavior."
    
    elif effect.effect_type == "event_frequency":
        return f"Events occur {intensity_text} more frequently."
    
    elif effect.effect_type == "resource_yield":
        return f"Resource yields are {intensity_text} affected."
    
    elif effect.effect_type == "relationship_change":
        return f"Relationship development is {intensity_text} influenced."
    
    elif effect.effect_type == "arc_development":
        return f"Story arcs develop {intensity_text} differently."
    
    elif effect.effect_type == "faction_tension":
        return f"Faction tensions are {intensity_text} affected."
    
    elif effect.effect_type == "weather_pattern":
        return f"Weather patterns are {intensity_text} altered."
    
    elif effect.effect_type == "economic_shift":
        return f"Economic factors are {intensity_text} shifted."
    
    elif effect.effect_type == "narrative_flavor":
        return f"The narrative atmosphere is {intensity_text} affected."
    
    else:
        return f"Unknown effect of {intensity_text} intensity."

def roll_chaos_event():
    """
    Generate a random chaos event from the predefined narrative chaos table.
    
    Returns:
        str: A randomly selected chaos event description
    """
    return random.choice(NARRATIVE_CHAOS_TABLE) 
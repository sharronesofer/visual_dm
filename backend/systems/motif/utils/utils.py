from typing import List, Dict, Any, Optional, Tuple, Union
from datetime import datetime, timedelta
import json
import random
import math
from dataclasses import dataclass
from collections import defaultdict

from backend.systems.motif.models import (
    Motif, MotifCategory, MotifScope, MotifLifecycle,
    MotifEffect, LocationInfo, MotifEffectTarget
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

# ===== Geometric Calculation Utilities =====

@dataclass
class Point:
    """Represents a 2D point with x, y coordinates."""
    x: float
    y: float

def calculate_distance(point1: Point, point2: Point) -> float:
    """Calculate Euclidean distance between two points."""
    return math.sqrt((point2.x - point1.x)**2 + (point2.y - point1.y)**2)

def point_in_circle(point: Point, center: Point, radius: float) -> bool:
    """Check if a point is within a circular area."""
    return calculate_distance(point, center) <= radius

def calculate_influence_area(motif: Motif) -> float:
    """Calculate the total area of influence for a motif."""
    if not motif.location:
        return float('inf') if motif.scope == MotifScope.GLOBAL else 0.0
    
    # Base radius from location, modified by intensity and scope
    base_radius = motif.location.radius or 1.0
    
    # Scope multipliers
    scope_multipliers = {
        MotifScope.LOCAL: 1.0,
        MotifScope.REGIONAL: 5.0,
        MotifScope.GLOBAL: float('inf')
    }
    
    if motif.scope == MotifScope.GLOBAL:
        return float('inf')
    
    effective_radius = base_radius * scope_multipliers[motif.scope] * (motif.intensity / 5.0)
    return math.pi * (effective_radius ** 2)

def find_motifs_in_radius(motifs: List[Motif], center: Point, radius: float) -> List[Motif]:
    """Find all motifs within a given radius of a point."""
    result = []
    for motif in motifs:
        if not motif.location:
            continue
        motif_center = Point(motif.location.x or 0, motif.location.y or 0)
        if calculate_distance(center, motif_center) <= radius:
            result.append(motif)
    return result

def calculate_motif_overlap(motif1: Motif, motif2: Motif) -> float:
    """Calculate the overlap percentage between two motifs' areas of influence."""
    if not motif1.location or not motif2.location:
        return 1.0 if motif1.scope == MotifScope.GLOBAL or motif2.scope == MotifScope.GLOBAL else 0.0
    
    center1 = Point(motif1.location.x or 0, motif1.location.y or 0)
    center2 = Point(motif2.location.x or 0, motif2.location.y or 0)
    
    radius1 = (motif1.location.radius or 1.0) * (motif1.intensity / 5.0)
    radius2 = (motif2.location.radius or 1.0) * (motif2.intensity / 5.0)
    
    distance = calculate_distance(center1, center2)
    
    # No overlap if too far apart
    if distance >= radius1 + radius2:
        return 0.0
    
    # Complete overlap if one circle is inside the other
    if distance <= abs(radius1 - radius2):
        smaller_area = math.pi * min(radius1, radius2) ** 2
        larger_area = math.pi * max(radius1, radius2) ** 2
        return smaller_area / larger_area
    
    # Partial overlap calculation using circle intersection formula
    # This is a simplified approximation
    overlap_distance = radius1 + radius2 - distance
    max_overlap = min(radius1, radius2) * 2
    overlap_ratio = overlap_distance / max_overlap
    
    return min(1.0, max(0.0, overlap_ratio))

# ===== Data Validation Utilities =====

def validate_motif_data(motif_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate motif data for completeness and correctness.
    Returns (is_valid, list_of_errors)
    """
    errors = []
    
    # Required fields
    required_fields = ['name', 'description', 'category', 'scope']
    for field in required_fields:
        if field not in motif_data or not motif_data[field]:
            errors.append(f"Missing required field: {field}")
    
    # Validate intensity range
    if 'intensity' in motif_data:
        intensity = motif_data['intensity']
        if not isinstance(intensity, (int, float)) or intensity < 1 or intensity > 10:
            errors.append("Intensity must be a number between 1 and 10")
    
    # Validate category
    if 'category' in motif_data:
        try:
            MotifCategory(motif_data['category'])
        except ValueError:
            errors.append(f"Invalid category: {motif_data['category']}")
    
    # Validate scope
    if 'scope' in motif_data:
        try:
            MotifScope(motif_data['scope'])
        except ValueError:
            errors.append(f"Invalid scope: {motif_data['scope']}")
    
    # Validate location data if present
    if 'location' in motif_data and motif_data['location']:
        location = motif_data['location']
        if isinstance(location, dict):
            if 'x' in location and not isinstance(location['x'], (int, float, type(None))):
                errors.append("Location x coordinate must be a number or null")
            if 'y' in location and not isinstance(location['y'], (int, float, type(None))):
                errors.append("Location y coordinate must be a number or null")
            if 'radius' in location and (not isinstance(location['radius'], (int, float)) or location['radius'] < 0):
                errors.append("Location radius must be a non-negative number")
    
    # Validate effects if present
    if 'effects' in motif_data and isinstance(motif_data['effects'], list):
        for i, effect in enumerate(motif_data['effects']):
            if not isinstance(effect, dict):
                errors.append(f"Effect {i} must be an object")
                continue
            
            if 'target' not in effect:
                errors.append(f"Effect {i} missing required field: target")
            else:
                try:
                    MotifEffectTarget(effect['target'])
                except ValueError:
                    errors.append(f"Effect {i} has invalid target: {effect['target']}")
            
            if 'intensity' in effect:
                eff_intensity = effect['intensity']
                if not isinstance(eff_intensity, (int, float)) or eff_intensity < 1 or eff_intensity > 10:
                    errors.append(f"Effect {i} intensity must be between 1 and 10")
    
    return len(errors) == 0, errors

def sanitize_motif_name(name: str) -> str:
    """Sanitize and normalize a motif name."""
    if not name:
        return "Unnamed Motif"
    
    # Remove excessive whitespace and normalize
    name = ' '.join(name.strip().split())
    
    # Capitalize first letter of each word
    name = ' '.join(word.capitalize() for word in name.split())
    
    # Limit length
    if len(name) > 100:
        name = name[:97] + "..."
    
    return name

def normalize_motif_description(description: str) -> str:
    """Normalize and clean up motif descriptions."""
    if not description:
        return "No description provided."
    
    # Remove excessive whitespace
    description = ' '.join(description.strip().split())
    
    # Ensure it ends with proper punctuation
    if not description.endswith('.') and not description.endswith('!') and not description.endswith('?'):
        description += '.'
    
    # Limit length
    if len(description) > 500:
        description = description[:497] + "..."
    
    return description

# ===== Advanced Narrative Synthesis Functions =====

def generate_motif_name(category: MotifCategory, scope: MotifScope) -> str:
    """Generate a descriptive name for a motif based on category and scope."""
    # Expanded adjectives grouped by category
    category_adjectives = {
        MotifCategory.ASCENSION: ["rising", "uplifting", "elevating", "transcendent", "soaring", "divine"],
        MotifCategory.BETRAYAL: ["treacherous", "faithless", "deceiving", "duplicitous", "false", "broken"],
        MotifCategory.CHAOS: ["unpredictable", "disordered", "tumultuous", "wild", "anarchic", "frenzied"],
        MotifCategory.COLLAPSE: ["crumbling", "falling", "declining", "ruinous", "deteriorating", "failing"],
        MotifCategory.COMPULSION: ["driving", "compelling", "irresistible", "forcing", "urgent", "consuming"],
        MotifCategory.CONTROL: ["dominating", "commanding", "restraining", "governing", "directing", "binding"],
        MotifCategory.DEATH: ["morbid", "deadly", "final", "terminal", "fatal", "mortal"],
        MotifCategory.DECEPTION: ["misleading", "illusory", "false", "deceptive", "cunning", "secretive"],
        MotifCategory.DEFIANCE: ["rebellious", "resistant", "defiant", "opposing", "insurgent", "revolutionary"],
        MotifCategory.DESIRE: ["yearning", "longing", "passionate", "wanting", "craving", "coveting"],
        MotifCategory.DESTINY: ["fated", "destined", "predetermined", "inevitable", "prophetic", "chosen"],
        MotifCategory.ECHO: ["resonant", "repeating", "reverberating", "haunting", "lingering", "persistent"],
        MotifCategory.FEAR: ["terrifying", "frightening", "dreadful", "menacing", "ominous", "threatening"],
        MotifCategory.HOPE: ["hopeful", "optimistic", "bright", "promising", "inspiring", "uplifting"],
        MotifCategory.MADNESS: ["insane", "deranged", "frenzied", "chaotic", "unhinged", "wild"],
        MotifCategory.POWER: ["mighty", "powerful", "dominant", "supreme", "overwhelming", "potent"],
        MotifCategory.SACRIFICE: ["sacrificial", "noble", "selfless", "devoted", "giving", "surrendering"],
        MotifCategory.VENGEANCE: ["vengeful", "retributive", "wrathful", "punishing", "vindictive", "avenging"],
    }
    
    # Expanded nouns grouped by scope
    scope_nouns = {
        MotifScope.GLOBAL: ["world", "era", "age", "cosmos", "realm", "existence", "reality", "universe"],
        MotifScope.REGIONAL: ["lands", "realm", "territory", "domain", "kingdom", "province", "region", "expanse"],
        MotifScope.LOCAL: ["sanctuary", "grounds", "vicinity", "territory", "enclave", "haven", "locale", "district"],
    }
    
    # Get random adjective and noun, or use defaults
    adjective = random.choice(
        category_adjectives.get(category, ["mysterious", "strange", "unknown", "enigmatic"]) 
    )
    noun = random.choice(
        scope_nouns.get(scope, ["domain", "area", "space", "zone"])
    )
    
    # Add occasional prefixes for variety
    prefixes = ["The", "A"] if random.random() < 0.8 else ["The Great", "The Ancient", "The Sacred", "The Eternal"]
    prefix = random.choice(prefixes)
    
    return f"{prefix} {adjective.capitalize()} {noun.capitalize()}"

def generate_motif_description(category: MotifCategory, scope: MotifScope, intensity: float) -> str:
    """Generate a descriptive text for a motif based on category, scope, and intensity."""
    intensity_desc = (
        "overwhelming" if intensity >= 8 else
        "powerful" if intensity >= 6 else
        "moderate" if intensity >= 4 else
        "subtle" if intensity >= 2 else
        "faint"
    )
    
    # Enhanced descriptions by category
    category_descriptions = {
        MotifCategory.ASCENSION: f"A {intensity_desc} sense of rising toward something greater permeates the air.",
        MotifCategory.BETRAYAL: f"An {intensity_desc} atmosphere of broken trust and lurking deception weighs heavily.",
        MotifCategory.CHAOS: f"A {intensity_desc} period of disorder and unpredictability disrupts the natural order.",
        MotifCategory.COLLAPSE: f"An {intensity_desc} feeling of decline and inevitable deterioration spreads.",
        MotifCategory.COMPULSION: f"A {intensity_desc} force drives actions beyond conscious control or reason.",
        MotifCategory.CONTROL: f"An {intensity_desc} presence of dominance and restraint shapes all interactions.",
        MotifCategory.DEATH: f"A {intensity_desc} shadow of mortality and finality hangs over everything.",
        MotifCategory.DECEPTION: f"An {intensity_desc} web of lies and illusions obscures the truth.",
        MotifCategory.DEFIANCE: f"A {intensity_desc} spirit of rebellion and resistance stirs within hearts.",
        MotifCategory.DESIRE: f"An {intensity_desc} current of longing and unfulfilled yearning flows through souls.",
        MotifCategory.DESTINY: f"An {intensity_desc} sense of fate and inevitable purpose guides events.",
        MotifCategory.ECHO: f"A {intensity_desc} resonance of past events reverberates through time.",
        MotifCategory.FEAR: f"An {intensity_desc} aura of dread and anxiety permeates every shadow.",
        MotifCategory.HOPE: f"A {intensity_desc} light of optimism and possibility shines through darkness.",
        MotifCategory.MADNESS: f"An {intensity_desc} descent into chaos and irrationality grips minds.",
        MotifCategory.POWER: f"An {intensity_desc} display of might and dominance shapes reality itself.",
        MotifCategory.SACRIFICE: f"A {intensity_desc} call to noble surrender and selfless giving emerges.",
        MotifCategory.VENGEANCE: f"An {intensity_desc} thirst for retribution and justice demands satisfaction.",
    }
    
    # Scope modifiers with more detail
    scope_modifiers = {
        MotifScope.GLOBAL: "This cosmic influence touches every corner of existence, reshaping the fundamental nature of reality.",
        MotifScope.REGIONAL: "This regional force affects the character and destiny of entire kingdoms and vast territories.",
        MotifScope.LOCAL: "This localized presence influences the immediate area, touching those who dwell or pass through.",
    }
    
    description = category_descriptions.get(
        category, 
        f"A {intensity_desc} manifestation of {category.value} emerges in the world."
    )
    
    scope_desc = scope_modifiers.get(scope, "")
    if scope_desc:
        description += f" {scope_desc}"
    
    # Add intensity-based additional details
    if intensity >= 7:
        description += " The effect is so potent that it may fundamentally alter the nature of those it touches."
    elif intensity >= 5:
        description += " Its presence is unmistakable and influences the thoughts and actions of all nearby."
    elif intensity >= 3:
        description += " Those sensitive to such forces will notice its subtle but persistent influence."
    else:
        description += " Only the most perceptive individuals might detect its gentle touch."
    
    return description

def estimate_motif_compatibility(motif1: Motif, motif2: Motif) -> float:
    """
    Estimate compatibility between two motifs on a scale of -1.0 to 1.0.
    Negative values suggest conflict, positive values suggest harmony.
    """
    # Define compatibility matrix for motif combinations
    # Uses available categories only
    compatibility_matrix = {
        # High compatibility (positive synergy)
        (MotifCategory.HOPE, MotifCategory.PEACE): 0.9,
        (MotifCategory.HOPE, MotifCategory.REDEMPTION): 0.8,
        (MotifCategory.CHAOS, MotifCategory.MADNESS): 0.8,
        (MotifCategory.POWER, MotifCategory.CONTROL): 0.7,
        (MotifCategory.BETRAYAL, MotifCategory.DECEPTION): 0.7,
        (MotifCategory.DEATH, MotifCategory.GRIEF): 0.9,
        (MotifCategory.FEAR, MotifCategory.PARANOIA): 0.7,
        (MotifCategory.JUSTICE, MotifCategory.TRUTH): 0.8,
        (MotifCategory.LOYALTY, MotifCategory.PROTECTION): 0.7,
        (MotifCategory.SACRIFICE, MotifCategory.REDEMPTION): 0.8,
        
        # Medium compatibility
        (MotifCategory.CHAOS, MotifCategory.FEAR): 0.4,
        (MotifCategory.POWER, MotifCategory.PRIDE): 0.5,
        (MotifCategory.HOPE, MotifCategory.FAITH): 0.6,
        (MotifCategory.OBSESSION, MotifCategory.MADNESS): 0.6,
        (MotifCategory.GUILT, MotifCategory.REGRET): 0.7,
        
        # Low compatibility (conflicting themes)
        (MotifCategory.HOPE, MotifCategory.FUTILITY): -0.9,
        (MotifCategory.PEACE, MotifCategory.CHAOS): -0.8,
        (MotifCategory.TRUTH, MotifCategory.DECEPTION): -0.9,
        (MotifCategory.JUSTICE, MotifCategory.BETRAYAL): -0.8,
        (MotifCategory.UNITY, MotifCategory.ISOLATION): -0.7,
        (MotifCategory.REDEMPTION, MotifCategory.VENGEANCE): -0.6,
        (MotifCategory.INNOCENCE, MotifCategory.TEMPTATION): -0.8,
        (MotifCategory.ASCENSION, MotifCategory.COLLAPSE): -0.8,
    }
    
    # Check if the pair exists in the matrix
    pair1 = (motif1.category, motif2.category)
    pair2 = (motif2.category, motif1.category)
    
    if pair1 in compatibility_matrix:
        base_compatibility = compatibility_matrix[pair1]
    elif pair2 in compatibility_matrix:
        base_compatibility = compatibility_matrix[pair2]
    else:
        # Default compatibility based on heuristics
        if motif1.category == motif2.category:
            base_compatibility = 0.8  # Same category motifs are highly compatible
        else:
            base_compatibility = 0.0  # Neutral compatibility for unknown pairs
    
    # Adjust based on intensity differences
    intensity_diff = abs(motif1.intensity - motif2.intensity)
    intensity_factor = 1.0 - (intensity_diff / 20.0)  # Reduce compatibility if intensities are very different
    
    # Adjust based on scope compatibility
    scope_factor = 1.0
    if motif1.scope != motif2.scope:
        # Different scopes may have slight compatibility reduction
        scope_factor = 0.9
    
    # Calculate final compatibility
    final_compatibility = base_compatibility * intensity_factor * scope_factor
    
    # Clamp to valid range
    return max(-1.0, min(1.0, final_compatibility))

def generate_realistic_duration(scope: MotifScope, intensity: float) -> int:
    """
    Generate a realistic duration in days for a motif based on scope and intensity.
    Global motifs last longer than regional ones, which last longer than local ones.
    Higher intensity often means longer duration.
    """
    base_duration = 0
    
    if scope == MotifScope.GLOBAL:
        # Global motifs: 21-60 days based on intensity
        base_duration = int(20 + (intensity * 4))
        variation = random.randint(-7, 7)
    elif scope == MotifScope.REGIONAL:
        # Regional motifs: intensity * (2-8) days
        multiplier = 2 + (intensity / 2)
        base_duration = int(intensity * multiplier)
        variation = random.randint(-3, 3)
    else:  # LOCAL
        # Local motifs: intensity * (1-4) days
        multiplier = 1 + (intensity / 3)
        base_duration = int(intensity * multiplier)
        variation = random.randint(-2, 2)
    
    # Ensure duration is at least 1 day
    return max(1, base_duration + variation)

def motif_to_narrative_context(motif: Motif) -> Dict[str, Any]:
    """
    Convert a motif to a comprehensive narrative context dictionary for use in text generation.
    This is useful for providing rich context to LLMs for narrative generation.
    """
    # Extract comprehensive narrative themes based on category
    themes = []
    descriptive_elements = []
    emotional_tone = "neutral"
    
    if motif.category == MotifCategory.BETRAYAL:
        themes.extend(["trust is fragile", "loyalty questioned", "hidden agendas"])
        descriptive_elements.extend(["whispered secrets", "sidelong glances", "broken promises"])
        emotional_tone = "suspicious"
    elif motif.category == MotifCategory.CHAOS:
        themes.extend(["unpredictability and disorder", "systems breaking down", "randomness prevails"])
        descriptive_elements.extend(["swirling energies", "crackling disruptions", "sudden changes"])
        emotional_tone = "chaotic"
    elif motif.category == MotifCategory.DEATH:
        themes.extend(["mortality and loss", "endings and finality", "the weight of time"])
        descriptive_elements.extend(["withering shadows", "cold silence", "fading echoes"])
        emotional_tone = "somber"
    elif motif.category == MotifCategory.HOPE:
        themes.extend(["optimism despite adversity", "light in darkness", "potential for renewal"])
        descriptive_elements.extend(["warm glimmers", "gentle breezes", "brightening horizons"])
        emotional_tone = "uplifting"
    elif motif.category == MotifCategory.FEAR:
        themes.extend(["lurking dangers", "uncertainty and anxiety", "paralyzing dread"])
        descriptive_elements.extend(["creeping shadows", "ominous sounds", "chilling presences"])
        emotional_tone = "tense"
    elif motif.category == MotifCategory.POWER:
        themes.extend(["dominance and control", "overwhelming force", "authority unchallenged"])
        descriptive_elements.extend(["commanding presence", "crackling energy", "bending reality"])
        emotional_tone = "imposing"
    
    # Use intensity to determine the strength of the theme
    intensity_descriptors = []
    if motif.intensity >= 8:
        intensity_descriptors.extend(["overwhelming", "all-consuming", "reality-altering"])
        themes.append(f"overwhelming {motif.category.value}")
    elif motif.intensity >= 6:
        intensity_descriptors.extend(["powerful", "dominant", "undeniable"])
        themes.append(f"prominent {motif.category.value}")
    elif motif.intensity >= 4:
        intensity_descriptors.extend(["noticeable", "present", "influential"])
        themes.append(f"noticeable {motif.category.value}")
    else:
        intensity_descriptors.extend(["subtle", "gentle", "whispered"])
        themes.append(f"subtle {motif.category.value}")
    
    # Extract effect descriptions with more detail
    effect_descriptions = []
    npc_effects = []
    environmental_effects = []
    narrative_effects = []
    
    for effect in motif.effects:
        if effect.target == MotifEffectTarget.NPC:
            npc_effects.append(f"NPCs exhibit {motif.category.value}-influenced behavior")
            effect_descriptions.append(f"Characters are drawn toward {motif.category.value}-related actions")
        elif effect.target == MotifEffectTarget.EVENT:
            effect_descriptions.append(f"Events related to {motif.category.value} manifest more frequently")
        elif effect.target == MotifEffectTarget.ENVIRONMENT:
            environmental_effects.append(f"The environment reflects the essence of {motif.category.value}")
            effect_descriptions.append(f"The very air seems charged with {motif.category.value}")
        elif effect.target == MotifEffectTarget.NARRATIVE:
            narrative_effects.append(f"Stories naturally gravitate toward themes of {motif.category.value}")
    
    # Estimate remaining duration
    remaining_days = 0
    if motif.end_time:
        now = datetime.now()
        if motif.end_time > now:
            remaining_days = (motif.end_time - now).days
    elif motif.start_time and motif.duration_days:
        end_time = motif.start_time + timedelta(days=motif.duration_days)
        now = datetime.now()
        if end_time > now:
            remaining_days = (end_time - now).days
    
    # Build the comprehensive context dictionary
    context = {
        "name": motif.name,
        "description": motif.description,
        "category": motif.category.value,
        "scope": motif.scope.value,
        "intensity": motif.intensity,
        "lifecycle": motif.lifecycle.value,
        "themes": themes,
        "effects": effect_descriptions,
        "descriptive_elements": descriptive_elements,
        "emotional_tone": emotional_tone,
        "intensity_descriptors": intensity_descriptors,
        "npc_effects": npc_effects,
        "environmental_effects": environmental_effects,
        "narrative_effects": narrative_effects,
        "remaining_days": remaining_days,
        "is_dominant": motif.intensity >= 7,
        "is_fading": motif.lifecycle in [MotifLifecycle.WANING, MotifLifecycle.DORMANT],
        "is_growing": motif.lifecycle == MotifLifecycle.EMERGING,
        "tags": motif.tags,
        "associated_elements": motif.associated_elements,
        "opposing_themes": motif.opposing_themes,
        "narrative_guidance": motif.narrative_guidance,
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
        # Global motifs affect everywhere equally
        if origin_motif.scope == MotifScope.GLOBAL:
            return {
                "original_id": origin_motif.id,
                "original_intensity": origin_motif.intensity,
                "new_intensity": origin_motif.intensity,
                "distance": distance,
                "decay_factor": 1.0,
                "category": origin_motif.category.value,
                "is_significant": origin_motif.intensity >= 3.0,
                "spread_type": "global"
            }
        return None
    
    # Adjust max distance based on scope
    scope_distances = {
        MotifScope.LOCAL: max_distance * 0.3,
        MotifScope.REGIONAL: max_distance * 1.0,
        MotifScope.GLOBAL: float('inf')
    }
    
    effective_max_distance = scope_distances[origin_motif.scope]
    
    # Check if we're beyond the maximum effective range
    if distance > effective_max_distance:
        return None
    
    # Calculate intensity decay based on distance with more sophisticated curve
    # Use exponential decay: intensity = original * e^(-k*distance)
    # where k is determined by scope and intensity
    decay_constant = 0.1 / (origin_motif.intensity / 5.0)  # Higher intensity spreads better
    
    if origin_motif.scope == MotifScope.LOCAL:
        decay_constant *= 2.0  # Local motifs decay faster
    elif origin_motif.scope == MotifScope.GLOBAL:
        decay_constant = 0.0  # Global motifs don't decay
    
    intensity_multiplier = math.exp(-decay_constant * distance)
    new_intensity = origin_motif.intensity * intensity_multiplier
    
    # If intensity is too low, no effect
    if new_intensity < 0.5:
        return None
    
    # Create spread parameters
    spread = {
        "original_id": origin_motif.id,
        "original_intensity": origin_motif.intensity,
        "new_intensity": new_intensity,
        "distance": distance,
        "decay_factor": intensity_multiplier,
        "category": origin_motif.category.value,
        "is_significant": new_intensity >= 3.0,
        "spread_type": origin_motif.scope.value,
        "effective_radius": effective_max_distance,
        "decay_constant": decay_constant,
    }
    
    return spread

def motif_effect_to_text(effect: MotifEffect) -> str:
    """Convert a motif effect to a human-readable text description."""
    intensity_text = (
        "overwhelmingly" if effect.intensity >= 8 else
        "strongly" if effect.intensity >= 6 else
        "moderately" if effect.intensity >= 4 else
        "mildly" if effect.intensity >= 2 else
        "barely"
    )
    
    if effect.target == MotifEffectTarget.NPC:
        return f"NPCs are {intensity_text} influenced in their behavior and decision-making."
    
    elif effect.target == MotifEffectTarget.EVENT:
        return f"Related events occur {intensity_text} more frequently and with greater impact."
    
    elif effect.target == MotifEffectTarget.QUEST:
        return f"Quest development and outcomes are {intensity_text} influenced."
    
    elif effect.target == MotifEffectTarget.FACTION:
        return f"Faction relationships and tensions are {intensity_text} affected."
    
    elif effect.target == MotifEffectTarget.ENVIRONMENT:
        return f"Environmental conditions and atmosphere are {intensity_text} altered."
    
    elif effect.target == MotifEffectTarget.ECONOMY:
        return f"Economic factors like prices and availability are {intensity_text} shifted."
    
    elif effect.target == MotifEffectTarget.NARRATIVE:
        return f"The narrative atmosphere and story direction are {intensity_text} affected."
    
    elif effect.target == MotifEffectTarget.CUSTOM:
        return f"Custom effect with {intensity_text} intensity: {effect.description}"
    
    else:
        return f"Effect on {effect.target} with {intensity_text} intensity: {effect.description}"

def roll_chaos_event():
    """
    Generate a random chaos event from the predefined narrative chaos table.
    
    Returns:
        str: A randomly selected chaos event description
    """
    return random.choice(NARRATIVE_CHAOS_TABLE)

# ===== Advanced Analysis Functions =====

def analyze_motif_ecosystem(motifs: List[Motif]) -> Dict[str, Any]:
    """
    Analyze a collection of motifs to understand their ecosystem and interactions.
    """
    if not motifs:
        return {"error": "No motifs provided for analysis"}
    
    # Category distribution
    category_counts = defaultdict(int)
    scope_counts = defaultdict(int)
    lifecycle_counts = defaultdict(int)
    
    total_intensity = 0
    high_intensity_motifs = []
    conflicting_pairs = []
    harmonious_pairs = []
    
    for motif in motifs:
        category_counts[motif.category.value] += 1
        scope_counts[motif.scope.value] += 1
        lifecycle_counts[motif.lifecycle.value] += 1
        total_intensity += motif.intensity
        
        if motif.intensity >= 7:
            high_intensity_motifs.append(motif.id)
    
    # Analyze relationships between motifs
    for i, motif1 in enumerate(motifs):
        for motif2 in motifs[i+1:]:
            compatibility = estimate_motif_compatibility(motif1, motif2)
            if compatibility <= -0.5:
                conflicting_pairs.append({
                    "motif1": motif1.id,
                    "motif2": motif2.id,
                    "compatibility": compatibility
                })
            elif compatibility >= 0.5:
                harmonious_pairs.append({
                    "motif1": motif1.id,
                    "motif2": motif2.id,
                    "compatibility": compatibility
                })
    
    average_intensity = total_intensity / len(motifs) if motifs else 0
    
    return {
        "total_motifs": len(motifs),
        "category_distribution": dict(category_counts),
        "scope_distribution": dict(scope_counts),
        "lifecycle_distribution": dict(lifecycle_counts),
        "average_intensity": round(average_intensity, 2),
        "high_intensity_motifs": high_intensity_motifs,
        "conflicting_pairs": conflicting_pairs,
        "harmonious_pairs": harmonious_pairs,
        "ecosystem_health": "stable" if len(conflicting_pairs) <= len(harmonious_pairs) else "unstable"
    }

def suggest_motif_narrative_hooks(motif: Motif) -> List[str]:
    """
    Generate narrative hooks and story ideas based on a motif.
    """
    hooks = []
    
    category_hooks = {
        MotifCategory.BETRAYAL: [
            "A trusted ally's true allegiance is questioned",
            "Secret meetings happen in shadowed corners",
            "Old letters reveal hidden motives",
            "A character must choose between conflicting loyalties"
        ],
        MotifCategory.HOPE: [
            "A beacon of light appears in the darkest hour",
            "An unexpected ally offers assistance",
            "Ancient prophecies speak of better times",
            "Small acts of kindness ripple outward"
        ],
        MotifCategory.FEAR: [
            "Shadows seem to move when no one is watching",
            "Whispered warnings speak of approaching danger",
            "Characters hesitate before important decisions",
            "The unknown lurks just beyond perception"
        ],
        MotifCategory.POWER: [
            "Ancient artifacts pulse with forgotten energy",
            "Political machinations shift the balance",
            "Raw force bends reality to its will",
            "Those in charge make increasingly bold demands"
        ]
    }
    
    # Get category-specific hooks
    base_hooks = category_hooks.get(motif.category, [
        f"The influence of {motif.category.value} touches everything",
        f"Characters find themselves drawn toward {motif.category.value}",
        f"The world seems saturated with {motif.category.value}"
    ])
    
    # Modify based on intensity
    if motif.intensity >= 7:
        intensity_modifier = "The overwhelming presence of this force"
        hooks.extend([f"{intensity_modifier} {hook.lower()}" for hook in base_hooks])
    elif motif.intensity >= 4:
        hooks.extend(base_hooks)
    else:
        hooks.extend([f"Subtle hints suggest that {hook.lower()}" for hook in base_hooks])
    
    # Add scope-specific modifications
    if motif.scope == MotifScope.GLOBAL:
        hooks.append("This influence affects kingdoms and nations across the world")
    elif motif.scope == MotifScope.REGIONAL:
        hooks.append("The entire region resonates with this energy")
    else:
        hooks.append("Local inhabitants notice strange changes in their daily lives")
    
    return hooks[:6]  # Return top 6 hooks

def generate_motif_interaction_effects(motif1: Motif, motif2: Motif) -> Dict[str, Any]:
    """
    Generate the effects when two motifs interact or overlap.
    """
    compatibility = estimate_motif_compatibility(motif1, motif2)
    overlap = calculate_motif_overlap(motif1, motif2) if motif1.location and motif2.location else 1.0
    
    interaction = {
        "motif1_id": motif1.id,
        "motif2_id": motif2.id,
        "compatibility": compatibility,
        "overlap": overlap,
        "interaction_strength": overlap * abs(compatibility),
    }
    
    if compatibility > 0.5:
        # Harmonious interaction
        interaction["type"] = "synergistic"
        interaction["effects"] = [
            "Both motifs are strengthened by their proximity",
            "Narrative themes reinforce each other",
            "Combined intensity creates a more powerful presence"
        ]
        interaction["combined_intensity"] = min(10, (motif1.intensity + motif2.intensity) * 0.6)
        
    elif compatibility < -0.5:
        # Conflicting interaction
        interaction["type"] = "antagonistic"
        interaction["effects"] = [
            "The motifs work against each other",
            "Tension and contradiction arise in the narrative",
            "Weaker motif may be suppressed or transformed"
        ]
        stronger_motif = motif1 if motif1.intensity > motif2.intensity else motif2
        interaction["dominant_motif"] = stronger_motif.id
        interaction["combined_intensity"] = abs(motif1.intensity - motif2.intensity)
        
    else:
        # Neutral interaction
        interaction["type"] = "neutral"
        interaction["effects"] = [
            "The motifs coexist without strong interaction",
            "Each maintains its individual character",
            "Minimal interference between themes"
        ]
        interaction["combined_intensity"] = (motif1.intensity + motif2.intensity) / 2
    
    return interaction

def calculate_motif_narrative_weight(motifs: List[Motif], location: Optional[Point] = None) -> Dict[str, float]:
    """
    Calculate the narrative weight of different themes at a given location.
    """
    theme_weights = defaultdict(float)
    
    for motif in motifs:
        # Calculate influence at location
        influence = motif.intensity
        
        if location and motif.location:
            motif_center = Point(motif.location.x or 0, motif.location.y or 0)
            distance = calculate_distance(location, motif_center)
            spread_info = calculate_motif_spread(motif, distance)
            
            if spread_info:
                influence = spread_info["new_intensity"]
            else:
                influence = 0  # Out of range
        
        # Add to theme weight
        theme_weights[motif.category.value] += influence
        
        # Add associated themes with reduced weight
        for theme in motif.associated_elements:
            theme_weights[theme] += influence * 0.3
    
    return dict(theme_weights)

def optimize_motif_placement(motifs: List[Motif], area_bounds: Tuple[float, float, float, float]) -> List[Dict[str, Any]]:
    """
    Suggest optimal placement for motifs within a given area to minimize conflicts.
    area_bounds: (min_x, min_y, max_x, max_y)
    """
    min_x, min_y, max_x, max_y = area_bounds
    suggestions = []
    
    # Simple grid-based placement strategy
    grid_size = int(math.sqrt(len(motifs))) + 1
    cell_width = (max_x - min_x) / grid_size
    cell_height = (max_y - min_y) / grid_size
    
    for i, motif in enumerate(motifs):
        grid_x = i % grid_size
        grid_y = i // grid_size
        
        suggested_x = min_x + (grid_x + 0.5) * cell_width
        suggested_y = min_y + (grid_y + 0.5) * cell_height
        
        # Check for conflicts with other motifs
        conflicts = []
        for j, other_motif in enumerate(motifs):
            if i != j:
                compatibility = estimate_motif_compatibility(motif, other_motif)
                if compatibility < -0.3:
                    conflicts.append(other_motif.id)
        
        suggestions.append({
            "motif_id": motif.id,
            "suggested_location": {"x": suggested_x, "y": suggested_y},
            "conflicts": conflicts,
            "isolation_needed": len(conflicts) > 0
        })
    
    return suggestions 
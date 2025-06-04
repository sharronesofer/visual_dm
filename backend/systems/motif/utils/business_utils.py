"""
Business logic utilities for motif system.
Contains narrative generation, game logic, and motif interaction functions.
"""

from typing import List, Dict, Any, Optional, Tuple
import random
from collections import defaultdict

from backend.infrastructure.systems.motif.models import (
    Motif, MotifCategory, MotifScope, MotifEffect, MotifEffectTarget, MotifLifecycle
)

# Import configuration system
from backend.infrastructure.config.motif_config_loader import config

# ===== Chaos Utility Functions =====

# For backward compatibility, also export the table
NARRATIVE_CHAOS_TABLE = config.get_chaos_events()

def roll_chaos_event(category: Optional[str] = None):
    """Roll a random chaos event from the narrative chaos table."""
    return random.choice(config.get_chaos_events(category))

# ===== Motif Generation and Naming =====

def generate_motif_name(category: MotifCategory, scope: MotifScope) -> str:
    """Generate a thematic name for a motif based on its category and scope."""
    
    # Get name components from configuration
    name_data = config.get_name_components(category.value if hasattr(category, 'value') else str(category))
    
    # Get base names and modifiers from config
    base_names = name_data.get("base_names", ["Unknown"])
    modifiers = name_data.get("modifiers", [""])
    
    # Combine randomly
    base = random.choice(base_names)
    modifier = random.choice(modifiers)
    
    if modifier and not modifier.startswith("of"):
        return f"{modifier} {base}"
    elif modifier:
        return f"{base} {modifier}"
    else:
        return base

def generate_motif_description(category: MotifCategory, scope: MotifScope, intensity: float) -> str:
    """Generate a thematic description for a motif."""
    
    # Intensity descriptors
    intensity_words = {
        1: "faint", 2: "subtle", 3: "noticeable", 4: "clear", 5: "strong",
        6: "powerful", 7: "intense", 8: "overwhelming", 9: "dominant", 10: "absolute"
    }
    
    intensity_word = intensity_words.get(int(intensity), "moderate")
    
    # Category descriptions
    category_descriptions = {
        MotifCategory.BETRAYAL: f"A {intensity_word} sense of broken trust and deception permeates the area",
        MotifCategory.CHAOS: f"An {intensity_word} aura of unpredictability and disorder affects everything",
        MotifCategory.DEATH: f"A {intensity_word} presence of mortality and endings hangs heavy",
        MotifCategory.HOPE: f"An {intensity_word} feeling of optimism and possibility fills the air",
        MotifCategory.POWER: f"A {intensity_word} emanation of authority and control dominates",
        MotifCategory.REDEMPTION: f"An {intensity_word} atmosphere of second chances and renewal prevails",
        # Add more as needed
    }
    
    base_desc = category_descriptions.get(
        category, 
        f"A {intensity_word} thematic influence of {category.value if hasattr(category, 'value') else str(category)} is present"
    )
    
    # Add scope context
    scope_context = {
        MotifScope.GLOBAL: "across the entire world",
        MotifScope.REGIONAL: "throughout this region", 
        MotifScope.LOCAL: "in this specific location",
        MotifScope.PLAYER_CHARACTER: "around the player character"
    }
    
    context = scope_context.get(scope, "in the area")
    
    return f"{base_desc} {context}."

# ===== Motif Compatibility and Interaction =====

def estimate_motif_compatibility(motif1: Motif, motif2: Motif) -> float:
    """
    Estimate how compatible two motifs are (0.0 = completely incompatible, 1.0 = perfectly compatible).
    Uses configuration data for theme relationships.
    """
    
    # Get theme relationship data from configuration
    opposing_pairs = config.get_opposing_themes()
    complementary_pairs = config.get_complementary_themes()
    
    # Get category values for comparison
    cat1 = motif1.category.value if hasattr(motif1.category, 'value') else str(motif1.category)
    cat2 = motif2.category.value if hasattr(motif2.category, 'value') else str(motif2.category)
    
    # Check if motifs are directly opposing using configuration
    if config.are_themes_opposing(cat1, cat2):
        # Opposing motifs - compatibility depends on intensity difference
        intensity_diff = abs(motif1.intensity - motif2.intensity)
        # Lower intensity difference = more conflict
        return max(0.0, (intensity_diff - 2) / 8.0)
    
    # Check if motifs are complementary using configuration
    if config.are_themes_complementary(cat1, cat2):
        return 0.8 + (min(motif1.intensity, motif2.intensity) / 50.0)
    
    # Same category motifs are generally compatible
    if motif1.category == motif2.category:
        return 0.7 + (min(motif1.intensity, motif2.intensity) / 30.0)
    
    # Default compatibility for unrelated motifs
    return 0.5

def generate_realistic_duration(scope: MotifScope, intensity: float) -> int:
    """Generate a realistic duration in days for a motif based on scope and intensity."""
    
    base_durations = {
        MotifScope.GLOBAL: (30, 365),      # 1 month to 1 year
        MotifScope.REGIONAL: (7, 90),      # 1 week to 3 months  
        MotifScope.LOCAL: (1, 30),         # 1 day to 1 month
        MotifScope.PLAYER_CHARACTER: (1, 14)  # 1 day to 2 weeks
    }
    
    min_days, max_days = base_durations.get(scope, (7, 30))
    
    # Higher intensity = longer duration
    intensity_multiplier = 0.5 + (intensity / 20.0)  # 0.5 to 1.0
    
    # Calculate duration with some randomness
    base_duration = min_days + (max_days - min_days) * intensity_multiplier
    randomized_duration = base_duration * random.uniform(0.7, 1.3)
    
    return max(1, int(randomized_duration))

def motif_to_narrative_context(motif: Motif) -> Dict[str, Any]:
    """
    Convert a motif to a narrative context dictionary suitable for story generation.
    """
    
    # Generate narrative hooks based on category
    narrative_hooks = {
        MotifCategory.BETRAYAL: [
            "Trust is fragile and easily broken",
            "Allies may harbor hidden agendas", 
            "Past loyalties are questioned",
            "Secrets threaten to surface"
        ],
        MotifCategory.REDEMPTION: [
            "Second chances are possible",
            "Past mistakes can be overcome",
            "Forgiveness is within reach",
            "Transformation is achievable"
        ],
        MotifCategory.POWER: [
            "Authority shapes all interactions",
            "Hierarchies determine outcomes",
            "Influence flows through established channels",
            "Control is the ultimate currency"
        ],
        # Add more as needed
    }
    
    hooks = narrative_hooks.get(motif.category, [
        f"The theme of {motif.category.value} influences events",
        f"Elements of {motif.category.value} appear in interactions"
    ])
    
    # Generate mood descriptors
    mood_descriptors = {
        MotifCategory.CHAOS: ["unpredictable", "volatile", "unstable", "turbulent"],
        MotifCategory.HOPE: ["optimistic", "uplifting", "inspiring", "bright"],
        MotifCategory.DEATH: ["somber", "heavy", "final", "melancholic"],
        MotifCategory.POWER: ["commanding", "authoritative", "dominant", "imposing"],
        # Add more as needed
    }
    
    mood = mood_descriptors.get(motif.category, ["thematic", "influential"])
    
    return {
        "motif_id": motif.id,
        "name": motif.name,
        "category": motif.category.value,
        "intensity": motif.intensity,
        "scope": motif.scope.value,
        "narrative_hooks": hooks,
        "mood_descriptors": mood,
        "theme": motif.theme,
        "tone": getattr(motif, 'tone', 'neutral'),
        "narrative_direction": getattr(motif, 'narrative_direction', 'steady'),
        "descriptors": getattr(motif, 'descriptors', []),
        "lifecycle": motif.lifecycle.value,
        "effects_summary": [effect.description for effect in motif.effects]
    }

# ===== Motif Analysis and Ecosystem Functions =====

def analyze_motif_ecosystem(motifs: List[Motif]) -> Dict[str, Any]:
    """
    Analyze a collection of motifs to understand their ecosystem dynamics.
    """
    if not motifs:
        return {
            "total_motifs": 0,
            "dominant_categories": [],
            "average_intensity": 0,
            "scope_distribution": {},
            "potential_conflicts": [],
            "narrative_themes": []
        }
    
    # Basic statistics
    total_motifs = len(motifs)
    total_intensity = sum(motif.intensity for motif in motifs)
    average_intensity = total_intensity / total_motifs if total_motifs > 0 else 0
    
    # Category analysis
    category_counts = defaultdict(int)
    category_intensities = defaultdict(list)
    
    for motif in motifs:
        category_counts[motif.category] += 1
        category_intensities[motif.category].append(motif.intensity)
    
    # Find dominant categories (by count and intensity)
    dominant_categories = sorted(
        category_counts.items(),
        key=lambda x: (x[1], sum(category_intensities[x[0]])),
        reverse=True
    )[:3]
    
    # Scope distribution
    scope_distribution = defaultdict(int)
    for motif in motifs:
        scope_distribution[motif.scope.value] += 1
    
    # Detect potential conflicts
    potential_conflicts = []
    for i, motif1 in enumerate(motifs):
        for motif2 in motifs[i+1:]:
            compatibility = estimate_motif_compatibility(motif1, motif2)
            if compatibility < 0.3:  # Low compatibility indicates conflict
                potential_conflicts.append({
                    "motif1": motif1.name,
                    "motif2": motif2.name,
                    "compatibility": compatibility,
                    "conflict_type": "thematic_opposition"
                })
    
    # Extract narrative themes
    narrative_themes = []
    for category, count in dominant_categories:
        avg_intensity = sum(category_intensities[category]) / len(category_intensities[category])
        if avg_intensity >= 6:
            narrative_themes.append(f"strong_{category.value}")
        elif avg_intensity >= 4:
            narrative_themes.append(f"moderate_{category.value}")
        else:
            narrative_themes.append(f"subtle_{category.value}")
    
    return {
        "total_motifs": total_motifs,
        "dominant_categories": [cat.value for cat, count in dominant_categories],
        "average_intensity": round(average_intensity, 2),
        "scope_distribution": dict(scope_distribution),
        "potential_conflicts": potential_conflicts,
        "narrative_themes": narrative_themes,
        "ecosystem_stability": 1.0 - (len(potential_conflicts) / max(1, total_motifs)),
        "thematic_diversity": len(category_counts) / max(1, total_motifs)
    }

def suggest_motif_narrative_hooks(motif: Motif) -> List[str]:
    """
    Generate narrative hooks and story suggestions based on a motif.
    """
    
    category_hooks = {
        MotifCategory.BETRAYAL: [
            "A trusted ally reveals their true allegiance",
            "Secret correspondence exposes hidden motives",
            "A character's past catches up with them",
            "Loyalties are tested by difficult choices"
        ],
        MotifCategory.REDEMPTION: [
            "A chance to right past wrongs appears",
            "Forgiveness becomes possible through sacrifice",
            "A character seeks to atone for their mistakes",
            "Second chances are offered to the undeserving"
        ],
        MotifCategory.POWER: [
            "Authority is challenged by unexpected opposition",
            "The cost of control becomes apparent",
            "Power corrupts those who wield it",
            "Hierarchies shift due to changing circumstances"
        ],
        MotifCategory.CHAOS: [
            "Order breaks down in unexpected ways",
            "Random events disrupt careful plans",
            "Unpredictable forces enter the scene",
            "Stability proves to be an illusion"
        ],
        MotifCategory.HOPE: [
            "Light appears in the darkest moment",
            "Unexpected help arrives when needed most",
            "A new possibility emerges from despair",
            "Faith is rewarded with positive change"
        ],
        # Add more categories as needed
    }
    
    base_hooks = category_hooks.get(motif.category, [
        f"The influence of {motif.category.value} creates new opportunities",
        f"Characters must deal with the effects of {motif.category.value}",
        f"The theme of {motif.category.value} shapes upcoming events"
    ])
    
    # Modify hooks based on intensity
    if motif.intensity >= 8:
        intensity_modifier = "overwhelmingly"
    elif motif.intensity >= 6:
        intensity_modifier = "strongly"
    elif motif.intensity >= 4:
        intensity_modifier = "noticeably"
    else:
        intensity_modifier = "subtly"
    
    # Modify hooks based on scope
    scope_modifiers = {
        MotifScope.GLOBAL: "affecting the entire world",
        MotifScope.REGIONAL: "impacting the local region",
        MotifScope.LOCAL: "influencing this specific area",
        MotifScope.PLAYER_CHARACTER: "centered around the player character"
    }
    
    scope_modifier = scope_modifiers.get(motif.scope, "in the area")
    
    # Combine base hooks with modifiers
    modified_hooks = []
    for hook in base_hooks:
        modified_hook = f"{hook}, {intensity_modifier} {scope_modifier}"
        modified_hooks.append(modified_hook)
    
    return modified_hooks

def generate_motif_interaction_effects(motif1: Motif, motif2: Motif) -> Dict[str, Any]:
    """
    Generate the effects of two motifs interacting with each other.
    """
    compatibility = estimate_motif_compatibility(motif1, motif2)
    
    interaction_type = "neutral"
    if compatibility < 0.3:
        interaction_type = "conflict"
    elif compatibility > 0.7:
        interaction_type = "synergy"
    
    effects = {
        "interaction_type": interaction_type,
        "compatibility_score": compatibility,
        "combined_intensity": min(10, (motif1.intensity + motif2.intensity) / 2),
        "narrative_result": "",
        "mechanical_effects": []
    }
    
    if interaction_type == "conflict":
        effects["narrative_result"] = f"The {motif1.category.value} and {motif2.category.value} themes create tension and contradiction"
        effects["mechanical_effects"] = [
            "Increased unpredictability in events",
            "NPCs may be conflicted or confused",
            "Narrative tension increases"
        ]
    elif interaction_type == "synergy":
        effects["narrative_result"] = f"The {motif1.category.value} and {motif2.category.value} themes reinforce each other"
        effects["mechanical_effects"] = [
            "Enhanced thematic consistency",
            "Stronger narrative direction",
            "Amplified motif effects"
        ]
    else:
        effects["narrative_result"] = f"The {motif1.category.value} and {motif2.category.value} themes coexist without major interaction"
        effects["mechanical_effects"] = [
            "Parallel narrative threads",
            "Diverse thematic elements",
            "Balanced influence"
        ]
    
    return effects

def calculate_motif_narrative_weight(motifs: List[Motif], location: Optional[Any] = None) -> Dict[str, float]:
    """
    Calculate the narrative weight of different themes based on active motifs.
    """
    if not motifs:
        return {}
    
    theme_weights = defaultdict(float)
    total_intensity = sum(motif.intensity for motif in motifs)
    
    if total_intensity == 0:
        return {}
    
    for motif in motifs:
        # Base weight from intensity
        base_weight = motif.intensity / total_intensity
        
        # Scope modifier
        scope_multipliers = {
            MotifScope.GLOBAL: 1.0,
            MotifScope.REGIONAL: 0.8,
            MotifScope.LOCAL: 0.6,
            MotifScope.PLAYER_CHARACTER: 0.7
        }
        
        scope_modifier = scope_multipliers.get(motif.scope, 1.0)
        
        # Lifecycle modifier
        lifecycle_multipliers = {
            MotifLifecycle.EMERGING: 0.7,
            MotifLifecycle.STABLE: 1.0,
            MotifLifecycle.WANING: 0.5,
            MotifLifecycle.DORMANT: 0.1,
            MotifLifecycle.CONCLUDED: 0.0
        }
        
        lifecycle_modifier = lifecycle_multipliers.get(motif.lifecycle, 1.0)
        
        final_weight = base_weight * scope_modifier * lifecycle_modifier
        theme_weights[motif.category.value] += final_weight
    
    # Normalize weights to sum to 1.0
    total_weight = sum(theme_weights.values())
    if total_weight > 0:
        theme_weights = {theme: weight / total_weight for theme, weight in theme_weights.items()}
    
    return dict(theme_weights)

def optimize_motif_placement(motifs: List[Motif], area_bounds: Tuple[float, float, float, float]) -> List[Dict[str, Any]]:
    """
    Suggest optimal placement for motifs within an area to minimize conflicts and maximize narrative coherence.
    """
    min_x, min_y, max_x, max_y = area_bounds
    area_width = max_x - min_x
    area_height = max_y - min_y
    
    placement_suggestions = []
    
    for motif in motifs:
        if motif.scope == MotifScope.GLOBAL:
            # Global motifs don't need specific placement
            placement_suggestions.append({
                "motif_id": motif.id,
                "placement_type": "global",
                "suggested_location": None,
                "reasoning": "Global scope affects entire area"
            })
            continue
        
        # For regional and local motifs, suggest placement based on compatibility
        compatible_motifs = []
        conflicting_motifs = []
        
        for other_motif in motifs:
            if other_motif.id == motif.id:
                continue
            
            compatibility = estimate_motif_compatibility(motif, other_motif)
            if compatibility > 0.7:
                compatible_motifs.append(other_motif)
            elif compatibility < 0.3:
                conflicting_motifs.append(other_motif)
        
        # Suggest placement strategy
        if conflicting_motifs:
            # Place away from conflicting motifs
            suggested_x = min_x + area_width * random.uniform(0.2, 0.8)
            suggested_y = min_y + area_height * random.uniform(0.2, 0.8)
            reasoning = f"Placed to minimize conflict with {len(conflicting_motifs)} opposing motifs"
        elif compatible_motifs:
            # Place near compatible motifs
            suggested_x = min_x + area_width * random.uniform(0.3, 0.7)
            suggested_y = min_y + area_height * random.uniform(0.3, 0.7)
            reasoning = f"Placed to synergize with {len(compatible_motifs)} compatible motifs"
        else:
            # Neutral placement
            suggested_x = min_x + area_width * 0.5
            suggested_y = min_y + area_height * 0.5
            reasoning = "Central placement for neutral thematic influence"
        
        placement_suggestions.append({
            "motif_id": motif.id,
            "placement_type": "positioned",
            "suggested_location": {"x": suggested_x, "y": suggested_y},
            "reasoning": reasoning,
            "compatible_motifs": [m.id for m in compatible_motifs],
            "conflicting_motifs": [m.id for m in conflicting_motifs]
        })
    
    return placement_suggestions 
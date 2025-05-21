#This utility defines the canonical motif vocabulary, motif generation logic, and lifecycle rule for rotation. It's a key backbone for NPC identity, chaos progression, and narrative theme escalation.
#It supports the motif, npc, chaos, and narrative systems.

from random import randint
from datetime import datetime
from typing import List, Dict, Any, Tuple, Optional
import random
import math
import numpy as np
from enum import Enum
from pydantic import BaseModel

from backend.systems.motif.models import Motif, MotifLifecycle
import backend.systems.motif.chaos_utils as chaos_utils

CANONICAL_MOTIFS = [
    "Ascension", "Betrayal", "Chaos", "Collapse", "Compulsion", "Control",
    "Death", "Deception", "Defiance", "Desire", "Destiny", "Echo", "Expansion",
    "Faith", "Fear", "Futility", "Grief", "Guilt", "Hope", "Hunger", "Innocence",
    "Invention", "Isolation", "Justice", "Loyalty", "Madness", "Obsession",
    "Paranoia", "Power", "Pride", "Protection", "Rebirth", "Redemption",
    "Regret", "Revelation", "Ruin", "Sacrifice", "Silence", "Shadow",
    "Stagnation", "Temptation", "Time", "Transformation", "Truth", "Unity",
    "Vengeance", "Worship"
]

def roll_new_motif(exclude=None, chaos_source=False):
    exclude = exclude or []
    options = [m for m in CANONICAL_MOTIFS if m not in exclude]
    theme = random.choice(options)
    lifespan = random.randint(2, 4)
    motif = {
        "theme": theme,
        "lifespan": lifespan,
        "entropy_tick": 0,
        "weight": 6 - lifespan
    }
    if chaos_source:
        motif["chaos_source"] = True
    return motif

def motif_needs_rotation(motif):
    return motif["entropy_tick"] <= 0


def generate_motif():
    life = randint(2, 4)
    return {
        "theme": randint(1, 50),
        "lifespan": life,
        "entropy_tick": 0,
        "weight": 6 - life
    }

def init_motif_pool(n=3):
    return {
        "active_motifs": [generate_motif() for _ in range(n)],
        "motif_history": [],
        "last_rotated": datetime.utcnow().isoformat()
    }

def rotate_expired_motifs(pool):
    rotated = False
    now = datetime.utcnow().isoformat()
    active = []

    for motif in pool.get("active_motifs", []):
        motif["entropy_tick"] += 1
        if motif["entropy_tick"] < motif["lifespan"]:
            active.append(motif)
        else:
            rotated = True
            pool.setdefault("motif_history", []).append(motif["theme"])

    while len(active) < 3:
        active.append(generate_motif())

    if rotated:
        pool["last_rotated"] = now

    pool["active_motifs"] = active
    return pool

def synthesize_motifs(motifs: List[Motif]) -> Dict[str, Any]:
    """
    Synthesize multiple motifs to produce a combined thematic effect.
    
    This is used when multiple motifs are active in a region to determine
    their combined narrative impact.
    
    Args:
        motifs: List of active motifs to synthesize
        
    Returns:
        Dictionary containing synthesized narrative elements
    """
    if not motifs:
        return {
            "theme": "None",
            "intensity": 0,
            "tone": "neutral",
            "narrative_direction": "steady",
            "descriptors": [],
            "conflicts": [],
            "dominant_motif": None,
            "synthesis_summary": "No active motifs present."
        }
    
    # Sort by intensity (descending)
    sorted_motifs = sorted(motifs, key=lambda m: m.intensity, reverse=True)
    
    # Find the dominant motif (highest intensity)
    dominant_motif = sorted_motifs[0]
    
    # Calculate weighted influence of each motif
    total_intensity = sum(m.intensity for m in motifs)
    motif_weights = {m.id: m.intensity / total_intensity for m in motifs}
    
    # Detect potential conflicts between motifs
    conflicts = []
    for i, motif1 in enumerate(motifs):
        for motif2 in motifs[i+1:]:
            if are_motifs_conflicting(motif1, motif2):
                conflicts.append((motif1.id, motif2.id))
    
    # Generate combined descriptors
    all_descriptors = []
    for motif in motifs:
        descriptors = motif.descriptors if hasattr(motif, 'descriptors') and motif.descriptors else []
        desc_weight = motif_weights[motif.id]
        # Select descriptors with probability based on motif weight
        for desc in descriptors:
            if random.random() < desc_weight * 1.5:  # 1.5x multiplier to include more descriptors
                all_descriptors.append(desc)
    
    # Ensure we have some descriptors
    if not all_descriptors and motifs:
        all_descriptors = [motifs[0].theme.lower()]
    
    # Limit to reasonable number
    all_descriptors = list(set(all_descriptors))[:5]
    
    # Determine overall tone based on weighted average
    tones = {"dark": 0, "neutral": 0, "light": 0}
    for motif in motifs:
        tone = getattr(motif, 'tone', 'neutral')
        tones[tone] += motif_weights[motif.id]
    
    max_tone = max(tones.items(), key=lambda x: x[1])[0]
    
    # Determine narrative direction
    directions = {"ascending": 0, "steady": 0, "descending": 0}
    for motif in motifs:
        # Default to steady if not specified
        direction = getattr(motif, 'narrative_direction', 'steady')
        directions[direction] += motif_weights[motif.id]
    
    max_direction = max(directions.items(), key=lambda x: x[1])[0]
    
    # Calculate composite intensity (weighted average, slightly favoring higher intensity)
    composite_intensity = 0
    for motif in motifs:
        composite_intensity += motif.intensity * motif_weights[motif.id] * 1.1
    
    # Cap at max intensity
    composite_intensity = min(round(composite_intensity), 10)
    
    # Create summary of the synthesis
    if conflicts:
        conflict_text = "Strong thematic conflict detected."
        conflict_motifs = [f"{get_motif_by_id(motifs, cid1).theme} vs {get_motif_by_id(motifs, cid2).theme}" 
                           for cid1, cid2 in conflicts[:2]]  # Limit to first 2 conflicts
        conflict_summary = f"{conflict_text} {', '.join(conflict_motifs)}"
    else:
        conflict_summary = "No significant thematic conflicts."
    
    # Primary theme is from dominant motif
    primary_theme = dominant_motif.theme
    
    return {
        "theme": primary_theme,
        "intensity": composite_intensity,
        "tone": max_tone,
        "narrative_direction": max_direction,
        "descriptors": all_descriptors,
        "conflicts": conflicts,
        "dominant_motif": dominant_motif.id,
        "synthesis_summary": f"The dominant theme is {primary_theme}. {conflict_summary}"
    }

def get_motif_by_id(motifs: List[Motif], motif_id: str) -> Optional[Motif]:
    """Helper function to get a motif by ID from a list"""
    for motif in motifs:
        if motif.id == motif_id:
            return motif
    return None

def are_motifs_conflicting(motif1: Motif, motif2: Motif) -> bool:
    """
    Determine if two motifs have conflicting themes.
    
    Args:
        motif1: First motif
        motif2: Second motif
        
    Returns:
        True if motifs conflict thematically, False otherwise
    """
    # Direct opposites (examples - could be expanded with more pairs)
    opposite_pairs = [
        ("growth", "decay"),
        ("life", "death"),
        ("order", "chaos"),
        ("creation", "destruction"),
        ("light", "darkness"),
        ("peace", "war"),
        ("hope", "despair"),
        ("love", "hate"),
        ("unity", "division"),
        ("abundance", "scarcity"),
        ("freedom", "oppression"),
        ("truth", "deception"),
    ]
    
    # Check for direct conflicts
    theme1 = motif1.theme.lower()
    theme2 = motif2.theme.lower()
    
    for opposite1, opposite2 in opposite_pairs:
        if ((opposite1 in theme1 and opposite2 in theme2) or
            (opposite2 in theme1 and opposite1 in theme2)):
            return True
    
    # Check tone conflicts (if tones are drastically different)
    tone1 = getattr(motif1, 'tone', 'neutral')
    tone2 = getattr(motif2, 'tone', 'neutral')
    
    if (tone1 == "dark" and tone2 == "light") or (tone1 == "light" and tone2 == "dark"):
        return True
    
    # Check narrative direction conflicts
    direction1 = getattr(motif1, 'narrative_direction', 'steady')
    direction2 = getattr(motif2, 'narrative_direction', 'steady')
    
    if (direction1 == "ascending" and direction2 == "descending") or (direction1 == "descending" and direction2 == "ascending"):
        return True
    
    return False

def get_region_motif_context(motifs: List[Motif], format_type: str = "descriptive") -> str:
    """
    Generate a narrative context description based on synthesized regional motifs.
    
    Args:
        motifs: List of active motifs in the region
        format_type: The format type for the context ("descriptive", "concise", or "gpt")
        
    Returns:
        A formatted string describing the motif context for the region
    """
    # Synthesize motifs
    synthesis = synthesize_motifs(motifs)
    
    if not motifs:
        if format_type == "gpt":
            return "No strong narrative themes. Events unfold naturally without external influence."
        else:
            return "No active motifs in this region."
    
    # Get the dominant motif
    dominant_motif = get_motif_by_id(motifs, synthesis["dominant_motif"])
    
    # Create appropriate context based on format type
    if format_type == "concise":
        return f"Region theme: {synthesis['theme']} (intensity: {synthesis['intensity']})"
        
    elif format_type == "gpt":
        # Format optimized for GPT context
        descriptors = ", ".join(synthesis["descriptors"]) if synthesis["descriptors"] else "neutral"
        conflict_text = ""
        if synthesis["conflicts"]:
            conflict_motifs = [f"{get_motif_by_id(motifs, cid1).theme}/{get_motif_by_id(motifs, cid2).theme}" 
                             for cid1, cid2 in synthesis["conflicts"][:1]]
            conflict_text = f" Thematic tension between {conflict_motifs[0]}."
        
        return (f"Regional theme: {synthesis['theme']} (intensity: {synthesis['intensity']}). "
                f"The narrative tone is {synthesis['tone']} with a {synthesis['narrative_direction']} trajectory. "
                f"Key motifs: {descriptors}.{conflict_text}")
    
    else:  # descriptive (default)
        conflicts = ""
        if synthesis["conflicts"]:
            conflict_pairs = []
            for cid1, cid2 in synthesis["conflicts"][:2]:  # Limit to first 2 conflicts
                m1 = get_motif_by_id(motifs, cid1)
                m2 = get_motif_by_id(motifs, cid2)
                if m1 and m2:
                    conflict_pairs.append(f"{m1.theme} and {m2.theme}")
            
            if conflict_pairs:
                conflicts = f" Thematic tension exists between {' and '.join(conflict_pairs)}."
        
        return (f"This region is dominated by the theme of {synthesis['theme']} "
                f"with an intensity of {synthesis['intensity']}. "
                f"The atmosphere is {synthesis['tone']}, and events are trending in a {synthesis['narrative_direction']} direction."
                f"{conflicts}")
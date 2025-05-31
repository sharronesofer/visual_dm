"""
Motif utilities module providing synthesis and helper functions.
"""

from typing import List, Dict, Optional, Any, Tuple
import random
from datetime import datetime

# Use fallback imports for missing dependencies
try:
    from backend.systems.motif.models import Motif
except ImportError:
    # Fallback mock class for resilience
    class Motif:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)


def synthesize_motifs(motifs: List[Motif]) -> Dict[str, Any]:
    """
    Synthesize a list of motifs into a unified narrative context.
    
    This function analyzes multiple active motifs and creates a cohesive
    narrative description that can be used for world generation, GPT context,
    or other narrative purposes.
    
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
    sorted_motifs = sorted(motifs, key=lambda m: getattr(m, 'intensity', 0), reverse=True)
    
    # Find the dominant motif (highest intensity)
    dominant_motif = sorted_motifs[0]
    
    # Calculate weighted influence of each motif
    total_intensity = sum(getattr(m, 'intensity', 0) for m in motifs)
    if total_intensity == 0:
        total_intensity = 1  # Avoid division by zero
    
    motif_weights = {getattr(m, 'id', str(i)): getattr(m, 'intensity', 0) / total_intensity 
                     for i, m in enumerate(motifs)}
    
    # Detect potential conflicts between motifs
    conflicts = []
    for i, motif1 in enumerate(motifs):
        for motif2 in motifs[i+1:]:
            if are_motifs_conflicting(motif1, motif2):
                conflicts.append((getattr(motif1, 'id', str(i)), 
                                getattr(motif2, 'id', str(i+1))))
    
    # Generate combined descriptors
    all_descriptors = []
    for motif in motifs:
        descriptors = getattr(motif, 'descriptors', [])
        if not descriptors:
            # Use theme as fallback descriptor
            theme = getattr(motif, 'theme', getattr(motif, 'category', 'neutral'))
            descriptors = [str(theme).lower()]
        
        desc_weight = motif_weights.get(getattr(motif, 'id', ''), 0)
        # Select descriptors with probability based on motif weight
        for desc in descriptors:
            if random.random() < desc_weight * 1.5:  # 1.5x multiplier to include more descriptors
                all_descriptors.append(desc)
    
    # Ensure we have some descriptors
    if not all_descriptors and motifs:
        theme = getattr(motifs[0], 'theme', getattr(motifs[0], 'category', 'neutral'))
        all_descriptors = [str(theme).lower()]
    
    # Limit to reasonable number
    all_descriptors = list(set(all_descriptors))[:5]
    
    # Determine overall tone based on weighted average
    tones = {"dark": 0, "neutral": 0, "light": 0}
    for motif in motifs:
        tone = getattr(motif, 'tone', 'neutral')
        if tone in tones:
            tones[tone] += motif_weights.get(getattr(motif, 'id', ''), 0)
    
    max_tone = max(tones.items(), key=lambda x: x[1])[0]
    
    # Determine narrative direction
    directions = {"ascending": 0, "steady": 0, "descending": 0}
    for motif in motifs:
        # Default to steady if not specified
        direction = getattr(motif, 'narrative_direction', 'steady')
        if direction in directions:
            directions[direction] += motif_weights.get(getattr(motif, 'id', ''), 0)
    
    max_direction = max(directions.items(), key=lambda x: x[1])[0]
    
    # Calculate composite intensity (weighted average, slightly favoring higher intensity)
    composite_intensity = 0
    for motif in motifs:
        intensity = getattr(motif, 'intensity', 0)
        weight = motif_weights.get(getattr(motif, 'id', ''), 0)
        composite_intensity += intensity * weight * 1.1
    
    # Cap at max intensity
    composite_intensity = min(round(composite_intensity), 10)
    
    # Create summary of the synthesis
    if conflicts:
        conflict_text = "Strong thematic conflict detected."
        conflict_motifs = []
        for cid1, cid2 in conflicts[:2]:  # Limit to first 2 conflicts
            motif1 = get_motif_by_id(motifs, cid1)
            motif2 = get_motif_by_id(motifs, cid2)
            if motif1 and motif2:
                theme1 = getattr(motif1, 'theme', getattr(motif1, 'category', 'unknown'))
                theme2 = getattr(motif2, 'theme', getattr(motif2, 'category', 'unknown'))
                conflict_motifs.append(f"{theme1} vs {theme2}")
        
        conflict_summary = f"{conflict_text} {', '.join(conflict_motifs)}" if conflict_motifs else conflict_text
    else:
        conflict_summary = "No significant thematic conflicts."
    
    # Primary theme is from dominant motif
    primary_theme = getattr(dominant_motif, 'theme', getattr(dominant_motif, 'category', 'neutral'))
    
    return {
        "theme": str(primary_theme),
        "intensity": composite_intensity,
        "tone": max_tone,
        "narrative_direction": max_direction,
        "descriptors": all_descriptors,
        "conflicts": conflicts,
        "dominant_motif": getattr(dominant_motif, 'id', None),
        "synthesis_summary": f"The dominant theme is {primary_theme}. {conflict_summary}"
    }


def get_motif_by_id(motifs: List[Motif], motif_id: str) -> Optional[Motif]:
    """Helper function to get a motif by ID from a list"""
    for motif in motifs:
        if getattr(motif, 'id', None) == motif_id:
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
    theme1 = str(getattr(motif1, 'theme', getattr(motif1, 'category', ''))).lower()
    theme2 = str(getattr(motif2, 'theme', getattr(motif2, 'category', ''))).lower()
    
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
    
    if ((direction1 == "ascending" and direction2 == "descending") or 
        (direction1 == "descending" and direction2 == "ascending")):
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
            conflict_motifs = []
            for cid1, cid2 in synthesis["conflicts"][:1]:
                motif1 = get_motif_by_id(motifs, cid1)
                motif2 = get_motif_by_id(motifs, cid2)
                if motif1 and motif2:
                    theme1 = getattr(motif1, 'theme', getattr(motif1, 'category', 'unknown'))
                    theme2 = getattr(motif2, 'theme', getattr(motif2, 'category', 'unknown'))
                    conflict_motifs.append(f"{theme1}/{theme2}")
            
            if conflict_motifs:
                conflict_text = f" Thematic tension between {conflict_motifs[0]}."
        
        return (f"Regional theme: {synthesis['theme']} (intensity: {synthesis['intensity']}). "
                f"The narrative tone is {synthesis['tone']} with a {synthesis['narrative_direction']} trajectory. "
                f"Key motifs: {descriptors}.{conflict_text}")
    
    else:  # descriptive (default)
        base_desc = f"This region is dominated by the theme of {synthesis['theme']} "
        base_desc += f"with an intensity of {synthesis['intensity']}/10. "
        
        if synthesis["descriptors"]:
            base_desc += f"The area is characterized by {', '.join(synthesis['descriptors'])}. "
        
        if synthesis["tone"] != "neutral":
            base_desc += f"The overall tone is {synthesis['tone']}. "
        
        if synthesis["narrative_direction"] != "steady":
            base_desc += f"The narrative direction is {synthesis['narrative_direction']}. "
        
        if synthesis["conflicts"]:
            base_desc += "There are conflicting themes creating tension in the region."
        
        return base_desc.strip()


# Mock functions for compatibility
def estimate_motif_compatibility(*args, **kwargs):
    """Mock function for compatibility"""
    return 0.5


def calculate_motif_spread(*args, **kwargs):
    """Mock function for compatibility"""
    return {"spread_radius": 100.0, "effectiveness": 0.8}
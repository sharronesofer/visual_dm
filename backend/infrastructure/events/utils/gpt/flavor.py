"""
GPT-based flavor text generation for items, effects, and relationships.
"""

from typing import Dict, Any, List, Optional
from .client import GPTClient

def gpt_flavor_identify_effect(item_name: str, effect: str) -> str:
    """
    Generate immersive text for revealing a single magical item effect.
    
    Args:
        item_name: Name of the magical item
        effect: The effect being revealed
        
    Returns:
        str: Generated flavor text describing the effect revelation
    """
    prompt = (
        f"The magical item '{item_name}' has revealed a new effect: {effect}.\n"
        "Describe what the character experiences or perceives as this effect becomes known. "
        "Use rich, mystical fantasy prose — keep it brief but evocative."
    )

    gpt = GPTClient()
    return gpt.call(
        system_prompt="You are a fantasy narrator describing magical item awakenings.",
        user_prompt=prompt,
        temperature=0.85,
        max_tokens=80
    )

def gpt_flavor_reveal_full_item(item: Dict[str, Any]) -> str:
    """
    Generate immersive text for when an item is fully identified.
    
    Args:
        item: Dictionary containing item data
        
    Returns:
        str: Generated flavor text for the full item reveal
    """
    name = item.get("identified_name", item.get("name", "Unknown Item"))
    effects = item.get("identified_effects", [])
    effect_list = ", ".join(effects) if effects else "mysterious latent properties"

    prompt = (
        f"The item '{name}' has now revealed all its effects: {effect_list}.\n"
        "Describe the culmination of the identification process and how the "
        "item's full nature becomes clear. Use rich, mystical fantasy prose."
    )

    gpt = GPTClient()
    return gpt.call(
        system_prompt="You are a fantasy narrator describing magical item awakenings.",
        user_prompt=prompt,
        temperature=0.85,
        max_tokens=150
    )

def get_goodwill_label(score: int) -> str:
    """
    Convert a numeric goodwill score into a descriptive label.
    
    Args:
        score: Numeric goodwill score
        
    Returns:
        str: Descriptive label for the goodwill level
    """
    if score <= 6:
        return "Loathes"
    elif score <= 12:
        return "Hates"
    elif score < 18:
        return "Dislikes"
    elif score == 24:
        return "Neutral"
    elif score <= 30:
        return "Likes"
    elif score <= 36:
        return "Loves"
    return "Adores" 
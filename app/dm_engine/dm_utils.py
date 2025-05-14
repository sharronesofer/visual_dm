# This is a compact DM utility module that helps classify prompts and narrate combat outcomes using GPT. It's a support file used by dm_engine.py and related GPT routes.
#It integrates with gpt, narrative, and combat layers.

from app.npcs.npc_utils import get_relationship_tier
from app.core.utils.gpt.client import GPTClient
from firebase_admin import db
from datetime import datetime
import openai
import logging

MOTIF_THEME_NAMES = {
    1: "paranoia",
    2: "vengeance",
    3: "greed",
    4: "honor",
    5: "betrayal",
    6: "forgiveness",
    7: "redemption",
    8: "despair",
    9: "loyalty",
    10: "loss",
    11: "ambition",
    12: "fear",
    13: "doubt",
    14: "madness",
    15: "grief",
    16: "curiosity",
    17: "justice",
    18: "hope",
    19: "peace",
    20: "conflict",
    21: "obsession",
    22: "shame",
    23: "revenge",
    24: "sacrifice",
    25: "duty",
    26: "resilience",
    27: "nostalgia",
    28: "melancholy",
    29: "conspiracy",
    30: "transcendence",
    31: "divine will",
    32: "chaos",
    33: "restoration",
    34: "temptation",
    35: "survival",
    36: "decay",
    37: "awakening",
    38: "regret",
    39: "discipline",
    40: "enlightenment"
}

def classify_request(prompt: str, character_id: str = None) -> str:
    """Classify the type of request using GPT."""
    try:
        gpt = GPTClient()
        response = gpt.classify_request(prompt, character_id)
        return response
    except Exception as e:
        logging.error(f"Error classifying request: {str(e)}")
        return "unknown"

def narrate_combat_action(actor_name: str, action_data: dict, outcome: dict) -> str:
    """Generate narrative for a combat action using GPT."""
    try:
        gpt = GPTClient()
        response = gpt.narrate_combat(actor_name, action_data, outcome)
        return response
    except Exception as e:
        logging.error(f"Error narrating combat: {str(e)}")
        return f"{actor_name} performs an action."

def gather_motifs_for_context(npc_id: str = None, region: str = None, poi_id: str = None) -> list:
    """Gather relevant motifs for the current context."""
    motifs = []
    if npc_id:
        # Get NPC-specific motifs
        pass
    if region:
        # Get region-specific motifs
        pass
    if poi_id:
        # Get POI-specific motifs
        pass
    return motifs

def resolve_names(input_text: str, npc_list: list, alias_map: dict = None, relationship_map: dict = None) -> str:
    """Resolve NPC names and aliases in text."""
    if not alias_map:
        alias_map = {}
    if not relationship_map:
        relationship_map = {}
        
    for npc in npc_list:
        # Replace aliases with proper names
        if npc.id in alias_map:
            for alias in alias_map[npc.id]:
                input_text = input_text.replace(alias, npc.name)
                
        # Replace relationship references
        if npc.id in relationship_map:
            for ref in relationship_map[npc.id]:
                input_text = input_text.replace(ref, npc.name)
                
    return input_text

def gather_relationship_context(npc_id: str, pc_id: str) -> dict:
    """Gather context about the relationship between an NPC and PC."""
    try:
        relationship_tier = get_relationship_tier(npc_id, pc_id)
        return {
            "relationship_tier": relationship_tier,
            "npc_id": npc_id,
            "pc_id": pc_id
        }
    except Exception as e:
        logging.error(f"Error gathering relationship context: {str(e)}")
        return {}

def gather_faction_context(npc_id: str, pc_id: str) -> dict:
    """Gather context about faction relationships."""
    try:
        # Get faction relationships
        return {}
    except Exception as e:
        logging.error(f"Error gathering faction context: {str(e)}")
        return {}

from flask import Blueprint, request, jsonify
from firebase_admin import db
import random
from datetime import datetime

npc_management_bp = Blueprint('npc_management', __name__)
__all__ = ["npc_management_bp"]

# npc_management.py
def generate_motifs(n=3):
    """
    Generates a list of motif objects with random theme, lifespan, and weight.
    """
    return [{
        "theme": random.randint(1, 50),
        "lifespan": (life := random.randint(2, 4)),
        "entropy_tick": 0,
        "weight": 6 - life
    } for _ in range(n)]

def validate_npc(npc):
    """
    Ensures the NPC dictionary has all REQUIRED_FIELDS.
    Any missing field is set to None to maintain consistency.
    """
    REQUIRED_FIELDS = [
        "character_name", "characterType", "level", "class", "race", "gender", "alignment",
        "region_of_origin", "background", "HP", "AC", "STR", "DEX", "CON", "INT", "WIS", "CHA", 
        "XP", "feats", "skills", "proficiencies", "features", "spells", "equipment", "inventory", 
        "notable_possessions", "known_languages", "faction_affiliations", "reputation", 
        "personality_traits", "notable_relationships", "hidden_ambition", "hidden_compassion",
        "hidden_discipline", "hidden_impulsivity", "hidden_integrity", "hidden_pragmatism",
        "hidden_resilience", "private_goal_short_term", "private_goal_mid_term",
        "private_goal_long_term", "opinion_of_pc", "opinion_of_party", "narrative_motif_pool",
        "status_effects", "cooldowns", "gold"
    ]
    
    for field in REQUIRED_FIELDS:
        if field not in npc:
            npc[field] = None
    return npc

def rotate_motifs_if_needed(pool):
    rotated = False
    active = []
    now = datetime.utcnow().isoformat()

    for motif in pool.get("active_motifs", []):
        motif["entropy_tick"] += 1
        if motif["entropy_tick"] < motif["lifespan"]:
            active.append(motif)
        else:
            rotated = True
            pool.setdefault("motif_history", []).append(motif["theme"])

    while len(active) < 3:
        life = random.randint(2, 4)
        new_motif = {
            "theme": random.randint(1, 50),
            "lifespan": life,
            "entropy_tick": 0,
            "weight": 6 - life
        }
        active.append(new_motif)
        pool.setdefault("motif_history", []).append(new_motif["theme"])

    if rotated:
        pool["last_rotated"] = now
    pool["active_motifs"] = active
    return pool

def complete_character(core):
    pool = core.get("narrative_motif_pool", {
        "active_motifs": [{"theme": random.randint(1, 50), "lifespan": random.randint(2,4), "entropy_tick": 0} for _ in range(3)],
        "motif_history": [],
        "last_rotated": datetime.utcnow().isoformat()
    })
    core["narrative_motif_pool"] = rotate_motifs_if_needed(pool)

    core.setdefault("XP", 0)
    core.setdefault("alignment", "Neutral")
    core.setdefault("proficiencies", [])
    core.setdefault("features", [])
    core.setdefault("languages", ["Common"])
    core.setdefault("inventory", core.get("equipment", []))
    core.setdefault("faction_affiliations", [])
    core.setdefault("reputation", 0)
    core.setdefault("opinion_of_party", {})
    core.setdefault("hidden_ambition", "")
    core.setdefault("current_location", core.get("location", "Unknown"))
    core.setdefault("last_rest_timestamp", datetime.utcnow().isoformat())
    core.setdefault("rumor_index", [])
    core.setdefault("beliefs", {})
    core.setdefault("narrator_style", "Cormac McCarthy meets Lovecraft")
    return core

@npc_management_bp.route('/npc_motif_tick', methods=['POST'])
def npc_motif_tick():
    all_npcs = db.reference('/npcs').get() or {}
    updated = {}
    for npc_id, npc in all_npcs.items():
        pool = npc.get("narrative_motif_pool", {})
        updated_pool = rotate_motifs_if_needed(pool)
        db.reference(f'/npcs/{npc_id}/narrative_motif_pool').set(updated_pool)
        updated[npc_id] = updated_pool["active_motifs"]
    return jsonify({"message": "NPC motifs rotated", "updated": updated})
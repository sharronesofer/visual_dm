from firebase_admin import db
import random

def loyalty_tick(npc_id, player_id, context_tags=None, cha_score=10):
    """
    Called once per combat or major scene.
    Adjusts goodwill based on loyalty, and handles potential betrayal if goodwill is too low.
    """
    rel_ref = db.reference(f"/npcs/{npc_id}/relationships/{player_id}")
    rel = rel_ref.get() or {}

    loyalty = rel.get("loyalty", 0)
    goodwill = rel.get("goodwill", 5)
    tags = rel.get("tags", [])

    # Goodwill regeneration after event
    regen = 0
    if loyalty >= 10:
        regen = 3
    elif loyalty > 0:
        regen = 1
    elif loyalty <= -5:
        regen = 0

    goodwill += regen

    # Cap goodwill
    goodwill = min(goodwill, 10)

    rel["goodwill"] = goodwill
    rel_ref.set(rel)

    return {
        "npc_id": npc_id,
        "player_id": player_id,
        "loyalty": loyalty,
        "goodwill": goodwill,
        "tags": tags,
        "regen_applied": regen
    }

def apply_loyalty_event(npc_id, player_id, alignment_score):
    """
    Adjusts loyalty and goodwill based on a scored action (-5 to +5).
    alignment_score is the degree to which the action aligned with NPC hidden attributes.
    """
    rel_ref = db.reference(f"/npcs/{npc_id}/relationships/{player_id}")
    rel = rel_ref.get() or {}

    loyalty = rel.get("loyalty", 0)
    goodwill = rel.get("goodwill", 5)
    tags = rel.get("tags", [])

    # Apply loyalty tag modifiers
    gain_mod, loss_mod = 1.0, 1.0
    if "loyalist" in tags:
        gain_mod = 1.5
        loss_mod = 0.5
    elif "coward" in tags:
        gain_mod = 0.5
        loss_mod = 1.5
    elif "bestie" in tags:
        loyalty = 10
    elif "nemesis" in tags:
        loyalty = -10

    if alignment_score > 0:
        loyalty += int(alignment_score * gain_mod)
        goodwill += 1
    elif alignment_score < 0:
        loyalty += int(alignment_score * loss_mod)
        goodwill -= abs(alignment_score)

    loyalty = max(-10, min(10, loyalty))
    goodwill = max(0, min(10, goodwill))

    rel.update({"loyalty": loyalty, "goodwill": goodwill})
    rel_ref.set(rel)

    return rel

def betrayal_check(npc_id, player_id, cha_score):
    """
    Runs when goodwill hits zero and loyalty is low.
    CHA check against DC = 10 + abs(loyalty)
    """
    rel_ref = db.reference(f"/npcs/{npc_id}/relationships/{player_id}")
    rel = rel_ref.get() or {}

    loyalty = rel.get("loyalty", 0)
    goodwill = rel.get("goodwill", 0)

    if goodwill > 0 or loyalty > 0:
        return {"status": "stable", "message": "No betrayal risk."}

    dc = 10 + abs(loyalty)
    roll = random.randint(1, 20) + int((cha_score - 10) / 2)

    outcome = "stays"
    if roll < dc:
        outcome = "betrays"

    return {
        "npc_id": npc_id,
        "player_id": player_id,
        "dc": dc,
        "roll": roll,
        "cha_score": cha_score,
        "outcome": outcome
    }

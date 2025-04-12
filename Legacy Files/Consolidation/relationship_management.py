from firebase_admin import db
from datetime import datetime
import uuid
import random

def create_party(player_id, npc_ids, party_name="Adventuring Party"):
    party_id = str(uuid.uuid4())
    members = [player_id] + npc_ids

    db.reference(f"/parties/{party_id}").set({
        "name": party_name,
        "members": members,
        "created_at": datetime.utcnow().isoformat()
    })

    db.reference(f"/players/{player_id}/party_id").set(party_id)
    for npc_id in npc_ids:
        db.reference(f"/npcs/{npc_id}/party_id").set(party_id)

    return party_id

def add_to_party(party_id, npc_id):
    party_ref = db.reference(f"/parties/{party_id}")
    party_data = party_ref.get()
    if not party_data:
        return False

    party_data["members"].append(npc_id)
    party_ref.set(party_data)
    db.reference(f"/npcs/{npc_id}/party_id").set(party_id)
    return True

def loyalty_tick(npc_id, player_id, cha_score=10):
    rel_ref = db.reference(f"/npcs/{npc_id}/relationships/{player_id}")
    rel = rel_ref.get() or {}

    loyalty = rel.get("loyalty", 0)
    goodwill = rel.get("goodwill", 5)
    tags = rel.get("tags", [])

    regen = 3 if loyalty >= 10 else (1 if loyalty > 0 else 0)
    goodwill = min(goodwill + regen, 10)

    rel["goodwill"] = goodwill
    rel_ref.set(rel)

    return {"loyalty": loyalty, "goodwill": goodwill, "tags": tags, "regen_applied": regen}

def apply_loyalty_event(npc_id, player_id, alignment_score):
    rel_ref = db.reference(f"/npcs/{npc_id}/relationships/{player_id}")
    rel = rel_ref.get() or {}

    loyalty = rel.get("loyalty", 0)
    goodwill = rel.get("goodwill", 5)
    tags = rel.get("tags", [])

    gain_mod, loss_mod = 1.5 if "loyalist" in tags else 0.5 if "coward" in tags else 1.0

    loyalty += int(alignment_score * (gain_mod if alignment_score > 0 else loss_mod))
    goodwill += 1 if alignment_score > 0 else -abs(alignment_score)

    loyalty = max(-10, min(10, loyalty))
    goodwill = max(0, min(10, goodwill))

    rel.update({"loyalty": loyalty, "goodwill": goodwill})
    rel_ref.set(rel)

    return rel

def betrayal_check(npc_id, player_id, cha_score):
    rel_ref = db.reference(f"/npcs/{npc_id}/relationships/{player_id}")
    rel = rel_ref.get() or {}

    loyalty = rel.get("loyalty", 0)
    goodwill = rel.get("goodwill", 0)

    if goodwill > 0 or loyalty > 0:
        return {"status": "stable"}

    dc = 10 + abs(loyalty)
    roll = random.randint(1, 20) + int((cha_score - 10) / 2)

    return {"dc": dc, "roll": roll, "outcome": "betrays" if roll < dc else "stays"}

def daily_relationship_tick():
    npcs = db.reference("/npcs").get() or {}
    players = db.reference("/players").get() or {}

    for npc_id, npc in npcs.items():
        for player_id in players:
            rel_ref = db.reference(f"/npcs/{npc_id}/relationships/{player_id}")
            rel = rel_ref.get() or {"trust": 0, "respect": 0, "envy": 0, "attraction": 0}

            rel["trust"] = min(max(rel["trust"] + random.randint(-1, 1), 0), 10)
            rel["respect"] = min(max(rel["respect"] + random.randint(-1, 1), 0), 10)
            rel["envy"] = min(max(rel["envy"] + random.randint(-1, 1), 0), 10)
            rel["attraction"] = min(max(rel["attraction"] + random.randint(-1, 1), 0), 10)

            rel_ref.set(rel)
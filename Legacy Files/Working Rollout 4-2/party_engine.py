from firebase_admin import db
from datetime import datetime
import uuid

def create_party(player_id, npc_ids, party_name="Adventuring Party"):
    party_id = str(uuid.uuid4())
    members = [player_id] + npc_ids

    party_ref = db.reference(f"/parties/{party_id}")
    party_ref.set({
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

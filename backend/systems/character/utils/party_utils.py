#This module handles all party data logic—creating parties, managing membership, updating Firebase, tracking XP, and handling abandonment. It interacts deeply with firebase, npc, and party systems, and touches on world indirectly through character XP and level attributes.

from uuid import uuid4
from datetime import datetime
from typing import List, Dict, Union
# from firebase_admin import db  # TODO: Replace with proper database integration
from backend.systems.memory.memory_utils import log_permanent_memory
from backend.systems.core.repositories.party_repository import PartyRepository

def create_party(player_id, npc_ids):
    party_id = f"party_{player_id}"
    party_ref = db.reference(f'/parties/{party_id}')

    party_data = {
        "members": [player_id] + npc_ids,
        "created_at": datetime.utcnow().isoformat()
    }
    party_ref.set(party_data)

    db.reference(f'/characters/{player_id}/party_id').set(party_id)
    for npc_id in npc_ids:
        db.reference(f'/characters/{npc_id}/party_id').set(party_id)

        # 🧠 Memory: NPC joined party
        log_permanent_memory(npc_id, f"Joined party with player {player_id} on {datetime.utcnow().isoformat()}")

    return party_id

def add_to_party(party_id, npc_id):
    party_ref = db.reference(f'/parties/{party_id}')
    party_data = party_ref.get()
    if not party_data:
        return False

    if npc_id not in party_data.get("members", []):
        party_data["members"].append(npc_id)
        party_ref.set(party_data)

        db.reference(f'/characters/{npc_id}/party_id').set(party_id)

        # 🧠 Log party join event
        log_permanent_memory(npc_id, f"Added to party {party_id} on {datetime.utcnow().isoformat()}")

        return True
    return False

def remove_from_party(party_id, member_id):
    party_ref = db.reference(f'/parties/{party_id}')
    party_data = party_ref.get()
    if not party_data:
        return False

    if member_id in party_data.get("members", []):
        party_data["members"].remove(member_id)
        db.reference(f'/characters/{member_id}/party_id').delete()
        party_ref.set(party_data)

        # 🧠 Log this to permanent memory
        log_permanent_memory(member_id, f"Removed from party {party_id} on {datetime.utcnow().isoformat()}")

        return True
    return False

def get_total_party_level(party_id, mode="sum"):
    party = db.reference(f"/parties/{party_id}").get() or {"members": []}
    total_level = sum(db.reference(f"/players/{m}").get().get("level", 1) for m in party["members"])

    return total_level if mode == "sum" else total_level // len(party["members"])

def award_xp_to_party(party_id, amount):
    party = db.reference(f"/parties/{party_id}").get() or {"members": []}
    awarded = {}

    for member_id in party["members"]:
        char_ref = db.reference(f"/players/{member_id}")
        char = char_ref.get() or {}
        char["XP"] = char.get("XP", 0) + amount
        char_ref.set(char)
        awarded[member_id] = char["XP"]

    return awarded

def abandon_party(npc_id):
    parties_ref = db.reference('/parties')
    parties = parties_ref.get() or {}

    for party_id, party_data in parties.items():
        if npc_id in party_data.get("members", []):
            party_data["members"].remove(npc_id)
            parties_ref.child(party_id).set(party_data)

            db.reference(f'/characters/{npc_id}/party_id').delete()
            db.reference(f'/characters/{npc_id}/attributeus_effects').set(["abandoned"])

            # 🧠 Permanent memory log
            log_permanent_memory(npc_id, f"Abandoned party {party_id} due to loyalty loss on {datetime.utcnow().isoformat()}")

            return True
    return False

# Example usage (replace direct session/Party usage):
# repo = PartyRepository(session)
# repo.create_party(party_data)
# repo.update_party(party_id, update_data)
# repo.delete_party(party_id)
"""
party_engine.py
Handles creating parties, adding NPCs or characters to parties, and basic party logic.
"""

import uuid
from datetime import datetime
from firebase_admin import db
from flask import Blueprint, request, jsonify
from typing import List, Dict, Union

party_bp = Blueprint("party_bp", __name__)
__all__ = ["party_bp"]

# ----------------------
# Create Party Endpoint
# ----------------------

@party_bp.route("/party/create", methods=["POST"])
def create_party_route():
    data = request.json
    character_id = data.get("character_id")
    npc_ids = data.get("npc_ids", [])
    party_name = data.get("party_name", "Adventuring Party")

    if not character_id:
        return jsonify({"error": "Missing character_id"}), 400

    party_id = create_party(character_id, npc_ids, party_name)
    return jsonify({"message": "Party created", "party_id": party_id}), 200

def create_party(character_id: str, npc_ids: List[str], party_name: str = "Adventuring Party") -> str:
    unique_npcs = list(set(npc_ids))
    party_id = str(uuid.uuid4())
    members = [character_id] + unique_npcs

    party_data = {
        "name": party_name,
        "members": members,
        "created_at": datetime.utcnow().isoformat()
    }
    db.reference(f"/parties/{party_id}").set(party_data)
    db.reference(f"/players/{character_id}/party_id").set(party_id)

    for npc_id in unique_npcs:
        db.reference(f"/npcs/{npc_id}/party_id").set(party_id)

    return party_id

# ----------------------
# Add NPC to Party
# ----------------------

@party_bp.route("/party/<party_id>/add_npc", methods=["POST"])
def add_npc_to_party_route(party_id):
    data = request.json
    npc_id = data.get("npc_id")
    if not npc_id:
        return jsonify({"error": "Missing npc_id"}), 400

    result = add_to_party(party_id, npc_id)
    status_code = 200 if result["success"] else 400
    return jsonify(result), status_code

def add_to_party(party_id: str, npc_id: str) -> Dict[str, Union[bool, str]]:
    party_ref = db.reference(f"/parties/{party_id}")
    party_data = party_ref.get()
    if not party_data:
        return {"success": False, "message": "Party does not exist."}

    members = party_data.get("members", [])
    if npc_id in members:
        return {"success": False, "message": f"NPC {npc_id} already in party."}

    members.append(npc_id)
    party_ref.update({"members": members})
    db.reference(f"/npcs/{npc_id}/party_id").set(party_id)

    return {"success": True, "message": f"NPC {npc_id} added to party."}

# ----------------------
# Remove Member from Party
# ----------------------

@party_bp.route("/party/<party_id>/remove_member", methods=["POST"])
def remove_member_route(party_id):
    data = request.json
    member_id = data.get("member_id")
    member_type = data.get("member_type", "npc")  # "npc" or "player"

    if not member_id:
        return jsonify({"error": "Missing member_id"}), 400

    result = remove_from_party(party_id, member_id, member_type)
    status_code = 200 if result["success"] else 400
    return jsonify(result), status_code

def remove_from_party(party_id: str, member_id: str, member_type: str) -> Dict[str, Union[bool, str]]:
    party_ref = db.reference(f"/parties/{party_id}")
    party_data = party_ref.get()
    if not party_data:
        return {"success": False, "message": "Party does not exist."}

    members = party_data.get("members", [])
    if member_id not in members:
        return {"success": False, "message": f"{member_type.capitalize()} {member_id} not in party."}

    members.remove(member_id)
    party_ref.update({"members": members})

    path = f"/npcs/{member_id}" if member_type == "npc" else f"/players/{member_id}"
    db.reference(f"{path}/party_id").delete()

    return {"success": True, "message": f"{member_type.capitalize()} {member_id} removed from party."}

# ----------------------
# Get Party Details
# ----------------------

@party_bp.route("/party/<party_id>", methods=["GET"])
def get_party_details(party_id):
    party_data = db.reference(f"/parties/{party_id}").get()
    if not party_data:
        return jsonify({"error": "Party does not exist."}), 404
    return jsonify(party_data), 200

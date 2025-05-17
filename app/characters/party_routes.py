# This route handles party creation and management including adding/removing NPCs, viewing party data, and simulating NPC abandonment based on loyalty logic.

from flask import Blueprint, request, jsonify
from app.core.database import db
from app.core.models.character import Character
from app.core.models.party import Party
from app.npcs.npc_loyalty_utils import should_abandon
from datetime import datetime
from typing import Dict, List, Optional
from fastapi import APIRouter, HTTPException
from visual_client.game.character import should_abandon as visual_client_should_abandon
from app.core.repositories.party_repository import PartyRepository

party_bp = Blueprint("party", __name__)

# === PARTY CREATION ===
@party_bp.route("/party/create", methods=["POST"])
def create_party_route():
    data = request.get_json(force=True)
    character_id = data.get("character_id")
    npc_ids = data.get("npc_ids", [])
    party_name = data.get("party_name", "Adventuring Party")

    if not character_id:
        return jsonify({"error": "Missing character_id."}), 400

    try:
        # Create new party
        party = Party(
            name=party_name,
            leader_id=character_id,
            created_at=datetime.utcnow()
        )
        db.session.add(party)
        db.session.commit()

        # Add members to party
        for npc_id in npc_ids:
            npc = Character.query.get(npc_id)
            if npc:
                party.members.append(npc)

        # Update leader's party affiliation
        leader = Character.query.get(character_id)
        if leader:
            leader.party_id = party.id

        db.session.commit()
        return jsonify({"message": "Party created.", "party_id": party.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# === ADD NPC TO PARTY BY PARTY ID ===
@party_bp.route("/party/<party_id>/add_npc", methods=["POST"])
def add_npc_to_party_route(party_id):
    data = request.get_json(force=True)
    npc_id = data.get("npc_id")

    if not npc_id:
        return jsonify({"error": "Missing npc_id."}), 400

    try:
        party = Party.query.get(party_id)
        npc = Character.query.get(npc_id)

        if not party or not npc:
            return jsonify({"error": "Party or NPC not found."}), 404

        party.members.append(npc)
        npc.party_id = party.id
        db.session.commit()

        return jsonify({"success": True, "message": f"Added {npc.name} to party {party.name}"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# === REMOVE MEMBER FROM PARTY ===
@party_bp.route("/party/<party_id>/remove_member", methods=["POST"])
def remove_member_route(party_id):
    data = request.get_json(force=True)
    member_id = data.get("member_id")
    member_type = data.get("member_type", "npc")  # Accepts 'npc' or 'player'

    if not member_id:
        return jsonify({"error": "Missing member_id."}), 400
    if member_type not in {"npc", "player"}:
        return jsonify({"error": "member_type must be 'npc' or 'player'."}), 400

    try:
        party = Party.query.get(party_id)
        member = Character.query.get(member_id)

        if not party or not member:
            return jsonify({"error": "Party or member not found."}), 404

        if member in party.members:
            party.members.remove(member)
            member.party_id = None
            db.session.commit()

            return jsonify({"success": True, "message": f"Removed {member.name} from party {party.name}"}), 200
        else:
            return jsonify({"error": "Member not in party."}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# === VIEW PARTY DETAILS ===
@party_bp.route("/party/<party_id>", methods=["GET"])
def get_party_details(party_id):
    try:
        party = Party.query.get(party_id)
        if not party:
            return jsonify({"error": "Party does not exist."}), 404

        return jsonify(party.to_dict()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# === ABANDONMENT CHECK ===
@party_bp.route("/npc/<npc_id>/abandon_party", methods=["POST"])
def abandon_party(npc_id):
    try:
        npc = Character.query.get(npc_id)
        if not npc:
            return jsonify({"error": "NPC not found"}), 404

        party = Party.query.get(npc.party_id)
        if not party:
            return jsonify({"message": "NPC was not in a party."})

        # Check if NPC should abandon party
        if should_abandon(npc, party):
            party.members.remove(npc)
            npc.party_id = None
            db.session.commit()

            return jsonify({"message": f"{npc.name} left party {party.name}"})
        else:
            return jsonify({"message": f"{npc.name} decided to stay in party {party.name}"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

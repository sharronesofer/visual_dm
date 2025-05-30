#This route module handles NPC creation, retrieval, updates, and deletion, acting as the API surface for persistent NPC management. It integrates with the NPCBuilder logic and Firebase persistence.
#It supports the npc, firebase, motif, memory, and faction systems.

from flask import Blueprint, request, jsonify
from firebase_admin import db
from app.npc.npc_builder_class import NPCBuilder
from app.npc.npc_loyalty_class import LoyaltyManager
from app.rules.character_gen_rules_utils import (
    load_feat_data, load_starter_kits, load_race_data, load_skill_list
)
import openai

npc_bp = Blueprint("npc", __name__)

@npc_bp.route("/npc/create", methods=["POST"])
def create_npc():
    try:
        data = request.get_json(force=True)
        
        # Load required data
        race_data = load_race_data()
        skills = load_skill_list()
        
        # Create NPC using builder
        builder = NPCBuilder(race_data, skills)
        
        # Set basic info
        builder.set_id(data.get("npc_id"))
        builder.set_name(data.get("name", "Unnamed NPC"))
        builder.set_race(data.get("race", "Human"))
        
        # Set attributes
        for stat, value in data.get("attributes", {}).items():
            builder.assign_stat(stat, value)
        
        # Add skills
        for skill in data.get("skills", []):
            builder.add_skill(skill)
        
        # Add tags
        for tag in data.get("tags", []):
            builder.add_tag(tag)
        
        # Set location
        loc = data.get("location", "0_0")
        region = data.get("region_id", "unknown_region")
        builder.set_location(region, loc)
        
        # Generate motifs
        builder.generate_motifs()
        
        # Initialize loyalty
        pc_id = data.get("pc_id")
        if pc_id:
            builder.init_loyalty_from_pc(pc_id)
        
        # Finalize NPC
        npc = builder.finalize()
        
        # Save to Firebase
        npc_id = npc["npc_id"]
        db.reference(f"/npcs/{npc_id}").set(npc)
        
        return jsonify(npc), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@npc_bp.route("/npc/<npc_id>", methods=["GET"])
def get_npc(npc_id):
    try:
        npc = db.reference(f"/npcs/{npc_id}").get()
        if not npc:
            return jsonify({"error": f"NPC '{npc_id}' not found."}), 404
        return jsonify(npc), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@npc_bp.route("/npc/<npc_id>", methods=["POST"])
def update_npc(npc_id):
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400
    
        npc_ref = db.reference(f"/npcs/{npc_id}")
        current = npc_ref.get() or {}
    
        allowed_keys = {
            "name", "alignment", "inventory", "features", "location",
            "motif_entropy", "core_motifs", "party_affiliation",
            "faction_affiliations", "reputation", "hidden_traits",
            "relationships", "opinion_of_party", "backstory"
        }
    
        # Filter only valid keys
        sanitized = {k: v for k, v in data.items() if k in allowed_keys}
        current.update(sanitized)
        npc_ref.set(current)
    
        return jsonify({"npc_id": npc_id, "updated": sanitized})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@npc_bp.route("/npc/<npc_id>", methods=["DELETE"])
def delete_npc(npc_id):
    try:
        # Remove NPC base
        db.reference(f"/npcs/{npc_id}").delete()
    
        # Optional: remove from rumor system
        db.reference(f"/npc_rumors/{npc_id}").delete()
    
        # Remove memory
        db.reference(f"/npc_memory/{npc_id}").delete()
    
        # Remove knowledge
        db.reference(f"/npc_knowledge/{npc_id}").delete()
    
        # Remove from any opinion matrices
        db.reference(f"/npc_opinion_matrix/{npc_id}").delete()
    
        # Remove from region/POI if tracked
        region_ref = db.reference("/poi_state")
        regions = region_ref.get() or {}
        for region_name, pois in regions.items():
            for poi_id, poi_data in pois.items():
                if "npcs_present" in poi_data and npc_id in poi_data["npcs_present"]:
                    poi_data["npcs_present"].remove(npc_id)
                    db.reference(f"/poi_state/{region_name}/{poi_id}").update(poi_data)
    
        return jsonify({"message": f"NPC {npc_id} fully removed from game state."})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@npc_bp.route("/npc/<npc_id>/info", methods=["GET"])
def get_npc_info(npc_id):
    try:
        npc = db.reference(f"/npcs/{npc_id}").get()
        if not npc:
            return jsonify({"error": f"NPC '{npc_id}' not found."}), 404
        # Hide loyalty, show goodwill
        display_npc = {
            "name": npc.get("name", "Unknown"),
            "goodwill": npc.get("loyalty", {}).get("goodwill", 0),
            "faction": npc.get("faction_affiliations", ["None"])[0],
            "motifs": npc.get("narrative_motif_pool", {})
        }
        return jsonify(display_npc)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@npc_bp.route('/npc/<npc_id>/refresh_goals', methods=['POST'])
def refresh_npc_goals(npc_id):
    """
    Refresh an NPC's personal goals via gpt-4.1.1-nano.
    """
    try:
        npc_ref = db.reference(f"/npcs/{npc_id}")
        npc = npc_ref.get()

        if not npc:
            return jsonify({"error": f"NPC {npc_id} not found."}), 404

        name = npc.get("name", "Unnamed")
        race = npc.get("race", "Human")
        char_class = npc.get("class", "Commoner")
        background = npc.get("backstory", "A simple wanderer.")

        goals_response = openai.ChatCompletion.create(
            model="gpt-4.1.1-nano",
            messages=[
                {"role": "system", "content": "Generate 3 short personal goals for a fantasy RPG NPC."},
                {"role": "user", "content": f"Name: {name}, Race: {race}, Class: {char_class}, Background: {background}."}
            ],
            temperature=0.7,
            max_tokens=150
        )

        goals = [g.strip("-• ") for g in goals_response.choices[0].message.content.strip().split("\n") if g.strip()]
        goals = goals[:3]

        npc["personal_goals"] = goals
        npc_ref.set(npc)

        return jsonify({"message": f"NPC {npc_id} goals refreshed.", "new_goals": goals})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@npc_bp.route('/npc/<npc_id>/loyalty/<character_id>', methods=['POST'])
def update_loyalty(npc_id, character_id):
    """
    Update NPC's loyalty towards a character.
    """
    try:
        data = request.get_json(force=True)
        alignment_score = data.get("alignment_score", 0)
        
        # Use the loyalty manager
        loyalty_manager = LoyaltyManager.load_from_firebase(npc_id, character_id)
        loyalty = loyalty_manager.apply_alignment_event(alignment_score, character_id)
        loyalty_manager.save_to_firebase(character_id)
        
        # Check for abandonment
        if loyalty_manager.should_abandon():
            abandon_party(npc_id)
            return jsonify({
                "message": f"NPC {npc_id} has left the party due to low loyalty.",
                "loyalty": loyalty
            })
        
        return jsonify({
            "message": f"Loyalty updated for NPC {npc_id}.",
            "loyalty": loyalty
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def abandon_party(npc_id):
    """Helper function to handle NPC abandoning the party."""
    npc_ref = db.reference(f"/npcs/{npc_id}")
    npc = npc_ref.get()

    if not npc or "party_id" not in npc:
        return {"error": "NPC not in a party."}

    party_id = npc["party_id"]
    party_ref = db.reference(f"/parties/{party_id}/members")
    members = party_ref.get() or []

    updated_members = [m for m in members if m != npc_id]
    party_ref.set(updated_members)

    # Clear NPC's party association
    npc_ref.update({"party_id": None})

    return {"message": f"{npc_id} has left party {party_id}.", "remaining_members": updated_members}
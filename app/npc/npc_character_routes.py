from flask import Blueprint, request, jsonify
from firebase_admin import db

from app.npc.npc_rumor_routes import rumor_bp

from app.npc.npc_loyalty_utils import (
    build_npc_from_input,
    save_npc_to_firebase,
    load_npc_from_firebase
)

npc_bp = Blueprint("npc", __name__)

@npc_bp.route("/npc/create", methods=["POST"])
def create_npc():
    try:
        data = request.get_json(force=True)
        npc = build_npc_from_input(data)

        npc_id = npc.get("npc_id") or npc.get("name")
        if not npc_id:
            return jsonify({"error": "Missing npc_id or name."}), 400

        save_npc_to_firebase(npc_id, npc)
        return jsonify(npc), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@npc_bp.route("/npc/<npc_id>", methods=["GET"])
def get_npc(npc_id):
    try:
        npc = load_npc_from_firebase(npc_id)
        if not npc:
            return jsonify({"error": f"NPC '{npc_id}' not found."}), 404
        return jsonify(npc), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@npc_bp.route("/npc/<npc_id>", methods=["PATCH"])
def update_npc(npc_id):
    try:
        data = request.get_json(force=True)
        ref = db.reference(f"/npcs/{npc_id}")
        existing = ref.get()
        if not existing:
            return jsonify({"error": f"NPC '{npc_id}' not found."}), 404

        existing.update(data)
        ref.set(existing)
        return jsonify(existing), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@npc_bp.route("/npc/<npc_id>", methods=["DELETE"])
def delete_npc(npc_id):
    try:
        ref = db.reference(f"/npcs/{npc_id}")
        if ref.get() is None:
            return jsonify({"error": f"NPC '{npc_id}' not found."}), 404
        ref.delete()
        return jsonify({"message": f"NPC '{npc_id}' deleted."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

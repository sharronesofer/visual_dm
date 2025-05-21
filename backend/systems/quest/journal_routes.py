from flask import Blueprint, request, jsonify
from firebase_admin import db

journal_bp = Blueprint("journal", __name__)

@journal_bp.route("/quests/<character_id>", methods=["GET"])
def get_character_quests(character_id):
    try:
        quests = db.reference(f"/quests/{character_id}").get() or []
        return jsonify(quests)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@journal_bp.route("/rumors/<region_id>", methods=["GET"])
def get_rumors(region_id):
    try:
        rumors = db.reference(f"/rumors/{region_id}").get() or []
        return jsonify(rumors)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@journal_bp.route("/notes/<character_id>", methods=["GET", "POST"])
def character_notes(character_id):
    try:
        ref = db.reference(f"/notes/{character_id}")
        if request.method == "GET":
            notes = ref.get() or []
            return jsonify(notes)
        if request.method == "POST":
            new_note = request.json.get("note")
            if not new_note:
                return jsonify({"error": "No note provided"}), 400
            notes = ref.get() or []
            notes.append(new_note)
            ref.set(notes)
            return jsonify({"message": "Note saved."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

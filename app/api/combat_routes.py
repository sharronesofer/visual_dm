from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.core.models.combat import Combat, CombatParticipant
from app.core.database import db
from app.api.schemas.encounter import EncounterSchema
from app.api.schemas.combat_log import CombatLogSchema

combat_bp = Blueprint('combat', __name__)

# --- Create Encounter ---
@combat_bp.route('/encounters', methods=['POST'])
@jwt_required()
def create_encounter():
    data = request.get_json(force=True)
    schema = EncounterSchema()
    try:
        encounter_data = schema.load(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    encounter = Combat(**encounter_data)
    db.session.add(encounter)
    db.session.commit()
    return jsonify(schema.dump(encounter)), 201

# --- Process Turn ---
@combat_bp.route('/encounters/<int:encounter_id>/turns', methods=['POST'])
@jwt_required()
def process_turn(encounter_id):
    encounter = Combat.query.get(encounter_id)
    if not encounter:
        return jsonify({'error': 'Encounter not found'}), 404
    data = request.get_json(force=True)
    # For simplicity, just append the action to the log
    action = data.get('action')
    if not action:
        return jsonify({'error': 'Missing action'}), 400
    log_entry = {'turn': encounter.current_turn, 'action': action}
    encounter.log.append(log_entry)
    encounter.current_turn += 1
    db.session.commit()
    return jsonify({'message': 'Turn processed', 'log_entry': log_entry}), 200

# --- Get Combat Log ---
@combat_bp.route('/encounters/<int:encounter_id>/log', methods=['GET'])
@jwt_required()
def get_combat_log(encounter_id):
    encounter = Combat.query.get(encounter_id)
    if not encounter:
        return jsonify({'error': 'Encounter not found'}), 404
    return jsonify({'log': encounter.log}), 200 
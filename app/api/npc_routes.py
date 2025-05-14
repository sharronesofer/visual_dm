from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.core.models.npc import NPC
from app.core.database import db
from app.api.schemas.npc import NPCSchema
from app.api.schemas.relationship import RelationshipSchema
from app.api.schemas.schedule import ScheduleSchema

npc_bp = Blueprint('npc', __name__)

# --- NPC CRUD ---
@npc_bp.route('/npcs', methods=['GET'])
@jwt_required()
def list_npcs():
    npcs = NPC.query.all()
    return jsonify(NPCSchema(many=True).dump(npcs)), 200

@npc_bp.route('/npcs', methods=['POST'])
@jwt_required()
def create_npc():
    data = request.get_json(force=True)
    schema = NPCSchema()
    try:
        npc_data = schema.load(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    npc = NPC(**npc_data)
    db.session.add(npc)
    db.session.commit()
    return jsonify(schema.dump(npc)), 201

@npc_bp.route('/npcs/<int:npc_id>', methods=['GET'])
@jwt_required()
def get_npc(npc_id):
    npc = NPC.query.get(npc_id)
    if not npc:
        return jsonify({'error': 'NPC not found'}), 404
    return jsonify(NPCSchema().dump(npc)), 200

@npc_bp.route('/npcs/<int:npc_id>', methods=['PUT'])
@jwt_required()
def update_npc(npc_id):
    npc = NPC.query.get(npc_id)
    if not npc:
        return jsonify({'error': 'NPC not found'}), 404
    data = request.get_json(force=True)
    schema = NPCSchema()
    try:
        npc_data = schema.load(data, partial=True)
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    for key, value in npc_data.items():
        setattr(npc, key, value)
    db.session.commit()
    return jsonify(schema.dump(npc)), 200

@npc_bp.route('/npcs/<int:npc_id>', methods=['DELETE'])
@jwt_required()
def delete_npc(npc_id):
    npc = NPC.query.get(npc_id)
    if not npc:
        return jsonify({'error': 'NPC not found'}), 404
    db.session.delete(npc)
    db.session.commit()
    return jsonify({'message': 'NPC deleted'}), 200

# --- NPC Relationships ---
@npc_bp.route('/npcs/<int:npc_id>/relationships', methods=['GET'])
@jwt_required()
def get_npc_relationships(npc_id):
    npc = NPC.query.get(npc_id)
    if not npc:
        return jsonify({'error': 'NPC not found'}), 404
    # Relationships are stored as a dict: {target_npc_id: {...}}
    rels = []
    for target_id, rel in npc.relationships.items():
        rels.append({'source_npc_id': npc_id, 'target_npc_id': int(target_id), **rel})
    return jsonify(RelationshipSchema(many=True).dump(rels)), 200

@npc_bp.route('/npcs/<int:npc_id>/relationships', methods=['POST'])
@jwt_required()
def create_npc_relationship(npc_id):
    npc = NPC.query.get(npc_id)
    if not npc:
        return jsonify({'error': 'NPC not found'}), 404
    data = request.get_json(force=True)
    schema = RelationshipSchema()
    try:
        rel_data = schema.load(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    target_id = str(rel_data['target_npc_id'])
    npc.relationships[target_id] = {k: v for k, v in rel_data.items() if k not in ['source_npc_id', 'target_npc_id']}
    db.session.commit()
    return jsonify(schema.dump({'source_npc_id': npc_id, **rel_data})), 201

@npc_bp.route('/npcs/<int:npc_id>/relationships/<int:target_id>', methods=['PUT'])
@jwt_required()
def update_npc_relationship(npc_id, target_id):
    npc = NPC.query.get(npc_id)
    if not npc:
        return jsonify({'error': 'NPC not found'}), 404
    if str(target_id) not in npc.relationships:
        return jsonify({'error': 'Relationship not found'}), 404
    data = request.get_json(force=True)
    for k, v in data.items():
        npc.relationships[str(target_id)][k] = v
    db.session.commit()
    return jsonify({'message': 'Relationship updated'}), 200

# --- NPC Schedule ---
@npc_bp.route('/npcs/<int:npc_id>/schedule', methods=['GET'])
@jwt_required()
def get_npc_schedule(npc_id):
    npc = NPC.query.get(npc_id)
    if not npc:
        return jsonify({'error': 'NPC not found'}), 404
    return jsonify({'schedule': npc.schedule}), 200

@npc_bp.route('/npcs/<int:npc_id>/schedule', methods=['PUT'])
@jwt_required()
def update_npc_schedule(npc_id):
    npc = NPC.query.get(npc_id)
    if not npc:
        return jsonify({'error': 'NPC not found'}), 404
    data = request.get_json(force=True)
    schedule = data.get('schedule')
    if not isinstance(schedule, list):
        return jsonify({'error': 'Schedule must be a list'}), 400
    npc.schedule = schedule
    db.session.commit()
    return jsonify({'schedule': npc.schedule}), 200 
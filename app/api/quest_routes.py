from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.models.quest_log import QuestLog  # Assuming this is the main quest model
from app.core.database import db
from app.api.schemas.quest import QuestSchema

quest_bp = Blueprint('quest', __name__)

# --- Quest CRUD ---
@quest_bp.route('/quests', methods=['GET'])
@jwt_required()
def list_quests():
    quests = QuestLog.query.all()
    return jsonify(QuestSchema(many=True).dump(quests)), 200

@quest_bp.route('/quests', methods=['POST'])
@jwt_required()
def create_quest():
    data = request.get_json(force=True)
    schema = QuestSchema()
    try:
        quest_data = schema.load(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    quest = QuestLog(**quest_data)
    db.session.add(quest)
    db.session.commit()
    return jsonify(schema.dump(quest)), 201

@quest_bp.route('/quests/<int:quest_id>', methods=['GET'])
@jwt_required()
def get_quest(quest_id):
    quest = QuestLog.query.get(quest_id)
    if not quest:
        return jsonify({'error': 'Quest not found'}), 404
    return jsonify(QuestSchema().dump(quest)), 200

@quest_bp.route('/quests/<int:quest_id>', methods=['PUT'])
@jwt_required()
def update_quest(quest_id):
    quest = QuestLog.query.get(quest_id)
    if not quest:
        return jsonify({'error': 'Quest not found'}), 404
    data = request.get_json(force=True)
    schema = QuestSchema()
    try:
        quest_data = schema.load(data, partial=True)
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    for key, value in quest_data.items():
        setattr(quest, key, value)
    db.session.commit()
    return jsonify(schema.dump(quest)), 200

@quest_bp.route('/quests/<int:quest_id>', methods=['DELETE'])
@jwt_required()
def delete_quest(quest_id):
    quest = QuestLog.query.get(quest_id)
    if not quest:
        return jsonify({'error': 'Quest not found'}), 404
    db.session.delete(quest)
    db.session.commit()
    return jsonify({'message': 'Quest deleted'}), 200

# --- Quest Progress ---
@quest_bp.route('/quests/<int:quest_id>/progress', methods=['GET'])
@jwt_required()
def get_quest_progress(quest_id):
    quest = QuestLog.query.get(quest_id)
    if not quest:
        return jsonify({'error': 'Quest not found'}), 404
    return jsonify({'progress': quest.progress}), 200

@quest_bp.route('/quests/<int:quest_id>/progress', methods=['PUT'])
@jwt_required()
def update_quest_progress(quest_id):
    quest = QuestLog.query.get(quest_id)
    if not quest:
        return jsonify({'error': 'Quest not found'}), 404
    data = request.get_json(force=True)
    progress = data.get('progress')
    if not isinstance(progress, dict):
        return jsonify({'error': 'Progress must be a dict'}), 400
    quest.progress = progress
    db.session.commit()
    return jsonify({'progress': quest.progress}), 200

# --- Quest Completion ---
@quest_bp.route('/quests/<int:quest_id>/complete', methods=['POST'])
@jwt_required()
def complete_quest(quest_id):
    quest = QuestLog.query.get(quest_id)
    if not quest:
        return jsonify({'error': 'Quest not found'}), 404
    quest.status = 'completed'
    db.session.commit()
    return jsonify({'message': 'Quest marked as complete'}), 200

# --- Quest Rewards ---
@quest_bp.route('/quests/<int:quest_id>/rewards', methods=['GET'])
@jwt_required()
def get_quest_rewards(quest_id):
    quest = QuestLog.query.get(quest_id)
    if not quest:
        return jsonify({'error': 'Quest not found'}), 404
    return jsonify({'rewards': quest.rewards}), 200 
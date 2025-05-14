from flask import Blueprint, jsonify, request
from app.services.quest_service import QuestService

quest_bp = Blueprint('quest', __name__)
quest_service = QuestService()

@quest_bp.route('/quests/<int:character_id>', methods=['GET'])
def get_quests(character_id):
    # TODO: Filter by character, currently returns all quests
    quests = [q.to_dict() for q in quest_service.get_all_quests()]
    return jsonify(quests)

@quest_bp.route('/quests/<int:character_id>/<int:quest_id>/branches', methods=['GET'])
def get_quest_branches(character_id, quest_id):
    branches = quest_service.get_quest_branches(quest_id)
    if branches is None:
        return jsonify({'error': 'Quest or branches not found'}), 404
    return jsonify(branches)

@quest_bp.route('/quests/<int:character_id>/<int:quest_id>/choose_branch', methods=['POST'])
def choose_quest_branch(character_id, quest_id):
    branch_data = request.get_json() or {}
    branch_data['character_id'] = character_id  # Ensure character_id is passed
    try:
        quest_service.add_branching_path(quest_id, branch_data)
        updated_quest = quest_service.get_quest(quest_id)
        return jsonify({
            'success': True,
            'message': 'Branch chosen and quest progressed.',
            'quest': updated_quest.to_dict() if updated_quest else None
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500 
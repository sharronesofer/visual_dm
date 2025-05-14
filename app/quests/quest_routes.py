"""
Quest-related API routes.
Handles quest creation, management, and journal entries.
"""

from flask import Blueprint, request, jsonify
from app.core.utils.error_utils import ValidationError, NotFoundError, DatabaseError
from app.quests.quest_validators import QuestValidator
from app.quests.quest_utils import QuestUtils

quest_bp = Blueprint('quests', __name__)

@quest_bp.route('/quests', methods=['POST'])
def create_quest():
    """Create a new quest."""
    try:
        data = request.get_json()
        QuestValidator.validate_quest_data(data)
        
        quest_id = QuestUtils.create_quest(data)
        
        return jsonify({
            'message': 'Quest created successfully',
            'quest_id': quest_id
        }), 201
        
    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    except DatabaseError as e:
        return jsonify({'error': str(e)}), 500

@quest_bp.route('/quests/<quest_id>', methods=['GET'])
def get_quest(quest_id):
    """Get quest details."""
    try:
        QuestValidator.validate_quest_id(quest_id)
        
        quest_data = QuestUtils.get_quest(quest_id)
        if not quest_data:
            raise NotFoundError(f"Quest {quest_id} not found")
            
        return jsonify(quest_data), 200
        
    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    except NotFoundError as e:
        return jsonify({'error': str(e)}), 404
    except DatabaseError as e:
        return jsonify({'error': str(e)}), 500

@quest_bp.route('/quests/<quest_id>/progress', methods=['PUT'])
def update_quest(quest_id):
    """Update quest progress."""
    try:
        QuestValidator.validate_quest_id(quest_id)
        data = request.get_json()
        
        if 'step_id' not in data:
            raise ValidationError("Step ID is required")
            
        quest_data = QuestUtils.get_quest(quest_id)
        if not quest_data:
            raise NotFoundError(f"Quest {quest_id} not found")
            
        if not QuestUtils.is_valid_step(quest_data, data['step_id']):
            raise ValidationError(f"Invalid step ID: {data['step_id']}")
            
        if not QuestUtils.update_quest_progress(quest_id, data['step_id']):
            raise DatabaseError("Failed to update quest progress")
            
        return jsonify({'message': 'Quest progress updated successfully'}), 200
        
    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    except NotFoundError as e:
        return jsonify({'error': str(e)}), 404
    except DatabaseError as e:
        return jsonify({'error': str(e)}), 500

@quest_bp.route('/quests/<quest_id>/journal', methods=['POST'])
def create_journal_entry(quest_id):
    """Create a journal entry for a quest."""
    try:
        QuestValidator.validate_quest_id(quest_id)
        data = request.get_json()
        
        # Add quest_id to data
        data['quest_id'] = quest_id
        QuestValidator.validate_journal_entry(data)
        
        # Verify quest exists
        if not QuestUtils.get_quest(quest_id):
            raise NotFoundError(f"Quest {quest_id} not found")
            
        # Save journal entry
        entry_id = QuestUtils.create_journal_entry(data)
        
        return jsonify({
            'message': 'Journal entry created successfully',
            'entry_id': entry_id
        }), 201
        
    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    except NotFoundError as e:
        return jsonify({'error': str(e)}), 404
    except DatabaseError as e:
        return jsonify({'error': str(e)}), 500

@quest_bp.route('/players/<player_id>/journal', methods=['GET'])
def get_journal_entries(player_id):
    """Get all journal entries for a player."""
    try:
        QuestValidator.validate_player_id(player_id)
        
        entries = QuestUtils.get_player_journal_entries(player_id)
        
        return jsonify(entries), 200
        
    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    except DatabaseError as e:
        return jsonify({'error': str(e)}), 500 
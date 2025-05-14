"""Quest-related routes and endpoints."""

from flask import Blueprint, request, jsonify
from firebase_admin import db
from datetime import datetime
from typing import Dict, Any, List
from app.auth.auth_utils import require_auth

quest_bp = Blueprint('quest', __name__)

@quest_bp.route('/create', methods=['POST'])
@require_auth
def create_quest() -> Dict[str, Any]:
    """
    Create a new quest.
    
    Returns:
        Dict containing quest data
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['title', 'description', 'type', 'difficulty']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'message': f'Missing required field: {field}'
                }), 400
                
        # Generate quest ID
        quest_id = f"quest_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        # Create quest data
        quest_data = {
            'quest_id': quest_id,
            'title': data['title'],
            'description': data['description'],
            'type': data['type'],
            'difficulty': data['difficulty'],
            'status': 'available',
            'created_at': datetime.utcnow().isoformat(),
            'requirements': data.get('requirements', {}),
            'objectives': data.get('objectives', []),
            'rewards': data.get('rewards', {}),
            'location': data.get('location'),
            'giver_id': data.get('giver_id'),
            'min_level': data.get('min_level', 1),
            'max_level': data.get('max_level'),
            'time_limit': data.get('time_limit'),
            'faction_requirements': data.get('faction_requirements', {}),
            'tags': data.get('tags', [])
        }
        
        # Save quest
        db.reference(f'/quests/{quest_id}').set(quest_data)
        
        return jsonify({
            'success': True,
            'quest': quest_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error creating quest: {str(e)}'
        }), 500

@quest_bp.route('/<quest_id>/accept', methods=['POST'])
@require_auth
def accept_quest(quest_id: str) -> Dict[str, Any]:
    """
    Accept a quest for a character.
    
    Args:
        quest_id: ID of the quest
        
    Returns:
        Dict containing updated quest data
    """
    try:
        data = request.get_json()
        character_id = data.get('character_id')
        
        if not character_id:
            return jsonify({
                'success': False,
                'message': 'Missing character_id'
            }), 400
            
        # Get quest and character data
        quest_ref = db.reference(f'/quests/{quest_id}')
        character_ref = db.reference(f'/characters/{character_id}')
        
        quest = quest_ref.get()
        character = character_ref.get()
        
        if not quest or not character:
            return jsonify({
                'success': False,
                'message': 'Quest or character not found'
            }), 404
            
        # Check requirements
        if not check_quest_requirements(quest, character):
            return jsonify({
                'success': False,
                'message': 'Character does not meet quest requirements'
            }), 400
            
        # Add quest to character's active quests
        active_quests = character.get('active_quests', [])
        if quest_id not in active_quests:
            active_quests.append(quest_id)
            character_ref.update({'active_quests': active_quests})
            
        # Update quest status
        quest['status'] = 'in_progress'
        quest['accepted_by'] = character_id
        quest['accepted_at'] = datetime.utcnow().isoformat()
        quest_ref.set(quest)
        
        return jsonify({
            'success': True,
            'quest': quest
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error accepting quest: {str(e)}'
        }), 500

@quest_bp.route('/<quest_id>/complete', methods=['POST'])
@require_auth
def complete_quest(quest_id: str) -> Dict[str, Any]:
    """
    Complete a quest and award rewards.
    
    Args:
        quest_id: ID of the quest
        
    Returns:
        Dict containing completion results
    """
    try:
        data = request.get_json()
        character_id = data.get('character_id')
        
        if not character_id:
            return jsonify({
                'success': False,
                'message': 'Missing character_id'
            }), 400
            
        # Get quest and character data
        quest_ref = db.reference(f'/quests/{quest_id}')
        character_ref = db.reference(f'/characters/{character_id}')
        
        quest = quest_ref.get()
        character = character_ref.get()
        
        if not quest or not character:
            return jsonify({
                'success': False,
                'message': 'Quest or character not found'
            }), 404
            
        # Verify quest is in progress
        if quest['status'] != 'in_progress' or quest.get('accepted_by') != character_id:
            return jsonify({
                'success': False,
                'message': 'Quest is not in progress for this character'
            }), 400
            
        # Check objectives completion
        if not check_objectives_completion(quest, character):
            return jsonify({
                'success': False,
                'message': 'Not all quest objectives are completed'
            }), 400
            
        # Award rewards
        rewards = award_quest_rewards(quest, character)
        
        # Update quest status
        quest['status'] = 'completed'
        quest['completed_at'] = datetime.utcnow().isoformat()
        quest_ref.set(quest)
        
        # Remove from active quests
        active_quests = character.get('active_quests', [])
        if quest_id in active_quests:
            active_quests.remove(quest_id)
            character_ref.update({'active_quests': active_quests})
            
        # Add to completed quests
        completed_quests = character.get('completed_quests', [])
        completed_quests.append(quest_id)
        character_ref.update({'completed_quests': completed_quests})
        
        return jsonify({
            'success': True,
            'quest': quest,
            'rewards': rewards
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error completing quest: {str(e)}'
        }), 500

@quest_bp.route('/available', methods=['GET'])
@require_auth
def list_available_quests() -> Dict[str, Any]:
    """
    List all available quests for a character.
    
    Returns:
        Dict containing list of available quests
    """
    try:
        character_id = request.args.get('character_id')
        
        if not character_id:
            return jsonify({
                'success': False,
                'message': 'Missing character_id parameter'
            }), 400
            
        # Get character data
        character_ref = db.reference(f'/characters/{character_id}')
        character = character_ref.get()
        
        if not character:
            return jsonify({
                'success': False,
                'message': 'Character not found'
            }), 404
            
        # Get all quests
        quests_ref = db.reference('/quests')
        quests = quests_ref.get() or {}
        
        # Filter available quests
        available_quests = {
            quest_id: quest_data
            for quest_id, quest_data in quests.items()
            if is_quest_available(quest_data, character)
        }
        
        return jsonify({
            'success': True,
            'quests': available_quests
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error listing quests: {str(e)}'
        }), 500

def check_quest_requirements(quest: Dict[str, Any], character: Dict[str, Any]) -> bool:
    """Check if a character meets quest requirements."""
    requirements = quest.get('requirements', {})
    
    # Check level requirements
    if quest.get('min_level') and character.get('level', 1) < quest['min_level']:
        return False
    if quest.get('max_level') and character.get('level', 1) > quest['max_level']:
        return False
        
    # Check faction requirements
    faction_reqs = quest.get('faction_requirements', {})
    character_faction = character.get('faction_id')
    if faction_reqs:
        if 'required_faction' in faction_reqs and character_faction != faction_reqs['required_faction']:
            return False
        if 'forbidden_faction' in faction_reqs and character_faction == faction_reqs['forbidden_faction']:
            return False
            
    # Add more requirement checks as needed
    return True

def check_objectives_completion(quest: Dict[str, Any], character: Dict[str, Any]) -> bool:
    """Check if all quest objectives are completed."""
    objectives = quest.get('objectives', [])
    completed_objectives = character.get('completed_objectives', {}).get(quest['quest_id'], [])
    return len(completed_objectives) == len(objectives)

def award_quest_rewards(quest: Dict[str, Any], character: Dict[str, Any]) -> Dict[str, Any]:
    """Award quest rewards to character."""
    rewards = quest.get('rewards', {})
    awarded = {
        'experience': 0,
        'gold': 0,
        'items': [],
        'reputation': {}
    }
    
    # Award experience
    if 'experience' in rewards:
        awarded['experience'] = rewards['experience']
        new_exp = character.get('experience', 0) + rewards['experience']
        db.reference(f'/characters/{character["character_id"]}').update({'experience': new_exp})
        
    # Award gold
    if 'gold' in rewards:
        awarded['gold'] = rewards['gold']
        new_gold = character.get('gold', 0) + rewards['gold']
        db.reference(f'/characters/{character["character_id"]}').update({'gold': new_gold})
        
    # Award items
    if 'items' in rewards:
        awarded['items'] = rewards['items']
        inventory = character.get('inventory', [])
        inventory.extend(rewards['items'])
        db.reference(f'/characters/{character["character_id"]}').update({'inventory': inventory})
        
    # Award reputation
    if 'reputation' in rewards:
        awarded['reputation'] = rewards['reputation']
        for faction_id, rep_change in rewards['reputation'].items():
            update_faction_reputation(character['character_id'], faction_id, rep_change)
            
    return awarded

def update_faction_reputation(character_id: str, faction_id: str, change: int) -> None:
    """Update a character's reputation with a faction."""
    char_faction_ref = db.reference(f'/faction_reputations/{character_id}/{faction_id}')
    current_rep = char_faction_ref.get() or 0
    char_faction_ref.set(max(-100, min(100, current_rep + change)))

def is_quest_available(quest: Dict[str, Any], character: Dict[str, Any]) -> bool:
    """Check if a quest is available for a character."""
    # Check quest status
    if quest['status'] != 'available':
        return False
        
    # Check if already completed
    if quest['quest_id'] in character.get('completed_quests', []):
        return False
        
    # Check if already active
    if quest['quest_id'] in character.get('active_quests', []):
        return False
        
    # Check requirements
    return check_quest_requirements(quest, character) 
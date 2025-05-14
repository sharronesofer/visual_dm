"""Combat-related routes and endpoints."""

from flask import Blueprint, request, jsonify
from datetime import datetime
from typing import Dict, Any
from app.auth.auth_utils import require_auth
from app.core.database import db
from app.core.models.combat import Combat, CombatParticipant, CombatAction
from app.core.models.character import Character
from app.core.models.inventory import InventoryItem
from app.combat.combat_utils import (
    calculate_attack_bonus,
    calculate_damage,
    apply_damage,
    make_death_saving_throw
)

combat_bp = Blueprint('combat', __name__)

@combat_bp.route('/start', methods=['POST'])
@require_auth
def start_combat() -> Dict[str, Any]:
    """
    Start a new combat encounter.
    
    Returns:
        Dict containing combat data
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['character_id', 'enemies']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'message': f'Missing required field: {field}'
                }), 400
                
        # Create combat
        combat = Combat(
            status='active',
            round_number=1,
            current_turn=0,
            initiative_order=[],
            log=[]
        )
        db.session.add(combat)
        db.session.commit()
        
        # Add participants
        character = db.session.query(Character).get(data['character_id'])
        if not character:
            return jsonify({
                'success': False,
                'message': 'Character not found'
            }), 404
            
        participant = CombatParticipant(
            combat_id=combat.id,
            character_id=character.id,
            initiative=0,
            current_health=character.current_health,
            current_mana=character.current_mana
        )
        db.session.add(participant)
        
        # Add enemies
        for enemy in data['enemies']:
            enemy_participant = CombatParticipant(
                combat_id=combat.id,
                npc_id=enemy['id'],
                initiative=enemy.get('initiative', 0),
                current_health=enemy.get('health', 100),
                current_mana=enemy.get('mana', 100)
            )
            db.session.add(enemy_participant)
            
        db.session.commit()
        
        return jsonify({
            'success': True,
            'combat': combat.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error starting combat: {str(e)}'
        }), 500

@combat_bp.route('/<int:combat_id>/attack', methods=['POST'])
@require_auth
def make_attack(combat_id: int) -> Dict[str, Any]:
    """
    Make an attack in combat.
    
    Args:
        combat_id: ID of the combat
        
    Returns:
        Dict containing attack results
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['attacker_id', 'target_id', 'weapon_id']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'message': f'Missing required field: {field}'
                }), 400
                
        # Get combat data
        combat = db.session.query(Combat).get(combat_id)
        if not combat:
            return jsonify({
                'success': False,
                'message': 'Combat not found'
            }), 404
            
        # Get attacker and target
        attacker = db.session.query(CombatParticipant).get(data['attacker_id'])
        target = db.session.query(CombatParticipant).get(data['target_id'])
        weapon = db.session.query(InventoryItem).get(data['weapon_id'])
        
        if not all([attacker, target, weapon]):
            return jsonify({
                'success': False,
                'message': 'Attacker, target, or weapon not found'
            }), 404
            
        # Calculate attack
        attack_bonus = calculate_attack_bonus(attacker, weapon)
        damage, damage_type = calculate_damage(weapon, attack_bonus)
        
        # Apply damage
        result = apply_damage(target, damage, damage_type)
        
        # Update target HP
        target.current_health = result['current_hp']
        
        # Create combat action
        action = CombatAction(
            combat_id=combat_id,
            actor_id=attacker.id,
            target_id=target.id,
            action_name='attack',
            damage_dealt=result['damage_dealt']
        )
        db.session.add(action)
        
        # Update combat log
        combat.log.append({
            'type': 'attack',
            'attacker_id': attacker.id,
            'target_id': target.id,
            'weapon_id': weapon.id,
            'damage_dealt': result['damage_dealt'],
            'timestamp': datetime.utcnow().isoformat()
        })
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'attack_result': result
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error making attack: {str(e)}'
        }), 500

@combat_bp.route('/<int:combat_id>/death-save', methods=['POST'])
@require_auth
def death_save(combat_id: int) -> Dict[str, Any]:
    """
    Make a death saving throw.
    
    Args:
        combat_id: ID of the combat
        
    Returns:
        Dict containing save results
    """
    try:
        data = request.get_json()
        character_id = data.get('character_id')
        
        if not character_id:
            return jsonify({
                'success': False,
                'message': 'Missing character_id'
            }), 400
            
        # Get character data
        character = db.session.query(Character).get(character_id)
        if not character:
            return jsonify({
                'success': False,
                'message': 'Character not found'
            }), 404
            
        # Make death save
        result = make_death_saving_throw(character)
        
        # Update character
        character.death_save_successes = result.get('successes', 0)
        character.death_save_failures = result.get('failures', 0)
        character.current_health = result.get('current_hp', 0)
        
        # Create combat action
        action = CombatAction(
            combat_id=combat_id,
            actor_id=character.id,
            action_name='death_save',
            damage_dealt=0
        )
        db.session.add(action)
        
        # Update combat log
        combat = db.session.query(Combat).get(combat_id)
        if combat:
            combat.log.append({
                'type': 'death_save',
                'character_id': character.id,
                'success': result.get('success', False),
                'timestamp': datetime.utcnow().isoformat()
            })
            
        db.session.commit()
        
        return jsonify({
            'success': True,
            'save_result': result
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error making death save: {str(e)}'
        }), 500

@combat_bp.route('/<int:combat_id>/end', methods=['POST'])
@require_auth
def end_combat(combat_id: int) -> Dict[str, Any]:
    """
    End a combat encounter.
    
    Args:
        combat_id: ID of the combat
        
    Returns:
        Dict containing end results
    """
    try:
        combat = db.session.query(Combat).get(combat_id)
        if not combat:
            return jsonify({
                'success': False,
                'message': 'Combat not found'
            }), 404
            
        combat.status = 'completed'
        combat.is_active = False
        
        # Update participants
        for participant in combat.participants:
            participant.is_active = False
            
        db.session.commit()
        
        return jsonify({
            'success': True,
            'combat': combat.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error ending combat: {str(e)}'
        }), 500 
"""
Combat-related API routes.
Provides endpoints for combat management and interaction.
"""

from flask import Blueprint, request, jsonify
from typing import Dict, Any, List, Optional
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm import joinedload
from app.core.database import db
from app.core.models.character import Character
from app.core.models.user import User
from app.core.models.party import Party
from app.core.models.world import Region
from app.core.models.quest import Quest
from app.core.models.spell import Spell
from app.core.models.inventory import InventoryItem
from app.core.models.save import SaveGame
from app.combat.combat_utils import resolve_combat_action, apply_combat_effects
from app.combat.combat_ram import ACTIVE_BATTLES
from app.core.utils.error_utils import ValidationError, DatabaseError, NotFoundError
from app.combat.combat_class import Combatant
from app.regions.worldgen_utils import attempt_rest
from app.combat.combat_state_class import CombatState
from uuid import uuid4
from datetime import datetime
from fastapi import APIRouter, HTTPException

combat_bp = Blueprint("combat", __name__)

router = APIRouter(prefix="/combat", tags=["combat"])

@router.post("/start")
async def start_combat(participants: List[Dict]) -> Dict:
    """Start a new combat encounter."""
    try:
        # Create combat state
        combat_state = CombatState()
        db.session.add(combat_state)
        db.session.flush()

        # Add participants
        for p_data in participants:
            participant = CombatParticipant(
                combat_state_id=combat_state.id,
                character_id=p_data.get('character_id'),
                npc_id=p_data.get('npc_id'),
                current_health=p_data.get('current_health', 0),
                current_mana=p_data.get('current_mana', 0)
            )
            db.session.add(participant)

        # Initialize combat engine
        engine = CombatEngine(combat_state)
        engine.roll_initiative()

        db.session.commit()
        return combat_state.to_dict()

    except Exception as e:
        db.session.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{combat_id}")
async def get_combat(combat_id: int) -> Dict:
    """Get combat state by ID."""
    combat_state = CombatState.query.get(combat_id)
    if not combat_state:
        raise HTTPException(status_code=404, detail="Combat not found")
    return combat_state.to_dict()

@router.post("/{combat_id}/action")
async def process_combat_action(combat_id: int, action: Dict) -> Dict:
    """Process a combat action."""
    combat_state = CombatState.query.get(combat_id)
    if not combat_state:
        raise HTTPException(status_code=404, detail="Combat not found")

    engine = CombatEngine(combat_state)
    result = engine.process_turn(action)
    
    db.session.commit()
    return result

@router.post("/{combat_id}/end")
async def end_combat(combat_id: int) -> Dict:
    """End a combat encounter."""
    combat_state = CombatState.query.get(combat_id)
    if not combat_state:
        raise HTTPException(status_code=404, detail="Combat not found")

    combat_state.status = 'completed'
    db.session.commit()
    return combat_state.to_dict()

@combat_bp.route('/combats', methods=['GET'])
def get_combats():
    """Get all active combat encounters."""
    combats = db.session.query(Combat).filter_by(is_active=True).all()
    return jsonify([combat.to_dict() for combat in combats]), 200

@combat_bp.route('/combats/<int:combat_id>', methods=['GET'])
def get_combat(combat_id):
    """Get a specific combat encounter."""
    combat = db.session.query(Combat).get_or_404(combat_id)
    return jsonify(combat.to_dict()), 200

@combat_bp.route('/combats/<int:combat_id>/participants', methods=['POST'])
def add_participant(combat_id):
    """Add a participant to a combat encounter."""
    data = request.get_json()
    participant = CombatParticipant(
        combat_id=combat_id,
        character_id=data.get('character_id'),
        npc_id=data.get('npc_id'),
        initiative=data.get('initiative', 0),
        current_health=data.get('current_health', 100),
        current_mana=data.get('current_mana', 100)
    )
    db.session.add(participant)
    db.session.commit()
    return jsonify(participant.to_dict()), 201

@combat_bp.route('/combats/<int:combat_id>/actions', methods=['POST'])
def add_action(combat_id):
    """Add an action to a combat encounter."""
    data = request.get_json()
    action = CombatAction(
        combat_id=combat_id,
        actor_id=data.get('actor_id'),
        target_id=data.get('target_id'),
        action_type=data.get('action_type'),
        action_name=data.get('action_name'),
        damage_dealt=data.get('damage_dealt', 0),
        healing_done=data.get('healing_done', 0)
    )
    db.session.add(action)
    db.session.commit()
    return jsonify(action.to_dict()), 201

@combat_bp.route('/combats/<int:combat_id>/state', methods=['GET'])
def get_combat_state(combat_id):
    """Get the current state of a combat encounter."""
    try:
        combat = db.session.query(Combat).get(combat_id)
        if not combat:
            return jsonify({"error": "Combat not found"}), 404
            
        return jsonify({
            "combat_id": combat.id,
            "status": combat.status,
            "participants": [p.to_dict() for p in combat.participants],
            "actions": [a.to_dict() for a in combat.actions]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@combat_bp.route('/combats/<int:combat_id>/participants', methods=['GET'])
def get_combat_participants(combat_id):
    """Get all participants in a combat encounter with related data."""
    try:
        combat = db.session.query(Combat)\
            .options(
                joinedload(Combat.participants).joinedload(CombatParticipant.character).joinedload(Character.combat_stats),
                joinedload(Combat.participants).joinedload(CombatParticipant.character).joinedload(Character.inventory),
                joinedload(Combat.participants).joinedload(CombatParticipant.character).joinedload(Character.spells)
            )\
            .get(combat_id)
            
        if not combat:
            return jsonify({"error": "Combat not found"}), 404
            
        return jsonify({
            "participants": [{
                **p.to_dict(),
                "character": {
                    **p.character.to_dict(),
                    "combat_stats": p.character.combat_stats.to_dict() if p.character.combat_stats else None,
                    "inventory": [item.to_dict() for item in p.character.inventory],
                    "spells": [spell.to_dict() for spell in p.character.spells]
                }
            } for p in combat.participants]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@combat_bp.route('/combats/<int:combat_id>/actions', methods=['GET'])
def get_combat_actions(combat_id):
    """Get all actions in a combat encounter."""
    try:
        combat = db.session.query(Combat).get(combat_id)
        if not combat:
            return jsonify({"error": "Combat not found"}), 404
            
        return jsonify({
            "actions": [a.to_dict() for a in combat.actions]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@combat_bp.route('/combats/round', methods=['POST'])
def combat_round():
    data = request.get_json(force=True)
    combatants = data.get("combatants")
    battlefield_context = data.get("battlefield_context", {})

    if not isinstance(combatants, list) or not combatants:
        return jsonify({"error": "A non-empty 'combatants' list is required."}), 400

    actions = []

    for combatant in combatants:
        if combatant.get("type") == "npc":
            action_data = choose_action_gpt(combatant, battlefield_context)

            target_id = action_data.get("target")
            if not target_id:
                actions.append({
                    "character_id": combatant.get("npc_id"),
                    "result": "No target specified"
                })
                continue

            # TEMPORARY: Mock target data (should be loaded from DB in real case)
            target_data = {
                "id": target_id,
                "character_id": target_id,
                "attributes": {"HP": 30, "AC": 12, "DEX": 10},
                "feats": [],
                "equipment": []
            }

            attacker_obj = Combatant(combatant["npc_id"], combatant)
            target_obj = Combatant(target_id, target_data)

            combat_action = CombatAction(attacker_obj, target_obj, action_data, battlefield_context)
            result = combat_action.resolve()
            actions.append(result)

        else:
            actions.append({
                "character_id": combatant.get("character_id"),
                "result": "awaiting_player_action"
            })

    return jsonify({"results": actions}), 200

@combat_bp.route('/combats/long_rest/<character_id>', methods=['POST'])
def long_rest(character_id):
    try:
        character = db.session.query(Character).get(character_id)
        if not character:
            return jsonify({"error": "Character not found"}), 404

        location = character.location
        if not location:
            return jsonify({"error": "Character has no location"}), 400

        result = attempt_rest(character, location)
        if result.get("success"):
            return jsonify(result), 200
        else:
            return jsonify(result), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@combat_bp.route('/combats/action/<battle_id>', methods=['POST'])
def combat_action_handler(battle_id):
    try:
        data = request.get_json()
        action = data.get("action")
        if not action:
            return jsonify({"error": "No action provided"}), 400

        result = resolve_combat_action(battle_id, action)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@combat_bp.route('/combats/turn', methods=['POST'])
def process_turn():
    try:
        data = request.get_json()
        battle_id = data.get("battle_id")
        if not battle_id:
            return jsonify({"error": "No battle_id provided"}), 400

        battle = ACTIVE_BATTLES.get(battle_id)
        if not battle:
            return jsonify({"error": "Battle not found"}), 404

        result = battle.process_turn()
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@combat_bp.route('/combats/resolve_action', methods=['POST'])
def resolve_action():
    try:
        data = request.get_json()
        battle_id = data.get("battle_id")
        action = data.get("action")
        if not battle_id or not action:
            return jsonify({"error": "Missing battle_id or action"}), 400

        result = resolve_combat_action(battle_id, action)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

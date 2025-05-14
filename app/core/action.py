"""
Action system for handling combat and other actions.
"""

from flask import current_app
from app.core.firebase import db as firebase_db
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import random

class ActionSystem:
    def __init__(self, app):
        self.app = app
        self.action_collection = firebase_db.collection('actions')
        self.combat_collection = firebase_db.collection('combat_instances')
        
    def perform_action(self, actor_id: str, target_id: str,
                      action_type: str, context: Dict) -> Dict:
        """Perform an action and return the result."""
        # Get actor and target
        actor = self._get_actor(actor_id)
        target = self._get_actor(target_id)
        
        if not actor or not target:
            return {'success': False, 'error': 'Actor or target not found'}
            
        # Calculate success chance
        success_chance = self._calculate_success_chance(
            actor, target, action_type, context
        )
        
        # Determine outcome
        success = random.random() < success_chance
        result = self._generate_result(
            actor, target, action_type, success, context
        )
        
        # Record action
        self._record_action(
            actor_id, target_id, action_type, success, result
        )
        
        return result
        
    def start_combat(self, participants: List[str]) -> str:
        """Start a combat instance between participants."""
        combat = {
            'participants': participants,
            'turn_order': self._determine_turn_order(participants),
            'current_turn': 0,
            'round': 1,
            'started_at': datetime.utcnow().isoformat(),
            'status': 'active',
            'actions': []
        }
        
        combat_doc = self.combat_collection.add(combat)
        return combat_doc[1].id
        
    def process_combat_turn(self, combat_id: str, 
                          action: Dict) -> Dict:
        """Process a turn in combat."""
        combat_doc = self.combat_collection.document(combat_id).get()
        if not combat_doc.exists:
            return {'success': False, 'error': 'Combat not found'}
            
        combat = combat_doc.to_dict()
        
        # Validate turn
        if not self._validate_turn(combat, action):
            return {'success': False, 'error': 'Invalid turn'}
            
        # Process action
        result = self.perform_action(
            action['actor_id'],
            action['target_id'],
            action['type'],
            {'combat': True, **action.get('context', {})}
        )
        
        # Update combat state
        self._update_combat_state(combat_id, action, result)
        
        return result
        
    def _get_actor(self, actor_id: str) -> Optional[Dict]:
        """Get an actor (character or NPC) by ID."""
        # Try character first
        character = current_app.character_system.get_character(actor_id)
        if character:
            return character
            
        # Try NPC
        npc = current_app.npc_system.get_npc(actor_id)
        if npc:
            return npc
            
        return None
        
    def _calculate_success_chance(self, actor: Dict, target: Dict,
                                action_type: str, context: Dict) -> float:
        """Calculate the chance of action success."""
        base_chance = 0.5
        
        # Adjust based on action type
        if action_type == 'attack':
            base_chance = self._calculate_attack_chance(actor, target)
        elif action_type == 'cast_spell':
            base_chance = self._calculate_spell_chance(actor, target, context)
        elif action_type == 'use_item':
            base_chance = self._calculate_item_chance(actor, target, context)
            
        # Apply context modifiers
        if context.get('combat'):
            base_chance *= 0.8  # Actions are harder in combat
            
        if context.get('advantage'):
            base_chance *= 1.2
            
        if context.get('disadvantage'):
            base_chance *= 0.8
            
        return min(0.95, max(0.05, base_chance))
        
    def _calculate_attack_chance(self, actor: Dict, target: Dict) -> float:
        """Calculate chance to hit in combat."""
        # Base on attack vs defense
        attack = actor.get('attack_bonus', 0)
        defense = target.get('armor_class', 10)
        
        # Add modifiers from stats
        if 'strength' in actor:
            attack += (actor['strength'] - 10) // 2
            
        if 'dexterity' in target:
            defense += (target['dexterity'] - 10) // 2
            
        # Calculate hit chance
        hit_chance = 0.5 + (attack - defense) * 0.05
        return min(0.95, max(0.05, hit_chance))
        
    def _calculate_spell_chance(self, actor: Dict, target: Dict,
                              context: Dict) -> float:
        """Calculate chance to successfully cast a spell."""
        # Base on spell level and caster level
        spell_level = context.get('spell_level', 1)
        caster_level = actor.get('level', 1)
        
        # Add modifiers from stats
        if 'intelligence' in actor:
            caster_level += (actor['intelligence'] - 10) // 4
            
        # Calculate success chance
        success_chance = 0.7 - (spell_level - caster_level) * 0.1
        return min(0.95, max(0.05, success_chance))
        
    def _calculate_item_chance(self, actor: Dict, target: Dict,
                             context: Dict) -> float:
        """Calculate chance to successfully use an item."""
        # Base on item complexity
        complexity = context.get('complexity', 1)
        
        # Add modifiers from stats
        if 'dexterity' in actor:
            complexity -= (actor['dexterity'] - 10) // 4
            
        # Calculate success chance
        success_chance = 0.8 - complexity * 0.1
        return min(0.95, max(0.05, success_chance))
        
    def _generate_result(self, actor: Dict, target: Dict,
                        action_type: str, success: bool,
                        context: Dict) -> Dict:
        """Generate the result of an action."""
        result = {
            'success': success,
            'action_type': action_type,
            'actor_id': actor['id'],
            'target_id': target['id'],
            'damage': 0,
            'effects': [],
            'message': ''
        }
        
        if success:
            if action_type == 'attack':
                result.update(self._generate_attack_result(actor, target))
            elif action_type == 'cast_spell':
                result.update(self._generate_spell_result(actor, target, context))
            elif action_type == 'use_item':
                result.update(self._generate_item_result(actor, target, context))
        else:
            result['message'] = self._generate_failure_message(
                action_type, actor, target
            )
            
        return result
        
    def _generate_attack_result(self, actor: Dict, target: Dict) -> Dict:
        """Generate the result of an attack."""
        # Calculate damage
        base_damage = random.randint(1, 6)  # d6
        if 'strength' in actor:
            base_damage += (actor['strength'] - 10) // 2
            
        # Apply target's damage reduction
        damage_reduction = target.get('damage_reduction', 0)
        final_damage = max(1, base_damage - damage_reduction)
        
        return {
            'damage': final_damage,
            'effects': ['hit'],
            'message': f"{actor['name']} hits {target['name']} for {final_damage} damage!"
        }
        
    def _generate_spell_result(self, actor: Dict, target: Dict,
                             context: Dict) -> Dict:
        """Generate the result of a spell."""
        spell = context.get('spell', {})
        effects = spell.get('effects', [])
        
        return {
            'damage': spell.get('damage', 0),
            'effects': effects,
            'message': f"{actor['name']} casts {spell['name']} on {target['name']}!"
        }
        
    def _generate_item_result(self, actor: Dict, target: Dict,
                            context: Dict) -> Dict:
        """Generate the result of using an item."""
        item = context.get('item', {})
        effects = item.get('effects', [])
        
        return {
            'damage': item.get('damage', 0),
            'effects': effects,
            'message': f"{actor['name']} uses {item['name']} on {target['name']}!"
        }
        
    def _generate_failure_message(self, action_type: str,
                                actor: Dict, target: Dict) -> str:
        """Generate a failure message for an action."""
        messages = {
            'attack': [
                f"{actor['name']} misses {target['name']}!",
                f"{target['name']} dodges {actor['name']}'s attack!",
                f"{actor['name']}'s attack glances off {target['name']}'s armor!"
            ],
            'cast_spell': [
                f"{actor['name']} fails to cast the spell!",
                f"The spell fizzles in {actor['name']}'s hands!",
                f"{target['name']} resists the spell!"
            ],
            'use_item': [
                f"{actor['name']} fumbles with the item!",
                f"The item fails to activate!",
                f"{target['name']} avoids the item's effect!"
            ]
        }
        
        return random.choice(messages.get(action_type, ['Action failed!']))
        
    def _determine_turn_order(self, participants: List[str]) -> List[str]:
        """Determine the order of turns in combat."""
        # Get initiative for each participant
        initiatives = []
        for participant_id in participants:
            actor = self._get_actor(participant_id)
            if actor:
                # Base initiative on dexterity
                initiative = random.randint(1, 20)
                if 'dexterity' in actor:
                    initiative += (actor['dexterity'] - 10) // 2
                    
                initiatives.append((participant_id, initiative))
                
        # Sort by initiative (highest first)
        initiatives.sort(key=lambda x: x[1], reverse=True)
        return [x[0] for x in initiatives]
        
    def _validate_turn(self, combat: Dict, action: Dict) -> bool:
        """Validate if an action can be taken in the current turn."""
        current_actor = combat['turn_order'][combat['current_turn']]
        return (
            action['actor_id'] == current_actor and
            action['target_id'] in combat['participants'] and
            combat['status'] == 'active'
        )
        
    def _update_combat_state(self, combat_id: str, action: Dict,
                           result: Dict) -> None:
        """Update the state of combat after an action."""
        combat_ref = self.combat_collection.document(combat_id)
        combat = combat_ref.get().to_dict()
        
        # Add action to history
        combat['actions'].append({
            'round': combat['round'],
            'turn': combat['current_turn'],
            'action': action,
            'result': result
        })
        
        # Update turn order
        combat['current_turn'] = (combat['current_turn'] + 1) % len(combat['turn_order'])
        if combat['current_turn'] == 0:
            combat['round'] += 1
            
        # Check for combat end
        if self._check_combat_end(combat):
            combat['status'] = 'ended'
            combat['ended_at'] = datetime.utcnow().isoformat()
            
        combat_ref.update(combat)
        
    def _check_combat_end(self, combat: Dict) -> bool:
        """Check if combat should end."""
        # Check if all participants on one side are defeated
        participants = combat['participants']
        active_participants = set()
        
        for action in combat['actions']:
            result = action['result']
            if result['success'] and result['damage'] > 0:
                target = self._get_actor(result['target_id'])
                if target and target.get('hit_points', 0) <= 0:
                    participants.remove(result['target_id'])
                    
        return len(participants) <= 1
        
    def _record_action(self, actor_id: str, target_id: str,
                      action_type: str, success: bool,
                      result: Dict) -> None:
        """Record an action in the database."""
        self.action_collection.add({
            'actor_id': actor_id,
            'target_id': target_id,
            'action_type': action_type,
            'success': success,
            'result': result,
            'timestamp': datetime.utcnow().isoformat()
        })

def init_action_system(app):
    """Initialize the action system."""
    app.action_system = ActionSystem(app) 
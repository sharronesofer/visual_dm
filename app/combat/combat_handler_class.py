"""
Combat action handler.
Provides functionality for processing combat actions and their effects.
"""

from typing import Dict, List, Optional, Any, Tuple
from app.core.models.combat import CombatState, CombatParticipant, CombatEngine
from app.core.models.character import Character
from app.core.models.npc import NPC
from app.core.models.spell import Spell, SpellEffect
from sqlalchemy.orm import Session
from app.combat.tactical_advantages import calculate_terrain_advantage
from app.combat.combat_utils import calculate_damage, apply_status_effects
from app.core.database import db
from app.combat.flanking_mechanics import FlankingHandler, process_opportunity_attack
from app.combat.opportunity_attacks import OpportunityAttackHandler
from app.combat.reach_weapons import ReachWeaponHandler

class CombatActionHandler:
    """Handler class for processing combat actions."""
    
    def __init__(self, combat_state: CombatState):
        self.combat_state = combat_state
        self.engine = CombatEngine(combat_state)

    def process_action(self, action: Dict) -> Dict:
        """Process a combat action and return the results."""
        current_actor = self.combat_state.get_current_actor()
        if not current_actor:
            return {'error': 'No current actor'}

        result = {
            'success': True,
            'actor_id': current_actor.id,
            'action': action,
            'effects': []
        }

        # Process action based on type
        if action['type'] == 'attack':
            target = next(p for p in self.combat_state.participants if p.id == action['target_id'])
            damage = self._calculate_damage(current_actor, action)
            target.take_damage(damage)
            result['effects'].append({
                'type': 'damage',
                'target_id': target.id,
                'amount': damage
            })
        elif action['type'] == 'spell':
            spell = self._get_spell(action['spell_id'])
            for effect in spell.effects:
                effect_result = effect.apply(current_actor)
                result['effects'].append(effect_result)
        elif action['type'] == 'item':
            item = self._get_item(action['item_id'])
            for effect in item.effects:
                effect_result = effect.apply(current_actor)
                result['effects'].append(effect_result)

        # Advance turn
        self.combat_state.next_turn()
        db.session.commit()

        return result

    def _calculate_damage(self, attacker: CombatParticipant, action: Dict) -> int:
        """Calculate damage for an attack."""
        base_damage = action.get('damage', 0)
        if attacker.character:
            damage_bonus = (attacker.character.strength - 10) // 2
        else:
            damage_bonus = (attacker.npc.strength - 10) // 2
        return base_damage + damage_bonus

    def _get_spell(self, spell_id: int) -> Spell:
        """Get a spell by ID."""
        return Spell.query.get(spell_id)

    def _get_item(self, item_id: int) -> 'Item':
        """Get an item by ID."""
        from app.core.models.item import Item
        return Item.query.get(item_id)

    def validate_action(self, action: Dict) -> bool:
        """Validate a combat action."""
        if not action.get('type'):
            return False

        current_actor = self.combat_state.get_current_actor()
        if not current_actor:
            return False

        if action['type'] == 'attack':
            if not action.get('target_id'):
                return False
            target = next((p for p in self.combat_state.participants if p.id == action['target_id']), None)
            if not target:
                return False
        elif action['type'] == 'spell':
            if not action.get('spell_id'):
                return False
            spell = self._get_spell(action['spell_id'])
            if not spell:
                return False
        elif action['type'] == 'item':
            if not action.get('item_id'):
                return False
            item = self._get_item(action['item_id'])
            if not item:
                return False

        return True

class CombatAction:
    def __init__(self, actor_id, action_data, full_attributes, combatant_state):
        self.actor_id = actor_id
        self.action_data = action_data  # Contains 'type', 'target', 'mp_cost', etc.
        self.full_attributes = full_attributes    # Actor's full character attributes
        self.combatant_state = combatant_state  # RAM state during combat
        self.outcome = {}

    def parse(self):
        return {
            "actor": self.actor_id,
            "action_type": self.action_data.get("type", "Attack"),
            "target": self.action_data.get("target"),
            "mp_cost": self.action_data.get("mp_cost", 0),
            "details": self.action_data
        }

class CombatEngine:
    def __init__(self, combat_state, characters):
        self.state = combat_state
        self.characters = characters

    def initiate_combat(self):
        # Set up initiative, shuffle turn order
        pass

    def resolve_turn(self, actor_id):
        # Call CombatActionHandler or roll initiative logic
        pass

    def narrate_combat_action(self, actor, action, outcome):
        return f"{actor['name']} performs {action}: {outcome}"

class CombatHandler:
    def __init__(self, combat_id: int):
        self.combat = Combat.query.get(combat_id)
        if not self.combat:
            raise ValueError(f"Combat with id {combat_id} not found")
        self.flanking_handler = FlankingHandler(combat_id)
        self.opportunity_handler = OpportunityAttackHandler(combat_id)
        self.reach_handler = ReachWeaponHandler(combat_id)

    def start_round(self) -> None:
        """Start a new combat round."""
        self.combat.round_number += 1
        self.combat.current_turn = 0
        
        # Reset opportunity attacks
        self.opportunity_handler.reset_opportunity_attacks()
        
        db.session.commit()

    def process_attack(self, attacker_id: int, target_id: int, action_type: str) -> Dict[str, Any]:
        """
        Process an attack action between two participants.
        
        Args:
            attacker_id: ID of the attacking participant
            target_id: ID of the target participant
            action_type: Type of attack action
            
        Returns:
            Dict containing the results of the attack
        """
        attacker = CombatParticipant.query.get(attacker_id)
        target = CombatParticipant.query.get(target_id)
        
        if not attacker or not target:
            raise ValueError("Attacker or target not found")
            
        # Check if attack is valid based on reach
        is_valid, reason = self.reach_handler.check_reach_attack_valid(attacker_id, target_id)
        if not is_valid:
            return {
                'success': False,
                'error': reason
            }
            
        # Update flanking effects before attack
        self.flanking_handler.apply_flanking_effects(target_id)
            
        # Calculate terrain advantages
        terrain_mods = {}
        if self.combat.tactical_grid:
            terrain_mods = calculate_terrain_advantage(
                self.combat.tactical_grid,
                attacker.position,
                target.position
            )
            
        # Apply reach weapon effects
        reach_effects = self.reach_handler.apply_reach_weapon_effects(
            attacker_id,
            action_type
        )
            
        # Calculate base damage with all modifiers
        damage = calculate_damage(
            attacker=attacker,
            target=target,
            action_type=action_type,
            terrain_modifiers=terrain_mods,
            reach_effects=reach_effects
        )
        
        # Apply damage and effects
        target.current_health = max(0, target.current_health - damage)
        
        # Update facing
        attacker.face_towards(target.position_q, target.position_r)
        
        # Log the action
        log_entry = {
            'round': self.combat.round_number,
            'attacker_id': attacker_id,
            'target_id': target_id,
            'action_type': action_type,
            'damage': damage,
            'terrain_advantages': terrain_mods,
            'reach_effects': reach_effects,
            'attacker_position': attacker.position,
            'target_position': target.position,
            'flanking_bonus': any(
                effect.get('type') == 'flanking'
                for effect in attacker.status_effects or []
            )
        }
        
        if not self.combat.log:
            self.combat.log = []
        self.combat.log.append(log_entry)
        
        # Check for combat end
        if target.current_health <= 0:
            self.handle_participant_defeat(target)
            
        db.session.commit()
        
        return {
            'success': True,
            'damage': damage,
            'terrain_advantages': terrain_mods,
            'reach_effects': reach_effects,
            'target_remaining_health': target.current_health,
            'log_entry': log_entry
        }

    def move_participant(
        self,
        participant_id: int,
        movement_path: List[Tuple[int, int]]
    ) -> Dict[str, Any]:
        """
        Move a participant along a path, handling opportunity attacks.
        
        Args:
            participant_id: ID of the participant to move
            movement_path: List of (q, r) positions in movement path
            
        Returns:
            Dict containing results of the move and any opportunity attacks
        """
        if not movement_path:
            return {'success': False, 'error': 'Empty movement path'}
            
        participant = CombatParticipant.query.get(participant_id)
        if not participant:
            return {'success': False, 'error': 'Participant not found'}
            
        # Validate each step in the path
        for position in movement_path:
            if position not in self.get_valid_moves(participant_id):
                return {
                    'success': False,
                    'error': f'Invalid move position: {position}'
                }
        
        old_position = participant.position
        
        # Check for opportunity attacks along the path
        triggers = self.opportunity_handler.check_opportunity_attack_triggers(
            participant_id,
            movement_path
        )
        
        # Process any triggered attacks
        opportunity_results = []
        if triggers:
            opportunity_results = self.opportunity_handler.process_opportunity_attacks(
                participant_id,
                triggers
            )
            
            # Check if participant was defeated by opportunity attacks
            if participant.current_health <= 0:
                self.handle_participant_defeat(participant)
                return {
                    'success': False,
                    'error': 'Participant defeated by opportunity attack',
                    'opportunity_attacks': opportunity_results
                }
        
        # Complete the movement
        participant.move_to(*movement_path[-1])
        
        # Update flanking effects for all participants
        for p in CombatParticipant.query.filter_by(combat_id=self.combat.id).all():
            self.flanking_handler.apply_flanking_effects(p.id)
            
        db.session.commit()
        
        return {
            'success': True,
            'old_position': old_position,
            'new_position': movement_path[-1],
            'path': movement_path,
            'opportunity_attacks': opportunity_results
        }

    def get_valid_moves(self, participant_id: int) -> List[Tuple[int, int]]:
        """
        Get valid movement positions for a participant.
        
        Args:
            participant_id: ID of the participant
            
        Returns:
            List of (q, r) coordinates representing valid moves
        """
        participant = CombatParticipant.query.get(participant_id)
        if not participant or not self.combat.tactical_grid:
            return []
            
        # Get all cells within movement range
        grid = self.combat.tactical_grid
        current_pos = participant.position
        movement_range = participant.movement_points
        
        # Apply movement penalties from status effects
        if participant.status_effects:
            for effect in participant.status_effects:
                if effect.get('type') == 'difficult_terrain':
                    movement_range = max(1, movement_range // 2)
                    break
        
        valid_moves = []
        for q in range(-movement_range, movement_range + 1):
            for r in range(-movement_range, movement_range + 1):
                candidate = (current_pos[0] + q, current_pos[1] + r)
                if grid.is_valid_move(current_pos, candidate, movement_range):
                    # Check if position is occupied
                    occupied = CombatParticipant.query.filter(
                        CombatParticipant.combat_id == self.combat.id,
                        CombatParticipant.position_q == candidate[0],
                        CombatParticipant.position_r == candidate[1]
                    ).first()
                    
                    if not occupied:
                        valid_moves.append(candidate)
        
        return valid_moves

    def get_valid_targets(self, attacker_id: int) -> List[Dict[str, Any]]:
        """
        Get all valid targets for an attacker based on reach and line of sight.
        
        Args:
            attacker_id: ID of the attacking participant
            
        Returns:
            List of dicts containing target info and attack validity
        """
        attacker = CombatParticipant.query.get(attacker_id)
        if not attacker:
            return []
            
        # Get all participants in combat except attacker
        potential_targets = CombatParticipant.query.filter(
            CombatParticipant.combat_id == self.combat.id,
            CombatParticipant.id != attacker_id
        ).all()
        
        valid_targets = []
        for target in potential_targets:
            # Skip defeated targets
            if any(effect.get('type') == 'defeated' for effect in target.status_effects or []):
                continue
                
            # Check if attack is valid
            is_valid, reason = self.reach_handler.check_reach_attack_valid(
                attacker_id,
                target.id
            )
            
            valid_targets.append({
                'target_id': target.id,
                'position': target.position,
                'current_health': target.current_health,
                'is_valid_target': is_valid,
                'invalid_reason': reason if not is_valid else None
            })
            
        return valid_targets

    def handle_participant_defeat(self, participant: CombatParticipant) -> None:
        """Handle when a participant is defeated in combat."""
        participant.status_effects.append({
            'type': 'defeated',
            'duration': -1  # Permanent
        })
        
        # Check if combat should end
        active_participants = CombatParticipant.query.filter(
            CombatParticipant.combat_id == self.combat.id,
            ~CombatParticipant.status_effects.contains([{'type': 'defeated'}])
        ).all()
        
        if len(active_participants) <= 1:
            self.end_combat()

    def end_combat(self) -> None:
        """End the current combat encounter."""
        self.combat.status = 'completed'
        db.session.commit()

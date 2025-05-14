"""
Combat system for managing battles and combat mechanics.
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime
import random
from firebase_admin import firestore
from app.core.models.status import StatusEffect, EffectType
from app.combat.damage_engine import DamageCalculationEngine, AttackType, DamageResult
from app.combat.combat_logger import CombatLogger, LogCategory, LogLevel
from app.combat.state_manager import CombatStateManager
from app.combat.resolution import CombatResolutionManager, CombatEndCondition

class CombatSystem:
    def __init__(self, app):
        self.app = app
        self.db = firestore.client()
        self.combat_collection = self.db.collection('combat_instances')
        self.damage_engine = DamageCalculationEngine()
        self.active_loggers: Dict[str, CombatLogger] = {}
        self.state_manager = CombatStateManager(app)
        self.resolution_manager = CombatResolutionManager(app)
        
    async def create_combat(self, participants: List[str]) -> Dict:
        """Create a new combat instance."""
        combat_data = {
            'participants': participants,
            'current_round': 1,
            'current_turn': 0,
            'initiative_order': [],
            'status': 'preparing',
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }
        
        # Save initial state
        combat_id = str(await self.combat_collection.insert_one(combat_data))
        await self.state_manager.save_combat_state(combat_id, combat_data)
        
        # Initialize logger
        self.active_loggers[combat_id] = CombatLogger(combat_id, self.app.db)
        
        return {'success': True, 'combat_id': combat_id}

    async def end_combat(self, combat_id: str, winner: Optional[str] = None) -> Dict:
        """End a combat encounter."""
        try:
            # Update combat status
            await self.state_manager.update_combat_status(combat_id, 'completed')
            
            # Save final state with winner
            state = await self.state_manager.load_combat_state(combat_id)
            if state:
                state_dict = {
                    'status': 'completed',
                    'winner': winner,
                    'updated_at': datetime.now()
                }
                await self.state_manager.save_combat_state(combat_id, state_dict)
            
            # Clean up logger
            if combat_id in self.active_loggers:
                del self.active_loggers[combat_id]
            
            return {'success': True, 'message': 'Combat ended successfully'}
            
        except Exception as e:
            return {'success': False, 'message': f'Error ending combat: {str(e)}'}

    async def pause_combat(self, combat_id: str) -> Dict:
        """Pause a combat encounter."""
        try:
            # Save current state
            combat = await self.get_combat(combat_id)
            if combat:
                await self.state_manager.save_combat_state(combat_id, combat)
                await self.state_manager.update_combat_status(combat_id, 'paused')
                return {'success': True, 'message': 'Combat paused successfully'}
            return {'success': False, 'message': 'Combat not found'}
            
        except Exception as e:
            return {'success': False, 'message': f'Error pausing combat: {str(e)}'}

    async def resume_combat(self, combat_id: str) -> Dict:
        """Resume a paused combat encounter."""
        try:
            # Load saved state
            state = await self.state_manager.load_combat_state(combat_id)
            if not state:
                return {'success': False, 'message': 'No saved state found'}
                
            # Update status and restore state
            await self.state_manager.update_combat_status(combat_id, 'active')
            await self.combat_collection.update_one(
                {'_id': combat_id},
                {'$set': {
                    'status': 'active',
                    'updated_at': datetime.now()
                }}
            )
            
            return {'success': True, 'message': 'Combat resumed successfully'}
            
        except Exception as e:
            return {'success': False, 'message': f'Error resuming combat: {str(e)}'}

    async def get_combat(self, combat_id: str) -> Optional[Dict]:
        """Get current combat state."""
        try:
            state = await self.state_manager.load_combat_state(combat_id)
            if state:
                return {
                    'combat_id': state.combat_id,
                    'participants': state.participants,
                    'initiative_order': state.initiative_order,
                    'current_round': state.current_round,
                    'current_turn': state.current_turn,
                    'active_effects': state.active_effects,
                    'battlefield_conditions': state.battlefield_conditions,
                    'status': state.status,
                    'created_at': state.created_at,
                    'updated_at': state.updated_at,
                    'winner': state.winner
                }
            return None
            
        except Exception as e:
            self.app.logger.error(f"Error getting combat state: {str(e)}")
            return None

    async def process_turn(self, combat_id: str, action_data: Dict) -> Dict:
        """Process a turn in combat."""
        try:
            # Get current state
            state = await self.state_manager.load_combat_state(combat_id)
            if not state:
                return {'success': False, 'message': 'Combat not found'}
                
            # Process the action
            # ... existing action processing code ...
            
            # Update state after action
            state_dict = {
                'current_turn': state.current_turn + 1,
                'updated_at': datetime.now()
            }
            
            # If round is complete, increment round counter
            if state.current_turn + 1 >= len(state.initiative_order):
                state_dict['current_round'] = state.current_round + 1
                state_dict['current_turn'] = 0
            
            await self.state_manager.save_combat_state(combat_id, state_dict)
            
            return {'success': True, 'message': 'Turn processed successfully'}
            
        except Exception as e:
            return {'success': False, 'message': f'Error processing turn: {str(e)}'}

    def start_combat(self, combat_id: str) -> Dict:
        """Start the combat and roll initiative."""
        combat = self.get_combat(combat_id)
        if not combat:
            return {'success': False, 'message': 'Combat not found'}
            
        logger = self.active_loggers.get(combat_id)
        if not logger:
            logger = CombatLogger(combat_id, self.app.db)
            self.active_loggers[combat_id] = logger
            
        # Roll initiative for all participants
        initiative_order = []
        for participant_id in combat['participants']:
            character = self.app.character_system.get_character(participant_id)
            if not character:
                continue
                
            # Calculate initiative
            dex_mod = (character.get('dexterity', 10) - 10) // 2
            initiative_roll = self.app.dice.roll(20)
            final_initiative = initiative_roll + dex_mod
            
            # Log initiative roll
            logger.log_initiative(
                actor_id=participant_id,
                roll=initiative_roll,
                modifiers={'dexterity': dex_mod},
                final_value=final_initiative
            )
            
            initiative_order.append({
                'id': participant_id,
                'initiative': final_initiative
            })
        
        # Sort by initiative
        initiative_order.sort(key=lambda x: x['initiative'], reverse=True)
        ordered_participants = [p['id'] for p in initiative_order]
        
        # Update combat status
        combat['status'] = 'active'
        combat['initiative_order'] = ordered_participants
        combat['current_turn'] = 0
        self.combat_collection.document(combat_id).set(combat)
        
        # Start first round
        logger.start_round()
        
        return {
            'success': True,
            'initiative_order': initiative_order
        }

    def process_attack(self, combat_id: str, attacker_id: str, 
                      defender_id: str, attack_type: str) -> Dict:
        """Process an attack in combat."""
        combat = self.get_combat(combat_id)
        if not combat:
            return {'success': False, 'message': 'Combat not found'}
            
        logger = self.active_loggers.get(combat_id)
        if not logger:
            logger = CombatLogger(combat_id, self.app.db)
            self.active_loggers[combat_id] = logger
            
        attacker = self.app.character_system.get_character(attacker_id)
        defender = self.app.character_system.get_character(defender_id)
        
        if not attacker or not defender:
            return {'success': False, 'message': 'Invalid attacker or defender'}
            
        # Calculate attack roll
        attack_roll = self.app.dice.roll(20)
        modifiers = self.calculate_attack_modifiers(attacker, attack_type)
        total_attack = attack_roll + sum(modifiers.values())
        
        # Check for critical hit
        is_critical = attack_roll == 20
        
        # Calculate if hit
        defender_ac = defender.get('armor_class', 10)
        is_hit = is_critical or total_attack >= defender_ac
        
        # Log attack
        logger.log_attack(
            attacker_id=attacker_id,
            defender_id=defender_id,
            attack_type=AttackType(attack_type),
            roll=attack_roll,
            modifiers=modifiers,
            success=is_hit,
            critical=is_critical
        )
        
        if not is_hit:
            return {
                'success': True,
                'hit': False,
                'message': 'Attack missed'
            }
            
        # Calculate and apply damage
        damage_result = self.damage_engine.calculate_damage(
            attacker=attacker,
            defender=defender,
            attack_type=AttackType(attack_type),
            is_critical=is_critical
        )
        
        # Log damage
        logger.log_damage(
            attacker_id=attacker_id,
            defender_id=defender_id,
            damage_result=damage_result
        )
        
        # Apply any effects
        for effect in damage_result.effects_applied:
            logger.log_effect(
                source_id=attacker_id,
                target_id=defender_id,
                effect=effect,
                duration=2,  # Default duration, adjust as needed
                is_applied=True
            )
        
        # Update defender's health
        self.app.character_system.update_health(
            defender_id,
            -damage_result.final_damage
        )
        
        # Check for combat end conditions
        if defender.get('health', 0) <= 0:
            self.end_combat(
                combat_id=combat_id,
                winner_id=attacker_id,
                reason=f"{defender.get('name', 'Defender')} was defeated"
            )
        
        return {
            'success': True,
            'hit': True,
            'critical': is_critical,
            'damage': damage_result.final_damage,
            'effects': damage_result.effects_applied
        }

    def calculate_attack_modifiers(self, attacker: Dict, attack_type: str) -> Dict[str, int]:
        """Calculate all applicable attack modifiers."""
        modifiers = {}
        
        if attack_type == AttackType.MELEE.value:
            modifiers['strength'] = (attacker.get('strength', 10) - 10) // 2
        elif attack_type == AttackType.RANGED.value:
            modifiers['dexterity'] = (attacker.get('dexterity', 10) - 10) // 2
            
        # Add proficiency if proficient with weapon
        modifiers['proficiency'] = attacker.get('proficiency_bonus', 2)
        
        # Add any status effect modifiers
        for effect in attacker.get('status_effects', []):
            if effect.get('affects') == 'attack':
                modifiers[f"effect_{effect['name']}"] = effect['modifier']
                
        return modifiers

    def get_combat_log(self, combat_id: str, filters: Optional[Dict] = None) -> List[Dict]:
        """Retrieve filtered combat log entries."""
        logger = self.active_loggers.get(combat_id)
        if not logger:
            logger = CombatLogger(combat_id, self.app.db)
            
        return logger.get_combat_log(filters)

    def get_combat_statistics(self, combat_id: str) -> Dict:
        """Retrieve combat statistics."""
        logger = self.active_loggers.get(combat_id)
        if not logger:
            logger = CombatLogger(combat_id, self.app.db)
            
        return logger.get_statistics()

    async def end_turn(self, combat_id: str) -> Dict:
        """End the current turn and check for combat end conditions."""
        combat = await self.get_combat(combat_id)
        if not combat:
            return {'success': False, 'message': 'Combat not found'}

        # Update turn and round
        combat['current_turn'] = (combat['current_turn'] + 1) % len(combat['initiative_order'])
        if combat['current_turn'] == 0:
            combat['current_round'] += 1

        # Check for combat end conditions
        end_condition = await self.resolution_manager.check_end_conditions(combat_id)
        if end_condition:
            resolution_result = await self.resolution_manager.resolve_combat(combat_id, end_condition)
            await self._handle_combat_resolution(combat_id, resolution_result)
            return {
                'success': True,
                'message': 'Combat ended',
                'end_condition': end_condition.value,
                'resolution': resolution_result
            }

        # Save updated combat state
        await self.state_manager.save_state(combat_id)
        return {'success': True, 'message': 'Turn ended'}

    async def _handle_combat_resolution(self, combat_id: str, resolution_result) -> None:
        """Handle the aftermath of combat resolution."""
        # Log the combat resolution
        logger = self.active_loggers.get(combat_id)
        if logger:
            await logger.log_event(
                LogCategory.SYSTEM,
                LogLevel.IMPORTANT,
                f"Combat ended with condition: {resolution_result.end_condition.value}",
                {
                    'winner': resolution_result.winner,
                    'survivors': resolution_result.survivors,
                    'casualties': resolution_result.casualties,
                    'experience_awarded': resolution_result.experience_awarded
                }
            )

        # Award experience to participants
        for character_id, xp in resolution_result.experience_awarded.items():
            await self.app.character_system.award_experience(character_id, xp)

        # Update character statuses
        for character_id in resolution_result.survivors:
            await self.app.character_system.set_combat_status(character_id, 'active')
        for character_id in resolution_result.casualties:
            await self.app.character_system.set_combat_status(character_id, 'defeated')

        # Clean up combat resources
        await self.resolution_manager._cleanup_combat(combat_id)

    async def force_end_combat(self, combat_id: str, reason: str = None) -> Dict:
        """Force end a combat encounter."""
        combat = await self.get_combat(combat_id)
        if not combat:
            return {'success': False, 'message': 'Combat not found'}

        resolution_result = await self.resolution_manager.resolve_combat(
            combat_id, 
            CombatEndCondition.FORCED,
            {'forced_end_reason': reason}
        )
        
        await self._handle_combat_resolution(combat_id, resolution_result)
        return {
            'success': True,
            'message': 'Combat forcefully ended',
            'resolution': resolution_result
        }

    async def attempt_retreat(self, combat_id: str, character_id: str) -> Dict:
        """Attempt to retreat from combat."""
        combat = await self.get_combat(combat_id)
        if not combat:
            return {'success': False, 'message': 'Combat not found'}

        can_retreat = await self.resolution_manager._check_retreat_conditions(
            combat_id,
            await self.resolution_manager._get_participant_statuses(combat_id)
        )

        if not can_retreat:
            return {'success': False, 'message': 'Retreat conditions not met'}

        # Handle retreat for the character
        await self.app.character_system.set_combat_status(character_id, 'retreated')
        
        # Check if this triggers a combat end condition
        end_condition = await self.resolution_manager.check_end_conditions(combat_id)
        if end_condition:
            resolution_result = await self.resolution_manager.resolve_combat(combat_id, end_condition)
            await self._handle_combat_resolution(combat_id, resolution_result)
            return {
                'success': True,
                'message': 'Retreated and combat ended',
                'resolution': resolution_result
            }

        return {'success': True, 'message': 'Successfully retreated'}

# Global combat system instance
combat_system = None

def init_combat_system(app) -> None:
    """Initialize the combat system."""
    global combat_system
    combat_system = CombatSystem(app) 
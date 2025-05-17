from typing import Dict, List, Optional, Union
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
from app.core.enums import DamageType
from app.combat.damage_engine import AttackType
from app.combat.combat_logger import CombatLogger, LogCategory, LogLevel
from app.combat.state_manager import CombatStateManager
from app.combat.loot_generator import LootGenerator, LootResult

class CombatEndCondition(Enum):
    VICTORY = "victory"  # All enemies defeated
    DEFEAT = "defeat"    # All players defeated
    RETREAT = "retreat"  # Players successfully retreated
    ESCAPE = "escape"    # Enemies successfully escaped
    TIMEOUT = "timeout"  # Combat exceeded maximum rounds
    OBJECTIVE = "objective"  # Special objective completed
    FORCED = "forced"    # GM/System forced end

@dataclass
class CombatResolutionResult:
    combat_id: str
    end_condition: CombatEndCondition
    winner: Optional[str]  # Winning faction/team ID
    rounds_completed: int
    survivors: List[str]  # IDs of surviving participants
    casualties: List[str]  # IDs of defeated participants
    experience_awarded: Dict[str, int]  # participant_id -> XP gained
    loot_generated: Dict[str, LootResult]  # enemy_id -> LootResult
    timestamp: datetime
    special_conditions: Dict  # Additional resolution data

class CombatResolutionManager:
    def __init__(self, app):
        self.app = app
        self.state_manager = CombatStateManager(app)
        self.combat_results = app.db.collection('combat_results')
        self.loot_generator = LootGenerator()
        
    async def check_end_conditions(self, combat_id: str) -> Optional[CombatEndCondition]:
        """Check if any end conditions are met for the combat."""
        combat_state = await self.state_manager.get_state(combat_id)
        if not combat_state:
            return None
            
        # Get all participants and their current status
        participants = await self._get_participant_statuses(combat_id)
        
        # Check for total victory/defeat
        players = [p for p in participants if p['type'] == 'player']
        enemies = [p for p in participants if p['type'] == 'enemy']
        
        if all(p['status'] == 'defeated' for p in enemies):
            return CombatEndCondition.VICTORY
        if all(p['status'] == 'defeated' for p in players):
            return CombatEndCondition.DEFEAT
            
        # Check for retreat conditions
        if await self._check_retreat_conditions(combat_id, participants):
            return CombatEndCondition.RETREAT
            
        # Check for escape conditions
        if await self._check_escape_conditions(combat_id, participants):
            return CombatEndCondition.ESCAPE
            
        # Check for timeout
        if combat_state.current_round > self.app.config.get('max_combat_rounds', 50):
            return CombatEndCondition.TIMEOUT
            
        # Check for special objectives
        if await self._check_special_objectives(combat_id):
            return CombatEndCondition.OBJECTIVE
            
        return None
        
    async def resolve_combat(self, combat_id: str, end_condition: CombatEndCondition) -> CombatResolutionResult:
        """Resolve combat and generate final results."""
        combat_state = await self.state_manager.get_state(combat_id)
        if not combat_state:
            raise ValueError(f"Combat {combat_id} not found")
            
        participants = await self._get_participant_statuses(combat_id)
        
        # Calculate survivors and casualties
        survivors = [p['id'] for p in participants if p['status'] != 'defeated']
        casualties = [p['id'] for p in participants if p['status'] == 'defeated']
        
        # Determine winner based on end condition
        winner = await self._determine_winner(combat_id, end_condition, participants)
        
        # Calculate experience points
        experience_awarded = await self._calculate_experience(combat_id, participants, end_condition)
        
        # Generate loot if players won
        loot_generated = {}
        if end_condition in [CombatEndCondition.VICTORY, CombatEndCondition.OBJECTIVE]:
            loot_generated = await self._generate_combat_loot(combat_id, participants)
        
        # Create resolution result
        result = CombatResolutionResult(
            combat_id=combat_id,
            end_condition=end_condition,
            winner=winner,
            rounds_completed=combat_state.current_round,
            survivors=survivors,
            casualties=casualties,
            experience_awarded=experience_awarded,
            loot_generated=loot_generated,
            timestamp=datetime.utcnow(),
            special_conditions=await self._get_special_conditions(combat_id)
        )
        
        # Save result to database
        await self._save_resolution_result(result)
        
        # Clean up combat state
        await self._cleanup_combat(combat_id)
        
        return result
        
    async def _get_participant_statuses(self, combat_id: str) -> List[Dict]:
        """Get current status of all combat participants."""
        combat = await self.app.combat_system.get_combat(combat_id)
        participants = []
        
        for participant_id in combat['participants']:
            # Try to get as player first
            participant = await self.app.character_system.get_character(participant_id)
            p_type = 'player'
            
            # If not found as player, try as enemy
            if not participant:
                participant = await self.app.npc_system.get_npc(participant_id)
                p_type = 'enemy'
                
            if participant:
                participants.append({
                    'id': participant_id,
                    'type': p_type,
                    'status': 'active' if participant['health'] > 0 else 'defeated',
                    'health': participant['health'],
                    'max_health': participant['max_health'],
                    'position': participant.get('position', None)
                })
                
        return participants
        
    async def _check_retreat_conditions(self, combat_id: str, participants: List[Dict]) -> bool:
        """Check if conditions for player retreat are met."""
        # Get combat state for battlefield info
        combat_state = await self.state_manager.get_state(combat_id)
        if not combat_state:
            return False
            
        # Get active players
        active_players = [p for p in participants if p['type'] == 'player' and p['status'] == 'active']
        
        # Basic retreat conditions:
        # 1. At least one player must be alive
        # 2. All active players must be near a valid exit point
        # 3. No enemies blocking the exit path
        if not active_players:
            return False
            
        # Check if all active players are near exit
        for player in active_players:
            if not await self._is_near_exit(combat_id, player['position']):
                return False
                
            # Check if path is blocked by enemies
            if await self._is_path_blocked(combat_id, player['position']):
                return False
                
        return True
        
    async def _check_escape_conditions(self, combat_id: str, participants: List[Dict]) -> bool:
        """Check if conditions for enemy escape are met."""
        # Similar to retreat but for enemies
        combat_state = await self.state_manager.get_state(combat_id)
        if not combat_state:
            return False
            
        active_enemies = [p for p in participants if p['type'] == 'enemy' and p['status'] == 'active']
        
        # Basic escape conditions:
        # 1. Less than 25% of original enemy force remains
        # 2. Remaining enemies must be near exit points
        # 3. No players blocking the exit path
        original_enemy_count = len([p for p in participants if p['type'] == 'enemy'])
        if len(active_enemies) / original_enemy_count > 0.25:
            return False
            
        for enemy in active_enemies:
            if not await self._is_near_exit(combat_id, enemy['position']):
                return False
                
            if await self._is_path_blocked(combat_id, enemy['position']):
                return False
                
        return True
        
    async def _check_special_objectives(self, combat_id: str) -> bool:
        """Check if any special combat objectives have been completed."""
        combat = await self.app.combat_system.get_combat(combat_id)
        if not combat.get('objectives'):
            return False
            
        # Check each objective's completion criteria
        for objective in combat['objectives']:
            if not await self._is_objective_complete(combat_id, objective):
                return False
                
        return True
        
    async def _determine_winner(self, combat_id: str, end_condition: CombatEndCondition, 
                              participants: List[Dict]) -> Optional[str]:
        """Determine the winning faction based on end condition and state."""
        if end_condition == CombatEndCondition.VICTORY:
            return 'players'
        elif end_condition == CombatEndCondition.DEFEAT:
            return 'enemies'
        elif end_condition == CombatEndCondition.RETREAT:
            return 'enemies'  # Technical victory for enemies if players retreat
        elif end_condition == CombatEndCondition.ESCAPE:
            return 'players'  # Technical victory for players if enemies escape
        elif end_condition == CombatEndCondition.OBJECTIVE:
            # Check objective completion to determine winner
            combat = await self.app.combat_system.get_combat(combat_id)
            return await self._get_objective_winner(combat)
        
        return None  # No clear winner for timeout or forced end
        
    async def _calculate_experience(self, combat_id: str, participants: List[Dict],
                                  end_condition: CombatEndCondition) -> Dict[str, int]:
        """Calculate experience points earned by each participant."""
        xp_awards = {}
        combat = await self.app.combat_system.get_combat(combat_id)
        
        # Get base XP values for defeated enemies
        defeated_enemies = [p for p in participants if p['type'] == 'enemy' and p['status'] == 'defeated']
        total_enemy_xp = sum(await self._get_enemy_xp_value(e['id']) for e in defeated_enemies)
        
        # Get surviving players
        surviving_players = [p for p in participants if p['type'] == 'player' and p['status'] == 'active']
        
        if not surviving_players:
            return xp_awards
            
        # Calculate share per player
        base_share = total_enemy_xp // len(surviving_players)
        
        # Apply modifiers based on end condition
        condition_multiplier = {
            CombatEndCondition.VICTORY: 1.0,
            CombatEndCondition.RETREAT: 0.5,
            CombatEndCondition.OBJECTIVE: 1.2,
            CombatEndCondition.TIMEOUT: 0.75
        }.get(end_condition, 0.0)
        
        # Award XP to each surviving player
        for player in surviving_players:
            # Calculate final XP with modifiers
            final_xp = int(base_share * condition_multiplier)
            
            # Apply any individual modifiers (e.g., from items or effects)
            final_xp = await self._apply_xp_modifiers(player['id'], final_xp)
            
            xp_awards[player['id']] = max(final_xp, 0)  # Ensure no negative XP
            
        return xp_awards
        
    async def _cleanup_combat(self, combat_id: str):
        """Perform cleanup after combat resolution."""
        # Clear combat state
        await self.state_manager.delete_state(combat_id)
        
        # Remove combat-specific effects from participants
        combat = await self.app.combat_system.get_combat(combat_id)
        for participant_id in combat['participants']:
            await self._cleanup_participant(participant_id)
            
        # Clear any temporary battlefield effects
        await self.app.combat_system.clear_battlefield_effects(combat_id)
        
        # Archive combat log
        await self.app.combat_system.archive_combat_log(combat_id)
        
    async def _cleanup_participant(self, participant_id: str):
        """Clean up combat-related effects and states for a participant."""
        # Remove temporary combat effects
        await self.app.effect_system.remove_combat_effects(participant_id)
        
        # Reset combat-specific flags
        await self.app.character_system.reset_combat_flags(participant_id)
        
        # Clear reaction states
        await self.app.combat_system.clear_reaction_state(participant_id)
        
    async def _is_near_exit(self, combat_id: str, position: Dict) -> bool:
        """Check if a position is near a valid exit point."""
        if not position:
            return False
            
        # Get battlefield layout
        battlefield = await self.app.combat_system.get_battlefield(combat_id)
        
        # Get exit points
        exit_points = battlefield.get('exit_points', [])
        
        # Check distance to nearest exit
        for exit_point in exit_points:
            distance = self._calculate_distance(position, exit_point)
            if distance <= battlefield.get('exit_range', 5):
                return True
                
        return False
        
    async def _is_path_blocked(self, combat_id: str, position: Dict) -> bool:
        """Check if path to nearest exit is blocked by enemies."""
        battlefield = await self.app.combat_system.get_battlefield(combat_id)
        
        # Get nearest exit point
        nearest_exit = await self._get_nearest_exit(combat_id, position)
        if not nearest_exit:
            return True  # No valid exit found
            
        # Check for blocking entities along path
        path = await self._calculate_path(position, nearest_exit)
        return await self._is_path_obstructed(combat_id, path)
        
    async def _save_resolution_result(self, result: CombatResolutionResult):
        """Save the combat resolution result to the database."""
        # Convert LootResult objects to dictionaries for database storage
        loot_data = {}
        for enemy_id, loot_result in result.loot_generated.items():
            loot_data[enemy_id] = {
                'items': [(item_id, qty) for item_id, qty in loot_result.items],
                'currency': {
                    'copper': loot_result.currency.copper,
                    'silver': loot_result.currency.silver,
                    'gold': loot_result.currency.gold,
                    'platinum': loot_result.currency.platinum
                },
                'special_items': loot_result.special_items
            }
        
        # Create the document data
        doc_data = {
            'combat_id': result.combat_id,
            'end_condition': result.end_condition.value,
            'winner': result.winner,
            'rounds_completed': result.rounds_completed,
            'survivors': result.survivors,
            'casualties': result.casualties,
            'experience_awarded': result.experience_awarded,
            'loot_generated': loot_data,
            'timestamp': result.timestamp,
            'special_conditions': result.special_conditions
        }
        
        # Save to database
        await self.combat_results.document(result.combat_id).set(doc_data)
        
    def _calculate_distance(self, pos1: Dict, pos2: Dict) -> float:
        """Calculate distance between two positions."""
        return ((pos1['x'] - pos2['x']) ** 2 + (pos1['y'] - pos2['y']) ** 2) ** 0.5 

    async def _generate_combat_loot(self, combat_id: str, participants: List[Dict]) -> Dict[str, LootResult]:
        """Generate loot for all defeated enemies in the combat."""
        loot_results = {}
        
        # Get combat details for party level calculation
        combat = await self.app.combat_system.get_combat(combat_id)
        party_level = await self._calculate_party_level(combat_id)
        
        # Process each defeated enemy
        defeated_enemies = [p for p in participants if p['type'] == 'enemy' and p['status'] == 'defeated']
        for enemy in defeated_enemies:
            # Get enemy details
            enemy_data = await self.app.npc_system.get_npc(enemy['id'])
            if not enemy_data:
                continue
                
            # Register enemy type if not already registered
            enemy_type = enemy_data.get('type', 'generic')
            if enemy['id'] not in self.loot_generator.enemy_types:
                self.loot_generator.register_enemy_type(enemy['id'], enemy_type)
                
            # Register loot table if not already registered
            if enemy_type not in self.loot_generator.loot_tables:
                loot_table = await self._get_enemy_loot_table(enemy_type)
                if loot_table:
                    self.loot_generator.register_loot_table(enemy_type, loot_table)
            
            # Generate loot for this enemy
            is_boss = enemy_data.get('is_boss', False)
            enemy_level = enemy_data.get('level', 1)
            
            try:
                loot = self.loot_generator.generate_loot(
                    enemy_id=enemy['id'],
                    enemy_level=enemy_level,
                    party_level=party_level,
                    is_boss=is_boss
                )
                loot_results[enemy['id']] = loot
            except ValueError as e:
                # Log error but continue with other enemies
                self.app.logger.error(f"Failed to generate loot for enemy {enemy['id']}: {str(e)}")
                continue
        
        return loot_results

    async def _calculate_party_level(self, combat_id: str) -> int:
        """Calculate the average level of the party."""
        combat = await self.app.combat_system.get_combat(combat_id)
        total_level = 0
        player_count = 0
        
        for participant_id in combat['participants']:
            character = await self.app.character_system.get_character(participant_id)
            if character:  # If it's a player character
                total_level += character.get('level', 1)
                player_count += 1
        
        return max(1, total_level // max(1, player_count))  # Ensure we don't divide by zero

    async def _get_enemy_loot_table(self, enemy_type: str) -> List[LootTableEntry]:
        """Fetch the loot table for an enemy type from the database."""
        try:
            loot_table_data = await self.app.db.collection('loot_tables').document(enemy_type).get()
            if not loot_table_data.exists:
                return []
            
            # Convert database data to LootTableEntry objects
            loot_table = []
            for entry in loot_table_data.to_dict().get('entries', []):
                loot_table.append(LootTableEntry(
                    item_id=entry['item_id'],
                    rarity=ItemRarity(entry['rarity']),
                    drop_chance=entry['drop_chance'],
                    level_requirement=entry['level_requirement'],
                    quantity_range=(entry['min_quantity'], entry['max_quantity']),
                    boss_only=entry.get('boss_only', False)
                ))
            
            return loot_table
        except Exception as e:
            self.app.logger.error(f"Failed to fetch loot table for enemy type {enemy_type}: {str(e)}")
            return [] 
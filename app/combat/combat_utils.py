"""
This module orchestrates AI combat behavior, initiative mechanics, and combat narration.
It integrates GPT for action decisions and prose, handles loyalty-driven abandonment, and
bridges live tactical logic with persistent game state.
"""

import os
import random
import json
from datetime import datetime
from typing import Dict, Tuple, Optional, List, Any
from sqlalchemy.orm.exc import NoResultFound
from functools import lru_cache
from dataclasses import dataclass
from collections import defaultdict

from app.combat.combat_handler_class import CombatAction
from app.combat.combat_class import Combatant
from app.combat.status_effects_utils import tick_status_effects, get_status_effect_modifiers
from app.characters.party_utils import abandon_party
from app.combat.combat_behavior_utils import should_abandon
from app.combat.combat_state_class import CombatState
from app.combat.combat_ram import ACTIVE_BATTLES
from app.combat.tactical_advantages import apply_terrain_advantages
from app.core.database import db
from app.core.models.character import Character
from app.core.models.user import User
from app.core.models.party import Party
from app.core.models.region import Region
from app.core.models.quest import Quest
from app.core.models.spell import Spell, SpellEffect
from app.core.models.inventory import InventoryItem
from app.core.models.combat import CombatStats, Combat, CombatParticipant, CombatEngine
from app.core.models.save import SaveGame
from app.models.weapon import Weapon
from app.utils.gpt_class import GPTClient
from app.core.services.ai import LLMService
from app.core.utils.error_utils import ValidationError, DatabaseError, NotFoundError
from app.core.models.status import StatusEffect, EffectType
from app.models import Quest
from visual_client.game.combat import (
    calculate_damage,
    calculate_attack_bonus,
    calculate_attack_roll,
    apply_damage,
    resolve_turn
)
from visual_client.game.character import should_abandon
from visual_client.game.narrative import narrate_combat_action

# Initialize GPT client and LLM service
gpt_client = GPTClient()
llm_service = LLMService()

def call(system_prompt: str, user_prompt: str, temperature: float = 0.7, max_tokens: int = 150) -> str:
    """Wrapper around LLM call to generate responses."""
    return llm_service.generate_response(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        temperature=temperature,
        max_tokens=max_tokens
    )

@dataclass
class CombatState:
    """Immutable combat state for efficient updates."""
    turn_order: List[str]
    current_turn: int
    combat_state: str
    combat_log: List[str]

class CombatEngine:
    def __init__(self, combatants):
        self.combatants = combatants
        self._state = CombatState(
            turn_order=self._init_turn_order(),
            current_turn=0,
            combat_state="active",
            combat_log=[]
        )
        self._damage_cache = {}
        self._ai_decision_cache = {}
        
    @lru_cache(maxsize=128)
    def _init_turn_order(self) -> List[str]:
        """Initialize turn order based on initiative."""
        return sorted(
            self.combatants,
            key=lambda c: c.get('initiative', 0),
            reverse=True
        )
    
    @lru_cache(maxsize=128)
    def calculate_damage(self, attacker: Dict[str, Any], weapon: Dict[str, Any], critical: bool = False) -> int:
        """Calculate damage for an attack with caching."""
        cache_key = (attacker.get('id'), weapon.get('id'), critical)
        if cache_key in self._damage_cache:
            return self._damage_cache[cache_key]
            
        base_damage = weapon.get("damage_dice", "1d6").roll()
        if critical:
            base_damage *= 2

        ability_mod = (attacker.get("strength", 10) - 10) // 2
        damage = base_damage + ability_mod
        
        self._damage_cache[cache_key] = damage
        return damage
    
    def _get_ai_decision(self, combatant: Dict[str, Any]) -> Dict[str, Any]:
        """Get AI decision with caching."""
        cache_key = combatant.get('id')
        if cache_key in self._ai_decision_cache:
            return self._ai_decision_cache[cache_key]
            
        # Simple AI decision making with caching
        if combatant.get('current_mp', 0) > 0 and random.random() < 0.3:
            decision = {
                "name": "magic_attack",
                "action_type": "action",
                "base_damage": 15,
                "mp_cost": 5,
                "status_condition": "burning",
                "effect_duration": 2
            }
        else:
            decision = {
                "name": "basic_attack",
                "action_type": "action",
                "base_damage": 10
            }
            
        self._ai_decision_cache[cache_key] = decision
        return decision
    
    def run_combat(self, max_turns=20) -> Dict[str, Any]:
        """Run a complete combat sequence with optimized state management."""
        turn_count = 0
        events = []
        
        while self._state.combat_state == "active" and turn_count < max_turns:
            current_combatant = self._state.turn_order[self._state.current_turn]
            
            if current_combatant.get("is_npc", False):
                action_data = self._get_ai_decision(current_combatant)
                target_id = self._select_ai_target(current_combatant)
                result = self.resolve_turn(action_data, target_id)
                events.append(result)
                
                if result.get("status") == "victory":
                    break
            else:
                return {
                    "status": "awaiting_player_action",
                    "current_combatant": current_combatant.get('character_id'),
                    "events": events
                }
            
            turn_count += 1
            self._state = CombatState(
                turn_order=self._state.turn_order,
                current_turn=(self._state.current_turn + 1) % len(self._state.turn_order),
                combat_state=self._state.combat_state,
                combat_log=self._state.combat_log
            )
            
        return {
            "status": self._state.combat_state,
            "turns": turn_count,
            "log": self._state.combat_log,
            "events": events
        }
    
    def _select_ai_target(self, combatant: Dict[str, Any]) -> str:
        """Select target for AI combatant with efficient targeting logic."""
        # Use a priority queue for target selection
        targets = []
        for target in self.combatants:
            if target.get('id') != combatant.get('id'):
                priority = (
                    target.get('current_hp', 0) / target.get('max_hp', 100),
                    -target.get('threat_level', 0)
                )
                targets.append((priority, target.get('id')))
        
        # Sort by priority and return highest priority target
        return sorted(targets, key=lambda x: x[0])[0][1] if targets else None

def initiate_combat(player_party, enemy_party, battle_name="Combat", use_ram=True):
    """Initialize a new combat encounter."""
    try:
        # Create combat record
        combat = Combat(
            name=battle_name,
            status='active',
            round_number=1,
            current_turn=0,
            initiative_order=[],
            log=[]
        )
        db.session.add(combat)
        db.session.commit()

        # Add participants
        for character in player_party:
            participant = CombatParticipant(
                combat_id=combat.id,
                character_id=character.id,
                initiative=roll_initiative(character.dexterity),
                current_health=character.current_health,
                current_mana=character.current_mana
            )
            db.session.add(participant)

        for enemy in enemy_party:
            participant = CombatParticipant(
                combat_id=combat.id,
                npc_id=enemy.id,
                initiative=roll_initiative(enemy.dexterity),
                current_health=enemy.current_health,
                current_mana=enemy.current_mana
            )
            db.session.add(participant)

        db.session.commit()

        # Update initiative order
        combat.initiative_order = sorted(
            combat.participants,
            key=lambda p: p.initiative,
            reverse=True
        )
        db.session.commit()

        return combat.id

    except Exception as e:
        db.session.rollback()
        raise DatabaseError(f"Failed to initiate combat: {str(e)}")

def log_combat_start(region_name, poi_id, participant_ids):
    """Log the start of a combat encounter."""
    try:
        combat = Combat(
            region_name=region_name,
            poi_id=poi_id,
            status='active',
            round_number=1,
            current_turn=0,
            initiative_order=[],
            log=[]
        )
        db.session.add(combat)
        db.session.commit()

        # Add participants
        for participant_id in participant_ids:
            participant = CombatParticipant(
                combat_id=combat.id,
                character_id=participant_id,
                initiative=0,
                current_health=100,
                current_mana=100
            )
            db.session.add(participant)

        db.session.commit()
        return combat.id

    except Exception as e:
        db.session.rollback()
        raise DatabaseError(f"Failed to log combat start: {str(e)}")

def roll_d20():
    """Roll a d20 die."""
    return random.randint(1, 20)

def roll_initiative(dexterity):
    """Roll initiative for a character."""
    return roll_d20() + (dexterity - 10) // 2

def resolve_saving_throw(stat_mod, dc):
    """Resolve a saving throw."""
    roll = roll_d20()
    total = roll + stat_mod
    success = total >= dc
    return {
        "roll": roll,
        "total": total,
        "success": success,
        "critical": roll == 20
    }

def apply_combat_status_effects(target_id, status_dict, source=None):
    """Apply status effects to a combat participant."""
    try:
        participant = db.session.query(CombatParticipant).get(target_id)
        if not participant:
            raise NotFoundError(f"Combat participant {target_id} not found")

        # Apply effects
        for effect_name, duration in status_dict.items():
            effect = StatusEffect(
                participant_id=participant.id,
                effect_type=EffectType[effect_name.upper()],
                duration=duration,
                source_id=source.id if source else None
            )
            db.session.add(effect)

        db.session.commit()
        return True

    except Exception as e:
        db.session.rollback()
        raise DatabaseError(f"Failed to apply status effects: {str(e)}")

def roll_fumble_effect():
    """Roll for a fumble effect."""
    effects = [
        "drop_weapon",
        "fall_prone",
        "hit_ally",
        "self_damage",
        "stunned"
    ]
    return random.choice(effects)

def calculate_attack_roll(attacker: Dict[str, Any], target: Dict[str, Any], advantage: bool = False, disadvantage: bool = False) -> Tuple[int, bool]:
    """Calculate attack roll with terrain advantages."""
    # Get base roll
    if advantage and not disadvantage:
        roll = max(random.randint(1, 20), random.randint(1, 20))
    elif disadvantage and not advantage:
        roll = min(random.randint(1, 20), random.randint(1, 20))
    else:
        roll = random.randint(1, 20)

    # Critical on natural 20
    is_critical = roll == 20

    # Apply terrain advantages if grid is available
    if 'grid' in attacker and 'position' in attacker and 'position' in target:
        modified_roll, advantages = apply_terrain_advantages(
            attacker['grid'],
            attacker,
            target,
            roll
        )
        roll = modified_roll

    # Add modifiers
    attack_bonus = calculate_attack_bonus(attacker)
    total = roll + attack_bonus

    return total, is_critical

def resolve_combat_action(combat_id: int, action: Dict) -> Dict:
    """Resolve a combat action with terrain advantages."""
    try:
        combat = Combat.query.get(combat_id)
        if not combat:
            raise NotFoundError("Combat not found")

        attacker = CombatParticipant.query.get(action['attacker_id'])
        target = CombatParticipant.query.get(action['target_id'])

        if not attacker or not target:
            raise NotFoundError("Participant not found")

        # Get tactical grid if available
        grid = combat.tactical_grid if hasattr(combat, 'tactical_grid') else None
        
        # Add grid and position to context
        attacker_context = {
            **attacker.to_dict(),
            'grid': grid,
            'position': (attacker.position_q, attacker.position_r)
        }
        target_context = {
            **target.to_dict(),
            'grid': grid,
            'position': (target.position_q, target.position_r)
        }

        # Calculate attack with terrain advantages
        attack_roll, is_critical = calculate_attack_roll(
            attacker_context,
            target_context,
            advantage=action.get('advantage', False),
            disadvantage=action.get('disadvantage', False)
        )

        # Determine hit
        ac = calculate_armor_class(
            target.dexterity_modifier,
            target.equipped_armor,
            target.equipped_shield
        )

        hit = attack_roll >= ac
        damage = 0
        if hit:
            # Calculate damage
            weapon = attacker.equipped_weapon or {'damage': '1d6'}
            damage = calculate_damage(attacker_context, weapon, is_critical)
            
            # Apply damage
            target.current_hp -= damage
            db.session.commit()

        # Generate result
        result = {
            'success': True,
            'hit': hit,
            'damage': damage,
            'attack_roll': attack_roll,
            'critical': is_critical,
            'target_hp': target.current_hp,
            'effects': []
        }

        # Add terrain advantage details if available
        if grid:
            result['terrain_advantages'] = calculate_terrain_advantage(
                grid,
                (attacker.position_q, attacker.position_r),
                (target.position_q, target.position_r)
            )

        return result

    except Exception as e:
        db.session.rollback()
        raise DatabaseError(f"Error resolving combat action: {str(e)}")

def apply_combat_effects(participant: CombatParticipant, effects: List[Dict]) -> None:
    """Apply combat effects to a participant."""
    for effect in effects:
        if effect['type'] == 'damage':
            participant.take_damage(effect['amount'])
        elif effect['type'] == 'healing':
            participant.heal(effect['amount'])
        elif effect['type'] == 'status':
            participant.add_status_effect(effect['name'], effect['duration'])

def calculate_damage(
    attacker: CombatParticipant,
    target: CombatParticipant,
    action_type: str,
    terrain_modifiers: Optional[Dict[str, float]] = None
) -> int:
    """
    Calculate damage for an attack, including terrain advantages.
    
    Args:
        attacker: The attacking participant
        target: The target participant
        action_type: Type of attack being performed
        terrain_modifiers: Dict of terrain-based modifiers
        
    Returns:
        Final damage amount
    """
    # Get base stats
    base_damage = 10  # This should come from weapon/ability
    
    # Apply attacker's offensive modifiers
    attack_power = base_damage
    if attacker.character:
        attack_power *= (1 + attacker.character.strength / 100)
    elif attacker.npc:
        attack_power *= (1 + attacker.npc.power / 100)
        
    # Apply target's defensive modifiers
    defense = 0
    if target.character:
        defense = target.character.defense
    elif target.npc:
        defense = target.npc.defense
        
    # Apply terrain modifiers
    if terrain_modifiers:
        attack_power *= (1 + terrain_modifiers.get('attack_bonus', 0))
        defense *= (1 + terrain_modifiers.get('defense_bonus', 0))
        
    # Apply status effects
    status_mods = get_status_effect_modifiers(attacker.status_effects)
    attack_power *= (1 + status_mods.get('damage_multiplier', 0))
    
    target_status_mods = get_status_effect_modifiers(target.status_effects)
    defense *= (1 + target_status_mods.get('defense_multiplier', 0))
    
    # Calculate final damage
    final_damage = max(1, int(attack_power - defense))
    
    # Apply critical hits
    if is_critical_hit(attacker, target, terrain_modifiers):
        final_damage *= 2
        
    return final_damage

def is_critical_hit(
    attacker: CombatParticipant,
    target: CombatParticipant,
    terrain_modifiers: Optional[Dict[str, float]] = None
) -> bool:
    """
    Determine if an attack is a critical hit.
    
    Args:
        attacker: The attacking participant
        target: The target participant
        terrain_modifiers: Dict of terrain-based modifiers
        
    Returns:
        Boolean indicating if the attack is a critical hit
    """
    import random
    
    # Base crit chance
    crit_chance = 0.05  # 5% base chance
    
    # Modify based on attacker stats
    if attacker.character:
        crit_chance += attacker.character.dexterity / 1000  # Each point of dex adds 0.1%
    elif attacker.npc:
        crit_chance += attacker.npc.critical_chance
        
    # Apply terrain advantages
    if terrain_modifiers:
        crit_chance += terrain_modifiers.get('critical_bonus', 0)
        
    # Cap maximum chance
    crit_chance = min(0.5, max(0.01, crit_chance))  # Between 1% and 50%
    
    return random.random() < crit_chance

def apply_status_effects(
    participant: CombatParticipant,
    effects: Dict[str, Any]
) -> None:
    """
    Apply status effects to a participant.
    
    Args:
        participant: The combat participant
        effects: Dictionary of effects to apply
    """
    if not participant.status_effects:
        participant.status_effects = []
        
    for effect_type, effect_data in effects.items():
        participant.status_effects.append({
            'type': effect_type,
            'duration': effect_data.get('duration', 1),
            'magnitude': effect_data.get('magnitude', 0)
        })

def apply_damage(target: Character, damage: int, damage_type: str) -> Dict[str, Any]:
    """Apply damage to a character."""
    try:
        # Calculate damage reduction
        damage_reduction = 0
        if target.armor:
            damage_reduction += target.armor.damage_reduction.get(damage_type, 0)
        if target.shield:
            damage_reduction += target.shield.damage_reduction.get(damage_type, 0)

        # Apply damage
        actual_damage = max(0, damage - damage_reduction)
        target.current_health = max(0, target.current_health - actual_damage)

        # Check for death
        is_dead = target.current_health <= 0
        if is_dead:
            target.is_dead = True

        db.session.commit()

        return {
            "damage_dealt": actual_damage,
            "damage_type": damage_type,
            "current_hp": target.current_health,
            "is_dead": is_dead
        }

    except Exception as e:
        db.session.rollback()
        raise DatabaseError(f"Failed to apply damage: {str(e)}")

def make_death_saving_throw(character: Character) -> Dict[str, Any]:
    """Make a death saving throw for a character."""
    try:
        roll = roll_d20()
        success = roll >= 10
        critical = roll == 20
        failure = roll == 1

        if success:
            character.death_save_successes += 1
        else:
            character.death_save_failures += 1

        if critical:
            character.current_health = 1
            character.death_save_successes = 0
            character.death_save_failures = 0
        elif failure:
            character.death_save_failures += 1

        is_stable = character.death_save_successes >= 3
        is_dead = character.death_save_failures >= 3

        if is_stable:
            character.current_health = 1
            character.death_save_successes = 0
            character.death_save_failures = 0
        elif is_dead:
            character.is_dead = True

        db.session.commit()

        return {
            "roll": roll,
            "success": success,
            "critical": critical,
            "failure": failure,
            "successes": character.death_save_successes,
            "failures": character.death_save_failures,
            "is_stable": is_stable,
            "is_dead": is_dead,
            "current_hp": character.current_health
        }

    except Exception as e:
        db.session.rollback()
        raise DatabaseError(f"Failed to make death saving throw: {str(e)}")

def calculate_armor_class(
    dexterity_modifier: int,
    armor: Optional[Dict[str, Any]] = None,
    shield: Optional[Dict[str, Any]] = None
) -> int:
    """Calculate armor class for a character."""
    base_ac = 10 + dexterity_modifier
    if armor:
        base_ac = armor.get("base_ac", base_ac)
    if shield:
        base_ac += shield.get("ac_bonus", 0)
    return base_ac

def determine_hit(
    attacker: Dict[str, Any],
    target: Dict[str, Any],
    attack_roll: int,
    modifiers: Optional[Dict[str, int]] = None
) -> Dict[str, Any]:
    """Determine if an attack hits."""
    if not modifiers:
        modifiers = {}

    # Calculate attack bonus
    attack_bonus = modifiers.get("attack_bonus", 0)
    total_roll = attack_roll + attack_bonus

    # Calculate target AC
    target_ac = calculate_armor_class(
        target.get("dexterity_modifier", 0),
        target.get("armor"),
        target.get("shield")
    )

    # Determine hit
    hit = total_roll >= target_ac
    critical = attack_roll == 20
    miss = attack_roll == 1

    return {
        "hit": hit,
        "critical": critical,
        "miss": miss,
        "total_roll": total_roll,
        "target_ac": target_ac
    }

def calculate_initiative(dexterity: int, bonus: int = 0) -> int:
    """Calculate initiative for a character."""
    dexterity_mod = (dexterity - 10) // 2
    return roll_d20() + dexterity_mod + bonus

def determine_combat_order(participants: List[Dict[str, Any]]) -> List[str]:
    """Determine combat order for participants."""
    # Roll initiative for each participant
    initiatives = []
    for participant in participants:
        initiative = calculate_initiative(
            participant.get("dexterity", 10),
            participant.get("initiative_bonus", 0)
        )
        initiatives.append((participant["id"], initiative))

    # Sort by initiative (highest first)
    initiatives.sort(key=lambda x: x[1], reverse=True)
    return [p[0] for p in initiatives]

def calculate_damage(attacker: Dict[str, Any], weapon: Dict[str, Any], critical: bool = False) -> int:
    """Calculate damage for an attack."""
    base_damage = weapon.get("damage_dice", "1d6").roll()
    if critical:
        base_damage *= 2

    ability_mod = (attacker.get("strength", 10) - 10) // 2
    return base_damage + ability_mod

def apply_status_effect(target: Dict[str, Any], effect: str, duration: int) -> Dict[str, Any]:
    """Apply a status effect to a target."""
    try:
        participant = db.session.query(CombatParticipant).get(target["id"])
        if not participant:
            raise NotFoundError(f"Combat participant {target['id']} not found")

        status = StatusEffect(
            participant_id=participant.id,
            effect_type=EffectType[effect.upper()],
            duration=duration
        )
        db.session.add(status)
        db.session.commit()

        return {
            "success": True,
            "effect": effect,
            "duration": duration
        }

    except Exception as e:
        db.session.rollback()
        raise DatabaseError(f"Failed to apply status effect: {str(e)}")

def check_death_save(character: Dict[str, Any]) -> Tuple[bool, bool, Dict[str, Any]]:
    """Check death saving throws for a character."""
    try:
        char = db.session.query(Character).get(character["id"])
        if not char:
            raise NotFoundError(f"Character {character['id']} not found")

        result = make_death_saving_throw(char)
        return (
            result["is_stable"],
            result["is_dead"],
            result
        )

    except Exception as e:
        raise DatabaseError(f"Failed to check death save: {str(e)}")

def process_combat_round(combatants: List[Dict[str, Any]], actions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Process a round of combat."""
    try:
        combat = db.session.query(Combat).get(actions[0]["combat_id"])
        if not combat:
            raise NotFoundError(f"Combat {actions[0]['combat_id']} not found")

        round_results = {
            "round_number": combat.round_number,
            "actions": [],
            "status_effects": [],
            "deaths": []
        }

        # Process each action
        for action in actions:
            actor = next(c for c in combatants if c["id"] == action["actor_id"])
            target = next(c for c in combatants if c["id"] == action["target_id"])

            # Resolve action
            result = resolve_combat_action(combat.id, action)
            round_results["actions"].append(result)

            # Check for deaths
            if result.get("is_dead"):
                round_results["deaths"].append(target["id"])

        # Update combat round
        combat.round_number += 1
        db.session.commit()

        return round_results

    except Exception as e:
        db.session.rollback()
        raise DatabaseError(f"Failed to process combat round: {str(e)}")

def check_combat_end(combatants: list) -> bool:
    """Check if combat has ended."""
    # Check if all enemies are dead
    enemies_dead = all(
        c.get("is_npc", False) and c.get("current_hp", 0) <= 0
        for c in combatants
    )

    # Check if all players are dead
    players_dead = all(
        not c.get("is_npc", False) and c.get("current_hp", 0) <= 0
        for c in combatants
    )

    return enemies_dead or players_dead

def check_combat_conditions(combat_state: CombatState) -> Dict:
    """Check combat conditions and return status."""
    active_participants = [p for p in combat_state.participants if p.current_health > 0]
    return {
        'is_active': len(active_participants) > 1,
        'round_number': combat_state.round_number,
        'current_turn': combat_state.current_turn,
        'active_participants': len(active_participants)
    }
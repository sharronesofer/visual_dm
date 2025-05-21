"""
Core combat utility functions for the Visual DM combat system.

This module provides essential combat mechanics and utilities for the backend combat system.
It includes dice mechanics, combat state management, and utility functions.
"""

import random
import json
from datetime import datetime
from backend.systems.combat.combat_handler_class import CombatAction
from backend.systems.combat.combat_class import Combatant
from backend.systems.combat.status_effects_utils import tick_status_effects
from backend.systems.combat.combat_state_class import CombatState
from backend.systems.combat.combat_ram import ACTIVE_BATTLES

# === Core Dice Mechanics ===

def roll_d20():
    """Roll a standard d20 die."""
    return random.randint(1, 20)


def roll_initiative(dexterity):
    """Calculate initiative based on dexterity modifier."""
    return random.randint(1, 20) + ((dexterity - 10) // 2)


def resolve_saving_throw(stat_mod, dc):
    """Perform a saving throw against a DC with a stat modifier."""
    roll = random.randint(1, 20) + stat_mod
    return {"roll": roll, "modifier": stat_mod, "dc": dc, "success": roll >= dc}


# === Combat Initializers & Core Utilities ===

def initiate_combat(player_party, enemy_party, battle_name="Combat", use_ram=True):
    """
    Initialize a new combat state with the given parties.
    
    Args:
        player_party: List of player character data
        enemy_party: List of enemy character data
        battle_name: Name for this combat encounter
        use_ram: If True, store in RAM; if False, use Firebase
        
    Returns:
        dict: Contains battle_id and combat_state
    """
    combat_state = CombatState(player_party, enemy_party, name=battle_name)
    if use_ram:
        ACTIVE_BATTLES[combat_state.battle_id] = combat_state
    else:
        from backend.systems.combat.combat_state_firebase_utils import start_firebase_combat
        start_firebase_combat(battle_name, player_party, enemy_party)

    return {
        "battle_id": combat_state.battle_id,
        "combat_state": combat_state
    }


def resolve_combat_action(attacker, action_data, battlefield_context):
    """
    Resolve a combat action between an attacker and target.
    
    Args:
        attacker: The attacking character data
        action_data: Action information (target, ability, etc.)
        battlefield_context: Additional context for the battlefield
        
    Returns:
        dict: Result of the combat action
    """
    target_id = action_data.get("target")
    ability = action_data.get("ability", "basic_attack")
    target = next((e for e in battlefield_context.get("enemies", []) if e["id"] == target_id), None)
    if not target:
        return {"hit": False, "error": f"Target {target_id} not found"}

    attributes = attacker.get("attributes", {})
    attributes_used = "STR" if attributes.get("STR", 10) >= attributes.get("DEX", 10) else "DEX"
    attributes_mod = (attributes.get(attributes_used, 10) - 10) // 2
    roll = random.randint(1, 20)
    attack_total = roll + attributes_mod
    ac = target.get("AC", 10)
    dr = target.get("DR", 0)

    result = {
        "attacker": attacker.get("name"),
        "target": target.get("name"),
        "attacker_id": attacker.get("id"),
        "target_id": target.get("id"),
        "ability": ability,
        "roll": roll,
        "attack_total": attack_total,
        "target_ac": ac,
        "hit": False,
        "crit": False,
        "fumble": False,
        "status_effects": {},
        "raw_damage": 0,
        "final_damage": 0,
        "damage_type": "slashing" if "cleave" in ability.lower() else "bludgeoning"
    }

    if roll == 1:
        # Critical failure
        result.update({
            "fumble": True,
            "outcome": f"{attacker.get('name')} fumbled the attack."
        })
        return result

    if roll == 20 or attack_total >= ac:
        result.update({"hit": True})
        base_damage = random.randint(1, 8) * (2 if roll == 20 else 1)
    else:
        result["outcome"] = "Miss"
        return result

    final_damage = max(0, base_damage + attributes_mod - dr)
    result.update({
        "crit": roll == 20,
        "raw_damage": base_damage + attributes_mod,
        "final_damage": final_damage,
        "outcome": f"Hit for {final_damage} damage."
    })
    
    return result


def get_active_combat(combat_id):
    """Retrieve an active combat state by ID."""
    return ACTIVE_BATTLES.get(combat_id)


def end_combat(combat_id):
    """End and clean up an active combat."""
    if combat_id in ACTIVE_BATTLES:
        del ACTIVE_BATTLES[combat_id]
        return True
    return False
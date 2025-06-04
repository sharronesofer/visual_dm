"""Combat utility functions for the combat system."""

from typing import List, Dict, Any, Optional
from uuid import uuid4
import random
import logging

from backend.infrastructure.config_loaders.combat_config_loader import combat_config

def initiate_combat(player_party: List[Dict[str, Any]], enemies: List[Dict[str, Any]], 
                   battle_name: str = "Combat Encounter") -> Dict[str, Any]:
    """
    Initiate a combat encounter between a player party and enemies.
    
    Args:
        player_party: List of player character data
        enemies: List of enemy data
        battle_name: Name for the combat encounter
        
    Returns:
        Dict containing combat initialization data
        
    Raises:
        ValueError: If party or enemies list is empty
        TypeError: If invalid data types are provided
    """
    # Input validation
    if not player_party:
        raise ValueError("Player party cannot be empty")
    if not enemies:
        raise ValueError("Enemies list cannot be empty")
    if not isinstance(player_party, list) or not isinstance(enemies, list):
        raise TypeError("Player party and enemies must be lists")
    
    try:
        # Generate a unique battle ID
        battle_id = f"battle_{uuid4().hex[:8]}"
        
        # Initialize combat state
        combat_state = {
            "battle_id": battle_id,
            "battle_name": battle_name,
            "round": 1,
            "turn": 0,
            "status": "active",
            "party": player_party,
            "enemies": enemies,
            "initiative_order": [],
            "combat_log": []
        }
        
        # Calculate initiative for all participants
        all_participants = []
        
        # Add player party to initiative
        for i, player in enumerate(player_party):
            if not isinstance(player, dict):
                raise TypeError(f"Player {i} must be a dictionary")
                
            initiative = _calculate_initiative(player)
            participant = {
                "id": player.get("id", f"player_{i}"),
                "name": player.get("name", f"Player {i+1}"),
                "initiative": initiative,
                "team": "player",
                "hp": combat_config.get_hp(player),
                "max_hp": combat_config.get_max_hp(player),
                "ac": combat_config.get_ac(player)
            }
            all_participants.append(participant)
        
        # Add enemies to initiative
        for i, enemy in enumerate(enemies):
            if not isinstance(enemy, dict):
                raise TypeError(f"Enemy {i} must be a dictionary")
                
            initiative = _calculate_initiative(enemy)
            participant = {
                "id": enemy.get("id", f"enemy_{i}"),
                "name": enemy.get("name", f"Enemy {i+1}"),
                "initiative": initiative,
                "team": "hostile",
                "hp": combat_config.get_hp(enemy),
                "max_hp": combat_config.get_max_hp(enemy),
                "ac": combat_config.get_ac(enemy)
            }
            all_participants.append(participant)
        
        # Sort by initiative (highest first)
        all_participants.sort(key=lambda x: x["initiative"], reverse=True)
        combat_state["initiative_order"] = all_participants
        
        # Add initial log entry
        if combat_config.get("logging.enable_combat_logging", True):
            combat_state["combat_log"].append({
                "round": 1,
                "message": f"Combat '{battle_name}' has begun!",
                "participants": len(all_participants)
            })
        
        return {
            "success": True,
            "battle_id": battle_id,
            "combat_state": combat_state,
            "message": f"Combat initiated: {battle_name}"
        }
        
    except (ValueError, TypeError) as e:
        # Re-raise validation errors
        raise e
    except Exception as e:
        # Wrap unexpected errors
        raise RuntimeError(f"Failed to initiate combat: {str(e)}") from e

def _calculate_initiative(character: Dict[str, Any]) -> int:
    """
    Calculate initiative for a character.
    
    Args:
        character: Character data dictionary
        
    Returns:
        Initiative value
    """
    dex_modifier = character.get("dex_modifier", combat_config.get_default_stat("dex_modifier"))
    initiative_die_size = combat_config.get("dice_systems.initiative_die_size", 20)
    initiative_die_count = combat_config.get("dice_systems.initiative_die_count", 1)
    
    # Roll initiative dice
    initiative_roll = sum(random.randint(1, initiative_die_size) for _ in range(initiative_die_count))
    return initiative_roll + dex_modifier

def calculate_damage(attacker: Dict[str, Any], target: Dict[str, Any], 
                    attack_roll: int, damage_dice: str = None) -> Dict[str, Any]:
    """
    Calculate damage from an attack.
    
    Args:
        attacker: Attacking character data
        target: Target character data
        attack_roll: The attack roll result
        damage_dice: Damage dice string (e.g., "1d6", "2d8+3")
        
    Returns:
        Dict containing damage calculation results
        
    Raises:
        ValueError: If invalid parameters are provided
        TypeError: If invalid data types are provided
    """
    # Input validation
    if not isinstance(attacker, dict) or not isinstance(target, dict):
        raise TypeError("Attacker and target must be dictionaries")
    if not isinstance(attack_roll, int):
        raise TypeError("Attack roll must be an integer")
    
    if damage_dice is None:
        damage_dice = combat_config.get_dice_config("default_damage")
    
    try:
        target_ac = combat_config.get_ac(target)
        
        # Check critical hit/miss thresholds
        critical_threshold = combat_config.get("combat_mechanics.critical_hit_threshold", 20)
        auto_miss_threshold = combat_config.get("combat_mechanics.auto_miss_threshold", 1)
        
        # Auto-miss on natural 1
        if attack_roll <= auto_miss_threshold:
            return {
                "hit": False,
                "damage": 0,
                "critical": False,
                "message": f"Critical miss! (Rolled {attack_roll})"
            }
        
        # Check if attack hits
        hit = attack_roll >= target_ac
        critical = attack_roll >= critical_threshold
        
        if not hit and not critical:
            return {
                "hit": False,
                "damage": 0,
                "critical": False,
                "message": f"Attack missed! (Rolled {attack_roll} vs AC {target_ac})"
            }
        
        # Calculate damage
        damage = _parse_and_roll_dice(damage_dice)
        
        # Double damage on critical hit
        if critical:
            damage *= 2
        
        # Apply minimum damage
        min_damage = combat_config.get("combat_mechanics.min_damage", 0)
        damage = max(min_damage, damage)
        
        hit_type = "critical hit" if critical else "hit"
        return {
            "hit": True,
            "damage": damage,
            "critical": critical,
            "message": f"{hit_type.capitalize()} for {damage} damage!"
        }
        
    except Exception as e:
        raise RuntimeError(f"Error calculating damage: {str(e)}") from e

def _parse_and_roll_dice(damage_dice: str) -> int:
    """
    Parse and roll damage dice.
    
    Args:
        damage_dice: Dice string like "1d6", "2d8+3", or just "5"
        
    Returns:
        Rolled damage value
    """
    try:
        # Handle simple number
        if "d" not in damage_dice:
            return int(damage_dice)
        
        # Parse dice notation
        parts = damage_dice.split("d")
        num_dice = int(parts[0]) if parts[0] else 1
        
        dice_and_modifier = parts[1].split("+") if "+" in parts[1] else [parts[1], "0"]
        dice_size = int(dice_and_modifier[0])
        modifier = int(dice_and_modifier[1]) if len(dice_and_modifier) > 1 else 0
        
        # Roll damage
        damage = sum(random.randint(1, dice_size) for _ in range(num_dice))
        return damage + modifier
        
    except (ValueError, IndexError) as e:
        # Fallback to default damage if parsing fails
        print(f"Warning: Failed to parse damage dice '{damage_dice}', using default")
        return random.randint(1, 6)  # Default 1d6

def apply_damage(target: Dict[str, Any], damage: int) -> Dict[str, Any]:
    """
    Apply damage to a target character.
    
    Args:
        target: Target character data
        damage: Amount of damage to apply
        
    Returns:
        Dict containing the updated target data and status
        
    Raises:
        ValueError: If invalid parameters are provided
        TypeError: If invalid data types are provided
    """
    # Input validation
    if not isinstance(target, dict):
        raise TypeError("Target must be a dictionary")
    if not isinstance(damage, (int, float)):
        raise TypeError("Damage must be a number")
    if damage < 0:
        raise ValueError("Damage cannot be negative")
    
    try:
        current_hp = combat_config.get_hp(target)
        max_hp = combat_config.get_max_hp(target)
        
        # Calculate new HP
        new_hp = max(combat_config.get("combat_mechanics.unconscious_hp_threshold", 0), 
                     current_hp - int(damage))
        
        # Update HP using config-aware method
        combat_config.set_hp(target, new_hp)
        
        # Determine status
        unconscious_threshold = combat_config.get("combat_mechanics.unconscious_hp_threshold", 0)
        status = "alive" if new_hp > unconscious_threshold else "unconscious"
        
        return {
            "success": True,
            "target": target,
            "previous_hp": current_hp,
            "new_hp": new_hp,
            "damage_taken": int(damage),
            "status": status,
            "message": f"Took {int(damage)} damage. HP: {new_hp}/{max_hp}"
        }
        
    except Exception as e:
        raise RuntimeError(f"Failed to apply damage: {str(e)}") from e

def format_combat_summary(combat_state: Dict[str, Any]) -> str:
    """
    Generate a human-readable summary of a combat.
    
    Args:
        combat_state: The full combat state
        
    Returns:
        str: A formatted summary of the combat
        
    Raises:
        TypeError: If combat_state is not a dictionary
    """
    if not isinstance(combat_state, dict):
        raise TypeError("Combat state must be a dictionary")
    
    try:
        summary = []
        
        # Basic combat info
        combat_name = combat_state.get('name', combat_state.get('battle_name', 'Unnamed Battle'))
        current_round = combat_state.get('round', combat_state.get('current_round', 1))
        
        summary.append(f"Combat: {combat_name}")
        summary.append(f"Round: {current_round}")
        
        # Party summary
        party = combat_state.get('party', [])
        if party:
            summary.append("\nParty:")
            for character in party:
                if isinstance(character, dict):
                    name = character.get('name', 'Unknown')
                    hp = combat_config.get_hp(character)
                    max_hp = combat_config.get_max_hp(character)
                    summary.append(f"  {name}: {hp}/{max_hp} HP")
        
        # Enemy summary
        enemies = combat_state.get('enemies', [])
        if enemies:
            summary.append("\nEnemies:")
            for enemy in enemies:
                if isinstance(enemy, dict):
                    name = enemy.get('name', 'Unknown')
                    hp = combat_config.get_hp(enemy)
                    max_hp = combat_config.get_max_hp(enemy)
                    summary.append(f"  {name}: {hp}/{max_hp} HP")
        
        # Initiative order (if available)
        initiative_order = combat_state.get('initiative_order', [])
        if initiative_order:
            summary.append("\nInitiative Order:")
            for participant in initiative_order[:5]:  # Show top 5
                if isinstance(participant, dict):
                    name = participant.get('name', 'Unknown')
                    initiative = participant.get('initiative', 0)
                    summary.append(f"  {name}: {initiative}")
        
        # Recent log entries (last 3)
        log_entries = combat_state.get('log', combat_state.get('combat_log', []))
        if log_entries:
            summary.append("\nRecent Events:")
            for entry in log_entries[-3:]:
                if isinstance(entry, dict):
                    message = entry.get('message', str(entry))
                elif isinstance(entry, str):
                    message = entry
                else:
                    message = str(entry)
                summary.append(f"  {message}")
        
        result = "\n".join(summary)
        return result
        
    except Exception as e:
        logging.error(f"Failed to format combat summary: {e}")
        return f"Combat Summary Error: {str(e)}" 
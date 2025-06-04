"""
Status Effects Business Logic

This module manages status effect application and resolution for combat.
Contains only business logic - no database operations or I/O.
"""

from datetime import datetime
from typing import Dict, Any, List, Optional, Union
import logging

from backend.infrastructure.config_loaders.combat_config_loader import combat_config
from backend.infrastructure.database_adapters.combat_database_adapter import combat_db_adapter


def apply_status_effect(combatant: Union[Dict[str, Any], Any], effect_name: str, 
                       duration: int = None, source: str = None, value: Any = None) -> Dict[str, Any]:
    """
    Apply a status effect to a combatant (pure business logic - in-memory only).
    
    Args:
        combatant: Combatant object or participant dictionary
        effect_name: Name of the effect to apply
        duration: Number of turns the effect should last (uses config default if None)
        source: ID of the source that applied the effect
        value: Optional value associated with the effect
        
    Returns:
        dict: The created effect object
        
    Raises:
        ValueError: If invalid parameters provided
        TypeError: If combatant is invalid type
    """
    # Input validation
    if not effect_name:
        raise ValueError("Effect name cannot be empty")
    if not isinstance(combatant, (dict, object)):
        raise TypeError("Combatant must be a dictionary or object")
    
    # Use default duration from config if not provided
    if duration is None:
        duration = combat_config.get_effect_duration("medium_term")
    
    if duration <= 0:
        raise ValueError("Duration must be positive")
    
    effect = {
        "name": effect_name,
        "duration": duration,
        "applied_by": source,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    if value is not None:
        effect["value"] = value
    
    try:
        # Handle application to a combat class instance
        if hasattr(combatant, 'status_effects') and hasattr(combatant, 'attributes'):
            combatant.status_effects.append(effect)
            combatant.attributes["status_effects"] = combatant.status_effects
            
            # Trigger persistence for long-duration effects
            persistent_threshold = combat_config.get("effect_durations.persistent_threshold", 20)
            if duration > persistent_threshold and hasattr(combatant, 'character_id'):
                success = combat_db_adapter.update_npc_status_effects(
                    combatant.character_id, 
                    combatant.status_effects
                )
                if not success:
                    logging.warning(f"Failed to persist status effect {effect_name} for NPC {combatant.character_id}")
        
        # Handle application to a dictionary participant
        elif isinstance(combatant, dict):
            combatant.setdefault("status_effects", []).append(effect)
            
            # Trigger persistence if we have participant info
            if "id" in combatant and "battle_id" in combatant:
                combat_db_adapter.update_combat_participant(
                    combatant["battle_id"],
                    combatant["id"],
                    combatant
                )
        else:
            raise TypeError("Combatant must have status_effects attribute or be a dictionary")
        
        logging.info(f"Applied status effect '{effect_name}' (duration: {duration}) to {_get_combatant_name(combatant)}")
        return effect
        
    except Exception as e:
        logging.error(f"Failed to apply status effect '{effect_name}': {str(e)}")
        raise RuntimeError(f"Failed to apply status effect: {str(e)}") from e


def tick_status_effects(combatant: Union[Dict[str, Any], Any]) -> List[str]:
    """
    Decrement status effect durations and remove expired effects from a combatant.
    Pure business logic - operates only in memory.
    
    Args:
        combatant: Combatant object with status_effects attribute
        
    Returns:
        list: Names of effects that expired this turn
        
    Raises:
        TypeError: If combatant doesn't have status effects
    """
    if not _has_status_effects(combatant):
        return []
    
    try:
        effects = _get_status_effects(combatant)
        updated = []
        expired = []
        
        for effect in effects:
            if not isinstance(effect, dict) or "duration" not in effect:
                logging.warning(f"Invalid effect format: {effect}")
                continue
                
            effect["duration"] -= 1
            if effect["duration"] > 0:
                updated.append(effect)
            else:
                expired.append(effect.get("name", "Unknown Effect"))
                logging.info(f"Status effect '{effect.get('name')}' expired on {_get_combatant_name(combatant)}")
        
        # Update combatant's effects
        _set_status_effects(combatant, updated)
        
        return expired
        
    except Exception as e:
        logging.error(f"Failed to tick status effects: {str(e)}")
        return []


def get_active_effects(combatant: Union[Dict[str, Any], Any]) -> List[Dict[str, Any]]:
    """
    Get all active status effects for a combatant.
    
    Args:
        combatant: Combatant object or dictionary
        
    Returns:
        List of active effect dictionaries
    """
    if not _has_status_effects(combatant):
        return []
    
    return _get_status_effects(combatant).copy()


def has_effect(combatant: Union[Dict[str, Any], Any], effect_name: str) -> bool:
    """
    Check if a combatant has a specific status effect.
    
    Args:
        combatant: Combatant object or dictionary
        effect_name: Name of the effect to check for
        
    Returns:
        True if the effect is active, False otherwise
    """
    effects = get_active_effects(combatant)
    return any(effect.get("name") == effect_name for effect in effects)


def remove_status_effect_by_name(combatant: Union[Dict[str, Any], Any], effect_name: str) -> bool:
    """
    Remove a specific status effect from a combatant by name.
    Pure business logic - operates only in memory.
    
    Args:
        combatant: Combatant object or dictionary
        effect_name: Name of the effect to remove
        
    Returns:
        bool: Whether the effect was successfully removed
    """
    if not effect_name or not _has_status_effects(combatant):
        return False
        
    try:
        effects = _get_status_effects(combatant)
        
        # Filter out the effect to remove
        updated_effects = [e for e in effects if e.get("name") != effect_name]
        
        # If we removed something, update the combatant
        if len(updated_effects) < len(effects):
            _set_status_effects(combatant, updated_effects)
            logging.info(f"Removed status effect '{effect_name}' from {_get_combatant_name(combatant)}")
            return True
        
        return False
        
    except Exception as e:
        logging.error(f"Failed to remove status effect '{effect_name}': {str(e)}")
        return False


def calculate_effect_impact(effect: Dict[str, Any], base_value: float) -> float:
    """
    Calculate the impact of a status effect on a base value.
    Pure business logic for effect calculations.
    
    Args:
        effect: The status effect dictionary
        base_value: The base value to modify
        
    Returns:
        The modified value
    """
    if not isinstance(effect, dict):
        return base_value
    
    effect_value = effect.get("value", 0)
    effect_type = effect.get("type", "additive")
    
    if effect_type == "additive":
        return base_value + effect_value
    elif effect_type == "multiplicative":
        return base_value * effect_value
    elif effect_type == "percentage":
        return base_value * (1 + effect_value / 100)
    else:
        return base_value


def get_effects_by_type(combatant: Union[Dict[str, Any], Any], effect_type: str) -> List[Dict[str, Any]]:
    """
    Get all active status effects of a specific type for a combatant.
    
    Args:
        combatant: Combatant object or dictionary
        effect_type: Type of effects to filter for
        
    Returns:
        List of matching effect dictionaries
    """
    effects = get_active_effects(combatant)
    return [effect for effect in effects if effect.get("type") == effect_type]


# Helper functions
def _has_status_effects(combatant: Union[Dict[str, Any], Any]) -> bool:
    """Check if combatant has status effects capability."""
    return (hasattr(combatant, 'status_effects') or 
            (isinstance(combatant, dict) and "status_effects" in combatant))


def _get_status_effects(combatant: Union[Dict[str, Any], Any]) -> List[Dict[str, Any]]:
    """Get status effects list from combatant."""
    if hasattr(combatant, 'status_effects'):
        return combatant.status_effects
    elif isinstance(combatant, dict):
        return combatant.get("status_effects", [])
    return []


def _set_status_effects(combatant: Union[Dict[str, Any], Any], effects: List[Dict[str, Any]]) -> None:
    """Set status effects list on combatant."""
    if hasattr(combatant, 'status_effects'):
        combatant.status_effects = effects
        if hasattr(combatant, 'attributes'):
            combatant.attributes["status_effects"] = effects
    elif isinstance(combatant, dict):
        combatant["status_effects"] = effects


def _get_combatant_name(combatant: Union[Dict[str, Any], Any]) -> str:
    """Get a displayable name for the combatant."""
    if hasattr(combatant, 'name'):
        return combatant.name
    elif isinstance(combatant, dict):
        return combatant.get("name", combatant.get("id", "Unknown"))
    return "Unknown" 
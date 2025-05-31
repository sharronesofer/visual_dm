"""
Equipment Durability utility functions.
This module provides functionality for managing equipment durability, including
damage, repair, and effects of durability on item performance.
"""

from typing import Dict, List, Optional, Any, Tuple
import logging
import random
from sqlalchemy.orm import Session
from backend.systems.equipment.models import Equipment, EquipmentDurabilityLog

logger = logging.getLogger(__name__)

# Import necessary database functionality
try:
    from backend.infrastructure.database import db
    from backend.systems.inventory.models import Item, InventoryItem
    HAS_DATABASE = True
except ImportError:
    HAS_DATABASE = False
    logger.warning("Database imports failed. Some durability functions may be limited.")

# Durability-related constants
DURABILITY_THRESHOLDS = {
    "perfect": 100.0,
    "excellent": 90.0,
    "good": 75.0,
    "worn": 50.0,
    "damaged": 25.0,
    "very_damaged": 10.0,
    "broken": 0.0
}

COMBAT_DAMAGE_BASE = {
    "weapon": 0.5,  # Weapons take damage on hit
    "armor": 0.2,   # Armor takes damage when hit
    "shield": 0.3,  # Shields take damage when blocking
    "accessory": 0.1  # Accessories take minimal damage
}

STAT_PENALTY_MULTIPLIERS = {
    "excellent": 0.0,  # No penalty
    "good": 0.0,       # No penalty
    "worn": 0.1,       # 10% stat reduction
    "damaged": 0.25,   # 25% stat reduction
    "very_damaged": 0.5  # 50% stat reduction
}

def get_durability_status(current_durability: float, max_durability: float) -> str:
    """
    Get the status label for the current durability state.
    
    Args:
        current_durability: Current durability value
        max_durability: Maximum durability value
        
    Returns:
        String status label (perfect, excellent, good, worn, damaged, very_damaged, broken)
    """
    if max_durability <= 0:
        return "broken"
        
    percentage = (current_durability / max_durability) * 100.0
    
    for status, threshold in sorted(DURABILITY_THRESHOLDS.items(), key=lambda x: x[1], reverse=True):
        if percentage >= threshold:
            return status
            
    return "broken"

def calculate_combat_damage(
    equipment_type: str, 
    combat_intensity: float = 1.0,
    is_critical: bool = False
) -> float:
    """
    Calculate durability damage from combat usage.
    
    Args:
        equipment_type: Type of equipment (weapon, armor, shield, accessory)
        combat_intensity: Multiplier for combat intensity (1.0 is normal)
        is_critical: Whether this was a critical hit (more damage)
        
    Returns:
        Amount of durability to reduce
    """
    base_damage = COMBAT_DAMAGE_BASE.get(equipment_type, 0.2)
    
    # Add randomness
    damage = base_damage * random.uniform(0.8, 1.2)
    
    # Apply combat intensity
    damage *= combat_intensity
    
    # Apply critical hit bonus
    if is_critical:
        damage *= 2.0
        
    return round(damage, 2)

def calculate_wear_damage(
    equipment_type: str,
    time_worn: float = 1.0,  # hours
    environmental_factor: float = 1.0  # normal conditions
) -> float:
    """
    Calculate durability damage from regular wear and tear.
    
    Args:
        equipment_type: Type of equipment
        time_worn: Hours the equipment has been worn/used
        environmental_factor: Multiplier for environmental conditions (rain, heat, etc.)
        
    Returns:
        Amount of durability to reduce
    """
    # Base wear values per hour
    base_wear = {
        "weapon": 0.05,
        "armor": 0.03,
        "shield": 0.02,
        "accessory": 0.01
    }
    
    wear = base_wear.get(equipment_type, 0.01) * time_worn * environmental_factor
    
    return round(wear, 2)

def apply_durability_damage(
    equipment_id: int, 
    damage_amount: float, 
    reason: str,
    details: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    Apply durability damage to an equipment item and log the change.
    
    Args:
        equipment_id: ID of the equipment
        damage_amount: Amount of durability to reduce
        reason: Reason for the damage (combat, wear, etc.)
        details: Optional details about the damage event
        
    Returns:
        Dictionary with updated equipment information
    """
    if not HAS_DATABASE:
        return {"success": False, "message": "Database not available"}
        
    try:
        equipment = Equipment.query.filter_by(id=equipment_id).first()
        if not equipment:
            return {"success": False, "message": f"Equipment with ID {equipment_id} not found"}
            
        # Store previous values for logging
        previous_durability = equipment.current_durability
        
        # Apply damage
        equipment.current_durability = max(0.0, equipment.current_durability - damage_amount)
        
        # Check if broken
        if equipment.current_durability <= 0:
            equipment.is_broken = True
            equipment.current_durability = 0.0
            
        # Create log entry
        log_entry = EquipmentDurabilityLog(
            equipment_id=equipment_id,
            previous_durability=previous_durability,
            new_durability=equipment.current_durability,
            change_amount=-damage_amount,  # Negative for damage
            change_reason=reason,
            event_details=details
        )
        
        db.session.add(log_entry)
        db.session.commit()
        
        return {
            "success": True,
            "equipment": equipment.to_dict(),
            "damage_applied": damage_amount,
            "is_broken": equipment.is_broken,
            "status": get_durability_status(equipment.current_durability, equipment.max_durability)
        }
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error applying durability damage: {e}")
        return {"success": False, "message": f"Error: {str(e)}"}

def calculate_repair_cost(
    current_durability: float,
    max_durability: float,
    item_value: float,
    repair_amount: Optional[float] = None
) -> Dict[str, float]:
    """
    Calculate the cost to repair an item.
    
    Args:
        current_durability: Current durability
        max_durability: Maximum durability
        item_value: Base value of the item
        repair_amount: Optional specific amount to repair, otherwise full repair
        
    Returns:
        Dictionary with repair cost and details
    """
    if current_durability >= max_durability:
        return {"cost": 0.0, "repair_amount": 0.0}
    
    if repair_amount is None:
        repair_amount = max_durability - current_durability
    else:
        repair_amount = min(repair_amount, max_durability - current_durability)
    
    # Calculate repair cost based on item value and repair percentage
    repair_percentage = repair_amount / max_durability
    base_cost = item_value * repair_percentage
    
    # Apply cost multiplier based on how damaged the item is
    durability_percentage = current_durability / max_durability
    
    if durability_percentage < 0.1:  # Very damaged items cost more to repair
        cost_multiplier = 1.5
    elif durability_percentage < 0.3:
        cost_multiplier = 1.25
    else:
        cost_multiplier = 1.0
    
    total_cost = base_cost * cost_multiplier
    
    return {
        "cost": round(total_cost, 2),
        "repair_amount": repair_amount,
        "cost_multiplier": cost_multiplier
    }

def repair_equipment(
    equipment_id: int, 
    repair_amount: Optional[float] = None,
    full_repair: bool = False
) -> Dict[str, Any]:
    """
    Repair equipment durability and log the change.
    
    Args:
        equipment_id: ID of the equipment
        repair_amount: Amount of durability to restore (None for full repair)
        full_repair: Force full repair regardless of repair_amount
        
    Returns:
        Dictionary with updated equipment information
    """
    if not HAS_DATABASE:
        return {"success": False, "message": "Database not available"}
        
    try:
        equipment = Equipment.query.filter_by(id=equipment_id).first()
        if not equipment:
            return {"success": False, "message": f"Equipment with ID {equipment_id} not found"}
            
        # Store previous values for logging
        previous_durability = equipment.current_durability
        
        if full_repair:
            repair_amount = equipment.max_durability - equipment.current_durability
        elif repair_amount is None:
            repair_amount = equipment.max_durability - equipment.current_durability
        else:
            repair_amount = min(repair_amount, equipment.max_durability - equipment.current_durability)
            
        # Apply repair
        equipment.current_durability = min(equipment.max_durability, equipment.current_durability + repair_amount)
        
        # Update broken status
        if equipment.current_durability > 0:
            equipment.is_broken = False
            
        # Create log entry
        log_entry = EquipmentDurabilityLog(
            equipment_id=equipment_id,
            previous_durability=previous_durability,
            new_durability=equipment.current_durability,
            change_amount=repair_amount,  # Positive for repair
            change_reason="repair",
            event_details={"full_repair": full_repair}
        )
        
        db.session.add(log_entry)
        db.session.commit()
        
        return {
            "success": True,
            "equipment": equipment.to_dict(),
            "repair_applied": repair_amount,
            "is_broken": equipment.is_broken,
            "status": get_durability_status(equipment.current_durability, equipment.max_durability)
        }
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error repairing equipment: {e}")
        return {"success": False, "message": f"Error: {str(e)}"}

def adjust_stats_for_durability(
    equipment: Dict[str, Any],
    item_stats: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Adjust item stats based on durability.
    
    Args:
        equipment: Equipment data with durability information
        item_stats: Base item stats
        
    Returns:
        Updated item stats adjusted for durability
    """
    # Make a copy to avoid modifying the original
    adjusted_stats = item_stats.copy()
    
    # Don't adjust if item is not equipped or has no stats
    if not equipment or not adjusted_stats:
        return adjusted_stats
    
    current_durability = equipment.get('current_durability', 100.0)
    max_durability = equipment.get('max_durability', 100.0)
    
    # Broken items provide no benefits
    if equipment.get('is_broken', False) or current_durability <= 0:
        for stat in adjusted_stats:
            if isinstance(adjusted_stats[stat], (int, float)):
                adjusted_stats[stat] = 0
        return adjusted_stats
    
    # Calculate durability status
    status = get_durability_status(current_durability, max_durability)
    
    # Apply stat penalties based on status
    penalty = STAT_PENALTY_MULTIPLIERS.get(status, 0.0)
    if penalty > 0:
        for stat in adjusted_stats:
            if isinstance(adjusted_stats[stat], (int, float)) and adjusted_stats[stat] > 0:
                adjusted_stats[stat] = round(adjusted_stats[stat] * (1 - penalty), 2)
    
    return adjusted_stats

def get_durability_history(
    equipment_id: int,
    limit: int = 10
) -> List[Dict[str, Any]]:
    """
    Get durability change history for an equipment item.
    
    Args:
        equipment_id: ID of the equipment
        limit: Maximum number of log entries to return
        
    Returns:
        List of durability log entries
    """
    if not HAS_DATABASE:
        return []
        
    try:
        logs = EquipmentDurabilityLog.query.filter_by(
            equipment_id=equipment_id
        ).order_by(
            EquipmentDurabilityLog.timestamp.desc()
        ).limit(limit).all()
        
        return [log.to_dict() for log in logs]
    except Exception as e:
        logger.error(f"Error getting durability history: {e}")
        return [] 
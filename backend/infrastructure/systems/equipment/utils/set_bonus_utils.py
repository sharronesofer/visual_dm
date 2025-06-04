"""
Equipment Set Bonus utility functions.
This module provides functionality for managing equipment sets and calculating
set bonuses when multiple pieces from the same set are equipped.
"""

from typing import Dict, List, Optional, Any
import logging
from sqlalchemy.orm import Session
from ..models.models import Equipment, EquipmentSet
from backend.systems.inventory.models import Item

logger = logging.getLogger(__name__)

# Import necessary database functionality
try:
    from backend.infrastructure.database import db
    HAS_DATABASE = True
except ImportError:
    HAS_DATABASE = False
    logger.warning("Database imports failed. Some set bonus functions may be limited.")

def get_equipment_sets() -> List[Dict[str, Any]]:
    """
    Get all available equipment sets.
    
    Returns:
        List of dictionaries containing equipment set information
    """
    if not HAS_DATABASE:
        return []
        
    try:
        sets = EquipmentSet.query.all()
        return [s.to_dict() for s in sets]
    except Exception as e:
        logger.error(f"Error getting equipment sets: {e}")
        return []

def get_equipment_set(set_id: int) -> Optional[Dict[str, Any]]:
    """
    Get a specific equipment set by ID.
    
    Args:
        set_id: ID of the equipment set
        
    Returns:
        Dictionary containing equipment set information, or None if not found
    """
    if not HAS_DATABASE:
        return None
        
    try:
        equipment_set = EquipmentSet.query.filter_by(id=set_id).first()
        if not equipment_set:
            return None
        return equipment_set.to_dict()
    except Exception as e:
        logger.error(f"Error getting equipment set {set_id}: {e}")
        return None

def get_item_set_membership(item_id: int) -> List[Dict[str, Any]]:
    """
    Get all sets that an item belongs to.
    
    Args:
        item_id: ID of the item
        
    Returns:
        List of equipment sets the item belongs to
    """
    if not HAS_DATABASE:
        return []
        
    try:
        sets = EquipmentSet.query.filter(
            EquipmentSet.item_ids.contains([item_id])
        ).all()
        return [s.to_dict() for s in sets]
    except Exception as e:
        logger.error(f"Error getting sets for item {item_id}: {e}")
        return []

def calculate_set_bonuses(character_id: int) -> Dict[str, Any]:
    """
    Calculate all active set bonuses for a character based on equipped items.
    
    Args:
        character_id: ID of the character
        
    Returns:
        Dictionary with set bonus information keyed by set ID
    """
    if not HAS_DATABASE:
        return {}
        
    try:
        # Get all equipped items for the character
        equipped_items = Equipment.query.filter_by(character_id=character_id).all()
        if not equipped_items:
            return {}
            
        # Get item IDs
        item_ids = [eq.item_id for eq in equipped_items if eq.item_id is not None]
        if not item_ids:
            return {}
            
        # Get all equipment sets
        all_sets = EquipmentSet.query.all()
        if not all_sets:
            return {}
            
        # Calculate which sets have pieces equipped and how many
        set_counts = {}
        set_details = {}
        
        for equipment_set in all_sets:
            # Count how many pieces of this set are equipped
            equipped_set_items = [item_id for item_id in item_ids 
                                if item_id in equipment_set.item_ids]
            count = len(equipped_set_items)
            
            if count > 0:
                set_counts[equipment_set.id] = count
                set_details[equipment_set.id] = {
                    'name': equipment_set.name,
                    'equipped_count': count,
                    'total_pieces': len(equipment_set.item_ids),
                    'active_bonuses': {}
                }
                
                # Check which bonuses are active based on count
                for pieces_required, bonuses in equipment_set.set_bonuses.items():
                    if count >= int(pieces_required):
                        set_details[equipment_set.id]['active_bonuses'][pieces_required] = bonuses
        
        return {
            'character_id': character_id,
            'active_sets': set_details
        }
    except Exception as e:
        logger.error(f"Error calculating set bonuses for character {character_id}: {e}")
        return {'character_id': character_id, 'active_sets': {}, 'error': str(e)}

def apply_set_bonuses(character_attributes: Dict[str, Any], set_bonuses: Dict[str, Any]) -> Dict[str, Any]:
    """
    Apply set bonuses to character attributes.
    
    Args:
        character_attributes: Dictionary containing character attributes
        set_bonuses: Dictionary with active set bonuses
        
    Returns:
        Updated character attributes with set bonuses applied
    """
    # Make a copy of the attributes to avoid modifying the original
    updated_attributes = character_attributes.copy()
    
    # Track applied bonuses for reporting
    applied_bonuses = []
    
    # Apply bonuses from each active set
    for set_id, set_info in set_bonuses.get('active_sets', {}).items():
        for pieces_required, bonuses in set_info.get('active_bonuses', {}).items():
            # Apply attribute bonuses
            for attribute, value in bonuses.get('stats', {}).items():
                if attribute in updated_attributes:
                    updated_attributes[attribute] += value
                else:
                    updated_attributes[attribute] = value
                    
                applied_bonuses.append({
                    'set': set_info['name'],
                    'pieces': pieces_required,
                    'bonus': f"{attribute} +{value}"
                })
                
            # Apply special effects
            for effect in bonuses.get('effects', []):
                if 'effects' not in updated_attributes:
                    updated_attributes['effects'] = []
                updated_attributes['effects'].append({
                    'id': f"set_bonus_{set_id}_{pieces_required}",
                    'name': effect.get('name', 'Set Bonus'),
                    'description': effect.get('description', ''),
                    'source': set_info['name'],
                    'is_set_bonus': True
                })
                
                applied_bonuses.append({
                    'set': set_info['name'],
                    'pieces': pieces_required,
                    'bonus': effect.get('name', 'Special Effect')
                })
    
    # Add the applied bonuses to the attributes for reference
    updated_attributes['applied_set_bonuses'] = applied_bonuses
    
    return updated_attributes

def create_equipment_set(
    name: str, 
    description: str, 
    item_ids: List[int], 
    set_bonuses: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """
    Create a new equipment set.
    
    Args:
        name: Name of the equipment set
        description: Description of the equipment set
        item_ids: List of item IDs that belong to this set
        set_bonuses: Dictionary mapping number of pieces to bonuses
        
    Returns:
        Dictionary containing the created equipment set, or None if creation failed
    """
    if not HAS_DATABASE:
        return None
        
    try:
        # Validate set bonuses format
        for pieces, bonuses in set_bonuses.items():
            try:
                pieces_int = int(pieces)
                if pieces_int <= 0:
                    return None
            except ValueError:
                return None
                
            if not isinstance(bonuses, dict):
                return None
        
        # Create new equipment set
        equipment_set = EquipmentSet(
            name=name,
            description=description,
            item_ids=item_ids,
            set_bonuses=set_bonuses
        )
        
        db.session.add(equipment_set)
        db.session.commit()
        
        return equipment_set.to_dict()
    except Exception as e:
        logger.error(f"Error creating equipment set: {e}")
        db.session.rollback()
        return None

def update_equipment_set(
    set_id: int,
    name: Optional[str] = None,
    description: Optional[str] = None,
    item_ids: Optional[List[int]] = None,
    set_bonuses: Optional[Dict[str, Any]] = None
) -> Optional[Dict[str, Any]]:
    """
    Update an existing equipment set.
    
    Args:
        set_id: ID of the equipment set to update
        name: Optional new name for the equipment set
        description: Optional new description
        item_ids: Optional new list of item IDs
        set_bonuses: Optional new set bonuses
        
    Returns:
        Dictionary containing the updated equipment set, or None if update failed
    """
    if not HAS_DATABASE:
        return None
        
    try:
        equipment_set = EquipmentSet.query.filter_by(id=set_id).first()
        if not equipment_set:
            return None
            
        # Update fields if provided
        if name is not None:
            equipment_set.name = name
        if description is not None:
            equipment_set.description = description
        if item_ids is not None:
            equipment_set.item_ids = item_ids
        if set_bonuses is not None:
            # Validate set bonuses format
            for pieces, bonuses in set_bonuses.items():
                try:
                    pieces_int = int(pieces)
                    if pieces_int <= 0:
                        return None
                except ValueError:
                    return None
                    
                if not isinstance(bonuses, dict):
                    return None
                    
            equipment_set.set_bonuses = set_bonuses
            
        equipment_set.updated_at = db.func.now()
        db.session.commit()
        
        return equipment_set.to_dict()
    except Exception as e:
        logger.error(f"Error updating equipment set {set_id}: {e}")
        db.session.rollback()
        return None

def delete_equipment_set(set_id: int) -> bool:
    """
    Delete an equipment set.
    
    Args:
        set_id: ID of the equipment set to delete
        
    Returns:
        True if deleted successfully, False otherwise
    """
    if not HAS_DATABASE:
        return False
        
    try:
        equipment_set = EquipmentSet.query.filter_by(id=set_id).first()
        if not equipment_set:
            return False
            
        db.session.delete(equipment_set)
        db.session.commit()
        
        return True
    except Exception as e:
        logger.error(f"Error deleting equipment set {set_id}: {e}")
        db.session.rollback()
        return False 
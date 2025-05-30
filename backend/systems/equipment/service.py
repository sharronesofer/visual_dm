"""
Equipment service for managing equipment operations.
This module provides high-level functions for equipment management.
"""

from typing import Dict, List, Optional, Any, Tuple
import logging
from .models import Equipment
from .inventory_utils import (
    load_equipment_rules, 
    can_equip_item, 
    get_equipment_stats,
    check_durability_requirements
)
from .identify_item_utils import (
    calculate_identification_cost,
    reveal_item_name_and_flavor
)
from .set_bonus_utils import (
    calculate_set_bonuses,
    apply_set_bonuses,
    get_equipment_sets,
    get_equipment_set,
    create_equipment_set,
    update_equipment_set,
    delete_equipment_set
)
from .durability_utils import (
    apply_durability_damage,
    calculate_combat_damage,
    calculate_wear_damage,
    calculate_repair_cost,
    repair_equipment,
    get_durability_history,
    get_durability_status
)

# Import canonical inventory functionality if it exists
try:
    from backend.core.database import db
    from backend.systems.inventory.models import Inventory, InventoryItem
    HAS_INVENTORY_SYSTEM = True
except ImportError:
    HAS_INVENTORY_SYSTEM = False

# Import narrative system utils if available    
try:
    from backend.systems.narrative.utils import (
        gpt_flavor_identify_effect,
        gpt_flavor_reveal_full_item
    )
    HAS_NARRATIVE_SYSTEM = True
except ImportError:
    HAS_NARRATIVE_SYSTEM = False
    # Fallback functions if narrative system not available
    def gpt_flavor_identify_effect(item_name, effect):
        return f"You discover that {item_name} has the effect: {effect}."
    def gpt_flavor_reveal_full_item(item):
        return f"All properties of {item.get('name', 'the item')} are now revealed."

logger = logging.getLogger(__name__)

class EquipmentService:
    """Service for managing character equipment."""
    
    @staticmethod
    async def equip_item(character_id: int, item_id: int, slot: str) -> Dict[str, Any]:
        """
        Equip an item from inventory to a character's equipment slot.
        
        Args:
            character_id: ID of the character
            item_id: ID of the item to equip
            slot: Slot to equip the item in
            
        Returns:
            Dict with success status and result information
        """
        try:
            # Verify character exists
            # This would normally check the character service
            
            # Verify item exists and is in inventory
            if HAS_INVENTORY_SYSTEM:
                item = InventoryItem.query.filter_by(
                    inventory_id=character_id, 
                    item_id=item_id
                ).first()
                
                if not item:
                    return {
                        "success": False,
                        "message": "Item not found in inventory"
                    }
                
                # Get item details for requirements check
                item_data = item.to_dict()
            else:
                # Mock item data for testing
                item_data = {"id": item_id, "slot": slot}
            
            # Check character stats for requirements
            # This would normally get character stats
            character_data = {"stats": {}, "equipped_items": []}
            
            # Check durability requirements
            if not check_durability_requirements(item_data):
                return {
                    "success": False,
                    "message": "Item is too damaged to equip"
                }
            
            # Check if item can be equipped
            if not can_equip_item(character_data, item_data):
                return {
                    "success": False,
                    "message": "Character does not meet requirements to equip this item"
                }
            
            # Check if slot already has an item
            existing_equipment = Equipment.query.filter_by(
                character_id=character_id,
                slot=slot
            ).first()
            
            old_item_id = None
            if existing_equipment:
                old_item_id = existing_equipment.item_id
                existing_equipment.item_id = item_id
                db.session.commit()
            else:
                # Create new equipment entry
                equipment = Equipment(
                    character_id=character_id,
                    slot=slot,
                    item_id=item_id,
                    current_durability=item_data.get("current_durability", 100.0),
                    max_durability=item_data.get("max_durability", 100.0),
                    is_broken=item_data.get("is_broken", False)
                )
                db.session.add(equipment)
                db.session.commit()
            
            # Recalculate set bonuses when equipment changes
            set_bonuses = calculate_set_bonuses(character_id)
            
            return {
                "success": True,
                "message": "Item equipped successfully",
                "old_item_id": old_item_id,
                "new_item_id": item_id,
                "set_bonuses": set_bonuses
            }
            
        except Exception as e:
            logger.error(f"Error equipping item: {e}")
            return {
                "success": False,
                "message": f"Error: {str(e)}"
            }
    
    @staticmethod
    async def unequip_item(character_id: int, slot: str) -> Dict[str, Any]:
        """
        Unequip an item from a character's equipment slot.
        
        Args:
            character_id: ID of the character
            slot: Slot to unequip the item from
            
        Returns:
            Dict with success status and result information
        """
        try:
            # Find equipment in slot
            equipment = Equipment.query.filter_by(
                character_id=character_id,
                slot=slot
            ).first()
            
            if not equipment:
                return {
                    "success": False,
                    "message": "No item equipped in that slot"
                }
            
            item_id = equipment.item_id
            
            # Remove equipment
            db.session.delete(equipment)
            db.session.commit()
            
            # Recalculate set bonuses when equipment changes
            set_bonuses = calculate_set_bonuses(character_id)
            
            return {
                "success": True,
                "message": "Item unequipped successfully",
                "item_id": item_id,
                "set_bonuses": set_bonuses
            }
            
        except Exception as e:
            logger.error(f"Error unequipping item: {e}")
            return {
                "success": False,
                "message": f"Error: {str(e)}"
            }
    
    @staticmethod
    async def get_character_equipment(character_id: int) -> Dict[str, Any]:
        """
        Get a character's equipped items.
        
        Args:
            character_id: ID of the character
            
        Returns:
            Dict with equipment information
        """
        try:
            # Get all equipment for character
            equipment_items = Equipment.query.filter_by(
                character_id=character_id
            ).all()
            
            # Convert to dict by slot
            equipment_by_slot = {}
            for eq in equipment_items:
                equipment_by_slot[eq.slot] = eq.to_dict()
            
            # Get item details for each equipped item
            if HAS_INVENTORY_SYSTEM:
                item_ids = [eq.item_id for eq in equipment_items if eq.item_id]
                items = InventoryItem.query.filter(
                    InventoryItem.item_id.in_(item_ids)
                ).all()
                
                item_details = {item.item_id: item.to_dict() for item in items}
                
                # Add item details to equipment
                for slot, eq in equipment_by_slot.items():
                    if eq["item_id"] in item_details:
                        eq["item"] = item_details[eq["item_id"]]
            
            # Calculate stats from equipment
            equipped_items = [eq.to_dict() for eq in equipment_items]
            stats = get_equipment_stats(equipped_items)
            
            # Calculate and apply set bonuses
            set_bonuses = calculate_set_bonuses(character_id)
            stats_with_bonuses = apply_set_bonuses(stats, set_bonuses)
            
            return {
                "success": True,
                "equipment": equipment_by_slot,
                "stats": stats_with_bonuses,
                "set_bonuses": set_bonuses
            }
            
        except Exception as e:
            logger.error(f"Error getting character equipment: {e}")
            return {
                "success": False,
                "message": f"Error: {str(e)}"
            }
            
    @staticmethod
    async def swap_equipment(character_id: int, slot: str, new_item_id: int) -> Dict[str, Any]:
        """
        Swap an equipped item with a new item in one operation.
        
        Args:
            character_id: ID of the character
            slot: Slot to swap item in
            new_item_id: ID of the new item to equip
            
        Returns:
            Dict with success status and result information
        """
        # This is a convenience method that combines unequip and equip
        result = await EquipmentService.unequip_item(character_id, slot)
        if not result["success"]:
            return result
            
        old_item_id = result.get("item_id")
        
        result = await EquipmentService.equip_item(character_id, new_item_id, slot)
        if result["success"]:
            result["old_item_id"] = old_item_id
            
        return result
    
    @staticmethod
    async def apply_combat_damage(
        equipment_id: int,
        equipment_type: str,
        combat_intensity: float = 1.0,
        is_critical: bool = False
    ) -> Dict[str, Any]:
        """
        Apply combat damage to an equipment item.
        
        Args:
            equipment_id: ID of the equipment
            equipment_type: Type of equipment (weapon, armor, shield, accessory)
            combat_intensity: Multiplier for combat intensity (1.0 is normal)
            is_critical: Whether this was a critical hit (more damage)
            
        Returns:
            Dict with damage result
        """
        try:
            # Calculate damage amount
            damage_amount = calculate_combat_damage(
                equipment_type,
                combat_intensity,
                is_critical
            )
            
            # Apply damage
            result = apply_durability_damage(
                equipment_id,
                damage_amount,
                "combat",
                {"combat_intensity": combat_intensity, "is_critical": is_critical}
            )
            
            return result
        except Exception as e:
            logger.error(f"Error applying combat damage: {e}")
            return {
                "success": False,
                "message": f"Error: {str(e)}"
            }
    
    @staticmethod
    async def apply_wear_damage(
        equipment_id: int,
        equipment_type: str,
        time_worn: float = 1.0,
        environmental_factor: float = 1.0
    ) -> Dict[str, Any]:
        """
        Apply wear and tear damage to an equipment item.
        
        Args:
            equipment_id: ID of the equipment
            equipment_type: Type of equipment (weapon, armor, shield, accessory)
            time_worn: Hours the equipment has been worn/used
            environmental_factor: Multiplier for environmental conditions (rain, heat, etc.)
            
        Returns:
            Dict with damage result
        """
        try:
            # Calculate wear damage
            damage_amount = calculate_wear_damage(
                equipment_type,
                time_worn,
                environmental_factor
            )
            
            # Apply damage
            result = apply_durability_damage(
                equipment_id,
                damage_amount,
                "wear",
                {"time_worn": time_worn, "environmental_factor": environmental_factor}
            )
            
            return result
        except Exception as e:
            logger.error(f"Error applying wear damage: {e}")
            return {
                "success": False,
                "message": f"Error: {str(e)}"
            }
    
    @staticmethod
    async def repair_equipment_item(
        equipment_id: int,
        repair_amount: Optional[float] = None,
        full_repair: bool = False
    ) -> Dict[str, Any]:
        """
        Repair an equipment item.
        
        Args:
            equipment_id: ID of the equipment
            repair_amount: Amount of durability to restore (None for full repair)
            full_repair: Force full repair regardless of repair_amount
            
        Returns:
            Dict with repair result
        """
        try:
            # Apply repair
            result = repair_equipment(
                equipment_id,
                repair_amount,
                full_repair
            )
            
            return result
        except Exception as e:
            logger.error(f"Error repairing equipment: {e}")
            return {
                "success": False,
                "message": f"Error: {str(e)}"
            }
    
    @staticmethod
    async def get_durability_status(equipment_id: int) -> Dict[str, Any]:
        """
        Get the durability status of an equipment item.
        
        Args:
            equipment_id: ID of the equipment
            
        Returns:
            Dict with durability status information
        """
        try:
            equipment = Equipment.query.filter_by(id=equipment_id).first()
            if not equipment:
                return {
                    "success": False,
                    "message": f"Equipment with ID {equipment_id} not found"
                }
                
            status = get_durability_status(equipment.current_durability, equipment.max_durability)
            
            return {
                "success": True,
                "equipment_id": equipment_id,
                "current_durability": equipment.current_durability,
                "max_durability": equipment.max_durability,
                "durability_percentage": round((equipment.current_durability / equipment.max_durability) * 100, 1) if equipment.max_durability > 0 else 0,
                "status": status,
                "is_broken": equipment.is_broken
            }
        except Exception as e:
            logger.error(f"Error getting durability status: {e}")
            return {
                "success": False,
                "message": f"Error: {str(e)}"
            }
    
    @staticmethod
    async def get_repair_cost(
        equipment_id: int,
        repair_amount: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Calculate the cost to repair an equipment item.
        
        Args:
            equipment_id: ID of the equipment
            repair_amount: Optional specific amount to repair, otherwise full repair
            
        Returns:
            Dict with repair cost information
        """
        try:
            equipment = Equipment.query.filter_by(id=equipment_id).first()
            if not equipment:
                return {
                    "success": False,
                    "message": f"Equipment with ID {equipment_id} not found"
                }
                
            # Get item value - this would normally come from the Item data
            # For now, using a mock value based on item_id
            item_value = 100.0 * (equipment.item_id % 10 + 1)  # Mock value
            
            cost_info = calculate_repair_cost(
                equipment.current_durability,
                equipment.max_durability,
                item_value,
                repair_amount
            )
            
            return {
                "success": True,
                "equipment_id": equipment_id,
                "repair_cost": cost_info["cost"],
                "repair_amount": cost_info["repair_amount"],
                "cost_multiplier": cost_info.get("cost_multiplier", 1.0),
                "current_durability": equipment.current_durability,
                "max_durability": equipment.max_durability
            }
        except Exception as e:
            logger.error(f"Error calculating repair cost: {e}")
            return {
                "success": False,
                "message": f"Error: {str(e)}"
            }
    
    @staticmethod
    async def get_durability_history(
        equipment_id: int,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Get durability change history for an equipment item.
        
        Args:
            equipment_id: ID of the equipment
            limit: Maximum number of log entries to return
            
        Returns:
            Dict with durability history
        """
        try:
            equipment = Equipment.query.filter_by(id=equipment_id).first()
            if not equipment:
                return {
                    "success": False,
                    "message": f"Equipment with ID {equipment_id} not found"
                }
                
            history = get_durability_history(equipment_id, limit)
            
            return {
                "success": True,
                "equipment_id": equipment_id,
                "history": history
            }
        except Exception as e:
            logger.error(f"Error getting durability history: {e}")
            return {
                "success": False,
                "message": f"Error: {str(e)}"
            }
        
    @staticmethod
    async def get_character_set_bonuses(character_id: int) -> Dict[str, Any]:
        """
        Get all active set bonuses for a character.
        
        Args:
            character_id: ID of the character
            
        Returns:
            Dict with active set bonuses information
        """
        try:
            set_bonuses = calculate_set_bonuses(character_id)
            
            return {
                "success": True,
                "character_id": character_id,
                "set_bonuses": set_bonuses
            }
            
        except Exception as e:
            logger.error(f"Error getting character set bonuses: {e}")
            return {
                "success": False,
                "message": f"Error: {str(e)}"
            }
    
    @staticmethod
    async def get_all_equipment_sets() -> Dict[str, Any]:
        """
        Get all available equipment sets.
        
        Returns:
            Dict with equipment sets information
        """
        try:
            sets = get_equipment_sets()
            
            return {
                "success": True,
                "equipment_sets": sets
            }
            
        except Exception as e:
            logger.error(f"Error getting equipment sets: {e}")
            return {
                "success": False,
                "message": f"Error: {str(e)}"
            }
    
    @staticmethod
    async def get_equipment_set_by_id(set_id: int) -> Dict[str, Any]:
        """
        Get a specific equipment set by ID.
        
        Args:
            set_id: ID of the equipment set
            
        Returns:
            Dict with equipment set information
        """
        try:
            equipment_set = get_equipment_set(set_id)
            
            if not equipment_set:
                return {
                    "success": False,
                    "message": f"Equipment set with ID {set_id} not found"
                }
                
            return {
                "success": True,
                "equipment_set": equipment_set
            }
            
        except Exception as e:
            logger.error(f"Error getting equipment set {set_id}: {e}")
            return {
                "success": False,
                "message": f"Error: {str(e)}"
            }
    
    @staticmethod
    async def create_new_equipment_set(
        name: str, 
        description: str, 
        item_ids: List[int], 
        set_bonuses: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create a new equipment set.
        
        Args:
            name: Name of the equipment set
            description: Description of the equipment set
            item_ids: List of item IDs that belong to this set
            set_bonuses: Dictionary mapping number of pieces to bonuses
            
        Returns:
            Dict with created equipment set information
        """
        try:
            equipment_set = create_equipment_set(name, description, item_ids, set_bonuses)
            
            if not equipment_set:
                return {
                    "success": False,
                    "message": "Failed to create equipment set"
                }
                
            return {
                "success": True,
                "message": "Equipment set created successfully",
                "equipment_set": equipment_set
            }
            
        except Exception as e:
            logger.error(f"Error creating equipment set: {e}")
            return {
                "success": False,
                "message": f"Error: {str(e)}"
            }
    
    @staticmethod
    async def update_existing_equipment_set(
        set_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
        item_ids: Optional[List[int]] = None,
        set_bonuses: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Update an existing equipment set.
        
        Args:
            set_id: ID of the equipment set to update
            name: Optional new name for the equipment set
            description: Optional new description
            item_ids: Optional new list of item IDs
            set_bonuses: Optional new set bonuses
            
        Returns:
            Dict with updated equipment set information
        """
        try:
            equipment_set = update_equipment_set(
                set_id, name, description, item_ids, set_bonuses
            )
            
            if not equipment_set:
                return {
                    "success": False,
                    "message": f"Equipment set with ID {set_id} not found or update failed"
                }
                
            return {
                "success": True,
                "message": "Equipment set updated successfully",
                "equipment_set": equipment_set
            }
            
        except Exception as e:
            logger.error(f"Error updating equipment set {set_id}: {e}")
            return {
                "success": False,
                "message": f"Error: {str(e)}"
            }
    
    @staticmethod
    async def delete_equipment_set_by_id(set_id: int) -> Dict[str, Any]:
        """
        Delete an equipment set.
        
        Args:
            set_id: ID of the equipment set to delete
            
        Returns:
            Dict with deletion result
        """
        try:
            success = delete_equipment_set(set_id)
            
            if not success:
                return {
                    "success": False,
                    "message": f"Equipment set with ID {set_id} not found or deletion failed"
                }
                
            return {
                "success": True,
                "message": "Equipment set deleted successfully"
            }
            
        except Exception as e:
            logger.error(f"Error deleting equipment set {set_id}: {e}")
            return {
                "success": False,
                "message": f"Error: {str(e)}"
            }
    
    @staticmethod
    async def identify_item(
        character_id: int, 
        item_id: int, 
        region: Optional[str] = None, 
        faction_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Identify a single unknown effect on an item.
        
        Args:
            character_id: ID of the character
            item_id: ID of the item to identify
            region: Optional region name for economic modifiers
            faction_id: Optional faction ID for discounts
            
        Returns:
            Dict with identification result
        """
        try:
            # Verify character exists and has the item
            if HAS_INVENTORY_SYSTEM:
                inventory_item = InventoryItem.query.filter_by(
                    inventory_id=character_id,
                    item_id=item_id
                ).first()
                
                if not inventory_item:
                    return {
                        "success": False,
                        "message": "Item not found in inventory"
                    }
                
                item = inventory_item.to_dict()
            else:
                # Mock item data for testing
                item = {
                    "id": item_id,
                    "name": "Unknown Item",
                    "unknown_effects": ["Magic effect"],
                    "identified_effects": []
                }
            
            # Check for unknown effects
            unknown_effects = item.get("unknown_effects", [])
            if not unknown_effects:
                return {
                    "success": False,
                    "message": "Item already fully identified"
                }
            
            # Calculate cost
            cost = calculate_identification_cost(item, region, faction_id)
            
            # Check if character has enough gold
            # This would normally check character's gold
            character_gold = 1000  # Mock value for testing
            
            if character_gold < cost:
                return {
                    "success": False,
                    "message": "Not enough gold",
                    "required": cost,
                    "current": character_gold
                }
            
            # Deduct gold
            # This would normally update character's gold
            remaining_gold = character_gold - cost
            
            # Reveal one effect
            revealed = unknown_effects.pop(0)
            item.setdefault("identified_effects", []).append(revealed)
            
            # Update item flavor text
            reveal_item_name_and_flavor(item)
            
            # Generate flavor text with GPT if available
            if HAS_NARRATIVE_SYSTEM:
                flavor = gpt_flavor_identify_effect(item.get("name", "Unknown Item"), revealed)
            else:
                flavor = f"You discover that {item.get('name', 'the item')} has the effect: {revealed}"
            
            # Update item in inventory
            if HAS_INVENTORY_SYSTEM:
                # Update inventory item properties
                inventory_item.properties = item
                db.session.commit()
            
            return {
                "success": True,
                "message": f"Effect '{revealed}' identified",
                "flavor": flavor,
                "gold_spent": cost,
                "remaining_gold": remaining_gold,
                "item_name": item.get("identified_name", item.get("name")),
                "reveal_flavor": item.get("reveal_flavor", "")
            }
            
        except Exception as e:
            logger.error(f"Error identifying item: {e}")
            return {
                "success": False,
                "message": f"Error: {str(e)}"
            }
    
    @staticmethod
    async def identify_item_full(character_id: int, item_id: int, npc_id: int) -> Dict[str, Any]:
        """
        Fully identify all effects on an item at once (requires special NPC).
        
        Args:
            character_id: ID of the character
            item_id: ID of the item to identify
            npc_id: ID of the NPC performing the identification
            
        Returns:
            Dict with full identification result
        """
        try:
            # Verify NPC permissions
            # This would normally check NPC data
            npc_valid = npc_id > 0 and npc_id < 1000  # Mock validation
            
            if not npc_valid:
                return {
                    "success": False,
                    "message": "This NPC cannot fully identify items"
                }
            
            # Verify character has the item
            if HAS_INVENTORY_SYSTEM:
                inventory_item = InventoryItem.query.filter_by(
                    inventory_id=character_id,
                    item_id=item_id
                ).first()
                
                if not inventory_item:
                    return {
                        "success": False,
                        "message": "Item not found in inventory"
                    }
                
                item = inventory_item.to_dict()
            else:
                # Mock item data for testing
                item = {
                    "id": item_id,
                    "name": "Unknown Item",
                    "unknown_effects": ["Magic effect 1", "Magic effect 2"],
                    "identified_effects": []
                }
            
            # Name and flavor reveal
            reveal_item_name_and_flavor(item)
            
            # Reveal all unknown effects
            identified = item.get("identified_effects", [])
            identified += item.get("unknown_effects", [])
            item["identified_effects"] = identified
            item["unknown_effects"] = []
            
            # Generate narrative with GPT if available
            if HAS_NARRATIVE_SYSTEM:
                gpt_response = gpt_flavor_reveal_full_item(item)
            else:
                gpt_response = f"All properties of {item.get('name', 'the item')} are now revealed."
            
            # Update item in inventory
            if HAS_INVENTORY_SYSTEM:
                # Update inventory item properties
                inventory_item.properties = item
                db.session.commit()
            
            return {
                "success": True,
                "message": "All effects revealed",
                "item_name": item.get("identified_name", item.get("name")),
                "flavor": item.get("flavor_text", ""),
                "gpt_narration": gpt_response,
                "effects": identified
            }
            
        except Exception as e:
            logger.error(f"Error fully identifying item: {e}")
            return {
                "success": False,
                "message": f"Error: {str(e)}"
            } 
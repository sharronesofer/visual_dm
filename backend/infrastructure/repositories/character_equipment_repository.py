"""
Character Equipment Repository - Infrastructure Layer

Implements persistence for character equipment data.
This is a simple in-memory implementation that could be replaced with database persistence.
"""

from typing import Dict, Any, List, Optional
from uuid import UUID
from collections import defaultdict

from backend.systems.equipment.services.business_logic_service import EquipmentInstanceData
from backend.systems.equipment.services.character_equipment_service import (
    CharacterEquipmentRepository as CharacterEquipmentRepositoryProtocol
)


class CharacterEquipmentRepository:
    """In-memory implementation of character equipment repository"""
    
    def __init__(self):
        # In-memory storage: character_id -> [equipment_instances]
        self._character_equipment: Dict[UUID, List[EquipmentInstanceData]] = defaultdict(list)
        # Track equipped items: equipment_id -> slot_name
        self._equipped_slots: Dict[UUID, str] = {}
        # Track character equipment slots: character_id -> {slot_name -> equipment_id}
        self._character_slots: Dict[UUID, Dict[str, Optional[UUID]]] = defaultdict(
            lambda: {
                'main_hand': None,
                'off_hand': None, 
                'chest': None,
                'helmet': None,
                'boots': None,
                'gloves': None,
                'ring_1': None,
                'ring_2': None,
                'amulet': None,
                'belt': None
            }
        )
    
    def get_character_equipment(self, character_id: UUID) -> List[EquipmentInstanceData]:
        """Get all equipment owned by character"""
        return self._character_equipment[character_id].copy()
    
    def get_equipped_items(self, character_id: UUID) -> List[EquipmentInstanceData]:
        """Get only equipped items for character"""
        all_equipment = self._character_equipment[character_id]
        equipped_ids = set(self._character_slots[character_id].values())
        equipped_ids.discard(None)  # Remove empty slots
        
        return [eq for eq in all_equipment if eq.id in equipped_ids]
    
    def create_equipment_for_character(self, character_id: UUID, 
                                     equipment_data: EquipmentInstanceData) -> EquipmentInstanceData:
        """Create new equipment and assign to character"""
        # Ensure the equipment is owned by the character
        equipment_data.owner_id = character_id
        
        # Add to character's equipment list
        self._character_equipment[character_id].append(equipment_data)
        
        # Initialize character slots if not exists
        if character_id not in self._character_slots:
            self._character_slots[character_id] = {
                'main_hand': None,
                'off_hand': None,
                'chest': None,
                'helmet': None,
                'boots': None,
                'gloves': None,
                'ring_1': None,
                'ring_2': None,
                'amulet': None,
                'belt': None
            }
        
        return equipment_data
    
    def equip_item(self, equipment_id: UUID, slot: str) -> bool:
        """Equip item to specific slot"""
        # Find the equipment instance
        equipment_item = None
        character_id = None
        
        for char_id, equipment_list in self._character_equipment.items():
            for eq in equipment_list:
                if eq.id == equipment_id:
                    equipment_item = eq
                    character_id = char_id
                    break
            if equipment_item:
                break
        
        if not equipment_item or not character_id:
            return False
        
        # Unequip any item currently in the target slot
        current_item_in_slot = self._character_slots[character_id].get(slot)
        if current_item_in_slot:
            self._equipped_slots.pop(current_item_in_slot, None)
        
        # Unequip the item from its current slot (if any)
        current_slot = self._equipped_slots.get(equipment_id)
        if current_slot:
            self._character_slots[character_id][current_slot] = None
        
        # Equip to new slot
        self._character_slots[character_id][slot] = equipment_id
        self._equipped_slots[equipment_id] = slot
        
        return True
    
    def unequip_item(self, equipment_id: UUID) -> bool:
        """Unequip item to inventory"""
        # Find the current slot
        current_slot = self._equipped_slots.get(equipment_id)
        if not current_slot:
            return True  # Already unequipped
        
        # Find the character
        character_id = None
        for char_id, equipment_list in self._character_equipment.items():
            for eq in equipment_list:
                if eq.id == equipment_id:
                    character_id = char_id
                    break
            if character_id:
                break
        
        if not character_id:
            return False
        
        # Remove from slot
        self._character_slots[character_id][current_slot] = None
        self._equipped_slots.pop(equipment_id, None)
        
        return True
    
    def get_equipment_by_id(self, equipment_id: UUID) -> Optional[EquipmentInstanceData]:
        """Get specific equipment instance by ID"""
        for equipment_list in self._character_equipment.values():
            for eq in equipment_list:
                if eq.id == equipment_id:
                    return eq
        return None
    
    def update_equipment(self, equipment_data: EquipmentInstanceData) -> bool:
        """Update existing equipment instance"""
        for character_id, equipment_list in self._character_equipment.items():
            for i, eq in enumerate(equipment_list):
                if eq.id == equipment_data.id:
                    # Replace the equipment instance
                    self._character_equipment[character_id][i] = equipment_data
                    return True
        return False
    
    def remove_equipment(self, equipment_id: UUID) -> bool:
        """Remove equipment instance completely"""
        # Unequip first if equipped
        self.unequip_item(equipment_id)
        
        # Remove from character's equipment list
        for character_id, equipment_list in self._character_equipment.items():
            for i, eq in enumerate(equipment_list):
                if eq.id == equipment_id:
                    self._character_equipment[character_id].pop(i)
                    return True
        
        return False
    
    def get_character_equipped_slots(self, character_id: UUID) -> Dict[str, Optional[UUID]]:
        """Get character's current equipment slot assignments"""
        return self._character_slots[character_id].copy()
    
    def get_item_equipped_slot(self, equipment_id: UUID) -> Optional[str]:
        """Get the slot where an item is currently equipped"""
        return self._equipped_slots.get(equipment_id)
    
    def transfer_equipment(self, equipment_id: UUID, new_owner_id: UUID) -> bool:
        """Transfer equipment to a different character"""
        # Find and remove from current owner
        equipment_item = None
        old_owner_id = None
        
        for character_id, equipment_list in self._character_equipment.items():
            for i, eq in enumerate(equipment_list):
                if eq.id == equipment_id:
                    equipment_item = self._character_equipment[character_id].pop(i)
                    old_owner_id = character_id
                    break
            if equipment_item:
                break
        
        if not equipment_item:
            return False
        
        # Unequip if currently equipped
        if old_owner_id and equipment_id in self._equipped_slots:
            current_slot = self._equipped_slots[equipment_id]
            self._character_slots[old_owner_id][current_slot] = None
            self._equipped_slots.pop(equipment_id)
        
        # Add to new owner
        equipment_item.owner_id = new_owner_id
        self._character_equipment[new_owner_id].append(equipment_item)
        
        return True
    
    def get_all_equipment_stats(self) -> Dict[str, Any]:
        """Get statistics about all equipment in the system"""
        total_items = sum(len(eq_list) for eq_list in self._character_equipment.values())
        total_characters = len(self._character_equipment)
        total_equipped = len(self._equipped_slots)
        
        return {
            'total_equipment_instances': total_items,
            'characters_with_equipment': total_characters,
            'total_equipped_items': total_equipped,
            'total_unequipped_items': total_items - total_equipped
        }
    
    def clear_character_equipment(self, character_id: UUID) -> bool:
        """Remove all equipment for a character (for testing/cleanup)"""
        if character_id not in self._character_equipment:
            return False
        
        # Unequip all items first
        equipment_list = self._character_equipment[character_id]
        for eq in equipment_list:
            self.unequip_item(eq.id)
        
        # Clear equipment list
        self._character_equipment[character_id].clear()
        
        return True


# Factory function for dependency injection
def create_character_equipment_repository() -> CharacterEquipmentRepository:
    """Create a character equipment repository instance"""
    return CharacterEquipmentRepository() 
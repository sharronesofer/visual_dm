"""
Equipment Database Repository - SQLAlchemy Implementation

Replaces the in-memory repository with actual database persistence.
Implements the CharacterEquipmentRepository protocol using SQLAlchemy.
"""

from typing import Dict, Any, List, Optional
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, desc

from backend.systems.equipment.services.business_logic_service import EquipmentInstanceData
from backend.systems.equipment.services.character_equipment_service import (
    CharacterEquipmentRepository as CharacterEquipmentRepositoryProtocol
)
from backend.infrastructure.database.models.equipment_models import (
    EquipmentInstance, EquipmentTemplate, CharacterEquipmentSlot, 
    MagicalEffect, EquipmentMaintenanceRecord, equipment_effects_association
)


class EquipmentDatabaseRepository:
    """SQLAlchemy-based implementation of character equipment repository"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def get_character_equipment(self, character_id: UUID) -> List[EquipmentInstanceData]:
        """Get all equipment owned by character"""
        # Query with eager loading to avoid N+1 queries
        equipment_instances = (
            self.db.query(EquipmentInstance)
            .options(joinedload(EquipmentInstance.template))
            .options(joinedload(EquipmentInstance.magical_effects))
            .filter(EquipmentInstance.owner_id == character_id)
            .all()
        )
        
        return [self._convert_to_business_model(eq) for eq in equipment_instances]
    
    def get_equipped_items(self, character_id: UUID) -> List[EquipmentInstanceData]:
        """Get only equipped items for character"""
        equipped_instances = (
            self.db.query(EquipmentInstance)
            .options(joinedload(EquipmentInstance.template))
            .options(joinedload(EquipmentInstance.magical_effects))
            .filter(
                and_(
                    EquipmentInstance.owner_id == character_id,
                    EquipmentInstance.is_equipped == True
                )
            )
            .all()
        )
        
        return [self._convert_to_business_model(eq) for eq in equipped_instances]
    
    def create_equipment_for_character(self, character_id: UUID, 
                                     equipment_data: EquipmentInstanceData) -> EquipmentInstanceData:
        """Create new equipment and assign to character"""
        # Create database instance
        db_equipment = EquipmentInstance(
            id=equipment_data.id,
            template_id=equipment_data.template_id,
            owner_id=character_id,
            quality_tier=equipment_data.quality_tier,
            custom_name=equipment_data.custom_name,
            durability=equipment_data.durability,
            max_durability=equipment_data.durability,  # Set max to current initially
            creation_date=equipment_data.creation_date or datetime.utcnow(),
            last_used=equipment_data.last_used,
            stat_modifiers={}  # Instance-specific modifications
        )
        
        # Handle magical effects
        if equipment_data.magical_effects:
            self._attach_magical_effects(db_equipment, equipment_data.magical_effects)
        
        # Initialize character equipment slots if needed
        self._ensure_character_slots_exist(character_id)
        
        # Save to database
        self.db.add(db_equipment)
        self.db.commit()
        self.db.refresh(db_equipment)
        
        return self._convert_to_business_model(db_equipment)
    
    def equip_item(self, equipment_id: UUID, slot: str) -> bool:
        """Equip item to specific slot"""
        try:
            # Get the equipment instance
            equipment = (
                self.db.query(EquipmentInstance)
                .filter(EquipmentInstance.id == equipment_id)
                .first()
            )
            
            if not equipment:
                return False
            
            character_id = equipment.owner_id
            
            # Check if slot exists for character
            slot_assignment = (
                self.db.query(CharacterEquipmentSlot)
                .filter(
                    and_(
                        CharacterEquipmentSlot.character_id == character_id,
                        CharacterEquipmentSlot.slot_name == slot
                    )
                )
                .first()
            )
            
            if not slot_assignment:
                # Create slot if it doesn't exist
                slot_assignment = CharacterEquipmentSlot(
                    character_id=character_id,
                    slot_name=slot
                )
                self.db.add(slot_assignment)
            
            # Unequip any item currently in the target slot
            if slot_assignment.equipment_id:
                self._unequip_item_by_id(slot_assignment.equipment_id)
            
            # Unequip the item from its current slot (if any)
            current_slot = (
                self.db.query(CharacterEquipmentSlot)
                .filter(CharacterEquipmentSlot.equipment_id == equipment_id)
                .first()
            )
            if current_slot:
                current_slot.equipment_id = None
                current_slot.equipped_at = None
            
            # Equip to new slot
            slot_assignment.equipment_id = equipment_id
            slot_assignment.equipped_at = datetime.utcnow()
            
            # Update equipment instance
            equipment.is_equipped = True
            equipment.equipped_slot = slot
            
            self.db.commit()
            return True
            
        except Exception as e:
            self.db.rollback()
            raise e
    
    def unequip_item(self, equipment_id: UUID) -> bool:
        """Unequip item to inventory"""
        try:
            return self._unequip_item_by_id(equipment_id)
        except Exception as e:
            self.db.rollback()
            raise e
    
    def _unequip_item_by_id(self, equipment_id: UUID) -> bool:
        """Internal method to unequip item"""
        # Find the slot assignment
        slot_assignment = (
            self.db.query(CharacterEquipmentSlot)
            .filter(CharacterEquipmentSlot.equipment_id == equipment_id)
            .first()
        )
        
        if slot_assignment:
            slot_assignment.equipment_id = None
            slot_assignment.equipped_at = None
        
        # Update equipment instance
        equipment = (
            self.db.query(EquipmentInstance)
            .filter(EquipmentInstance.id == equipment_id)
            .first()
        )
        
        if equipment:
            equipment.is_equipped = False
            equipment.equipped_slot = None
        
        self.db.commit()
        return True
    
    def get_equipment_by_id(self, equipment_id: UUID) -> Optional[EquipmentInstanceData]:
        """Get specific equipment instance by ID"""
        equipment = (
            self.db.query(EquipmentInstance)
            .options(joinedload(EquipmentInstance.template))
            .options(joinedload(EquipmentInstance.magical_effects))
            .filter(EquipmentInstance.id == equipment_id)
            .first()
        )
        
        if equipment:
            return self._convert_to_business_model(equipment)
        return None
    
    def update_equipment(self, equipment_data: EquipmentInstanceData) -> bool:
        """Update existing equipment instance"""
        try:
            equipment = (
                self.db.query(EquipmentInstance)
                .filter(EquipmentInstance.id == equipment_data.id)
                .first()
            )
            
            if not equipment:
                return False
            
            # Update fields
            equipment.quality_tier = equipment_data.quality_tier
            equipment.custom_name = equipment_data.custom_name
            equipment.durability = equipment_data.durability
            equipment.last_used = equipment_data.last_used
            
            # Update magical effects if changed
            if equipment_data.magical_effects:
                equipment.magical_effects.clear()
                self._attach_magical_effects(equipment, equipment_data.magical_effects)
            
            self.db.commit()
            return True
            
        except Exception as e:
            self.db.rollback()
            raise e
    
    def remove_equipment(self, equipment_id: UUID) -> bool:
        """Remove equipment instance completely"""
        try:
            # Unequip first if equipped
            self._unequip_item_by_id(equipment_id)
            
            # Remove from database
            equipment = (
                self.db.query(EquipmentInstance)
                .filter(EquipmentInstance.id == equipment_id)
                .first()
            )
            
            if equipment:
                self.db.delete(equipment)
                self.db.commit()
                return True
            
            return False
            
        except Exception as e:
            self.db.rollback()
            raise e
    
    def get_character_equipped_slots(self, character_id: UUID) -> Dict[str, Optional[UUID]]:
        """Get character's current equipment slot assignments"""
        slot_assignments = (
            self.db.query(CharacterEquipmentSlot)
            .filter(CharacterEquipmentSlot.character_id == character_id)
            .all()
        )
        
        # Build slots dictionary
        slots = {
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
        
        for assignment in slot_assignments:
            slots[assignment.slot_name] = assignment.equipment_id
        
        return slots
    
    def get_item_equipped_slot(self, equipment_id: UUID) -> Optional[str]:
        """Get the slot where an item is currently equipped"""
        slot_assignment = (
            self.db.query(CharacterEquipmentSlot)
            .filter(CharacterEquipmentSlot.equipment_id == equipment_id)
            .first()
        )
        
        return slot_assignment.slot_name if slot_assignment else None
    
    def transfer_equipment(self, equipment_id: UUID, new_owner_id: UUID) -> bool:
        """Transfer equipment to a different character"""
        try:
            # Unequip first if equipped
            self._unequip_item_by_id(equipment_id)
            
            # Update owner
            equipment = (
                self.db.query(EquipmentInstance)
                .filter(EquipmentInstance.id == equipment_id)
                .first()
            )
            
            if equipment:
                equipment.owner_id = new_owner_id
                self.db.commit()
                return True
            
            return False
            
        except Exception as e:
            self.db.rollback()
            raise e
    
    def get_all_equipment_stats(self) -> Dict[str, Any]:
        """Get statistics about all equipment in the system"""
        # Count total equipment instances
        total_items = self.db.query(EquipmentInstance).count()
        
        # Count characters with equipment
        characters_with_equipment = (
            self.db.query(EquipmentInstance.owner_id)
            .distinct()
            .count()
        )
        
        # Count equipped items
        total_equipped = (
            self.db.query(EquipmentInstance)
            .filter(EquipmentInstance.is_equipped == True)
            .count()
        )
        
        return {
            'total_equipment_instances': total_items,
            'characters_with_equipment': characters_with_equipment,
            'total_equipped_items': total_equipped,
            'total_unequipped_items': total_items - total_equipped
        }
    
    def clear_character_equipment(self, character_id: UUID) -> bool:
        """Remove all equipment for a character (for testing/cleanup)"""
        try:
            # Get all character equipment
            equipment_instances = (
                self.db.query(EquipmentInstance)
                .filter(EquipmentInstance.owner_id == character_id)
                .all()
            )
            
            # Unequip and remove all items
            for equipment in equipment_instances:
                self._unequip_item_by_id(equipment.id)
                self.db.delete(equipment)
            
            self.db.commit()
            return True
            
        except Exception as e:
            self.db.rollback()
            raise e
    
    def record_durability_change(self, equipment_id: UUID, event_type: str, 
                               durability_before: float, durability_after: float,
                               cause: str = None, event_data: Dict[str, Any] = None) -> bool:
        """Record durability change in maintenance history"""
        try:
            maintenance_record = EquipmentMaintenanceRecord(
                equipment_id=equipment_id,
                event_type=event_type,
                durability_before=durability_before,
                durability_after=durability_after,
                durability_change=durability_after - durability_before,
                cause=cause,
                event_data=event_data or {}
            )
            
            self.db.add(maintenance_record)
            self.db.commit()
            return True
            
        except Exception as e:
            self.db.rollback()
            raise e
    
    # Helper methods
    def _convert_to_business_model(self, db_equipment: EquipmentInstance) -> EquipmentInstanceData:
        """Convert database model to business domain model"""
        # Convert magical effects
        magical_effects = []
        for effect in db_equipment.magical_effects:
            # Get power level from association table
            effect_data = {
                'effect_type': effect.effect_type,
                'power_level': 50,  # Default, should query association table
                'description': effect.description,
                'stat_name': effect.parameters.get('stat_name') if effect.parameters else None
            }
            magical_effects.append(effect_data)
        
        return EquipmentInstanceData(
            id=db_equipment.id,
            template_id=db_equipment.template_id,
            owner_id=db_equipment.owner_id,
            quality_tier=db_equipment.quality_tier,
            magical_effects=magical_effects,
            durability=db_equipment.durability,
            custom_name=db_equipment.custom_name,
            creation_date=db_equipment.creation_date,
            last_used=db_equipment.last_used
        )
    
    def _attach_magical_effects(self, equipment: EquipmentInstance, magical_effects: List[Dict[str, Any]]):
        """Attach magical effects to equipment instance"""
        for effect_data in magical_effects:
            # Find or create magical effect
            effect_type = effect_data.get('effect_type')
            effect = (
                self.db.query(MagicalEffect)
                .filter(MagicalEffect.effect_type == effect_type)
                .first()
            )
            
            if not effect:
                # Create new effect if it doesn't exist
                effect = MagicalEffect(
                    effect_id=f"{effect_type}_{datetime.utcnow().timestamp()}",
                    name=effect_data.get('description', effect_type),
                    description=effect_data.get('description', ''),
                    effect_type=effect_type,
                    parameters=effect_data
                )
                self.db.add(effect)
                self.db.flush()  # Get the ID
            
            equipment.magical_effects.append(effect)
    
    def _ensure_character_slots_exist(self, character_id: UUID):
        """Ensure character has all standard equipment slots"""
        standard_slots = ['main_hand', 'off_hand', 'chest', 'helmet', 'boots', 
                         'gloves', 'ring_1', 'ring_2', 'amulet', 'belt']
        
        existing_slots = (
            self.db.query(CharacterEquipmentSlot.slot_name)
            .filter(CharacterEquipmentSlot.character_id == character_id)
            .all()
        )
        existing_slot_names = {slot[0] for slot in existing_slots}
        
        for slot_name in standard_slots:
            if slot_name not in existing_slot_names:
                slot = CharacterEquipmentSlot(
                    character_id=character_id,
                    slot_name=slot_name
                )
                self.db.add(slot)
        
        self.db.commit()


# Factory function for dependency injection
def create_equipment_database_repository(db_session: Session) -> EquipmentDatabaseRepository:
    """Create an equipment database repository instance"""
    return EquipmentDatabaseRepository(db_session) 
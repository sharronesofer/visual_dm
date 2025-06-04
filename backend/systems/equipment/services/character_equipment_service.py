"""
Character Equipment Service - Character-Equipment Integration

This service manages the integration between characters and their unique equipment.
Handles the complete equipment lifecycle for character ownership according to user requirements:
- Unique equipment instances with base type + quality + magical effects
- Character ownership tracking
- Equipment slot management  
- Combat stat integration
"""

from typing import Dict, Any, List, Optional, Tuple, Protocol
from uuid import UUID, uuid4
from datetime import datetime
from dataclasses import dataclass

from .business_logic_service import (
    EquipmentBusinessLogicService, 
    EquipmentInstanceData, 
    EquipmentBaseTemplate,
    QualityTierData
)

# Domain Models for Character Integration
@dataclass
class CharacterEquipmentSlot:
    """Character equipment slot with equipped item"""
    slot_name: str  # main_hand, off_hand, chest, helmet, etc.
    equipped_item_id: Optional[UUID] = None
    allows_item_types: List[str] = None  # weapon, armor, accessory
    
    def is_occupied(self) -> bool:
        return self.equipped_item_id is not None
    
    def can_equip(self, item_type: str) -> bool:
        if not self.allows_item_types:
            return True
        return item_type in self.allows_item_types


@dataclass
class CharacterEquipmentLoadout:
    """Complete character equipment configuration"""
    character_id: UUID
    equipment_slots: Dict[str, CharacterEquipmentSlot]
    equipped_items: List[EquipmentInstanceData]
    inventory_items: List[EquipmentInstanceData]
    total_stat_bonuses: Dict[str, int]
    
    def get_equipped_count(self) -> int:
        return len(self.equipped_items)
    
    def get_total_items(self) -> int:
        return len(self.equipped_items) + len(self.inventory_items)
    
    def get_total_value(self) -> int:
        """Calculate total value of all character equipment"""
        total = 0
        for item in self.equipped_items + self.inventory_items:
            # Would need to calculate from base template + quality + effects
            total += 100  # Placeholder
        return total


# Repository Protocol for Character Equipment
class CharacterEquipmentRepository(Protocol):
    """Repository interface for character equipment data access"""
    
    def get_character_equipment(self, character_id: UUID) -> List[EquipmentInstanceData]:
        """Get all equipment owned by character"""
        ...
    
    def get_equipped_items(self, character_id: UUID) -> List[EquipmentInstanceData]:
        """Get only equipped items for character"""
        ...
    
    def create_equipment_for_character(self, character_id: UUID, 
                                     equipment_data: EquipmentInstanceData) -> EquipmentInstanceData:
        """Create new equipment and assign to character"""
        ...
    
    def equip_item(self, equipment_id: UUID, slot: str) -> bool:
        """Equip item to specific slot"""
        ...
    
    def unequip_item(self, equipment_id: UUID) -> bool:
        """Unequip item to inventory"""
        ...


# Template Repository Protocol
class EquipmentTemplateRepository(Protocol):
    """Repository interface for equipment template data"""
    
    def get_template(self, template_id: str) -> Optional[EquipmentBaseTemplate]:
        """Get equipment base template"""
        ...
    
    def get_quality_tier(self, tier: str) -> Optional[QualityTierData]:
        """Get quality tier configuration"""
        ...
    
    def get_available_magical_effects(self) -> List[Dict[str, Any]]:
        """Get available magical effects for equipment"""
        ...


class CharacterEquipmentService:
    """Service for managing character equipment integration"""
    
    def __init__(self, 
                 business_logic: EquipmentBusinessLogicService,
                 equipment_repo: CharacterEquipmentRepository,
                 template_repo: EquipmentTemplateRepository):
        self.business_logic = business_logic
        self.equipment_repo = equipment_repo
        self.template_repo = template_repo
        
        # Standard equipment slots for characters - 12 total per Bible specification
        self.STANDARD_EQUIPMENT_SLOTS = {
            'main_hand': CharacterEquipmentSlot('main_hand', allows_item_types=['weapon']),
            'off_hand': CharacterEquipmentSlot('off_hand', allows_item_types=['weapon', 'shield']),
            'chest': CharacterEquipmentSlot('chest', allows_item_types=['armor']),
            'pants': CharacterEquipmentSlot('pants', allows_item_types=['armor']),
            'boots': CharacterEquipmentSlot('boots', allows_item_types=['armor']),
            'gloves': CharacterEquipmentSlot('gloves', allows_item_types=['armor']),
            'hat': CharacterEquipmentSlot('hat', allows_item_types=['armor']),
            'ring_1': CharacterEquipmentSlot('ring_1', allows_item_types=['accessory']),
            'ring_2': CharacterEquipmentSlot('ring_2', allows_item_types=['accessory']),
            'amulet': CharacterEquipmentSlot('amulet', allows_item_types=['accessory']),
            'earring_1': CharacterEquipmentSlot('earring_1', allows_item_types=['accessory']),
            'earring_2': CharacterEquipmentSlot('earring_2', allows_item_types=['accessory'])
        }
    
    def create_unique_equipment_for_character(self, 
                                            character_id: UUID, 
                                            template_id: str,
                                            quality_tier: str = 'basic',
                                            magical_effects: List[Dict[str, Any]] = None,
                                            custom_name: Optional[str] = None) -> EquipmentInstanceData:
        """
        Create a unique equipment instance for a character according to user requirements.
        
        Each equipment instance is unique due to:
        - Base type (shared stats like damage, crit, reach)
        - Quality tier (basic, military, noble) 
        - 3-20+ magical effects (mostly unique per item)
        """
        if magical_effects is None:
            magical_effects = []
        
        # Business validation
        validation = self.business_logic.validate_equipment_creation(
            template_id, quality_tier, magical_effects
        )
        if not validation['valid']:
            raise ValueError(f"Equipment creation failed: {validation['errors']}")
        
        # Get base template to determine display name
        template = self.template_repo.get_template(template_id)
        if not template:
            raise ValueError(f"Template not found: {template_id}")
        
        # Generate display name if not provided
        if not custom_name:
            custom_name = self.business_logic.generate_equipment_display_name(
                template.name, quality_tier, magical_effects
            )
        
        # Create unique equipment instance
        equipment_data = EquipmentInstanceData(
            id=uuid4(),
            template_id=template_id,
            owner_id=character_id,
            quality_tier=quality_tier,
            magical_effects=magical_effects,
            durability=100.0,
            custom_name=custom_name,
            creation_date=datetime.utcnow()
        )
        
        # Persist via repository
        return self.equipment_repo.create_equipment_for_character(character_id, equipment_data)
    
    def get_character_equipment_loadout(self, character_id: UUID) -> CharacterEquipmentLoadout:
        """
        Get complete equipment loadout for character including equipped and inventory items.
        Makes it obvious what the character has as per user requirement.
        """
        all_equipment = self.equipment_repo.get_character_equipment(character_id)
        equipped_items = [eq for eq in all_equipment if eq.id in self._get_equipped_item_ids(character_id)]
        inventory_items = [eq for eq in all_equipment if eq.id not in self._get_equipped_item_ids(character_id)]
        
        # Build equipment slots with current assignments
        equipment_slots = self.STANDARD_EQUIPMENT_SLOTS.copy()
        for item in equipped_items:
            slot_name = self._get_item_slot(item.id)
            if slot_name and slot_name in equipment_slots:
                equipment_slots[slot_name].equipped_item_id = item.id
        
        # Calculate total stat bonuses from all equipped items
        total_stats = self._calculate_total_stat_bonuses(equipped_items)
        
        return CharacterEquipmentLoadout(
            character_id=character_id,
            equipment_slots=equipment_slots,
            equipped_items=equipped_items,
            inventory_items=inventory_items,
            total_stat_bonuses=total_stats
        )
    
    def equip_item_to_character(self, character_id: UUID, equipment_id: UUID, 
                              target_slot: str) -> Dict[str, Any]:
        """
        Equip an item to a specific character slot with business rule validation.
        """
        # Get character's equipment
        all_equipment = self.equipment_repo.get_character_equipment(character_id)
        equipment_item = next((eq for eq in all_equipment if eq.id == equipment_id), None)
        
        if not equipment_item:
            return {'success': False, 'error': 'Equipment not found or not owned by character'}
        
        # Validate equipment is functional
        if not self.business_logic.is_equipment_functional(equipment_item.durability):
            return {'success': False, 'error': 'Cannot equip broken equipment'}
        
        # Get equipment template to check slot compatibility
        template = self.template_repo.get_template(equipment_item.template_id)
        if not template:
            return {'success': False, 'error': 'Equipment template not found'}
        
        # Validate slot compatibility
        slot_config = self.STANDARD_EQUIPMENT_SLOTS.get(target_slot)
        if not slot_config:
            return {'success': False, 'error': f'Invalid equipment slot: {target_slot}'}
        
        if not slot_config.can_equip(template.item_type):
            return {'success': False, 'error': f'Cannot equip {template.item_type} to {target_slot}'}
        
        # Check if slot is already occupied
        current_loadout = self.get_character_equipment_loadout(character_id)
        if current_loadout.equipment_slots[target_slot].is_occupied():
            return {'success': False, 'error': f'Slot {target_slot} is already occupied'}
        
        # Perform the equip operation
        success = self.equipment_repo.equip_item(equipment_id, target_slot)
        
        if success:
            return {
                'success': True, 
                'message': f'Equipped {equipment_item.custom_name or template.name} to {target_slot}'
            }
        else:
            return {'success': False, 'error': 'Failed to equip item due to repository error'}
    
    def unequip_item_from_character(self, character_id: UUID, equipment_id: UUID) -> Dict[str, Any]:
        """Unequip an item from character, moving it to inventory."""
        # Verify ownership
        all_equipment = self.equipment_repo.get_character_equipment(character_id)
        equipment_item = next((eq for eq in all_equipment if eq.id == equipment_id), None)
        
        if not equipment_item:
            return {'success': False, 'error': 'Equipment not found or not owned by character'}
        
        success = self.equipment_repo.unequip_item(equipment_id)
        
        if success:
            return {
                'success': True,
                'message': f'Unequipped {equipment_item.custom_name} to inventory'
            }
        else:
            return {'success': False, 'error': 'Failed to unequip item'}
    
    def get_character_combat_stats(self, character_id: UUID) -> Dict[str, int]:
        """
        Calculate character's combat stats from equipped equipment.
        This provides the integration with combat system as requested.
        """
        loadout = self.get_character_equipment_loadout(character_id)
        total_stats = {}
        
        for equipment_item in loadout.equipped_items:
            # Get base template stats
            template = self.template_repo.get_template(equipment_item.template_id)
            if not template:
                continue
            
            # Apply durability penalties  
            penalty = self.business_logic.calculate_stat_penalties(equipment_item.durability)
            
            # Add base stats with penalties
            for stat, value in template.base_stats.items():
                effective_value = int(value * (1.0 - penalty))
                total_stats[stat] = total_stats.get(stat, 0) + effective_value
            
            # Add magical effect bonuses
            for effect in equipment_item.magical_effects:
                if effect.get('effect_type') == 'stat_bonus':
                    stat_name = effect.get('stat_name')
                    bonus = effect.get('power_level', 0)
                    if stat_name:
                        total_stats[stat_name] = total_stats.get(stat_name, 0) + bonus
        
        return total_stats
    
    def get_equipment_repair_recommendations(self, character_id: UUID) -> List[Dict[str, Any]]:
        """Get repair recommendations for character's equipment."""
        all_equipment = self.equipment_repo.get_character_equipment(character_id)
        return self.business_logic.calculate_repair_urgency(all_equipment)
    
    def generate_magical_effects_for_equipment(self, template_id: str, quality_tier: str,
                                             effect_count: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Generate random magical effects for equipment based on user requirements.
        Equipment can have 3-20+ effects that make it unique.
        """
        if effect_count is None:
            # Generate random count based on quality tier
            quality_ranges = {
                'basic': (3, 8),
                'military': (5, 12), 
                'noble': (8, 20)
            }
            min_effects, max_effects = quality_ranges.get(quality_tier, (3, 8))
            effect_count = min_effects + (max_effects - min_effects) // 2
        
        # Get available magical effects
        available_effects = self.template_repo.get_available_magical_effects()
        if not available_effects:
            return []  # No effects available
        
        # Generate unique combination of effects
        import random
        selected_effects = random.sample(available_effects, min(effect_count, len(available_effects)))
        
        # Add power levels based on quality tier
        quality_power_ranges = {
            'basic': (30, 75),
            'military': (50, 90),
            'noble': (70, 100)
        }
        min_power, max_power = quality_power_ranges.get(quality_tier, (30, 75))
        
        magical_effects = []
        for effect_template in selected_effects:
            power_level = random.randint(min_power, max_power)
            magical_effects.append({
                'effect_type': effect_template.get('effect_type'),
                'power_level': power_level,
                'description': effect_template.get('description'),
                'stat_name': effect_template.get('stat_name'),
                'bonus_amount': effect_template.get('bonus_amount', power_level // 10)
            })
        
        return magical_effects
    
    # Helper methods
    def _get_equipped_item_ids(self, character_id: UUID) -> List[UUID]:
        """Get IDs of currently equipped items for character."""
        equipped_items = self.equipment_repo.get_equipped_items(character_id)
        return [item.id for item in equipped_items]
    
    def _get_item_slot(self, equipment_id: UUID) -> Optional[str]:
        """Get the slot where an item is currently equipped."""
        # This now uses the actual repository method
        if hasattr(self.equipment_repo, 'get_item_equipped_slot'):
            return self.equipment_repo.get_item_equipped_slot(equipment_id)
        return None
    
    def _calculate_total_stat_bonuses(self, equipped_items: List[EquipmentInstanceData]) -> Dict[str, int]:
        """Calculate total stat bonuses from all equipped items."""
        total_stats = {}
        
        for item in equipped_items:
            template = self.template_repo.get_template(item.template_id)
            if template:
                # Add base stats with durability penalties
                penalty = self.business_logic.calculate_stat_penalties(item.durability)
                for stat, value in template.base_stats.items():
                    effective_value = int(value * (1.0 - penalty))
                    total_stats[stat] = total_stats.get(stat, 0) + effective_value
                
                # Add magical effect bonuses
                for effect in item.magical_effects:
                    if effect.get('effect_type') == 'stat_bonus':
                        stat_name = effect.get('stat_name')
                        bonus = effect.get('bonus_amount', 0)
                        if stat_name:
                            total_stats[stat_name] = total_stats.get(stat_name, 0) + bonus
        
        return total_stats


def create_character_equipment_service(business_logic: EquipmentBusinessLogicService,
                                     equipment_repo: CharacterEquipmentRepository,
                                     template_repo: EquipmentTemplateRepository) -> CharacterEquipmentService:
    """Factory function to create character equipment service"""
    return CharacterEquipmentService(business_logic, equipment_repo, template_repo) 
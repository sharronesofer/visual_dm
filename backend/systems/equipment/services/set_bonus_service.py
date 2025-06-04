"""
Equipment Set Bonus Service

This service manages equipment set bonuses according to Development Bible standards.
Integrates with the business logic service to provide set bonus calculations.

Key Business Rules (per user requirements):
- Equipment sets are mandatory for all equipment types
- 12 total equipment slots: 2 rings, 1 amulet, 1 boots, 1 gloves, 1 weapon, 
  1 off-hand, 2 earrings, 1 hat, 1 pants, 1 chest
- Equipment below 30% durability doesn't count for set bonuses
- Multiple sets can be active simultaneously
- Set bonuses grow based on number of pieces equipped
"""

from typing import Dict, Any, List, Optional, Tuple
from uuid import UUID
import logging

from backend.systems.equipment.services.business_logic_service import (
    EquipmentBusinessLogicService, EquipmentInstanceData, EquipmentSetData,
    EquipmentSlot
)

logger = logging.getLogger(__name__)


class SetBonusService:
    """Service for managing equipment set bonuses"""
    
    def __init__(self):
        self.business_service = EquipmentBusinessLogicService()
        # Cache for set data to avoid repeated lookups
        self._set_cache = {}
    
    def calculate_character_set_bonuses(self, character_id: UUID, 
                                     equipped_items: List[EquipmentInstanceData],
                                     available_sets: List[EquipmentSetData]) -> Dict[str, Any]:
        """
        Calculate all active set bonuses for a character based on equipped items
        
        Args:
            character_id: Character UUID
            equipped_items: List of equipped equipment instances  
            available_sets: List of all available equipment sets
            
        Returns:
            Dictionary with active set bonuses and details
        """
        try:
            # Validate character ownership
            ownership_result = self.business_service.validate_character_ownership(
                character_id, equipped_items
            )
            
            if not ownership_result['valid']:
                logger.warning(f"Character {character_id} ownership validation failed: {ownership_result['issues']}")
                return {
                    'character_id': str(character_id),
                    'active_sets': {},
                    'total_sets_active': 0,
                    'error': 'Invalid character ownership',
                    'details': ownership_result['issues']
                }
            
            # Calculate set bonuses using business logic
            set_bonus_result = self.business_service.calculate_set_bonuses(
                equipped_items, available_sets
            )
            
            # Add character context
            set_bonus_result['character_id'] = str(character_id)
            set_bonus_result['equipment_count'] = len(equipped_items)
            set_bonus_result['functional_equipment_count'] = len([
                item for item in equipped_items 
                if self.business_service.is_equipment_functional(item.durability)
            ])
            set_bonus_result['set_bonus_eligible_count'] = len([
                item for item in equipped_items 
                if item.counts_for_set_bonus()
            ])
            
            return set_bonus_result
            
        except Exception as e:
            logger.error(f"Error calculating set bonuses for character {character_id}: {e}")
            return {
                'character_id': str(character_id),
                'active_sets': {},
                'total_sets_active': 0,
                'error': str(e)
            }
    
    def apply_set_bonuses_to_character_stats(self, base_stats: Dict[str, Any],
                                           set_bonus_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply calculated set bonuses to character stats
        
        Args:
            base_stats: Character's base statistics
            set_bonus_data: Set bonus data from calculate_character_set_bonuses
            
        Returns:
            Updated stats with set bonuses applied
        """
        try:
            return self.business_service.apply_set_bonuses_to_stats(
                base_stats, set_bonus_data
            )
        except Exception as e:
            logger.error(f"Error applying set bonuses to stats: {e}")
            # Return original stats if error occurs
            stats_copy = base_stats.copy()
            stats_copy['set_bonus_error'] = str(e)
            return stats_copy
    
    def get_set_bonus_preview(self, current_equipment: List[EquipmentInstanceData],
                            new_equipment: EquipmentInstanceData,
                            available_sets: List[EquipmentSetData]) -> Dict[str, Any]:
        """
        Preview what set bonuses would be active if new equipment was equipped
        
        Args:
            current_equipment: Currently equipped items
            new_equipment: New equipment piece to preview
            available_sets: Available equipment sets
            
        Returns:
            Comparison of current vs potential set bonuses
        """
        try:
            # Calculate current set bonuses
            current_bonuses = self.business_service.calculate_set_bonuses(
                current_equipment, available_sets
            )
            
            # Calculate potential set bonuses with new equipment
            # Note: This would need logic to determine which slot the new equipment goes in
            # and potentially replace existing equipment
            potential_equipment = current_equipment + [new_equipment]
            potential_bonuses = self.business_service.calculate_set_bonuses(
                potential_equipment, available_sets
            )
            
            # Compare the differences
            comparison = {
                'current_sets': current_bonuses['total_sets_active'],
                'potential_sets': potential_bonuses['total_sets_active'],
                'new_equipment': {
                    'id': str(new_equipment.id),
                    'template_id': new_equipment.template_id,
                    'counts_for_set_bonus': new_equipment.counts_for_set_bonus()
                },
                'bonus_changes': [],
                'new_bonuses': [],
                'lost_bonuses': []
            }
            
            # Analyze changes in detail
            current_sets = current_bonuses.get('active_sets', {})
            potential_sets = potential_bonuses.get('active_sets', {})
            
            # Find new bonuses
            for set_id, set_info in potential_sets.items():
                if set_id not in current_sets:
                    comparison['new_bonuses'].append({
                        'set': set_info['name'],
                        'equipped_count': set_info['equipped_count'],
                        'bonuses': set_info['active_bonuses']
                    })
                elif set_info['equipped_count'] > current_sets[set_id]['equipped_count']:
                    comparison['bonus_changes'].append({
                        'set': set_info['name'],
                        'old_count': current_sets[set_id]['equipped_count'],
                        'new_count': set_info['equipped_count'],
                        'additional_bonuses': set_info['active_bonuses']
                    })
            
            # Find lost bonuses (if equipment was replaced)
            for set_id, set_info in current_sets.items():
                if set_id not in potential_sets:
                    comparison['lost_bonuses'].append({
                        'set': set_info['name'],
                        'lost_count': set_info['equipped_count'],
                        'lost_bonuses': set_info['active_bonuses']
                    })
            
            return comparison
            
        except Exception as e:
            logger.error(f"Error calculating set bonus preview: {e}")
            return {
                'error': str(e),
                'current_sets': 0,
                'potential_sets': 0
            }
    
    def get_available_equipment_slots(self) -> List[str]:
        """
        Get all available equipment slots per user requirements
        
        Returns:
            List of all 12 equipment slot names
        """
        return [slot.value for slot in self.business_service.ALL_EQUIPMENT_SLOTS]
    
    def validate_equipment_set_configuration(self, set_data: EquipmentSetData) -> Dict[str, Any]:
        """
        Validate that an equipment set configuration is valid
        
        Args:
            set_data: Equipment set data to validate
            
        Returns:
            Validation result with any errors found
        """
        errors = []
        warnings = []
        
        # Validate basic structure
        if not set_data.set_id:
            errors.append("Set ID is required")
        
        if not set_data.name:
            errors.append("Set name is required")
        
        if not set_data.equipment_slots:
            errors.append("Equipment slots list cannot be empty")
        
        # Validate equipment slots are valid
        valid_slots = set(self.business_service.ALL_EQUIPMENT_SLOTS)
        for slot in set_data.equipment_slots:
            if slot not in valid_slots:
                errors.append(f"Invalid equipment slot: {slot}")
        
        # Validate set bonuses structure
        if not set_data.set_bonuses:
            warnings.append("No set bonuses defined")
        else:
            max_pieces = len(set_data.equipment_slots)
            for piece_count in set_data.set_bonuses.keys():
                if isinstance(piece_count, str):
                    try:
                        piece_count = int(piece_count)
                    except ValueError:
                        errors.append(f"Invalid piece count key: {piece_count}")
                        continue
                
                if piece_count > max_pieces:
                    errors.append(f"Set bonus for {piece_count} pieces exceeds total set size of {max_pieces}")
                
                if piece_count < 2:
                    warnings.append(f"Set bonus for {piece_count} pieces is unusual (most sets start at 2+ pieces)")
        
        # Check for duplicate slots
        if len(set_data.equipment_slots) != len(set(set_data.equipment_slots)):
            errors.append("Duplicate equipment slots found in set")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'set_id': set_data.set_id,
            'total_pieces': len(set_data.equipment_slots)
        }
    
    def get_repair_impact_on_set_bonuses(self, character_id: UUID,
                                       equipment_to_repair: List[EquipmentInstanceData],
                                       available_sets: List[EquipmentSetData]) -> Dict[str, Any]:
        """
        Calculate how repairing equipment would affect set bonuses
        
        Args:
            character_id: Character UUID
            equipment_to_repair: Equipment items that would be repaired
            available_sets: Available equipment sets
            
        Returns:
            Analysis of set bonus changes from repairs
        """
        try:
            # Find equipment that would become set-bonus-eligible after repair
            currently_excluded = []
            would_be_included = []
            
            for item in equipment_to_repair:
                if not item.counts_for_set_bonus():
                    currently_excluded.append(item)
                    
                    # Simulate repair to above 30% durability
                    if item.durability < 30.0:
                        # Create a copy with simulated repair
                        repaired_item = EquipmentInstanceData(
                            id=item.id,
                            template_id=item.template_id,
                            owner_id=item.owner_id,
                            quality_tier=item.quality_tier,
                            magical_effects=item.magical_effects,
                            durability=max(50.0, item.durability + 30.0),  # Simulate repair
                            equipment_slot=item.equipment_slot,
                            custom_name=item.custom_name,
                            creation_date=item.creation_date,
                            last_used=item.last_used,
                            usage_count=item.usage_count
                        )
                        would_be_included.append(repaired_item)
            
            return {
                'character_id': str(character_id),
                'currently_excluded_count': len(currently_excluded),
                'would_be_included_count': len(would_be_included),
                'excluded_items': [
                    {
                        'id': str(item.id),
                        'template_id': item.template_id,
                        'durability': item.durability,
                        'custom_name': item.custom_name
                    }
                    for item in currently_excluded
                ],
                'repair_recommendations': [
                    {
                        'id': str(item.id),
                        'template_id': item.template_id,
                        'current_durability': next(
                            (orig.durability for orig in currently_excluded if orig.id == item.id),
                            0.0
                        ),
                        'after_repair_durability': item.durability,
                        'set_bonus_impact': 'Would become eligible for set bonuses'
                    }
                    for item in would_be_included
                ]
            }
            
        except Exception as e:
            logger.error(f"Error calculating repair impact on set bonuses: {e}")
            return {
                'character_id': str(character_id),
                'error': str(e)
            }


def create_set_bonus_service() -> SetBonusService:
    """Factory function to create set bonus service"""
    return SetBonusService() 
"""
Equipment Durability Integration Service

Provides a unified interface for equipment durability management across all systems.
This service acts as the central hub for all durability-related operations,
consolidating previously scattered logic from combat, time, and repair systems.
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session

from .durability_service import DurabilityService
from backend.systems.equipment.models.equipment_quality import EquipmentQuality
from backend.systems.repair.services.repair_service import RepairService

logger = logging.getLogger(__name__)

class EquipmentDurabilityIntegration:
    """
    Unified service for equipment durability management across all game systems.
    
    This service provides the single source of truth for:
    - Time-based degradation
    - Combat damage calculations  
    - Environmental wear
    - Condition-based stat penalties
    - Repair integration
    - Cross-system durability events
    """
    
    def __init__(self, db_session: Session):
        self.db = db_session
        self.logger = logger
        self.durability_service = DurabilityService(db_session)
        self.repair_service = RepairService(db_session)
    
    # ==========================================
    # UNIFIED DURABILITY PROCESSING
    # ==========================================
    
    def process_equipment_durability_update(
        self,
        character_id: str,
        time_elapsed_hours: float = 0.0,
        combat_events: List[Dict[str, Any]] = None,
        environmental_exposure: Dict[str, Any] = None,
        usage_intensity: float = 1.0
    ) -> Dict[str, Any]:
        """
        Process comprehensive durability updates for all character equipment.
        
        This is the main entry point for system-wide durability updates.
        
        Args:
            character_id: Character whose equipment to update
            time_elapsed_hours: Hours since last update
            combat_events: List of combat events affecting equipment
            environmental_exposure: Environmental conditions
            usage_intensity: Overall usage intensity multiplier
            
        Returns:
            Complete durability update results for all equipment
        """
        try:
            # Get all character equipment
            equipment_list = self._get_character_equipment(character_id)
            
            if not equipment_list:
                return {
                    "success": True,
                    "character_id": character_id,
                    "equipment_updates": [],
                    "total_equipment_processed": 0,
                    "degradation_summary": {}
                }
            
            # Calculate last update time for time-based degradation
            last_update = datetime.utcnow() - timedelta(hours=time_elapsed_hours) if time_elapsed_hours > 0 else datetime.utcnow()
            
            equipment_updates = []
            total_degradation = 0.0
            broken_equipment = []
            condition_changes = []
            
            for equipment in equipment_list:
                equipment_id = equipment['id']
                current_durability = equipment.get('current_durability', 100.0)
                quality_str = equipment.get('quality', 'basic')
                equipment_type = equipment.get('type', 'weapon')
                
                # Skip if already broken and no repair context
                if current_durability <= 0.0:
                    continue
                
                # Convert quality string to enum
                quality = EquipmentQuality(quality_str)
                
                # Prepare degradation factors
                degradation_factors = {
                    'usage_intensity': usage_intensity,
                    'environment': environmental_exposure.get('environment', 'normal') if environmental_exposure else 'normal',
                    'combat_events': self._filter_equipment_combat_events(equipment_id, combat_events or []),
                    'environmental_exposure': self._prepare_environmental_exposure(equipment_type, environmental_exposure)
                }
                
                # Process comprehensive degradation
                degradation_result = self.durability_service.process_comprehensive_degradation(
                    equipment_id=equipment_id,
                    current_durability=current_durability,
                    quality=quality,
                    last_update=last_update,
                    degradation_factors=degradation_factors
                )
                
                # Track statistics
                total_degradation += degradation_result['total_degradation']
                
                # Track broken equipment
                if degradation_result['became_broken']:
                    broken_equipment.append({
                        'equipment_id': equipment_id,
                        'name': equipment.get('name', 'Unknown Item'),
                        'type': equipment_type
                    })
                
                # Track condition changes
                if degradation_result['condition_changed']:
                    condition_changes.append({
                        'equipment_id': equipment_id,
                        'name': equipment.get('name', 'Unknown Item'),
                        'previous_condition': degradation_result['previous_condition']['status'],
                        'new_condition': degradation_result['new_condition']['status']
                    })
                
                # Update equipment durability in database
                self._update_equipment_durability(equipment_id, degradation_result['new_durability'])
                
                equipment_updates.append(degradation_result)
            
            # Generate summary
            degradation_summary = {
                'total_degradation': round(total_degradation, 2),
                'average_degradation': round(total_degradation / len(equipment_list), 2) if equipment_list else 0.0,
                'broken_equipment_count': len(broken_equipment),
                'condition_changes_count': len(condition_changes),
                'broken_equipment': broken_equipment,
                'condition_changes': condition_changes,
                'needs_immediate_repair': [
                    eq for eq in equipment_updates 
                    if eq.get('needs_immediate_attention', False)
                ]
            }
            
            self.logger.info(
                f"Processed durability for character {character_id}: "
                f"{len(equipment_list)} items, {total_degradation:.2f} total degradation, "
                f"{len(broken_equipment)} broken items"
            )
            
            return {
                "success": True,
                "character_id": character_id,
                "equipment_updates": equipment_updates,
                "total_equipment_processed": len(equipment_list),
                "degradation_summary": degradation_summary,
                "time_elapsed_hours": time_elapsed_hours,
                "usage_intensity": usage_intensity
            }
            
        except Exception as e:
            self.logger.error(f"Error processing durability update for character {character_id}: {e}")
            return {"success": False, "error": str(e)}
    
    # ==========================================
    # COMBAT INTEGRATION
    # ==========================================
    
    def process_combat_durability_damage(
        self,
        combat_participants: List[Dict[str, Any]],
        combat_duration_rounds: int = 1,
        combat_intensity: float = 1.0
    ) -> Dict[str, Any]:
        """
        Process durability damage for all equipment used in combat.
        
        Args:
            combat_participants: List of combat participant data
            combat_duration_rounds: Length of combat in rounds
            combat_intensity: Overall combat intensity multiplier
            
        Returns:
            Combat durability damage results
        """
        combat_updates = {}
        
        for participant in combat_participants:
            character_id = participant.get('character_id')
            if not character_id:
                continue
            
            # Extract combat events for this character
            combat_events = participant.get('combat_events', [])
            
            # Add combat duration factor
            for event in combat_events:
                event['combat_duration_factor'] = combat_duration_rounds / 10.0  # Normalize to 10-round baseline
                event['intensity'] = event.get('intensity', 1.0) * combat_intensity
            
            # Process durability update with combat focus
            update_result = self.process_equipment_durability_update(
                character_id=character_id,
                time_elapsed_hours=0.0,  # Combat is instantaneous for time purposes
                combat_events=combat_events,
                usage_intensity=combat_intensity
            )
            
            combat_updates[character_id] = update_result
        
        return {
            "combat_durability_updates": combat_updates,
            "combat_duration_rounds": combat_duration_rounds,
            "combat_intensity": combat_intensity
        }
    
    # ==========================================
    # STAT PENALTY INTEGRATION
    # ==========================================
    
    def get_equipment_effective_stats(
        self,
        equipment_id: str,
        base_stats: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Get equipment stats with durability-based penalties applied.
        
        Args:
            equipment_id: Equipment identifier
            base_stats: Base equipment statistics
            
        Returns:
            Effective stats with condition penalties
        """
        try:
            # Get current equipment durability
            equipment = self._get_equipment_details(equipment_id)
            if not equipment:
                return base_stats
            
            current_durability = equipment.get('current_durability', 100.0)
            
            # Apply condition penalties
            effective_stats = self.durability_service.apply_condition_penalties(
                base_stats=base_stats,
                durability=current_durability
            )
            
            # Add durability context
            condition_info = self.durability_service.get_condition_effects(current_durability)
            
            return {
                **effective_stats,
                '_durability_info': {
                    'current_durability': current_durability,
                    'condition': condition_info,
                    'stat_penalty_applied': condition_info['stat_penalty_multiplier']
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error getting effective stats for equipment {equipment_id}: {e}")
            return base_stats
    
    def validate_equipment_usability(
        self,
        equipment_id: str,
        action_type: str = "use"
    ) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Validate if equipment can be used for a specific action.
        
        Args:
            equipment_id: Equipment identifier
            action_type: Type of action ('equip', 'use', 'enhance', 'combat')
            
        Returns:
            Tuple of (is_usable, reason, condition_info)
        """
        try:
            equipment = self._get_equipment_details(equipment_id)
            if not equipment:
                return False, "Equipment not found", {}
            
            current_durability = equipment.get('current_durability', 100.0)
            
            # Check usability
            is_valid, reason = self.durability_service.validate_equipment_condition(
                durability=current_durability,
                action=action_type
            )
            
            # Get condition information
            condition_info = self.durability_service.get_condition_effects(current_durability)
            
            return is_valid, reason, condition_info
            
        except Exception as e:
            self.logger.error(f"Error validating equipment {equipment_id} usability: {e}")
            return False, f"Error validating equipment: {e}", {}
    
    # ==========================================
    # REPAIR INTEGRATION
    # ==========================================
    
    def get_repair_recommendations(
        self,
        character_id: str,
        max_total_cost: Optional[float] = None,
        priority_threshold: str = "urgent"
    ) -> Dict[str, Any]:
        """
        Get repair recommendations for character's equipment.
        
        Args:
            character_id: Character identifier
            max_total_cost: Maximum total repair budget
            priority_threshold: Minimum priority level for recommendations
            
        Returns:
            Repair recommendations with cost estimates
        """
        try:
            equipment_list = self._get_character_equipment(character_id)
            recommendations = []
            total_estimated_cost = 0.0
            
            priority_order = {"critical": 3, "urgent": 2, "recommended": 1, "minor": 0}
            min_priority = priority_order.get(priority_threshold, 2)
            
            for equipment in equipment_list:
                equipment_id = equipment['id']
                current_durability = equipment.get('current_durability', 100.0)
                
                # Get condition effects
                condition_info = self.durability_service.get_condition_effects(current_durability)
                
                # Check if repair is needed based on priority threshold
                repair_priority = priority_order.get(condition_info['repair_urgency'], 0)
                if repair_priority < min_priority:
                    continue
                
                # Calculate repair cost for full restoration
                quality = EquipmentQuality(equipment.get('quality', 'basic'))
                repair_cost_info = self.durability_service.calculate_repair_cost(
                    equipment_id=equipment_id,
                    current_durability=current_durability,
                    target_durability=100.0,
                    quality=quality,
                    base_item_value=equipment.get('base_value', 100.0)
                )
                
                if repair_cost_info['can_repair']:
                    recommendations.append({
                        'equipment_id': equipment_id,
                        'equipment_name': equipment.get('name', 'Unknown Item'),
                        'current_condition': condition_info,
                        'repair_cost': repair_cost_info['repair_cost'],
                        'repair_priority': condition_info['repair_urgency'],
                        'effectiveness_gain': 100.0 - condition_info['effectiveness_percentage']
                    })
                    total_estimated_cost += repair_cost_info['repair_cost']
            
            # Sort by priority and cost-effectiveness
            recommendations.sort(key=lambda x: (
                -priority_order.get(x['repair_priority'], 0),  # High priority first
                x['repair_cost'] / max(x['effectiveness_gain'], 1.0)  # Cost per effectiveness gain
            ))
            
            # Apply budget constraints if specified
            if max_total_cost:
                budget_filtered = []
                running_cost = 0.0
                for rec in recommendations:
                    if running_cost + rec['repair_cost'] <= max_total_cost:
                        budget_filtered.append(rec)
                        running_cost += rec['repair_cost']
                    else:
                        rec['exceeds_budget'] = True
                
                recommendations = budget_filtered
            
            return {
                "character_id": character_id,
                "repair_recommendations": recommendations,
                "total_estimated_cost": round(total_estimated_cost, 2),
                "priority_threshold": priority_threshold,
                "budget_constraint": max_total_cost,
                "recommendations_count": len(recommendations)
            }
            
        except Exception as e:
            self.logger.error(f"Error getting repair recommendations for character {character_id}: {e}")
            return {"error": str(e)}
    
    # ==========================================
    # PRIVATE HELPER METHODS
    # ==========================================
    
    def _get_character_equipment(self, character_id: str) -> List[Dict[str, Any]]:
        """Get all equipment for a character."""
        # Mock implementation - would query equipment/inventory system
        return [
            {
                "id": f"eq_{character_id}_001",
                "name": "Steel Longsword",
                "type": "weapon",
                "quality": "military",
                "current_durability": 65.5,
                "base_value": 250.0,
                "equipped": True
            },
            {
                "id": f"eq_{character_id}_002", 
                "name": "Chain Mail",
                "type": "armor",
                "quality": "military",
                "current_durability": 45.2,
                "base_value": 180.0,
                "equipped": True
            },
            {
                "id": f"eq_{character_id}_003",
                "name": "Steel Shield",
                "type": "shield", 
                "quality": "basic",
                "current_durability": 30.8,
                "base_value": 80.0,
                "equipped": True
            }
        ]
    
    def _get_equipment_details(self, equipment_id: str) -> Dict[str, Any]:
        """Get details for specific equipment."""
        # Mock implementation - would query equipment system
        return {
            "id": equipment_id,
            "current_durability": 45.5,
            "quality": "military",
            "base_value": 250.0,
            "type": "weapon",
            "name": "Steel Longsword"
        }
    
    def _filter_equipment_combat_events(
        self,
        equipment_id: str, 
        combat_events: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Filter combat events relevant to specific equipment."""
        return [
            event for event in combat_events 
            if event.get('equipment_id') == equipment_id
        ]
    
    def _prepare_environmental_exposure(
        self,
        equipment_type: str,
        environmental_exposure: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Prepare environmental exposure data for durability calculations."""
        if not environmental_exposure:
            return {}
        
        return {
            'equipment_type': equipment_type,
            'environment': environmental_exposure.get('environment', 'normal'),
            'hours': environmental_exposure.get('exposure_hours', 0.0),
            'material': environmental_exposure.get('material', 'metal')
        }
    
    def _update_equipment_durability(self, equipment_id: str, new_durability: float):
        """Update equipment durability in database."""
        # Mock implementation - would update equipment system
        self.logger.debug(f"Updated equipment {equipment_id} durability to {new_durability:.1f}%")
    
    # ==========================================
    # BULK OPERATIONS
    # ==========================================
    
    def bulk_process_time_degradation(
        self,
        character_ids: List[str],
        hours_elapsed: float,
        environmental_conditions: Dict[str, str] = None
    ) -> Dict[str, Any]:
        """
        Process time-based degradation for multiple characters efficiently.
        
        Args:
            character_ids: List of character IDs to process
            hours_elapsed: Hours since last update
            environmental_conditions: Environment per character (character_id -> environment)
            
        Returns:
            Bulk processing results
        """
        bulk_results = {}
        total_processed = 0
        
        for character_id in character_ids:
            try:
                # Get environment for this character
                environment = environmental_conditions.get(character_id, 'normal') if environmental_conditions else 'normal'
                
                environmental_exposure = {
                    'environment': environment,
                    'exposure_hours': hours_elapsed
                }
                
                result = self.process_equipment_durability_update(
                    character_id=character_id,
                    time_elapsed_hours=hours_elapsed,
                    environmental_exposure=environmental_exposure
                )
                
                bulk_results[character_id] = result
                total_processed += result.get('total_equipment_processed', 0)
                
            except Exception as e:
                self.logger.error(f"Error in bulk processing for character {character_id}: {e}")
                bulk_results[character_id] = {"success": False, "error": str(e)}
        
        return {
            "bulk_processing_results": bulk_results,
            "total_characters_processed": len(character_ids),
            "total_equipment_processed": total_processed,
            "hours_elapsed": hours_elapsed
        } 
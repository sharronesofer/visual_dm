"""
Temporary compatibility layer for crafting-to-repair migration

This module provides a bridge between the old crafting system interface
and the new repair/equipment system, allowing for gradual migration.
"""

import warnings
from typing import Dict, Any, List, Optional
from backend.systems.repair.services.repair_service import RepairService
from backend.infrastructure.services.equipment.durability_service import DurabilityService

class CraftingCompatibilityService:
    """
    Provides crafting-like interface for repair operations.
    
    This is a temporary bridge to help transition from crafting to repair system.
    """
    
    def __init__(self, repair_service: RepairService, durability_service: DurabilityService):
        self.repair_service = repair_service
        self.durability_service = durability_service
        self._warn_deprecation()
    
    def _warn_deprecation(self):
        """Warn about deprecated crafting API usage."""
        warnings.warn(
            "CraftingCompatibilityService is deprecated. "
            "Please migrate to RepairService and DurabilityService directly.",
            DeprecationWarning,
            stacklevel=3
        )
    
    def get_available_stations(self, equipment_type: str = "all") -> List[Dict[str, Any]]:
        """
        Legacy crafting station interface -> repair stations
        
        Args:
            equipment_type: Type of equipment (mapped to repair station capabilities)
            
        Returns:
            List of available repair stations in crafting-compatible format
        """
        # Use the main service to get stations, avoiding duplication
        all_stations = []
        for station_id, station_data in self.repair_service.repair_stations.items():
            if station_id in ['version', 'description', 'repair_efficiency_modifiers', 'repair_services']:
                continue
                
            if isinstance(station_data, dict) and 'metadata' in station_data:
                all_stations.append({
                    "id": station_id,
                    "name": station_data.get("name", station_id),
                    "type": f"repair_{station_data.get('type', 'basic')}",
                    "level": station_data.get("level", 1),
                    "location": "Workshop",  # Generic location
                    "available": True,
                    "capabilities": station_data.get("metadata", {}).get("repair_capabilities", {}).get("equipment_types", [])
                })
        
        return all_stations
    
    def get_craftable_items(self, character_skills: Dict[str, int], station_type: str = None) -> List[Dict[str, Any]]:
        """
        Legacy craftable items interface -> repairable equipment
        
        Args:
            character_skills: Character skill levels
            station_type: Station type filter
            
        Returns:
            List of repairable equipment in crafting-compatible format
        """
        # Get damaged equipment that can be repaired
        damaged_equipment = self.durability_service.get_damaged_equipment()
        
        craftable_items = []
        for equipment in damaged_equipment:
            # Use main service's skill mapping instead of duplicating logic
            required_skill = self.repair_service._get_equipment_skill_mapping(equipment.get("type", ""))
            
            # Map crafting skills to repair skills
            skill_mapping = {
                "smithing": "repair_weapons",
                "leatherworking": "repair_armor", 
                "tailoring": "repair_armor",
                "engineering": "repair_general"
            }
            
            # Check if player has appropriate skill
            has_skill = False
            for craft_skill, repair_skill in skill_mapping.items():
                if craft_skill in character_skills and repair_skill == required_skill:
                    if character_skills[craft_skill] >= 1:
                        has_skill = True
                        break
            
            if has_skill:
                craftable_items.append({
                    "id": f"repair_{equipment['id']}",
                    "name": f"Repair {equipment['name']}",
                    "description": f"Restore {equipment['name']} to working condition",
                    "skill_required": required_skill,
                    "min_skill_level": 1,
                    "crafting_time": self._estimate_repair_time(equipment),
                    "ingredients": self._get_repair_materials_legacy(equipment)
                })
        
        return craftable_items
    
    def craft_item(self, recipe_id: str, materials: List[Dict[str, Any]], character_id: str) -> Dict[str, Any]:
        """
        Legacy crafting interface -> repair operation
        
        Args:
            recipe_id: Recipe ID (should start with 'repair_')
            materials: Available materials
            character_id: Character performing the action
            
        Returns:
            Crafting result in legacy format
        """
        if not recipe_id.startswith("repair_"):
            raise ValueError("Only repair operations are supported through compatibility layer")
        
        # Extract equipment ID from recipe ID
        equipment_id = recipe_id.replace("repair_", "")
        
        # Convert materials list to dict format expected by repair service
        materials_dict = {}
        for material in materials:
            materials_dict[material["item_id"]] = material.get("quantity", 1)
        
        # Use basic repair station as default
        station_id = "basic_repair_station"
        target_durability = 100.0
        
        # Perform repair operation using main service
        repair_result = self.repair_service.perform_repair(
            equipment_id=equipment_id,
            station_id=station_id,
            target_durability=target_durability,
            available_materials=materials_dict,
            craftsman_skill="journeyman"
        )
        
        # Convert to crafting result format
        return {
            "success": repair_result["success"],
            "result_items": [{
                "item_id": equipment_id,
                "quantity": 1,
                "condition": "repaired" if repair_result["success"] else "partially_repaired"
            }],
            "experience_gained": 10 if repair_result["success"] else 5,
            "materials_consumed": repair_result.get("materials_consumed", []),
            "message": repair_result.get("reason", "Repair completed successfully")
        }
    
    def get_recipe_requirements(self, recipe_id: str) -> Dict[str, Any]:
        """
        Legacy recipe requirements -> repair requirements
        
        Args:
            recipe_id: Recipe ID (should start with 'repair_')
            
        Returns:
            Requirements in crafting-compatible format
        """
        if not recipe_id.startswith("repair_"):
            return {"error": "Recipe not found"}
        
        equipment_id = recipe_id.replace("repair_", "")
        
        # Get equipment from main service
        equipment = self.repair_service._get_equipment_from_db(equipment_id)
        if not equipment:
            return {"error": "Equipment not found"}
        
        # Use main service to calculate requirements
        station_id = "basic_repair_station"
        target_durability = 100.0
        
        requirements = self.repair_service.calculate_repair_requirements(
            equipment, target_durability, station_id
        )
        
        if "error" in requirements:
            return requirements
        
        # Convert to legacy format
        ingredients = []
        for material, quantity in requirements.get("materials_needed", {}).items():
            ingredients.append({
                "item_id": material,
                "quantity": quantity
            })
        
        return {
            "ingredients": ingredients,
            "skill_required": self.repair_service._get_equipment_skill_mapping(equipment.get("type", "")),
            "min_skill_level": 1,
            "crafting_time": int(requirements.get("estimated_time_hours", 1) * 60),  # Convert to minutes
            "station_required": station_id
        }
    
    def _estimate_repair_time(self, equipment: Dict[str, Any]) -> int:
        """Estimate repair time based on equipment damage using main service logic."""
        damage_level = (100.0 - equipment.get("current_durability", 50.0)) / 100.0
        # Use repair service's time calculation constants
        time_config = self.repair_service.repair_formulas.get("cost_formulas", {})
        base_time_minutes = time_config.get("time_cost_base", 2.0) * 60  # Convert hours to minutes
        return int(base_time_minutes * (1 + damage_level))
    
    def _get_repair_materials_legacy(self, equipment: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get required materials for repair in legacy crafting format."""
        # Use main service's material calculation
        from backend.systems.equipment.models.equipment_quality import EquipmentQuality
        
        quality = EquipmentQuality(equipment.get("quality", "basic"))
        equipment_type = equipment.get("type", "weapon")
        current_durability = equipment.get("current_durability", 50.0)
        
        repair_percentage = (100.0 - current_durability) / 100.0
        damage_severity = repair_percentage
        
        materials_dict = self.repair_service._calculate_material_quantities(
            equipment_type, quality, repair_percentage, damage_severity
        )
        
        # Convert to legacy list format
        materials_list = []
        for material, quantity in materials_dict.items():
            materials_list.append({
                "item_id": material,
                "quantity": quantity
            })
        
        return materials_list

# Convenience factory function
def create_crafting_compatibility_service() -> CraftingCompatibilityService:
    """Create a compatibility service with default dependencies."""
    from sqlalchemy.orm import Session
    # This would normally get a real database session
    db_session = Session()  # Placeholder
    
    repair_service = RepairService(db_session)
    durability_service = DurabilityService(db_session)
    return CraftingCompatibilityService(repair_service, durability_service) 
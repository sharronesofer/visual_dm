"""
Repair Business Service - Pure Business Logic

Contains the core business rules and domain logic for the repair system.
"""

import random
from typing import Dict, List, Any, Optional, Tuple, Protocol
from datetime import datetime

from backend.systems.equipment.models.equipment_quality import EquipmentQuality
from backend.systems.repair.models.repair_models import (
    RepairRequest, RepairStatus, RepairSkill, RepairRequirement
)


# Business domain data structures
class RepairCalculationData:
    """Business domain data for repair calculations"""
    def __init__(
        self,
        equipment_id: str,
        equipment_type: str,
        current_durability: float,
        target_durability: float,
        quality: EquipmentQuality,
        base_value: float
    ):
        self.equipment_id = equipment_id
        self.equipment_type = equipment_type
        self.current_durability = current_durability
        self.target_durability = target_durability
        self.quality = quality
        self.base_value = base_value


class RepairOperationData:
    """Business domain data for repair operations"""
    def __init__(
        self,
        equipment_id: str,
        station_id: str,
        target_durability: float,
        available_materials: Dict[str, int],
        craftsman_skill: str = "journeyman"
    ):
        self.equipment_id = equipment_id
        self.station_id = station_id
        self.target_durability = target_durability
        self.available_materials = available_materials
        self.craftsman_skill = craftsman_skill


# Business Logic Protocols (dependency injection)
class RepairRepository(Protocol):
    """Protocol for repair data access"""
    
    def get_equipment_by_id(self, equipment_id: str) -> Optional[Dict[str, Any]]:
        """Get equipment by ID"""
        ...
    
    def update_equipment_durability(self, equipment_id: str, new_durability: float) -> bool:
        """Update equipment durability"""
        ...
    
    def create_repair_request(self, repair_request: RepairRequest) -> RepairRequest:
        """Create repair request"""
        ...
    
    def get_repair_request_by_id(self, repair_request_id: str) -> Optional[RepairRequest]:
        """Get repair request by ID"""
        ...
    
    def update_repair_request(self, repair_request: RepairRequest) -> RepairRequest:
        """Update repair request"""
        ...
    
    def get_repair_requests(
        self,
        repairer_id: Optional[str] = None,
        character_id: Optional[str] = None,
        status_filter: Optional[RepairStatus] = None
    ) -> List[RepairRequest]:
        """Get repair requests with filtering"""
        ...


class RepairDataService(Protocol):
    """Protocol for repair configuration data"""
    
    def get_repair_stations(self) -> Dict[str, Any]:
        """Get repair stations configuration"""
        ...
    
    def get_building_materials(self) -> Dict[str, Any]:
        """Get building materials configuration"""
        ...
    
    def get_repair_formulas(self) -> Dict[str, Any]:
        """Get repair formulas configuration"""
        ...


class DurabilityService(Protocol):
    """Protocol for durability calculations"""
    
    def calculate_repair_cost(
        self,
        equipment_id: str,
        current_durability: float,
        target_durability: float,
        quality: EquipmentQuality,
        base_item_value: float
    ) -> Dict[str, Any]:
        """Calculate repair cost"""
        ...
    
    def estimate_repair_time(
        self,
        current_durability: float,
        target_durability: float,
        quality: EquipmentQuality,
        repairer_skill: int
    ) -> Dict[str, Any]:
        """Estimate repair time"""
        ...


class RepairBusinessService:
    """Service class for repair business logic - pure business rules"""
    
    # Business constants for repair success rates
    REPAIR_SUCCESS_RATES = {
        "novice": 0.60,      # 60% base success
        "apprentice": 0.75,  # 75% base success  
        "journeyman": 0.85,  # 85% base success
        "expert": 0.95,      # 95% base success
        "master": 0.99       # 99% base success
    }
    
    # Business constants for critical failure rates
    CRITICAL_FAILURE_RATES = {
        "novice": 0.15,      # 15% chance of critical failure
        "apprentice": 0.08,  # 8% chance of critical failure
        "journeyman": 0.04,  # 4% chance of critical failure
        "expert": 0.02,      # 2% chance of critical failure
        "master": 0.01       # 1% chance of critical failure
    }
    
    def __init__(
        self,
        repair_repository: RepairRepository,
        repair_data_service: RepairDataService,
        durability_service: DurabilityService
    ):
        self.repair_repository = repair_repository
        self.repair_data_service = repair_data_service
        self.durability_service = durability_service
    
    def calculate_repair_success_chance(
        self,
        damage_severity: float,
        craftsman_skill: str,
        station_efficiency: float
    ) -> float:
        """
        Business rule: Calculate repair success chance using configuration.
        
        Args:
            damage_severity: How damaged the item is (0.0 to 1.0)
            craftsman_skill: Skill level of the craftsman
            station_efficiency: Efficiency of the repair station
            
        Returns:
            Success chance percentage
        """
        config = self.repair_data_service.get_repair_formulas().get("repair_success_rates", {})
        
        base_success = config.get("base_success_rate", 85.0)
        damage_penalty_mult = config.get("damage_penalty_multiplier", 20.0)
        skill_modifiers = config.get("skill_modifiers", {})
        bounds = config.get("success_bounds", {"minimum": 50.0, "maximum": 99.0})
        
        # Business rule: Apply skill modifier
        skill_modifier = skill_modifiers.get(craftsman_skill, 1.0)
        
        # Business rule: Calculate damage penalty
        damage_penalty = damage_severity * damage_penalty_mult
        
        # Business rule: Apply station efficiency bonus
        efficiency_bonus = (station_efficiency - 1.0) * 10  # 10% per 0.1 efficiency
        
        # Final calculation
        final_success_rate = (base_success * skill_modifier) - damage_penalty + efficiency_bonus
        
        # Business rule: Clamp to bounds
        return max(bounds["minimum"], min(bounds["maximum"], final_success_rate))
    
    def get_equipment_skill_mapping(self, equipment_type: str) -> str:
        """Business rule: Get the required skill for equipment type."""
        mapping = self.repair_data_service.get_repair_formulas().get("equipment_skill_mapping", {})
        return mapping.get(equipment_type.lower(), "repair_general")
    
    def calculate_material_quantities(
        self,
        equipment_type: str,
        quality: EquipmentQuality,
        repair_percentage: float,
        damage_severity: float
    ) -> Dict[str, int]:
        """
        Business rule: Calculate material quantities using configuration.
        
        Args:
            equipment_type: Type of equipment
            quality: Quality level
            repair_percentage: How much repair is needed
            damage_severity: How damaged the item is
            
        Returns:
            Dictionary of materials and quantities needed
        """
        config = self.repair_data_service.get_repair_formulas().get("material_calculations", {})
        
        base_multiplier = config.get("base_quantity_multiplier", 5)
        quality_multipliers = config.get("quality_multipliers", {
            'basic': 1.0,
            'military': 1.5,
            'mastercraft': 2.0
        })
        
        # Business rule: Quality affects material requirements
        quality_multiplier = quality_multipliers.get(quality.value, 1.0)
        
        # Business rule: Base quantity calculation
        base_qty = max(1, int(repair_percentage * damage_severity * base_multiplier))
        final_qty = max(1, int(base_qty * quality_multiplier))
        
        # Business rule: Different equipment types need different materials
        return {"iron_ingot": final_qty, "leather": max(1, final_qty // 2)}
    
    def get_available_repair_stations(
        self,
        equipment_type: str,
        equipment_quality: EquipmentQuality
    ) -> List[Dict[str, Any]]:
        """
        Business rule: Find stations that can handle specific equipment.
        
        Args:
            equipment_type: Type of equipment to repair
            equipment_quality: Quality level of equipment
            
        Returns:
            List of available repair stations
        """
        repair_stations = self.repair_data_service.get_repair_stations()
        available_stations = []
        
        for station_id, station_data in repair_stations.items():
            # Skip metadata entries
            if station_id in ['version', 'description', 'repair_efficiency_modifiers', 'repair_services']:
                continue
                
            if not isinstance(station_data, dict) or 'metadata' not in station_data:
                continue
            
            capabilities = station_data.get('metadata', {}).get('repair_capabilities', {})
            
            # Business rule: Check if station can handle this equipment type
            supported_types = capabilities.get('equipment_types', [])
            if equipment_type not in supported_types and 'all' not in supported_types:
                continue
            
            # Business rule: Check quality level restrictions
            quality_levels = capabilities.get('quality_levels', ['basic', 'military', 'mastercraft'])
            if equipment_quality.value not in quality_levels:
                continue
            
            available_stations.append({
                'station_id': station_id,
                'name': station_data.get('name', station_id),
                'efficiency': capabilities.get('efficiency', 1.0),
                'supported_types': supported_types,
                'quality_levels': quality_levels
            })
        
        return available_stations
    
    def perform_repair_operation(self, operation_data: RepairOperationData) -> Dict[str, Any]:
        """
        Business rule: Perform the actual repair with success/failure logic.
        
        Args:
            operation_data: Repair operation parameters
            
        Returns:
            Repair result with success/failure and details
        """
        # Business rule: Equipment must exist
        equipment = self.repair_repository.get_equipment_by_id(operation_data.equipment_id)
        if not equipment:
            return {
                'success': False,
                'reason': f'Equipment {operation_data.equipment_id} not found',
                'equipment_id': operation_data.equipment_id
            }
        
        # Business rule: Calculate requirements first
        calc_data = RepairCalculationData(
            equipment_id=equipment['id'],
            equipment_type=equipment.get('type', 'weapon'),
            current_durability=equipment.get('current_durability', 100.0),
            target_durability=operation_data.target_durability,
            quality=EquipmentQuality(equipment.get('quality', 'basic')),
            base_value=equipment.get('base_value', 100.0)
        )
        
        requirements = self.calculate_repair_requirements(calc_data, operation_data.station_id)
        
        if not requirements.get('can_repair'):
            return {
                'success': False,
                'reason': requirements.get('reason', 'Cannot repair'),
                'equipment_id': operation_data.equipment_id
            }
        
        # Business rule: Check material availability
        materials_needed = requirements['materials_needed']
        missing_materials = []
        
        for material, qty_needed in materials_needed.items():
            available_qty = operation_data.available_materials.get(material, 0)
            if available_qty < qty_needed:
                missing_materials.append({
                    'material': material,
                    'needed': qty_needed,
                    'available': available_qty,
                    'missing': qty_needed - available_qty
                })
        
        if missing_materials:
            return {
                'success': False,
                'reason': 'Insufficient materials',
                'missing_materials': missing_materials,
                'equipment_id': operation_data.equipment_id
            }
        
        # Business rule: Calculate success chance
        damage_severity = (100.0 - calc_data.current_durability) / 100.0
        station_efficiency = requirements['station_efficiency']
        
        success_rate = self.calculate_repair_success_chance(
            damage_severity, operation_data.craftsman_skill, station_efficiency
        )
        
        # Business rule: Actual repair attempt with randomness
        repair_roll = random.uniform(0, 100)
        repair_successful = repair_roll <= success_rate
        
        durability_to_restore = calc_data.target_durability - calc_data.current_durability
        
        if repair_successful:
            # Business rule: Full repair success
            final_durability = min(100.0, calc_data.target_durability)
            
            # Update equipment durability
            self.repair_repository.update_equipment_durability(
                operation_data.equipment_id, final_durability
            )
            
            return {
                'success': True,
                'equipment_id': operation_data.equipment_id,
                'durability_restored': round(durability_to_restore, 1),
                'final_durability': round(final_durability, 1),
                'materials_consumed': materials_needed,
                'cost': requirements['adjusted_repair_cost'],
                'time_taken_hours': requirements['estimated_time_hours'],
                'craftsman_skill': operation_data.craftsman_skill,
                'success_rate': round(success_rate, 1)
            }
        else:
            # Business rule: Partial repair on failure
            partial_restore = durability_to_restore * 0.3  # 30% of intended repair
            partial_durability = calc_data.current_durability + partial_restore
            partial_materials = {k: max(1, v // 2) for k, v in materials_needed.items()}
            
            # Update equipment with partial repair
            self.repair_repository.update_equipment_durability(
                operation_data.equipment_id, partial_durability
            )
            
            return {
                'success': False,
                'reason': 'Repair partially failed',
                'equipment_id': operation_data.equipment_id,
                'partial_durability_restored': round(partial_restore, 1),
                'final_durability': round(partial_durability, 1),
                'materials_consumed': partial_materials,
                'cost': requirements['adjusted_repair_cost'] * 0.5,
                'time_taken_hours': requirements['estimated_time_hours'],
                'success_rate': round(success_rate, 1)
            }
    
    def calculate_repair_requirements(
        self,
        calc_data: RepairCalculationData,
        station_id: str
    ) -> Dict[str, Any]:
        """
        Business rule: Calculate what's needed to repair equipment at a station.
        
        Args:
            calc_data: Repair calculation data
            station_id: ID of the repair station to use
            
        Returns:
            Dictionary with repair requirements and costs
        """
        # Business rule: Station must exist and be capable
        repair_stations = self.repair_data_service.get_repair_stations()
        station_data = repair_stations.get(station_id, {})
        if not station_data:
            return {"error": f"Unknown repair station: {station_id}"}
        
        # Business rule: Check if station can handle this repair
        available_stations = self.get_available_repair_stations(
            calc_data.equipment_type, calc_data.quality
        )
        if not any(s['station_id'] == station_id for s in available_stations):
            return {"error": f"Station {station_id} cannot repair this equipment"}
        
        # Business rule: Calculate base repair cost using durability service
        cost_info = self.durability_service.calculate_repair_cost(
            calc_data.equipment_id, calc_data.current_durability, 
            calc_data.target_durability, calc_data.quality, calc_data.base_value
        )
        
        if not cost_info.get('can_repair'):
            return cost_info
        
        # Business rule: Get station modifiers
        capabilities = station_data.get('metadata', {}).get('repair_capabilities', {})
        efficiency = capabilities.get('efficiency', 1.0)
        
        # Business rule: Calculate material requirements
        repair_percentage = (calc_data.target_durability - calc_data.current_durability) / 100.0
        damage_severity = (100.0 - calc_data.current_durability) / 100.0
        
        materials_needed = self.calculate_material_quantities(
            calc_data.equipment_type, calc_data.quality, repair_percentage, damage_severity
        )
        
        # Business rule: Calculate time required using configuration
        time_config = self.repair_data_service.get_repair_formulas().get("cost_formulas", {})
        base_time_hours = repair_percentage * time_config.get("time_cost_base", 2.0)
        actual_time = base_time_hours / efficiency
        
        # Business rule: Apply station efficiency to cost
        adjusted_cost = cost_info['repair_cost'] / efficiency
        
        return {
            **cost_info,
            'adjusted_repair_cost': round(adjusted_cost, 2),
            'materials_needed': materials_needed,
            'estimated_time_hours': round(actual_time, 1),
            'station_efficiency': efficiency,
            'station_name': station_data.get('name', station_id),
            'can_repair': True
        }
    
    def create_repair_request(
        self,
        equipment_id: str,
        character_id: str,
        target_durability: float = 100.0,
        repairer_id: Optional[str] = None,
        priority: str = "normal",
        max_cost: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Business rule: Create a repair request with validation.
        
        Args:
            equipment_id: ID of equipment to repair
            character_id: ID of character requesting repair
            target_durability: Desired durability percentage
            repairer_id: Optional specific repairer ID
            priority: Priority level
            max_cost: Maximum cost character is willing to pay
            
        Returns:
            Repair request result
        """
        # Business rule: Equipment must exist
        equipment = self.repair_repository.get_equipment_by_id(equipment_id)
        if not equipment:
            return {"success": False, "error": "Equipment not found"}
        
        current_durability = equipment.get('current_durability', 100.0)
        
        # Business rule: Validate repair is needed
        if current_durability >= target_durability:
            return {
                "success": False, 
                "error": "Equipment doesn't need repair",
                "current_durability": current_durability,
                "target_durability": target_durability
            }
        
        # Business rule: Calculate costs and validate budget
        quality = EquipmentQuality(equipment.get('quality', 'basic'))
        base_value = equipment.get('base_value', 100.0)
        
        repair_cost_info = self.durability_service.calculate_repair_cost(
            equipment_id=equipment_id,
            current_durability=current_durability,
            target_durability=target_durability,
            quality=quality,
            base_item_value=base_value
        )
        
        # Business rule: Check budget constraints
        if max_cost and repair_cost_info["repair_cost"] > max_cost:
            return {
                "success": False,
                "error": "Repair cost exceeds maximum budget",
                "estimated_cost": repair_cost_info["repair_cost"],
                "max_cost": max_cost
            }
        
        # Business rule: Estimate repair time
        repair_time_info = self.durability_service.estimate_repair_time(
            current_durability=current_durability,
            target_durability=target_durability,
            quality=quality,
            repairer_skill=75  # Default skill level
        )
        
        # Business rule: Determine repair requirements
        equipment_type = equipment.get('type', 'weapon')
        repair_requirements = self._determine_repair_requirements(
            equipment_type=equipment_type,
            current_durability=current_durability,
            target_durability=target_durability,
            quality=quality
        )
        
        # Business rule: Create and save repair request
        repair_request = RepairRequest(
            equipment_id=equipment_id,
            character_id=character_id,
            target_durability=target_durability,
            estimated_cost=repair_cost_info["repair_cost"],
            estimated_time_hours=repair_time_info["final_time_hours"],
            priority=priority,
            status=RepairStatus.PENDING,
            repairer_id=repairer_id,
            requirements=repair_requirements,
            created_at=datetime.utcnow()
        )
        
        saved_request = self.repair_repository.create_repair_request(repair_request)
        
        return {
            "success": True,
            "repair_request_id": saved_request.id,
            "equipment_id": equipment_id,
            "current_durability": current_durability,
            "target_durability": target_durability,
            "cost_breakdown": repair_cost_info,
            "time_estimate": repair_time_info,
            "requirements": repair_requirements,
            "status": RepairStatus.PENDING.value
        }
    
    def _determine_repair_requirements(
        self,
        equipment_type: str,
        current_durability: float,
        target_durability: float,
        quality: EquipmentQuality
    ) -> List[RepairRequirement]:
        """Business rule: Determine what materials/tools are needed for repair."""
        requirements = []
        
        repair_amount = target_durability - current_durability
        
        # Business rule: Basic materials always needed
        requirements.append(RepairRequirement(
            item_type="material",
            item_id="repair_metal",
            quantity=max(1, int(repair_amount / 10)),
            required=True
        ))
        
        # Business rule: Additional requirements for heavily damaged items
        if current_durability < 25.0:
            requirements.append(RepairRequirement(
                item_type="tool",
                item_id="master_tools",
                quantity=1,
                required=True
            ))
        
        # Business rule: Quality-specific requirements
        if quality in [EquipmentQuality.MILITARY, EquipmentQuality.MASTERCRAFT]:
            requirements.append(RepairRequirement(
                item_type="material",
                item_id="quality_oil",
                quantity=1,
                required=False
            ))
        
        return requirements


def create_repair_business_service(
    repair_repository: RepairRepository,
    repair_data_service: RepairDataService,
    durability_service: DurabilityService
) -> RepairBusinessService:
    """Factory function to create repair business service"""
    return RepairBusinessService(repair_repository, repair_data_service, durability_service) 
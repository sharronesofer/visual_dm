"""
Repair Service - Business Orchestration

Orchestrates repair operations using business logic services and infrastructure components.
"""

from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

from backend.systems.equipment.models.equipment_quality import EquipmentQuality
from backend.systems.repair.models.repair_models import (
    RepairRequest, RepairStatus, RepairSkill, RepairRequirement
)
from backend.systems.repair.services.repair_business_service import (
    RepairBusinessService, RepairCalculationData, RepairOperationData
)
from backend.infrastructure.database.repositories.repair_repository import RepairRepository
from backend.infrastructure.services.repair.repair_data_loader import RepairDataLoader
from backend.infrastructure.services.equipment.durability_service import DurabilityService


class RepairService:
    """Service for orchestrating equipment repairs using business logic and infrastructure"""
    
    def __init__(
        self,
        repair_business_service: RepairBusinessService,
        repair_repository: RepairRepository,
        repair_data_loader: RepairDataLoader,
        durability_service: DurabilityService
    ):
        self.business_service = repair_business_service
        self.repository = repair_repository
        self.data_loader = repair_data_loader
        self.durability_service = durability_service
    
    def get_available_repair_stations(
        self,
        equipment_type: str,
        equipment_quality: EquipmentQuality
    ) -> List[Dict[str, Any]]:
        """Get stations that can handle specific equipment type and quality"""
        return self.business_service.get_available_repair_stations(equipment_type, equipment_quality)
    
    def calculate_repair_requirements(
        self,
        equipment: Dict[str, Any],
        target_durability: float,
        station_id: str
    ) -> Dict[str, Any]:
        """Calculate what's needed to repair equipment at a specific station"""
        calc_data = RepairCalculationData(
            equipment_id=equipment.get('id'),
            equipment_type=equipment.get('type', 'weapon'),
            current_durability=equipment.get('current_durability', 100.0),
            target_durability=target_durability,
            quality=EquipmentQuality(equipment.get('quality', 'basic')),
            base_value=equipment.get('base_value', 100.0)
        )
        
        return self.business_service.calculate_repair_requirements(calc_data, station_id)
    
    def perform_repair(
        self,
        equipment_id: str,
        station_id: str,
        target_durability: float,
        available_materials: Dict[str, int],
        craftsman_skill: str = "journeyman"
    ) -> Dict[str, Any]:
        """Perform the actual repair operation"""
        operation_data = RepairOperationData(
            equipment_id=equipment_id,
            station_id=station_id,
            target_durability=target_durability,
            available_materials=available_materials,
            craftsman_skill=craftsman_skill
        )
        
        return self.business_service.perform_repair_operation(operation_data)
    
    def get_repair_cost_estimate(
        self,
        equipment_type: str,
        quality: EquipmentQuality,
        current_durability: float,
        target_durability: float = 100.0
    ) -> Dict[str, Any]:
        """Get a quick repair cost estimate without specifying a station"""
        # Get available stations for this equipment
        stations = self.business_service.get_available_repair_stations(equipment_type, quality)
        
        if not stations:
            return {
                'error': f'No repair stations available for {quality.value} {equipment_type}'
            }
        
        # Calculate cost range using different stations
        base_value = 100.0  # Default base value for estimation
        base_cost_info = self.durability_service.calculate_repair_cost(
            'estimate', current_durability, target_durability, quality, base_value
        )
        
        if not base_cost_info.get('can_repair'):
            return base_cost_info
        
        # Calculate range based on station efficiencies
        min_efficiency = min(s['efficiency'] for s in stations)
        max_efficiency = max(s['efficiency'] for s in stations)
        
        base_cost = base_cost_info['repair_cost']
        min_cost = base_cost / max_efficiency  # Higher efficiency = lower cost
        max_cost = base_cost / min_efficiency   # Lower efficiency = higher cost
        
        return {
            'base_repair_cost': round(base_cost, 2),
            'cost_range': {
                'min': round(min_cost, 2),
                'max': round(max_cost, 2)
            },
            'available_stations': len(stations),
            'repair_percentage': base_cost_info['repair_percentage'],
            'quality': quality.value,
            'damage_severity': base_cost_info['damage_severity']
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
        """Create a comprehensive repair request with cost estimation"""
        return self.business_service.create_repair_request(
            equipment_id=equipment_id,
            character_id=character_id,
            target_durability=target_durability,
            repairer_id=repairer_id,
            priority=priority,
            max_cost=max_cost
        )
    
    def execute_repair(
        self,
        repair_request_id: str,
        repairer_id: str,
        repairer_skill_level: str = "journeyman",
        use_premium_materials: bool = False
    ) -> Dict[str, Any]:
        """Execute equipment repair with success/failure mechanics"""
        # Get repair request
        repair_request = self.repository.get_repair_request_by_id(repair_request_id)
        if not repair_request:
            return {"success": False, "error": "Repair request not found"}
        
        if repair_request.status != RepairStatus.PENDING:
            return {"success": False, "error": f"Repair request status is {repair_request.status.value}"}
        
        # Get equipment details
        equipment = self.repository.get_equipment_details(repair_request.equipment_id)
        current_durability = equipment.get('current_durability', 100.0)
        
        # Calculate success probability using business service
        base_success_rate = self.business_service.REPAIR_SUCCESS_RATES.get(repairer_skill_level, 0.75)
        
        # Modify success rate based on factors
        success_modifiers = {
            "premium_materials": 0.1 if use_premium_materials else 0.0,
            "equipment_condition": self.durability_service.get_condition_effects(current_durability).get('repair_difficulty_modifier', 0.0),
            "repair_complexity": self._get_complexity_modifier(repair_request.target_durability - current_durability)
        }
        
        final_success_rate = min(0.99, base_success_rate + sum(success_modifiers.values()))
        
        # Roll for success/failure
        import random
        roll = random.random()
        repair_successful = roll <= final_success_rate
        
        # Determine repair outcome
        if repair_successful:
            # Successful repair
            actual_durability_gained = self._calculate_successful_repair(
                current_durability, 
                repair_request.target_durability,
                repairer_skill_level,
                use_premium_materials
            )
            new_durability = min(100.0, current_durability + actual_durability_gained)
            
            repair_result = {
                "outcome": "success",
                "durability_gained": actual_durability_gained,
                "new_durability": new_durability,
                "final_success_rate": final_success_rate,
                "modifiers": success_modifiers
            }
            
        else:
            # Failed repair - check for critical failure
            critical_failure_rate = self.business_service.CRITICAL_FAILURE_RATES.get(repairer_skill_level, 0.08)
            critical_failure = random.random() <= critical_failure_rate
            
            if critical_failure:
                # Critical failure - equipment takes additional damage
                damage_dealt = random.uniform(2.0, 8.0)
                new_durability = max(0.0, current_durability - damage_dealt)
                
                repair_result = {
                    "outcome": "critical_failure",
                    "durability_lost": damage_dealt,
                    "new_durability": new_durability,
                    "final_success_rate": final_success_rate,
                    "modifiers": success_modifiers
                }
            else:
                # Normal failure - no change to equipment
                repair_result = {
                    "outcome": "failure",
                    "durability_gained": 0.0,
                    "new_durability": current_durability,
                    "final_success_rate": final_success_rate,
                    "modifiers": success_modifiers
                }
        
        # Update equipment durability in database
        self.repository.update_equipment_durability(
            repair_request.equipment_id, 
            repair_result["new_durability"]
        )
        
        # Update repair request status
        repair_request.status = RepairStatus.COMPLETED if repair_successful else RepairStatus.FAILED
        repair_request.completed_at = datetime.utcnow()
        repair_request.repairer_id = repairer_id
        repair_request.actual_cost = repair_request.estimated_cost
        
        # Process payment if successful
        if repair_successful:
            payment_result = self._process_repair_payment(
                repair_request.character_id,
                repairer_id,
                repair_request.estimated_cost
            )
            repair_result["payment"] = payment_result
        
        self.repository.update_repair_request(repair_request)
        
        repair_result.update({
            "repair_request_id": repair_request_id,
            "equipment_id": repair_request.equipment_id,
            "repairer_id": repairer_id,
            "skill_level": repairer_skill_level,
            "premium_materials": use_premium_materials,
            "cost": repair_request.estimated_cost if repair_successful else 0
        })
        
        return repair_result
    
    def get_available_repairers(
        self,
        region_id: Optional[str] = None,
        equipment_type: Optional[str] = None,
        min_skill_level: str = "novice"
    ) -> List[Dict[str, Any]]:
        """Get list of available repairers with their capabilities"""
        # This would query a repairers table/system
        # For now, return mock data structure
        mock_repairers = [
            {
                "repairer_id": "blacksmith_001",
                "name": "Master Gareth",
                "location": "Town Square Forge",
                "skill_level": "master",
                "specializations": ["weapon", "armor"],
                "reputation": 95,
                "base_cost_multiplier": 1.2,
                "success_rate_bonus": 0.05,
                "available": True,
                "queue_length": 2
            },
            {
                "repairer_id": "tinker_002", 
                "name": "Apprentice Lyra",
                "location": "Market District",
                "skill_level": "apprentice",
                "specializations": ["accessory", "shield"],
                "reputation": 65,
                "base_cost_multiplier": 0.8,
                "success_rate_bonus": 0.0,
                "available": True,
                "queue_length": 0
            }
        ]
        
        return mock_repairers
    
    def get_repair_queue(
        self,
        repairer_id: Optional[str] = None,
        character_id: Optional[str] = None,
        status_filter: Optional[RepairStatus] = None
    ) -> List[Dict[str, Any]]:
        """Get repair queue with filtering options"""
        repair_requests = self.repository.get_repair_requests(repairer_id, character_id, status_filter)
        
        result = []
        for request in repair_requests:
            result.append({
                "repair_request_id": request.id,
                "equipment_id": request.equipment_id,
                "character_id": request.character_id,
                "target_durability": request.target_durability,
                "estimated_cost": request.estimated_cost,
                "estimated_time_hours": request.estimated_time_hours,
                "priority": request.priority,
                "status": request.status.value,
                "created_at": request.created_at.isoformat(),
                "repairer_id": request.repairer_id
            })
        
        return result
    
    # Helper methods for business calculations
    def _get_complexity_modifier(self, repair_amount: float) -> float:
        """Get success rate modifier based on repair complexity"""
        if repair_amount > 75:
            return -0.15  # Major repairs are harder
        elif repair_amount > 50:
            return -0.1   # Moderate repairs are somewhat harder
        else:
            return 0.0    # Minor repairs have no penalty
    
    def _calculate_successful_repair(
        self,
        current_durability: float,
        target_durability: float,
        skill_level: str,
        premium_materials: bool
    ) -> float:
        """Calculate actual durability gained from successful repair"""
        intended_gain = target_durability - current_durability
        
        # Skill affects efficiency
        skill_multipliers = {
            "novice": 0.8,      # 80% efficiency
            "apprentice": 0.9,  # 90% efficiency
            "journeyman": 1.0,  # 100% efficiency
            "expert": 1.1,      # 110% efficiency
            "master": 1.2       # 120% efficiency
        }
        
        efficiency = skill_multipliers.get(skill_level, 1.0)
        if premium_materials:
            efficiency *= 1.1  # 10% bonus for premium materials
        
        actual_gain = intended_gain * efficiency
        
        # Add some randomness
        import random
        randomness = random.uniform(0.9, 1.1)
        
        return actual_gain * randomness
    
    def _process_repair_payment(
        self,
        character_id: str,
        repairer_id: str,
        amount: float
    ) -> Dict[str, Any]:
        """Process payment for repair services"""
        # Mock implementation - would integrate with economy system
        return {
            "success": True,
            "amount": amount,
            "character_id": character_id,
            "repairer_id": repairer_id,
            "transaction_id": f"repair_payment_{character_id}_{repairer_id}"
        }


def create_repair_service(
    repair_business_service: RepairBusinessService,
    repair_repository: RepairRepository,
    repair_data_loader: RepairDataLoader,
    durability_service: DurabilityService
) -> RepairService:
    """Factory function to create repair service"""
    return RepairService(
        repair_business_service, repair_repository, repair_data_loader, durability_service
    ) 
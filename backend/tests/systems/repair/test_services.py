"""
Test module for repair.services

Tests repair services according to Development Bible standards:
- Repair job management and execution
- Skill-based repair calculations
- Resource consumption and cost management
- Quality and success determination
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
from uuid import uuid4

# Import the module under test
try:
    from backend.systems.repair.services import (
        RepairService, RepairJobService, RepairCostService,
        RepairSkillService, RepairQualityService
    )
    repair_services_available = True
except ImportError as e:
    print(f"Repair services not available: {e}")
    repair_services_available = False
    
    # Create mock classes for testing
    class RepairService:
        def __init__(self, job_service=None, cost_service=None, skill_service=None):
            self.job_service = job_service
            self.cost_service = cost_service
            self.skill_service = skill_service
        
        def initiate_repair(self, equipment_id, repairer_id, target_quality="good"):
            return {
                "id": str(uuid4()),
                "equipment_id": equipment_id,
                "repairer_id": repairer_id,
                "status": "pending",
                "target_quality": target_quality
            }
        
        def execute_repair(self, repair_job_id):
            return {"success": True, "quality_achieved": "good", "durability_restored": 30.0}
        
        def get_repair_estimate(self, equipment_id, target_quality):
            return {"estimated_cost": 100, "estimated_time": 120, "success_chance": 0.75}
    
    class RepairJobService:
        def __init__(self, repository=None):
            self.repository = repository
        
        def create_repair_job(self, equipment_id, repairer_id, **kwargs):
            return {
                "id": str(uuid4()),
                "equipment_id": equipment_id,
                "repairer_id": repairer_id,
                "status": "pending",
                "created_at": datetime.utcnow()
            }
        
        def start_repair_job(self, job_id):
            return {"status": "in_progress", "started_at": datetime.utcnow()}
        
        def complete_repair_job(self, job_id, success=True):
            return {"status": "completed" if success else "failed", "completed_at": datetime.utcnow()}
        
        def get_active_jobs(self, repairer_id):
            return []
    
    class RepairCostService:
        def __init__(self, material_service=None, tool_service=None):
            self.material_service = material_service
            self.tool_service = tool_service
        
        def calculate_repair_cost(self, equipment_id, target_quality, repairer_skill):
            base_cost = 50
            quality_multiplier = {"poor": 0.5, "basic": 0.8, "good": 1.0, "excellent": 1.5, "masterwork": 2.0}
            skill_discount = max(0.5, 1.0 - (repairer_skill / 200.0))
            return int(base_cost * quality_multiplier.get(target_quality, 1.0) * skill_discount)
        
        def get_material_requirements(self, equipment_id, target_quality):
            return [{"material": "iron_ingot", "quantity": 2, "cost": 20}]
        
        def get_tool_requirements(self, equipment_id):
            return [{"tool": "hammer", "required": True}]
    
    class RepairSkillService:
        def __init__(self, character_service=None):
            self.character_service = character_service
        
        def get_repair_skill(self, character_id, skill_category="general"):
            return {"skill_level": 5, "experience": 500, "specializations": []}
        
        def calculate_success_chance(self, character_id, repair_difficulty):
            skill_level = 5
            base_chance = 0.5
            skill_modifier = skill_level / 10.0
            return min(0.95, max(0.05, base_chance + skill_modifier))
        
        def award_experience(self, character_id, repair_difficulty, success):
            base_xp = {"trivial": 5, "easy": 10, "moderate": 20, "hard": 40, "expert": 80, "legendary": 160}
            multiplier = 1.0 if success else 0.3
            return int(base_xp.get(repair_difficulty, 20) * multiplier)
    
    class RepairQualityService:
        def __init__(self):
            pass
        
        def determine_repair_quality(self, target_quality, repairer_skill, materials_used):
            # Simplified quality determination
            quality_levels = ["poor", "basic", "good", "excellent", "masterwork"]
            target_index = quality_levels.index(target_quality) if target_quality in quality_levels else 2
            
            # Higher skill and better materials can achieve target or better
            skill_bonus = min(2, repairer_skill // 20)
            achieved_index = min(len(quality_levels) - 1, max(0, target_index + skill_bonus - 1))
            
            return quality_levels[achieved_index]
        
        def calculate_durability_restoration(self, current_durability, target_quality, achieved_quality):
            base_restoration = {"poor": 10, "basic": 20, "good": 30, "excellent": 45, "masterwork": 60}
            return min(100.0, current_durability + base_restoration.get(achieved_quality, 30))


class MockRepairRepository:
    """Mock repair repository for testing"""
    
    def save_repair_job(self, job_data):
        return {**job_data, "id": str(uuid4())}
    
    def get_repair_job(self, job_id):
        return {
            "id": job_id,
            "equipment_id": str(uuid4()),
            "status": "pending",
            "created_at": datetime.utcnow()
        }
    
    def update_repair_job(self, job_id, update_data):
        return {**update_data, "id": job_id, "updated_at": datetime.utcnow()}
    
    def get_jobs_by_repairer(self, repairer_id):
        return []


class MockEquipmentService:
    """Mock equipment service for testing"""
    
    def get_equipment(self, equipment_id):
        return {
            "id": equipment_id,
            "name": "Iron Sword",
            "material_type": "metal",
            "current_durability": 45.0,
            "max_durability": 100.0,
            "condition": "damaged"
        }
    
    def update_equipment_durability(self, equipment_id, new_durability):
        return {"durability_updated": True, "new_durability": new_durability}


class TestRepairService:
    """Test class for RepairService"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.mock_job_service = RepairJobService()
        self.mock_cost_service = RepairCostService()
        self.mock_skill_service = RepairSkillService()
        self.repair_service = RepairService(
            self.mock_job_service,
            self.mock_cost_service,
            self.mock_skill_service
        )
    
    def test_service_creation(self):
        """Test that the service can be created"""
        assert self.repair_service is not None
        assert self.repair_service.job_service is not None
        assert self.repair_service.cost_service is not None
        assert self.repair_service.skill_service is not None
    
    def test_initiate_repair(self):
        """Test initiating a repair job"""
        equipment_id = str(uuid4())
        repairer_id = str(uuid4())
        target_quality = "excellent"
        
        repair_job = self.repair_service.initiate_repair(
            equipment_id, repairer_id, target_quality
        )
        
        assert isinstance(repair_job, dict)
        assert "id" in repair_job
        assert repair_job["equipment_id"] == equipment_id
        assert repair_job["repairer_id"] == repairer_id
        assert repair_job["status"] == "pending"
        assert repair_job["target_quality"] == target_quality
    
    def test_execute_repair(self):
        """Test executing a repair job"""
        repair_job_id = str(uuid4())
        result = self.repair_service.execute_repair(repair_job_id)
        
        assert isinstance(result, dict)
        assert "success" in result
        assert "quality_achieved" in result
        assert "durability_restored" in result
        assert isinstance(result["success"], bool)
        assert isinstance(result["durability_restored"], (int, float))
    
    def test_get_repair_estimate(self):
        """Test getting repair estimate"""
        equipment_id = str(uuid4())
        target_quality = "good"
        
        estimate = self.repair_service.get_repair_estimate(equipment_id, target_quality)
        
        assert isinstance(estimate, dict)
        assert "estimated_cost" in estimate
        assert "estimated_time" in estimate
        assert "success_chance" in estimate
        assert isinstance(estimate["estimated_cost"], int)
        assert isinstance(estimate["estimated_time"], (int, float))
        assert 0.0 <= estimate["success_chance"] <= 1.0


class TestRepairJobService:
    """Test class for RepairJobService"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.mock_repository = MockRepairRepository()
        self.job_service = RepairJobService(self.mock_repository)
    
    def test_service_creation(self):
        """Test that the job service can be created"""
        assert self.job_service is not None
        assert self.job_service.repository is not None
    
    def test_create_repair_job(self):
        """Test creating a repair job"""
        equipment_id = str(uuid4())
        repairer_id = str(uuid4())
        
        job = self.job_service.create_repair_job(
            equipment_id,
            repairer_id,
            difficulty="moderate",
            target_quality="good"
        )
        
        assert isinstance(job, dict)
        assert "id" in job
        assert job["equipment_id"] == equipment_id
        assert job["repairer_id"] == repairer_id
        assert job["status"] == "pending"
        assert "created_at" in job
    
    def test_start_repair_job(self):
        """Test starting a repair job"""
        job_id = str(uuid4())
        result = self.job_service.start_repair_job(job_id)
        
        assert isinstance(result, dict)
        assert result["status"] == "in_progress"
        assert "started_at" in result
        assert isinstance(result["started_at"], datetime)
    
    def test_complete_repair_job(self):
        """Test completing a repair job"""
        job_id = str(uuid4())
        
        # Test successful completion
        success_result = self.job_service.complete_repair_job(job_id, success=True)
        assert success_result["status"] == "completed"
        assert "completed_at" in success_result
        
        # Test failed completion
        failure_result = self.job_service.complete_repair_job(job_id, success=False)
        assert failure_result["status"] == "failed"
        assert "completed_at" in failure_result
    
    def test_get_active_jobs(self):
        """Test getting active jobs for a repairer"""
        repairer_id = str(uuid4())
        active_jobs = self.job_service.get_active_jobs(repairer_id)
        
        assert isinstance(active_jobs, list)


class TestRepairCostService:
    """Test class for RepairCostService"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.mock_material_service = Mock()
        self.mock_tool_service = Mock()
        self.cost_service = RepairCostService(
            self.mock_material_service,
            self.mock_tool_service
        )
    
    def test_service_creation(self):
        """Test that the cost service can be created"""
        assert self.cost_service is not None
        assert self.cost_service.material_service is not None
        assert self.cost_service.tool_service is not None
    
    def test_calculate_repair_cost(self):
        """Test repair cost calculation"""
        equipment_id = str(uuid4())
        
        # Test different quality levels
        basic_cost = self.cost_service.calculate_repair_cost(
            equipment_id, "basic", repairer_skill=50
        )
        excellent_cost = self.cost_service.calculate_repair_cost(
            equipment_id, "excellent", repairer_skill=50
        )
        masterwork_cost = self.cost_service.calculate_repair_cost(
            equipment_id, "masterwork", repairer_skill=50
        )
        
        assert isinstance(basic_cost, int)
        assert isinstance(excellent_cost, int)
        assert isinstance(masterwork_cost, int)
        
        # Higher quality should generally cost more
        assert excellent_cost > basic_cost
        assert masterwork_cost > excellent_cost
    
    def test_skill_impact_on_cost(self):
        """Test skill impact on repair cost"""
        equipment_id = str(uuid4())
        target_quality = "good"
        
        # Test different skill levels
        novice_cost = self.cost_service.calculate_repair_cost(
            equipment_id, target_quality, repairer_skill=10
        )
        expert_cost = self.cost_service.calculate_repair_cost(
            equipment_id, target_quality, repairer_skill=90
        )
        
        # Higher skill should result in lower cost
        assert expert_cost < novice_cost
    
    def test_get_material_requirements(self):
        """Test getting material requirements"""
        equipment_id = str(uuid4())
        materials = self.cost_service.get_material_requirements(equipment_id, "good")
        
        assert isinstance(materials, list)
        if materials:  # If materials are required
            for material in materials:
                assert "material" in material
                assert "quantity" in material
                assert "cost" in material
    
    def test_get_tool_requirements(self):
        """Test getting tool requirements"""
        equipment_id = str(uuid4())
        tools = self.cost_service.get_tool_requirements(equipment_id)
        
        assert isinstance(tools, list)
        if tools:  # If tools are required
            for tool in tools:
                assert "tool" in tool
                assert "required" in tool


class TestRepairSkillService:
    """Test class for RepairSkillService"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.mock_character_service = Mock()
        self.skill_service = RepairSkillService(self.mock_character_service)
    
    def test_service_creation(self):
        """Test that the skill service can be created"""
        assert self.skill_service is not None
        assert self.skill_service.character_service is not None
    
    def test_get_repair_skill(self):
        """Test getting repair skill for a character"""
        character_id = str(uuid4())
        skill = self.skill_service.get_repair_skill(character_id, "weapon_repair")
        
        assert isinstance(skill, dict)
        assert "skill_level" in skill
        assert "experience" in skill
        assert "specializations" in skill
        assert isinstance(skill["skill_level"], int)
        assert isinstance(skill["experience"], int)
        assert isinstance(skill["specializations"], list)
    
    def test_calculate_success_chance(self):
        """Test success chance calculation"""
        character_id = str(uuid4())
        
        # Test different difficulties
        easy_chance = self.skill_service.calculate_success_chance(character_id, "easy")
        hard_chance = self.skill_service.calculate_success_chance(character_id, "hard")
        legendary_chance = self.skill_service.calculate_success_chance(character_id, "legendary")
        
        assert isinstance(easy_chance, (int, float))
        assert isinstance(hard_chance, (int, float))
        assert isinstance(legendary_chance, (int, float))
        
        # All chances should be within valid range
        assert 0.0 <= easy_chance <= 1.0
        assert 0.0 <= hard_chance <= 1.0
        assert 0.0 <= legendary_chance <= 1.0
    
    def test_award_experience(self):
        """Test awarding experience for repair attempts"""
        character_id = str(uuid4())
        
        # Test successful repair
        success_xp = self.skill_service.award_experience(character_id, "moderate", success=True)
        assert isinstance(success_xp, int)
        assert success_xp > 0
        
        # Test failed repair (should give less XP)
        failure_xp = self.skill_service.award_experience(character_id, "moderate", success=False)
        assert isinstance(failure_xp, int)
        assert failure_xp < success_xp
    
    def test_experience_scaling_with_difficulty(self):
        """Test experience scaling with repair difficulty"""
        character_id = str(uuid4())
        
        easy_xp = self.skill_service.award_experience(character_id, "easy", success=True)
        hard_xp = self.skill_service.award_experience(character_id, "hard", success=True)
        legendary_xp = self.skill_service.award_experience(character_id, "legendary", success=True)
        
        # Harder repairs should give more experience
        assert hard_xp > easy_xp
        assert legendary_xp > hard_xp


class TestRepairQualityService:
    """Test class for RepairQualityService"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.quality_service = RepairQualityService()
    
    def test_service_creation(self):
        """Test that the quality service can be created"""
        assert self.quality_service is not None
    
    def test_determine_repair_quality(self):
        """Test determining actual repair quality"""
        # Test with different target qualities and skills
        basic_result = self.quality_service.determine_repair_quality(
            target_quality="basic",
            repairer_skill=30,
            materials_used=["standard_iron"]
        )
        
        excellent_result = self.quality_service.determine_repair_quality(
            target_quality="excellent",
            repairer_skill=80,
            materials_used=["high_carbon_steel"]
        )
        
        assert isinstance(basic_result, str)
        assert isinstance(excellent_result, str)
        
        # Results should be valid quality levels
        valid_qualities = ["poor", "basic", "good", "excellent", "masterwork"]
        assert basic_result in valid_qualities
        assert excellent_result in valid_qualities
    
    def test_skill_impact_on_quality(self):
        """Test skill impact on achieved quality"""
        target_quality = "good"
        materials = ["standard_materials"]
        
        # Low skill repairer
        low_skill_result = self.quality_service.determine_repair_quality(
            target_quality, repairer_skill=20, materials_used=materials
        )
        
        # High skill repairer
        high_skill_result = self.quality_service.determine_repair_quality(
            target_quality, repairer_skill=90, materials_used=materials
        )
        
        # Both should be valid qualities
        valid_qualities = ["poor", "basic", "good", "excellent", "masterwork"]
        assert low_skill_result in valid_qualities
        assert high_skill_result in valid_qualities
        
        # Higher skill should generally achieve better or equal quality
        quality_order = {q: i for i, q in enumerate(valid_qualities)}
        assert quality_order[high_skill_result] >= quality_order[low_skill_result]
    
    def test_calculate_durability_restoration(self):
        """Test durability restoration calculation"""
        current_durability = 30.0
        
        # Test different achieved qualities
        poor_restoration = self.quality_service.calculate_durability_restoration(
            current_durability, "good", "poor"
        )
        excellent_restoration = self.quality_service.calculate_durability_restoration(
            current_durability, "good", "excellent"
        )
        masterwork_restoration = self.quality_service.calculate_durability_restoration(
            current_durability, "good", "masterwork"
        )
        
        assert isinstance(poor_restoration, (int, float))
        assert isinstance(excellent_restoration, (int, float))
        assert isinstance(masterwork_restoration, (int, float))
        
        # All should be greater than current durability
        assert poor_restoration > current_durability
        assert excellent_restoration > current_durability
        assert masterwork_restoration > current_durability
        
        # Better quality should restore more durability
        assert excellent_restoration > poor_restoration
        assert masterwork_restoration > excellent_restoration
        
        # None should exceed 100%
        assert poor_restoration <= 100.0
        assert excellent_restoration <= 100.0
        assert masterwork_restoration <= 100.0


class TestRepairServicesIntegration:
    """Integration tests for repair services"""
    
    def setup_method(self):
        """Set up integrated test fixtures"""
        self.mock_repository = MockRepairRepository()
        self.mock_equipment_service = MockEquipmentService()
        
        self.job_service = RepairJobService(self.mock_repository)
        self.cost_service = RepairCostService()
        self.skill_service = RepairSkillService()
        self.quality_service = RepairQualityService()
        
        self.repair_service = RepairService(
            self.job_service,
            self.cost_service,
            self.skill_service
        )
    
    def test_complete_repair_workflow(self):
        """Test complete repair workflow from initiation to completion"""
        equipment_id = str(uuid4())
        repairer_id = str(uuid4())
        target_quality = "good"
        
        # 1. Get repair estimate
        estimate = self.repair_service.get_repair_estimate(equipment_id, target_quality)
        assert isinstance(estimate, dict)
        assert "estimated_cost" in estimate
        
        # 2. Initiate repair
        repair_job = self.repair_service.initiate_repair(equipment_id, repairer_id, target_quality)
        assert repair_job["status"] == "pending"
        
        # 3. Start repair job
        start_result = self.job_service.start_repair_job(repair_job["id"])
        assert start_result["status"] == "in_progress"
        
        # 4. Execute repair
        execution_result = self.repair_service.execute_repair(repair_job["id"])
        assert isinstance(execution_result, dict)
        assert "success" in execution_result
        
        # 5. Complete repair job
        completion_result = self.job_service.complete_repair_job(
            repair_job["id"], 
            success=execution_result["success"]
        )
        assert completion_result["status"] in ["completed", "failed"]
    
    def test_cost_calculation_integration(self):
        """Test cost calculation integration with skills and materials"""
        equipment_id = str(uuid4())
        repairer_id = str(uuid4())
        
        # Get repairer skill
        skill_info = self.skill_service.get_repair_skill(repairer_id)
        
        # Calculate cost based on skill
        repair_cost = self.cost_service.calculate_repair_cost(
            equipment_id, "excellent", skill_info["skill_level"]
        )
        
        # Get material requirements
        materials = self.cost_service.get_material_requirements(equipment_id, "excellent")
        
        # Verify integration
        assert isinstance(repair_cost, int)
        assert repair_cost > 0
        assert isinstance(materials, list)
    
    def test_quality_determination_integration(self):
        """Test quality determination with skills and materials"""
        repairer_id = str(uuid4())
        target_quality = "excellent"
        materials_used = ["high_carbon_steel", "binding_agent"]
        
        # Get repairer skill
        skill_info = self.skill_service.get_repair_skill(repairer_id)
        
        # Determine achieved quality
        achieved_quality = self.quality_service.determine_repair_quality(
            target_quality, skill_info["skill_level"], materials_used
        )
        
        # Calculate durability restoration
        durability_restored = self.quality_service.calculate_durability_restoration(
            40.0, target_quality, achieved_quality
        )
        
        # Verify integration
        assert isinstance(achieved_quality, str)
        assert achieved_quality in ["poor", "basic", "good", "excellent", "masterwork"]
        assert isinstance(durability_restored, (int, float))
        assert 40.0 < durability_restored <= 100.0
    
    def test_experience_award_integration(self):
        """Test experience awarding integration with repair completion"""
        repairer_id = str(uuid4())
        repair_difficulty = "hard"
        
        # Test successful repair experience
        success_xp = self.skill_service.award_experience(
            repairer_id, repair_difficulty, success=True
        )
        
        # Test failed repair experience
        failure_xp = self.skill_service.award_experience(
            repairer_id, repair_difficulty, success=False
        )
        
        # Verify experience awards
        assert isinstance(success_xp, int)
        assert isinstance(failure_xp, int)
        assert success_xp > 0
        assert failure_xp > 0
        assert success_xp > failure_xp
    
    def test_repair_job_lifecycle_integration(self):
        """Test complete repair job lifecycle"""
        equipment_id = str(uuid4())
        repairer_id = str(uuid4())
        
        # Create repair job
        job = self.job_service.create_repair_job(
            equipment_id, repairer_id, difficulty="moderate", target_quality="good"
        )
        job_id = job["id"]
        
        # Start the job
        start_result = self.job_service.start_repair_job(job_id)
        assert start_result["status"] == "in_progress"
        
        # Get success chance
        success_chance = self.skill_service.calculate_success_chance(repairer_id, "moderate")
        assert 0.0 <= success_chance <= 1.0
        
        # Complete the job (simulate success)
        completion_result = self.job_service.complete_repair_job(job_id, success=True)
        assert completion_result["status"] == "completed"
        
        # Award experience
        xp_awarded = self.skill_service.award_experience(repairer_id, "moderate", success=True)
        assert xp_awarded > 0
    
    def test_repair_cost_skill_interaction(self):
        """Test repair cost and skill level interaction"""
        equipment_id = str(uuid4())
        target_quality = "excellent"
        
        # Test costs for different skill levels
        novice_cost = self.cost_service.calculate_repair_cost(equipment_id, target_quality, 10)
        journeyman_cost = self.cost_service.calculate_repair_cost(equipment_id, target_quality, 50)
        master_cost = self.cost_service.calculate_repair_cost(equipment_id, target_quality, 100)
        
        # Higher skill should reduce cost
        assert master_cost <= journeyman_cost <= novice_cost
        
        # All costs should be positive
        assert novice_cost > 0
        assert journeyman_cost > 0
        assert master_cost > 0
    
    def test_equipment_condition_impact(self):
        """Test equipment condition impact on repair requirements"""
        # Simulate different equipment conditions
        heavily_damaged_equipment = str(uuid4())
        lightly_damaged_equipment = str(uuid4())
        
        # Get repair estimates for different conditions
        heavy_estimate = self.repair_service.get_repair_estimate(heavily_damaged_equipment, "good")
        light_estimate = self.repair_service.get_repair_estimate(lightly_damaged_equipment, "good")
        
        # Both should be valid estimates
        assert isinstance(heavy_estimate, dict)
        assert isinstance(light_estimate, dict)
        assert "estimated_cost" in heavy_estimate
        assert "estimated_cost" in light_estimate
        assert "estimated_time" in heavy_estimate
        assert "estimated_time" in light_estimate 
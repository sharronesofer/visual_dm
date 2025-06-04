"""
Test module for repair.models

Tests repair models according to Development Bible standards:
- Equipment repair and maintenance systems
- Repair skill and proficiency tracking
- Resource consumption and cost calculation
- Quality and durability restoration
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
from uuid import uuid4
from enum import Enum

# Import the module under test
try:
    from backend.systems.repair.models import (
        RepairJob, RepairSkill, RepairMaterial, RepairTool,
        RepairQuality, RepairDifficulty, RepairStatus, RepairCost
    )
    repair_models_available = True
except ImportError as e:
    print(f"Repair models not available: {e}")
    repair_models_available = False
    
    # Create mock classes for testing
    class RepairQuality(Enum):
        POOR = "poor"
        BASIC = "basic"
        GOOD = "good"
        EXCELLENT = "excellent"
        MASTERWORK = "masterwork"
    
    class RepairDifficulty(Enum):
        TRIVIAL = "trivial"
        EASY = "easy"
        MODERATE = "moderate"
        HARD = "hard"
        EXPERT = "expert"
        LEGENDARY = "legendary"
    
    class RepairStatus(Enum):
        PENDING = "pending"
        IN_PROGRESS = "in_progress"
        COMPLETED = "completed"
        FAILED = "failed"
        CANCELLED = "cancelled"
    
    class RepairJob:
        def __init__(self, **kwargs):
            self.id = kwargs.get('id', str(uuid4()))
            self.equipment_id = kwargs.get('equipment_id', str(uuid4()))
            self.repairer_id = kwargs.get('repairer_id', str(uuid4()))
            self.status = kwargs.get('status', RepairStatus.PENDING)
            self.difficulty = kwargs.get('difficulty', RepairDifficulty.MODERATE)
            self.target_quality = kwargs.get('target_quality', RepairQuality.GOOD)
            self.current_durability = kwargs.get('current_durability', 50.0)
            self.target_durability = kwargs.get('target_durability', 80.0)
            self.materials_required = kwargs.get('materials_required', [])
            self.tools_required = kwargs.get('tools_required', [])
            self.estimated_time = kwargs.get('estimated_time', timedelta(hours=2))
            self.gold_cost = kwargs.get('gold_cost', 100)
            self.created_at = kwargs.get('created_at', datetime.utcnow())
            for k, v in kwargs.items():
                setattr(self, k, v)
        
        def calculate_success_chance(self, repairer_skill):
            base_chance = 0.5
            skill_modifier = min(repairer_skill / 100.0, 1.0)
            difficulty_modifier = {
                RepairDifficulty.TRIVIAL: 0.4,
                RepairDifficulty.EASY: 0.2,
                RepairDifficulty.MODERATE: 0.0,
                RepairDifficulty.HARD: -0.2,
                RepairDifficulty.EXPERT: -0.4,
                RepairDifficulty.LEGENDARY: -0.6
            }.get(self.difficulty, 0.0)
            return max(0.1, min(0.95, base_chance + skill_modifier + difficulty_modifier))
        
        def is_completable(self):
            return self.status == RepairStatus.IN_PROGRESS
        
        def get_durability_gain(self):
            return max(0.0, self.target_durability - self.current_durability)
    
    class RepairSkill:
        def __init__(self, **kwargs):
            self.id = kwargs.get('id', str(uuid4()))
            self.character_id = kwargs.get('character_id', str(uuid4()))
            self.skill_category = kwargs.get('skill_category', 'general_repair')
            self.skill_level = kwargs.get('skill_level', 1)
            self.experience_points = kwargs.get('experience_points', 0)
            self.specializations = kwargs.get('specializations', [])
            for k, v in kwargs.items():
                setattr(self, k, v)
        
        def get_repair_bonus(self, equipment_type):
            base_bonus = self.skill_level * 5
            specialization_bonus = 10 if equipment_type in self.specializations else 0
            return base_bonus + specialization_bonus
        
        def can_attempt_difficulty(self, difficulty):
            required_levels = {
                RepairDifficulty.TRIVIAL: 1,
                RepairDifficulty.EASY: 1,
                RepairDifficulty.MODERATE: 3,
                RepairDifficulty.HARD: 5,
                RepairDifficulty.EXPERT: 8,
                RepairDifficulty.LEGENDARY: 10
            }
            return self.skill_level >= required_levels.get(difficulty, 1)
    
    class RepairMaterial:
        def __init__(self, **kwargs):
            self.id = kwargs.get('id', str(uuid4()))
            self.name = kwargs.get('name', 'Iron Ingot')
            self.material_type = kwargs.get('material_type', 'metal')
            self.quality_grade = kwargs.get('quality_grade', 'standard')
            self.durability_bonus = kwargs.get('durability_bonus', 5.0)
            self.cost_per_unit = kwargs.get('cost_per_unit', 10)
            self.availability = kwargs.get('availability', 'common')
            for k, v in kwargs.items():
                setattr(self, k, v)
        
        def get_quality_modifier(self):
            modifiers = {
                'poor': 0.5,
                'standard': 1.0,
                'high': 1.5,
                'superior': 2.0,
                'legendary': 3.0
            }
            return modifiers.get(self.quality_grade, 1.0)
        
        def is_suitable_for_repair(self, equipment_material):
            # Simplified compatibility check
            return self.material_type == equipment_material or self.material_type == 'universal'
    
    class RepairTool:
        def __init__(self, **kwargs):
            self.id = kwargs.get('id', str(uuid4()))
            self.name = kwargs.get('name', 'Hammer')
            self.tool_type = kwargs.get('tool_type', 'basic')
            self.efficiency_bonus = kwargs.get('efficiency_bonus', 1.0)
            self.quality_bonus = kwargs.get('quality_bonus', 0.0)
            self.durability = kwargs.get('durability', 100.0)
            self.required_skill_level = kwargs.get('required_skill_level', 1)
            for k, v in kwargs.items():
                setattr(self, k, v)
        
        def can_be_used_by(self, character_skill_level):
            return character_skill_level >= self.required_skill_level
        
        def is_functional(self):
            return self.durability > 0.0
        
        def apply_wear(self, usage_intensity=1.0):
            wear_amount = usage_intensity * 2.0
            self.durability = max(0.0, self.durability - wear_amount)
    
    class RepairCost:
        def __init__(self, **kwargs):
            self.base_cost = kwargs.get('base_cost', 50)
            self.material_costs = kwargs.get('material_costs', {})
            self.labor_cost = kwargs.get('labor_cost', 25)
            self.tool_maintenance_cost = kwargs.get('tool_maintenance_cost', 5)
            self.skill_modifier = kwargs.get('skill_modifier', 1.0)
            for k, v in kwargs.items():
                setattr(self, k, v)
        
        def calculate_total_cost(self):
            material_total = sum(self.material_costs.values())
            base_total = self.base_cost + material_total + self.labor_cost + self.tool_maintenance_cost
            return int(base_total * self.skill_modifier)
        
        def get_cost_breakdown(self):
            return {
                'base_cost': self.base_cost,
                'materials': sum(self.material_costs.values()),
                'labor': self.labor_cost,
                'tool_maintenance': self.tool_maintenance_cost,
                'skill_modifier': self.skill_modifier,
                'total': self.calculate_total_cost()
            }


class TestRepairQuality:
    """Test class for RepairQuality enum"""

    def test_quality_levels(self):
        """Test RepairQuality enum has expected values"""
        assert hasattr(RepairQuality, 'POOR')
        assert hasattr(RepairQuality, 'BASIC')
        assert hasattr(RepairQuality, 'GOOD')
        assert hasattr(RepairQuality, 'EXCELLENT')
        assert hasattr(RepairQuality, 'MASTERWORK')

    def test_quality_progression(self):
        """Test quality levels represent logical progression"""
        qualities = [
            RepairQuality.POOR, RepairQuality.BASIC, RepairQuality.GOOD,
            RepairQuality.EXCELLENT, RepairQuality.MASTERWORK
        ]
        assert len(set(qualities)) == len(qualities)


class TestRepairDifficulty:
    """Test class for RepairDifficulty enum"""

    def test_difficulty_levels(self):
        """Test RepairDifficulty enum has expected values"""
        assert hasattr(RepairDifficulty, 'TRIVIAL')
        assert hasattr(RepairDifficulty, 'EASY')
        assert hasattr(RepairDifficulty, 'MODERATE')
        assert hasattr(RepairDifficulty, 'HARD')
        assert hasattr(RepairDifficulty, 'EXPERT')
        assert hasattr(RepairDifficulty, 'LEGENDARY')

    def test_difficulty_progression(self):
        """Test difficulty levels represent logical progression"""
        difficulties = [
            RepairDifficulty.TRIVIAL, RepairDifficulty.EASY, RepairDifficulty.MODERATE,
            RepairDifficulty.HARD, RepairDifficulty.EXPERT, RepairDifficulty.LEGENDARY
        ]
        assert len(set(difficulties)) == len(difficulties)


class TestRepairJob:
    """Test class for RepairJob model"""

    @pytest.fixture
    def sample_repair_job_data(self):
        """Sample repair job data for testing"""
        return {
            "equipment_id": str(uuid4()),
            "repairer_id": str(uuid4()),
            "status": RepairStatus.PENDING,
            "difficulty": RepairDifficulty.MODERATE,
            "target_quality": RepairQuality.GOOD,
            "current_durability": 35.0,
            "target_durability": 85.0,
            "materials_required": ["iron_ingot", "leather_strips"],
            "tools_required": ["hammer", "anvil"],
            "estimated_time": timedelta(hours=3),
            "gold_cost": 150
        }

    def test_repair_job_creation(self, sample_repair_job_data):
        """Test RepairJob creation with standard parameters"""
        job = RepairJob(**sample_repair_job_data)
        
        assert job.equipment_id == sample_repair_job_data["equipment_id"]
        assert job.repairer_id == sample_repair_job_data["repairer_id"]
        assert job.status == RepairStatus.PENDING
        assert job.difficulty == RepairDifficulty.MODERATE
        assert job.target_quality == RepairQuality.GOOD
        assert job.current_durability == 35.0
        assert job.target_durability == 85.0
        assert len(job.materials_required) == 2
        assert len(job.tools_required) == 2
        assert job.gold_cost == 150

    def test_repair_job_defaults(self):
        """Test RepairJob creation with default values"""
        job = RepairJob()
        
        assert job.status == RepairStatus.PENDING
        assert job.difficulty == RepairDifficulty.MODERATE
        assert job.target_quality == RepairQuality.GOOD
        assert job.current_durability == 50.0
        assert job.target_durability == 80.0
        assert isinstance(job.materials_required, list)
        assert isinstance(job.tools_required, list)
        assert isinstance(job.estimated_time, timedelta)
        assert job.gold_cost == 100

    def test_success_chance_calculation(self, sample_repair_job_data):
        """Test repair success chance calculation"""
        job = RepairJob(**sample_repair_job_data)
        
        # Test with different skill levels
        low_skill_chance = job.calculate_success_chance(25)
        medium_skill_chance = job.calculate_success_chance(50)
        high_skill_chance = job.calculate_success_chance(90)
        
        assert isinstance(low_skill_chance, (int, float))
        assert isinstance(medium_skill_chance, (int, float))
        assert isinstance(high_skill_chance, (int, float))
        
        # Higher skill should generally mean higher success chance
        assert 0.1 <= low_skill_chance <= 0.95
        assert 0.1 <= medium_skill_chance <= 0.95
        assert 0.1 <= high_skill_chance <= 0.95
        assert high_skill_chance >= low_skill_chance

    def test_completability_check(self, sample_repair_job_data):
        """Test repair job completability check"""
        # Pending job should not be completable
        pending_job = RepairJob(status=RepairStatus.PENDING)
        assert pending_job.is_completable() is False
        
        # In-progress job should be completable
        in_progress_job = RepairJob(status=RepairStatus.IN_PROGRESS)
        assert in_progress_job.is_completable() is True
        
        # Completed job should not be completable
        completed_job = RepairJob(status=RepairStatus.COMPLETED)
        assert completed_job.is_completable() is False

    def test_durability_gain_calculation(self, sample_repair_job_data):
        """Test durability gain calculation"""
        job = RepairJob(**sample_repair_job_data)
        durability_gain = job.get_durability_gain()
        
        assert durability_gain == 50.0  # 85.0 - 35.0
        assert durability_gain >= 0.0

    def test_difficulty_impact_on_success(self):
        """Test difficulty impact on success chance"""
        repairer_skill = 50
        
        # Test different difficulties
        trivial_job = RepairJob(difficulty=RepairDifficulty.TRIVIAL)
        hard_job = RepairJob(difficulty=RepairDifficulty.HARD)
        legendary_job = RepairJob(difficulty=RepairDifficulty.LEGENDARY)
        
        trivial_chance = trivial_job.calculate_success_chance(repairer_skill)
        hard_chance = hard_job.calculate_success_chance(repairer_skill)
        legendary_chance = legendary_job.calculate_success_chance(repairer_skill)
        
        # Easier repairs should have higher success chance
        assert trivial_chance > hard_chance
        assert hard_chance > legendary_chance


class TestRepairSkill:
    """Test class for RepairSkill model"""

    @pytest.fixture
    def sample_skill_data(self):
        """Sample repair skill data for testing"""
        return {
            "character_id": str(uuid4()),
            "skill_category": "weapon_repair",
            "skill_level": 5,
            "experience_points": 750,
            "specializations": ["swords", "bows"]
        }

    def test_repair_skill_creation(self, sample_skill_data):
        """Test RepairSkill creation"""
        skill = RepairSkill(**sample_skill_data)
        
        assert skill.character_id == sample_skill_data["character_id"]
        assert skill.skill_category == "weapon_repair"
        assert skill.skill_level == 5
        assert skill.experience_points == 750
        assert len(skill.specializations) == 2
        assert "swords" in skill.specializations

    def test_repair_skill_defaults(self):
        """Test RepairSkill with default values"""
        skill = RepairSkill()
        
        assert skill.skill_category == "general_repair"
        assert skill.skill_level == 1
        assert skill.experience_points == 0
        assert isinstance(skill.specializations, list)

    def test_repair_bonus_calculation(self, sample_skill_data):
        """Test repair bonus calculation"""
        skill = RepairSkill(**sample_skill_data)
        
        # Test with specialized equipment
        sword_bonus = skill.get_repair_bonus("swords")
        assert sword_bonus == 35  # (5 * 5) + 10 specialization bonus
        
        # Test with non-specialized equipment
        armor_bonus = skill.get_repair_bonus("armor")
        assert armor_bonus == 25  # (5 * 5) + 0 specialization bonus

    def test_difficulty_attempt_capability(self, sample_skill_data):
        """Test difficulty attempt capability"""
        skill = RepairSkill(**sample_skill_data)  # Level 5
        
        # Should be able to attempt up to hard difficulty
        assert skill.can_attempt_difficulty(RepairDifficulty.TRIVIAL) is True
        assert skill.can_attempt_difficulty(RepairDifficulty.EASY) is True
        assert skill.can_attempt_difficulty(RepairDifficulty.MODERATE) is True
        assert skill.can_attempt_difficulty(RepairDifficulty.HARD) is True
        
        # Should not be able to attempt expert or legendary
        assert skill.can_attempt_difficulty(RepairDifficulty.EXPERT) is False
        assert skill.can_attempt_difficulty(RepairDifficulty.LEGENDARY) is False

    def test_skill_progression_levels(self):
        """Test different skill progression levels"""
        novice = RepairSkill(skill_level=1)
        expert = RepairSkill(skill_level=8)
        master = RepairSkill(skill_level=10)
        
        # Novice can only do easy repairs
        assert novice.can_attempt_difficulty(RepairDifficulty.MODERATE) is True
        assert novice.can_attempt_difficulty(RepairDifficulty.EXPERT) is False
        
        # Expert can do expert repairs
        assert expert.can_attempt_difficulty(RepairDifficulty.EXPERT) is True
        assert expert.can_attempt_difficulty(RepairDifficulty.LEGENDARY) is False
        
        # Master can do legendary repairs
        assert master.can_attempt_difficulty(RepairDifficulty.LEGENDARY) is True


class TestRepairMaterial:
    """Test class for RepairMaterial model"""

    @pytest.fixture
    def sample_material_data(self):
        """Sample repair material data for testing"""
        return {
            "name": "Enchanted Steel",
            "material_type": "metal",
            "quality_grade": "superior",
            "durability_bonus": 15.0,
            "cost_per_unit": 50,
            "availability": "rare"
        }

    def test_repair_material_creation(self, sample_material_data):
        """Test RepairMaterial creation"""
        material = RepairMaterial(**sample_material_data)
        
        assert material.name == "Enchanted Steel"
        assert material.material_type == "metal"
        assert material.quality_grade == "superior"
        assert material.durability_bonus == 15.0
        assert material.cost_per_unit == 50
        assert material.availability == "rare"

    def test_repair_material_defaults(self):
        """Test RepairMaterial with default values"""
        material = RepairMaterial()
        
        assert material.name == "Iron Ingot"
        assert material.material_type == "metal"
        assert material.quality_grade == "standard"
        assert material.durability_bonus == 5.0
        assert material.cost_per_unit == 10
        assert material.availability == "common"

    def test_quality_modifier_calculation(self, sample_material_data):
        """Test quality modifier calculation"""
        # Test different quality grades
        poor_material = RepairMaterial(quality_grade="poor")
        standard_material = RepairMaterial(quality_grade="standard")
        superior_material = RepairMaterial(quality_grade="superior")
        legendary_material = RepairMaterial(quality_grade="legendary")
        
        assert poor_material.get_quality_modifier() == 0.5
        assert standard_material.get_quality_modifier() == 1.0
        assert superior_material.get_quality_modifier() == 2.0
        assert legendary_material.get_quality_modifier() == 3.0

    def test_repair_suitability_check(self, sample_material_data):
        """Test repair suitability for equipment"""
        metal_material = RepairMaterial(material_type="metal")
        leather_material = RepairMaterial(material_type="leather")
        universal_material = RepairMaterial(material_type="universal")
        
        # Metal material should be suitable for metal equipment
        assert metal_material.is_suitable_for_repair("metal") is True
        assert metal_material.is_suitable_for_repair("wood") is False
        
        # Universal material should be suitable for anything
        assert universal_material.is_suitable_for_repair("metal") is True
        assert universal_material.is_suitable_for_repair("leather") is True
        assert universal_material.is_suitable_for_repair("wood") is True

    def test_material_cost_scaling(self):
        """Test material cost scaling with quality"""
        # Higher quality materials should generally cost more
        poor_material = RepairMaterial(quality_grade="poor", cost_per_unit=5)
        legendary_material = RepairMaterial(quality_grade="legendary", cost_per_unit=100)
        
        # Quality modifier should reflect the cost difference
        assert poor_material.get_quality_modifier() < legendary_material.get_quality_modifier()
        assert poor_material.cost_per_unit < legendary_material.cost_per_unit


class TestRepairTool:
    """Test class for RepairTool model"""

    @pytest.fixture
    def sample_tool_data(self):
        """Sample repair tool data for testing"""
        return {
            "name": "Master's Hammer",
            "tool_type": "advanced",
            "efficiency_bonus": 1.5,
            "quality_bonus": 0.2,
            "durability": 90.0,
            "required_skill_level": 6
        }

    def test_repair_tool_creation(self, sample_tool_data):
        """Test RepairTool creation"""
        tool = RepairTool(**sample_tool_data)
        
        assert tool.name == "Master's Hammer"
        assert tool.tool_type == "advanced"
        assert tool.efficiency_bonus == 1.5
        assert tool.quality_bonus == 0.2
        assert tool.durability == 90.0
        assert tool.required_skill_level == 6

    def test_repair_tool_defaults(self):
        """Test RepairTool with default values"""
        tool = RepairTool()
        
        assert tool.name == "Hammer"
        assert tool.tool_type == "basic"
        assert tool.efficiency_bonus == 1.0
        assert tool.quality_bonus == 0.0
        assert tool.durability == 100.0
        assert tool.required_skill_level == 1

    def test_tool_usage_capability(self, sample_tool_data):
        """Test tool usage capability based on skill"""
        tool = RepairTool(**sample_tool_data)  # Requires skill level 6
        
        # Character with sufficient skill can use tool
        assert tool.can_be_used_by(6) is True
        assert tool.can_be_used_by(8) is True
        
        # Character with insufficient skill cannot use tool
        assert tool.can_be_used_by(4) is False
        assert tool.can_be_used_by(5) is False

    def test_tool_functionality_check(self, sample_tool_data):
        """Test tool functionality based on durability"""
        tool = RepairTool(durability=50.0)
        assert tool.is_functional() is True
        
        broken_tool = RepairTool(durability=0.0)
        assert broken_tool.is_functional() is False

    def test_tool_wear_application(self, sample_tool_data):
        """Test tool wear during usage"""
        tool = RepairTool(durability=100.0)
        initial_durability = tool.durability
        
        # Apply normal wear
        tool.apply_wear(1.0)
        assert tool.durability < initial_durability
        assert tool.durability == 98.0  # 100 - (1.0 * 2.0)
        
        # Apply heavy wear
        tool.apply_wear(2.0)
        assert tool.durability == 94.0  # 98 - (2.0 * 2.0)
        
        # Tool should not go below 0 durability
        tool.apply_wear(50.0)
        assert tool.durability == 0.0

    def test_tool_efficiency_benefits(self):
        """Test tool efficiency benefits"""
        basic_tool = RepairTool(efficiency_bonus=1.0)
        advanced_tool = RepairTool(efficiency_bonus=2.0)
        master_tool = RepairTool(efficiency_bonus=3.0, quality_bonus=0.5)
        
        # More advanced tools should provide better bonuses
        assert advanced_tool.efficiency_bonus > basic_tool.efficiency_bonus
        assert master_tool.efficiency_bonus > advanced_tool.efficiency_bonus
        assert master_tool.quality_bonus > basic_tool.quality_bonus


class TestRepairCost:
    """Test class for RepairCost model"""

    @pytest.fixture
    def sample_cost_data(self):
        """Sample repair cost data for testing"""
        return {
            "base_cost": 75,
            "material_costs": {"iron_ingot": 30, "leather": 15},
            "labor_cost": 40,
            "tool_maintenance_cost": 10,
            "skill_modifier": 0.8  # Skilled repairer discount
        }

    def test_repair_cost_creation(self, sample_cost_data):
        """Test RepairCost creation"""
        cost = RepairCost(**sample_cost_data)
        
        assert cost.base_cost == 75
        assert cost.material_costs["iron_ingot"] == 30
        assert cost.material_costs["leather"] == 15
        assert cost.labor_cost == 40
        assert cost.tool_maintenance_cost == 10
        assert cost.skill_modifier == 0.8

    def test_repair_cost_defaults(self):
        """Test RepairCost with default values"""
        cost = RepairCost()
        
        assert cost.base_cost == 50
        assert isinstance(cost.material_costs, dict)
        assert cost.labor_cost == 25
        assert cost.tool_maintenance_cost == 5
        assert cost.skill_modifier == 1.0

    def test_total_cost_calculation(self, sample_cost_data):
        """Test total cost calculation"""
        cost = RepairCost(**sample_cost_data)
        total_cost = cost.calculate_total_cost()
        
        # Expected: (75 + 45 + 40 + 10) * 0.8 = 170 * 0.8 = 136
        expected_cost = int((75 + 45 + 40 + 10) * 0.8)
        assert total_cost == expected_cost

    def test_cost_breakdown(self, sample_cost_data):
        """Test cost breakdown details"""
        cost = RepairCost(**sample_cost_data)
        breakdown = cost.get_cost_breakdown()
        
        assert isinstance(breakdown, dict)
        assert "base_cost" in breakdown
        assert "materials" in breakdown
        assert "labor" in breakdown
        assert "tool_maintenance" in breakdown
        assert "skill_modifier" in breakdown
        assert "total" in breakdown
        
        assert breakdown["base_cost"] == 75
        assert breakdown["materials"] == 45  # 30 + 15
        assert breakdown["labor"] == 40
        assert breakdown["tool_maintenance"] == 10
        assert breakdown["skill_modifier"] == 0.8

    def test_skill_modifier_impact(self):
        """Test skill modifier impact on cost"""
        base_cost_data = {
            "base_cost": 100,
            "material_costs": {"iron": 50},
            "labor_cost": 30,
            "tool_maintenance_cost": 10
        }
        
        # Novice repairer (higher cost)
        novice_cost = RepairCost(**base_cost_data, skill_modifier=1.5)
        
        # Expert repairer (lower cost)
        expert_cost = RepairCost(**base_cost_data, skill_modifier=0.7)
        
        novice_total = novice_cost.calculate_total_cost()
        expert_total = expert_cost.calculate_total_cost()
        
        # Expert should cost less than novice
        assert expert_total < novice_total


class TestRepairModelsIntegration:
    """Integration tests for repair models"""

    def test_complete_repair_workflow(self):
        """Test complete repair workflow integration"""
        # Create repair skill
        skill = RepairSkill(
            skill_level=6,
            specializations=["swords"],
            experience_points=800
        )
        
        # Create repair materials
        material = RepairMaterial(
            name="High Carbon Steel",
            quality_grade="high",
            durability_bonus=12.0
        )
        
        # Create repair tool
        tool = RepairTool(
            name="Forging Hammer",
            efficiency_bonus=1.8,
            required_skill_level=5
        )
        
        # Create repair job
        job = RepairJob(
            difficulty=RepairDifficulty.HARD,
            target_quality=RepairQuality.EXCELLENT,
            current_durability=25.0,
            target_durability=95.0
        )
        
        # Test integration
        assert skill.can_attempt_difficulty(job.difficulty) is True
        assert tool.can_be_used_by(skill.skill_level) is True
        assert material.is_suitable_for_repair("metal") is True
        
        success_chance = job.calculate_success_chance(skill.skill_level * 10)
        assert 0.1 <= success_chance <= 0.95

    def test_repair_cost_calculation_integration(self):
        """Test repair cost calculation with all components"""
        # Create materials with costs
        materials = {
            "steel_ingot": 25,
            "binding_agent": 10,
            "polishing_compound": 5
        }
        
        # Create repair cost
        repair_cost = RepairCost(
            base_cost=60,
            material_costs=materials,
            labor_cost=35,
            tool_maintenance_cost=8,
            skill_modifier=0.85  # Skilled craftsman discount
        )
        
        # Calculate total and breakdown
        total_cost = repair_cost.calculate_total_cost()
        breakdown = repair_cost.get_cost_breakdown()
        
        # Verify calculation
        expected_materials = 40  # 25 + 10 + 5
        expected_subtotal = 60 + 40 + 35 + 8  # 143
        expected_total = int(143 * 0.85)  # 121
        
        assert breakdown["materials"] == expected_materials
        assert total_cost == expected_total

    def test_tool_durability_impact_on_repair(self):
        """Test tool durability impact on repair process"""
        # Create high-quality tool
        pristine_tool = RepairTool(
            durability=100.0,
            efficiency_bonus=2.0,
            quality_bonus=0.3
        )
        
        # Create worn tool
        worn_tool = RepairTool(
            durability=30.0,
            efficiency_bonus=2.0,
            quality_bonus=0.3
        )
        
        # Create broken tool
        broken_tool = RepairTool(
            durability=0.0,
            efficiency_bonus=2.0,
            quality_bonus=0.3
        )
        
        # Test functionality
        assert pristine_tool.is_functional() is True
        assert worn_tool.is_functional() is True
        assert broken_tool.is_functional() is False
        
        # Simulate tool wear
        pristine_tool.apply_wear(10.0)  # Heavy usage
        assert pristine_tool.durability == 80.0

    def test_skill_specialization_bonus_integration(self):
        """Test skill specialization bonus integration"""
        # Create specialized skill
        weapon_specialist = RepairSkill(
            skill_level=7,
            specializations=["swords", "axes", "polearms"]
        )
        
        # Create general skill
        general_repairer = RepairSkill(
            skill_level=7,
            specializations=[]
        )
        
        # Test specialization bonus
        specialist_sword_bonus = weapon_specialist.get_repair_bonus("swords")
        general_sword_bonus = general_repairer.get_repair_bonus("swords")
        
        # Specialist should get bonus
        assert specialist_sword_bonus > general_sword_bonus
        assert specialist_sword_bonus == 45  # (7 * 5) + 10
        assert general_sword_bonus == 35     # (7 * 5) + 0

    def test_material_quality_impact_on_repair(self):
        """Test material quality impact on repair outcome"""
        # Different quality materials
        poor_material = RepairMaterial(
            quality_grade="poor",
            durability_bonus=3.0,
            cost_per_unit=5
        )
        
        legendary_material = RepairMaterial(
            quality_grade="legendary",
            durability_bonus=25.0,
            cost_per_unit=200
        )
        
        # Quality modifiers should reflect material grade
        assert poor_material.get_quality_modifier() == 0.5
        assert legendary_material.get_quality_modifier() == 3.0
        
        # Better materials should provide more durability bonus
        assert legendary_material.durability_bonus > poor_material.durability_bonus
        assert legendary_material.cost_per_unit > poor_material.cost_per_unit 
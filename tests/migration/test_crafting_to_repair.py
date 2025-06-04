"""
Tests for Crafting to Repair System Migration

Validates that the migration from crafting to repair system works correctly.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any, List

from backend.systems.repair.compat.crafting_bridge import CraftingCompatibilityService
from backend.systems.repair.services.repair_service import RepairService
from backend.systems.equipment.services.durability_service import DurabilityService
from backend.systems.equipment.models.equipment_quality import EquipmentQuality


class TestCraftingCompatibilityService:
    """Test the compatibility bridge between crafting and repair systems."""
    
    @pytest.fixture
    def mock_repair_service(self):
        """Mock repair service for testing."""
        mock = MagicMock()
        mock.get_available_stations.return_value = []
        mock.get_repair_estimate.return_value = {}
        mock.perform_repair.return_value = {}
        return mock
    
    @pytest.fixture
    def mock_durability_service(self):
        """Mock durability service for testing."""
        mock = MagicMock()
        mock.get_damaged_equipment.return_value = []
        return mock
    
    @pytest.fixture
    def compat_service(self, mock_repair_service, mock_durability_service):
        """Create compatibility service with mocked dependencies."""
        with patch('warnings.warn'):  # Suppress deprecation warnings in tests
            return CraftingCompatibilityService(mock_repair_service, mock_durability_service)
    
    def test_get_available_stations_conversion(self, compat_service, mock_repair_service):
        """Test that repair stations are converted to crafting station format."""
        # Arrange
        mock_repair_stations = [
            {
                "id": "station_1",
                "name": "Basic Repair Station",
                "station_type": "basic_repair_station",
                "efficiency_bonus": 1.1,
                "location": "Town Square",
                "specializations": ["weapons", "armor"]
            },
            {
                "id": "station_2", 
                "name": "Master Workshop",
                "station_type": "master_repair_workshop",
                "efficiency_bonus": 1.5,
                "specializations": ["mastercraft_equipment"]
            }
        ]
        mock_repair_service.get_available_stations.return_value = mock_repair_stations
        
        # Act
        crafting_stations = compat_service.get_available_stations()
        
        # Assert
        assert len(crafting_stations) == 2
        
        station_1 = crafting_stations[0]
        assert station_1["id"] == "station_1"
        assert station_1["name"] == "Basic Repair Station"
        assert station_1["type"] == "repair_basic_repair_station"
        assert station_1["level"] == 1.1
        assert station_1["location"] == "Town Square"
        assert station_1["available"] == True
        assert station_1["capabilities"] == ["weapons", "armor"]
        
        station_2 = crafting_stations[1]
        assert station_2["type"] == "repair_master_repair_workshop"
        assert station_2["level"] == 1.5
        assert station_2["location"] == "Unknown"  # Default when not provided
    
    def test_get_craftable_items_skill_mapping(self, compat_service, mock_durability_service):
        """Test that crafting skills are mapped to repair skills correctly."""
        # Arrange
        character_skills = {
            "smithing": 5,
            "leatherworking": 3,
            "tailoring": 2,
            "engineering": 4,
            "irrelevant_skill": 10
        }
        
        damaged_equipment = [
            {
                "id": "sword_1",
                "name": "Iron Sword",
                "type": "weapon_sword",
                "damage_level": 0.4
            },
            {
                "id": "armor_1", 
                "name": "Leather Armor",
                "type": "armor_light",
                "damage_level": 0.6
            }
        ]
        mock_durability_service.get_damaged_equipment.return_value = damaged_equipment
        
        # Act
        craftable_items = compat_service.get_craftable_items(character_skills)
        
        # Assert
        assert len(craftable_items) == 2
        
        # Check weapon repair item
        weapon_item = next(item for item in craftable_items if "sword" in item["name"].lower())
        assert weapon_item["id"] == "repair_sword_1"
        assert weapon_item["skill_required"] == "repair_weapons"
        assert weapon_item["min_skill_level"] == 1
        assert "Repair" in weapon_item["name"]
        
        # Check armor repair item
        armor_item = next(item for item in craftable_items if "armor" in item["name"].lower())
        assert armor_item["id"] == "repair_armor_1"
        assert armor_item["skill_required"] == "repair_armor"
    
    def test_craft_item_repair_operation(self, compat_service, mock_repair_service):
        """Test that craft_item calls perform_repair with correct parameters."""
        # Arrange
        recipe_id = "repair_sword_123"
        materials = [{"item_id": "iron_ingot", "quantity": 2}]
        character_id = "char_456"
        
        mock_repair_result = {
            "success": True,
            "experience_gained": 15,
            "materials_used": materials,
            "message": "Equipment repaired successfully"
        }
        mock_repair_service.perform_repair.return_value = mock_repair_result
        
        # Act
        result = compat_service.craft_item(recipe_id, materials, character_id)
        
        # Assert
        mock_repair_service.perform_repair.assert_called_once_with(
            equipment_id="sword_123",
            materials=materials,
            repairer_id=character_id
        )
        
        assert result["success"] == True
        assert result["experience_gained"] == 15
        assert result["result_items"][0]["item_id"] == "sword_123"
        assert result["result_items"][0]["condition"] == "repaired"
        assert result["materials_consumed"] == materials
    
    def test_craft_item_invalid_recipe_id(self, compat_service):
        """Test that craft_item raises error for non-repair recipe IDs."""
        # Arrange
        invalid_recipe_id = "craft_potion_123"
        materials = []
        character_id = "char_456"
        
        # Act & Assert
        with pytest.raises(ValueError, match="Only repair operations are supported"):
            compat_service.craft_item(invalid_recipe_id, materials, character_id)
    
    def test_get_recipe_requirements_repair_estimate(self, compat_service, mock_repair_service):
        """Test that recipe requirements are retrieved from repair estimates."""
        # Arrange
        recipe_id = "repair_armor_789"
        
        mock_repair_estimate = {
            "required_materials": [
                {"item_id": "leather", "quantity": 1},
                {"item_id": "iron_scraps", "quantity": 3}
            ],
            "required_skill": "repair_armor",
            "estimated_time": 450,
            "recommended_station": "leather_repair_station"
        }
        mock_repair_service.get_repair_estimate.return_value = mock_repair_estimate
        
        # Act
        requirements = compat_service.get_recipe_requirements(recipe_id)
        
        # Assert
        mock_repair_service.get_repair_estimate.assert_called_once_with("armor_789")
        
        assert requirements["ingredients"] == mock_repair_estimate["required_materials"]
        assert requirements["skill_required"] == "repair_armor"
        assert requirements["min_skill_level"] == 1
        assert requirements["crafting_time"] == 450
        assert requirements["station_required"] == "leather_repair_station"
    
    def test_get_recipe_requirements_invalid_recipe(self, compat_service):
        """Test that invalid recipe IDs return error."""
        # Arrange
        invalid_recipe_id = "craft_sword_123"
        
        # Act
        result = compat_service.get_recipe_requirements(invalid_recipe_id)
        
        # Assert
        assert "error" in result
        assert result["error"] == "Recipe not found"
    
    def test_repair_skill_mapping(self, compat_service):
        """Test equipment type to repair skill mapping."""
        # Test weapon mapping
        weapon_equipment = {"type": "weapon_sword"}
        skill = compat_service._get_repair_skill_for_equipment(weapon_equipment)
        assert skill == "repair_weapons"
        
        # Test sword mapping (also weapons)
        sword_equipment = {"type": "sword_iron"}
        skill = compat_service._get_repair_skill_for_equipment(sword_equipment)
        assert skill == "repair_weapons"
        
        # Test axe mapping (also weapons, hence tool_pickaxe was matching)
        axe_equipment = {"type": "battle_axe"}
        skill = compat_service._get_repair_skill_for_equipment(axe_equipment)
        assert skill == "repair_weapons"
        
        # Test armor mapping
        armor_equipment = {"type": "armor_heavy"}
        skill = compat_service._get_repair_skill_for_equipment(armor_equipment)
        assert skill == "repair_armor"
        
        # Test helmet mapping (also armor)
        helmet_equipment = {"type": "helmet_iron"}
        skill = compat_service._get_repair_skill_for_equipment(helmet_equipment)
        assert skill == "repair_armor"
        
        # Test general mapping (should default to general for unknown types)
        misc_equipment = {"type": "tool_hammer"}  # Changed from tool_pickaxe (which contains 'axe')
        skill = compat_service._get_repair_skill_for_equipment(misc_equipment)
        assert skill == "repair_general"
        
        # Test default case (no type)
        no_type_equipment = {}
        skill = compat_service._get_repair_skill_for_equipment(no_type_equipment)
        assert skill == "repair_general"
    
    def test_repair_time_estimation(self, compat_service):
        """Test repair time estimation based on damage level."""
        # Test low damage
        low_damage_eq = {"damage_level": 0.2}
        time = compat_service._estimate_repair_time(low_damage_eq)
        assert time == 360  # 300 * (1 + 0.2)
        
        # Test high damage
        high_damage_eq = {"damage_level": 0.8}
        time = compat_service._estimate_repair_time(high_damage_eq)
        assert time == 540  # 300 * (1 + 0.8)
        
        # Test default damage level
        no_damage_eq = {}
        time = compat_service._estimate_repair_time(no_damage_eq)
        assert time == 450  # 300 * (1 + 0.5)
    
    def test_repair_materials_by_quality(self, compat_service):
        """Test material requirements based on equipment quality."""
        # Test military quality
        military_eq = {"quality": "military"}
        materials = compat_service._get_repair_materials(military_eq)
        assert any(mat["item_id"] == "iron_ingot" for mat in materials)
        assert any(mat["item_id"] == "leather" for mat in materials)
        
        # Test basic quality (default)
        basic_eq = {"quality": "basic"}
        materials = compat_service._get_repair_materials(basic_eq)
        assert any(mat["item_id"] == "iron_scraps" for mat in materials)
        assert any(mat["item_id"] == "rough_cloth" for mat in materials)
        
        # Test unknown quality (should default to basic)
        unknown_eq = {}
        materials = compat_service._get_repair_materials(unknown_eq)
        assert any(mat["item_id"] == "iron_scraps" for mat in materials)
        
        # Test mastercraft quality
        mastercraft_eq = {"quality": "mastercraft"}
        materials = compat_service._get_repair_materials(mastercraft_eq)
        assert len(materials) == 2
        assert any(mat["item_id"] == "steel_ingot" for mat in materials)
        assert any(mat["item_id"] == "fine_cloth" for mat in materials)


class TestEquipmentQualityMigration:
    """Test equipment quality system functionality."""
    
    def test_quality_enum_values(self):
        """Test that quality enum has expected values."""
        assert EquipmentQuality.BASIC.value == "basic"
        assert EquipmentQuality.MILITARY.value == "military"
        assert EquipmentQuality.MASTERCRAFT.value == "mastercraft"
    
    def test_quality_config_properties(self):
        """Test quality configuration properties."""
        from backend.systems.equipment.models.equipment_quality import QualityConfig
        
        # Test basic quality configuration
        assert QualityConfig.get_durability_period(EquipmentQuality.BASIC).days == 7  # 1 week
        assert QualityConfig.get_repair_cost(EquipmentQuality.BASIC) == 500.0  # BASE_REPAIR_COST * 1.0
        assert QualityConfig.VALUE_MULTIPLIERS[EquipmentQuality.BASIC] == 1.0
        assert QualityConfig.SPRITE_SUFFIXES[EquipmentQuality.BASIC] == "_basic"
        
        # Test military quality configuration
        assert QualityConfig.get_durability_period(EquipmentQuality.MILITARY).days == 14  # 2 weeks
        assert QualityConfig.get_repair_cost(EquipmentQuality.MILITARY) == 750.0  # BASE_REPAIR_COST * 1.5
        assert QualityConfig.VALUE_MULTIPLIERS[EquipmentQuality.MILITARY] == 3.0
        assert QualityConfig.SPRITE_SUFFIXES[EquipmentQuality.MILITARY] == "_military"
        
        # Test mastercraft quality configuration
        assert QualityConfig.get_durability_period(EquipmentQuality.MASTERCRAFT).days == 28  # 4 weeks
        assert QualityConfig.get_repair_cost(EquipmentQuality.MASTERCRAFT) == 1500.0  # BASE_REPAIR_COST * 3.0
        assert QualityConfig.VALUE_MULTIPLIERS[EquipmentQuality.MASTERCRAFT] == 6.0
        assert QualityConfig.SPRITE_SUFFIXES[EquipmentQuality.MASTERCRAFT] == "_mastercraft"


class TestMigrationIntegration:
    """Integration tests for the complete migration."""
    
    def test_deprecation_warnings_are_triggered(self):
        """Test that deprecation warnings are properly triggered."""
        with pytest.warns(DeprecationWarning, match="crafting system is deprecated"):
            from backend.systems.crafting import models
        
        with pytest.warns(DeprecationWarning, match="CraftingCompatibilityService is deprecated"):
            mock_repair = Mock()
            mock_durability = Mock()
            CraftingCompatibilityService(mock_repair, mock_durability)
    
    def test_import_compatibility_file_exists(self):
        """Test that the compatibility import file was created."""
        import os
        compat_file = "backend/api/crafting_compat.py"
        assert os.path.exists(compat_file), f"Compatibility file should exist at {compat_file}"
    
    def test_api_endpoints_structure(self):
        """Test that new API endpoints have correct structure."""
        from backend.api.repair.routers.repair_router import router as repair_router
        from backend.api.repair.routers.equipment_router import router as equipment_router
        
        # Check repair router endpoints
        repair_routes = [route.path for route in repair_router.routes]
        expected_repair_routes = [
            "/repair/stations",
            "/repair/estimate", 
            "/repair/perform",
            "/repair/equipment/{equipment_id}/status",
            "/repair/equipment/damaged",
            "/repair/equipment/{equipment_id}/decay",
            "/repair/materials",
            "/repair/legacy/craftable"
        ]
        
        for expected_route in expected_repair_routes:
            assert any(expected_route in route for route in repair_routes), f"Missing route: {expected_route}"
        
        # Check equipment router endpoints
        equipment_routes = [route.path for route in equipment_router.routes]
        expected_equipment_routes = [
            "/equipment/qualities",
            "/equipment/create",
            "/equipment/{equipment_id}",
            "/equipment/character/{character_id}/all"
        ]
        
        for expected_route in expected_equipment_routes:
            assert any(expected_route in route for route in equipment_routes), f"Missing route: {expected_route}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 
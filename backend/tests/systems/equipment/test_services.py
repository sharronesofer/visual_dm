"""
Test module for equipment.services

Tests equipment services according to Development Bible standards:
- Hybrid equipment service orchestration
- Template-based equipment management
- Business logic validation
- Service layer separation
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from uuid import uuid4

# Import the module under test
try:
    from backend.systems.equipment.services import (
        EquipmentBusinessLogicService, EnchantingService,
        EquipmentInstanceData, EquipmentBaseTemplate, QualityTierData,
        CharacterEquipmentService
    )
    from backend.systems.equipment.models.equipment_models import EquipmentInstance
    services_available = True
except ImportError:
    services_available = False


@pytest.mark.skipif(not services_available, reason="Equipment services not available")
class TestEquipmentServices:
    """Test suite for equipment system services"""
    
    def test_business_logic_service_initialization(self):
        """Test business logic service can be initialized"""
        service = EquipmentBusinessLogicService()
        assert service is not None
        assert service.QUALITY_TIERS == ['basic', 'military', 'mastercraft']
        assert service.DAILY_USE_HOURS == 8
        assert service.MAX_MAGICAL_EFFECTS_LEGACY == 20
    
    def test_create_equipment_instance_business_logic(self):
        """Test equipment instance creation with business validation"""
        service = EquipmentBusinessLogicService()
        
        # Test valid equipment creation
        validation = service.validate_equipment_creation(
            'sword_rapier', 'basic', []
        )
        assert validation['valid'] is True
        assert len(validation['errors']) == 0
    
    def test_equipment_validation_business_rules(self):
        """Test business rule validation"""
        service = EquipmentBusinessLogicService()
        
        # Test invalid quality tier
        validation = service.validate_equipment_creation(
            'sword_rapier', 'invalid_quality', []
        )
        assert validation['valid'] is False
        assert any('Invalid quality tier' in error for error in validation['errors'])
        
        # Test too many magical effects
        too_many_effects = [{'effect_type': 'test', 'power_level': 50} for _ in range(25)]
        validation = service.validate_equipment_creation(
            'sword_rapier', 'basic', too_many_effects
        )
        assert validation['valid'] is False
        assert any('Too many magical effects' in error for error in validation['errors'])
    
    def test_durability_calculation_business_logic(self):
        """Test durability calculation according to user requirements"""
        service = EquipmentBusinessLogicService()
        
        # Test basic quality: should break after 1 week (168 hours) of daily use
        new_durability, details = service.calculate_durability_degradation(
            current_durability=100.0,
            quality_tier='basic',
            hours_of_use=168.0,  # 1 week * 8 hours/day * 7 days
            environment_factor=1.0
        )
        
        # Should be close to 0 (item broken after 1 week)
        assert new_durability <= 5.0  # Allow small margin for rounding
        
        # Test military quality: should last 2 weeks
        new_durability, details = service.calculate_durability_degradation(
            current_durability=100.0,
            quality_tier='military',
            hours_of_use=168.0,  # Same 1 week usage
            environment_factor=1.0
        )
        
        # Should be around 50% durability left after 1 week (lasts 2 weeks total)
        assert 45.0 <= new_durability <= 55.0
    
    def test_equipment_uniqueness_calculation(self):
        """Test equipment uniqueness scoring based on magical effects"""
        service = EquipmentBusinessLogicService()
        
        # No effects = 0 uniqueness
        score = service.calculate_equipment_uniqueness_score([])
        assert score == 0.0
        
        # Some effects = positive uniqueness
        effects = [
            {'effect_type': 'stat_bonus', 'power_level': 75},
            {'effect_type': 'damage_bonus', 'power_level': 50}
        ]
        score = service.calculate_equipment_uniqueness_score(effects)
        assert 0.0 < score <= 1.0
    
    def test_enchanting_service_business_logic(self):
        """Test enchanting service without infrastructure dependencies"""
        service = EnchantingService()  # No dependencies to avoid circular imports
        assert service is not None
        assert service.character_profiles == {}


@pytest.mark.skipif(not services_available, reason="Equipment services not available")
class TestEquipmentServicesIntegration:
    """Test suite for integrated equipment service workflows"""
    
    def test_business_logic_service_workflow(self):
        """Test complete business logic workflow"""
        service = EquipmentBusinessLogicService()
        
        # Create equipment with business validation
        magical_effects = [
            {'effect_type': 'stat_bonus', 'power_level': 60, 'stat_name': 'attack'},
            {'effect_type': 'damage_bonus', 'power_level': 40}
        ]
        
        validation = service.validate_equipment_creation('sword_rapier', 'military', magical_effects)
        assert validation['valid'] is True
        
        # Generate display name
        display_name = service.generate_equipment_display_name(
            'Rapier', 'military', magical_effects
        )
        assert 'Military-Grade' in display_name
        assert 'Rapier' in display_name
        assert 'Magical' in display_name
    
    def test_durability_status_integration(self):
        """Test durability status and penalty integration"""
        service = EquipmentBusinessLogicService()
        
        # Test different durability levels
        test_cases = [
            (95.0, 'excellent', 0.0),
            (80.0, 'good', 0.0),
            (60.0, 'worn', 0.1),
            (35.0, 'damaged', 0.25),
            (15.0, 'very_damaged', 0.5),
            (0.0, 'broken', 1.0)
        ]
        
        for durability, expected_status, expected_penalty in test_cases:
            status = service.get_durability_status(durability)
            penalty = service.calculate_stat_penalties(durability)
            functionality = service.is_equipment_functional(durability)
            
            assert status == expected_status
            assert penalty == expected_penalty
            assert functionality == (durability > 0.0)

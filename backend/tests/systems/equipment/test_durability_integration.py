"""
Test module for equipment durability integration

Tests weapon attack integration and environmental factors according to Development Bible.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import json
import tempfile
import os

try:
    from backend.infrastructure.services.equipment.durability_service import DurabilityService
    durability_service_available = True
except ImportError:
    durability_service_available = False


@pytest.mark.skipif(not durability_service_available, reason="Durability service not available")
class TestDurabilityIntegration:
    """Test durability integration features."""
    
    @pytest.fixture
    def mock_db_session(self):
        """Mock database session."""
        return Mock()
    
    @pytest.fixture
    def temp_config_file(self):
        """Create temporary config file for testing."""
        config_data = {
            "environmental_factors": {
                "normal": 1.0,
                "humid": 1.2,
                "dry": 0.8,
                "extreme_cold": 1.5,
                "extreme_heat": 1.3,
                "corrupted": 2.0
            },
            "integration_triggers": {
                "weapon_attack_given": {
                    "enabled": True,
                    "durability_loss_base": 1.0,
                    "critical_multiplier": 1.5
                },
                "weapon_attack_received": {
                    "enabled": True,
                    "durability_loss_base": 0.5,
                    "critical_multiplier": 1.2
                }
            }
        }
        
        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        json.dump(config_data, temp_file)
        temp_file.close()
        
        yield temp_file.name
        
        # Cleanup
        os.unlink(temp_file.name)
    
    def test_environmental_factors_load_from_json(self, mock_db_session, temp_config_file):
        """Test that environmental factors are loaded from JSON configuration."""
        # Patch the config path to use our temporary file
        with patch('backend.infrastructure.services.equipment.durability_service.Path') as mock_path:
            mock_path.return_value.parent.parent.parent.parent / "data" / "systems" / "repair" / "repair_config.json" = temp_config_file
            
            service = DurabilityService(mock_db_session)
            
            # Verify environmental factors are loaded correctly
            assert service.ENVIRONMENTAL_FACTORS["normal"] == 1.0
            assert service.ENVIRONMENTAL_FACTORS["humid"] == 1.2
            assert service.ENVIRONMENTAL_FACTORS["dry"] == 0.8
            assert service.ENVIRONMENTAL_FACTORS["extreme_cold"] == 1.5
            assert service.ENVIRONMENTAL_FACTORS["corrupted"] == 2.0
    
    def test_weapon_attack_integration_triggers(self, mock_db_session, temp_config_file):
        """Test weapon attack integration triggers work correctly."""
        with patch('backend.infrastructure.services.equipment.durability_service.Path') as mock_path:
            mock_path.return_value.parent.parent.parent.parent / "data" / "systems" / "repair" / "repair_config.json" = temp_config_file
            
            service = DurabilityService(mock_db_session)
            
            # Mock the apply_durability_damage method
            with patch.object(service, 'apply_durability_damage') as mock_apply_damage:
                mock_apply_damage.return_value = {
                    "success": True,
                    "durability_before": 80.0,
                    "durability_after": 79.0,
                    "damage_applied": 1.0
                }
                
                # Test weapon attack given (attacker)
                result = service.apply_weapon_attack_damage(
                    equipment_id="sword_123",
                    attack_type="melee",
                    is_critical=False,
                    is_attacker=True
                )
                
                assert result["success"] is True
                assert result["attack_type"] == "melee"
                assert result["is_critical"] is False
                assert result["is_attacker"] is True
                
                # Verify damage calculation
                mock_apply_damage.assert_called_with("sword_123", 1.0, "weapon_attack")
    
    def test_weapon_attack_critical_multiplier(self, mock_db_session, temp_config_file):
        """Test critical attack multiplier is applied correctly."""
        with patch('backend.infrastructure.services.equipment.durability_service.Path') as mock_path:
            mock_path.return_value.parent.parent.parent.parent / "data" / "systems" / "repair" / "repair_config.json" = temp_config_file
            
            service = DurabilityService(mock_db_session)
            
            with patch.object(service, 'apply_durability_damage') as mock_apply_damage:
                mock_apply_damage.return_value = {"success": True}
                
                # Test critical attack (attacker)
                service.apply_weapon_attack_damage(
                    equipment_id="sword_123",
                    attack_type="melee",
                    is_critical=True,
                    is_attacker=True
                )
                
                # Should apply 1.5x damage for critical attack
                mock_apply_damage.assert_called_with("sword_123", 1.5, "weapon_attack")
    
    def test_weapon_attack_received_damage(self, mock_db_session, temp_config_file):
        """Test receiving attacks causes appropriate durability loss."""
        with patch('backend.infrastructure.services.equipment.durability_service.Path') as mock_path:
            mock_path.return_value.parent.parent.parent.parent / "data" / "systems" / "repair" / "repair_config.json" = temp_config_file
            
            service = DurabilityService(mock_db_session)
            
            with patch.object(service, 'apply_durability_damage') as mock_apply_damage:
                mock_apply_damage.return_value = {"success": True}
                
                # Test receiving attack (defender)
                service.apply_weapon_attack_damage(
                    equipment_id="armor_456",
                    attack_type="melee",
                    is_critical=True,
                    is_attacker=False
                )
                
                # Should apply 0.5 * 1.2 = 0.6 damage for critical received attack
                mock_apply_damage.assert_called_with("armor_456", 0.6, "weapon_attack")
    
    def test_integration_trigger_disabled(self, mock_db_session):
        """Test that disabled integration triggers don't apply damage."""
        config_data = {
            "integration_triggers": {
                "weapon_attack_given": {
                    "enabled": False,
                    "durability_loss_base": 1.0
                }
            }
        }
        
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        json.dump(config_data, temp_file)
        temp_file.close()
        
        try:
            with patch('backend.infrastructure.services.equipment.durability_service.Path') as mock_path:
                mock_path.return_value.parent.parent.parent.parent / "data" / "systems" / "repair" / "repair_config.json" = temp_file.name
                
                service = DurabilityService(mock_db_session)
                
                result = service.apply_weapon_attack_damage(
                    equipment_id="sword_123",
                    attack_type="melee",
                    is_critical=False,
                    is_attacker=True
                )
                
                assert result["success"] is False
                assert result["reason"] == "Integration trigger disabled"
        finally:
            os.unlink(temp_file.name)
    
    def test_fallback_to_hardcoded_values(self, mock_db_session):
        """Test fallback to hardcoded values when config file is missing."""
        with patch('backend.infrastructure.services.equipment.durability_service.Path') as mock_path:
            # Point to non-existent file
            mock_path.return_value.parent.parent.parent.parent / "data" / "systems" / "repair" / "repair_config.json" = "/nonexistent/path.json"
            
            service = DurabilityService(mock_db_session)
            
            # Verify fallback values are used
            assert service.ENVIRONMENTAL_FACTORS["normal"] == 1.0
            assert service.ENVIRONMENTAL_FACTORS["humid"] == 1.2
            assert service.integration_triggers == {}


@pytest.mark.skipif(not durability_service_available, reason="Durability service not available")
class TestEnvironmentalFactorsIntegration:
    """Test environmental factors integration."""
    
    def test_environmental_factor_application(self):
        """Test that environmental factors are properly applied."""
        # This would test the actual application of environmental factors
        # but depends on the complete durability calculation implementation
        pass 
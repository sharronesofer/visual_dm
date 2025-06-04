"""
Test module for combat.status_effects

This module tests the status effects functionality.
"""

import pytest
from unittest.mock import Mock, patch

# Import the module under test
try:
    from backend.systems.combat import status_effects
    status_effects_available = True
except ImportError:
    status_effects_available = False


@pytest.mark.skipif(not status_effects_available, reason="combat.status_effects module not found")
class TestStatusEffects:
    """Test class for status_effects module"""
    
    def test_module_imports(self):
        """Test that the module can be imported successfully"""
        assert status_effects is not None
        
    def test_module_structure(self):
        """Test that module has expected structure"""
        # Expected functions based on actual implementation
        expected_functions = [
            'apply_status_effect', 
            'tick_status_effects', 
            'get_active_effects', 
            'has_effect',
            'remove_status_effect_by_name',
            'calculate_effect_impact'
        ]
        
        for func_name in expected_functions:
            assert hasattr(status_effects, func_name), f"Expected function {func_name} not found in status_effects module"
        
    @pytest.mark.asyncio
    async def test_basic_functionality(self):
        """Test basic functionality"""
        # Test that we can create a mock combatant and apply effects
        mock_combatant = {"status_effects": []}
        
        # Test applying a status effect
        effect = status_effects.apply_status_effect(
            mock_combatant, 
            "test_effect", 
            duration=5, 
            source="test"
        )
        
        assert effect["name"] == "test_effect"
        assert effect["duration"] == 5
        assert len(mock_combatant["status_effects"]) == 1
        
    def test_effect_checking(self):
        """Test effect checking functionality"""
        mock_combatant = {"status_effects": [{"name": "poisoned", "duration": 3}]}
        
        # Test has_effect
        assert status_effects.has_effect(mock_combatant, "poisoned") is True
        assert status_effects.has_effect(mock_combatant, "stunned") is False
        
        # Test get_active_effects
        effects = status_effects.get_active_effects(mock_combatant)
        assert len(effects) == 1
        assert effects[0]["name"] == "poisoned"

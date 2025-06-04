"""
Test for the rumor rules module that was moved from the rules system.

This test verifies that rumor-specific logic is properly separated
and works with dependency injection.
"""

import pytest
from typing import Dict, Any, Optional


class MockRumorConfigProvider:
    """Mock configuration provider for testing"""
    
    def __init__(self, config_data: Optional[Dict[str, Any]] = None):
        self.config_data = config_data or {}
    
    def load_json_config(self, filename: str, fallback_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Mock config loading"""
        if filename == "rumor_config.json" and self.config_data:
            return self.config_data
        return fallback_data or {}


def test_rumor_rules_import():
    """Test that rumor rules can be imported successfully."""
    from backend.systems.rumor.utils.rumor_rules import (
        get_rumor_constants,
        get_rumor_decay_rate,
        get_rumor_mutation_chance,
        get_rumor_spread_radius,
        get_rumor_believability_threshold,
        set_rumor_config_provider
    )
    
    # Test with default (no config provider)
    constants = get_rumor_constants()
    assert isinstance(constants, dict)
    assert "base_decay_rate" in constants
    assert constants["base_decay_rate"] == 0.05


def test_rumor_decay_calculation():
    """Test rumor decay rate calculations."""
    from backend.systems.rumor.utils.rumor_rules import get_rumor_decay_rate, set_rumor_config_provider
    
    # Reset config provider for clean test
    set_rumor_config_provider(None)
    
    # Test with default values
    decay_rate = get_rumor_decay_rate("moderate", 1)
    assert decay_rate == 0.05  # base_rate * 1.0 * 1 day
    
    # Test severity affects decay
    trivial_decay = get_rumor_decay_rate("trivial", 1)
    critical_decay = get_rumor_decay_rate("critical", 1)
    assert trivial_decay > critical_decay  # Trivial rumors decay faster


def test_rumor_mutation_calculation():
    """Test rumor mutation chance calculations."""
    from backend.systems.rumor.utils.rumor_rules import get_rumor_mutation_chance, set_rumor_config_provider
    
    # Reset config provider for clean test
    set_rumor_config_provider(None)
    
    # Test basic mutation chance
    mutation_chance = get_rumor_mutation_chance("moderate", 0)
    assert mutation_chance == 0.2  # base chance
    
    # Test that spread count affects mutation
    high_spread_mutation = get_rumor_mutation_chance("moderate", 100)
    assert high_spread_mutation > mutation_chance


def test_rumor_spread_radius():
    """Test rumor spread radius calculations."""
    from backend.systems.rumor.utils.rumor_rules import get_rumor_spread_radius, set_rumor_config_provider
    
    # Reset config provider for clean test
    set_rumor_config_provider(None)
    
    # Test basic spread radius
    radius = get_rumor_spread_radius("moderate", 1)
    expected = int(10 * 1.0 * (1 + 1 * 0.8))  # base * severity * time factor
    assert radius == expected
    
    # Test that critical rumors spread further
    critical_radius = get_rumor_spread_radius("critical", 1)
    trivial_radius = get_rumor_spread_radius("trivial", 1)
    assert critical_radius > trivial_radius


def test_rumor_believability_threshold():
    """Test rumor believability threshold calculations."""
    from backend.systems.rumor.utils.rumor_rules import get_rumor_believability_threshold, set_rumor_config_provider
    
    # Reset config provider for clean test
    set_rumor_config_provider(None)
    
    # Test basic believability
    threshold = get_rumor_believability_threshold("moderate", 0.0)
    assert threshold == 0.5  # base threshold for moderate
    
    # Test relationship affects believability
    friend_threshold = get_rumor_believability_threshold("moderate", 1.0)  # Strong positive relationship
    enemy_threshold = get_rumor_believability_threshold("moderate", -1.0)  # Strong negative relationship
    assert friend_threshold < threshold < enemy_threshold


def test_rumor_config_injection():
    """Test that configuration injection works properly."""
    from backend.systems.rumor.utils.rumor_rules import (
        get_rumor_constants, 
        set_rumor_config_provider,
        reload_rumor_config
    )
    
    # Create mock config with different values
    mock_config = {
        "decay": {
            "base_daily_rate": 0.1,
            "severity_factors": {
                "moderate": 2.0
            }
        }
    }
    
    # Set up mock provider
    provider = MockRumorConfigProvider(mock_config)
    set_rumor_config_provider(provider)
    
    # Clear cache and get new constants
    reload_rumor_config()
    constants = get_rumor_constants()
    
    # Verify the injected config was used
    assert constants["base_decay_rate"] == 0.1
    assert constants["decay_severity_factors"]["moderate"] == 2.0
    
    # Clean up
    set_rumor_config_provider(None)
    reload_rumor_config()


def test_separation_from_rules_system():
    """Test that rumor functions are no longer in the rules system."""
    import backend.systems.rules as rules_system
    
    # These functions should NOT be in the rules system anymore
    assert not hasattr(rules_system, 'get_rumor_constants')
    assert not hasattr(rules_system, 'get_rumor_decay_rate')
    assert not hasattr(rules_system, 'get_rumor_mutation_chance')
    
    # But they should be accessible from the rumor system
    from backend.systems.rumor.utils import rumor_rules
    assert hasattr(rumor_rules, 'get_rumor_constants')
    assert hasattr(rumor_rules, 'get_rumor_decay_rate')
    assert hasattr(rumor_rules, 'get_rumor_mutation_chance')


if __name__ == '__main__':
    pytest.main([__file__]) 
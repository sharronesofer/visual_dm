"""
Integration tests for Rules and Rumor systems
--------------------------------------------
Tests the full integration between systems with proper dependency injection.
"""

import pytest


def test_rules_system_initialization():
    """Test that rules system can be properly initialized."""
    from backend.infrastructure.rules_data_loader import initialize_rules_system
    from backend.systems.rules import get_balance_constants, calculate_hp_for_level
    
    # Initialize the system
    initialize_rules_system()
    
    # Test that configuration loading works
    constants = get_balance_constants()
    assert isinstance(constants, dict)
    assert "starting_gold" in constants
    
    # Test that business logic functions work
    hp = calculate_hp_for_level(5, 2)
    assert hp > 0  # Should calculate a reasonable HP value


def test_rumor_system_initialization():
    """Test that rumor system can be properly initialized."""
    from backend.infrastructure.rules_data_loader import initialize_rumor_system
    from backend.systems.rumor.utils.rumor_rules import get_rumor_constants, get_rumor_decay_rate
    
    # Initialize the system
    initialize_rumor_system()
    
    # Test that configuration loading works
    constants = get_rumor_constants()
    assert isinstance(constants, dict)
    assert "base_decay_rate" in constants
    
    # Test that business logic functions work
    decay_rate = get_rumor_decay_rate("moderate", 1)
    assert decay_rate > 0  # Should calculate a reasonable decay rate


def test_full_system_initialization():
    """Test that all systems can be initialized together."""
    from backend.infrastructure.rules_data_loader import initialize_all_systems
    from backend.systems.rules import get_balance_constants
    from backend.systems.rumor.utils.rumor_rules import get_rumor_constants
    
    # Initialize all systems
    initialize_all_systems()
    
    # Test both systems work
    rules_constants = get_balance_constants()
    rumor_constants = get_rumor_constants()
    
    assert isinstance(rules_constants, dict)
    assert isinstance(rumor_constants, dict)
    assert "starting_gold" in rules_constants
    assert "base_decay_rate" in rumor_constants


def test_systems_are_independent():
    """Test that rules and rumor systems don't interfere with each other."""
    from backend.infrastructure.rules_data_loader import initialize_all_systems
    from backend.systems.rules import calculate_hp_for_level, get_balance_constants
    from backend.systems.rumor.utils.rumor_rules import get_rumor_decay_rate, get_rumor_constants
    
    # Initialize all systems
    initialize_all_systems()
    
    # Test rules system
    hp = calculate_hp_for_level(10, 3)
    rules_constants = get_balance_constants()
    
    # Test rumor system
    decay = get_rumor_decay_rate("critical", 2)
    rumor_constants = get_rumor_constants()
    
    # Verify both work independently
    assert hp > 0
    assert decay > 0
    assert rules_constants != rumor_constants  # Should be different configs
    
    # Verify no cross-contamination
    assert "base_decay_rate" not in rules_constants
    assert "starting_gold" not in rumor_constants


def test_backward_compatibility_after_initialization():
    """Test that backward compatibility is maintained after initialization."""
    from backend.infrastructure.rules_data_loader import initialize_all_systems
    from backend.systems.rules import balance_constants
    
    # Initialize systems
    initialize_all_systems()
    
    # Test backward compatibility features still work
    assert "starting_gold" in balance_constants
    assert balance_constants["starting_gold"] == 100
    assert balance_constants.get("max_level") == 20
    
    # Test dict-like access
    for key in balance_constants.keys():
        assert key in balance_constants
        value = balance_constants[key]
        assert value is not None


if __name__ == '__main__':
    pytest.main([__file__]) 
"""
Rules System Initialization
---------------------------
Proper initialization of the rules system with dependency injection.
This should be called during application startup.
"""

from .rules_config_bridge import initialize_rules_system


def setup_rules_system():
    """
    Initialize the rules system with proper dependency injection.
    
    This function:
    1. Creates the infrastructure configuration bridge
    2. Injects it into the business logic rules system
    3. Ensures the system is ready for use
    
    Should be called during application startup, after database
    and other infrastructure is initialized.
    """
    try:
        initialize_rules_system()
        print("✓ Rules system initialized successfully with configuration provider")
    except Exception as e:
        print(f"⚠ Warning: Failed to initialize rules system: {e}")
        print("  Rules system will use fallback constants only")


if __name__ == "__main__":
    # Allow running this script directly for testing
    setup_rules_system()
    
    # Test basic functionality
    from backend.systems.rules import balance_constants, calculate_ability_modifier
    
    print(f"Starting gold: {balance_constants['starting_gold']}")
    print(f"Ability modifier for 16: {calculate_ability_modifier(16)}")
    print("Rules system test completed successfully") 
"""
Usage Examples for the Tension and War System

This module provides examples demonstrating how to use the tension and war systems.
"""

from datetime import datetime
from .services import TensionManager, WarManager


def tension_system_example():
    """Example of using the TensionManager."""
    print("=== Tension System Example ===")
    
    # Initialize the tension manager
    tension_manager = TensionManager()
    
    # Get tension for a region
    region_id = "northern_valleys"
    tension_data = tension_manager.get_tension(region_id)
    print(f"Current tension in {region_id}: {tension_data['tensions']}")
    
    # Modify tension for a faction in the region
    updated_tension = tension_manager.modify_tension(
        region_id=region_id,
        faction="mountain_kingdom",
        value=15,
        reason="border_dispute"
    )
    print(f"Updated tension in {region_id}: {updated_tension['tensions']}")
    
    # Decay tension over time
    decayed_tension = tension_manager.decay_tension(region_id)
    print(f"Decayed tension in {region_id}: {decayed_tension['tensions']}")
    
    # Reset tension to zero
    reset_tension = tension_manager.reset_tension(region_id)
    print(f"Reset tension in {region_id}: {reset_tension['tensions']}")
    
    # Get tension level category
    tension_value = 75  # Example tension value
    tension_level = tension_manager.get_tension_level(tension_value)
    print(f"Tension level for value {tension_value}: {tension_level.value}")
    
    # Update tension between two specific factions
    new_tension = tension_manager.update_tension(
        faction_a_id="mountain_kingdom",
        faction_b_id="forest_tribe",
        value=30,
        reason="trade_dispute"
    )
    print(f"New tension between factions: {new_tension}")
    
    print("===========================")


def war_system_example():
    """Example of using the WarManager."""
    print("=== War System Example ===")
    
    # Initialize the war manager
    war_manager = WarManager()
    
    # Initialize a war between two factions in different regions
    region_a = "northern_valleys"
    region_b = "eastern_hills"
    faction_a = "mountain_kingdom"
    faction_b = "forest_tribe"
    
    war_status = war_manager.initialize_war(
        region_a=region_a,
        region_b=region_b,
        faction_a=faction_a,
        faction_b=faction_b
    )
    print(f"War initialized: {faction_a} vs {faction_b}")
    print(f"Status: {war_status}")
    
    # Get the current war status for a region
    current_status = war_manager.get_war_status(region_a)
    print(f"Current war status for {region_a}: {current_status}")
    
    # Advance the war by one day
    advanced_war = war_manager.advance_war_day(region_a)
    print(f"War day {advanced_war['day']} events: {len(advanced_war['events'])}")
    
    # Generate raids
    raids = war_manager.generate_daily_raids(region_a)
    print(f"Generated {len(raids)} raids in {region_a}")
    
    # Record a POI conquest
    conquest = war_manager.record_poi_conquest(
        region=region_a,
        poi_id="mountain_pass",
        faction=faction_a
    )
    print(f"Conquest recorded: {conquest}")
    
    print("===========================")


def run_examples():
    """Run all examples."""
    tension_system_example()
    print("\n")
    war_system_example()


if __name__ == "__main__":
    run_examples() 
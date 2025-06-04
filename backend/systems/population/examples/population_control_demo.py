"""
Population Control Demonstration

This script demonstrates the new population control levers that address
over/under-population issues and racial distribution management.
"""

from backend.systems.population.managers.population_manager import PopulationManager
from backend.systems.population.utils.consolidated_utils import (
    calculate_controlled_growth_rate,
    calculate_racial_distribution,
    RaceType
)

def demonstrate_growth_controls():
    """Demonstrate population growth control levers."""
    print("=== POPULATION GROWTH CONTROLS ===\n")
    
    # Scenario 1: Normal growing settlement
    print("1. Normal growing settlement (500 people, capacity 1000):")
    growth_rate = calculate_controlled_growth_rate(
        current_population=500,
        base_growth_rate=0.02,  # 2% base growth
        carrying_capacity=1000,
        resource_availability=1.0,
        stability_factor=0.8
    )
    print(f"   Controlled growth rate: {growth_rate:.3f} ({growth_rate*100:.1f}% annual)")
    
    # Scenario 2: Overpopulated settlement
    print("\n2. Overpopulated settlement (1500 people, capacity 1000):")
    growth_rate = calculate_controlled_growth_rate(
        current_population=1500,
        base_growth_rate=0.02,
        carrying_capacity=1000,
        resource_availability=0.6,  # Resource scarcity
        stability_factor=0.5  # Social unrest
    )
    print(f"   Controlled growth rate: {growth_rate:.3f} ({growth_rate*100:.1f}% annual)")
    print("   Note: Negative growth due to overpopulation and resource scarcity")
    
    # Scenario 3: Nearly extinct settlement
    print("\n3. Nearly extinct settlement (15 people, capacity 1000):")
    growth_rate = calculate_controlled_growth_rate(
        current_population=15,
        base_growth_rate=0.02,
        carrying_capacity=1000,
        resource_availability=1.2,  # Abundant resources
        stability_factor=0.9  # High stability
    )
    print(f"   Controlled growth rate: {growth_rate:.3f} ({growth_rate*100:.1f}% annual)")
    print("   Note: Very low growth due to extinction pressure")

def demonstrate_racial_distribution():
    """Demonstrate racial distribution controls."""
    print("\n=== RACIAL DISTRIBUTION CONTROLS ===\n")
    
    # Scenario 1: Forest settlement
    print("1. Forest settlement (1000 people):")
    distribution = calculate_racial_distribution(
        total_population=1000,
        region_type="forest"
    )
    print("   Racial breakdown:")
    for race, count in sorted(distribution.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / 1000) * 100
        print(f"   - {race.title()}: {count} ({percentage:.1f}%)")
    
    # Scenario 2: Mountain dwarven stronghold
    print("\n2. Mountain settlement with dwarven culture:")
    cultural_factors = {"dwarf": 2.0, "giant": 1.5}  # Strong dwarven culture
    distribution = calculate_racial_distribution(
        total_population=800,
        region_type="mountain",
        cultural_factors=cultural_factors
    )
    print("   Racial breakdown:")
    for race, count in sorted(distribution.items(), key=lambda x: x[1], reverse=True):
        if count > 0:
            percentage = (count / 800) * 100
            print(f"   - {race.title()}: {count} ({percentage:.1f}%)")
    
    # Scenario 3: Urban trading hub
    print("\n3. Urban trading hub with historical human dominance:")
    historical_dist = {"human": 0.8, "halfling": 0.15, "elf": 0.05}
    distribution = calculate_racial_distribution(
        total_population=5000,
        region_type="urban",
        historical_distribution=historical_dist
    )
    print("   Racial breakdown:")
    for race, count in sorted(distribution.items(), key=lambda x: x[1], reverse=True):
        if count > 0:
            percentage = (count / 5000) * 100
            print(f"   - {race.title()}: {count} ({percentage:.1f}%)")

def demonstrate_manager_controls():
    """Demonstrate PopulationManager control methods."""
    print("\n=== POPULATION MANAGER CONTROLS ===\n")
    
    # Initialize manager
    manager = PopulationManager()
    
    # Demonstrate global growth modifier
    print("1. Global Growth Rate Control:")
    print(f"   Original base growth rate: {manager.config['growth_control']['base_growth_rate']}")
    
    manager.set_global_growth_modifier(0.5)  # Half speed
    print(f"   After 0.5x modifier: {manager.config['growth_control']['base_growth_rate']}")
    
    manager.set_global_growth_modifier(2.0)  # Back to normal
    print(f"   After 2.0x modifier: {manager.config['growth_control']['base_growth_rate']}")
    
    # Demonstrate racial weight adjustment
    print("\n2. Global Racial Weight Control:")
    print("   Original human percentage:", manager.config['racial_distribution']['default_weights']['human'])
    
    manager.set_racial_weights({"human": 0.4, "elf": 0.3})  # More balanced fantasy world
    print("   After adjustment - Human:", manager.config['racial_distribution']['default_weights']['human'])
    print("   After adjustment - Elf:", manager.config['racial_distribution']['default_weights']['elf'])
    
    # Demonstrate regional modifiers
    print("\n3. Regional Modifier Control:")
    manager.set_regional_modifiers("swamp", {"orc": 3.0, "goblin": 4.0, "human": 0.2})
    print("   Set swamp region to favor orcs and goblins, discourage humans")
    print("   Swamp modifiers:", manager.config['racial_distribution']['regional_modifiers']['swamp'])

def demonstrate_configuration_control():
    """Demonstrate JSON configuration control."""
    print("\n=== CONFIGURATION CONTROL ===\n")
    
    manager = PopulationManager()
    
    print("1. Runtime Configuration Updates:")
    
    # Update overpopulation penalty
    config_update = {
        "growth_control": {
            "overpopulation_penalty": 0.25  # Harsher penalty
        }
    }
    manager.update_config(config_update)
    print(f"   Updated overpopulation penalty to: {manager.config['growth_control']['overpopulation_penalty']}")
    
    # Update war impact settings
    config_update = {
        "war_impact": {
            "base_mortality_multiplier": 0.2,  # Less deadly wars
            "refugee_percentage": 0.6  # More refugees
        }
    }
    manager.update_config(config_update)
    print(f"   Updated war mortality to: {manager.config['war_impact']['base_mortality_multiplier']}")
    print(f"   Updated refugee percentage to: {manager.config['war_impact']['refugee_percentage']}")
    
    print("\n2. Configuration can be saved and loaded from JSON files for easy designer control")
    print("   Location: data/systems/population/population_config.json")

if __name__ == "__main__":
    print("POPULATION SYSTEM CONTROL DEMONSTRATION")
    print("=" * 50)
    
    demonstrate_growth_controls()
    demonstrate_racial_distribution()  
    demonstrate_manager_controls()
    demonstrate_configuration_control()
    
    print("\n" + "=" * 50)
    print("SUMMARY:")
    print("✅ Growth rate controls prevent overpopulation explosions")
    print("✅ Growth rate controls prevent extinction spirals") 
    print("✅ Racial distribution can be controlled by region, culture, and history")
    print("✅ Global modifiers allow easy population tuning")
    print("✅ All parameters are JSON-configurable for designers")
    print("✅ PopulationManager provides unified interface for other systems")
    print("✅ No more duplicate functions or missing dependencies!") 
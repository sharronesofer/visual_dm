#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.abspath("."))

from backend.systems.world_state.main import initialize_world_state_system
from backend.systems.world_state import StateCategory, WorldRegion
from backend.systems.world_state.features.derivative_state import DerivedStateRule

def test_derivative_state():
    print("Testing derivative state functionality...")
    
    # Initialize the system
    config = {
        "storage_dir": None,  # In-memory only
        "backup_dir": None,   # No backups
        "max_backup_versions": 0,
        "max_history_records": 50,
        "auto_save_interval": 0,  # Disable auto-save
    }
    
    world_state = initialize_world_state_system(config=config)
    print(f"World state system initialized: {world_state}")
    print(f"Manager instance: {world_state.manager}")
    print(f"Derivative calculator instance: {world_state.derivative_calculator}")
    print(f"Derivative calculator world_state ref: {world_state.derivative_calculator.world_state}")
    
    # Set some basic state
    print("\nSetting basic state...")
    world_state.set_state(key="world.population.humans", value=1000)
    world_state.set_state(key="world.population.elves", value=500)
    
    # Check if the manager can find these values
    print("\nChecking manager state...")
    humans_var = world_state.manager.get_state_variable("world.population.humans")
    elves_var = world_state.manager.get_state_variable("world.population.elves")
    print(f"Humans variable: {humans_var}")
    print(f"Elves variable: {elves_var}")
    
    # Check if derivative calculator can find these values
    print("\nChecking derivative calculator access...")
    calc = world_state.derivative_calculator
    humans_var_calc = calc.world_state.get_state_variable("world.population.humans")
    elves_var_calc = calc.world_state.get_state_variable("world.population.elves")
    print(f"Derivative calc humans variable: {humans_var_calc}")
    print(f"Derivative calc elves variable: {elves_var_calc}")
    
    # Register a simple rule
    print("\nRegistering derivative rule...")
    calc.register_rule(
        DerivedStateRule(
            key="test.population.total",
            dependencies=["world.population.humans", "world.population.elves"],
            calculator=lambda deps: sum(v for v in deps.values() if v is not None),
            category=StateCategory.POPULATION,
            tags=["population", "total", "derived"],
            description="Test total population",
        )
    )
    
    # Test the derived value
    print("\nTesting derived value...")
    total_pop = world_state.get_derived_value("test.population.total")
    print(f"Total population: {total_pop}")
    
    # Debug the rule calculation
    print("\nDebug rule calculation...")
    rule = calc.rules.get("test.population.total")
    if rule:
        dependency_values = {}
        for dep_key in rule.dependencies:
            print(f"  Looking for dependency: {dep_key}")
            state_var = calc.world_state.get_state_variable(dep_key)
            dep_value = state_var.value if state_var else None
            dependency_values[dep_key] = dep_value
            print(f"    Found: {state_var} -> {dep_value}")
        
        print(f"Dependency values: {dependency_values}")
        try:
            result = rule.calculator(dependency_values)
            print(f"Calculator result: {result}")
        except Exception as e:
            print(f"Calculator error: {e}")

if __name__ == "__main__":
    test_derivative_state() 
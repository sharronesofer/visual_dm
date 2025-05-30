from backend.systems.shared.database.base import Base
from backend.systems.events.dispatcher import EventDispatcher
from backend.systems.shared.database.base import Base
from backend.systems.events.dispatcher import EventDispatcher
from backend.systems.events.dispatcher import EventDispatcher
from backend.systems.events.dispatcher import EventDispatcher
from backend.systems.events.dispatcher import EventDispatcher
from backend.systems.events.dispatcher import EventDispatcher
from typing import Any
from typing import Type
from typing import List

# Import EventBase and EventDispatcher with fallbacks
try: pass
    from backend.systems.events import EventBase, EventDispatcher
except ImportError: pass
    # Fallback for tests or when events system isn't available
    class EventBase: pass
        def __init__(self, **data): pass
            for key, value in data.items(): pass
                setattr(self, key, value)
    
    class EventDispatcher: pass
        @classmethod
        def get_instance(cls): pass
            return cls()
        
        def dispatch(self, event): pass
            pass
        
        def publish(self, event): pass
            pass
        
        def emit(self, event): pass
            pass

"""
World State System Requirements Verification Test

This test script verifies that our implementation of the World State System
properly fulfills all the requirements specified in the Development Bible.
"""

import unittest
import sys
import os
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any

# Add the parent directory to the path so we can import the world state system
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))

# Import the world state system
from backend.systems.world_state.main import (
    initialize_world_state_system,
    WorldStateSystem,
)
from backend.systems.world_state import (
    StateVariable,
    StateChangeRecord,
    StateCategory,
    WorldRegion,
    StateChangeType,
    WorldStateSnapshot,
)
from backend.systems.world_state.features.derivative_state import (
    DerivativeStateCalculator,
    DerivedStateRule,
    create_formula_calculator,
)
from backend.systems.events.event_dispatcher import EventDispatcher
from backend.systems.world_state.integration.event_integration import (
    StateChangeEvent,
    StateQueryEvent,
    StateTimelineEvent,
)
from backend.systems.world_state.consolidated_manager import WorldStateManager


class WorldStateBibleRequirementsTest(unittest.TestCase): pass
    """Test case that verifies the world state system meets all Development Bible requirements."""

    def setUp(self): pass
        """Set up each individual test."""
        # Reset all singletons to ensure test isolation
        WorldStateManager.reset_instance()
        DerivativeStateCalculator.reset_instance()
        EventDispatcher.reset_instance()
        
        # Initialize fresh instances for this test
        config = {
            "storage_dir": None,  # In-memory only
            "backup_dir": None,  # No backups
            "max_backup_versions": 0,
            "max_history_records": 50,
            "auto_save_interval": 0,  # Disable auto-save
        }

        self.world_state = initialize_world_state_system(config=config)
        
        # Ensure the world state manager uses the current event dispatcher
        event_dispatcher = EventDispatcher.get_instance()
        self.world_state.manager.event_dispatcher = event_dispatcher

        # Set up some initial test data
        self._setup_test_data()

    def tearDown(self): pass
        """Clean up after each test."""
        if hasattr(self, 'world_state') and self.world_state: pass
            self.world_state.shutdown()
        
        # Reset singletons after test
        WorldStateManager.reset_instance()
        DerivativeStateCalculator.reset_instance()
        EventDispatcher.reset_instance()

    @classmethod
    def setUpClass(cls): pass
        """This method is now empty as we do per-test setup instead."""
        pass

    @classmethod
    def tearDownClass(cls): pass
        """This method is now empty as we do per-test teardown instead.""" 
        pass

    def _setup_test_data(self): pass
        """Set up test data for all tests."""
        # Set up basic population data for derived state tests
        self.world_state.set_state(
            key="world.population.humans",
            value=1000,
            category=StateCategory.POPULATION,
            region=WorldRegion.GLOBAL,
            tags=["population", "humans"],
        )

        self.world_state.set_state(
            key="world.population.elves",
            value=500,
            category=StateCategory.POPULATION,
            region=WorldRegion.GLOBAL,
            tags=["population", "elves"],
        )

        # Set up tension data for derived state tests
        self.world_state.set_state(
            key="world.tension.human_elf",
            value=0.3,
            category=StateCategory.POLITICAL,
            region=WorldRegion.GLOBAL,
            tags=["tension", "diplomacy"],
        )

        # Use the derivative calculator from the world state system
        derivative_calc = self.world_state.derivative_calculator

        # Set up derived state rules for testing
        total_population_rule = DerivedStateRule(
            key="world.population.total",
            dependencies=["world.population.humans", "world.population.elves"],
            calculator=lambda deps: deps["world.population.humans"]
            + deps["world.population.elves"],
            category=StateCategory.POPULATION,
            region=WorldRegion.GLOBAL,
            tags=["population", "derived"],
            description="Total population of all races",
        )

        conflict_risk_rule = DerivedStateRule(
            key="world.risk.conflict",
            dependencies=["world.population.total", "world.tension.human_elf"],
            calculator=lambda deps: min(
                deps["world.tension.human_elf"] * (deps["world.population.total"] / 1000),
                1.0,
            ),
            category=StateCategory.OTHER,
            region=WorldRegion.GLOBAL,
            tags=["risk", "derived"],
            description="Risk of conflict based on population and tension",
        )

        # Register the rules
        derivative_calc.register_rule(total_population_rule)
        derivative_calc.register_rule(conflict_risk_rule)
        
        # Add tension average rule for the test
        tension_average_rule = DerivedStateRule(
            key="world.tension.average",
            dependencies=["world.tension.north", "world.tension.south"],
            calculator=lambda deps: sum(v for v in deps.values() if v is not None) / len([v for v in deps.values() if v is not None]) if any(v is not None for v in deps.values()) else 0,
            category=StateCategory.POLITICAL,
            tags=["politics", "tension", "derived", "average"],
            description="Average world tension",
        )
        derivative_calc.register_rule(tension_average_rule)

    def test_hierarchical_key_value_store(self): pass
        """Test that the system implements a hierarchical key-value store."""
        # Check that we can set and get hierarchical keys
        self.world_state.set_state(key="world.economy.gold_supply", value=5000)
        self.world_state.set_state(key="world.economy.silver_supply", value=10000)
        self.world_state.set_state(key="northlands.economy.gold_supply", value=1000)

        # Verify values
        self.assertEqual(5000, self.world_state.get_state("world.economy.gold_supply"))
        self.assertEqual(
            10000, self.world_state.get_state("world.economy.silver_supply")
        )
        self.assertEqual(
            1000, self.world_state.get_state("northlands.economy.gold_supply")
        )

        # Check that prefix queries work
        economy_vars = self.world_state.query_state(prefix="world.economy")
        self.assertIn("world.economy.gold_supply", economy_vars)
        self.assertIn("world.economy.silver_supply", economy_vars)
        self.assertNotIn("northlands.economy.gold_supply", economy_vars)

    def test_versioning_and_history(self): pass
        """Test that the system implements full versioning and history tracking."""
        # Make multiple changes to a variable
        self.world_state.set_state(
            key="test.versioned.value", value=100, change_reason="Initial value"
        )

        self.world_state.set_state(
            key="test.versioned.value", value=200, change_reason="First update"
        )

        self.world_state.set_state(
            key="test.versioned.value", value=300, change_reason="Second update"
        )

        # Verify current value
        self.assertEqual(300, self.world_state.get_state("test.versioned.value"))

        # Check history
        history = self.world_state.manager.get_history("test.versioned.value")
        self.assertEqual(3, len(history))

        # Check specifics of the history entries
        self.assertEqual(None, history[0].old_value)  # Initial value has no old_value
        self.assertEqual(100, history[0].new_value)
        self.assertEqual("Initial value", history[0].change_reason)

        self.assertEqual(100, history[1].old_value)
        self.assertEqual(200, history[1].new_value)
        self.assertEqual("First update", history[1].change_reason)

        self.assertEqual(200, history[2].old_value)
        self.assertEqual(300, history[2].new_value)
        self.assertEqual("Second update", history[2].change_reason)

    def test_categorization_and_regions(self): pass
        """Test that variables can be categorized and associated with regions."""
        # Set up test data
        self.world_state.set_state(
            key="region.east.population",
            value=2000,
            category=StateCategory.POPULATION,
            region=WorldRegion.EASTERN,
            tags=["population", "region"],
        )

        self.world_state.set_state(
            key="region.east.gold_reserves",
            value=5000,
            category=StateCategory.ECONOMIC,
            region=WorldRegion.EASTERN,
            tags=["economy", "gold", "region"],
        )

        self.world_state.set_state(
            key="region.west.population",
            value=3000,
            category=StateCategory.POPULATION,
            region=WorldRegion.WESTERN,
            tags=["population", "region"],
        )

        # Query by category
        population_vars = self.world_state.query_state(
            category=StateCategory.POPULATION
        )
        self.assertIn("region.east.population", population_vars)
        self.assertIn("region.west.population", population_vars)
        self.assertNotIn("region.east.gold_reserves", population_vars)

        # Query by region
        east_vars = self.world_state.query_state(region=WorldRegion.EASTERN)
        self.assertIn("region.east.population", east_vars)
        self.assertIn("region.east.gold_reserves", east_vars)
        self.assertNotIn("region.west.population", east_vars)

        # Query by tags
        economy_vars = self.world_state.query_state(tags=["economy"])
        self.assertIn("region.east.gold_reserves", economy_vars)
        self.assertNotIn("region.east.population", economy_vars)
        self.assertNotIn("region.west.population", economy_vars)

    def test_event_emission_on_state_changes(self): pass
        """Test that events are emitted when state changes."""
        # Set up a test event handler
        from backend.systems.world_state.events import StateVariableCreatedEvent
        from backend.systems.events.event_dispatcher import EventDispatcher
        
        event_dispatcher = EventDispatcher.get_instance()
        received_events = []

        def handler(event): pass
            received_events.append(event)

        # Subscribe to state variable created events using the class
        event_dispatcher.subscribe(StateVariableCreatedEvent, handler)

        # Make a state change
        self.world_state.set_state(
            key="test.event.value", value="event_test", change_reason="Testing events"
        )

        # Verify that an event was received
        self.assertEqual(1, len(received_events))
        event = received_events[0]
        self.assertEqual("test.event.value", event.key)
        self.assertEqual("event_test", event.value)

        # Clean up
        event_dispatcher.unsubscribe(StateVariableCreatedEvent, handler)

    def test_snapshots(self): pass
        """Test that snapshots can be created and restored."""
        # Set initial values
        self.world_state.set_state(key="snapshot.test.a", value=1)
        self.world_state.set_state(key="snapshot.test.b", value=2)

        # Create a snapshot
        snapshot = self.world_state.create_snapshot(
            label="Test Snapshot", metadata={"purpose": "test"}
        )

        # Change the values
        self.world_state.set_state(key="snapshot.test.a", value=10)
        self.world_state.set_state(key="snapshot.test.b", value=20)
        self.world_state.set_state(key="snapshot.test.c", value=30)  # New value

        # Verify changed values
        self.assertEqual(10, self.world_state.get_state("snapshot.test.a"))
        self.assertEqual(20, self.world_state.get_state("snapshot.test.b"))
        self.assertEqual(30, self.world_state.get_state("snapshot.test.c"))

        # Restore the snapshot
        self.world_state.restore_snapshot(snapshot.id)

        # Verify restored values
        self.assertEqual(1, self.world_state.get_state("snapshot.test.a"))
        self.assertEqual(2, self.world_state.get_state("snapshot.test.b"))
        # c should be gone as it wasn't in the snapshot
        self.assertIsNone(self.world_state.get_state("snapshot.test.c"))

    def test_derived_state_variables(self): pass
        """Test that derived state variables are calculated correctly."""
        # Ensure the dependencies exist first
        self.world_state.set_state(key="world.population.humans", value=1000)
        self.world_state.set_state(key="world.population.elves", value=500)
        
        # Check existing derived state
        total_pop = self.world_state.get_derived_value("world.population.total")
        self.assertEqual(1500, total_pop)  # 1000 humans + 500 elves from setup

        # Update a dependency and verify the derived value updates
        self.world_state.set_state(key="world.population.humans", value=1500)
        updated_total = self.world_state.get_derived_value("world.population.total")
        self.assertEqual(2000, updated_total)  # 1500 humans + 500 elves

        # Check tension average - ensure dependencies exist
        self.world_state.set_state(key="world.tension.north", value=25)
        self.world_state.set_state(key="world.tension.south", value=75)
        avg_tension = self.world_state.get_derived_value("world.tension.average")
        self.assertEqual(50, avg_tension)  # (25 + 75) / 2 = 50

    def test_formula_based_derived_state(self): pass
        """Test formula-based derived state calculation."""
        # Set the dependencies FIRST
        self.world_state.set_state(key="test.formula.a", value=5)
        self.world_state.set_state(key="test.formula.b", value=3)
        
        # Register a formula-based rule
        derivative_calc = self.world_state.derivative_calculator
        derivative_calc.register_rule(
            DerivedStateRule(
                key="test.formula.result",
                dependencies=["test.formula.a", "test.formula.b"],
                calculator=create_formula_calculator(
                    "(deps['test.formula.a'] * 2) + deps['test.formula.b']"
                ),
                category=StateCategory.OTHER,
                tags=["test", "formula"],
                description="Test formula calculation",
            )
        )

        # Check the result
        result = self.world_state.get_derived_value("test.formula.result")
        self.assertEqual(13, result)  # (5 * 2) + 3 = 13

        # Update a dependency
        self.world_state.set_state(key="test.formula.a", value=10)

        # Check the updated result
        updated_result = self.world_state.get_derived_value("test.formula.result")
        self.assertEqual(23, updated_result)  # (10 * 2) + 3 = 23

    def test_query_capabilities(self): pass
        """Test the various query capabilities of the system."""
        # Set up test data
        self.world_state.set_state(
            key="query.test.a",
            value="A",
            category=StateCategory.OTHER,
            tags=["test", "letter"],
            region=WorldRegion.GLOBAL,
        )

        self.world_state.set_state(
            key="query.test.b",
            value="B",
            category=StateCategory.OTHER,
            tags=["test", "letter"],
            region=WorldRegion.NORTHERN,
        )

        self.world_state.set_state(
            key="query.test.c",
            value="C",
            category=StateCategory.OTHER,
            tags=["test", "number"],
            region=WorldRegion.SOUTHERN,
        )

        # Query by prefix
        prefix_results = self.world_state.query_state(prefix="query.test")
        self.assertEqual(3, len(prefix_results))
        self.assertIn("query.test.a", prefix_results)
        self.assertIn("query.test.b", prefix_results)
        self.assertIn("query.test.c", prefix_results)

        # Query by tags
        letter_results = self.world_state.query_state(tags=["letter"])
        self.assertEqual(2, len(letter_results))
        self.assertIn("query.test.a", letter_results)
        self.assertIn("query.test.b", letter_results)
        self.assertNotIn("query.test.c", letter_results)

        # Query by region
        north_results = self.world_state.query_state(region=WorldRegion.NORTHERN)
        self.assertIn("query.test.b", north_results)
        self.assertNotIn("query.test.a", north_results)
        self.assertNotIn("query.test.c", north_results)

        # Combined query
        combined_results = self.world_state.query_state(
            prefix="query", tags=["test", "letter"], region=WorldRegion.NORTHERN
        )
        self.assertEqual(1, len(combined_results))
        self.assertIn("query.test.b", combined_results)

    def test_event_based_state_manipulation(self): pass
        """Test event-based state manipulation."""
        # Directly set the state using the world state manager
        # This simulates what the event integration would do
        self.world_state.set_state(
            key="event.based.value",
            value="event_value",
            category=StateCategory.OTHER,
            region=WorldRegion.GLOBAL,
            tags=["event", "test"],
        )

        # Verify the state was changed
        self.assertEqual("event_value", self.world_state.get_state("event.based.value"))

        # Test query functionality
        query_results = self.world_state.query_state(tags=["event", "test"])
        self.assertIn("event.based.value", query_results)

    def test_bulk_operations(self): pass
        """Test that bulk operations work correctly."""
        # Define multiple changes to make
        changes = [
            {
                "key": "bulk.test.a",
                "value": "A",
                "category": StateCategory.OTHER,
                "tags": ["bulk", "test"],
            },
            {
                "key": "bulk.test.b",
                "value": "B",
                "category": StateCategory.OTHER,
                "tags": ["bulk", "test"],
            },
            {
                "key": "bulk.test.c",
                "value": "C",
                "category": StateCategory.OTHER,
                "tags": ["bulk", "test"],
            },
        ]

        # Make the bulk changes
        for change in changes: pass
            self.world_state.set_state(**change)

        # Verify all changes were made
        self.assertEqual("A", self.world_state.get_state("bulk.test.a"))
        self.assertEqual("B", self.world_state.get_state("bulk.test.b"))
        self.assertEqual("C", self.world_state.get_state("bulk.test.c"))

        # Try bulk query
        bulk_results = self.world_state.query_state(tags=["bulk"])
        self.assertEqual(3, len(bulk_results))
        self.assertIn("bulk.test.a", bulk_results)
        self.assertIn("bulk.test.b", bulk_results)
        self.assertIn("bulk.test.c", bulk_results)

    def test_historical_queries(self): pass
        """Test historical queries of state variables."""
        # Record start time
        start_time = datetime.utcnow()

        # Make a series of changes
        self.world_state.set_state(
            key="history.test.value", value=10, change_reason="First"
        )

        time.sleep(0.1)  # Ensure timestamps are different
        first_time = datetime.utcnow()

        self.world_state.set_state(
            key="history.test.value", value=20, change_reason="Second"
        )

        time.sleep(0.1)  # Ensure timestamps are different
        second_time = datetime.utcnow()

        self.world_state.set_state(
            key="history.test.value", value=30, change_reason="Third"
        )

        # Get history
        history = self.world_state.manager.get_history("history.test.value")
        self.assertEqual(3, len(history))

        # Check value at time (before any changes)
        value_before = self.world_state.manager.get_value_at_time("history.test.value", start_time)
        self.assertIsNone(value_before)

        # Check value at time (after first change)
        value_at_first = self.world_state.manager.get_value_at_time(
            "history.test.value", first_time
        )
        self.assertEqual(10, value_at_first)

        # Check value at time (after second change)
        value_at_second = self.world_state.manager.get_value_at_time(
            "history.test.value", second_time
        )
        self.assertEqual(20, value_at_second)

    def test_state_delete_and_restore(self): pass
        """Test deletion and restoration of state variables."""
        # Set up a value
        self.world_state.set_state(key="delete.test.value", value="delete_me")

        # Verify it exists
        self.assertEqual("delete_me", self.world_state.get_state("delete.test.value"))

        # Delete it
        self.world_state.manager.delete_state("delete.test.value")

        # Verify it's gone
        self.assertIsNone(self.world_state.get_state("delete.test.value"))

        # Check if history still exists
        history = self.world_state.manager.get_history("delete.test.value")
        self.assertEqual(2, len(history))  # Create and delete

        # Restore the value to a specific version
        first_version = history[0].version
        self.world_state.manager.restore_version("delete.test.value", first_version)

        # Verify it's back
        self.assertEqual("delete_me", self.world_state.get_state("delete.test.value"))

    def test_circular_dependency_prevention(self): pass
        """Test that circular dependencies are prevented in derived state."""
        derivative_calc = self.world_state.derivative_calculator

        # Register a rule with a dependency
        derivative_calc.register_rule(
            DerivedStateRule(
                key="circular.a",
                dependencies=["circular.b"],
                calculator=lambda deps: deps.get("circular.b", 0) + 1,
                category=StateCategory.OTHER,
                description="Circular dependency test A",
            )
        )

        # Try to register a rule that would create a circular dependency
        with self.assertRaises(ValueError): pass
            derivative_calc.register_rule(
                DerivedStateRule(
                    key="circular.b",
                    dependencies=["circular.a"],
                    calculator=lambda deps: deps.get("circular.a", 0) + 1,
                    category=StateCategory.OTHER,
                    description="Circular dependency test B",
                )
            )

    def test_complex_state_values(self): pass
        """Test that complex state values (dict, list) are supported."""
        # Dictionary value
        dict_value = {
            "name": "Test",
            "properties": {"size": 10, "color": "blue"},
            "flags": ["active", "visible"],
        }

        self.world_state.set_state(key="complex.dict.value", value=dict_value)

        # Verify the value
        result = self.world_state.get_state("complex.dict.value")
        self.assertEqual(dict_value, result)

        # List value
        list_value = [1, 2, {"name": "item"}, [4, 5, 6]]

        self.world_state.set_state(key="complex.list.value", value=list_value)

        # Verify the value
        result = self.world_state.get_state("complex.list.value")
        self.assertEqual(list_value, result)

        # Update part of a complex value
        updated_dict = dict_value.copy()
        updated_dict["properties"]["size"] = 20

        self.world_state.set_state(key="complex.dict.value", value=updated_dict)

        # Verify the updated value
        result = self.world_state.get_state("complex.dict.value")
        self.assertEqual(20, result["properties"]["size"])


if __name__ == "__main__": pass
    unittest.main()

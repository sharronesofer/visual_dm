from backend.systems.shared.database.base import Base
from backend.systems.events.dispatcher import EventDispatcher
from backend.systems.shared.database.base import Base
from backend.systems.events.dispatcher import EventDispatcher
from backend.systems.events.dispatcher import EventDispatcher
from backend.systems.events.dispatcher import EventDispatcher
from backend.systems.events.dispatcher import EventDispatcher
from backend.systems.events.dispatcher import EventDispatcher
from typing import Any

# Import EventBase and EventDispatcher with fallbacks
try:
    from backend.systems.events import EventBase, EventDispatcher
except ImportError:
    # Fallback for tests or when events system isn't available
    class EventBase:
        def __init__(self, **data):
            for key, value in data.items():
                setattr(self, key, value)
    
    class EventDispatcher:
        @classmethod
        def get_instance(cls):
            return cls()
        
        def dispatch(self, event):
        def publish(self, event):
        def emit(self, event):
"""
Tests for backend.systems.world_state.features.derivative_state

Comprehensive tests for the DerivativeStateCalculator class and related functionality.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from typing import Dict, Any

# Import the module being tested
try:
    from backend.systems.world_state.features.derivative_state import (
        DerivativeStateCalculator,
        DerivedStateRule,
        create_formula_calculator
    )
    from backend.systems.world_state.consolidated_manager import WorldStateManager
    from backend.systems.world_state.consolidated_state_models import (
        StateVariable,
        StateCategory,
        WorldRegion
    )
    from backend.systems.events.event_dispatcher import EventDispatcher
except ImportError as e:
    pytest.skip(f"Could not import required modules: {e}", allow_module_level=True)


@pytest.fixture
def reset_singletons():
    """Reset all singleton instances before each test."""
    # Store original instances
    original_calculator = DerivativeStateCalculator._instance
    original_manager = WorldStateManager._instance
    
    # Clear instances
    DerivativeStateCalculator._instance = None
    WorldStateManager._instance = None
    
    yield
    
    # Restore original instances
    DerivativeStateCalculator._instance = original_calculator
    WorldStateManager._instance = original_manager


@pytest.fixture
def mock_world_state():
    """Create a mock world state manager."""
    mock_manager = Mock(spec=WorldStateManager)
    mock_manager.get_state_variable = Mock()
    return mock_manager


@pytest.fixture
def mock_event_dispatcher():
    """Create a mock event dispatcher."""
    mock_dispatcher = Mock(spec=EventDispatcher)
    mock_dispatcher.subscribe = Mock()
    return mock_dispatcher


@pytest.fixture
def calculator(reset_singletons, mock_world_state, mock_event_dispatcher):
    """Create a derivative state calculator with mocked dependencies."""
    with patch('backend.systems.world_state.features.derivative_state.WorldStateManager.get_instance', return_value=mock_world_state), \
         patch('backend.systems.world_state.features.derivative_state.EventDispatcher.get_instance', return_value=mock_event_dispatcher):
        calc = DerivativeStateCalculator.get_instance()
        yield calc


class TestDerivedStateRule:
    """Test DerivedStateRule class."""
    
    def test_creation_with_defaults(self):
        """Test creating a rule with default values."""
        def simple_calc(deps):
            return sum(deps.values())
        
        rule = DerivedStateRule(
            key="test.rule",
            dependencies=["dep1", "dep2"],
            calculator=simple_calc
        )
        
        assert rule.key == "test.rule"
        assert rule.dependencies == ["dep1", "dep2"]
        assert rule.calculator == simple_calc
        assert rule.category == StateCategory.OTHER
        assert rule.region == WorldRegion.GLOBAL
        assert "derived" in rule.tags
        assert rule.description == ""
        assert rule.metadata == {}
    
    def test_creation_with_all_fields(self):
        """Test creating a rule with all fields specified."""
        def custom_calc(deps):
            return deps.get("dep1", 0) * 2
        
        rule = DerivedStateRule(
            key="test.custom",
            dependencies=["dep1"],
            calculator=custom_calc,
            category=StateCategory.POLITICAL,
            region=WorldRegion.NORTHERN,
            tags=["custom", "test"],
            description="A test rule",
            metadata={"version": "1.0"}
        )
        
        assert rule.key == "test.custom"
        assert rule.dependencies == ["dep1"]
        assert rule.category == StateCategory.POLITICAL
        assert rule.region == WorldRegion.NORTHERN
        assert "custom" in rule.tags
        assert "test" in rule.tags
        assert "derived" in rule.tags  # Should be added automatically
        assert rule.description == "A test rule"
        assert rule.metadata == {"version": "1.0"}
    
    def test_repr(self):
        """Test string representation."""
        def calc(deps):
            return 0
        
        rule = DerivedStateRule(
            key="test.repr",
            dependencies=["dep1", "dep2", "dep3"],
            calculator=calc
        )
        
        repr_str = repr(rule)
        assert "DerivedStateRule" in repr_str
        assert "test.repr" in repr_str
        assert "deps=3" in repr_str


class TestDerivativeStateCalculatorSingleton:
    """Test singleton behavior of DerivativeStateCalculator."""
    
    def test_singleton_instance(self, reset_singletons):
        """Test that get_instance returns the same instance."""
        with patch('backend.systems.world_state.features.derivative_state.WorldStateManager.get_instance'), \
             patch('backend.systems.world_state.features.derivative_state.EventDispatcher.get_instance'):
            calc1 = DerivativeStateCalculator.get_instance()
            calc2 = DerivativeStateCalculator.get_instance()
            
            assert calc1 is calc2
    
    def test_init_raises_error_if_instance_exists(self, reset_singletons):
        """Test that creating a new instance raises an error if one already exists."""
        with patch('backend.systems.world_state.features.derivative_state.WorldStateManager.get_instance'), \
             patch('backend.systems.world_state.features.derivative_state.EventDispatcher.get_instance'):
            # Create first instance
            calc1 = DerivativeStateCalculator.get_instance()
            
            # Try to create second instance directly
            with pytest.raises(RuntimeError):
                DerivativeStateCalculator()


class TestDerivativeStateCalculatorInitialization:
    """Test initialization functionality."""
    
    def test_initialization(self, calculator, mock_event_dispatcher):
        """Test calculator initialization."""
        calculator.initialize()
        
        # Verify event subscription
        mock_event_dispatcher.subscribe.assert_called_with(
            "world_state.changed", calculator._handle_state_change
        )
        
        # Verify built-in rules are registered
        assert len(calculator.rules) > 0
        assert "world.population.total" in calculator.rules


class TestRuleManagement:
    """Test rule registration, updating, and removal."""
    
    def test_register_new_rule(self, calculator):
        """Test registering a new rule."""
        def calc_func(deps):
            return deps.get("dep1", 0) + deps.get("dep2", 0)
        
        rule = DerivedStateRule(
            key="test.new.rule",
            dependencies=["dep1", "dep2"],
            calculator=calc_func
        )
        
        # Mock the world state to return values for dependencies
        calculator.world_state.get_state_variable.side_effect = lambda key: (
            Mock(value=5) if key == "dep1" else
            Mock(value=3) if key == "dep2" else
            None
        )
        
        result = calculator.register_rule(rule)
        
        assert result is True
        assert "test.new.rule" in calculator.rules
        assert calculator.rules["test.new.rule"] == rule
        
        # Check dependency graphs are updated
        assert "dep1" in calculator.dependency_graph
        assert "dep2" in calculator.dependency_graph
        assert "test.new.rule" in calculator.dependency_graph["dep1"]
        assert "test.new.rule" in calculator.dependency_graph["dep2"]
    
    def test_register_duplicate_rule(self, calculator):
        """Test registering a rule that already exists."""
        def calc_func(deps):
            return 0
        
        rule = DerivedStateRule(
            key="test.duplicate",
            dependencies=["dep1"],
            calculator=calc_func
        )
        
        # Register first time
        calculator.register_rule(rule)
        
        # Try to register again
        result = calculator.register_rule(rule)
        
        assert result is False
    
    def test_register_circular_dependency(self, calculator):
        """Test that circular dependencies are prevented."""
        def calc_func(deps):
            return 0
        
        # Register first rule
        rule1 = DerivedStateRule(
            key="test.circular1",
            dependencies=["test.circular2"],
            calculator=calc_func
        )
        calculator.register_rule(rule1)
        
        # Try to register rule that would create circular dependency
        rule2 = DerivedStateRule(
            key="test.circular2",
            dependencies=["test.circular1"],
            calculator=calc_func
        )
        
        with pytest.raises(ValueError):
            calculator.register_rule(rule2)
    
    def test_update_existing_rule(self, calculator):
        """Test updating an existing rule."""
        def calc_func1(deps):
            return deps.get("dep1", 0)
        
        def calc_func2(deps):
            return deps.get("dep1", 0) * 2
        
        # Register initial rule
        rule1 = DerivedStateRule(
            key="test.update",
            dependencies=["dep1"],
            calculator=calc_func1
        )
        calculator.register_rule(rule1)
        
        # Update rule
        rule2 = DerivedStateRule(
            key="test.update",
            dependencies=["dep1", "dep2"],
            calculator=calc_func2
        )
        
        result = calculator.update_rule(rule2)
        
        assert result is True
        assert calculator.rules["test.update"] == rule2
    
    def test_update_nonexistent_rule(self, calculator):
        """Test updating a rule that doesn't exist."""
        def calc_func(deps):
            return 0
        
        rule = DerivedStateRule(
            key="test.nonexistent",
            dependencies=["dep1"],
            calculator=calc_func
        )
        
        result = calculator.update_rule(rule)
        
        assert result is False
    
    def test_remove_rule(self, calculator):
        """Test removing a rule."""
        def calc_func(deps):
            return 0
        
        rule = DerivedStateRule(
            key="test.remove",
            dependencies=["dep1"],
            calculator=calc_func
        )
        
        # Register rule
        calculator.register_rule(rule)
        assert "test.remove" in calculator.rules
        
        # Remove rule
        result = calculator.remove_rule("test.remove")
        
        assert result is True
        assert "test.remove" not in calculator.rules
        assert "test.remove" not in calculator.value_cache
        assert "test.remove" not in calculator.last_update
    
    def test_remove_nonexistent_rule(self, calculator):
        """Test removing a rule that doesn't exist."""
        result = calculator.remove_rule("test.nonexistent")
        
        assert result is False


class TestValueCalculation:
    """Test derived value calculation."""
    
    def test_get_derived_value_simple(self, calculator):
        """Test getting a simple derived value."""
        def calc_func(deps):
            return deps.get("dep1", 0) + deps.get("dep2", 0)
        
        rule = DerivedStateRule(
            key="test.simple",
            dependencies=["dep1", "dep2"],
            calculator=calc_func
        )
        
        # Mock world state values
        calculator.world_state.get_state_variable.side_effect = lambda key: (
            Mock(value=10) if key == "dep1" else
            Mock(value=20) if key == "dep2" else
            None
        )
        
        calculator.register_rule(rule)
        
        result = calculator.get_derived_value("test.simple")
        
        assert result == 30
        assert "test.simple" in calculator.value_cache
        assert calculator.value_cache["test.simple"] == 30
    
    def test_get_derived_value_with_derived_dependency(self, calculator):
        """Test getting a derived value that depends on another derived value."""
        def calc_func1(deps):
            return deps.get("base1", 0) + deps.get("base2", 0)
        
        def calc_func2(deps):
            return deps.get("test.level1", 0) * 2
        
        # Register first level rule
        rule1 = DerivedStateRule(
            key="test.level1",
            dependencies=["base1", "base2"],
            calculator=calc_func1
        )
        
        # Register second level rule (depends on first)
        rule2 = DerivedStateRule(
            key="test.level2",
            dependencies=["test.level1"],
            calculator=calc_func2
        )
        
        # Mock world state values
        calculator.world_state.get_state_variable.side_effect = lambda key: (
            Mock(value=5) if key == "base1" else
            Mock(value=7) if key == "base2" else
            None
        )
        
        calculator.register_rule(rule1)
        calculator.register_rule(rule2)
        
        result = calculator.get_derived_value("test.level2")
        
        # Should be (5 + 7) * 2 = 24
        assert result == 24
    
    def test_get_derived_value_nonexistent(self, calculator):
        """Test getting a derived value that doesn't exist."""
        result = calculator.get_derived_value("test.nonexistent")
        
        assert result is None
    
    def test_get_derived_value_with_error(self, calculator):
        """Test getting a derived value when calculation fails."""
        def calc_func(deps):
            raise ValueError("Calculation error")
        
        rule = DerivedStateRule(
            key="test.error",
            dependencies=["dep1"],
            calculator=calc_func
        )
        
        calculator.register_rule(rule)
        
        result = calculator.get_derived_value("test.error")
        
        # Should return None when calculation fails
        assert result is None


class TestDependencyManagement:
    """Test dependency tracking and updates."""
    
    def test_dependency_graph_creation(self, calculator):
        """Test that dependency graphs are created correctly."""
        def calc_func(deps):
            return 0
        
        rule = DerivedStateRule(
            key="test.deps",
            dependencies=["dep1", "dep2"],
            calculator=calc_func
        )
        
        calculator.register_rule(rule)
        
        # Check dependency graph
        assert "dep1" in calculator.dependency_graph
        assert "dep2" in calculator.dependency_graph
        assert "test.deps" in calculator.dependency_graph["dep1"]
        assert "test.deps" in calculator.dependency_graph["dep2"]
        
        # Check inverse dependency graph
        assert "dep1" in calculator.inverse_dependency_graph["test.deps"]
        assert "dep2" in calculator.inverse_dependency_graph["test.deps"]
    
    def test_handle_state_change(self, calculator):
        """Test handling of state change events."""
        def calc_func(deps):
            return deps.get("dep1", 0) * 2
        
        rule = DerivedStateRule(
            key="test.change",
            dependencies=["dep1"],
            calculator=calc_func
        )
        
        calculator.register_rule(rule)
        
        # Mock initial value
        calculator.world_state.get_state_variable.return_value = Mock(value=5)
        initial_value = calculator.get_derived_value("test.change")
        assert initial_value == 10
        
        # Mock changed value
        calculator.world_state.get_state_variable.return_value = Mock(value=8)
        
        # Simulate state change event
        calculator._handle_state_change({"key": "dep1"})
        
        # Check that derived value was recalculated
        new_value = calculator.get_derived_value("test.change")
        assert new_value == 16
    
    def test_get_dependent_keys(self, calculator):
        """Test getting keys that depend on a given key."""
        def calc_func(deps):
            return 0
        
        rule1 = DerivedStateRule(
            key="test.dep1",
            dependencies=["base_key"],
            calculator=calc_func
        )
        
        rule2 = DerivedStateRule(
            key="test.dep2",
            dependencies=["base_key", "other_key"],
            calculator=calc_func
        )
        
        calculator.register_rule(rule1)
        calculator.register_rule(rule2)
        
        dependent_keys = calculator.get_dependent_keys("base_key")
        
        assert "test.dep1" in dependent_keys
        assert "test.dep2" in dependent_keys
        assert len(dependent_keys) == 2


class TestUtilityMethods:
    """Test utility and information methods."""
    
    def test_get_all_derived_keys(self, calculator):
        """Test getting all derived keys."""
        def calc_func(deps):
            return 0
        
        # Initialize to register built-in rules
        calculator.initialize()
        
        rule1 = DerivedStateRule(key="test.key1", dependencies=["dep1"], calculator=calc_func)
        rule2 = DerivedStateRule(key="test.key2", dependencies=["dep2"], calculator=calc_func)
        
        calculator.register_rule(rule1)
        calculator.register_rule(rule2)
        
        all_keys = calculator.get_all_derived_keys()
        
        assert "test.key1" in all_keys
        assert "test.key2" in all_keys
        # Should also include built-in rules
        assert "world.population.total" in all_keys
    
    def test_get_rule_info(self, calculator):
        """Test getting rule information."""
        def calc_func(deps):
            return deps.get("dep1", 0) * 2
        
        rule = DerivedStateRule(
            key="test.info",
            dependencies=["dep1"],
            calculator=calc_func,
            category=StateCategory.POLITICAL,
            region=WorldRegion.NORTHERN,
            tags=["test", "info"],
            description="Test rule for info",
            metadata={"version": "1.0"}
        )
        
        calculator.register_rule(rule)
        
        info = calculator.get_rule_info("test.info")
        
        assert info["key"] == "test.info"
        assert info["dependencies"] == ["dep1"]
        assert info["category"] == "POLITICAL"
        assert info["region"] == "NORTHERN"
        assert info["tags"] == ["test", "info", "derived"]
        assert info["description"] == "Test rule for info"
        assert info["metadata"] == {"version": "1.0"}
    
    def test_get_rule_info_nonexistent(self, calculator):
        """Test getting rule info for nonexistent rule."""
        info = calculator.get_rule_info("test.nonexistent")
        
        assert info is None


class TestFormulaCalculator:
    """Test formula-based calculator creation."""
    
    def test_simple_formula(self):
        """Test creating a simple formula calculator."""
        formula = "deps['a'] + deps['b']"
        calc_func = create_formula_calculator(formula)
        
        result = calc_func({"a": 5, "b": 3})
        
        assert result == 8
    
    def test_complex_formula(self):
        """Test creating a complex formula calculator."""
        formula = "(deps['x'] * 2) + deps['y'] - 1"
        calc_func = create_formula_calculator(formula)
        
        result = calc_func({"x": 4, "y": 3})
        
        # (4 * 2) + 3 - 1 = 8 + 3 - 1 = 10
        assert result == 10
    
    def test_formula_with_functions(self):
        """Test formula with built-in functions."""
        formula = "max(deps['a'], deps['b']) + min(deps['c'], deps['d'])"
        calc_func = create_formula_calculator(formula)
        
        result = calc_func({"a": 10, "b": 5, "c": 3, "d": 7})
        
        # max(10, 5) + min(3, 7) = 10 + 3 = 13
        assert result == 13
    
    def test_formula_with_error(self):
        """Test formula that causes an error."""
        formula = "deps['nonexistent'] * 2"
        calc_func = create_formula_calculator(formula)
        
        result = calc_func({"a": 5})
        
        # Should return None on error
        assert result is None


class TestBuiltInRules:
    """Test built-in rules functionality."""
    
    def test_population_total_rule(self, calculator):
        """Test the built-in population total rule."""
        # Mock world state to return population values
        def mock_get_state_variable(key):
            values = {
                "world.population.humans": Mock(value=1000),
                "world.population.elves": Mock(value=500),
                "world.population.dwarves": Mock(value=300),
                "world.population.orcs": Mock(value=200)
            }
            return values.get(key)
        
        calculator.world_state.get_state_variable.side_effect = mock_get_state_variable
        
        calculator.initialize()
        
        total = calculator.get_derived_value("world.population.total")
        
        # Should be 1000 + 500 + 300 + 200 = 2000
        assert total == 2000
    
    def test_population_total_rule_with_missing_values(self, calculator):
        """Test population total rule with some missing values."""
        def mock_get_state_variable(key):
            values = {
                "world.population.humans": Mock(value=1000),
                "world.population.elves": Mock(value=500),
                # dwarves and orcs missing
            }
            return values.get(key)
        
        calculator.world_state.get_state_variable.side_effect = mock_get_state_variable
        
        calculator.initialize()
        
        total = calculator.get_derived_value("world.population.total")
        
        # Should be 1000 + 500 + 0 + 0 = 1500
        assert total == 1500


# Run the tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])

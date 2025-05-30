from typing import Any
"""
Tests for backend.systems.world_state.main

Comprehensive tests for the WorldStateSystem class and its initialization functions.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

# Import the module being tested
try:
    from backend.systems.world_state.main import WorldStateSystem, initialize_world_state_system
    from backend.systems.world_state.consolidated_manager import WorldStateManager
    from backend.systems.world_state.consolidated_state_models import StateCategory, WorldRegion
except ImportError as e:
    pytest.skip(f"Could not import required modules: {e}", allow_module_level=True)


@pytest.fixture
def reset_singletons():
    """Reset all singleton instances before each test."""
    # Store original instances
    original_world_state_manager = WorldStateManager._instance
    original_world_state_system = WorldStateSystem._instance
    
    # Clear instances
    WorldStateManager._instance = None
    WorldStateSystem._instance = None
    
    yield
    
    # Restore original instances
    WorldStateManager._instance = original_world_state_manager
    WorldStateSystem._instance = original_world_state_system


class TestWorldStateSystemSingleton:
    """Test singleton behavior of WorldStateSystem."""
    
    def test_singleton_instance(self, reset_singletons):
        """Test that get_instance returns the same instance."""
        system1 = WorldStateSystem.get_instance()
        system2 = WorldStateSystem.get_instance()
        
        assert system1 is system2
    
    def test_init_raises_error_if_instance_exists(self, reset_singletons):
        """Test that creating a new instance raises an error if one already exists."""
        # Create first instance
        system1 = WorldStateSystem.get_instance()
        
        # Try to create second instance directly
        with pytest.raises(RuntimeError):
            WorldStateSystem()


class TestWorldStateSystemInitialization:
    """Test initialization and dependency setup."""
    
    @patch('backend.systems.world_state.main.WorldStateManager.get_instance')
    @patch('backend.systems.world_state.main.WorldStateEventIntegration.get_instance')
    @patch('backend.systems.world_state.main.DerivativeStateCalculator.get_instance')
    def test_init_components(self, mock_derivative, mock_event, mock_manager, reset_singletons):
        """Test that all components are properly initialized."""
        # Create mock instances
        mock_manager_instance = Mock()
        mock_event_instance = Mock()
        mock_derivative_instance = Mock()
        
        mock_manager.return_value = mock_manager_instance
        mock_event.return_value = mock_event_instance
        mock_derivative.return_value = mock_derivative_instance
        
        # Create system
        system = WorldStateSystem.get_instance()
        
        # Verify components are set
        assert system.manager is mock_manager_instance
        assert system.event_integration is mock_event_instance
        assert system.derivative_calculator is mock_derivative_instance
        assert system.initialized is False
    
    @patch('backend.systems.world_state.main.WorldStateManager.get_instance')
    @patch('backend.systems.world_state.main.WorldStateEventIntegration.get_instance')
    @patch('backend.systems.world_state.main.DerivativeStateCalculator.get_instance')
    @patch('backend.systems.world_state.main.logger')
    def test_initialize_without_app(self, mock_logger, mock_derivative, mock_event, mock_manager, reset_singletons):
        """Test initialization without FastAPI app."""
        # Create mock instances
        mock_manager_instance = Mock()
        mock_event_instance = Mock()
        mock_derivative_instance = Mock()
        
        mock_manager.return_value = mock_manager_instance
        mock_event.return_value = mock_event_instance
        mock_derivative.return_value = mock_derivative_instance
        
        # Configure manager to raise exception on get_world_state (no existing state)
        mock_manager_instance.get_world_state.side_effect = Exception("No existing state")
        
        # Create and initialize system
        system = WorldStateSystem.get_instance()
        system.initialize()
        
        # Verify initialization
        assert system.initialized is True
        mock_event_instance.initialize.assert_called_once()
        mock_derivative_instance.initialize.assert_called_once()
        mock_manager_instance.get_world_state.assert_called_once()
        
        # Verify logging
        mock_logger.info.assert_any_call("Initializing World State System")
        mock_logger.info.assert_any_call("World State System initialized successfully")
    
    @patch('backend.systems.world_state.main.WorldStateManager.get_instance')
    @patch('backend.systems.world_state.main.WorldStateEventIntegration.get_instance')
    @patch('backend.systems.world_state.main.DerivativeStateCalculator.get_instance')
    @patch('backend.systems.world_state.main.logger')
    def test_initialize_with_app(self, mock_logger, mock_derivative, mock_event, mock_manager, reset_singletons):
        """Test initialization with FastAPI app."""
        # Create mock instances
        mock_manager_instance = Mock()
        mock_event_instance = Mock()
        mock_derivative_instance = Mock()
        mock_app = Mock()
        
        mock_manager.return_value = mock_manager_instance
        mock_event.return_value = mock_event_instance
        mock_derivative.return_value = mock_derivative_instance
        
        # Configure manager to not raise exception (existing state)
        mock_manager_instance.get_world_state.return_value = {"test": "state"}
        
        # Create and initialize system
        system = WorldStateSystem.get_instance()
        system.initialize(app=mock_app)
        
        # Verify app router was included
        mock_app.include_router.assert_called_once()
        mock_logger.info.assert_any_call("World State API routes registered")
        
        assert system.initialized is True
    
    @patch('backend.systems.world_state.main.WorldStateManager.get_instance')
    @patch('backend.systems.world_state.main.WorldStateEventIntegration.get_instance')
    @patch('backend.systems.world_state.main.DerivativeStateCalculator.get_instance')
    @patch('backend.systems.world_state.main.logger')
    def test_initialize_already_initialized(self, mock_logger, mock_derivative, mock_event, mock_manager, reset_singletons):
        """Test that re-initializing logs a warning and returns early."""
        # Create mock instances
        mock_manager_instance = Mock()
        mock_event_instance = Mock()
        mock_derivative_instance = Mock()
        
        mock_manager.return_value = mock_manager_instance
        mock_event.return_value = mock_event_instance
        mock_derivative.return_value = mock_derivative_instance
        
        # Create and initialize system
        system = WorldStateSystem.get_instance()
        system.initialize()
        
        # Reset mocks
        mock_event_instance.reset_mock()
        mock_derivative_instance.reset_mock()
        mock_logger.reset_mock()
        
        # Try to initialize again
        system.initialize()
        
        # Verify warning and no re-initialization
        mock_logger.warning.assert_called_once_with("World State System already initialized")
        mock_event_instance.initialize.assert_not_called()
        mock_derivative_instance.initialize.assert_not_called()
    
    @patch('backend.systems.world_state.main.WorldStateManager.get_instance')
    @patch('backend.systems.world_state.main.WorldStateEventIntegration.get_instance')
    @patch('backend.systems.world_state.main.DerivativeStateCalculator.get_instance')
    def test_initialize_with_config(self, mock_derivative, mock_event, mock_manager, reset_singletons):
        """Test initialization with custom config."""
        # Create mock instances
        mock_manager_instance = Mock()
        mock_event_instance = Mock()
        mock_derivative_instance = Mock()
        
        mock_manager.return_value = mock_manager_instance
        mock_event.return_value = mock_event_instance
        mock_derivative.return_value = mock_derivative_instance
        
        # Configure manager to raise exception on get_world_state
        mock_manager_instance.get_world_state.side_effect = Exception("No existing state")
        
        # Create and initialize system with config
        system = WorldStateSystem.get_instance()
        config = {"test_setting": "test_value"}
        system.initialize(config=config)
        
        # Verify initialization completed
        assert system.initialized is True


class TestWorldStateSystemShutdown:
    """Test shutdown functionality."""
    
    @patch('backend.systems.world_state.main.WorldStateManager.get_instance')
    @patch('backend.systems.world_state.main.WorldStateEventIntegration.get_instance')
    @patch('backend.systems.world_state.main.DerivativeStateCalculator.get_instance')
    @patch('backend.systems.world_state.main.logger')
    def test_shutdown_initialized_system(self, mock_logger, mock_derivative, mock_event, mock_manager, reset_singletons):
        """Test shutting down an initialized system."""
        # Create mock instances
        mock_manager_instance = Mock()
        mock_event_instance = Mock()
        mock_derivative_instance = Mock()
        
        mock_manager.return_value = mock_manager_instance
        mock_event.return_value = mock_event_instance
        mock_derivative.return_value = mock_derivative_instance
        
        # Create and initialize system
        system = WorldStateSystem.get_instance()
        system.initialize()
        
        # Shutdown system
        system.shutdown()
        
        # Verify shutdown
        assert system.initialized is False
        mock_manager_instance.save_world_state.assert_called_once()
        mock_logger.info.assert_any_call("Shutting down World State System")
        mock_logger.info.assert_any_call("World State System shutdown complete")
    
    @patch('backend.systems.world_state.main.WorldStateManager.get_instance')
    @patch('backend.systems.world_state.main.WorldStateEventIntegration.get_instance')
    @patch('backend.systems.world_state.main.DerivativeStateCalculator.get_instance')
    @patch('backend.systems.world_state.main.logger')
    def test_shutdown_with_save_error(self, mock_logger, mock_derivative, mock_event, mock_manager, reset_singletons):
        """Test shutdown when save fails."""
        # Create mock instances
        mock_manager_instance = Mock()
        mock_event_instance = Mock()
        mock_derivative_instance = Mock()
        
        mock_manager.return_value = mock_manager_instance
        mock_event.return_value = mock_event_instance
        mock_derivative.return_value = mock_derivative_instance
        
        # Configure save to fail
        mock_manager_instance.save_world_state.side_effect = Exception("Save failed")
        
        # Create and initialize system
        system = WorldStateSystem.get_instance()
        system.initialize()
        
        # Shutdown system
        system.shutdown()
        
        # Verify shutdown completed despite error
        assert system.initialized is False
        mock_logger.warning.assert_called_once()
        assert "Could not save world state during shutdown" in str(mock_logger.warning.call_args)
    
    @patch('backend.systems.world_state.main.WorldStateManager.get_instance')
    @patch('backend.systems.world_state.main.WorldStateEventIntegration.get_instance')
    @patch('backend.systems.world_state.main.DerivativeStateCalculator.get_instance')
    def test_shutdown_uninitialized_system(self, mock_derivative, mock_event, mock_manager, reset_singletons):
        """Test shutting down an uninitialized system."""
        # Create mock instances
        mock_manager_instance = Mock()
        mock_event_instance = Mock()
        mock_derivative_instance = Mock()
        
        mock_manager.return_value = mock_manager_instance
        mock_event.return_value = mock_event_instance
        mock_derivative.return_value = mock_derivative_instance
        
        # Create system but don't initialize
        system = WorldStateSystem.get_instance()
        
        # Shutdown system (should return early)
        system.shutdown()
        
        # Verify no save attempt
        mock_manager_instance.save_world_state.assert_not_called()


class TestWorldStateSystemAPIWrapper:
    """Test API wrapper methods."""
    
    @patch('backend.systems.world_state.main.WorldStateManager.get_instance')
    @patch('backend.systems.world_state.main.WorldStateEventIntegration.get_instance')
    @patch('backend.systems.world_state.main.DerivativeStateCalculator.get_instance')
    def test_set_state(self, mock_derivative, mock_event, mock_manager, reset_singletons):
        """Test set_state wrapper method."""
        # Create mock instances
        mock_manager_instance = Mock()
        mock_event_instance = Mock()
        mock_derivative_instance = Mock()
        
        mock_manager.return_value = mock_manager_instance
        mock_event.return_value = mock_event_instance
        mock_derivative.return_value = mock_derivative_instance
        
        # Configure manager response
        mock_state_var = Mock()
        mock_manager_instance.set_state.return_value = mock_state_var
        
        # Create system and call method
        system = WorldStateSystem.get_instance()
        result = system.set_state("test.key", "test_value", category=StateCategory.POLITICAL)
        
        # Verify call was forwarded
        mock_manager_instance.set_state.assert_called_once_with(
            "test.key", "test_value", category=StateCategory.POLITICAL
        )
        assert result is mock_state_var
    
    @patch('backend.systems.world_state.main.WorldStateManager.get_instance')
    @patch('backend.systems.world_state.main.WorldStateEventIntegration.get_instance')
    @patch('backend.systems.world_state.main.DerivativeStateCalculator.get_instance')
    def test_get_state_exists(self, mock_derivative, mock_event, mock_manager, reset_singletons):
        """Test get_state wrapper method when state exists."""
        # Create mock instances
        mock_manager_instance = Mock()
        mock_event_instance = Mock()
        mock_derivative_instance = Mock()
        
        mock_manager.return_value = mock_manager_instance
        mock_event.return_value = mock_event_instance
        mock_derivative.return_value = mock_derivative_instance
        
        # Configure manager response
        mock_state_var = Mock()
        mock_state_var.value = "test_value"
        mock_manager_instance.get_state_variable.return_value = mock_state_var
        
        # Create system and call method
        system = WorldStateSystem.get_instance()
        result = system.get_state("test.key")
        
        # Verify call was forwarded and value returned
        mock_manager_instance.get_state_variable.assert_called_once_with("test.key")
        assert result == "test_value"
    
    @patch('backend.systems.world_state.main.WorldStateManager.get_instance')
    @patch('backend.systems.world_state.main.WorldStateEventIntegration.get_instance')
    @patch('backend.systems.world_state.main.DerivativeStateCalculator.get_instance')
    def test_get_state_not_exists(self, mock_derivative, mock_event, mock_manager, reset_singletons):
        """Test get_state wrapper method when state doesn't exist."""
        # Create mock instances
        mock_manager_instance = Mock()
        mock_event_instance = Mock()
        mock_derivative_instance = Mock()
        
        mock_manager.return_value = mock_manager_instance
        mock_event.return_value = mock_event_instance
        mock_derivative.return_value = mock_derivative_instance
        
        # Configure manager response (no state variable)
        mock_manager_instance.get_state_variable.return_value = None
        
        # Create system and call method
        system = WorldStateSystem.get_instance()
        result = system.get_state("nonexistent.key")
        
        # Verify None returned
        assert result is None
    
    @patch('backend.systems.world_state.main.WorldStateManager.get_instance')
    @patch('backend.systems.world_state.main.WorldStateEventIntegration.get_instance')
    @patch('backend.systems.world_state.main.DerivativeStateCalculator.get_instance')
    def test_create_snapshot(self, mock_derivative, mock_event, mock_manager, reset_singletons):
        """Test create_snapshot wrapper method."""
        # Create mock instances
        mock_manager_instance = Mock()
        mock_event_instance = Mock()
        mock_derivative_instance = Mock()
        
        mock_manager.return_value = mock_manager_instance
        mock_event.return_value = mock_event_instance
        mock_derivative.return_value = mock_derivative_instance
        
        # Configure manager response
        mock_snapshot = Mock()
        mock_manager_instance.create_snapshot.return_value = mock_snapshot
        
        # Create system and call method
        system = WorldStateSystem.get_instance()
        result = system.create_snapshot("Test Snapshot", {"key": "value"})
        
        # Verify call was forwarded
        mock_manager_instance.create_snapshot.assert_called_once_with(
            "Test Snapshot", {"key": "value"}
        )
        assert result is mock_snapshot
    
    @patch('backend.systems.world_state.main.WorldStateManager.get_instance')
    @patch('backend.systems.world_state.main.WorldStateEventIntegration.get_instance')
    @patch('backend.systems.world_state.main.DerivativeStateCalculator.get_instance')
    def test_restore_snapshot(self, mock_derivative, mock_event, mock_manager, reset_singletons):
        """Test restore_snapshot wrapper method."""
        # Create mock instances
        mock_manager_instance = Mock()
        mock_event_instance = Mock()
        mock_derivative_instance = Mock()
        
        mock_manager.return_value = mock_manager_instance
        mock_event.return_value = mock_event_instance
        mock_derivative.return_value = mock_derivative_instance
        
        # Configure manager response
        mock_manager_instance.restore_snapshot.return_value = True
        
        # Create system and call method
        system = WorldStateSystem.get_instance()
        result = system.restore_snapshot("snapshot-id-123")
        
        # Verify call was forwarded
        mock_manager_instance.restore_snapshot.assert_called_once_with("snapshot-id-123")
        assert result is True
    
    @patch('backend.systems.world_state.main.WorldStateManager.get_instance')
    @patch('backend.systems.world_state.main.WorldStateEventIntegration.get_instance')
    @patch('backend.systems.world_state.main.DerivativeStateCalculator.get_instance')
    def test_get_derived_value(self, mock_derivative, mock_event, mock_manager, reset_singletons):
        """Test get_derived_value wrapper method."""
        # Create mock instances
        mock_manager_instance = Mock()
        mock_event_instance = Mock()
        mock_derivative_instance = Mock()
        
        mock_manager.return_value = mock_manager_instance
        mock_event.return_value = mock_event_instance
        mock_derivative.return_value = mock_derivative_instance
        
        # Configure derivative calculator response
        mock_derivative_instance.get_derived_value.return_value = "derived_value"
        
        # Create system and call method
        system = WorldStateSystem.get_instance()
        result = system.get_derived_value("derived.key")
        
        # Verify call was forwarded
        mock_derivative_instance.get_derived_value.assert_called_once_with("derived.key")
        assert result == "derived_value"


class TestWorldStateSystemQuery:
    """Test query functionality."""
    
    @patch('backend.systems.world_state.main.WorldStateManager.get_instance')
    @patch('backend.systems.world_state.main.WorldStateEventIntegration.get_instance')
    @patch('backend.systems.world_state.main.DerivativeStateCalculator.get_instance')
    def test_query_state_no_filters(self, mock_derivative, mock_event, mock_manager, reset_singletons):
        """Test query_state with no filters."""
        # Create mock instances
        mock_manager_instance = Mock()
        mock_event_instance = Mock()
        mock_derivative_instance = Mock()
        
        mock_manager.return_value = mock_manager_instance
        mock_event.return_value = mock_event_instance
        mock_derivative.return_value = mock_derivative_instance
        
        # Configure manager response
        all_vars = {
            "var1": Mock(category=StateCategory.POLITICAL, region=WorldRegion.NORTHERN, tags=["tag1"]),
            "var2": Mock(category=StateCategory.ECONOMIC, region=WorldRegion.SOUTHERN, tags=["tag2"])
        }
        mock_manager_instance.get_all_state_variables.return_value = all_vars
        
        # Create system and call method
        system = WorldStateSystem.get_instance()
        result = system.query_state()
        
        # Verify all variables returned
        assert result == all_vars
    
    @patch('backend.systems.world_state.main.WorldStateManager.get_instance')
    @patch('backend.systems.world_state.main.WorldStateEventIntegration.get_instance')
    @patch('backend.systems.world_state.main.DerivativeStateCalculator.get_instance')
    def test_query_state_with_prefix(self, mock_derivative, mock_event, mock_manager, reset_singletons):
        """Test query_state with prefix filter."""
        # Create mock instances
        mock_manager_instance = Mock()
        mock_event_instance = Mock()
        mock_derivative_instance = Mock()
        
        mock_manager.return_value = mock_manager_instance
        mock_event.return_value = mock_event_instance
        mock_derivative.return_value = mock_derivative_instance
        
        # Configure manager response
        all_vars = {
            "test.var1": Mock(),
            "test.var2": Mock(),
            "other.var": Mock()
        }
        mock_manager_instance.get_all_state_variables.return_value = all_vars
        
        # Create system and call method
        system = WorldStateSystem.get_instance()
        result = system.query_state(prefix="test.")
        
        # Verify only prefixed variables returned
        expected = {"test.var1": all_vars["test.var1"], "test.var2": all_vars["test.var2"]}
        assert result == expected
    
    @patch('backend.systems.world_state.main.WorldStateManager.get_instance')
    @patch('backend.systems.world_state.main.WorldStateEventIntegration.get_instance')
    @patch('backend.systems.world_state.main.DerivativeStateCalculator.get_instance')
    def test_query_state_with_category(self, mock_derivative, mock_event, mock_manager, reset_singletons):
        """Test query_state with category filter."""
        # Create mock instances
        mock_manager_instance = Mock()
        mock_event_instance = Mock()
        mock_derivative_instance = Mock()
        
        mock_manager.return_value = mock_manager_instance
        mock_event.return_value = mock_event_instance
        mock_derivative.return_value = mock_derivative_instance
        
        # Configure manager response
        all_vars = {
            "var1": Mock(category=StateCategory.POLITICAL),
            "var2": Mock(category=StateCategory.ECONOMIC),
            "var3": Mock(category=StateCategory.POLITICAL)
        }
        mock_manager_instance.get_all_state_variables.return_value = all_vars
        
        # Create system and call method
        system = WorldStateSystem.get_instance()
        result = system.query_state(category=StateCategory.POLITICAL)
        
        # Verify only political variables returned
        expected = {"var1": all_vars["var1"], "var3": all_vars["var3"]}
        assert result == expected
    
    @patch('backend.systems.world_state.main.WorldStateManager.get_instance')
    @patch('backend.systems.world_state.main.WorldStateEventIntegration.get_instance')
    @patch('backend.systems.world_state.main.DerivativeStateCalculator.get_instance')
    def test_query_state_with_region(self, mock_derivative, mock_event, mock_manager, reset_singletons):
        """Test query_state with region filter."""
        # Create mock instances
        mock_manager_instance = Mock()
        mock_event_instance = Mock()
        mock_derivative_instance = Mock()
        
        mock_manager.return_value = mock_manager_instance
        mock_event.return_value = mock_event_instance
        mock_derivative.return_value = mock_derivative_instance
        
        # Configure manager response
        all_vars = {
            "var1": Mock(region=WorldRegion.NORTHERN),
            "var2": Mock(region=WorldRegion.SOUTHERN),
            "var3": Mock(region=WorldRegion.NORTHERN)
        }
        mock_manager_instance.get_all_state_variables.return_value = all_vars
        
        # Create system and call method
        system = WorldStateSystem.get_instance()
        result = system.query_state(region=WorldRegion.NORTHERN)
        
        # Verify only northern variables returned
        expected = {"var1": all_vars["var1"], "var3": all_vars["var3"]}
        assert result == expected
    
    @patch('backend.systems.world_state.main.WorldStateManager.get_instance')
    @patch('backend.systems.world_state.main.WorldStateEventIntegration.get_instance')
    @patch('backend.systems.world_state.main.DerivativeStateCalculator.get_instance')
    def test_query_state_with_tags_all_required(self, mock_derivative, mock_event, mock_manager, reset_singletons):
        """Test query_state with tags filter (all tags required)."""
        # Create mock instances
        mock_manager_instance = Mock()
        mock_event_instance = Mock()
        mock_derivative_instance = Mock()
        
        mock_manager.return_value = mock_manager_instance
        mock_event.return_value = mock_event_instance
        mock_derivative.return_value = mock_derivative_instance
        
        # Configure manager response
        all_vars = {
            "var1": Mock(tags=["tag1", "tag2", "tag3"]),
            "var2": Mock(tags=["tag1", "tag2"]),
            "var3": Mock(tags=["tag1", "tag3"])
        }
        mock_manager_instance.get_all_state_variables.return_value = all_vars
        
        # Create system and call method
        system = WorldStateSystem.get_instance()
        result = system.query_state(tags=["tag1", "tag2"])
        
        # Verify only variables with all tags returned
        expected = {"var1": all_vars["var1"], "var2": all_vars["var2"]}
        assert result == expected
    
    @patch('backend.systems.world_state.main.WorldStateManager.get_instance')
    @patch('backend.systems.world_state.main.WorldStateEventIntegration.get_instance')
    @patch('backend.systems.world_state.main.DerivativeStateCalculator.get_instance')
    def test_query_state_with_tags_any_match(self, mock_derivative, mock_event, mock_manager, reset_singletons):
        """Test query_state with tags filter (any tag matches)."""
        # Create mock instances
        mock_manager_instance = Mock()
        mock_event_instance = Mock()
        mock_derivative_instance = Mock()
        
        mock_manager.return_value = mock_manager_instance
        mock_event.return_value = mock_event_instance
        mock_derivative.return_value = mock_derivative_instance
        
        # Configure manager response
        all_vars = {
            "var1": Mock(tags=["tag1", "tag3"]),
            "var2": Mock(tags=["tag2", "tag4"]),
            "var3": Mock(tags=["tag5"])
        }
        mock_manager_instance.get_all_state_variables.return_value = all_vars
        
        # Create system and call method
        system = WorldStateSystem.get_instance()
        result = system.query_state(tags=["tag1", "tag2"], match_any=True)
        
        # Verify variables with any matching tag returned
        expected = {"var1": all_vars["var1"], "var2": all_vars["var2"]}
        assert result == expected
    
    @patch('backend.systems.world_state.main.WorldStateManager.get_instance')
    @patch('backend.systems.world_state.main.WorldStateEventIntegration.get_instance')
    @patch('backend.systems.world_state.main.DerivativeStateCalculator.get_instance')
    def test_query_state_combined_filters(self, mock_derivative, mock_event, mock_manager, reset_singletons):
        """Test query_state with multiple filters combined."""
        # Create mock instances
        mock_manager_instance = Mock()
        mock_event_instance = Mock()
        mock_derivative_instance = Mock()
        
        mock_manager.return_value = mock_manager_instance
        mock_event.return_value = mock_event_instance
        mock_derivative.return_value = mock_derivative_instance
        
        # Configure manager response
        all_vars = {
            "test.var1": Mock(category=StateCategory.POLITICAL, region=WorldRegion.NORTHERN, tags=["tag1"]),
            "test.var2": Mock(category=StateCategory.POLITICAL, region=WorldRegion.SOUTHERN, tags=["tag1"]),
            "other.var": Mock(category=StateCategory.POLITICAL, region=WorldRegion.NORTHERN, tags=["tag1"]),
            "test.var3": Mock(category=StateCategory.ECONOMIC, region=WorldRegion.NORTHERN, tags=["tag1"])
        }
        mock_manager_instance.get_all_state_variables.return_value = all_vars
        
        # Create system and call method with multiple filters
        system = WorldStateSystem.get_instance()
        result = system.query_state(
            prefix="test.",
            category=StateCategory.POLITICAL,
            region=WorldRegion.NORTHERN,
            tags=["tag1"]
        )
        
        # Verify only variable matching all filters returned
        expected = {"test.var1": all_vars["test.var1"]}
        assert result == expected


class TestInitializeFunction:
    """Test the initialize_world_state_system function."""
    
    @patch('backend.systems.world_state.main.WorldStateSystem.get_instance')
    def test_initialize_function_without_args(self, mock_get_instance, reset_singletons):
        """Test initialize function without arguments."""
        mock_system = Mock()
        mock_get_instance.return_value = mock_system
        
        result = initialize_world_state_system()
        
        mock_get_instance.assert_called_once()
        mock_system.initialize.assert_called_once_with(None, None)
        assert result is mock_system
    
    @patch('backend.systems.world_state.main.WorldStateSystem.get_instance')
    def test_initialize_function_with_args(self, mock_get_instance, reset_singletons):
        """Test initialize function with arguments."""
        mock_system = Mock()
        mock_get_instance.return_value = mock_system
        mock_app = Mock()
        config = {"test": "config"}
        
        result = initialize_world_state_system(mock_app, config)
        
        mock_get_instance.assert_called_once()
        mock_system.initialize.assert_called_once_with(mock_app, config)
        assert result is mock_system


# Run the tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 
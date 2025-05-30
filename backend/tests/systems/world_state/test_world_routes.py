"""
Tests for backend.systems.world_state.world_routes

Comprehensive tests for the Flask world routes functionality.
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from flask import Flask

# Import the module being tested
try: pass
    from backend.systems.world_state.world_routes import world_bp
except ImportError as e: pass
    pytest.skip(f"Could not import backend.systems.world_state.world_routes: {e}", allow_module_level=True)


class TestWorldRoutes: pass
    """Test world routes functionality."""

    def setup_method(self): pass
        """Set up test fixtures."""
        self.app = Flask(__name__)
        self.app.register_blueprint(world_bp)
        self.client = self.app.test_client()
        self.app.config['TESTING'] = True

    @patch('backend.systems.world_state.world_routes.generate_region')
    @patch('backend.systems.world_state.world_routes.WorldStateManager')
    def test_generate_initial_world_success(self, mock_manager_class, mock_generate_region): pass
        """Test successful world generation."""
        # Mock the generate_region function
        mock_region_data = {
            "tiles": {"tile1": {}, "tile2": {}},
            "poi_list": [{"id": "poi1"}, {"id": "poi2"}]
        }
        mock_generate_region.return_value = ("test_region_123", mock_region_data)
        
        # Mock the WorldStateManager
        mock_manager = Mock()
        mock_manager_class.get_instance.return_value = mock_manager
        mock_manager.get_world_state.return_value = {"existing": "data"}
        mock_manager.update_world_state.return_value = None
        
        # Make the request
        response = self.client.post('/generate_initial_world')
        
        # Verify response
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert data["message"] == "World generated with starting region test_region_123."
        assert data["region_id"] == "test_region_123"
        assert data["tiles_created"] == 2
        assert data["poi_count"] == 2
        
        # Verify manager calls
        mock_manager.get_world_state.assert_called_once()
        mock_manager.update_world_state.assert_called_once_with({"home_region": "test_region_123"})

    @patch('backend.systems.world_state.world_routes.generate_region')
    @patch('backend.systems.world_state.world_routes.WorldStateManager')
    def test_generate_initial_world_empty_region_data(self, mock_manager_class, mock_generate_region): pass
        """Test world generation with empty region data."""
        # Mock empty region data
        mock_generate_region.return_value = ("empty_region", {})
        
        # Mock the WorldStateManager
        mock_manager = Mock()
        mock_manager_class.get_instance.return_value = mock_manager
        mock_manager.get_world_state.return_value = {}
        
        # Make the request
        response = self.client.post('/generate_initial_world')
        
        # Verify response
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert data["region_id"] == "empty_region"
        assert data["tiles_created"] == 0
        assert data["poi_count"] == 0

    @patch('backend.systems.world_state.world_routes.generate_region')
    def test_generate_initial_world_generation_error(self, mock_generate_region): pass
        """Test world generation when region generation fails."""
        # Mock generate_region to raise an exception
        mock_generate_region.side_effect = Exception("Region generation failed")
        
        # Make the request
        response = self.client.post('/generate_initial_world')
        
        # Verify error response
        assert response.status_code == 500
        data = json.loads(response.data)
        assert "error" in data
        assert "Region generation failed" in data["error"]

    @patch('backend.systems.world_state.world_routes.WorldStateManager')
    def test_generate_initial_world_manager_error(self, mock_manager_class): pass
        """Test world generation when WorldStateManager fails."""
        # Mock WorldStateManager to raise an exception
        mock_manager_class.get_instance.side_effect = Exception("Manager initialization failed")
        
        # Make the request
        response = self.client.post('/generate_initial_world')
        
        # Verify error response
        assert response.status_code == 500
        data = json.loads(response.data)
        assert "error" in data
        assert "Manager initialization failed" in data["error"]

    @patch('backend.systems.world_state.world_routes.WorldStateManager')
    def test_get_world_summary_success(self, mock_manager_class): pass
        """Test successful world summary retrieval."""
        # Mock the WorldStateManager
        mock_manager = Mock()
        mock_manager_class.get_instance.return_value = mock_manager
        
        mock_world_state = {
            "global": {"time": "day 1", "weather": "sunny"},
            "regions": {"region1": {"population": 1000}},
            "pois": {"poi1": {"type": "tavern"}}
        }
        mock_manager.get_world_state.return_value = mock_world_state
        
        # Make the request
        response = self.client.get('/world_summary')
        
        # Verify response
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert data["global_state"] == {"time": "day 1", "weather": "sunny"}
        assert data["regional_state"] == {"region1": {"population": 1000}}
        assert data["poi_state"] == {"poi1": {"type": "tavern"}}
        
        # Verify manager calls
        mock_manager.get_world_state.assert_called_once()

    @patch('backend.systems.world_state.world_routes.WorldStateManager')
    def test_get_world_summary_empty_state(self, mock_manager_class): pass
        """Test world summary with empty state."""
        # Mock the WorldStateManager with empty state
        mock_manager = Mock()
        mock_manager_class.get_instance.return_value = mock_manager
        mock_manager.get_world_state.return_value = {}
        
        # Make the request
        response = self.client.get('/world_summary')
        
        # Verify response
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert data["global_state"] == {}
        assert data["regional_state"] == {}
        assert data["poi_state"] == {}

    @patch('backend.systems.world_state.world_routes.WorldStateManager')
    def test_get_world_summary_manager_error(self, mock_manager_class): pass
        """Test world summary when manager fails."""
        # Mock WorldStateManager to raise an exception
        mock_manager_class.get_instance.side_effect = Exception("Manager error")
        
        # Make the request
        response = self.client.get('/world_summary')
        
        # Verify error response
        assert response.status_code == 500
        data = json.loads(response.data)
        assert "error" in data
        assert "Manager error" in data["error"]

    @patch('backend.systems.world_state.world_routes.WorldStateManager')
    def test_tick_world_success_default_values(self, mock_manager_class): pass
        """Test successful world tick with default values."""
        # Mock the WorldStateManager
        mock_manager = Mock()
        mock_manager_class.get_instance.return_value = mock_manager
        
        mock_updated_state = {
            "current_date": {"day": 1, "hour": 12, "minute": 1}
        }
        mock_manager.advance_world_time.return_value = mock_updated_state
        
        # Make the request with empty JSON
        response = self.client.post('/tick_world', 
                                  data=json.dumps({}),
                                  content_type='application/json')
        
        # Verify response
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert data["message"] == "World tick processed."
        assert data["current_date"] == {"day": 1, "hour": 12, "minute": 1}
        
        # Verify manager calls with default values
        mock_manager.advance_world_time.assert_called_once_with(
            days=0, hours=0, minutes=1
        )

    @patch('backend.systems.world_state.world_routes.WorldStateManager')
    def test_tick_world_success_custom_values(self, mock_manager_class): pass
        """Test successful world tick with custom values."""
        # Mock the WorldStateManager
        mock_manager = Mock()
        mock_manager_class.get_instance.return_value = mock_manager
        
        mock_updated_state = {
            "current_date": {"day": 3, "hour": 15, "minute": 30}
        }
        mock_manager.advance_world_time.return_value = mock_updated_state
        
        # Make the request with custom time values
        tick_data = {"days": 2, "hours": 3, "minutes": 30}
        response = self.client.post('/tick_world',
                                  data=json.dumps(tick_data),
                                  content_type='application/json')
        
        # Verify response
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert data["message"] == "World tick processed."
        assert data["current_date"] == {"day": 3, "hour": 15, "minute": 30}
        
        # Verify manager calls with custom values
        mock_manager.advance_world_time.assert_called_once_with(
            days=2, hours=3, minutes=30
        )

    @patch('backend.systems.world_state.world_routes.WorldStateManager')
    def test_tick_world_no_json_data(self, mock_manager_class): pass
        """Test world tick with no JSON data."""
        # Mock the WorldStateManager
        mock_manager = Mock()
        mock_manager_class.get_instance.return_value = mock_manager
        
        mock_updated_state = {"current_date": {"day": 1, "hour": 0, "minute": 1}}
        mock_manager.advance_world_time.return_value = mock_updated_state
        
        # Make the request without JSON data
        response = self.client.post('/tick_world')
        
        # Verify response (should use default values)
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert data["message"] == "World tick processed."
        
        # Verify manager calls with default values
        mock_manager.advance_world_time.assert_called_once_with(
            days=0, hours=0, minutes=1
        )

    @patch('backend.systems.world_state.world_routes.WorldStateManager')
    def test_tick_world_manager_error(self, mock_manager_class): pass
        """Test world tick when manager fails."""
        # Mock WorldStateManager to raise an exception
        mock_manager_class.get_instance.side_effect = Exception("Tick processing failed")
        
        # Make the request
        response = self.client.post('/tick_world',
                                  data=json.dumps({"days": 1}),
                                  content_type='application/json')
        
        # Verify error response
        assert response.status_code == 500
        data = json.loads(response.data)
        assert "error" in data
        assert "Tick processing failed" in data["error"]

    @patch('backend.systems.world_state.world_routes.WorldStateManager')
    def test_get_global_state_success(self, mock_manager_class): pass
        """Test successful global state retrieval."""
        # Mock the WorldStateManager
        mock_manager = Mock()
        mock_manager_class.get_instance.return_value = mock_manager
        
        mock_world_state = {
            "global": {"time": "day 5", "weather": "rainy", "events": []},
            "regions": {"region1": {}},  # Should be ignored
            "pois": {"poi1": {}}  # Should be ignored
        }
        mock_manager.get_world_state.return_value = mock_world_state
        
        # Make the request
        response = self.client.get('/global_state')
        
        # Verify response
        assert response.status_code == 200
        data = json.loads(response.data)
        
        # Should only return global state
        assert data == {"time": "day 5", "weather": "rainy", "events": []}
        
        # Verify manager calls
        mock_manager.get_world_state.assert_called_once()

    @patch('backend.systems.world_state.world_routes.WorldStateManager')
    def test_get_global_state_empty(self, mock_manager_class): pass
        """Test global state retrieval when global state is empty."""
        # Mock the WorldStateManager
        mock_manager = Mock()
        mock_manager_class.get_instance.return_value = mock_manager
        mock_manager.get_world_state.return_value = {"regions": {}, "pois": {}}
        
        # Make the request
        response = self.client.get('/global_state')
        
        # Verify response
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data == {}

    @patch('backend.systems.world_state.world_routes.WorldStateManager')
    def test_get_global_state_manager_error(self, mock_manager_class): pass
        """Test global state retrieval when manager fails."""
        # Mock WorldStateManager to raise an exception
        mock_manager_class.get_instance.side_effect = Exception("Global state access failed")
        
        # Make the request
        response = self.client.get('/global_state')
        
        # Verify error response
        assert response.status_code == 500
        data = json.loads(response.data)
        assert "error" in data
        assert "Global state access failed" in data["error"]

    @patch('backend.systems.world_state.world_routes.WorldStateManager')
    def test_update_global_state_success(self, mock_manager_class): pass
        """Test successful global state update."""
        # Mock the WorldStateManager
        mock_manager = Mock()
        mock_manager_class.get_instance.return_value = mock_manager
        mock_manager.update_world_state.return_value = None
        
        # Prepare update data
        update_data = {"time": "day 10", "weather": "stormy"}
        
        # Make the request
        response = self.client.post('/global_state/update',
                                  data=json.dumps(update_data),
                                  content_type='application/json')
        
        # Verify response
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["message"] == "Global state updated successfully."
        
        # Verify manager calls
        mock_manager.update_world_state.assert_called_once_with({
            "global": {"time": "day 10", "weather": "stormy"}
        })

    @patch('backend.systems.world_state.world_routes.WorldStateManager')
    def test_update_global_state_empty_data(self, mock_manager_class): pass
        """Test global state update with empty data."""
        # Mock the WorldStateManager
        mock_manager = Mock()
        mock_manager_class.get_instance.return_value = mock_manager
        mock_manager.update_world_state.return_value = None
        
        # Make the request with empty data
        response = self.client.post('/global_state/update',
                                  data=json.dumps({}),
                                  content_type='application/json')
        
        # Verify response
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["message"] == "Global state updated successfully."
        
        # Verify manager calls
        mock_manager.update_world_state.assert_called_once_with({"global": {}})

    @patch('backend.systems.world_state.world_routes.WorldStateManager')
    def test_update_global_state_manager_error(self, mock_manager_class): pass
        """Test global state update when manager fails."""
        # Mock WorldStateManager to raise an exception
        mock_manager_class.get_instance.side_effect = Exception("Update failed")
        
        # Make the request
        response = self.client.post('/global_state/update',
                                  data=json.dumps({"test": "data"}),
                                  content_type='application/json')
        
        # Verify error response
        assert response.status_code == 500
        data = json.loads(response.data)
        assert "error" in data
        assert "Update failed" in data["error"]

    def test_update_global_state_invalid_json(self): pass
        """Test global state update with invalid JSON."""
        # Make the request with invalid JSON
        response = self.client.post('/global_state/update',
                                  data='invalid json',
                                  content_type='application/json')
        
        # Verify error response
        assert response.status_code == 500
        data = json.loads(response.data)
        assert "error" in data


class TestWorldRoutesIntegration: pass
    """Test integration scenarios for world routes."""

    def setup_method(self): pass
        """Set up test fixtures."""
        self.app = Flask(__name__)
        self.app.register_blueprint(world_bp)
        self.client = self.app.test_client()
        self.app.config['TESTING'] = True

    @patch('backend.systems.world_state.world_routes.generate_region')
    @patch('backend.systems.world_state.world_routes.WorldStateManager')
    def test_full_world_workflow(self, mock_manager_class, mock_generate_region): pass
        """Test a complete workflow: generate world, get summary, tick, update."""
        # Mock the generate_region function
        mock_region_data = {"tiles": {"tile1": {}}, "poi_list": [{"id": "poi1"}]}
        mock_generate_region.return_value = ("test_region", mock_region_data)
        
        # Mock the WorldStateManager
        mock_manager = Mock()
        mock_manager_class.get_instance.return_value = mock_manager
        
        # Step 1: Generate initial world
        mock_manager.get_world_state.return_value = {}
        response1 = self.client.post('/generate_initial_world')
        assert response1.status_code == 200
        
        # Step 2: Get world summary
        mock_manager.get_world_state.return_value = {
            "global": {"time": "day 1"},
            "regions": {"test_region": {}},
            "pois": {"poi1": {}}
        }
        response2 = self.client.get('/world_summary')
        assert response2.status_code == 200
        
        # Step 3: Tick world
        mock_manager.advance_world_time.return_value = {"current_date": {"day": 2}}
        response3 = self.client.post('/tick_world',
                                   data=json.dumps({"days": 1}),
                                   content_type='application/json')
        assert response3.status_code == 200
        
        # Step 4: Update global state
        response4 = self.client.post('/global_state/update',
                                   data=json.dumps({"weather": "sunny"}),
                                   content_type='application/json')
        assert response4.status_code == 200
        
        # Verify all operations succeeded
        assert all(r.status_code == 200 for r in [response1, response2, response3, response4])


def test_module_imports(): pass
    """Test that the module can be imported without errors."""
    from backend.systems.world_state.world_routes import world_bp
    assert world_bp is not None

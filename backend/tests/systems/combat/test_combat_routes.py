from typing import Type
"""
Tests for backend.systems.combat.combat_routes

Comprehensive tests for all combat API endpoints including initialization,
character management, damage/healing, effects, actions, and state management.
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
from fastapi import HTTPException

# Import the module being tested
try: pass
    from backend.systems.combat.combat_routes import router
    from backend.systems.combat.combat_class import Combat
    from backend.systems.combat.unified_effects import CombatEffect, EffectType
    from backend.systems.combat.action_system import ActionResult, ActionType
    from fastapi import FastAPI
except ImportError as e: pass
    pytest.skip(f"Could not import combat routes: {e}", allow_module_level=True)


@pytest.fixture
def app(): pass
    """Create FastAPI app with combat routes."""
    app = FastAPI()
    app.include_router(router)  # Router already has /combat prefix
    return app


@pytest.fixture
def client(app): pass
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def mock_combat(): pass
    """Create a mock combat instance."""
    combat = Mock(spec=Combat)
    combat.combat_id = "test_combat_123"
    combat.get_combat_state.return_value = {
        "combat_id": "test_combat_123",
        "status": "active",
        "characters": {
            "char1": {"hp": 100, "max_hp": 100},
            "char2": {"hp": 80, "max_hp": 100}
        }
    }
    return combat


@pytest.fixture
def mock_combat_state_manager(): pass
    """Mock the combat state manager."""
    with patch('backend.systems.combat.combat_routes.combat_state_manager') as mock: pass
        yield mock


@pytest.fixture
def mock_event_dispatcher(): pass
    """Mock the event dispatcher."""
    with patch('backend.systems.combat.combat_routes.event_dispatcher') as mock: pass
        yield mock


class TestCombatInitialization: pass
    """Test combat initialization endpoints."""

    def test_create_combat_success(self, client, mock_combat_state_manager, mock_event_dispatcher): pass
        """Test successful combat creation."""
        mock_combat = Mock()
        mock_combat.combat_id = "new_combat_123"
        mock_combat.get_combat_state.return_value = {"combat_id": "new_combat_123", "status": "pending"}
        
        mock_combat_state_manager.create_combat.return_value = mock_combat
        
        response = client.post("/combat/create", json={
            "characters": {"char1": {"hp": 100}, "char2": {"hp": 80}},
            "area_size": [20.0, 20.0]
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["combat_id"] == "new_combat_123"
        assert "combat_state" in data

    def test_create_combat_invalid_data(self, client, mock_combat_state_manager): pass
        """Test combat creation with invalid data."""
        mock_combat_state_manager.create_combat.side_effect = ValueError("Invalid characters")
        
        response = client.post("/combat/create", json={
            "characters": {},  # Empty characters
            "area_size": [20.0, 20.0]
        })
        
        assert response.status_code == 400
        assert "Invalid characters" in response.json()["detail"]

    def test_start_combat_success(self, client, mock_combat_state_manager, mock_event_dispatcher): pass
        """Test successful combat start."""
        mock_combat = Mock()
        mock_combat.start_combat.return_value = {"status": "active", "current_turn": "char1"}
        mock_combat_state_manager.get_combat.return_value = mock_combat
        
        response = client.post("/combat/start/test_combat_123")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "active"

    def test_start_combat_not_found(self, client, mock_combat_state_manager): pass
        """Test starting non-existent combat."""
        mock_combat_state_manager.get_combat.return_value = None
        
        response = client.post("/combat/start/nonexistent_combat")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]


class TestCombatFlow: pass
    """Test combat flow endpoints."""

    def test_next_turn_success(self, client, mock_combat_state_manager, mock_event_dispatcher): pass
        """Test successful turn advancement."""
        mock_combat = Mock()
        mock_combat.next_turn.return_value = {"current_turn": "char2", "round": 2}
        mock_combat_state_manager.get_combat.return_value = mock_combat
        
        response = client.post("/combat/next_turn/test_combat_123")
        
        assert response.status_code == 200
        data = response.json()
        assert data["current_turn"] == "char2"

    def test_end_combat_success(self, client, mock_combat_state_manager, mock_event_dispatcher): pass
        """Test successful combat end."""
        mock_combat = Mock()
        mock_combat.end_combat.return_value = {"status": "ended", "winner": "players"}
        mock_combat_state_manager.get_combat.return_value = mock_combat
        
        response = client.post("/combat/end/test_combat_123")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ended"

    def test_pause_combat_success(self, client, mock_combat_state_manager): pass
        """Test successful combat pause."""
        mock_combat = Mock()
        mock_combat.pause_combat.return_value = {"status": "paused"}
        mock_combat_state_manager.get_combat.return_value = mock_combat
        
        response = client.post("/combat/pause/test_combat_123")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "paused"

    def test_resume_combat_success(self, client, mock_combat_state_manager): pass
        """Test successful combat resume."""
        mock_combat = Mock()
        mock_combat.resume_combat.return_value = {"status": "active"}
        mock_combat_state_manager.get_combat.return_value = mock_combat
        
        response = client.post("/combat/resume/test_combat_123")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "active"


class TestCharacterManagement: pass
    """Test character management endpoints."""

    def test_add_character_success(self, client, mock_combat_state_manager): pass
        """Test successful character addition."""
        mock_combat = Mock()
        mock_combat.add_character.return_value = "new_char_123"
        mock_combat.get_combat_state.return_value = {"characters": {"new_char_123": {"hp": 100}}}
        mock_combat_state_manager.get_combat.return_value = mock_combat
        
        response = client.post("/combat/add_character/test_combat_123", json={
            "character_id": "new_char_123",
            "character_data": {"hp": 100, "max_hp": 100}
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["character_id"] == "new_char_123"

    def test_remove_character_success(self, client, mock_combat_state_manager): pass
        """Test successful character removal."""
        mock_combat = Mock()
        mock_combat.remove_character.return_value = True
        mock_combat.get_combat_state.return_value = {"characters": {}}
        mock_combat_state_manager.get_combat.return_value = mock_combat
        
        response = client.delete("/combat/remove_character/test_combat_123/char_to_remove")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_move_character_success(self, client, mock_combat_state_manager): pass
        """Test successful character movement."""
        mock_combat = Mock()
        mock_combat.move_character.return_value = {
            "success": True,
            "new_position": [10.0, 15.0],
            "movement_used": 5.0
        }
        mock_combat_state_manager.get_combat.return_value = mock_combat
        
        response = client.post("/combat/move_character/test_combat_123", json={
            "character_id": "char1",
            "destination": [10.0, 15.0]
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["new_position"] == [10.0, 15.0]


class TestDamageAndHealing: pass
    """Test damage and healing endpoints."""

    def test_apply_damage_success(self, client, mock_combat_state_manager, mock_event_dispatcher): pass
        """Test successful damage application."""
        mock_combat = Mock()
        mock_combat.apply_damage.return_value = {
            "success": True,
            "actual_damage": 25.0,
            "remaining_hp": 75,
            "defeated": False
        }
        mock_combat_state_manager.get_combat.return_value = mock_combat
        
        response = client.post("/combat/apply_damage/test_combat_123", json={
            "source_id": "char1",
            "target_id": "char2",
            "damage": 25.0,
            "damage_type": "physical"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["actual_damage"] == 25.0

    def test_apply_damage_invalid_character(self, client, mock_combat_state_manager): pass
        """Test damage application with invalid character."""
        mock_combat = Mock()
        mock_combat.apply_damage.side_effect = ValueError("Character not found")
        mock_combat_state_manager.get_combat.return_value = mock_combat
        
        response = client.post("/combat/apply_damage/test_combat_123", json={
            "source_id": "invalid_char",
            "target_id": "char2",
            "damage": 25.0,
            "damage_type": "physical"
        })
        
        assert response.status_code == 400
        assert "Character not found" in response.json()["detail"]

    def test_apply_healing_success(self, client, mock_combat_state_manager, mock_event_dispatcher): pass
        """Test successful healing application."""
        mock_combat = Mock()
        mock_combat.apply_healing.return_value = {
            "healing": 20.0,
            "target_hp": 100,
            "target_max_hp": 100
        }
        mock_combat_state_manager.get_combat.return_value = mock_combat
        
        response = client.post("/combat/apply_healing/test_combat_123", json={
            "source_id": "char1",
            "target_id": "char2",
            "healing": 20.0
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["healing"] == 20.0
        assert data["target_hp"] == 100


class TestEffects: pass
    """Test effect management endpoints."""

    def test_apply_effect_success(self, client, mock_combat_state_manager): pass
        """Test successful effect application."""
        mock_combat = Mock()
        mock_combat.apply_effect.return_value = {
            "success": True,
            "effect": {"id": "effect_123", "name": "Poison"},
            "combat_state": {}
        }
        mock_combat_state_manager.get_combat.return_value = mock_combat
        
        response = client.post("/combat/apply_effect/test_combat_123", json={
            "source_id": "char1",
            "target_id": "char2",
            "effect": {
                "name": "Poison",
                "effect_type": "DEBUFF",
                "duration": 3
            }
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_remove_effect_success(self, client, mock_combat_state_manager): pass
        """Test successful effect removal."""
        mock_combat = Mock()
        mock_combat.remove_effect.return_value = {
            "success": True,
            "removed_effects": 1
        }
        mock_combat_state_manager.get_combat.return_value = mock_combat
        
        response = client.delete("/combat/remove_effect/test_combat_123/char1/effect_123")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_get_character_effects_success(self, client, mock_combat_state_manager): pass
        """Test successful character effects retrieval."""
        mock_combat = Mock()
        mock_combat.get_character_effects.return_value = {
            "character_id": "char1",
            "effects": [
                {"id": "effect_123", "name": "Poison", "duration": 2}
            ]
        }
        mock_combat_state_manager.get_combat.return_value = mock_combat
        
        response = client.get("/combat/get_character_effects/test_combat_123/char1")
        
        assert response.status_code == 200
        data = response.json()
        assert data["character_id"] == "char1"
        assert len(data["effects"]) == 1


class TestActions: pass
    """Test action system endpoints."""

    def test_take_action_success(self, client, mock_combat_state_manager, mock_event_dispatcher): pass
        """Test successful action execution."""
        mock_combat = Mock()
        mock_combat.take_action.return_value = {
            "success": True,
            "action_result": {"damage": 15, "hit": True},
            "combat_state": {}
        }
        mock_combat_state_manager.get_combat.return_value = mock_combat
        
        response = client.post("/combat/take_action/test_combat_123", json={
            "character_id": "char1",
            "action": {
                "type": "attack",
                "target_id": "char2"
            }
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_get_available_actions_success(self, client, mock_combat_state_manager): pass
        """Test successful available actions retrieval."""
        mock_combat = Mock()
        mock_combat.get_available_actions.return_value = {
            "character_id": "char1",
            "actions": [
                {"type": "attack", "name": "Sword Strike"},
                {"type": "move", "name": "Move"}
            ]
        }
        mock_combat_state_manager.get_combat.return_value = mock_combat
        
        response = client.get("/combat/get_available_actions/test_combat_123/char1")
        
        assert response.status_code == 200
        data = response.json()
        assert data["character_id"] == "char1"
        assert len(data["actions"]) == 2

    def test_ready_action_success(self, client, mock_combat_state_manager): pass
        """Test successful action readying."""
        mock_combat = Mock()
        mock_combat.ready_action.return_value = {
            "success": True,
            "readied_action": {"type": "attack", "trigger": "enemy_approaches"}
        }
        mock_combat_state_manager.get_combat.return_value = mock_combat
        
        response = client.post("/combat/ready_action/test_combat_123", json={
            "character_id": "char1",
            "action": {"type": "attack", "target_id": "char2"},
            "trigger": "enemy_approaches"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


class TestStateManagement: pass
    """Test combat state management endpoints."""

    def test_get_combat_state_success(self, client, mock_combat_state_manager): pass
        """Test successful combat state retrieval."""
        mock_combat = Mock()
        mock_combat.get_combat_state.return_value = {
            "combat_id": "test_combat_123",
            "status": "active",
            "current_turn": "char1",
            "round": 3
        }
        mock_combat_state_manager.get_combat.return_value = mock_combat
        
        response = client.get("/combat/get_state/test_combat_123")
        
        assert response.status_code == 200
        data = response.json()
        assert data["combat_id"] == "test_combat_123"
        assert data["status"] == "active"

    def test_save_combat_state_success(self, client, mock_combat_state_manager): pass
        """Test successful combat state saving."""
        mock_combat = Mock()
        mock_combat.save_to_file.return_value = True
        mock_combat_state_manager.get_combat.return_value = mock_combat
        
        response = client.post("/combat/save_state/test_combat_123", json={
            "filename": "combat_save.json"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_load_combat_state_success(self, client, mock_combat_state_manager): pass
        """Test successful combat state loading."""
        mock_combat = Mock()
        mock_combat.load_from_file.return_value = True
        mock_combat.get_combat_state.return_value = {"combat_id": "loaded_combat"}
        mock_combat_state_manager.get_combat.return_value = mock_combat
        
        response = client.post("/combat/load_state/test_combat_123", json={
            "filename": "combat_save.json"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


class TestErrorHandling: pass
    """Test error handling scenarios."""

    def test_combat_not_found_error(self, client, mock_combat_state_manager): pass
        """Test error when combat is not found."""
        mock_combat_state_manager.get_combat.return_value = None
        
        response = client.get("/combat/state/nonexistent_combat")
        assert response.status_code == 404

    def test_invalid_json_error(self, client, mock_combat_state_manager): pass
        """Test error with invalid JSON data."""
        response = client.post("/combat/create", data="invalid json")
        assert response.status_code == 422  # FastAPI validation error

    def test_missing_required_fields(self, client, mock_combat_state_manager): pass
        """Test error with missing required fields."""
        response = client.post("/combat/take_action/test_combat", json={})
        assert response.status_code == 422  # Missing required fields

    def test_internal_server_error(self, client, mock_combat_state_manager): pass
        """Test internal server error handling."""
        mock_combat = Mock()
        mock_combat.get_combat_state.side_effect = Exception("Database error")
        mock_combat_state_manager.get_combat.return_value = mock_combat
        
        response = client.get("/combat/get_state/test_combat")
        
        assert response.status_code == 500

    def test_create_combat_normal_operation(self, client, mock_combat_state_manager): pass
        """Test create combat normal operation without state manager create_combat method."""
        # Remove the create_combat method to test normal operation path
        if hasattr(mock_combat_state_manager, 'create_combat'): pass
            delattr(mock_combat_state_manager, 'create_combat')
        
        with patch('backend.systems.combat.combat_routes.Combat') as mock_combat_class: pass
            mock_combat = Mock()
            mock_combat.combat_id = "normal_combat_123"
            mock_combat.get_combat_state.return_value = {"combat_id": "normal_combat_123"}
            mock_combat_class.return_value = mock_combat
            
            response = client.post("/combat/create", json={
                "characters": {"char1": {"hp": 100}},
                "area_size": [20.0, 20.0]
            })
            
            assert response.status_code == 200
            mock_combat_state_manager.add_combat.assert_called_once()

    def test_take_action_value_error(self, client, mock_combat_state_manager): pass
        """Test take action with ValueError from combat."""
        mock_combat = Mock()
        mock_combat.take_action.side_effect = ValueError("Invalid action")
        mock_combat_state_manager.get_combat.return_value = mock_combat
        
        response = client.post("/combat/take_action/test_combat", json={
            "character_id": "char1",
            "action": {"type": "invalid_action"}
        })
        
        assert response.status_code == 400
        assert "Invalid action" in response.json()["detail"]


class TestAlternativeEndpoints: pass
    """Test alternative endpoint implementations."""

    def test_get_state_alt(self, client, mock_combat_state_manager): pass
        """Test alternative get state endpoint."""
        mock_combat = Mock()
        mock_combat.get_combat_state.return_value = {"status": "active"}
        mock_combat_state_manager.get_combat.return_value = mock_combat
        
        response = client.get("/combat/get_state/test_combat")
        
        assert response.status_code == 200
        data = response.json()
        assert "combat_id" in data or "state" in data

    def test_get_available_actions_alt(self, client, mock_combat_state_manager): pass
        """Test alternative get available actions endpoint."""
        mock_combat = Mock()
        mock_combat.get_available_actions.return_value = ["attack", "defend"]
        mock_combat_state_manager.get_combat.return_value = mock_combat
        
        response = client.get("/combat/get_available_actions/test_combat/char1")
        
        assert response.status_code == 200
        data = response.json()
        assert "actions" in data

    def test_move_character_alt(self, client, mock_combat_state_manager): pass
        """Test alternative move character endpoint."""
        mock_combat = Mock()
        mock_combat.move_character.return_value = {"success": True, "new_position": [5.0, 5.0]}
        mock_combat_state_manager.get_combat.return_value = mock_combat
        
        response = client.post("/combat/move_character/test_combat", json={
            "character_id": "char1",
            "destination": [5.0, 5.0],
            "avoid_others": True
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_save_state(self, client, mock_combat_state_manager): pass
        """Test save state endpoint."""
        mock_combat = Mock()
        mock_combat_state_manager.get_combat.return_value = mock_combat
        
        response = client.post("/combat/save_state/test_combat", json={
            "filename": "test_save.json"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "message" in data

    def test_load_state(self, client, mock_combat_state_manager): pass
        """Test load state endpoint."""
        mock_combat = Mock()
        mock_combat.get_combat_state.return_value = {"status": "active"}
        mock_combat_state_manager.get_combat.return_value = mock_combat
        
        response = client.post("/combat/load_state/test_combat", json={
            "filename": "test_save.json"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "state" in data

    def test_delete_combat(self, client, mock_combat_state_manager): pass
        """Test delete combat endpoint."""
        mock_combat = Mock()
        mock_combat_state_manager.get_combat.return_value = mock_combat
        mock_combat_state_manager.remove_combat.return_value = True
        
        response = client.delete("/combat/test_combat")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "test_combat" in data["message"]

    def test_list_combats(self, client, mock_combat_state_manager): pass
        """Test list combats endpoint."""
        # Create mock combat objects with the required attributes
        mock_combat1 = Mock()
        mock_combat1.name = "Combat 1"
        mock_combat1.status = "active"
        mock_combat1.characters = {"char1": {}, "char2": {}}
        mock_combat1.current_turn = "char1"
        mock_combat1.round = 1
        
        mock_combat2 = Mock()
        mock_combat2.name = "Combat 2"
        mock_combat2.status = "paused"
        mock_combat2.characters = {"char3": {}}
        mock_combat2.current_turn = "char3"
        mock_combat2.round = 2
        
        mock_combat_state_manager.get_all_combats.return_value = {
            "combat1": mock_combat1,
            "combat2": mock_combat2
        }
        
        response = client.get("/combat/list")
        
        assert response.status_code == 200
        data = response.json()
        assert "combats" in data
        assert len(data["combats"]) == 2

    def test_get_visible_entities(self, client, mock_combat_state_manager): pass
        """Test get visible entities endpoint."""
        mock_combat = Mock()
        mock_combat.get_visible_entities.return_value = ["char2", "char3"]
        mock_combat_state_manager.get_combat.return_value = mock_combat
        
        response = client.get("/combat/visible_entities/test_combat/char1")
        
        assert response.status_code == 200
        data = response.json()
        assert "visible_entities" in data

    def test_perception_check(self, client, mock_combat_state_manager): pass
        """Test perception check endpoint."""
        mock_combat = Mock()
        mock_combat.perception_check.return_value = {"success": True, "detected": True}
        mock_combat_state_manager.get_combat.return_value = mock_combat
        
        response = client.post("/combat/perception_check/test_combat", json={
            "observer_id": "char1",
            "target_id": "char2",
            "bonus": 2.0
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


class TestEdgeCases: pass
    """Test edge cases and boundary conditions."""

    def test_create_combat_default_area_size(self, client, mock_combat_state_manager): pass
        """Test create combat with default area size."""
        mock_combat = Mock()
        mock_combat.combat_id = "default_area_combat"
        mock_combat.get_combat_state.return_value = {"combat_id": "default_area_combat"}
        mock_combat_state_manager.create_combat.return_value = mock_combat
        
        response = client.post("/combat/create", json={
            "characters": {"char1": {"hp": 100}}
            # No area_size provided - should use default [20.0, 20.0]
        })
        
        assert response.status_code == 200
        # Verify default area size was used
        mock_combat_state_manager.create_combat.assert_called_with(
            {"char1": {"hp": 100}}, [20.0, 20.0]
        )

    def test_get_combat_state_with_combat_id(self, client, mock_combat_state_manager): pass
        """Test get combat state when state already has combat_id."""
        mock_combat = Mock()
        mock_combat.get_combat_state.return_value = {
            "combat_id": "test_combat",
            "status": "active",
            "characters": {}
        }
        mock_combat_state_manager.get_combat.return_value = mock_combat
        
        response = client.get("/combat/state/test_combat")
        
        assert response.status_code == 200
        data = response.json()
        assert data["combat_id"] == "test_combat"
        assert "state" not in data  # Should return state directly, not wrapped

    def test_get_combat_state_without_combat_id(self, client, mock_combat_state_manager): pass
        """Test get combat state when state doesn't have combat_id."""
        mock_combat = Mock()
        mock_combat.get_combat_state.return_value = {
            "status": "active",
            "characters": {}
        }
        mock_combat_state_manager.get_combat.return_value = mock_combat
        
        response = client.get("/combat/state/test_combat")
        
        assert response.status_code == 200
        data = response.json()
        assert data["combat_id"] == "test_combat"
        assert "state" in data  # Should be wrapped with combat_id

    def test_take_action_with_various_action_formats(self, client, mock_combat_state_manager): pass
        """Test take action with different action format variations."""
        mock_combat = Mock()
        mock_combat.take_action.return_value = {"success": True, "narrative": "Action completed"}
        mock_combat_state_manager.get_combat.return_value = mock_combat
        
        # Test with action_id instead of type
        response = client.post("/combat/take_action/test_combat", json={
            "character_id": "char1",
            "action": {"action_id": "attack", "target_id": "char2", "params": {"weapon": "sword"}}
        })
        
        assert response.status_code == 200
        mock_combat.take_action.assert_called_with("char1", "attack", "char2", {"weapon": "sword"})

    def test_take_action_without_target_or_params(self, client, mock_combat_state_manager): pass
        """Test take action without target_id or params."""
        mock_combat = Mock()
        mock_combat.take_action.return_value = {"success": True}
        mock_combat_state_manager.get_combat.return_value = mock_combat
        
        response = client.post("/combat/take_action/test_combat", json={
            "character_id": "char1",
            "action": {"type": "defend"}  # No target_id or params
        })
        
        assert response.status_code == 200
        mock_combat.take_action.assert_called_with("char1", "defend", None, {})

    def test_next_turn_event_with_different_character_keys(self, client, mock_combat_state_manager, mock_event_dispatcher): pass
        """Test next turn event handling with different character key formats."""
        mock_combat = Mock()
        mock_combat.next_turn.return_value = {
            "current_character": "char2",  # Using current_character instead of current_turn
            "turn_number": 3
        }
        mock_combat_state_manager.get_combat.return_value = mock_combat
        
        response = client.post("/combat/next_turn/test_combat")
        
        assert response.status_code == 200
        # Verify event was published with correct character
        mock_event_dispatcher.publish_sync.assert_called()
        event_call = mock_event_dispatcher.publish_sync.call_args[0][0]
        assert event_call.entities_involved == ["char2"]

    def test_next_turn_event_without_character(self, client, mock_combat_state_manager, mock_event_dispatcher): pass
        """Test next turn event when no current character is specified."""
        mock_combat = Mock()
        mock_combat.next_turn.return_value = {"turn_number": 1}  # No current_character or current_turn
        mock_combat_state_manager.get_combat.return_value = mock_combat
        
        response = client.post("/combat/next_turn/test_combat")
        
        assert response.status_code == 200
        # Verify event was published with empty entities_involved
        mock_event_dispatcher.publish_sync.assert_called()
        event_call = mock_event_dispatcher.publish_sync.call_args[0][0]
        assert event_call.entities_involved == []


def test_module_imports(): pass
    """Test that the module can be imported without errors."""
    from backend.systems.combat import combat_routes
    assert combat_routes is not None

"""
Tests for world state persistence system.
"""

import pytest
from datetime import datetime
from app.core.models.world_state import WorldState, WorldStateManager
from app.core.models.version_control import VersionControl
from app.core.database import db

@pytest.fixture
def world_data():
    """Test world data."""
    return {
        "name": "Test World",
        "description": "A test game world",
        "game_time": 1440.0,  # 1 day in minutes
        "time_scale": 60.0,   # 1 minute real time = 1 hour game time
        "current_season": "summer",
        "season_progress": 0.5,
        "current_weather": "rain",
        "weather_duration": 120.0,
        "world_data": {
            "discovered_locations": ["town_1", "dungeon_1"],
            "active_quests": ["quest_1", "quest_2"],
            "global_variables": {"war_status": "peace", "plague_active": False}
        }
    }

@pytest.fixture
def test_world(world_data):
    """Create a test world state."""
    return WorldStateManager.create_world(
        name=world_data["name"],
        description=world_data["description"]
    )

class TestWorldState:
    """Test cases for WorldState model."""

    def test_create_world_state(self, world_data):
        """Test creating a new world state."""
        world = WorldState(
            name=world_data["name"],
            description=world_data["description"]
        )
        
        assert world.name == world_data["name"]
        assert world.description == world_data["description"]
        assert isinstance(world.version, VersionControl)
        assert world.version.major == 0
        assert world.version.minor == 1

    def test_world_state_to_dict(self, test_world):
        """Test converting world state to dictionary."""
        data = test_world.to_dict()
        
        assert data["name"] == test_world.name
        assert data["description"] == test_world.description
        assert isinstance(data["created_at"], str)
        assert isinstance(data["last_saved_at"], str)
        assert "version" in data
        assert data["version"]["major"] == 0
        assert data["version"]["minor"] == 1

    def test_world_state_from_dict(self, world_data):
        """Test creating world state from dictionary."""
        world = WorldState.from_dict(world_data)
        
        assert world.name == world_data["name"]
        assert world.description == world_data["description"]
        assert world.game_time == world_data["game_time"]
        assert world.current_season == world_data["current_season"]
        assert world.world_data == world_data["world_data"]

    def test_save_world_state(self, test_world):
        """Test saving world state."""
        original_time = test_world.last_saved_at
        original_version = test_world.version.minor
        
        # Make some changes
        test_world.current_weather = "storm"
        test_world.world_data["new_key"] = "new_value"
        
        # Save changes
        test_world.save()
        
        assert test_world.last_saved_at > original_time
        assert test_world.version.minor == original_version + 1
        assert test_world.current_weather == "storm"
        assert test_world.world_data["new_key"] == "new_value"

    def test_create_world_snapshot(self, test_world):
        """Test creating a world state snapshot."""
        original_major = test_world.version.major
        
        # Create snapshot
        test_world.create_snapshot("Major update")
        
        assert test_world.version.major == original_major + 1
        assert test_world.version.minor == 0
        assert test_world.version.description == "Major update"

    def test_restore_world_snapshot(self, test_world):
        """Test restoring world state from snapshot."""
        # Create a snapshot to restore to
        test_world.create_snapshot("Initial state")
        original_version_id = test_world.version.id
        
        # Make changes and create new snapshot
        test_world.current_weather = "storm"
        test_world.create_snapshot("Weather change")
        
        # Restore to original snapshot
        test_world.restore_snapshot(original_version_id)
        
        assert test_world.version.description == f"Restored from version {original_version_id}"
        assert test_world.version.major == 1  # Original major version
        assert test_world.version.minor == 0  # Reset minor version

class TestWorldStateManager:
    """Test cases for WorldStateManager."""

    def test_create_world(self, world_data):
        """Test creating a new world through manager."""
        world = WorldStateManager.create_world(
            name=world_data["name"],
            description=world_data["description"]
        )
        
        assert world.id is not None
        assert world.name == world_data["name"]
        assert world.description == world_data["description"]
        assert isinstance(world.version, VersionControl)

    def test_get_world(self, test_world):
        """Test retrieving a world by ID."""
        world = WorldStateManager.get_world(test_world.id)
        assert world.id == test_world.id
        assert world.name == test_world.name

    def test_get_nonexistent_world(self):
        """Test retrieving a non-existent world."""
        world = WorldStateManager.get_world(999)
        assert world is None

    def test_get_worlds(self, test_world):
        """Test retrieving all worlds."""
        # Create additional test worlds
        WorldStateManager.create_world("World 2")
        WorldStateManager.create_world("World 3")
        
        worlds = WorldStateManager.get_worlds()
        assert len(worlds) >= 3
        assert any(w.name == test_world.name for w in worlds)

    def test_save_world(self, test_world):
        """Test saving a world through manager."""
        original_time = test_world.last_saved_at
        
        # Make changes and save
        test_world.current_season = "winter"
        WorldStateManager.save_world(test_world.id)
        
        # Refresh from database
        updated_world = WorldStateManager.get_world(test_world.id)
        assert updated_world.last_saved_at > original_time
        assert updated_world.current_season == "winter"

    def test_create_world_snapshot(self, test_world):
        """Test creating a snapshot through manager."""
        original_major = test_world.version.major
        
        WorldStateManager.create_snapshot(
            test_world.id,
            description="Test snapshot"
        )
        
        # Refresh from database
        updated_world = WorldStateManager.get_world(test_world.id)
        assert updated_world.version.major == original_major + 1
        assert updated_world.version.description == "Test snapshot"

    def test_restore_world_snapshot(self, test_world):
        """Test restoring a snapshot through manager."""
        # Create initial snapshot
        WorldStateManager.create_snapshot(test_world.id, "Initial state")
        original_version_id = test_world.version.id
        
        # Make changes
        test_world.current_weather = "fog"
        test_world.save()
        
        # Restore snapshot
        WorldStateManager.restore_snapshot(test_world.id, original_version_id)
        
        # Refresh from database
        restored_world = WorldStateManager.get_world(test_world.id)
        assert restored_world.version.description == f"Restored from version {original_version_id}"

    def test_delete_world(self, test_world):
        """Test deleting a world."""
        world_id = test_world.id
        WorldStateManager.delete_world(world_id)
        
        deleted_world = WorldStateManager.get_world(world_id)
        assert deleted_world is None 
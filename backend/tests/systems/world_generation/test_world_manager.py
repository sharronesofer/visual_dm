from typing import List
"""
Tests for the world manager.

This module contains tests for world data persistence, loading, and retrieval.
"""

import pytest
import os
import json
from unittest.mock import patch, MagicMock

from backend.systems.world_generation.world_manager import (
    WorldManager,
    load_world_from_file,
    save_world_to_file,
    get_world_data,
    get_region_data,
    get_continent_data,
    list_available_worlds,
)


class TestWorldManager:
    """Tests for the WorldManager class."""

    def test_initialization(self, temp_data_dir):
        """Test initializing the WorldManager."""
        # Create a manager with the temp directory
        manager = WorldManager(data_dir=temp_data_dir)

        # Verify attributes
        assert manager.data_dir == temp_data_dir
        assert manager.worlds == {}
        assert manager.loaded_worlds == set()

    def test_register_world(self, temp_data_dir):
        """Test registering a world with the manager."""
        # Create a manager and a test world
        manager = WorldManager(data_dir=temp_data_dir)
        world_id = "test-world"
        world_data = {
            "id": world_id,
            "name": "Test World",
            "version": "1.0",
            "continents": {},
        }

        # Register the world
        manager.register_world(world_id, world_data)

        # Verify the world was registered
        assert world_id in manager.worlds
        assert manager.worlds[world_id] == world_data
        assert world_id in manager.loaded_worlds

    def test_unregister_world(self, temp_data_dir):
        """Test unregistering a world from the manager."""
        # Create a manager and register a test world
        manager = WorldManager(data_dir=temp_data_dir)
        world_id = "test-world"
        world_data = {"id": world_id, "name": "Test World"}

        manager.register_world(world_id, world_data)

        # Unregister the world
        manager.unregister_world(world_id)

        # Verify the world was unregistered
        assert world_id not in manager.worlds
        assert world_id not in manager.loaded_worlds

    def test_get_world(self, temp_data_dir):
        """Test getting a world from the manager."""
        # Create a manager and register a test world
        manager = WorldManager(data_dir=temp_data_dir)
        world_id = "test-world"
        world_data = {"id": world_id, "name": "Test World"}

        manager.register_world(world_id, world_data)

        # Get the world
        result = manager.get_world(world_id)

        # Verify the result
        assert result == world_data

    def test_get_nonexistent_world(self, temp_data_dir):
        """Test getting a world that doesn't exist."""
        # Create a manager
        manager = WorldManager(data_dir=temp_data_dir)

        # Try to get a nonexistent world
        result = manager.get_world("nonexistent-world")

        # Verify the result is None
        assert result is None

    def test_has_world(self, temp_data_dir):
        """Test checking if a world exists."""
        # Create a manager and register a test world
        manager = WorldManager(data_dir=temp_data_dir)
        world_id = "test-world"
        world_data = {"id": world_id, "name": "Test World"}

        manager.register_world(world_id, world_data)

        # Check if worlds exist
        assert manager.has_world(world_id) is True
        assert manager.has_world("nonexistent-world") is False

    def test_save_world(self, temp_data_dir):
        """Test saving a world to disk."""
        # Create a manager and register a test world
        manager = WorldManager(data_dir=temp_data_dir)
        world_id = "test-world"
        world_data = {
            "id": world_id,
            "name": "Test World",
            "version": "1.0",
            "continents": {
                "continent1": {
                    "id": "continent1",
                    "name": "Test Continent",
                    "regions": {"region1": {"id": "region1", "name": "Test Region"}},
                }
            },
        }

        manager.register_world(world_id, world_data)

        # Save the world
        file_path = manager.save_world(world_id)

        # Verify the file was created
        assert os.path.exists(file_path)

        # Verify the file contents
        with open(file_path, "r") as f:
            saved_data = json.load(f)
            assert saved_data == world_data

    def test_load_world(self, temp_data_dir):
        """Test loading a world from disk."""
        # Create a test world file
        world_id = "test-world"
        world_data = {"id": world_id, "name": "Test World", "version": "1.0"}

        # Save the world to a file first
        file_path = os.path.join(temp_data_dir, f"{world_id}.json")
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, "w") as f:
            json.dump(world_data, f)

        # Create a manager and load the world
        manager = WorldManager(data_dir=temp_data_dir)
        loaded_world = manager.load_world(world_id)

        # Verify the world was loaded
        assert loaded_world == world_data
        assert world_id in manager.worlds
        assert world_id in manager.loaded_worlds

    def test_load_nonexistent_world(self, temp_data_dir):
        """Test loading a world that doesn't exist."""
        # Create a manager
        manager = WorldManager(data_dir=temp_data_dir)

        # Try to load a nonexistent world
        result = manager.load_world("nonexistent-world")

        # Verify the result is None
        assert result is None

    def test_list_worlds(self, temp_data_dir):
        """Test listing available worlds."""
        # Create test world files
        world_ids = ["world1", "world2", "world3"]

        for world_id in world_ids:
            file_path = os.path.join(temp_data_dir, f"{world_id}.json")
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            with open(file_path, "w") as f:
                json.dump({"id": world_id, "name": f"World {world_id}"}, f)

        # Create a manager and list worlds
        manager = WorldManager(data_dir=temp_data_dir)
        worlds = manager.list_worlds()

        # Verify the list contains the expected worlds
        assert len(worlds) == len(world_ids)
        for world_id in world_ids:
            assert world_id in worlds

    def test_get_continent(self, temp_data_dir):
        """Test getting a continent from a world."""
        # Create a manager and register a test world with continents
        manager = WorldManager(data_dir=temp_data_dir)
        world_id = "test-world"
        continent_id = "test-continent"
        continent_data = {"id": continent_id, "name": "Test Continent"}

        world_data = {
            "id": world_id,
            "name": "Test World",
            "continents": {continent_id: continent_data},
        }

        manager.register_world(world_id, world_data)

        # Get the continent
        result = manager.get_continent(world_id, continent_id)

        # Verify the result
        assert result == continent_data

    def test_get_nonexistent_continent(self, temp_data_dir):
        """Test getting a continent that doesn't exist."""
        # Create a manager and register a test world
        manager = WorldManager(data_dir=temp_data_dir)
        world_id = "test-world"
        world_data = {"id": world_id, "name": "Test World", "continents": {}}

        manager.register_world(world_id, world_data)

        # Try to get a nonexistent continent
        result = manager.get_continent(world_id, "nonexistent-continent")

        # Verify the result is None
        assert result is None

    def test_get_region(self, temp_data_dir):
        """Test getting a region from a continent."""
        # Create a manager and register a test world with continents and regions
        manager = WorldManager(data_dir=temp_data_dir)
        world_id = "test-world"
        continent_id = "test-continent"
        region_id = "test-region"
        region_data = {"id": region_id, "name": "Test Region"}

        world_data = {
            "id": world_id,
            "name": "Test World",
            "continents": {
                continent_id: {
                    "id": continent_id,
                    "name": "Test Continent",
                    "regions": {region_id: region_data},
                }
            },
        }

        manager.register_world(world_id, world_data)

        # Get the region
        result = manager.get_region(world_id, continent_id, region_id)

        # Verify the result
        assert result == region_data

    def test_get_nonexistent_region(self, temp_data_dir):
        """Test getting a region that doesn't exist."""
        # Create a manager and register a test world with continents
        manager = WorldManager(data_dir=temp_data_dir)
        world_id = "test-world"
        continent_id = "test-continent"

        world_data = {
            "id": world_id,
            "name": "Test World",
            "continents": {
                continent_id: {
                    "id": continent_id,
                    "name": "Test Continent",
                    "regions": {},
                }
            },
        }

        manager.register_world(world_id, world_data)

        # Try to get a nonexistent region
        result = manager.get_region(world_id, continent_id, "nonexistent-region")

        # Verify the result is None
        assert result is None


class TestWorldGenerationMethods:
    """Tests for world generation methods in WorldManager."""

    @pytest.fixture
    def manager(self, temp_data_dir):
        """Create a WorldManager instance for testing."""
        return WorldManager(data_dir=temp_data_dir)

    def test_initialize_world_with_seed(self, manager):
        """Test initializing a world with a specific seed."""
        seed = 12345
        name = "Test World"
        
        result = manager.initialize_world(seed=seed, name=name)
        
        assert manager.is_initialized is True
        assert manager.last_seed == seed
        assert result["metadata"]["seed"] == seed
        assert result["metadata"]["name"] == name
        assert result["metadata"]["version"] == "1.0.0"
        assert "creation_timestamp" in result["metadata"]
        assert result["continents"] == []
        assert result["regions"] == []
        assert result["oceans"] == []
        assert result["climate_zones"] == []

    def test_initialize_world_without_seed(self, manager):
        """Test initializing a world without specifying a seed."""
        result = manager.initialize_world(name="Random World")
        
        assert manager.is_initialized is True
        assert manager.last_seed is not None
        assert result["metadata"]["seed"] is not None
        assert result["metadata"]["name"] == "Random World"

    def test_initialize_world_default_name(self, manager):
        """Test initializing a world with default name."""
        result = manager.initialize_world(seed=54321)
        
        assert result["metadata"]["name"] == "Generated World"

    @patch('backend.systems.world_generation.world_manager.ContinentService')
    @patch('backend.systems.world_generation.world_manager.RiverGenerator')
    @patch('backend.systems.world_generation.world_manager.SettlementService')
    @patch('backend.systems.world_generation.world_manager.RegionalFeatures')
    def test_initialize_world_services(self, mock_regional_features, mock_settlement_service, 
                                     mock_river_generator, mock_continent_service, manager):
        """Test that services are properly initialized."""
        manager.initialize_world(seed=12345)
        
        assert manager.continent_service is not None
        assert manager.river_generator is not None
        assert manager.settlement_service is not None
        assert manager.regional_features_service is not None

    def test_generate_world_not_initialized(self, manager):
        """Test generating a world without initialization raises error."""
        # Ensure the manager is not initialized for this test
        manager.is_initialized = False
        with pytest.raises(ValueError, match="World not initialized"):
            manager.generate_world()

    @patch('backend.systems.world_generation.world_manager.WorldManager.generate_continent')
    @patch('backend.systems.world_generation.world_manager.WorldManager._generate_world_oceans')
    @patch('backend.systems.world_generation.world_manager.WorldManager._generate_climate_zones')
    @patch('backend.systems.world_generation.world_manager.WorldManager._collect_all_regions')
    @patch('backend.systems.world_generation.world_manager.WorldManager._save_world_data')
    def test_generate_world_success(self, mock_save, mock_collect_regions, mock_climate, 
                                   mock_oceans, mock_generate_continent, manager):
        """Test successful world generation."""
        # Initialize the world first
        manager.initialize_world(seed=12345)
        
        # Mock continent generation
        mock_continent = {"id": "continent_1", "name": "Continent 1"}
        mock_generate_continent.return_value = mock_continent
        
        # Mock region collection
        mock_collect_regions.return_value = [{"id": "region_1", "name": "Region 1"}]
        
        # Generate world
        result = manager.generate_world(num_continents=2)
        
        # Verify method calls
        assert mock_generate_continent.call_count == 2
        mock_oceans.assert_called_once()
        mock_climate.assert_called_once()
        mock_collect_regions.assert_called_once()
        mock_save.assert_called_once()
        
        # Verify state
        assert manager.is_generating is False
        assert result == manager.world_data

    @patch('backend.systems.world_generation.world_manager.WorldManager._generate_regions_for_continent')
    @patch('backend.systems.world_generation.world_manager.WorldManager._generate_rivers_for_continent')
    @patch('backend.systems.world_generation.world_manager.WorldManager._generate_settlements_for_continent')
    @patch('backend.systems.world_generation.world_manager.WorldManager._generate_features_for_continent')
    @patch('backend.systems.world_generation.world_manager.generate_continent_region_coordinates')
    @patch('backend.systems.world_generation.world_manager.get_continent_boundary')
    def test_generate_continent_success(self, mock_boundary, mock_coordinates, mock_features, 
                                       mock_settlements, mock_rivers, mock_regions, manager):
        """Test successful continent generation."""
        # Initialize the world first
        manager.initialize_world(seed=12345)
        
        # Mock dependencies
        mock_coordinates.return_value = [(0, 0), (1, 1)]
        mock_boundary.return_value = {"min_x": 0, "max_x": 1, "min_y": 0, "max_y": 1}
        
        # Mock continent service
        mock_continent = {
            "id": "test_continent_123",
            "name": "Test Continent",
            "region_ids": ["region1", "region2"],
            "regions": [],
            "boundary": {"min_x": 0, "max_x": 1, "min_y": 0, "max_y": 1},
            "metadata": {"created": "2025-01-01"}
        }
        manager.continent_service = MagicMock()
        manager.continent_service.create_continent.return_value = mock_continent
        
        # Add the continent to world data so _get_continent_by_id can find it
        manager.world_data["continents"].append(mock_continent)
        
        # Generate continent
        result = manager.generate_continent(name="Test Continent", origin_x=10, origin_y=20)
        
        # Verify result structure
        assert "id" in result
        assert result["name"] == "Test Continent"
        assert "regions" in result
        assert "boundary" in result
        assert "metadata" in result

    @patch('backend.systems.world_generation.world_manager.WorldManager._generate_regions_for_continent')
    @patch('backend.systems.world_generation.world_manager.WorldManager._generate_rivers_for_continent')
    @patch('backend.systems.world_generation.world_manager.WorldManager._generate_settlements_for_continent')
    @patch('backend.systems.world_generation.world_manager.WorldManager._generate_features_for_continent')
    def test_generate_continent_default_parameters(self, mock_features, mock_settlements, mock_rivers, mock_regions, manager):
        """Test continent generation with default parameters."""
        # Initialize the world first
        manager.initialize_world(seed=12345)
        
        # Mock dependencies
        with patch('backend.systems.world_generation.world_manager.generate_continent_region_coordinates') as mock_coords, \
             patch('backend.systems.world_generation.world_manager.get_continent_boundary') as mock_boundary:
            mock_coords.return_value = [(0, 0)]
            mock_boundary.return_value = {"min_x": 0, "max_x": 1, "min_y": 0, "max_y": 1}
            
                        # Mock continent service
            mock_continent = {
                "id": "auto_continent",
                "name": "Auto Continent",
                "region_ids": ["region1"],
                "regions": [],
                "boundary": {"min_x": 0, "max_x": 1, "min_y": 0, "max_y": 1},
                "metadata": {"created": "2025-01-01"}
            }
            manager.continent_service = MagicMock()
            manager.continent_service.create_continent.return_value = mock_continent
            
            # Add the continent to world data so _get_continent_by_id can find it
            manager.world_data["continents"].append(mock_continent)
            
            # Generate continent with defaults
            result = manager.generate_continent()
            
            # Verify default name was generated
            assert result["name"] is not None
            assert len(result["name"]) > 0

    @patch('backend.systems.world_generation.world_manager.WorldManager._generate_regions_for_continent')
    @patch('backend.systems.world_generation.world_manager.WorldManager._generate_rivers_for_continent')
    @patch('backend.systems.world_generation.world_manager.WorldManager._generate_settlements_for_continent')
    @patch('backend.systems.world_generation.world_manager.WorldManager._generate_features_for_continent')
    def test_generate_continent_calls_sub_methods(self, mock_features, mock_settlements, 
                                                 mock_rivers, mock_regions, manager):
        """Test that continent generation calls all sub-generation methods."""
        # Initialize the world first
        manager.initialize_world(seed=12345)
        
        # Mock dependencies
        with patch('backend.systems.world_generation.world_manager.generate_continent_region_coordinates') as mock_coords, \
             patch('backend.systems.world_generation.world_manager.get_continent_boundary') as mock_boundary:
            mock_coords.return_value = [(0, 0)]
            mock_boundary.return_value = {"min_x": 0, "max_x": 1, "min_y": 0, "max_y": 1}
            
            # Mock continent service
            mock_continent = MagicMock()
            mock_continent.continent_id = "test_continent"
            mock_continent.name = "Test Continent"
            mock_continent.region_ids = ["region1"]
            manager.continent_service = MagicMock()
            manager.continent_service.create_new_continent.return_value = mock_continent
            
            # Generate continent
            manager.generate_continent()
            
            # Verify all sub-methods were called
            mock_regions.assert_called_once()
            mock_rivers.assert_called_once()
            mock_settlements.assert_called_once()
            mock_features.assert_called_once()

    def test_generate_regions_for_continent(self, manager):
        """Test region generation for a continent."""
        # Initialize the world first
        manager.initialize_world(seed=12345)
        
        # Add a test continent to world data
        test_continent = {
            "id": "test_continent",
            "name": "Test Continent",
            "region_coordinates": [(0, 0), (1, 1)]
        }
        manager.world_data["continents"].append(test_continent)
        
        # Mock dependencies
        manager.biome_calculator = MagicMock()
        manager.biome_calculator.calculate_biome.return_value = "forest"
        manager.continent_service = MagicMock()
        manager.continent_service.create_region.return_value = {"id": "region1", "name": "Test Region"}
        
        with patch('backend.systems.world_generation.world_manager.map_region_to_latlon') as mock_map:
            mock_map.return_value = (45.0, -90.0)
            
            # Test the method
            continent_id = "test_continent"
            manager._generate_regions_for_continent(continent_id)
            
            # Verify biome calculator was used
            manager.biome_calculator.calculate_biome.assert_called()

    def test_generate_rivers_for_continent(self, manager):
        """Test river generation for a continent."""
        # Initialize the world first
        manager.initialize_world(seed=12345)
        
        # Add test continent and regions
        test_continent = {"id": "test_continent", "name": "Test Continent"}
        manager.world_data["continents"].append(test_continent)
        manager.world_data["regions"].append({
            "id": "region1", 
            "continent_id": "test_continent",
            "name": "Test Region"
        })
        
        # Test the method (it doesn't actually call river generator in current implementation)
        continent_id = "test_continent"
        manager._generate_rivers_for_continent(continent_id)
        
        # Verify the method completed without error
        # The current implementation just prints and sets empty rivers list
        assert test_continent.get("rivers", []) == []

    def test_generate_settlements_for_continent(self, manager):
        """Test settlement generation for a continent."""
        # Initialize the world first
        manager.initialize_world(seed=12345)
        
        # Add test continent and regions
        test_continent = {"id": "test_continent", "name": "Test Continent"}
        manager.world_data["continents"].append(test_continent)
        test_region = {
            "id": "region1", 
            "continent_id": "test_continent",
            "name": "Test Region"
        }
        manager.world_data["regions"].append(test_region)
        
        # Mock settlement service
        manager.settlement_service = MagicMock()
        manager.settlement_service.generate_settlements_for_region.return_value = [{"id": "settlement1", "name": "Test Town"}]
        
        # Test the method
        continent_id = "test_continent"
        manager._generate_settlements_for_continent(continent_id)
        
        # Verify settlement service was called
        manager.settlement_service.generate_settlements_for_region.assert_called_once_with("region1")
        
        # Verify settlements were added to region
        assert "settlements" in test_region

    def test_generate_features_for_continent(self, manager):
        """Test feature generation for a continent."""
        # Initialize the world first
        manager.initialize_world(seed=12345)
        
        # Add test continent and regions
        test_continent = {"id": "test_continent", "name": "Test Continent"}
        manager.world_data["continents"].append(test_continent)
        test_region = {
            "id": "region1", 
            "continent_id": "test_continent",
            "name": "Test Region"
        }
        manager.world_data["regions"].append(test_region)
        
        # Mock regional features service
        manager.regional_features_service = MagicMock()
        manager.regional_features_service.generate_regional_features.return_value = [{"id": "feature1", "name": "Test Mountain"}]
        
        # Test the method
        continent_id = "test_continent"
        manager._generate_features_for_continent(continent_id)
        
        # Verify regional features service was called
        manager.regional_features_service.generate_regional_features.assert_called_once_with("region1")
        
        # Verify landmarks were added to region
        assert "landmarks" in test_region

    def test_generate_world_oceans(self, manager):
        """Test ocean generation."""
        # Initialize the world first
        manager.initialize_world(seed=12345)
        
        # Test the method
        manager._generate_world_oceans()
        
        # Verify oceans were added to world data
        assert "oceans" in manager.world_data
        assert isinstance(manager.world_data["oceans"], list)

    def test_generate_climate_zones(self, manager):
        """Test climate zone generation."""
        # Initialize the world first
        manager.initialize_world(seed=12345)
        
        # Test the method
        manager._generate_climate_zones()
        
        # Verify climate zones were added to world data
        assert "climate_zones" in manager.world_data
        assert isinstance(manager.world_data["climate_zones"], list)

    def test_collect_all_regions(self, manager):
        """Test collecting all regions from continents."""
        # Initialize the world first
        manager.initialize_world(seed=12345)
        
        # Add test regions directly to world_data["regions"] (this is how the method works)
        manager.world_data["regions"] = [
            {"id": "region1", "name": "Region 1"},
            {"id": "region2", "name": "Region 2"},
            {"id": "region3", "name": "Region 3"}
        ]
        
        # Test the method
        result = manager._collect_all_regions()
        
        # Verify all regions were collected
        assert len(result) == 3
        region_ids = [r["id"] for r in result]
        assert "region1" in region_ids
        assert "region2" in region_ids
        assert "region3" in region_ids

    def test_get_continent_by_id(self, manager):
        """Test getting continent by ID."""
        # Initialize the world first
        manager.initialize_world(seed=12345)
        
        # Add test continents
        test_continent = {"id": "continent1", "name": "Test Continent"}
        manager.world_data["continents"] = [test_continent]
        
        # Test the method
        result = manager._get_continent_by_id("continent1")
        
        # Verify correct continent was returned
        assert result == test_continent

    def test_get_continent_by_id_not_found(self, manager):
        """Test getting continent by ID when not found."""
        # Initialize the world first
        manager.initialize_world(seed=12345)
        
        # Test the method with non-existent ID
        result = manager._get_continent_by_id("nonexistent")
        
        # Verify None was returned
        assert result is None

    def test_save_world_data(self, manager, temp_data_dir):
        """Test saving world data to file."""
        # Initialize the world first
        manager.initialize_world(seed=12345, name="Test World")
        
        # Test the method
        manager._save_world_data()
        
        # Verify file was created in worlds subdirectory
        worlds_dir = os.path.join(temp_data_dir, "worlds")
        assert os.path.exists(worlds_dir)
        
        # Find the generated file (it uses seed and timestamp in filename)
        files = os.listdir(worlds_dir)
        assert len(files) == 1
        saved_file = os.path.join(worlds_dir, files[0])
        
        # Verify file contents
        with open(saved_file, 'r') as f:
            saved_data = json.load(f)
            assert saved_data["metadata"]["name"] == "Test World"
            assert saved_data["metadata"]["seed"] == 12345

    def test_export_world_json(self, manager, temp_data_dir):
        """Test exporting world to JSON format."""
        # Initialize the world first
        manager.initialize_world(seed=12345, name="Export Test")
        
        # Test export with full path
        export_path = os.path.join(temp_data_dir, "export_test.json")
        result_path = manager.export_world(filename=export_path, format="json")
        
        # Verify file was created
        assert os.path.exists(result_path)
        assert result_path.endswith("export_test.json")
        
        # Verify file contents
        with open(result_path, 'r') as f:
            exported_data = json.load(f)
            assert exported_data["metadata"]["name"] == "Export Test"

    @patch('backend.systems.world_generation.world_manager.WorldManager.initialize_world')
    def test_import_world(self, mock_initialize, manager, temp_data_dir):
        """Test importing world from file."""
        # Create test world file
        test_world_data = {
            "metadata": {"name": "Import Test", "seed": 54321},
            "continents": [],
            "regions": []
        }
        
        import_file = os.path.join(temp_data_dir, "import_test.json")
        with open(import_file, 'w') as f:
            json.dump(test_world_data, f)
        
        # Test import
        result = manager.import_world(import_file)
        
        # Verify world was imported
        assert result["metadata"]["name"] == "Import Test"
        assert result["metadata"]["seed"] == 54321
        assert manager.world_data == test_world_data


# Tests for module-level functions


def test_load_world_from_file(temp_data_dir):
    """Test loading a world from a file."""
    # Create a test world file
    world_id = "test-world"
    world_data = {"id": world_id, "name": "Test World", "version": "1.0"}

    file_path = os.path.join(temp_data_dir, f"{world_id}.json")
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    with open(file_path, "w") as f:
        json.dump(world_data, f)

    # Load the world
    loaded_data = load_world_from_file(file_path)

    # Verify the data
    assert loaded_data == world_data


def test_save_world_to_file(temp_data_dir):
    """Test saving a world to a file."""
    # Create test data
    world_id = "test-world"
    world_data = {"id": world_id, "name": "Test World", "version": "1.0"}

    file_path = os.path.join(temp_data_dir, f"{world_id}.json")

    # Save the world
    saved_path = save_world_to_file(world_data, file_path)

    # Verify the file was created
    assert os.path.exists(saved_path)

    # Verify the file contents
    with open(saved_path, "r") as f:
        saved_data = json.load(f)
        assert saved_data == world_data


def test_get_world_data(temp_data_dir):
    """Test getting world data using the module function."""
    # Create a world manager instance with a test world
    manager = WorldManager(data_dir=temp_data_dir)
    world_id = "test-world"
    world_data = {"id": world_id, "name": "Test World"}

    manager.register_world(world_id, world_data)

    # Patch the get_instance method to return our manager
    with patch(
        "backend.systems.world_generation.world_manager.WorldManager.get_instance",
        return_value=manager,
    ):
        # Get the world data
        result = get_world_data(world_id)

        # Verify the result
        assert result == world_data


def test_get_continent_data(temp_data_dir):
    """Test getting continent data using the module function."""
    # Create a world manager instance with a test world and continent
    manager = WorldManager(data_dir=temp_data_dir)
    world_id = "test-world"
    continent_id = "test-continent"
    continent_data = {"id": continent_id, "name": "Test Continent"}

    world_data = {
        "id": world_id,
        "name": "Test World",
        "continents": {continent_id: continent_data},
    }

    manager.register_world(world_id, world_data)

    # Patch the get_instance method to return our manager
    with patch(
        "backend.systems.world_generation.world_manager.WorldManager.get_instance",
        return_value=manager,
    ):
        # Get the continent data
        result = get_continent_data(world_id, continent_id)

        # Verify the result
        assert result == continent_data


def test_get_region_data(temp_data_dir):
    """Test getting region data using the module function."""
    # Create a world manager instance with a test world, continent, and region
    manager = WorldManager(data_dir=temp_data_dir)
    world_id = "test-world"
    continent_id = "test-continent"
    region_id = "test-region"
    region_data = {"id": region_id, "name": "Test Region"}

    world_data = {
        "id": world_id,
        "name": "Test World",
        "continents": {
            continent_id: {
                "id": continent_id,
                "name": "Test Continent",
                "regions": {region_id: region_data},
            }
        },
    }

    manager.register_world(world_id, world_data)

    # Patch the get_instance method to return our manager
    with patch(
        "backend.systems.world_generation.world_manager.WorldManager.get_instance",
        return_value=manager,
    ):
        # Get the region data
        result = get_region_data(world_id, continent_id, region_id)

        # Verify the result
        assert result == region_data


def test_list_available_worlds(temp_data_dir):
    """Test listing available worlds using the module function."""
    # Create a world manager instance with some test worlds
    manager = WorldManager(data_dir=temp_data_dir)

    # Create test world files
    world_ids = ["world1", "world2", "world3"]

    for world_id in world_ids:
        file_path = os.path.join(temp_data_dir, f"{world_id}.json")
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, "w") as f:
            json.dump({"id": world_id, "name": f"World {world_id}"}, f)

    # Patch the get_instance method to return our manager
    with patch(
        "backend.systems.world_generation.world_manager.WorldManager.get_instance",
        return_value=manager,
    ):
        # List available worlds
        worlds = list_available_worlds()

        # Verify the list contains the expected worlds
        assert len(worlds) == len(world_ids)
        for world_id in world_ids:
            assert world_id in worlds

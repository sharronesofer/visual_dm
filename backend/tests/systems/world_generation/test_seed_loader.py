from backend.systems.world_generation.enums import BiomeType
from backend.systems.world_generation.enums import BiomeType
from backend.systems.world_generation.enums import BiomeType
from backend.systems.world_generation.enums import BiomeType
from backend.systems.world_generation.enums import BiomeType
from backend.systems.world_generation.enums import BiomeType
from typing import Any
from typing import Type
from typing import List
from dataclasses import field
"""
Tests for backend.systems.world_generation.seed_loader

Tests for seed loading functionality in world generation.
"""

import pytest
from unittest.mock import Mock, patch, mock_open
import json
import os
import tempfile
import shutil
from typing import Dict, Any, List

from pydantic import ValidationError

# Import the module being tested
from backend.systems.world_generation.seed_loader import (
    load_world_seed_json,
    validate_world_seed,
    list_available_world_seeds,
    create_world_from_seed,
    load_world_seed,
    load_and_create_world,
    DEFAULT_WORLD_SEED_DIR,
)

from backend.systems.world_generation.models import (
    WorldSeed,
    WorldSettings,
    World,
    Continent,
    Region,
    BiomeType,
)





class TestLoadWorldSeedJson: pass
    """Test the load_world_seed_json function."""

    def test_load_valid_json(self): pass
        """Test loading a valid JSON file."""
        test_data = {"name": "Test World", "version": "1.0"}
        
        with patch("builtins.open", mock_open(read_data=json.dumps(test_data))): pass
            result = load_world_seed_json("test.json")
            
        assert result == test_data

    def test_load_nonexistent_file(self): pass
        """Test loading a file that doesn't exist."""
        with patch("builtins.open", side_effect=FileNotFoundError()): pass
            with pytest.raises(FileNotFoundError) as exc_info: pass
                load_world_seed_json("nonexistent.json")
            
            assert "World seed file not found" in str(exc_info.value)

    def test_load_invalid_json(self): pass
        """Test loading a file with invalid JSON."""
        invalid_json = '{"name": "Test", "invalid": }'
        
        with patch("builtins.open", mock_open(read_data=invalid_json)): pass
            with pytest.raises(json.JSONDecodeError) as exc_info: pass
                load_world_seed_json("invalid.json")
            
            assert "Invalid JSON in world seed file" in str(exc_info.value)

    def test_load_empty_file(self): pass
        """Test loading an empty file."""
        with patch("builtins.open", mock_open(read_data="")): pass
            with pytest.raises(json.JSONDecodeError): pass
                load_world_seed_json("empty.json")

    def test_load_with_encoding(self): pass
        """Test that file is loaded with UTF-8 encoding."""
        test_data = {"name": "Test World", "description": "World with unicode: ñáéíóú"}
        
        with patch("builtins.open", mock_open(read_data=json.dumps(test_data))) as mock_file: pass
            load_world_seed_json("test.json")
            
            mock_file.assert_called_once_with("test.json", "r", encoding="utf-8")


class TestValidateWorldSeed: pass
    """Test the validate_world_seed function."""

    def test_validate_valid_seed(self): pass
        """Test validating a valid world seed."""
        seed_data = {
            "name": "Test World",
            "version": "1.0",
            "metadata": {},
            "world_settings": {
                "size": "medium",
                "climate": "temperate",
                "terrain_roughness": 0.5,
                "water_coverage": 0.3,
                "temperature": 0.5,
                "precipitation": 0.5,
            },
            "regions": [],
            "continents": [],
        }
        
        result = validate_world_seed(seed_data)
        
        assert isinstance(result, WorldSeed)
        assert result.name == "Test World"
        assert result.version == "1.0"

    def test_validate_minimal_seed(self): pass
        """Test validating a minimal world seed."""
        seed_data = {
            "name": "Minimal World",
            "version": "1.0",
            "metadata": {}
        }
        
        result = validate_world_seed(seed_data)
        
        assert isinstance(result, WorldSeed)
        assert result.name == "Minimal World"

    def test_validate_invalid_seed(self): pass
        """Test validating an invalid world seed."""
        seed_data = {
            "version": "1.0",  # Missing required 'name' and 'metadata' fields
        }
        
        with pytest.raises(ValueError) as exc_info: pass
            validate_world_seed(seed_data)
        
        assert "Invalid world seed data" in str(exc_info.value)

    def test_validate_empty_seed(self): pass
        """Test validating an empty seed."""
        with pytest.raises(ValueError): pass
            validate_world_seed({})

    def test_validate_seed_with_invalid_types(self): pass
        """Test validating a seed with invalid field types."""
        seed_data = {
            "name": 123,  # Should be string
            "version": "1.0",
        }
        
        with pytest.raises(ValueError): pass
            validate_world_seed(seed_data)


class TestListAvailableWorldSeeds: pass
    """Test the list_available_world_seeds function."""

    def setup_method(self): pass
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self): pass
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)

    def test_list_seeds_in_directory(self): pass
        """Test listing seeds in a directory with valid files."""
        # Create test seed files
        seed1 = {"name": "World 1", "version": "1.0", "metadata": {"author": "Test"}}
        seed2 = {"name": "World 2", "version": "2.0"}
        
        with open(os.path.join(self.temp_dir, "world1.json"), "w") as f: pass
            json.dump(seed1, f)
        with open(os.path.join(self.temp_dir, "world2.json"), "w") as f: pass
            json.dump(seed2, f)
        
        result = list_available_world_seeds(self.temp_dir)
        
        assert len(result) == 2
        assert any(seed["name"] == "World 1" for seed in result)
        assert any(seed["name"] == "World 2" for seed in result)

    def test_list_seeds_with_invalid_files(self): pass
        """Test listing seeds with some invalid files."""
        # Create valid and invalid files
        valid_seed = {"name": "Valid World", "version": "1.0"}
        
        with open(os.path.join(self.temp_dir, "valid.json"), "w") as f: pass
            json.dump(valid_seed, f)
        with open(os.path.join(self.temp_dir, "invalid.json"), "w") as f: pass
            f.write("invalid json content")
        with open(os.path.join(self.temp_dir, "not_json.txt"), "w") as f: pass
            f.write("not a json file")
        
        result = list_available_world_seeds(self.temp_dir)
        
        assert len(result) == 1
        assert result[0]["name"] == "Valid World"

    def test_list_seeds_empty_directory(self): pass
        """Test listing seeds in an empty directory."""
        result = list_available_world_seeds(self.temp_dir)
        assert result == []

    def test_list_seeds_nonexistent_directory(self): pass
        """Test listing seeds in a nonexistent directory."""
        result = list_available_world_seeds("/nonexistent/directory")
        assert result == []

    def test_list_seeds_default_directory(self): pass
        """Test listing seeds using default directory."""
        with patch("os.path.exists", return_value=False): pass
            result = list_available_world_seeds()
            assert result == []

    def test_list_seeds_excludes_schema_files(self): pass
        """Test that schema files are excluded from listing."""
        # Create regular and schema files
        seed = {"name": "Test World", "version": "1.0"}
        schema = {"$schema": "http://json-schema.org/draft-07/schema#"}
        
        with open(os.path.join(self.temp_dir, "world.json"), "w") as f: pass
            json.dump(seed, f)
        with open(os.path.join(self.temp_dir, "world.schema.json"), "w") as f: pass
            json.dump(schema, f)
        
        result = list_available_world_seeds(self.temp_dir)
        
        assert len(result) == 1
        assert result[0]["name"] == "Test World"

    def test_list_seeds_metadata_extraction(self): pass
        """Test that metadata is correctly extracted."""
        seed = {
            "name": "Test World",
            "version": "1.0",
            "metadata": {"author": "Test Author", "description": "Test description"}
        }
        
        with open(os.path.join(self.temp_dir, "world.json"), "w") as f: pass
            json.dump(seed, f)
        
        result = list_available_world_seeds(self.temp_dir)
        
        assert len(result) == 1
        assert result[0]["metadata"]["author"] == "Test Author"

    def test_list_seeds_missing_fields(self): pass
        """Test handling of seeds with missing optional fields."""
        seed = {"name": "Minimal World"}  # Missing version and metadata
        
        with open(os.path.join(self.temp_dir, "minimal.json"), "w") as f: pass
            json.dump(seed, f)
        
        result = list_available_world_seeds(self.temp_dir)
        
        assert len(result) == 1
        assert result[0]["name"] == "Minimal World"
        assert result[0]["version"] == "Unknown"
        assert result[0]["metadata"] == {}


class TestCreateWorldFromSeed: pass
    """Test the create_world_from_seed function."""

    def test_create_world_minimal_seed(self): pass
        """Test creating world from minimal seed."""
        seed = WorldSeed(name="Test World", version="1.0", metadata={})
        
        world, continents, regions = create_world_from_seed(seed)
        
        assert isinstance(world, World)
        assert world.name == "Test World"
        assert len(continents) == 1  # Default continent created
        assert continents[0].name == "Test World Mainland"
        assert len(regions) == 0

    def test_create_world_with_settings(self): pass
        """Test creating world with custom settings."""
        settings = WorldSettings(
            seed="test-seed",
            continents=3,
            region_density=1.5,
        )
        seed = WorldSeed(
            name="Custom World",
            version="1.0",
            world_settings=settings,
            metadata={"author": "Test"}
        )
        
        world, continents, regions = create_world_from_seed(seed)
        
        assert world.name == "Custom World"
        assert world.settings.seed == "test-seed"
        assert world.settings.continents == 3
        assert world.custom_data["author"] == "Test"

    def test_create_world_with_predefined_continents(self): pass
        """Test creating world with predefined continents."""
        continents_data = [
            {
                "name": "Continent A",
                "regions": [1, 2],
                "custom_data": {"type": "mainland"}
            },
            {
                "name": "Continent B",
                "regions": [3],
                "custom_data": {"type": "island"}
            }
        ]
        
        seed = WorldSeed(
            name="Multi-Continent World",
            version="1.0",
            metadata={},
            continents=continents_data
        )
        
        world, continents, regions = create_world_from_seed(seed)
        
        assert len(continents) == 2
        assert continents[0].name == "Continent A"
        assert continents[1].name == "Continent B"
        assert continents[0].custom_data["type"] == "mainland"

    def test_create_world_with_regions(self): pass
        """Test creating world with predefined regions."""
        regions_data = [
            {
                "id": 1,
                "name": "Forest Region",
                "biome": BiomeType.FOREST,
                "custom_data": {"difficulty": "easy"}
            },
            {
                "id": 2,
                "name": "Mountain Region",
                "biome": BiomeType.MOUNTAIN,
                "custom_data": {"difficulty": "hard"}
            }
        ]
        
        seed = WorldSeed(
            name="Region World",
            version="1.0",
            metadata={},
            regions=regions_data
        )
        
        world, continents, regions = create_world_from_seed(seed)
        
        assert len(regions) == 2
        assert regions[0].name == "Forest Region"
        assert regions[0].primary_biome == BiomeType.FOREST
        assert regions[1].name == "Mountain Region"
        assert regions[1].primary_biome == BiomeType.MOUNTAIN
        
        # Regions should be assigned to the default continent
        assert len(continents) == 1
        assert len(continents[0].regions) == 2

    def test_create_world_with_continents_and_regions(self): pass
        """Test creating world with both continents and regions."""
        continents_data = [
            {"name": "Main Continent", "regions": [1, 2]},
            {"name": "Island Continent", "regions": [3]}
        ]
        regions_data = [
            {"id": 1, "name": "Region 1", "biome": BiomeType.FOREST},
            {"id": 2, "name": "Region 2", "biome": BiomeType.PLAINS},
            {"id": 3, "name": "Region 3", "biome": BiomeType.MOUNTAIN}
        ]
        
        seed = WorldSeed(
            name="Complex World",
            version="1.0",
            metadata={},
            continents=continents_data,
            regions=regions_data
        )
        
        world, continents, regions = create_world_from_seed(seed)
        
        assert len(continents) == 2
        assert len(regions) == 3
        
        # Check continent assignments
        main_continent = next(c for c in continents if c.name == "Main Continent")
        island_continent = next(c for c in continents if c.name == "Island Continent")
        
        assert len(main_continent.regions) == 2
        assert len(island_continent.regions) == 1

    def test_create_world_region_without_continent_assignment(self): pass
        """Test creating regions that aren't assigned to specific continents."""
        regions_data = [
            {"id": 1, "name": "Orphan Region", "biome": BiomeType.DESERT}
        ]
        
        seed = WorldSeed(
            name="Orphan World",
            version="1.0",
            metadata={},
            regions=regions_data
        )
        
        world, continents, regions = create_world_from_seed(seed)
        
        # Should create default continent and assign orphan region to it
        assert len(continents) == 1
        assert len(regions) == 1
        assert continents[0].regions == ["1"]  # Region IDs are stored as strings


class TestLoadWorldSeed: pass
    """Test the load_world_seed function."""

    def setup_method(self): pass
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self): pass
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)

    def test_load_seed_by_file_path(self): pass
        """Test loading seed by file path."""
        seed_data = {"name": "Test World", "version": "1.0", "metadata": {}}
        file_path = os.path.join(self.temp_dir, "test.json")
        
        with open(file_path, "w") as f: pass
            json.dump(seed_data, f)
        
        result = load_world_seed(file_path=file_path)
        
        assert isinstance(result, WorldSeed)
        assert result.name == "Test World"

    def test_load_seed_by_name(self): pass
        """Test loading seed by name from default directory."""
        seed_data = {"name": "Named World", "version": "1.0", "metadata": {}}
        
        with patch("backend.systems.world_generation.seed_loader.list_available_world_seeds") as mock_list: pass
            mock_list.return_value = [
                {
                    "filename": "named.json",
                    "path": "/fake/path/named.json",
                    "name": "Named World",
                    "version": "1.0"
                }
            ]
            
            with patch("backend.systems.world_generation.seed_loader.load_world_seed_json") as mock_load: pass
                mock_load.return_value = seed_data
                
                result = load_world_seed(name="Named World")
                
                assert isinstance(result, WorldSeed)
                assert result.name == "Named World"

    def test_load_seed_name_not_found(self): pass
        """Test loading seed with name that doesn't exist."""
        with patch("backend.systems.world_generation.seed_loader.list_available_world_seeds") as mock_list: pass
            mock_list.return_value = []
            
            with pytest.raises(FileNotFoundError) as exc_info: pass
                load_world_seed(name="Nonexistent World")
            
            assert "World seed 'Nonexistent World' not found" in str(exc_info.value)

    def test_load_seed_no_parameters(self): pass
        """Test loading seed without any parameters."""
        with pytest.raises(ValueError) as exc_info: pass
            load_world_seed()
        
        assert "Either file_path or name must be provided" in str(exc_info.value)

    def test_load_seed_both_parameters(self): pass
        """Test loading seed with both file_path and name."""
        with pytest.raises(ValueError) as exc_info: pass
            load_world_seed(file_path="test.json", name="Test World")
        
        assert "Only one of file_path or name should be provided" in str(exc_info.value)


class TestLoadAndCreateWorld: pass
    """Test the load_and_create_world function."""

    def setup_method(self): pass
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self): pass
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)

    def test_load_and_create_world_by_path(self): pass
        """Test loading and creating world by file path."""
        seed_data = {
            "name": "Complete World",
            "version": "1.0",
            "metadata": {},
            "regions": [
                {"id": 1, "name": "Test Region", "biome": BiomeType.FOREST}
            ]
        }
        file_path = os.path.join(self.temp_dir, "complete.json")
        
        with open(file_path, "w") as f: pass
            json.dump(seed_data, f)
        
        world, continents, regions = load_and_create_world(file_path=file_path)
        
        assert isinstance(world, World)
        assert world.name == "Complete World"
        assert len(continents) == 1
        assert len(regions) == 1
        assert regions[0].name == "Test Region"

    def test_load_and_create_world_by_name(self): pass
        """Test loading and creating world by name."""
        seed_data = {"name": "Named Complete World", "version": "1.0", "metadata": {}}
        
        with patch("backend.systems.world_generation.seed_loader.load_world_seed") as mock_load: pass
            mock_load.return_value = WorldSeed(**seed_data)
            
            world, continents, regions = load_and_create_world(name="Named Complete World")
            
            assert world.name == "Named Complete World"
            mock_load.assert_called_once_with(file_path=None, name="Named Complete World")


class TestEdgeCases: pass
    """Test edge cases and error handling."""

    def test_default_world_seed_dir_constant(self): pass
        """Test that DEFAULT_WORLD_SEED_DIR is properly defined."""
        assert isinstance(DEFAULT_WORLD_SEED_DIR, str)
        assert "worlds" in DEFAULT_WORLD_SEED_DIR

    def test_create_world_with_none_settings(self): pass
        """Test creating world when world_settings is None."""
        seed = WorldSeed(name="No Settings World", version="1.0", metadata={}, world_settings=None)
        
        world, continents, regions = create_world_from_seed(seed)
        
        assert isinstance(world.settings, WorldSettings)  # Should create default settings

    def test_create_world_with_empty_continents_list(self): pass
        """Test creating world with empty continents list."""
        seed = WorldSeed(
            name="Empty Continents World",
            version="1.0",
            metadata={},
            continents=[]
        )
        
        world, continents, regions = create_world_from_seed(seed)
        
        assert len(continents) == 1  # Should create default continent

    def test_region_assignment_to_nonexistent_continent(self): pass
        """Test region assignment when referenced continent doesn't exist."""
        continents_data = [
            {"name": "Continent A", "regions": [1]}
        ]
        regions_data = [
            {"id": 2, "name": "Orphan Region", "biome": BiomeType.PLAINS}  # Not in any continent
        ]
        
        seed = WorldSeed(
            name="Orphan Region World",
            version="1.0",
            metadata={},
            continents=continents_data,
            regions=regions_data
        )
        
        world, continents, regions = create_world_from_seed(seed)
        
        # Orphan region should be assigned to first continent
        assert len(regions) == 1
        # Region model doesn't have continent_id field - relationship is tracked in continent.regions


def test_module_imports(): pass
    """Test that the module imports correctly."""
    from backend.systems.world_generation.seed_loader import (
        load_world_seed_json,
        validate_world_seed,
        list_available_world_seeds,
        create_world_from_seed,
        load_world_seed,
        load_and_create_world,
    )
    
    assert load_world_seed_json is not None
    assert validate_world_seed is not None
    assert list_available_world_seeds is not None
    assert create_world_from_seed is not None
    assert load_world_seed is not None
    assert load_and_create_world is not None


def test_default_directory_path(): pass
    """Test that the default directory path is constructed correctly."""
    assert os.path.isabs(DEFAULT_WORLD_SEED_DIR)
    assert DEFAULT_WORLD_SEED_DIR.endswith(os.path.join("data", "modding", "worlds"))

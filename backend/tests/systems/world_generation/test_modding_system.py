from backend.systems.world_generation.modding_system import ModDataManager
from backend.systems.shared.database.base import Base
from backend.systems.world_generation.modding_system import ModDataManager
from backend.systems.shared.database.base import Base
from backend.systems.world_generation.modding_system import ModDataManager
from backend.systems.world_generation.modding_system import ModDataManager
from backend.systems.world_generation.modding_system import ModDataManager
from backend.systems.world_generation.modding_system import ModDataManager
"""
Comprehensive tests for the modding system module.

Tests all classes and methods in the modding system for world generation.
"""

import os
import json
import tempfile
import shutil
import uuid
from unittest.mock import patch, mock_open, MagicMock
from datetime import datetime
import pytest

from backend.systems.world_generation.modding_system import (
    ModDataManager,
    ModValidationService,
    ModSynchronizer,
    TechnicalModInterface,
    CasualModInterface,
    DEFAULT_MODDING_DIR,
    DEFAULT_WORLDS_DIR,
    DEFAULT_SCHEMAS_DIR,
    DEFAULT_ASSETS_DIR,
)


class TestModDataManager: pass
    """Test cases for ModDataManager class."""

    def setup_method(self): pass
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.modding_dir = os.path.join(self.temp_dir, "modding")
        self.worlds_dir = os.path.join(self.modding_dir, "worlds")
        self.schemas_dir = os.path.join(self.modding_dir, "schemas")
        self.assets_dir = os.path.join(self.modding_dir, "assets")

    def teardown_method(self): pass
        """Clean up test fixtures."""
        if os.path.exists(self.temp_dir): pass
            shutil.rmtree(self.temp_dir)

    def test_init_creates_directories(self): pass
        """Test that initialization creates required directories."""
        manager = ModDataManager(
            modding_dir=self.modding_dir,
            worlds_dir=self.worlds_dir,
            schemas_dir=self.schemas_dir,
            assets_dir=self.assets_dir,
        )

        assert os.path.exists(self.modding_dir)
        assert os.path.exists(self.worlds_dir)
        assert os.path.exists(self.schemas_dir)
        assert os.path.exists(self.assets_dir)
        assert manager.modding_dir == self.modding_dir
        assert manager.worlds_dir == self.worlds_dir
        assert manager.schemas_dir == self.schemas_dir
        assert manager.assets_dir == self.assets_dir

    def test_init_with_defaults(self): pass
        """Test initialization with default paths."""
        manager = ModDataManager()
        
        assert manager.modding_dir == DEFAULT_MODDING_DIR
        assert manager.worlds_dir == DEFAULT_WORLDS_DIR
        assert manager.schemas_dir == DEFAULT_SCHEMAS_DIR
        assert manager.assets_dir == DEFAULT_ASSETS_DIR

    def test_load_schemas_success(self): pass
        """Test successful schema loading."""
        # Create test schema file
        os.makedirs(self.schemas_dir, exist_ok=True)
        schema_data = {"type": "object", "properties": {"name": {"type": "string"}}}
        schema_path = os.path.join(self.schemas_dir, "test.schema.json")
        
        with open(schema_path, "w") as f: pass
            json.dump(schema_data, f)

        manager = ModDataManager(
            modding_dir=self.modding_dir,
            worlds_dir=self.worlds_dir,
            schemas_dir=self.schemas_dir,
            assets_dir=self.assets_dir,
        )

        assert "test" in manager.schemas
        assert manager.schemas["test"] == schema_data

    def test_load_schemas_error_handling(self): pass
        """Test schema loading with invalid JSON."""
        os.makedirs(self.schemas_dir, exist_ok=True)
        schema_path = os.path.join(self.schemas_dir, "invalid.schema.json")
        
        # Create invalid JSON file
        with open(schema_path, "w") as f: pass
            f.write("invalid json content")

        with patch('backend.systems.world_generation.modding_system.logger') as mock_logger: pass
            manager = ModDataManager(
                modding_dir=self.modding_dir,
                worlds_dir=self.worlds_dir,
                schemas_dir=self.schemas_dir,
                assets_dir=self.assets_dir,
            )
            
            assert "invalid" not in manager.schemas
            mock_logger.error.assert_called()

    def test_get_available_worlds_success(self): pass
        """Test getting available worlds successfully."""
        os.makedirs(self.worlds_dir, exist_ok=True)
        
        world_data = {
            "id": "test_world",
            "name": "Test World",
            "description": "A test world",
            "author": "Test Author",
            "creation_date": "2023-01-01T00:00:00",
        }
        
        world_path = os.path.join(self.worlds_dir, "test_world.json")
        with open(world_path, "w") as f: pass
            json.dump(world_data, f)

        manager = ModDataManager(
            modding_dir=self.modding_dir,
            worlds_dir=self.worlds_dir,
            schemas_dir=self.schemas_dir,
            assets_dir=self.assets_dir,
        )

        worlds = manager.get_available_worlds()
        
        assert len(worlds) == 1
        assert worlds[0]["id"] == "test_world"
        assert worlds[0]["name"] == "Test World"
        assert worlds[0]["description"] == "A test world"
        assert worlds[0]["author"] == "Test Author"
        assert worlds[0]["creation_date"] == "2023-01-01T00:00:00"
        assert worlds[0]["file_path"] == world_path

    def test_get_available_worlds_missing_fields(self): pass
        """Test getting worlds with missing metadata fields."""
        os.makedirs(self.worlds_dir, exist_ok=True)
        
        world_data = {"id": "minimal_world"}
        world_path = os.path.join(self.worlds_dir, "minimal_world.json")
        
        with open(world_path, "w") as f: pass
            json.dump(world_data, f)

        manager = ModDataManager(
            modding_dir=self.modding_dir,
            worlds_dir=self.worlds_dir,
            schemas_dir=self.schemas_dir,
            assets_dir=self.assets_dir,
        )

        worlds = manager.get_available_worlds()
        
        assert len(worlds) == 1
        assert worlds[0]["id"] == "minimal_world"
        assert worlds[0]["name"] == "Unnamed World"
        assert worlds[0]["description"] == ""
        assert worlds[0]["author"] == "Unknown"
        assert worlds[0]["creation_date"] == ""

    def test_get_available_worlds_error_handling(self): pass
        """Test error handling when loading invalid world files."""
        os.makedirs(self.worlds_dir, exist_ok=True)
        
        # Create invalid JSON file
        invalid_path = os.path.join(self.worlds_dir, "invalid.json")
        with open(invalid_path, "w") as f: pass
            f.write("invalid json")

        with patch('backend.systems.world_generation.modding_system.logger') as mock_logger: pass
            manager = ModDataManager(
                modding_dir=self.modding_dir,
                worlds_dir=self.worlds_dir,
                schemas_dir=self.schemas_dir,
                assets_dir=self.assets_dir,
            )

            worlds = manager.get_available_worlds()
            
            assert len(worlds) == 0
            mock_logger.error.assert_called()

    def test_load_world_seed_success(self): pass
        """Test successful world seed loading."""
        os.makedirs(self.worlds_dir, exist_ok=True)
        
        world_data = {"id": "test_world", "name": "Test World"}
        world_path = os.path.join(self.worlds_dir, "test_world.json")
        
        with open(world_path, "w") as f: pass
            json.dump(world_data, f)

        manager = ModDataManager(
            modding_dir=self.modding_dir,
            worlds_dir=self.worlds_dir,
            schemas_dir=self.schemas_dir,
            assets_dir=self.assets_dir,
        )

        loaded_data = manager.load_world_seed("test_world")
        
        assert loaded_data == world_data

    def test_load_world_seed_not_found(self): pass
        """Test loading non-existent world seed."""
        manager = ModDataManager(
            modding_dir=self.modding_dir,
            worlds_dir=self.worlds_dir,
            schemas_dir=self.schemas_dir,
            assets_dir=self.assets_dir,
        )

        with patch('backend.systems.world_generation.modding_system.logger') as mock_logger: pass
            result = manager.load_world_seed("nonexistent")
            
            assert result is None
            mock_logger.error.assert_called()

    def test_load_world_seed_error_handling(self): pass
        """Test error handling when loading invalid world seed."""
        os.makedirs(self.worlds_dir, exist_ok=True)
        
        # Create invalid JSON file
        world_path = os.path.join(self.worlds_dir, "invalid.json")
        with open(world_path, "w") as f: pass
            f.write("invalid json")

        manager = ModDataManager(
            modding_dir=self.modding_dir,
            worlds_dir=self.worlds_dir,
            schemas_dir=self.schemas_dir,
            assets_dir=self.assets_dir,
        )

        with patch('backend.systems.world_generation.modding_system.logger') as mock_logger: pass
            result = manager.load_world_seed("invalid")
            
            assert result is None
            mock_logger.error.assert_called()

    def test_save_world_seed_success(self): pass
        """Test successful world seed saving."""
        manager = ModDataManager(
            modding_dir=self.modding_dir,
            worlds_dir=self.worlds_dir,
            schemas_dir=self.schemas_dir,
            assets_dir=self.assets_dir,
        )

        world_data = {
            "id": "test_world",
            "name": "Test World",
            "biomes": [],
            "factions": [],
        }

        with patch.object(manager, 'validate_world_seed', return_value=True): pass
            result = manager.save_world_seed(world_data)
            
            assert result is True
            
            # Check file was created
            world_path = os.path.join(self.worlds_dir, "test_world.json")
            assert os.path.exists(world_path)
            
            # Check content
            with open(world_path, "r") as f: pass
                saved_data = json.load(f)
                assert saved_data["id"] == "test_world"
                assert saved_data["name"] == "Test World"
                assert "creation_date" in saved_data

    def test_save_world_seed_auto_generate_id(self): pass
        """Test saving world seed with auto-generated ID."""
        manager = ModDataManager(
            modding_dir=self.modding_dir,
            worlds_dir=self.worlds_dir,
            schemas_dir=self.schemas_dir,
            assets_dir=self.assets_dir,
        )

        world_data = {
            "name": "Test World",
            "biomes": [],
            "factions": [],
        }

        with patch.object(manager, 'validate_world_seed', return_value=True): pass
            result = manager.save_world_seed(world_data)
            
            assert result is True
            assert "id" in world_data
            assert "creation_date" in world_data

    def test_save_world_seed_validation_failure(self): pass
        """Test saving invalid world seed."""
        manager = ModDataManager(
            modding_dir=self.modding_dir,
            worlds_dir=self.worlds_dir,
            schemas_dir=self.schemas_dir,
            assets_dir=self.assets_dir,
        )

        world_data = {"invalid": "data"}

        with patch.object(manager, 'validate_world_seed', return_value=False): pass
            with patch('backend.systems.world_generation.modding_system.logger') as mock_logger: pass
                result = manager.save_world_seed(world_data)
                
                assert result is False
                mock_logger.error.assert_called()

    def test_save_world_seed_file_error(self): pass
        """Test error handling when saving world seed fails."""
        manager = ModDataManager(
            modding_dir=self.modding_dir,
            worlds_dir=self.worlds_dir,
            schemas_dir=self.schemas_dir,
            assets_dir=self.assets_dir,
        )

        world_data = {
            "id": "test_world",
            "name": "Test World",
            "biomes": [],
            "factions": [],
        }

        with patch.object(manager, 'validate_world_seed', return_value=True): pass
            with patch('builtins.open', side_effect=IOError("Permission denied")): pass
                with patch('backend.systems.world_generation.modding_system.logger') as mock_logger: pass
                    result = manager.save_world_seed(world_data)
                    
                    assert result is False
                    mock_logger.error.assert_called()

    def test_validate_world_seed_valid(self): pass
        """Test validation of valid world seed."""
        manager = ModDataManager(
            modding_dir=self.modding_dir,
            worlds_dir=self.worlds_dir,
            schemas_dir=self.schemas_dir,
            assets_dir=self.assets_dir,
        )

        world_data = {
            "name": "Test World",
            "biomes": [],
            "factions": [],
        }

        result = manager.validate_world_seed(world_data)
        assert result is True

    def test_validate_world_seed_missing_fields(self): pass
        """Test validation of world seed with missing required fields."""
        manager = ModDataManager(
            modding_dir=self.modding_dir,
            worlds_dir=self.worlds_dir,
            schemas_dir=self.schemas_dir,
            assets_dir=self.assets_dir,
        )

        world_data = {"name": "Test World"}  # Missing biomes and factions

        with patch('backend.systems.world_generation.modding_system.logger') as mock_logger: pass
            result = manager.validate_world_seed(world_data)
            
            assert result is False
            mock_logger.error.assert_called()


class TestModValidationService: pass
    """Test cases for ModValidationService class."""

    def setup_method(self): pass
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.schemas_dir = os.path.join(self.temp_dir, "schemas")

    def teardown_method(self): pass
        """Clean up test fixtures."""
        if os.path.exists(self.temp_dir): pass
            shutil.rmtree(self.temp_dir)

    def test_init_with_custom_dir(self): pass
        """Test initialization with custom schemas directory."""
        os.makedirs(self.schemas_dir, exist_ok=True)
        validator = ModValidationService(schemas_dir=self.schemas_dir)
        assert validator.schemas_dir == self.schemas_dir

    def test_init_with_default_dir(self): pass
        """Test initialization with default schemas directory."""
        validator = ModValidationService()
        assert validator.schemas_dir == DEFAULT_SCHEMAS_DIR

    def test_load_schemas(self): pass
        """Test schema loading."""
        os.makedirs(self.schemas_dir, exist_ok=True)
        
        schema_data = {"type": "object", "properties": {"name": {"type": "string"}}}
        schema_path = os.path.join(self.schemas_dir, "test.schema.json")
        
        with open(schema_path, "w") as f: pass
            json.dump(schema_data, f)

        validator = ModValidationService(schemas_dir=self.schemas_dir)
        
        assert "test" in validator.schemas
        assert validator.schemas["test"] == schema_data

    def test_validate_mod_success(self): pass
        """Test successful mod validation."""
        os.makedirs(self.schemas_dir, exist_ok=True)
        validator = ModValidationService(schemas_dir=self.schemas_dir)
        validator.schemas = {"test": {"type": "object"}}

        mod_data = {"name": "Test Mod"}
        is_valid, errors = validator.validate_mod(mod_data, "test")
        
        # Since we're not implementing full JSON schema validation,
        # this should return True with empty errors
        assert is_valid is True
        assert errors == []

    def test_validate_mod_schema_not_found(self): pass
        """Test validation with non-existent schema."""
        os.makedirs(self.schemas_dir, exist_ok=True)
        validator = ModValidationService(schemas_dir=self.schemas_dir)
        validator.schemas = {}

        mod_data = {"name": "Test Mod"}
        is_valid, errors = validator.validate_mod(mod_data, "nonexistent")
        
        assert is_valid is False
        assert len(errors) == 1
        assert "Schema 'nonexistent' not found" in errors[0]


class TestModSynchronizer: pass
    """Test cases for ModSynchronizer class."""

    def setup_method(self): pass
        """Set up test fixtures."""
        self.mock_manager = MagicMock()
        self.synchronizer = ModSynchronizer(self.mock_manager)

    def test_init(self): pass
        """Test initialization."""
        assert self.synchronizer.mod_data_manager == self.mock_manager

    def test_check_conflicts_no_conflicts(self): pass
        """Test conflict checking with no conflicts."""
        world_a = {
            "id": "world_a",
            "name": "World A",
            "biomes": [{"id": "forest", "name": "Forest"}],
            "factions": [{"id": "humans", "name": "Humans"}],
        }
        world_b = {
            "id": "world_b", 
            "name": "World B",
            "biomes": [{"id": "desert", "name": "Desert"}],
            "factions": [{"id": "elves", "name": "Elves"}],
        }

        conflicts = self.synchronizer.check_conflicts(world_a, world_b)
        assert len(conflicts) == 0

    def test_check_conflicts_with_conflicts(self): pass
        """Test conflict checking with conflicts."""
        world_a = {
            "id": "same_world",
            "name": "Same Name",
            "biomes": [{"id": "forest", "name": "Forest"}],
            "factions": [{"id": "humans", "name": "Humans"}],
        }
        world_b = {
            "id": "same_world",
            "name": "Same Name", 
            "biomes": [{"id": "forest", "name": "Different Forest"}],
            "factions": [{"id": "humans", "name": "Different Humans"}],
        }

        conflicts = self.synchronizer.check_conflicts(world_a, world_b)
        assert len(conflicts) == 2
        assert any("ID conflict" in conflict and "same_world" in conflict for conflict in conflicts)
        assert any("Name conflict" in conflict and "Same Name" in conflict for conflict in conflicts)

    def test_check_conflicts_missing_sections(self): pass
        """Test conflict checking with missing sections."""
        world_a = {
            "id": "world_a",
            "name": "World A", 
            "biomes": [{"id": "forest", "name": "Forest"}]
        }
        world_b = {
            "id": "world_b",
            "name": "World B",
            "factions": [{"id": "humans", "name": "Humans"}]
        }

        conflicts = self.synchronizer.check_conflicts(world_a, world_b)
        assert len(conflicts) == 0

    def test_merge_world_seeds_basic(self): pass
        """Test basic world seed merging."""
        base_seed = {
            "name": "Base World",
            "biomes": [{"id": "forest", "name": "Forest"}],
            "factions": [{"id": "humans", "name": "Humans"}],
        }
        override_seed = {
            "name": "Override World",
            "biomes": [{"id": "desert", "name": "Desert"}],
            "religions": [{"id": "sun_worship", "name": "Sun Worship"}],
        }

        merged = self.synchronizer.merge_world_seeds(base_seed, override_seed)
        
        assert merged["name"] == "Override World"
        assert len(merged["biomes"]) == 2  # Both forest and desert
        assert len(merged["factions"]) == 1  # Only humans from base
        assert len(merged["religions"]) == 1  # Sun worship from override

    def test_merge_world_seeds_with_conflicts(self): pass
        """Test world seed merging with conflicts."""
        base_seed = {
            "biomes": [{"id": "forest", "name": "Forest", "temperature": "mild"}],
        }
        override_seed = {
            "biomes": [{"id": "forest2", "name": "Forest", "humidity": "high"}],
        }

        merged = self.synchronizer.merge_world_seeds(base_seed, override_seed)
        
        # Should have one biome with merged properties (merged by name)
        assert len(merged["biomes"]) == 1
        biome = merged["biomes"][0]
        assert biome["name"] == "Forest"  # Same name
        assert biome["temperature"] == "mild"  # From base
        assert biome["humidity"] == "high"  # From override

    def test_merge_dict_basic(self): pass
        """Test basic dictionary merging."""
        dict_a = {"a": 1, "b": 2, "nested": {"x": 10}}
        dict_b = {"b": 3, "c": 4, "nested": {"y": 20}}

        merged = self.synchronizer.merge_dict(dict_a, dict_b)
        
        assert merged["a"] == 1
        assert merged["b"] == 3  # Override wins
        assert merged["c"] == 4
        assert merged["nested"]["x"] == 10
        assert merged["nested"]["y"] == 20

    def test_merge_dict_with_none(self): pass
        """Test dictionary merging with None values."""
        dict_a = {"a": 1, "b": None}
        dict_b = {"b": 2, "c": None}

        merged = self.synchronizer.merge_dict(dict_a, dict_b)
        
        assert merged["a"] == 1
        assert merged["b"] == 2
        assert merged["c"] is None

    def test_merge_biomes_no_conflicts(self): pass
        """Test biome merging without conflicts."""
        biomes_a = [{"id": "forest", "name": "Forest"}]
        biomes_b = [{"id": "desert", "name": "Desert"}]

        merged = self.synchronizer.merge_biomes(biomes_a, biomes_b)
        
        assert len(merged) == 2
        assert any(b["id"] == "forest" for b in merged)
        assert any(b["id"] == "desert" for b in merged)

    def test_merge_biomes_with_conflicts(self): pass
        """Test biome merging with conflicts."""
        biomes_a = [{"id": "forest", "name": "Forest", "temperature": "mild"}]
        biomes_b = [{"id": "forest2", "name": "Forest", "humidity": "high"}]

        merged = self.synchronizer.merge_biomes(biomes_a, biomes_b)
        
        assert len(merged) == 1
        biome = merged[0]
        assert biome["name"] == "Forest"  # Same name
        assert biome["temperature"] == "mild"  # From base
        assert biome["humidity"] == "high"  # From override

    def test_merge_factions_no_conflicts(self): pass
        """Test faction merging without conflicts."""
        factions_a = [{"id": "humans", "name": "Humans"}]
        factions_b = [{"id": "elves", "name": "Elves"}]

        merged = self.synchronizer.merge_factions(factions_a, factions_b)
        
        assert len(merged) == 2
        assert any(f["id"] == "humans" for f in merged)
        assert any(f["id"] == "elves" for f in merged)

    def test_merge_factions_with_conflicts(self): pass
        """Test faction merging with conflicts."""
        factions_a = [{"id": "humans", "name": "Humans", "culture": "medieval"}]
        factions_b = [{"id": "humans2", "name": "Humans", "technology": "advanced"}]

        merged = self.synchronizer.merge_factions(factions_a, factions_b)
        
        assert len(merged) == 1
        faction = merged[0]
        assert faction["name"] == "Humans"  # Same name
        assert faction["culture"] == "medieval"  # From base
        assert faction["technology"] == "advanced"  # From override


class TestTechnicalModInterface: pass
    """Test cases for TechnicalModInterface class."""

    def setup_method(self): pass
        """Set up test fixtures."""
        self.mock_manager = MagicMock()
        self.mock_validator = MagicMock()
        self.interface = TechnicalModInterface(self.mock_manager, self.mock_validator)

    def test_init(self): pass
        """Test initialization."""
        assert self.interface.mod_data_manager == self.mock_manager
        assert self.interface.validator == self.mock_validator

    def test_create_new_world_seed_default(self): pass
        """Test creating new world seed with default template."""
        world_seed = self.interface.create_new_world_seed()
        
        assert world_seed["name"] == "New World"
        assert world_seed["description"] == "A custom world created with the Technical Mod Interface"
        assert world_seed["author"] == "Technical Modder"
        assert world_seed["version"] == "1.0.0"
        assert "biomes" in world_seed
        assert "factions" in world_seed
        assert "religions" in world_seed
        assert "regions" in world_seed
        assert "items" in world_seed
        assert "creatures" in world_seed
        assert "worldgen_rules" in world_seed

    def test_create_new_world_seed_with_template(self): pass
        """Test creating new world seed with existing template."""
        template_data = {
            "id": "template_id",
            "name": "Template World",
            "description": "Template description",
            "creation_date": "2023-01-01",
            "biomes": [{"id": "forest"}],
        }

        # Mock file operations
        with patch('os.path.exists', return_value=True): pass
            with patch('builtins.open', mock_open(read_data=json.dumps(template_data))): pass
                world_seed = self.interface.create_new_world_seed("custom_template")
                
                assert world_seed["name"] == "Template World"
                assert world_seed["description"] == "Template description"
                assert len(world_seed["biomes"]) == 1
                assert "id" not in world_seed  # Should be removed
                assert "creation_date" not in world_seed  # Should be removed

    def test_create_new_world_seed_template_not_found(self): pass
        """Test creating world seed when template doesn't exist."""
        with patch('os.path.exists', return_value=False): pass
            world_seed = self.interface.create_new_world_seed("nonexistent")
            
            # Should fall back to default
            assert world_seed["name"] == "New World"

    def test_create_new_world_seed_template_error(self): pass
        """Test creating world seed when template loading fails."""
        with patch('os.path.exists', return_value=True): pass
            with patch('builtins.open', side_effect=IOError("File error")): pass
                with patch('backend.systems.world_generation.modding_system.logger') as mock_logger: pass
                    world_seed = self.interface.create_new_world_seed("error_template")
                    
                    # Should fall back to default
                    assert world_seed["name"] == "New World"
                    mock_logger.error.assert_called()

    def test_validate_json(self): pass
        """Test JSON validation."""
        self.mock_validator.validate_mod.return_value = (True, [])
        
        json_data = {"name": "Test"}
        is_valid, errors = self.interface.validate_json(json_data, "test_schema")
        
        assert is_valid is True
        assert errors == []
        self.mock_validator.validate_mod.assert_called_once_with(json_data, "test_schema")

    def test_save_world_seed(self): pass
        """Test world seed saving."""
        self.mock_manager.save_world_seed.return_value = True
        
        world_data = {"name": "Test World"}
        result = self.interface.save_world_seed(world_data)
        
        assert result is True
        self.mock_manager.save_world_seed.assert_called_once_with(world_data)


class TestCasualModInterface: pass
    """Test cases for CasualModInterface class."""

    def setup_method(self): pass
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.assets_dir = os.path.join(self.temp_dir, "assets")
        
        self.mock_manager = MagicMock()
        self.mock_manager.assets_dir = self.assets_dir
        self.interface = CasualModInterface(self.mock_manager)

    def teardown_method(self): pass
        """Clean up test fixtures."""
        if os.path.exists(self.temp_dir): pass
            shutil.rmtree(self.temp_dir)

    def test_init(self): pass
        """Test initialization."""
        assert self.interface.mod_data_manager == self.mock_manager

    def test_get_available_assets_success(self): pass
        """Test getting available assets successfully."""
        # Create test asset
        biome_dir = os.path.join(self.assets_dir, "biomes")
        os.makedirs(biome_dir, exist_ok=True)
        
        asset_data = {
            "id": "forest",
            "name": "Forest Biome",
            "description": "A lush forest",
            "preview_image": "forest.png",
        }
        
        asset_path = os.path.join(biome_dir, "forest.json")
        with open(asset_path, "w") as f: pass
            json.dump(asset_data, f)

        assets = self.interface.get_available_assets("biomes")
        
        assert len(assets) == 1
        assert assets[0]["id"] == "forest"
        assert assets[0]["name"] == "Forest Biome"
        assert assets[0]["description"] == "A lush forest"
        assert assets[0]["preview_image"] == "forest.png"
        assert assets[0]["file_path"] == asset_path

    def test_get_available_assets_missing_fields(self): pass
        """Test getting assets with missing metadata fields."""
        biome_dir = os.path.join(self.assets_dir, "biomes")
        os.makedirs(biome_dir, exist_ok=True)
        
        asset_data = {"id": "minimal"}
        asset_path = os.path.join(biome_dir, "minimal.json")
        
        with open(asset_path, "w") as f: pass
            json.dump(asset_data, f)

        assets = self.interface.get_available_assets("biomes")
        
        assert len(assets) == 1
        assert assets[0]["id"] == "minimal"
        assert assets[0]["name"] == "Unnamed Asset"
        assert assets[0]["description"] == ""
        assert assets[0]["preview_image"] == ""

    def test_get_available_assets_no_directory(self): pass
        """Test getting assets when directory doesn't exist."""
        assets = self.interface.get_available_assets("nonexistent")
        assert len(assets) == 0

    def test_get_available_assets_error_handling(self): pass
        """Test error handling when loading invalid asset files."""
        biome_dir = os.path.join(self.assets_dir, "biomes")
        os.makedirs(biome_dir, exist_ok=True)
        
        # Create invalid JSON file
        invalid_path = os.path.join(biome_dir, "invalid.json")
        with open(invalid_path, "w") as f: pass
            f.write("invalid json")

        with patch('backend.systems.world_generation.modding_system.logger') as mock_logger: pass
            assets = self.interface.get_available_assets("biomes")
            
            assert len(assets) == 0
            mock_logger.error.assert_called()

    def test_create_world_from_selections(self): pass
        """Test creating world from user selections."""
        selections = {
            "biomes": ["forest", "desert"],
            "factions": ["humans"],
        }
        metadata = {
            "name": "Custom World",
            "description": "My custom world",
            "author": "Test User",
        }

        # Mock asset loading
        def mock_load_asset(asset_type, asset_id): pass
            return {"id": asset_id, "name": f"{asset_id.title()} Asset"}

        with patch.object(self.interface, '_load_asset', side_effect=mock_load_asset): pass
            world_seed = self.interface.create_world_from_selections(selections, metadata)
            
            assert world_seed["name"] == "Custom World"
            assert world_seed["description"] == "My custom world"
            assert world_seed["author"] == "Test User"
            assert world_seed["version"] == "1.0.0"
            assert "id" in world_seed
            assert "creation_date" in world_seed
            
            assert len(world_seed["biomes"]) == 2
            assert len(world_seed["factions"]) == 1
            assert world_seed["biomes"][0]["id"] == "forest"
            assert world_seed["biomes"][1]["id"] == "desert"
            assert world_seed["factions"][0]["id"] == "humans"

    def test_create_world_from_selections_minimal_metadata(self): pass
        """Test creating world with minimal metadata."""
        selections = {"biomes": ["forest"]}
        metadata = {}

        with patch.object(self.interface, '_load_asset', return_value={"id": "forest"}): pass
            world_seed = self.interface.create_world_from_selections(selections, metadata)
            
            assert world_seed["name"] == "Custom World"
            assert world_seed["description"] == "A world created with the Casual Mod Interface"
            assert world_seed["author"] == "Casual Modder"

    def test_create_world_from_selections_asset_not_found(self): pass
        """Test creating world when some assets can't be loaded."""
        selections = {"biomes": ["forest", "nonexistent"]}
        metadata = {"name": "Test World"}

        def mock_load_asset(asset_type, asset_id): pass
            if asset_id == "forest": pass
                return {"id": "forest", "name": "Forest"}
            return None

        with patch.object(self.interface, '_load_asset', side_effect=mock_load_asset): pass
            world_seed = self.interface.create_world_from_selections(selections, metadata)
            
            # Should only include the successfully loaded asset
            assert len(world_seed["biomes"]) == 1
            assert world_seed["biomes"][0]["id"] == "forest"

    def test_load_asset_success(self): pass
        """Test successful asset loading."""
        biome_dir = os.path.join(self.assets_dir, "biomes")
        os.makedirs(biome_dir, exist_ok=True)
        
        asset_data = {"id": "forest", "name": "Forest Biome"}
        asset_path = os.path.join(biome_dir, "forest.json")
        
        with open(asset_path, "w") as f: pass
            json.dump(asset_data, f)

        loaded_asset = self.interface._load_asset("biomes", "forest")
        
        assert loaded_asset == asset_data

    def test_load_asset_not_found(self): pass
        """Test loading non-existent asset."""
        with patch('backend.systems.world_generation.modding_system.logger') as mock_logger: pass
            result = self.interface._load_asset("biomes", "nonexistent")
            
            assert result is None
            mock_logger.error.assert_called()

    def test_load_asset_error_handling(self): pass
        """Test error handling when loading invalid asset."""
        biome_dir = os.path.join(self.assets_dir, "biomes")
        os.makedirs(biome_dir, exist_ok=True)
        
        # Create invalid JSON file
        asset_path = os.path.join(biome_dir, "invalid.json")
        with open(asset_path, "w") as f: pass
            f.write("invalid json")

        with patch('backend.systems.world_generation.modding_system.logger') as mock_logger: pass
            result = self.interface._load_asset("biomes", "invalid")
            
            assert result is None
            mock_logger.error.assert_called()

    def test_save_world_seed(self): pass
        """Test world seed saving."""
        self.mock_manager.save_world_seed.return_value = True
        
        world_data = {"name": "Test World"}
        result = self.interface.save_world_seed(world_data)
        
        assert result is True
        self.mock_manager.save_world_seed.assert_called_once_with(world_data)


class TestModuleConstants: pass
    """Test module-level constants and singleton instances."""

    def test_default_paths(self): pass
        """Test that default paths are properly defined."""
        assert DEFAULT_MODDING_DIR is not None
        assert DEFAULT_WORLDS_DIR is not None
        assert DEFAULT_SCHEMAS_DIR is not None
        assert DEFAULT_ASSETS_DIR is not None

    def test_singleton_instances_exist(self): pass
        """Test that singleton instances are created."""
        from backend.systems.world_generation.modding_system import (
            mod_data_manager,
            mod_validator,
            mod_synchronizer,
            technical_mod_interface,
            casual_mod_interface,
        )
        
        assert mod_data_manager is not None
        assert mod_validator is not None
        assert mod_synchronizer is not None
        assert technical_mod_interface is not None
        assert casual_mod_interface is not None
        
        # Check types
        assert isinstance(mod_data_manager, ModDataManager)
        assert isinstance(mod_validator, ModValidationService)
        assert isinstance(mod_synchronizer, ModSynchronizer)
        assert isinstance(technical_mod_interface, TechnicalModInterface)
        assert isinstance(casual_mod_interface, CasualModInterface)


class TestIntegration: pass
    """Integration tests for modding system components."""

    def setup_method(self): pass
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.modding_dir = os.path.join(self.temp_dir, "modding")
        self.worlds_dir = os.path.join(self.modding_dir, "worlds")
        self.schemas_dir = os.path.join(self.modding_dir, "schemas")
        self.assets_dir = os.path.join(self.modding_dir, "assets")

    def teardown_method(self): pass
        """Clean up test fixtures."""
        if os.path.exists(self.temp_dir): pass
            shutil.rmtree(self.temp_dir)

    def test_full_workflow_technical_interface(self): pass
        """Test complete workflow using technical interface."""
        # Create manager and interfaces
        manager = ModDataManager(
            modding_dir=self.modding_dir,
            worlds_dir=self.worlds_dir,
            schemas_dir=self.schemas_dir,
            assets_dir=self.assets_dir,
        )
        validator = ModValidationService(schemas_dir=self.schemas_dir)
        tech_interface = TechnicalModInterface(manager, validator)

        # Create new world seed
        world_seed = tech_interface.create_new_world_seed()
        world_seed["name"] = "Integration Test World"
        world_seed["biomes"] = [{"id": "forest", "name": "Test Forest"}]

        # Save world seed
        result = tech_interface.save_world_seed(world_seed)
        assert result is True

        # Load world seed back
        loaded_seed = manager.load_world_seed(world_seed["id"])
        assert loaded_seed is not None
        assert loaded_seed["name"] == "Integration Test World"

        # Check available worlds
        available_worlds = manager.get_available_worlds()
        assert len(available_worlds) == 1
        assert available_worlds[0]["name"] == "Integration Test World"

    def test_full_workflow_casual_interface(self): pass
        """Test complete workflow using casual interface."""
        # Create manager and interface
        manager = ModDataManager(
            modding_dir=self.modding_dir,
            worlds_dir=self.worlds_dir,
            schemas_dir=self.schemas_dir,
            assets_dir=self.assets_dir,
        )
        casual_interface = CasualModInterface(manager)

        # Create test assets
        biome_dir = os.path.join(self.assets_dir, "biomes")
        os.makedirs(biome_dir, exist_ok=True)
        
        forest_asset = {"id": "forest", "name": "Forest Biome"}
        with open(os.path.join(biome_dir, "forest.json"), "w") as f: pass
            json.dump(forest_asset, f)

        # Get available assets
        assets = casual_interface.get_available_assets("biomes")
        assert len(assets) == 1

        # Create world from selections
        selections = {"biomes": ["forest"]}
        metadata = {"name": "Casual Test World", "author": "Test User"}
        
        world_seed = casual_interface.create_world_from_selections(selections, metadata)
        assert world_seed["name"] == "Casual Test World"
        assert len(world_seed["biomes"]) == 1

        # Save world seed
        result = casual_interface.save_world_seed(world_seed)
        assert result is True

        # Verify it was saved
        available_worlds = manager.get_available_worlds()
        assert len(available_worlds) == 1
        assert available_worlds[0]["name"] == "Casual Test World"

    def test_synchronizer_integration(self): pass
        """Test synchronizer integration with manager."""
        manager = ModDataManager(
            modding_dir=self.modding_dir,
            worlds_dir=self.worlds_dir,
            schemas_dir=self.schemas_dir,
            assets_dir=self.assets_dir,
        )
        synchronizer = ModSynchronizer(manager)

        # Create two world seeds
        world_a = {
            "id": "world_a",
            "name": "World A",
            "biomes": [{"id": "forest", "name": "Forest A"}],
            "factions": [{"id": "humans", "name": "Humans A"}],
        }
        
        world_b = {
            "id": "world_b", 
            "name": "World B",
            "biomes": [{"id": "desert", "name": "Desert B"}],
            "factions": [{"id": "elves", "name": "Elves B"}],
        }

        # Save both worlds
        manager.save_world_seed(world_a)
        manager.save_world_seed(world_b)

        # Check for conflicts
        conflicts = synchronizer.check_conflicts(world_a, world_b)
        assert len(conflicts) == 0  # No conflicts expected

        # Merge worlds
        merged = synchronizer.merge_world_seeds(world_a, world_b)
        assert merged["name"] == "World B"  # Override wins
        assert len(merged["biomes"]) == 2  # Both biomes
        assert len(merged["factions"]) == 2  # Both factions


class TestErrorHandling: pass
    """Test error handling scenarios."""

    def test_modding_system_with_permission_errors(self): pass
        """Test handling of permission errors."""
        with patch('os.makedirs', side_effect=PermissionError("Permission denied")): pass
            with pytest.raises(PermissionError): pass
                ModDataManager(modding_dir="/invalid/path")

    def test_modding_system_with_disk_full(self): pass
        """Test handling of disk full errors."""
        manager = ModDataManager()
        world_data = {"name": "Test", "biomes": [], "factions": []}
        
        with patch.object(manager, 'validate_world_seed', return_value=True): pass
            with patch('builtins.open', side_effect=OSError("No space left on device")): pass
                with patch('backend.systems.world_generation.modding_system.logger') as mock_logger: pass
                    result = manager.save_world_seed(world_data)
                    
                    assert result is False
                    mock_logger.error.assert_called()

    def test_corrupted_schema_files(self): pass
        """Test handling of corrupted schema files."""
        temp_dir = tempfile.mkdtemp()
        schemas_dir = os.path.join(temp_dir, "schemas")
        
        try: pass
            os.makedirs(schemas_dir)
            
            # Create corrupted schema file
            with open(os.path.join(schemas_dir, "corrupted.schema.json"), "w") as f: pass
                f.write("{ invalid json content")

            with patch('backend.systems.world_generation.modding_system.logger') as mock_logger: pass
                manager = ModDataManager(schemas_dir=schemas_dir)
                
                assert "corrupted" not in manager.schemas
                mock_logger.error.assert_called()
        finally: pass
            shutil.rmtree(temp_dir)

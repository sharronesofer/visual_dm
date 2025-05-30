"""
Tests for the WorldGenerator class.

This module contains tests for the WorldGenerator that orchestrates the
world generation process.
"""

import pytest
import os
import json
import random
import time
from unittest.mock import patch, MagicMock, call

from backend.systems.world_generation.world_generator import (
    WorldGenerator,
    GenerationPhase,
    GenerationStatus,
)


class TestWorldGenerator: pass
    """Tests for the WorldGenerator class."""

    def test_singleton_pattern(self): pass
        """Test that WorldGenerator follows singleton pattern."""
        generator1 = WorldGenerator()
        generator2 = WorldGenerator()
        assert generator1 is generator2
        assert generator1._initialized is True

    def test_initialization(self): pass
        """Test that the WorldGenerator initializes correctly."""
        world_generator = WorldGenerator()
        
        # Check basic attributes
        assert world_generator._initialized is True
        assert world_generator.world_data is not None
        assert world_generator.biome_calculator is not None
        assert world_generator.adjacency_rules is not None
        assert world_generator.is_initialized is False
        assert world_generator.is_generating is False
        assert world_generator.last_seed is None

        # Check world data structure
        assert "metadata" in world_generator.world_data
        assert "continents" in world_generator.world_data
        assert "regions" in world_generator.world_data
        assert "oceans" in world_generator.world_data
        assert "climate_zones" in world_generator.world_data

    @patch('backend.systems.world_generation.world_generator.ContinentService')
    @patch('backend.systems.world_generation.world_generator.SettlementService')
    @patch('backend.systems.world_generation.world_generator.RegionalFeatures')
    def test_initialize_world_with_seed(self, mock_regional_features, mock_settlement_service, mock_continent_service): pass
        """Test initializing a world with a specific seed."""
        world_generator = WorldGenerator()
        test_seed = 12345
        test_name = "Test World"
        
        result = world_generator.initialize_world(seed=test_seed, name=test_name)
        
        assert world_generator.is_initialized is True
        assert world_generator.last_seed == test_seed
        assert result["metadata"]["seed"] == test_seed
        assert result["metadata"]["name"] == test_name
        assert world_generator.continent_service is not None
        assert world_generator.settlement_service is not None
        assert world_generator.regional_features is not None

    @patch('backend.systems.world_generation.world_generator.ContinentService')
    @patch('backend.systems.world_generation.world_generator.SettlementService')
    @patch('backend.systems.world_generation.world_generator.RegionalFeatures')
    def test_initialize_world_without_seed(self, mock_regional_features, mock_settlement_service, mock_continent_service): pass
        """Test initializing a world without specifying a seed."""
        world_generator = WorldGenerator()
        
        result = world_generator.initialize_world()
        
        assert world_generator.is_initialized is True
        assert world_generator.last_seed is not None
        assert result["metadata"]["seed"] is not None
        assert result["metadata"]["name"] == "Generated World"

    def test_generate_world_not_initialized(self): pass
        """Test that generate_world raises error when not initialized."""
        world_generator = WorldGenerator()
        world_generator.is_initialized = False
        
        with pytest.raises(ValueError, match="World not initialized"): pass
            world_generator.generate_world()

    @patch('backend.systems.world_generation.world_generator.ContinentService')
    @patch('backend.systems.world_generation.world_generator.SettlementService')
    @patch('backend.systems.world_generation.world_generator.RegionalFeatures')
    def test_generate_world_success(self, mock_regional_features, mock_settlement_service, mock_continent_service): pass
        """Test successful world generation."""
        world_generator = WorldGenerator()
        world_generator.initialize_world(seed=12345)
        
        # Mock the continent service
        mock_continent = {
            "id": 1,
            "name": "Continent 1",
            "regions": []
        }
        world_generator.continent_service.create_continent.return_value = mock_continent
        
        # Mock private methods
        with patch.object(world_generator, '_generate_regions_for_continent') as mock_regions, \
             patch.object(world_generator, '_generate_rivers_for_continent') as mock_rivers, \
             patch.object(world_generator, '_generate_settlements_for_continent') as mock_settlements, \
             patch.object(world_generator, '_generate_features_for_continent') as mock_features, \
             patch.object(world_generator, '_generate_world_oceans') as mock_oceans, \
             patch.object(world_generator, '_generate_climate_zones') as mock_climate, \
             patch.object(world_generator, '_collect_all_regions') as mock_collect, \
             patch.object(world_generator, '_save_world_data') as mock_save: pass
            mock_collect.return_value = []
            
            result = world_generator.generate_world(num_continents=2)
            
            # Verify methods were called
            assert world_generator.continent_service.create_continent.call_count == 2
            assert mock_regions.call_count == 2
            assert mock_rivers.call_count == 2
            assert mock_settlements.call_count == 2
            assert mock_features.call_count == 2
            mock_oceans.assert_called_once()
            mock_climate.assert_called_once()
            mock_collect.assert_called_once()
            mock_save.assert_called_once()
            
            assert result is not None
            assert world_generator.is_generating is False

    def test_generate_continent_not_initialized(self): pass
        """Test that generate_continent raises error when not initialized."""
        world_generator = WorldGenerator()
        world_generator.is_initialized = False
        
        with pytest.raises(ValueError, match="World not initialized"): pass
            world_generator.generate_continent()

    @patch('backend.systems.world_generation.world_generator.ContinentService')
    @patch('backend.systems.world_generation.world_generator.SettlementService')
    @patch('backend.systems.world_generation.world_generator.RegionalFeatures')
    def test_generate_continent_success(self, mock_regional_features, mock_settlement_service, mock_continent_service): pass
        """Test successful continent generation."""
        world_generator = WorldGenerator()
        world_generator.initialize_world(seed=12345)
        
        # Mock the continent service
        mock_continent = {
            "id": 1,
            "name": "Test Continent",
            "regions": []
        }
        world_generator.continent_service.create_continent.return_value = mock_continent
        
        # Mock private methods
        with patch.object(world_generator, '_generate_regions_for_continent') as mock_regions, \
             patch.object(world_generator, '_generate_rivers_for_continent') as mock_rivers, \
             patch.object(world_generator, '_generate_settlements_for_continent') as mock_settlements, \
             patch.object(world_generator, '_generate_features_for_continent') as mock_features: pass
            result = world_generator.generate_continent(
                name="Test Continent",
                min_regions=5,
                max_regions=10,
                origin_x=100,
                origin_y=200
            )
            
            # Verify continent service was called with correct parameters
            world_generator.continent_service.create_continent.assert_called_once_with(
                "Test Continent", 5, 10, 100, 200
            )
            
            # Verify generation methods were called
            mock_regions.assert_called_once_with(1)
            mock_rivers.assert_called_once_with(1)
            mock_settlements.assert_called_once_with(1)
            mock_features.assert_called_once_with(1)
            
            assert result == mock_continent

    @patch('backend.systems.world_generation.world_generator.ContinentService')
    @patch('backend.systems.world_generation.world_generator.SettlementService')
    @patch('backend.systems.world_generation.world_generator.RegionalFeatures')
    def test_get_weather_for_region(self, mock_regional_features, mock_settlement_service, mock_continent_service): pass
        """Test getting weather for a region."""
        world_generator = WorldGenerator()
        world_generator.initialize_world(seed=12345)
        
        # Mock the world data with a region
        test_region = {
            "id": "test_region",
            "latitude": 45.0,
            "longitude": -75.0,
            "elevation": 100,
            "biome": "temperate_forest"
        }
        world_generator.world_data["regions"] = [test_region]
        
        with patch('backend.systems.world_generation.world_generation_utils.generate_procedural_weather') as mock_weather: pass
            mock_weather.return_value = {
                "temperature": 20,
                "humidity": 60,
                "precipitation": 0.1,
                "wind_speed": 5
            }
            
            result = world_generator.get_weather_for_region("test_region")
            
            mock_weather.assert_called_once()
            assert result["temperature"] == 20
            assert result["humidity"] == 60

    @patch('backend.systems.world_generation.world_generator.ContinentService')
    @patch('backend.systems.world_generation.world_generator.SettlementService')
    @patch('backend.systems.world_generation.world_generator.RegionalFeatures')
    def test_get_weather_for_nonexistent_region(self, mock_regional_features, mock_settlement_service, mock_continent_service): pass
        """Test getting weather for a region that doesn't exist."""
        world_generator = WorldGenerator()
        world_generator.initialize_world(seed=12345)
        
        result = world_generator.get_weather_for_region("nonexistent")
        
        assert result == {}

    @patch('backend.systems.world_generation.world_generator.ContinentService')
    @patch('backend.systems.world_generation.world_generator.SettlementService')
    @patch('backend.systems.world_generation.world_generator.RegionalFeatures')
    @patch('builtins.open', create=True)
    @patch('json.dump')
    def test_save_world_data(self, mock_json_dump, mock_open, mock_regional_features, mock_settlement_service, mock_continent_service): pass
        """Test saving world data."""
        world_generator = WorldGenerator()
        world_generator.initialize_world(seed=12345)
        
        world_generator._save_world_data()
        
        mock_open.assert_called_once()
        mock_json_dump.assert_called_once()

    @patch('os.path.exists')
    @patch('builtins.open', create=True)
    @patch('json.load')
    def test_load_world(self, mock_json_load, mock_open, mock_exists): pass
        """Test loading world data."""
        world_generator = WorldGenerator()
        
        mock_world_data = {
            "metadata": {"seed": 12345, "name": "Test World"},
            "continents": [],
            "regions": []
        }
        mock_json_load.return_value = mock_world_data
        mock_exists.return_value = True
        
        result = world_generator.load_world("test_world.json")
        
        mock_open.assert_called_once_with("test_world.json", "r")
        mock_json_load.assert_called_once()
        assert result == mock_world_data
        assert world_generator.world_data == mock_world_data

    @patch('os.path.exists')
    def test_load_world_file_not_found(self, mock_exists): pass
        """Test loading world data when file doesn't exist."""
        world_generator = WorldGenerator()
        
        mock_exists.return_value = False
        
        with pytest.raises(FileNotFoundError, match="World data file not found"): pass
            world_generator.load_world("nonexistent.json")

    @patch('backend.systems.world_generation.world_generator.ContinentService')
    @patch('backend.systems.world_generation.world_generator.SettlementService')
    @patch('backend.systems.world_generation.world_generator.RegionalFeatures')
    @patch('builtins.open', create=True)
    @patch('json.dump')
    def test_export_world_json(self, mock_json_dump, mock_open, mock_regional_features, mock_settlement_service, mock_continent_service): pass
        """Test exporting world data as JSON."""
        world_generator = WorldGenerator()
        world_generator.initialize_world(seed=12345)
        
        result = world_generator.export_world(format="json")
        
        mock_open.assert_called_once()
        mock_json_dump.assert_called_once()
        assert result.endswith(".json")

    @patch('backend.systems.world_generation.world_generator.ContinentService')
    @patch('backend.systems.world_generation.world_generator.SettlementService')
    @patch('backend.systems.world_generation.world_generator.RegionalFeatures')
    def test_export_world_unsupported_format(self, mock_regional_features, mock_settlement_service, mock_continent_service): pass
        """Test exporting world data with unsupported format."""
        world_generator = WorldGenerator()
        world_generator.initialize_world(seed=12345)
        
        with pytest.raises(ValueError, match="Unsupported export format"): pass
            world_generator.export_world(format="xml")

    @patch('backend.systems.world_generation.world_generator.ContinentService')
    @patch('backend.systems.world_generation.world_generator.SettlementService')
    @patch('backend.systems.world_generation.world_generator.RegionalFeatures')
    def test_get_continent_by_id_existing(self, mock_regional_features, mock_settlement_service, mock_continent_service): pass
        """Test getting an existing continent by ID."""
        world_generator = WorldGenerator()
        world_generator.initialize_world(seed=12345)
        
        test_continent = {"id": 1, "name": "Test Continent"}
        world_generator.world_data["continents"] = [test_continent]
        
        result = world_generator._get_continent_by_id(1)
        
        assert result == test_continent

    @patch('backend.systems.world_generation.world_generator.ContinentService')
    @patch('backend.systems.world_generation.world_generator.SettlementService')
    @patch('backend.systems.world_generation.world_generator.RegionalFeatures')
    def test_get_continent_by_id_nonexistent(self, mock_regional_features, mock_settlement_service, mock_continent_service): pass
        """Test getting a nonexistent continent by ID."""
        world_generator = WorldGenerator()
        world_generator.initialize_world(seed=12345)
        
        result = world_generator._get_continent_by_id(999)
        
        assert result is None

    @patch('backend.systems.world_generation.world_generator.ContinentService')
    @patch('backend.systems.world_generation.world_generator.SettlementService')
    @patch('backend.systems.world_generation.world_generator.RegionalFeatures')
    def test_collect_all_regions(self, mock_regional_features, mock_settlement_service, mock_continent_service): pass
        """Test collecting all regions from all continents."""
        world_generator = WorldGenerator()
        world_generator.initialize_world(seed=12345)
        
        # Mock continents with regions
        continent1 = {"id": 1, "regions": [{"id": "r1"}, {"id": "r2"}]}
        continent2 = {"id": 2, "regions": [{"id": "r3"}]}
        world_generator.world_data["continents"] = [continent1, continent2]
        
        result = world_generator._collect_all_regions()
        
        assert len(result) == 3
        assert {"id": "r1"} in result
        assert {"id": "r2"} in result
        assert {"id": "r3"} in result

    def test_get_continent_regions(self): pass
        """Test getting regions for a specific continent."""
        world_generator = WorldGenerator()
        world_generator.initialize_world(seed=12345)
        
        # Mock continent with regions
        test_regions = [{"id": "r1"}, {"id": "r2"}]
        continent = {"id": 1, "regions": test_regions}
        world_generator.world_data["continents"] = [continent]
        
        result = world_generator._get_continent_regions(1)
        
        assert result == test_regions

    def test_get_continent_regions_nonexistent(self): pass
        """Test getting regions for a nonexistent continent."""
        world_generator = WorldGenerator()
        world_generator.initialize_world(seed=12345)
        
        result = world_generator._get_continent_regions(999)
        
        assert result == []


class TestGenerationEnums: pass
    """Tests for the generation enums."""

    def test_generation_phase_enum(self): pass
        """Test GenerationPhase enum values."""
        assert GenerationPhase.NOT_STARTED.value == "not_started"
        assert GenerationPhase.INITIALIZING.value == "initializing"
        assert GenerationPhase.CONTINENTS.value == "continents"
        assert GenerationPhase.REGIONS.value == "regions"
        assert GenerationPhase.COMPLETED.value == "completed"
        assert GenerationPhase.ERROR.value == "error"

    def test_generation_status_enum(self): pass
        """Test GenerationStatus enum values."""
        assert GenerationStatus.IDLE.value == "idle"
        assert GenerationStatus.GENERATING.value == "generating"
        assert GenerationStatus.PAUSED.value == "paused"
        assert GenerationStatus.COMPLETED.value == "completed"
        assert GenerationStatus.FAILED.value == "failed"

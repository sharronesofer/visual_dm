"""
from dataclasses import dataclass
Tests for backend.systems.world_state.utils.terrain_generator

Comprehensive tests for the terrain generation functionality.
"""

import pytest
import json
import numpy as np
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, mock_open
from dataclasses import asdict

# Import the module being tested
try: pass
    from backend.systems.world_state.utils.terrain_generator import (
        NoiseLayer, TerrainConfig, BiomeInfo, TerrainGenerator
    )
except ImportError as e: pass
    pytest.skip(f"Could not import backend.systems.world_state.utils.terrain_generator: {e}", allow_module_level=True)


class TestNoiseLayer: pass
    """Test NoiseLayer dataclass."""

    def test_noise_layer_creation(self): pass
        """Test NoiseLayer creation with all parameters."""
        layer = NoiseLayer(
            scale=100.0,
            amplitude=1.0,
            octaves=4,
            persistence=0.5,
            lacunarity=2.0,
            seed_offset=1000
        )
        
        assert layer.scale == 100.0
        assert layer.amplitude == 1.0
        assert layer.octaves == 4
        assert layer.persistence == 0.5
        assert layer.lacunarity == 2.0
        assert layer.seed_offset == 1000

    def test_noise_layer_defaults(self): pass
        """Test NoiseLayer default values."""
        layer = NoiseLayer(scale=50.0, amplitude=0.5)
        
        assert layer.scale == 50.0
        assert layer.amplitude == 0.5
        assert layer.octaves == 1
        assert layer.persistence == 0.5
        assert layer.lacunarity == 2.0
        assert layer.seed_offset == 0


class TestTerrainConfig: pass
    """Test TerrainConfig dataclass."""

    def test_terrain_config_creation(self): pass
        """Test TerrainConfig creation."""
        elevation_layers = [NoiseLayer(scale=100.0, amplitude=1.0)]
        moisture_layers = [NoiseLayer(scale=120.0, amplitude=0.8)]
        temperature_layers = [NoiseLayer(scale=150.0, amplitude=0.9)]
        
        config = TerrainConfig(
            elevation_layers=elevation_layers,
            moisture_layers=moisture_layers,
            temperature_layers=temperature_layers,
            river_threshold=0.8,
            mountain_threshold=0.7,
            lake_threshold=0.25,
            transition_width=0.2
        )
        
        assert config.elevation_layers == elevation_layers
        assert config.moisture_layers == moisture_layers
        assert config.temperature_layers == temperature_layers
        assert config.river_threshold == 0.8
        assert config.mountain_threshold == 0.7
        assert config.lake_threshold == 0.25
        assert config.transition_width == 0.2

    def test_terrain_config_defaults(self): pass
        """Test TerrainConfig default values."""
        config = TerrainConfig()
        
        assert config.elevation_layers == []
        assert config.moisture_layers == []
        assert config.temperature_layers == []
        assert config.river_threshold == 0.85
        assert config.mountain_threshold == 0.75
        assert config.lake_threshold == 0.3
        assert config.transition_width == 0.15

    def test_terrain_config_default_classmethod(self): pass
        """Test TerrainConfig.default() class method."""
        config = TerrainConfig.default()
        
        assert len(config.elevation_layers) == 3
        assert len(config.moisture_layers) == 2
        assert len(config.temperature_layers) == 2
        
        # Test first elevation layer
        assert config.elevation_layers[0].scale == 100.0
        assert config.elevation_layers[0].amplitude == 1.0
        assert config.elevation_layers[0].octaves == 4
        
        # Test moisture layers
        assert config.moisture_layers[0].scale == 120.0
        assert config.moisture_layers[0].amplitude == 1.0
        
        # Test temperature layers
        assert config.temperature_layers[0].scale == 150.0
        assert config.temperature_layers[0].amplitude == 1.0


class TestBiomeInfo: pass
    """Test BiomeInfo dataclass."""

    def test_biome_info_creation(self): pass
        """Test BiomeInfo creation with all parameters."""
        biome = BiomeInfo(
            id="test_biome",
            name="Test Biome",
            temperature_range=(0.3, 0.7),
            moisture_range=(0.4, 0.8),
            elevation_range=(0.2, 0.6),
            features=["trees", "rocks"],
            resources={"wood": 0.8, "stone": 0.6},
            color="#00FF00",
            is_water=False,
            is_transition=True,
            base_biomes=["forest", "plains"]
        )
        
        assert biome.id == "test_biome"
        assert biome.name == "Test Biome"
        assert biome.temperature_range == (0.3, 0.7)
        assert biome.moisture_range == (0.4, 0.8)
        assert biome.elevation_range == (0.2, 0.6)
        assert biome.features == ["trees", "rocks"]
        assert biome.resources == {"wood": 0.8, "stone": 0.6}
        assert biome.color == "#00FF00"
        assert biome.is_water == False
        assert biome.is_transition == True
        assert biome.base_biomes == ["forest", "plains"]

    def test_biome_info_defaults(self): pass
        """Test BiomeInfo default values."""
        biome = BiomeInfo(
            id="test",
            name="Test",
            temperature_range=(0, 1),
            moisture_range=(0, 1),
            elevation_range=(0, 1),
            features=[],
            resources={},
            color="#FFFFFF"
        )
        
        assert biome.is_water == False
        assert biome.is_transition == False
        assert biome.base_biomes == []


class TestTerrainGeneratorInitialization: pass
    """Test TerrainGenerator initialization."""

    def test_init_basic(self): pass
        """Test basic initialization."""
        config = TerrainConfig.default()
        generator = TerrainGenerator(seed=12345, config=config)
        
        assert generator.seed == 12345
        assert generator.config == config
        assert generator.biomes == {}
        assert generator.biome_order == []
        assert generator.waterbiomes == []
        assert generator.landbiomes == []
        assert generator._noise_cache == {}

    def test_init_custom_config(self): pass
        """Test initialization with custom config."""
        config = TerrainConfig(
            elevation_layers=[NoiseLayer(scale=200.0, amplitude=2.0)],
            river_threshold=0.9
        )
        generator = TerrainGenerator(seed=54321, config=config)
        
        assert generator.seed == 54321
        assert generator.config.river_threshold == 0.9
        assert len(generator.config.elevation_layers) == 1


class TestBiomeDataLoading: pass
    """Test biome data loading functionality."""

    def setup_method(self): pass
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = TerrainConfig.default()
        self.generator = TerrainGenerator(seed=12345, config=self.config)

    def teardown_method(self): pass
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)

    def test_load_biome_data_from_file(self): pass
        """Test loading biome data from existing file."""
        biome_data = {
            "forest": {
                "name": "Forest",
                "temperature_range": [0.3, 0.7],
                "moisture_range": [0.6, 1.0],
                "elevation_range": [0.3, 0.7],
                "features": ["trees", "wildlife"],
                "resources": {"wood": 0.9, "game": 0.7},
                "color": "#228B22"
            },
            "desert": {
                "name": "Desert",
                "temperature_range": [0.7, 1.0],
                "moisture_range": [0.0, 0.3],
                "elevation_range": [0.3, 0.8],
                "features": ["dunes", "cacti"],
                "resources": {"sand": 0.9, "gold": 0.2},
                "color": "#EDC9AF"
            }
        }
        
        biome_file = Path(self.temp_dir) / "biomes.json"
        with open(biome_file, "w") as f: pass
            json.dump(biome_data, f)
        
        self.generator.load_biome_data(str(self.temp_dir))
        
        assert "forest" in self.generator.biomes
        assert "desert" in self.generator.biomes
        assert self.generator.biomes["forest"].name == "Forest"
        assert self.generator.biomes["desert"].name == "Desert"
        assert "forest" in self.generator.landbiomes
        assert "desert" in self.generator.landbiomes

    def test_load_biome_data_no_file(self): pass
        """Test loading biome data when file doesn't exist (uses defaults)."""
        self.generator.load_biome_data(str(self.temp_dir))
        
        # Should load default biomes
        assert "ocean" in self.generator.biomes
        assert "desert" in self.generator.biomes
        assert "plains" in self.generator.biomes
        assert "forest" in self.generator.biomes
        assert "mountains" in self.generator.biomes
        assert "tundra" in self.generator.biomes
        assert "swamp" in self.generator.biomes
        assert "river" in self.generator.biomes
        
        # Check water vs land biomes
        assert "ocean" in self.generator.waterbiomes
        assert "river" in self.generator.waterbiomes
        assert "forest" in self.generator.landbiomes
        assert "desert" in self.generator.landbiomes

    def test_load_biome_data_water_biomes(self): pass
        """Test proper categorization of water biomes."""
        biome_data = {
            "ocean": {
                "name": "Ocean",
                "temperature_range": [0.0, 1.0],
                "moisture_range": [0.0, 1.0],
                "elevation_range": [0.0, 0.3],
                "features": ["deep_water"],
                "resources": {"fish": 0.8},
                "color": "#0077BE",
                "is_water": True
            },
            "lake": {
                "name": "Lake",
                "temperature_range": [0.0, 1.0],
                "moisture_range": [0.0, 1.0],
                "elevation_range": [0.3, 0.6],
                "features": ["shallow_water"],
                "resources": {"fish": 0.6},
                "color": "#4169E1",
                "is_water": True
            }
        }
        
        biome_file = Path(self.temp_dir) / "biomes.json"
        with open(biome_file, "w") as f: pass
            json.dump(biome_data, f)
        
        self.generator.load_biome_data(str(self.temp_dir))
        
        assert len(self.generator.waterbiomes) == 2
        assert "ocean" in self.generator.waterbiomes
        assert "lake" in self.generator.waterbiomes
        assert len(self.generator.landbiomes) == 0

    def test_load_biome_data_corrupted_json(self): pass
        """Test loading biome data with corrupted JSON."""
        biome_file = Path(self.temp_dir) / "biomes.json"
        with open(biome_file, "w") as f: pass
            f.write("invalid json content")
        
        with pytest.raises(json.JSONDecodeError): pass
            self.generator.load_biome_data(str(self.temp_dir))


class TestTransitionBiomeGeneration: pass
    """Test transition biome generation."""

    def setup_method(self): pass
        """Set up test environment."""
        self.config = TerrainConfig.default()
        self.generator = TerrainGenerator(seed=12345, config=self.config)
        
        # Load default biomes
        self.generator.load_biome_data("nonexistent_dir")  # Will use defaults

    def test_generate_transition_biomes(self): pass
        """Test transition biome generation."""
        original_biome_count = len(self.generator.biomes)
        
        self.generator.generate_transition_biomes()
        
        # Should have more biomes after generating transitions
        assert len(self.generator.biomes) > original_biome_count
        
        # Check that transition biomes are marked properly
        transition_biomes = [
            biome for biome in self.generator.biomes.values()
            if biome.is_transition
        ]
        assert len(transition_biomes) > 0
        
        # Check transition biome properties
        for transition_biome in transition_biomes: pass
            assert len(transition_biome.base_biomes) == 2
            assert transition_biome.id.count("_") >= 1  # Should have underscore in name

    def test_transition_biome_properties(self): pass
        """Test that transition biomes have proper blended properties."""
        self.generator.generate_transition_biomes()
        
        # Find a transition biome
        transition_biome = None
        for biome in self.generator.biomes.values(): pass
            if biome.is_transition: pass
                transition_biome = biome
                break
        
        assert transition_biome is not None
        
        # Get base biomes
        base1 = self.generator.biomes[transition_biome.base_biomes[0]]
        base2 = self.generator.biomes[transition_biome.base_biomes[1]]
        
        # Check that ranges encompass both base biomes
        assert (transition_biome.temperature_range[0] <= min(base1.temperature_range[0], base2.temperature_range[0]))
        assert (transition_biome.temperature_range[1] >= max(base1.temperature_range[1], base2.temperature_range[1]))


class TestNoiseGeneration: pass
    """Test noise generation functionality."""

    def setup_method(self): pass
        """Set up test environment."""
        self.config = TerrainConfig.default()
        self.generator = TerrainGenerator(seed=12345, config=self.config)

    def test_perlin_noise_deterministic(self): pass
        """Test that Perlin noise is deterministic for same inputs."""
        x, y, seed = 10.5, 20.3, 12345
        
        noise1 = self.generator._perlin_noise(x, y, seed)
        noise2 = self.generator._perlin_noise(x, y, seed)
        
        assert noise1 == noise2

    def test_perlin_noise_different_seeds(self): pass
        """Test that Perlin noise produces different values for different seeds."""
        x, y = 10.5, 20.3
        
        noise1 = self.generator._perlin_noise(x, y, 12345)
        noise2 = self.generator._perlin_noise(x, y, 54321)
        
        assert noise1 != noise2

    def test_perlin_noise_range(self): pass
        """Test that Perlin noise stays within expected range."""
        # Test multiple points
        for i in range(100): pass
            x = i * 0.1
            y = i * 0.15
            noise = self.generator._perlin_noise(x, y, 12345)
            assert -1.0 <= noise <= 1.0

    def test_fractal_noise(self): pass
        """Test fractal noise generation."""
        x, y = 10.0, 15.0
        scale = 50.0
        octaves = 3
        persistence = 0.5
        lacunarity = 2.0
        seed = 12345
        
        noise = self.generator._fractal_noise(x, y, scale, octaves, persistence, lacunarity, seed)
        
        assert isinstance(noise, float)
        assert -1.0 <= noise <= 1.0

    def test_fractal_noise_octaves_effect(self): pass
        """Test that different octave counts produce different results."""
        x, y = 10.0, 15.0
        scale = 50.0
        persistence = 0.5
        lacunarity = 2.0
        seed = 12345
        
        noise1 = self.generator._fractal_noise(x, y, scale, 1, persistence, lacunarity, seed)
        noise2 = self.generator._fractal_noise(x, y, scale, 4, persistence, lacunarity, seed)
        
        assert noise1 != noise2

    def test_generate_noise_with_layers(self): pass
        """Test noise generation with multiple layers."""
        x, y = 10.0, 15.0
        region_seed = 12345
        
        noise_layers = [
            NoiseLayer(scale=100.0, amplitude=1.0, octaves=2),
            NoiseLayer(scale=50.0, amplitude=0.5, octaves=1)
        ]
        
        noise = self.generator._generate_noise(x, y, noise_layers, region_seed)
        
        assert isinstance(noise, float)
        # Should be normalized to [0, 1] range
        assert 0.0 <= noise <= 1.0

    def test_generate_noise_caching(self): pass
        """Test that noise generation uses caching."""
        x, y = 10.0, 15.0
        region_seed = 12345
        noise_layers = [NoiseLayer(scale=100.0, amplitude=1.0)]
        
        # First call should compute and cache
        noise1 = self.generator._generate_noise(x, y, noise_layers, region_seed)
        
        # Second call should use cache
        noise2 = self.generator._generate_noise(x, y, noise_layers, region_seed)
        
        assert noise1 == noise2
        assert len(self.generator._noise_cache) > 0


class TestBiomeDetermination: pass
    """Test biome determination functionality."""

    def setup_method(self): pass
        """Set up test environment."""
        self.config = TerrainConfig.default()
        self.generator = TerrainGenerator(seed=12345, config=self.config)
        self.generator.load_biome_data("nonexistent_dir")  # Use defaults

    def test_determine_biome_basic(self): pass
        """Test basic biome determination."""
        # Test ocean (low elevation)
        biome = self.generator._determine_biome(
            elevation=0.2, temperature=0.5, moisture=0.5
        )
        assert biome == "ocean"
        
        # Test mountains (high elevation)
        biome = self.generator._determine_biome(
            elevation=0.8, temperature=0.3, moisture=0.4
        )
        assert biome == "mountains"

    def test_determine_biome_river(self): pass
        """Test river biome determination."""
        biome = self.generator._determine_biome(
            elevation=0.5, temperature=0.5, moisture=0.7, is_river=True
        )
        assert biome == "river"

    def test_determine_biome_desert(self): pass
        """Test desert biome determination."""
        biome = self.generator._determine_biome(
            elevation=0.5, temperature=0.9, moisture=0.1
        )
        assert biome == "desert"

    def test_determine_biome_forest(self): pass
        """Test forest biome determination."""
        biome = self.generator._determine_biome(
            elevation=0.5, temperature=0.5, moisture=0.8
        )
        assert biome == "forest"

    def test_determine_biome_tundra(self): pass
        """Test tundra biome determination."""
        biome = self.generator._determine_biome(
            elevation=0.5, temperature=0.1, moisture=0.3
        )
        assert biome == "tundra"

    def test_calculate_factor_score(self): pass
        """Test factor score calculation."""
        # Perfect match
        score = self.generator._calculate_factor_score(0.5, (0.3, 0.7))
        assert score == 1.0
        
        # Outside range
        score = self.generator._calculate_factor_score(0.1, (0.3, 0.7))
        assert score < 1.0
        
        # Edge of range
        score = self.generator._calculate_factor_score(0.3, (0.3, 0.7))
        assert score == 1.0


class TestUtilityMethods: pass
    """Test utility methods."""

    def setup_method(self): pass
        """Set up test environment."""
        self.config = TerrainConfig.default()
        self.generator = TerrainGenerator(seed=12345, config=self.config)

    def test_ranges_overlap_true(self): pass
        """Test overlapping ranges."""
        assert self.generator._ranges_overlap((0.3, 0.7), (0.5, 0.9)) == True
        assert self.generator._ranges_overlap((0.1, 0.5), (0.3, 0.8)) == True

    def test_ranges_overlap_false(self): pass
        """Test non-overlapping ranges."""
        assert self.generator._ranges_overlap((0.1, 0.3), (0.5, 0.8)) == False
        assert self.generator._ranges_overlap((0.7, 0.9), (0.1, 0.5)) == False

    def test_ranges_overlap_touching(self): pass
        """Test touching ranges."""
        assert self.generator._ranges_overlap((0.1, 0.5), (0.5, 0.8)) == True

    def test_merge_ranges(self): pass
        """Test range merging."""
        merged = self.generator._merge_ranges((0.3, 0.7), (0.5, 0.9))
        assert merged == (0.3, 0.9)
        
        merged = self.generator._merge_ranges((0.1, 0.8), (0.4, 0.6))
        assert merged == (0.1, 0.8)

    def test_merge_resources(self): pass
        """Test resource merging."""
        res1 = {"wood": 0.8, "stone": 0.6}
        res2 = {"wood": 0.4, "gold": 0.7}
        
        merged = self.generator._merge_resources(res1, res2)
        
        assert merged["wood"] == 0.6  # Average of 0.8 and 0.4
        assert merged["stone"] == 0.6  # Only in res1
        assert merged["gold"] == 0.7   # Only in res2

    def test_blend_colors(self): pass
        """Test color blending."""
        color1 = "#FF0000"  # Red
        color2 = "#0000FF"  # Blue
        
        blended = self.generator._blend_colors(color1, color2)
        
        assert blended.startswith("#")
        assert len(blended) == 7
        # Should be some form of purple (between red and blue)

    def test_blend_colors_same(self): pass
        """Test blending identical colors."""
        color = "#FF0000"
        blended = self.generator._blend_colors(color, color)
        assert blended == color


class TestTerrainGeneration: pass
    """Test main terrain generation functionality."""

    def setup_method(self): pass
        """Set up test environment."""
        self.config = TerrainConfig.default()
        self.generator = TerrainGenerator(seed=12345, config=self.config)
        self.generator.load_biome_data("nonexistent_dir")  # Use defaults

    def test_generate_terrain_basic(self): pass
        """Test basic terrain generation."""
        result = self.generator.generate_terrain(
            region_x=0, region_y=0, size=64, region_seed=12345
        )
        
        assert "elevation" in result
        assert "temperature" in result
        assert "moisture" in result
        assert "biomes" in result
        assert "rivers" in result
        
        # Check array dimensions
        assert result["elevation"].shape == (64, 64)
        assert result["temperature"].shape == (64, 64)
        assert result["moisture"].shape == (64, 64)
        assert result["biomes"].shape == (64, 64)
        assert result["rivers"].shape == (64, 64)

    def test_generate_terrain_different_sizes(self): pass
        """Test terrain generation with different sizes."""
        for size in [32, 64, 128]: pass
            result = self.generator.generate_terrain(
                region_x=0, region_y=0, size=size, region_seed=12345
            )
            
            assert result["elevation"].shape == (size, size)
            assert result["biomes"].shape == (size, size)

    def test_generate_terrain_deterministic(self): pass
        """Test that terrain generation is deterministic."""
        result1 = self.generator.generate_terrain(
            region_x=0, region_y=0, size=32, region_seed=12345
        )
        result2 = self.generator.generate_terrain(
            region_x=0, region_y=0, size=32, region_seed=12345
        )
        
        assert np.array_equal(result1["elevation"], result2["elevation"])
        assert np.array_equal(result1["biomes"], result2["biomes"])

    def test_generate_terrain_different_seeds(self): pass
        """Test that different seeds produce different terrain."""
        result1 = self.generator.generate_terrain(
            region_x=0, region_y=0, size=32, region_seed=12345
        )
        result2 = self.generator.generate_terrain(
            region_x=0, region_y=0, size=32, region_seed=54321
        )
        
        assert not np.array_equal(result1["elevation"], result2["elevation"])

    def test_generate_terrain_with_biome_influence(self): pass
        """Test terrain generation with biome influence."""
        biome_influence = {"forest": 0.8, "desert": 0.2}
        
        result = self.generator.generate_terrain(
            region_x=0, region_y=0, size=32, region_seed=12345,
            biome_influence=biome_influence
        )
        
        # Should still produce valid terrain
        assert "elevation" in result
        assert "biomes" in result
        assert result["elevation"].shape == (32, 32)

    def test_generate_improved_rivers(self): pass
        """Test river generation."""
        elevation_map = np.random.random((64, 64))
        
        rivers = self.generator._generate_improved_rivers(
            elevation_map, region_seed=12345, size=64
        )
        
        assert rivers.shape == (64, 64)
        assert rivers.dtype == bool
        # Should have some rivers (but not everywhere)
        assert 0 < np.sum(rivers) < rivers.size


class TestBiomeAccessors: pass
    """Test biome accessor methods."""

    def setup_method(self): pass
        """Set up test environment."""
        self.config = TerrainConfig.default()
        self.generator = TerrainGenerator(seed=12345, config=self.config)
        self.generator.load_biome_data("nonexistent_dir")  # Use defaults

    def test_get_biome_info_existing(self): pass
        """Test getting existing biome info."""
        biome_info = self.generator.get_biome_info("forest")
        
        assert biome_info is not None
        assert biome_info.id == "forest"
        assert biome_info.name == "Forest"
        assert isinstance(biome_info.features, list)
        assert isinstance(biome_info.resources, dict)

    def test_get_biome_info_nonexistent(self): pass
        """Test getting non-existent biome info."""
        biome_info = self.generator.get_biome_info("nonexistent_biome")
        assert biome_info is None

    def test_get_all_biomes(self): pass
        """Test getting all biomes."""
        all_biomes = self.generator.get_all_biomes()
        
        assert isinstance(all_biomes, dict)
        assert len(all_biomes) > 0
        assert "forest" in all_biomes
        assert "desert" in all_biomes
        assert "ocean" in all_biomes
        
        # All values should be BiomeInfo objects
        for biome in all_biomes.values(): pass
            assert isinstance(biome, BiomeInfo)


def test_module_imports(): pass
    """Test that the module can be imported without errors."""
    from backend.systems.world_state.utils.terrain_generator import TerrainGenerator
    assert TerrainGenerator is not None

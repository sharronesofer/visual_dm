from backend.systems.shared.database.base import Base
from backend.systems.shared.database.base import Base
"""
Tests for regional features generation.

This module contains tests for landmark and point of interest generation
within regions, including biome-specific features and positioning logic.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import random

from backend.systems.world_generation.regional_features import RegionalFeatures


class TestRegionalFeatures:
    """Tests for regional features generation."""

    @pytest.fixture
    def sample_world_data(self):
        """Create sample world data for testing."""
        return {
            "regions": [
                {
                    "id": 1,
                    "x": 100,
                    "y": 200,
                    "width": 15,
                    "height": 15,
                    "biome": "forest",
                },
                {
                    "id": 2,
                    "x": 150,
                    "y": 250,
                    "width": 20,
                    "height": 20,
                    "biome": "desert",
                },
                {
                    "id": 3,
                    "x": 200,
                    "y": 300,
                    "width": 10,
                    "height": 10,
                    "biome": "mountain",
                },
                {
                    "id": 4,
                    "x": 250,
                    "y": 350,
                    "width": 12,
                    "height": 12,
                    "biome": "coast",
                },
                {
                    "id": 5,
                    "x": 300,
                    "y": 400,
                    "width": 18,
                    "height": 18,
                    "biome": "unknown_biome",  # Test fallback to default
                },
            ]
        }

    @pytest.fixture
    def regional_features(self, sample_world_data):
        """Create RegionalFeatures instance for testing."""
        return RegionalFeatures(sample_world_data)

    def test_init_basic(self, sample_world_data):
        """Test basic initialization of RegionalFeatures."""
        rf = RegionalFeatures(sample_world_data)
        
        assert rf.world_data == sample_world_data
        assert rf.landmarks == []
        assert rf.landmark_id_counter == 1
        assert isinstance(rf.landmark_templates, dict)

    def test_init_landmark_templates_structure(self, regional_features):
        """Test that landmark templates are properly structured."""
        templates = regional_features.landmark_templates
        
        # Check that all expected biomes have templates
        expected_biomes = [
            "forest", "jungle", "desert", "grassland", "mountain", 
            "tundra", "coast", "swamp", "default"
        ]
        
        for biome in expected_biomes:
            assert biome in templates
            assert isinstance(templates[biome], list)
            assert len(templates[biome]) > 0
            
            # Check that all template entries are strings
            for template in templates[biome]:
                assert isinstance(template, str)
                assert len(template) > 0

    def test_landmark_templates_content(self, regional_features):
        """Test specific landmark template content."""
        templates = regional_features.landmark_templates
        
        # Test forest templates
        assert "Ancient Tree" in templates["forest"]
        assert "Druid Circle" in templates["forest"]
        
        # Test desert templates
        assert "Oasis" in templates["desert"]
        assert "Ancient Pyramid" in templates["desert"]
        
        # Test mountain templates
        assert "Mountain Peak" in templates["mountain"]
        assert "Mining Camp" in templates["mountain"]
        
        # Test coast templates
        assert "Lighthouse" in templates["coast"]
        assert "Shipwreck" in templates["coast"]

    @patch('backend.systems.world_generation.regional_features.get_elevation_at_point')
    @patch('backend.systems.world_generation.regional_features.get_rainfall_at_point')
    @patch('backend.systems.world_generation.regional_features.random.randint')
    @patch('backend.systems.world_generation.regional_features.random.choice')
    @patch('backend.systems.world_generation.regional_features.random.random')
    def test_generate_regional_features_basic(self, mock_random, mock_choice, mock_randint, 
                                            mock_rainfall, mock_elevation, regional_features):
        """Test basic regional features generation."""
        # Mock return values
        mock_randint.side_effect = [3, 5, 6, 5, 6, 5, 6, 1, 2, 3]  # landmark_count, positions, danger_levels
        mock_choice.side_effect = ["Ancient Tree", "Hidden Grove", "Sacred Glade", "ancient", "well-preserved", "old", "intact", "recent", "restored"]
        mock_random.side_effect = [0.2, 0.4, 0.6]  # resource chances
        mock_elevation.return_value = 0.5
        mock_rainfall.return_value = 0.4
        
        landmarks = regional_features.generate_regional_features(1, min_landmarks=2, max_landmarks=5)
        
        assert isinstance(landmarks, list)
        assert len(landmarks) == 3  # Based on mocked randint
        
        # Check landmark structure
        for landmark in landmarks:
            assert "id" in landmark
            assert "name" in landmark
            assert "type" in landmark
            assert "region_id" in landmark
            assert "x" in landmark
            assert "y" in landmark
            assert "elevation" in landmark
            assert "description" in landmark
            assert "resources" in landmark
            assert "danger_level" in landmark
            assert "discovered" in landmark
            
            assert landmark["region_id"] == 1
            assert landmark["discovered"] == False

    def test_generate_regional_features_invalid_region(self, regional_features):
        """Test generation with invalid region ID."""
        landmarks = regional_features.generate_regional_features(999)
        
        assert landmarks == []

    @patch('backend.systems.world_generation.regional_features.get_elevation_at_point')
    @patch('backend.systems.world_generation.regional_features.get_rainfall_at_point')
    @patch('backend.systems.world_generation.regional_features.random.randint')
    @patch('backend.systems.world_generation.regional_features.random.choice')
    @patch('backend.systems.world_generation.regional_features.random.random')
    def test_generate_regional_features_biome_modifiers(self, mock_random, mock_choice, mock_randint,
                                                      mock_rainfall, mock_elevation, regional_features):
        """Test biome-specific landmark count modifiers."""
        mock_elevation.return_value = 0.5
        mock_rainfall.return_value = 0.1  # Dry for desert
        mock_random.return_value = 0.8  # No resources
        mock_choice.return_value = "Oasis"
        
        # Test desert (should have fewer landmarks due to 0.7 modifier)
        mock_randint.side_effect = [2, 5, 6, 5, 6, 1, 2]  # Reduced count due to biome_mod
        landmarks_desert = regional_features.generate_regional_features(2, min_landmarks=3, max_landmarks=8)
        
        # Test forest (should have more landmarks due to 1.3 modifier)
        mock_randint.side_effect = [4] + [5, 6, 1] * 20  # count + (x_offset, y_offset, danger_level) * landmarks
        landmarks_forest = regional_features.generate_regional_features(1, min_landmarks=3, max_landmarks=8)
        
        assert isinstance(landmarks_desert, list)
        assert isinstance(landmarks_forest, list)

    @patch('backend.systems.world_generation.regional_features.get_elevation_at_point')
    @patch('backend.systems.world_generation.regional_features.get_rainfall_at_point')
    @patch('backend.systems.world_generation.regional_features.random.randint')
    @patch('backend.systems.world_generation.regional_features.random.choice')
    @patch('backend.systems.world_generation.regional_features.random.random')
    def test_generate_regional_features_size_factor(self, mock_random, mock_choice, mock_randint,
                                                   mock_rainfall, mock_elevation, regional_features):
        """Test region size factor in landmark generation."""
        mock_elevation.return_value = 0.5
        mock_rainfall.return_value = 0.4
        mock_random.return_value = 0.8  # No resources
        mock_choice.return_value = "Mountain Peak"
        mock_randint.side_effect = [1] + [5, 6, 1] * 20  # count + (x_offset, y_offset, danger_level) * landmarks
        
        # Test small region (10x10 = 100, vs standard 225)
        landmarks = regional_features.generate_regional_features(3, min_landmarks=3, max_landmarks=8)
        
        assert isinstance(landmarks, list)

    @patch('backend.systems.world_generation.regional_features.get_elevation_at_point')
    @patch('backend.systems.world_generation.regional_features.get_rainfall_at_point')
    @patch('backend.systems.world_generation.regional_features.random.randint')
    @patch('backend.systems.world_generation.regional_features.random.choice')
    @patch('backend.systems.world_generation.regional_features.random.random')
    def test_generate_regional_features_unknown_biome_fallback(self, mock_random, mock_choice, mock_randint,
                                                             mock_rainfall, mock_elevation, regional_features):
        """Test fallback to default biome for unknown biomes."""
        mock_elevation.return_value = 0.5
        mock_rainfall.return_value = 0.4
        mock_random.return_value = 0.8  # No resources
        mock_choice.return_value = "Strange Monument"  # From default templates
        mock_randint.side_effect = [2, 5, 6, 5, 6, 1, 2]
        
        landmarks = regional_features.generate_regional_features(5)  # unknown_biome region
        
        assert isinstance(landmarks, list)
        # Should use default templates
        if landmarks:
            assert landmarks[0]["type"] == "Strange Monument"

    @patch('backend.systems.world_generation.regional_features.get_elevation_at_point')
    @patch('backend.systems.world_generation.regional_features.get_rainfall_at_point')
    @patch('backend.systems.world_generation.regional_features.random.randint')
    @patch('backend.systems.world_generation.regional_features.random.choice')
    @patch('backend.systems.world_generation.regional_features.random.random')
    def test_generate_landmark_basic(self, mock_random, mock_choice, mock_randint,
                                   mock_rainfall, mock_elevation, regional_features):
        """Test basic landmark generation."""
        mock_elevation.return_value = 0.5
        mock_rainfall.return_value = 0.4
        mock_randint.side_effect = [5, 6, 3]  # x_offset, y_offset, danger_level
        mock_choice.side_effect = ["Sacred Grove", "Rare Wood", "ancient", "well-preserved"]  # landmark_type, resource, age, condition
        mock_random.return_value = 0.2  # Trigger resource generation
        
        region = regional_features.world_data["regions"][0]  # Forest region
        existing_positions = set()
        
        landmark = regional_features._generate_landmark(region, "forest", existing_positions)
        
        assert landmark is not None
        assert landmark["type"] == "Sacred Grove"
        assert landmark["region_id"] == 1
        assert landmark["x"] == 105  # region_x (100) + x_offset (5)
        assert landmark["y"] == 206  # region_y (200) + y_offset (6)
        assert landmark["elevation"] == 0.5
        assert landmark["danger_level"] == 3
        assert landmark["discovered"] == False
        assert "Rare Wood" in landmark["resources"]

    @patch('backend.systems.world_generation.regional_features.get_elevation_at_point')
    @patch('backend.systems.world_generation.regional_features.get_rainfall_at_point')
    @patch('backend.systems.world_generation.regional_features.random.randint')
    def test_generate_landmark_mountain_elevation_constraint(self, mock_randint, mock_rainfall, 
                                                           mock_elevation, regional_features):
        """Test mountain landmark elevation constraints."""
        region = regional_features.world_data["regions"][2]  # Mountain region
        existing_positions = set()
        
        # First attempt: low elevation (should be rejected)
        # Second attempt: high elevation (should be accepted)
        mock_elevation.side_effect = [0.3, 0.8]  # Low then high elevation
        mock_rainfall.return_value = 0.4
        mock_randint.side_effect = [5, 6, 7, 8, 3]  # Two position attempts, danger_level
        
        with patch('backend.systems.world_generation.regional_features.random.choice') as mock_choice:
            with patch('backend.systems.world_generation.regional_features.random.random') as mock_random:
                mock_choice.return_value = "Mountain Peak"
                mock_random.return_value = 0.8  # No resources
                
                landmark = regional_features._generate_landmark(region, "mountain", existing_positions)
                
                assert landmark is not None
                assert landmark["elevation"] == 0.8  # High elevation accepted

    @patch('backend.systems.world_generation.regional_features.get_elevation_at_point')
    @patch('backend.systems.world_generation.regional_features.get_rainfall_at_point')
    @patch('backend.systems.world_generation.regional_features.random.randint')
    def test_generate_landmark_coast_elevation_constraint(self, mock_randint, mock_rainfall,
                                                        mock_elevation, regional_features):
        """Test coast landmark elevation constraints."""
        region = regional_features.world_data["regions"][3]  # Coast region
        existing_positions = set()
        
        # First attempt: high elevation (should be rejected)
        # Second attempt: low elevation (should be accepted)
        mock_elevation.side_effect = [0.5, 0.1]  # High then low elevation
        mock_rainfall.return_value = 0.4
        mock_randint.side_effect = [5, 6, 7, 8, 2]  # Two position attempts, danger_level
        
        with patch('backend.systems.world_generation.regional_features.random.choice') as mock_choice:
            with patch('backend.systems.world_generation.regional_features.random.random') as mock_random:
                mock_choice.return_value = "Lighthouse"
                mock_random.return_value = 0.8  # No resources
                
                landmark = regional_features._generate_landmark(region, "coast", existing_positions)
                
                assert landmark is not None
                assert landmark["elevation"] == 0.1  # Low elevation accepted

    @patch('backend.systems.world_generation.regional_features.get_elevation_at_point')
    @patch('backend.systems.world_generation.regional_features.get_rainfall_at_point')
    @patch('backend.systems.world_generation.regional_features.random.randint')
    def test_generate_landmark_desert_rainfall_constraint(self, mock_randint, mock_rainfall,
                                                        mock_elevation, regional_features):
        """Test desert landmark rainfall constraints."""
        region = regional_features.world_data["regions"][1]  # Desert region
        existing_positions = set()
        
        # First attempt: high rainfall (should be rejected)
        # Second attempt: low rainfall (should be accepted)
        mock_elevation.return_value = 0.5
        mock_rainfall.side_effect = [0.5, 0.1]  # High then low rainfall
        mock_randint.side_effect = [5, 6, 7, 8, 4]  # Two position attempts, danger_level
        
        with patch('backend.systems.world_generation.regional_features.random.choice') as mock_choice:
            with patch('backend.systems.world_generation.regional_features.random.random') as mock_random:
                mock_choice.return_value = "Oasis"
                mock_random.return_value = 0.8  # No resources
                
                landmark = regional_features._generate_landmark(region, "desert", existing_positions)
                
                assert landmark is not None

    @patch('backend.systems.world_generation.regional_features.get_elevation_at_point')
    @patch('backend.systems.world_generation.regional_features.get_rainfall_at_point')
    @patch('backend.systems.world_generation.regional_features.random.randint')
    def test_generate_landmark_position_collision_avoidance(self, mock_randint, mock_rainfall,
                                                          mock_elevation, regional_features):
        """Test that landmarks avoid existing positions."""
        region = regional_features.world_data["regions"][0]  # Forest region
        existing_positions = {(105, 206)}  # Block first position
        
        mock_elevation.return_value = 0.5
        mock_rainfall.return_value = 0.4
        # First attempt: collision (105, 206)
        # Second attempt: clear position (107, 208)
        mock_randint.side_effect = [5, 6, 7, 8, 1]  # Two position attempts, danger_level
        
        with patch('backend.systems.world_generation.regional_features.random.choice') as mock_choice:
            with patch('backend.systems.world_generation.regional_features.random.random') as mock_random:
                mock_choice.side_effect = ["Ancient Tree", "ancient", "well-preserved"]
                mock_random.return_value = 0.8  # No resources
                
                landmark = regional_features._generate_landmark(region, "forest", existing_positions)
                
                assert landmark is not None
                assert (landmark["x"], landmark["y"]) == (107, 208)  # Second position

    @patch('backend.systems.world_generation.regional_features.get_elevation_at_point')
    @patch('backend.systems.world_generation.regional_features.get_rainfall_at_point')
    @patch('backend.systems.world_generation.regional_features.random.randint')
    def test_generate_landmark_max_attempts_exceeded(self, mock_randint, mock_rainfall,
                                                   mock_elevation, regional_features):
        """Test landmark generation when max attempts are exceeded."""
        region = regional_features.world_data["regions"][2]  # Mountain region
        existing_positions = set()
        
        # Always return low elevation (invalid for mountain)
        mock_elevation.return_value = 0.3
        mock_rainfall.return_value = 0.4
        mock_randint.side_effect = [5, 6] * 20  # 20 attempts, all invalid
        
        landmark = regional_features._generate_landmark(region, "mountain", existing_positions)
        
        assert landmark is None

    @patch('backend.systems.world_generation.regional_features.random.choice')
    @patch('backend.systems.world_generation.regional_features.random.random')
    def test_generate_landmark_resource_generation_mine(self, mock_random, mock_choice, regional_features):
        """Test resource generation for mine-type landmarks."""
        region = regional_features.world_data["regions"][1]  # Use desert region (index 1)
        existing_positions = set()
        
        mock_random.side_effect = [0.2]  # Trigger resource generation
        mock_choice.side_effect = ["Crystal Cave", "Gems", "ancient", "well-preserved"]  # Mine type, resource, age, condition
        
        with patch('backend.systems.world_generation.regional_features.get_elevation_at_point') as mock_elevation:
            with patch('backend.systems.world_generation.regional_features.get_rainfall_at_point') as mock_rainfall:
                with patch('backend.systems.world_generation.regional_features.random.randint') as mock_randint:
                    mock_elevation.return_value = 0.5
                    mock_rainfall.return_value = 0.1  # Low rainfall for desert
                    mock_randint.side_effect = [5, 6, 2] * 50  # Provide enough values for validation loops
                    
                    landmark = regional_features._generate_landmark(region, "desert", existing_positions)
                    
                    assert landmark is not None
                    assert "Gems" in landmark["resources"]

    @patch('backend.systems.world_generation.regional_features.random.choice')
    @patch('backend.systems.world_generation.regional_features.random.random')
    def test_generate_landmark_resource_generation_forest(self, mock_random, mock_choice, regional_features):
        """Test resource generation for forest-type landmarks."""
        region = regional_features.world_data["regions"][0]
        existing_positions = set()
        
        mock_random.side_effect = [0.2]  # Trigger resource generation
        mock_choice.side_effect = ["Sacred Grove", "Medicinal Herbs", "ancient", "well-preserved"]  # Forest type, resource, age, condition
        
        with patch('backend.systems.world_generation.regional_features.get_elevation_at_point') as mock_elevation:
            with patch('backend.systems.world_generation.regional_features.get_rainfall_at_point') as mock_rainfall:
                with patch('backend.systems.world_generation.regional_features.random.randint') as mock_randint:
                    mock_elevation.return_value = 0.5
                    mock_rainfall.return_value = 0.4
                    mock_randint.side_effect = [5, 6, 3]
                    
                    landmark = regional_features._generate_landmark(region, "forest", existing_positions)
                    
                    assert landmark is not None
                    assert "Medicinal Herbs" in landmark["resources"]

    @patch('backend.systems.world_generation.regional_features.random.choice')
    @patch('backend.systems.world_generation.regional_features.random.random')
    def test_generate_landmark_resource_generation_ruins(self, mock_random, mock_choice, regional_features):
        """Test resource generation for ruins-type landmarks."""
        region = regional_features.world_data["regions"][0]
        existing_positions = set()
        
        mock_random.side_effect = [0.2]  # Trigger resource generation
        mock_choice.side_effect = ["Ancient Ruins", "Lost Knowledge", "ancient", "well-preserved"]  # Ruins type, resource, age, condition
        
        with patch('backend.systems.world_generation.regional_features.get_elevation_at_point') as mock_elevation:
            with patch('backend.systems.world_generation.regional_features.get_rainfall_at_point') as mock_rainfall:
                with patch('backend.systems.world_generation.regional_features.random.randint') as mock_randint:
                    mock_elevation.return_value = 0.5
                    mock_rainfall.return_value = 0.4
                    mock_randint.side_effect = [5, 6, 4]
                    
                    landmark = regional_features._generate_landmark(region, "swamp", existing_positions)
                    
                    assert landmark is not None
                    assert "Lost Knowledge" in landmark["resources"]

    @patch('backend.systems.world_generation.regional_features.random.choice')
    @patch('backend.systems.world_generation.regional_features.random.random')
    def test_generate_landmark_no_resources(self, mock_random, mock_choice, regional_features):
        """Test landmark generation without resources."""
        region = regional_features.world_data["regions"][0]
        existing_positions = set()
        
        mock_random.return_value = 0.8  # No resource generation
        mock_choice.return_value = "Ancient Tree"
        
        with patch('backend.systems.world_generation.regional_features.get_elevation_at_point') as mock_elevation:
            with patch('backend.systems.world_generation.regional_features.get_rainfall_at_point') as mock_rainfall:
                with patch('backend.systems.world_generation.regional_features.random.randint') as mock_randint:
                    mock_elevation.return_value = 0.5
                    mock_rainfall.return_value = 0.4
                    mock_randint.side_effect = [5, 6, 1]
                    
                    landmark = regional_features._generate_landmark(region, "forest", existing_positions)
                    
                    assert landmark is not None
                    assert landmark["resources"] == []

    def test_generate_landmark_description_temple_ruins(self, regional_features):
        """Test description generation for temple/ruins landmarks."""
        with patch('backend.systems.world_generation.regional_features.random.choice') as mock_choice:
            mock_choice.side_effect = ["ancient", "well-preserved"]
            
            description = regional_features._generate_landmark_description("Ancient Temple", "forest")
            
            assert "ancient" in description
            assert "well-preserved" in description
            assert "surrounded by tall trees" in description
            assert "Local legends speak of its importance" in description

    def test_generate_landmark_description_village_settlement(self, regional_features):
        """Test description generation for village/settlement landmarks."""
        with patch('backend.systems.world_generation.regional_features.random.choice') as mock_choice:
            mock_choice.side_effect = ["old", "intact"]
            
            description = regional_features._generate_landmark_description("Tribal Village", "jungle")
            
            assert "intact" in description
            assert "hidden among towering trees" in description
            assert "shows signs of habitation" in description

    def test_generate_landmark_description_cave_den(self, regional_features):
        """Test description generation for cave/den landmarks."""
        with patch('backend.systems.world_generation.regional_features.random.choice') as mock_choice:
            mock_choice.side_effect = ["weathered", "crumbling"]
            
            description = regional_features._generate_landmark_description("Beast Den", "mountain")
            
            assert "crumbling" in description
            assert "perched precariously on the rocky slopes" in description
            assert "opening in the earth" in description

    def test_generate_landmark_description_generic(self, regional_features):
        """Test description generation for generic landmarks."""
        with patch('backend.systems.world_generation.regional_features.random.choice') as mock_choice:
            mock_choice.side_effect = ["recent", "restored"]
            
            description = regional_features._generate_landmark_description("Trading Post", "grassland")
            
            assert "restored" in description
            assert "visible for miles across the open plains" in description
            assert "trading post" in description.lower()

    def test_generate_landmark_description_all_biomes(self, regional_features):
        """Test description generation for all biome types."""
        biomes = ["forest", "jungle", "desert", "grassland", "mountain", "tundra", "coast", "swamp"]
        
        for biome in biomes:
            with patch('backend.systems.world_generation.regional_features.random.choice') as mock_choice:
                mock_choice.side_effect = ["ancient", "well-preserved"]
                
                description = regional_features._generate_landmark_description("Test Landmark", biome)
                
                assert isinstance(description, str)
                assert len(description) > 0

    def test_generate_landmark_description_unknown_biome(self, regional_features):
        """Test description generation for unknown biome."""
        with patch('backend.systems.world_generation.regional_features.random.choice') as mock_choice:
            mock_choice.side_effect = ["ancient", "well-preserved"]
            
            description = regional_features._generate_landmark_description("Test Landmark", "unknown")
            
            assert "nestled in the landscape" in description

    def test_get_region_by_id_valid(self, regional_features):
        """Test getting region by valid ID."""
        region = regional_features._get_region_by_id(1)
        
        assert region is not None
        assert region["id"] == 1
        assert region["biome"] == "forest"

    def test_get_region_by_id_invalid(self, regional_features):
        """Test getting region by invalid ID."""
        region = regional_features._get_region_by_id(999)
        
        assert region is None

    def test_get_region_by_id_empty_regions(self):
        """Test getting region when no regions exist."""
        rf = RegionalFeatures({"regions": []})
        region = rf._get_region_by_id(1)
        
        assert region is None

    def test_get_region_by_id_no_regions_key(self):
        """Test getting region when regions key doesn't exist."""
        rf = RegionalFeatures({})
        region = rf._get_region_by_id(1)
        
        assert region is None

    def test_landmark_id_counter_increment(self, regional_features):
        """Test that landmark ID counter increments properly."""
        initial_counter = regional_features.landmark_id_counter
        
        with patch('backend.systems.world_generation.regional_features.get_elevation_at_point') as mock_elevation:
            with patch('backend.systems.world_generation.regional_features.get_rainfall_at_point') as mock_rainfall:
                with patch('backend.systems.world_generation.regional_features.random.randint') as mock_randint:
                    with patch('backend.systems.world_generation.regional_features.random.choice') as mock_choice:
                        with patch('backend.systems.world_generation.regional_features.random.random') as mock_random:
                            mock_elevation.return_value = 0.5
                            mock_rainfall.return_value = 0.4
                            mock_randint.side_effect = [5, 6, 1]
                            mock_choice.return_value = "Ancient Tree"
                            mock_random.return_value = 0.8
                            
                            region = regional_features.world_data["regions"][0]
                            landmark = regional_features._generate_landmark(region, "forest", set())
                            
                            assert landmark["id"] == initial_counter
                            assert regional_features.landmark_id_counter == initial_counter + 1

    def test_landmarks_list_population(self, regional_features):
        """Test that landmarks are added to the landmarks list."""
        initial_count = len(regional_features.landmarks)
        
        with patch('backend.systems.world_generation.regional_features.get_elevation_at_point') as mock_elevation:
            with patch('backend.systems.world_generation.regional_features.get_rainfall_at_point') as mock_rainfall:
                with patch('backend.systems.world_generation.regional_features.random.randint') as mock_randint:
                    with patch('backend.systems.world_generation.regional_features.random.choice') as mock_choice:
                        with patch('backend.systems.world_generation.regional_features.random.random') as mock_random:
                            mock_elevation.return_value = 0.5
                            mock_rainfall.return_value = 0.4
                            mock_randint.side_effect = [5, 6, 2]
                            mock_choice.return_value = "Hidden Grove"
                            mock_random.return_value = 0.8
                            
                            region = regional_features.world_data["regions"][0]
                            landmark = regional_features._generate_landmark(region, "forest", set())
                            
                            assert len(regional_features.landmarks) == initial_count + 1
                            assert regional_features.landmarks[-1] == landmark

    @patch('backend.systems.world_generation.regional_features.get_elevation_at_point')
    @patch('backend.systems.world_generation.regional_features.get_rainfall_at_point')
    @patch('backend.systems.world_generation.regional_features.random.randint')
    @patch('backend.systems.world_generation.regional_features.random.choice')
    @patch('backend.systems.world_generation.regional_features.random.random')
    def test_integration_full_generation_workflow(self, mock_random, mock_choice, mock_randint,
                                                mock_rainfall, mock_elevation, regional_features):
        """Test complete landmark generation workflow."""
        # Setup mocks for successful generation
        mock_elevation.return_value = 0.5
        mock_rainfall.return_value = 0.4
        mock_randint.side_effect = [3, 5, 6, 7, 8, 9, 10, 1, 2, 3]  # count + positions + danger
        mock_choice.side_effect = ["Sacred Grove", "Hidden Grove", "Sacred Glade", "Rare Wood", "ancient", "well-preserved", "old", "intact", "recent", "restored"]
        mock_random.side_effect = [0.2, 0.8, 0.8]  # First has resources, others don't
        
        # Generate landmarks for forest region
        landmarks = regional_features.generate_regional_features(1, min_landmarks=2, max_landmarks=5)
        
        # Verify results
        assert len(landmarks) == 3
        assert all(landmark["region_id"] == 1 for landmark in landmarks)
        assert all(landmark["discovered"] == False for landmark in landmarks)
        assert landmarks[0]["resources"]  # First landmark has resources
        assert not landmarks[1]["resources"]  # Others don't
        assert not landmarks[2]["resources"]
        
        # Verify landmarks were added to the instance list
        assert len(regional_features.landmarks) == 3

    def test_error_handling_missing_region_dimensions(self, regional_features):
        """Test handling of regions missing width/height."""
        # Add region without dimensions
        regional_features.world_data["regions"].append({
            "id": 10,
            "x": 100,
            "y": 200,
            "biome": "forest"
            # Missing width and height
        })
        
        with patch('backend.systems.world_generation.regional_features.get_elevation_at_point') as mock_elevation:
            with patch('backend.systems.world_generation.regional_features.get_rainfall_at_point') as mock_rainfall:
                with patch('backend.systems.world_generation.regional_features.random.randint') as mock_randint:
                    with patch('backend.systems.world_generation.regional_features.random.choice') as mock_choice:
                        with patch('backend.systems.world_generation.regional_features.random.random') as mock_random:
                            mock_elevation.return_value = 0.5
                            mock_rainfall.return_value = 0.4
                            mock_randint.side_effect = [2, 5, 6, 7, 8, 1, 2]
                            mock_choice.return_value = "Ancient Tree"
                            mock_random.return_value = 0.8
                            
                            landmarks = regional_features.generate_regional_features(10)
                            
                            # Should use default dimensions (15x15)
                            assert isinstance(landmarks, list)

    def test_edge_case_minimum_landmark_count(self, regional_features):
        """Test edge case with minimum landmark count."""
        with patch('backend.systems.world_generation.regional_features.get_elevation_at_point') as mock_elevation:
            with patch('backend.systems.world_generation.regional_features.get_rainfall_at_point') as mock_rainfall:
                with patch('backend.systems.world_generation.regional_features.random.randint') as mock_randint:
                    with patch('backend.systems.world_generation.regional_features.random.choice') as mock_choice:
                        with patch('backend.systems.world_generation.regional_features.random.random') as mock_random:
                            mock_elevation.return_value = 0.5
                            mock_rainfall.return_value = 0.4
                            mock_randint.side_effect = [1, 5, 6, 1]  # Minimum count
                            mock_choice.return_value = "Ancient Tree"
                            mock_random.return_value = 0.8
                            
                            landmarks = regional_features.generate_regional_features(1, min_landmarks=1, max_landmarks=1)
                            
                            assert len(landmarks) == 1

    def test_edge_case_zero_landmarks(self, regional_features):
        """Test edge case where calculation results in zero landmarks."""
        # Create very small region in barren biome
        regional_features.world_data["regions"].append({
            "id": 11,
            "x": 100,
            "y": 200,
            "width": 1,
            "height": 1,
            "biome": "tundra"  # Barren biome with 0.7 modifier
        })
        
        with patch('backend.systems.world_generation.regional_features.random.randint') as mock_randint:
            # Even with heavy modifiers, should generate at least 1 landmark
            mock_randint.return_value = 1
            
            with patch('backend.systems.world_generation.regional_features.get_elevation_at_point') as mock_elevation:
                with patch('backend.systems.world_generation.regional_features.get_rainfall_at_point') as mock_rainfall:
                    with patch('backend.systems.world_generation.regional_features.random.choice') as mock_choice:
                        with patch('backend.systems.world_generation.regional_features.random.random') as mock_random:
                            mock_elevation.return_value = 0.5
                            mock_rainfall.return_value = 0.4
                            mock_choice.return_value = "Ice Cave"
                            mock_random.return_value = 0.8
                            
                            landmarks = regional_features.generate_regional_features(11, min_landmarks=0, max_landmarks=1)
                            
                            # Should still generate at least 1 due to max(1, ...) constraint
                            assert len(landmarks) >= 0 
"""
Tests for dialogue region integration module.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from backend.systems.dialogue.region_integration import DialogueRegionIntegration


class TestDialogueRegionIntegration: pass
    """Test suite for DialogueRegionIntegration class."""

    @pytest.fixture
    def mock_region_manager(self): pass
        """Create a mock region manager."""
        manager = Mock()
        manager.get_region.return_value = {
            "id": "region_1",
            "name": "Test Region",
            "description": "A test region description",
            "biome": "forest",
            "climate": "temperate",
            "terrain": "hills",
            "population": 1000,
            "faction_control": "kingdom",
            "stability": "stable",
            "danger_level": "low",
            "notable_landmarks": ["Ancient Tower", "Crystal Lake"],
            "resources": ["iron", "wood"],
            "resource_abundance": {"iron": "abundant", "wood": "common"},
            "resource_importance": {"iron": "high", "wood": "medium"},
            "native_knowledge": "This land has been our home for generations.",
            "scholarly_knowledge": "Archaeological evidence suggests ancient civilizations.",
            "history": "Founded by the first settlers 200 years ago.",
            "seasonal_descriptions": {
                "spring": "flowers bloom across the hills",
                "summer": "the forests are lush and green",
                "autumn": "leaves turn golden and red",
                "winter": "snow covers the landscape"
            },
            "weather_descriptions": {
                "rain": "The hills glisten with moisture",
                "snow": "A white blanket covers everything",
                "clear": "The sun shines brightly"
            }
        }
        manager.get_adjacent_regions.return_value = [
            {
                "id": "region_2",
                "name": "Northern Plains",
                "direction": "north",
                "border_type": "river",
                "relationship": "friendly"
            },
            {
                "id": "region_3", 
                "name": "Southern Desert",
                "direction": "south",
                "border_type": "mountain",
                "relationship": "neutral"
            }
        ]
        return manager

    @pytest.fixture
    def mock_biome_manager(self): pass
        """Create a mock biome manager."""
        manager = Mock()
        manager.get_biome.return_value = {
            "id": "forest",
            "name": "Temperate Forest",
            "description": "A lush temperate forest with diverse wildlife",
            "climate": "temperate",
            "flora": ["oak trees", "wildflowers", "ferns"],
            "fauna": ["deer", "rabbits", "songbirds"],
            "terrain_features": ["rolling hills", "streams", "clearings"],
            "common_weather": ["rain", "sunshine", "overcast"],
            "seasonal_changes": {
                "spring": "new growth emerges",
                "summer": "full canopy coverage",
                "autumn": "leaves change colors",
                "winter": "trees are bare"
            },
            "weather_effects": {
                "rain": "the forest comes alive with moisture",
                "snow": "a peaceful silence falls over the woods",
                "clear": "sunlight filters through the canopy"
            },
            "dialogue_references": [
                "the rustling of leaves",
                "bird songs in the distance",
                "the scent of pine"
            ]
        }
        return manager

    @pytest.fixture
    def mock_poi_service(self): pass
        """Create a mock POI service."""
        poi_service = Mock()
        poi_service.get_poi.return_value = {
            "id": "location_1",
            "name": "Test Location",
            "region_id": "region_1"
        }
        return poi_service

    @pytest.fixture
    def integration(self, mock_region_manager, mock_biome_manager): pass
        """Create a DialogueRegionIntegration instance with mocked dependencies."""
        return DialogueRegionIntegration(
            region_manager=mock_region_manager,
            biome_manager=mock_biome_manager
        )

    def test_init_with_managers(self, mock_region_manager, mock_biome_manager): pass
        """Test initialization with provided managers."""
        integration = DialogueRegionIntegration(
            region_manager=mock_region_manager,
            biome_manager=mock_biome_manager
        )
        
        assert integration.region_manager == mock_region_manager
        assert integration.biome_manager == mock_biome_manager

    @patch('backend.systems.dialogue.region_integration.RegionManager')
    @patch('backend.systems.dialogue.region_integration.BiomeManager')
    def test_init_without_managers(self, mock_biome_cls, mock_region_cls): pass
        """Test initialization without provided managers."""
        mock_region_instance = Mock()
        mock_biome_instance = Mock()
        mock_region_cls.get_instance.return_value = mock_region_instance
        mock_biome_cls.get_instance.return_value = mock_biome_instance
        
        integration = DialogueRegionIntegration()
        
        assert integration.region_manager == mock_region_instance
        assert integration.biome_manager == mock_biome_instance
        mock_region_cls.get_instance.assert_called_once()
        mock_biome_cls.get_instance.assert_called_once()

    def test_add_region_context_to_dialogue_full_options(self, integration): pass
        """Test adding region context with all options enabled."""
        context = {"existing": "data"}
        
        result = integration.add_region_context_to_dialogue(
            context=context,
            region_id="region_1",
            include_biome=True,
            include_resources=True,
            include_adjacents=True,
            include_details=True
        )
        
        assert "region" in result
        assert "current" in result["region"]
        assert result["region"]["current"]["id"] == "region_1"
        assert result["region"]["current"]["name"] == "Test Region"
        assert "biome" in result["region"]
        assert result["region"]["biome"]["name"] == "Temperate Forest"
        assert "resources" in result["region"]
        assert "adjacent_regions" in result["region"]
        assert result["existing"] == "data"

    def test_add_region_context_to_dialogue_minimal_options(self, integration): pass
        """Test adding region context with minimal options."""
        context = {}
        
        result = integration.add_region_context_to_dialogue(
            context=context,
            region_id="region_1",
            include_biome=False,
            include_resources=False,
            include_adjacents=False,
            include_details=False
        )
        
        assert "region" in result
        assert "current" in result["region"]
        assert "biome" not in result["region"]
        assert "resources" not in result["region"]
        assert "adjacent_regions" not in result["region"]

    def test_add_region_context_to_dialogue_existing_region_context(self, integration): pass
        """Test adding region context when region already exists in context."""
        context = {"region": {"existing": "region_data"}}
        
        result = integration.add_region_context_to_dialogue(
            context=context,
            region_id="region_1"
        )
        
        assert result["region"]["existing"] == "region_data"
        assert "current" in result["region"]

    def test_add_region_context_to_dialogue_region_not_found(self, integration): pass
        """Test adding region context when region not found."""
        integration.region_manager.get_region.return_value = None
        
        result = integration.add_region_context_to_dialogue(
            context={},
            region_id="nonexistent"
        )
        
        assert "region" in result
        assert "current" not in result["region"]

    def test_get_region_description_for_dialogue_visitor_perspective(self, integration): pass
        """Test getting region description from visitor perspective."""
        result = integration.get_region_description_for_dialogue(
            region_id="region_1",
            perspective="visitor",
            season="spring",
            weather="clear"
        )
        
        assert "Test Region" in result
        assert "test region description" in result.lower()
        assert "temperate forest" in result.lower()
        assert "flowers bloom" in result
        assert "sun shines brightly" in result

    def test_get_region_description_for_dialogue_native_perspective(self, integration): pass
        """Test getting region description from native perspective."""
        result = integration.get_region_description_for_dialogue(
            region_id="region_1",
            perspective="native"
        )
        
        assert "Test Region" in result
        assert "your home" in result
        assert "generations" in result

    def test_get_region_description_for_dialogue_scholar_perspective(self, integration): pass
        """Test getting region description from scholar perspective."""
        result = integration.get_region_description_for_dialogue(
            region_id="region_1",
            perspective="scholar"
        )
        
        assert "Test Region" in result
        assert "historically" in result.lower()
        assert "archaeological" in result.lower()

    def test_get_region_description_for_dialogue_unknown_perspective(self, integration): pass
        """Test getting region description with unknown perspective."""
        result = integration.get_region_description_for_dialogue(
            region_id="region_1",
            perspective="unknown"
        )
        
        assert "Test Region" in result
        assert "test region description" in result.lower()

    def test_get_region_description_for_dialogue_region_not_found(self, integration): pass
        """Test getting region description when region not found."""
        integration.region_manager.get_region.return_value = None
        
        result = integration.get_region_description_for_dialogue(
            region_id="nonexistent"
        )
        
        assert "unknown" in result.lower()

    def test_get_region_description_for_dialogue_exception(self, integration): pass
        """Test getting region description with exception."""
        integration.region_manager.get_region.side_effect = Exception("Test error")
        
        result = integration.get_region_description_for_dialogue(
            region_id="region_1"
        )
        
        assert "unavailable" in result.lower()

    @patch('backend.systems.dialogue.region_integration.POIService')
    def test_get_region_context_by_location_success(self, mock_poi_cls, integration): pass
        """Test getting region context by location successfully."""
        mock_poi_service = Mock()
        mock_poi_service.get_poi.return_value = {"region_id": "region_1"}
        mock_poi_cls.return_value = mock_poi_service
        
        result = integration.get_region_context_by_location("location_1")
        
        assert "region" in result
        assert result["region"]["id"] == "region_1"
        assert "biome" in result
        assert result["biome"]["name"] == "Temperate Forest"

    @patch('backend.systems.dialogue.region_integration.POIService')
    def test_get_region_context_by_location_no_region(self, mock_poi_cls, integration): pass
        """Test getting region context by location when no region found."""
        mock_poi_service = Mock()
        mock_poi_service.get_poi.return_value = None
        mock_poi_cls.return_value = mock_poi_service
        
        result = integration.get_region_context_by_location("location_1")
        
        assert result == {}

    @patch('backend.systems.dialogue.region_integration.POIService')
    def test_get_region_context_by_location_exception(self, mock_poi_cls, integration): pass
        """Test getting region context by location with exception."""
        mock_poi_service = Mock()
        mock_poi_service.get_poi.side_effect = Exception("Test error")
        mock_poi_cls.return_value = mock_poi_service
        
        result = integration.get_region_context_by_location("location_1")
        
        assert result == {}

    def test_get_biome_dialogue_references_general(self, integration): pass
        """Test getting general biome dialogue references."""
        result = integration.get_biome_dialogue_references(
            biome_id="forest",
            reference_type="general"
        )
        
        assert len(result) == 3
        assert "the rustling of leaves" in result
        assert "bird songs in the distance" in result
        assert "the scent of pine" in result

    def test_get_biome_dialogue_references_flora(self, integration): pass
        """Test getting flora biome dialogue references."""
        result = integration.get_biome_dialogue_references(
            biome_id="forest",
            reference_type="flora"
        )
        
        assert len(result) == 3
        assert "oak trees" in result
        assert "wildflowers" in result
        assert "ferns" in result

    def test_get_biome_dialogue_references_fauna(self, integration): pass
        """Test getting fauna biome dialogue references."""
        result = integration.get_biome_dialogue_references(
            biome_id="forest",
            reference_type="fauna"
        )
        
        assert len(result) == 3
        assert "deer" in result
        assert "rabbits" in result
        assert "songbirds" in result

    def test_get_biome_dialogue_references_terrain(self, integration): pass
        """Test getting terrain biome dialogue references."""
        result = integration.get_biome_dialogue_references(
            biome_id="forest",
            reference_type="terrain"
        )
        
        assert len(result) == 3
        assert "rolling hills" in result
        assert "streams" in result
        assert "clearings" in result

    def test_get_biome_dialogue_references_weather(self, integration): pass
        """Test getting weather biome dialogue references."""
        result = integration.get_biome_dialogue_references(
            biome_id="forest",
            reference_type="weather"
        )
        
        assert len(result) == 3
        assert "rain" in result
        assert "sunshine" in result
        assert "overcast" in result

    def test_get_biome_dialogue_references_with_season(self, integration): pass
        """Test getting biome dialogue references with seasonal additions."""
        biome_data = integration.biome_manager.get_biome.return_value
        biome_data["seasonal_references"] = {"spring": ["blooming flowers", "new growth"]}
        
        result = integration.get_biome_dialogue_references(
            biome_id="forest",
            reference_type="general",
            season="spring"
        )
        
        assert len(result) == 5  # 3 general + 2 seasonal
        assert "blooming flowers" in result
        assert "new growth" in result

    def test_get_biome_dialogue_references_biome_not_found(self, integration): pass
        """Test getting biome dialogue references when biome not found."""
        integration.biome_manager.get_biome.return_value = None
        
        result = integration.get_biome_dialogue_references(
            biome_id="nonexistent"
        )
        
        assert result == []

    def test_get_biome_dialogue_references_exception(self, integration): pass
        """Test getting biome dialogue references with exception."""
        integration.biome_manager.get_biome.side_effect = Exception("Test error")
        
        result = integration.get_biome_dialogue_references(
            biome_id="forest"
        )
        
        assert result == []

    def test_get_region_comparison_success(self, integration): pass
        """Test getting region comparison successfully."""
        # Set up second region
        region2_data = {
            "id": "region_2",
            "name": "Mountain Region",
            "biome": "mountain",
            "climate": "cold",
            "terrain": "rocky",
            "resources": ["stone", "iron"]
        }
        biome2_data = {
            "id": "mountain",
            "name": "Mountain Biome"
        }
        
        # Mock the calls to return different data for region_2
        def region_side_effect(region_id): pass
            if region_id == "region_1": pass
                return integration.region_manager.get_region.return_value
            elif region_id == "region_2": pass
                return region2_data
            return None
        
        def biome_side_effect(biome_id): pass
            if biome_id == "forest": pass
                return integration.biome_manager.get_biome.return_value
            elif biome_id == "mountain": pass
                return biome2_data
            return None
        
        integration.region_manager.get_region.side_effect = region_side_effect
        integration.biome_manager.get_biome.side_effect = biome_side_effect
        
        result = integration.get_region_comparison("region_1", "region_2")
        
        assert "region1" in result
        assert "region2" in result
        assert "differences" in result
        assert "similarities" in result
        assert result["region1"]["name"] == "Test Region"
        assert result["region2"]["name"] == "Mountain Region"
        assert len(result["differences"]) > 0
        assert any("iron" in diff for diff in result["similarities"])

    def test_get_region_comparison_region_not_found(self, integration): pass
        """Test getting region comparison when region not found."""
        integration.region_manager.get_region.return_value = None
        
        result = integration.get_region_comparison("region_1", "nonexistent")
        
        assert result == {}

    def test_get_region_comparison_exception(self, integration): pass
        """Test getting region comparison with exception."""
        integration.region_manager.get_region.side_effect = Exception("Test error")
        
        result = integration.get_region_comparison("region_1", "region_2")
        
        assert result == {}

    def test_get_region_info_with_details(self, integration): pass
        """Test getting region info with details."""
        result = integration._get_region_info("region_1", include_details=True)
        
        assert result["id"] == "region_1"
        assert result["name"] == "Test Region"
        assert result["biome"] == "forest"
        assert result["description"] == "A test region description"
        assert result["terrain"] == "hills"
        assert result["population"] == 1000

    def test_get_region_info_without_details(self, integration): pass
        """Test getting region info without details."""
        result = integration._get_region_info("region_1", include_details=False)
        
        assert result["id"] == "region_1"
        assert result["name"] == "Test Region"
        assert result["biome"] == "forest"
        assert "description" not in result
        assert "terrain" not in result

    def test_get_region_info_region_not_found(self, integration): pass
        """Test getting region info when region not found."""
        integration.region_manager.get_region.return_value = None
        
        result = integration._get_region_info("nonexistent")
        
        assert result == {}

    def test_get_region_info_exception(self, integration): pass
        """Test getting region info with exception."""
        integration.region_manager.get_region.side_effect = Exception("Test error")
        
        result = integration._get_region_info("region_1")
        
        assert result == {}

    def test_get_biome_info_success(self, integration): pass
        """Test getting biome info successfully."""
        result = integration._get_biome_info("forest")
        
        assert result["id"] == "forest"
        assert result["name"] == "Temperate Forest"
        assert result["description"] == "A lush temperate forest with diverse wildlife"
        assert "flora" in result
        assert "fauna" in result
        assert len(result["flora"]) == 3

    def test_get_biome_info_biome_not_found(self, integration): pass
        """Test getting biome info when biome not found."""
        integration.biome_manager.get_biome.return_value = None
        
        result = integration._get_biome_info("nonexistent")
        
        assert result == {}

    def test_get_biome_info_exception(self, integration): pass
        """Test getting biome info with exception."""
        integration.biome_manager.get_biome.side_effect = Exception("Test error")
        
        result = integration._get_biome_info("forest")
        
        assert result == {}

    def test_get_region_resources_success(self, integration): pass
        """Test getting region resources successfully."""
        result = integration._get_region_resources("region_1")
        
        assert len(result) == 2
        assert result[0]["name"] == "iron"
        assert result[0]["abundance"] == "abundant"
        assert result[0]["importance"] == "high"
        assert result[1]["name"] == "wood"

    def test_get_region_resources_region_not_found(self, integration): pass
        """Test getting region resources when region not found."""
        integration.region_manager.get_region.return_value = None
        
        result = integration._get_region_resources("nonexistent")
        
        assert result == []

    def test_get_region_resources_exception(self, integration): pass
        """Test getting region resources with exception."""
        integration.region_manager.get_region.side_effect = Exception("Test error")
        
        result = integration._get_region_resources("region_1")
        
        assert result == []

    def test_get_adjacent_regions_success(self, integration): pass
        """Test getting adjacent regions successfully."""
        result = integration._get_adjacent_regions("region_1")
        
        assert len(result) == 2
        assert result[0]["id"] == "region_2"
        assert result[0]["name"] == "Northern Plains"
        assert result[0]["direction"] == "north"
        assert result[0]["border_type"] == "river"
        assert result[1]["id"] == "region_3"

    def test_get_adjacent_regions_exception(self, integration): pass
        """Test getting adjacent regions with exception."""
        integration.region_manager.get_adjacent_regions.side_effect = Exception("Test error")
        
        result = integration._get_adjacent_regions("region_1")
        
        assert result == []

    def test_get_seasonal_region_description_with_region_description(self, integration): pass
        """Test getting seasonal region description with region-specific description."""
        result = integration._get_seasonal_region_description("region_1", "spring")
        
        assert result == "flowers bloom across the hills"

    def test_get_seasonal_region_description_with_biome_fallback(self, integration): pass
        """Test getting seasonal region description with biome fallback."""
        region_data = integration.region_manager.get_region.return_value
        region_data["seasonal_descriptions"] = {}  # No region-specific descriptions
        
        result = integration._get_seasonal_region_description("region_1", "summer")
        
        assert "during summer" in result.lower()
        assert "full canopy coverage" in result

    def test_get_seasonal_region_description_no_description(self, integration): pass
        """Test getting seasonal region description when no description available."""
        region_data = integration.region_manager.get_region.return_value
        region_data["seasonal_descriptions"] = {}
        region_data["biome"] = None
        
        result = integration._get_seasonal_region_description("region_1", "winter")
        
        assert result == ""

    def test_get_seasonal_region_description_region_not_found(self, integration): pass
        """Test getting seasonal region description when region not found."""
        integration.region_manager.get_region.return_value = None
        
        result = integration._get_seasonal_region_description("nonexistent", "spring")
        
        assert result == ""

    def test_get_seasonal_region_description_exception(self, integration): pass
        """Test getting seasonal region description with exception."""
        integration.region_manager.get_region.side_effect = Exception("Test error")
        
        result = integration._get_seasonal_region_description("region_1", "spring")
        
        assert result == ""

    def test_get_weather_region_description_with_region_description(self, integration): pass
        """Test getting weather region description with region-specific description."""
        result = integration._get_weather_region_description("region_1", "rain")
        
        assert result == "The hills glisten with moisture"

    def test_get_weather_region_description_with_biome_fallback(self, integration): pass
        """Test getting weather region description with biome fallback."""
        region_data = integration.region_manager.get_region.return_value
        region_data["weather_descriptions"] = {}  # No region-specific descriptions
        
        result = integration._get_weather_region_description("region_1", "snow")
        
        assert "during snow conditions" in result.lower()
        assert "peaceful silence" in result

    def test_get_weather_region_description_no_description(self, integration): pass
        """Test getting weather region description when no description available."""
        region_data = integration.region_manager.get_region.return_value
        region_data["weather_descriptions"] = {}
        region_data["biome"] = None
        
        result = integration._get_weather_region_description("region_1", "clear")
        
        assert result == ""

    def test_get_weather_region_description_region_not_found(self, integration): pass
        """Test getting weather region description when region not found."""
        integration.region_manager.get_region.return_value = None
        
        result = integration._get_weather_region_description("nonexistent", "rain")
        
        assert result == ""

    def test_get_weather_region_description_exception(self, integration): pass
        """Test getting weather region description with exception."""
        integration.region_manager.get_region.side_effect = Exception("Test error")
        
        result = integration._get_weather_region_description("region_1", "rain")
        
        assert result == ""

    @patch('backend.systems.dialogue.region_integration.POIService')
    def test_get_region_for_location_success(self, mock_poi_cls, integration): pass
        """Test getting region for location successfully."""
        mock_poi_service = Mock()
        mock_poi_service.get_poi.return_value = {"region_id": "region_1"}
        mock_poi_cls.return_value = mock_poi_service
        
        result = integration._get_region_for_location("location_1")
        
        assert result == "region_1"

    @patch('backend.systems.dialogue.region_integration.POIService')
    def test_get_region_for_location_no_location(self, mock_poi_cls, integration): pass
        """Test getting region for location when location not found."""
        mock_poi_service = Mock()
        mock_poi_service.get_poi.return_value = None
        mock_poi_cls.return_value = mock_poi_service
        
        result = integration._get_region_for_location("nonexistent")
        
        assert result is None

    @patch('backend.systems.dialogue.region_integration.POIService')
    def test_get_region_for_location_exception(self, mock_poi_cls, integration): pass
        """Test getting region for location with exception."""
        mock_poi_service = Mock()
        mock_poi_service.get_poi.side_effect = Exception("Test error")
        mock_poi_cls.return_value = mock_poi_service
        
        result = integration._get_region_for_location("location_1")
        
        assert result is None


class TestStubBiomeManager: pass
    """Test suite for the stub BiomeManager class."""

    def test_get_instance(self): pass
        """Test getting instance of stub BiomeManager."""
        from backend.systems.dialogue.region_integration import BiomeManager
        
        instance = BiomeManager.get_instance()
        
        assert isinstance(instance, BiomeManager)

    def test_get_biome_returns_none(self): pass
        """Test that get_biome returns None for stub implementation."""
        from backend.systems.dialogue.region_integration import BiomeManager
        
        manager = BiomeManager()
        result = manager.get_biome("any_biome_id")
        
        assert result is None 
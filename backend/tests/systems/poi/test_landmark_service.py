from backend.systems.poi.models import PointOfInterest
from backend.systems.poi.models import PointOfInterest
from backend.systems.poi.models import PointOfInterest
from backend.systems.poi.models import PointOfInterest
from backend.systems.poi.models import PointOfInterest
from backend.systems.poi.models import PointOfInterest
from typing import Any
from typing import Type
from typing import List
from datetime import datetime
"""
Tests for backend.systems.poi.services.landmark_service

This module contains tests for POI landmark functionality.
"""

import pytest
from unittest.mock import Mock, patch
from typing import Dict, Any, List
import uuid

from backend.systems.poi.services.landmark_service import LandmarkService
from backend.systems.poi.models import PointOfInterest, POIType


class TestLandmarkService: pass
    """Tests for POI landmark service."""

    @pytest.fixture
    def sample_poi(self): pass
        """Create a sample POI for testing."""
        poi = Mock(spec=PointOfInterest)
        poi.id = "poi_1"
        poi.name = "Test Village"
        poi.poi_type = POIType.VILLAGE
        poi.landmarks = []
        poi.metadata = {}
        poi.update_timestamp = Mock()
        return poi

    @pytest.fixture
    def city_poi(self): pass
        """Create a city POI for testing."""
        poi = Mock(spec=PointOfInterest)
        poi.id = "city_1"
        poi.name = "Test City"
        poi.poi_type = POIType.CITY
        poi.landmarks = []
        poi.metadata = {}
        poi.update_timestamp = Mock()
        return poi

    @pytest.fixture
    def poi_with_landmarks(self): pass
        """Create a POI with existing landmarks."""
        poi = Mock(spec=PointOfInterest)
        poi.id = "poi_with_landmarks"
        poi.name = "Landmark Village"
        poi.poi_type = POIType.VILLAGE
        poi.landmarks = [
            {
                "id": "landmark_1",
                "type": "monument",
                "name": "Victory Monument",
                "category": "cultural",
                "rarity": "common",
                "description": "A monument to past victories",
                "bonuses": {"cultural_value": 1.0},
                "created_at": "2023-01-01T00:00:00"
            }
        ]
        poi.metadata = {}
        poi.update_timestamp = Mock()
        return poi

    def test_landmark_categories_constants(self): pass
        """Test that landmark categories are properly defined."""
        categories = LandmarkService.LANDMARK_CATEGORIES
        
        assert "natural" in categories
        assert "cultural" in categories
        assert "historical" in categories
        assert "economic" in categories
        assert "military" in categories
        assert "magical" in categories
        assert "religious" in categories
        
        # Check some specific landmark types
        assert "waterfall" in categories["natural"]
        assert "monument" in categories["cultural"]
        assert "ruins" in categories["historical"]
        assert "market" in categories["economic"]
        assert "fortress" in categories["military"]
        assert "wizard_tower" in categories["magical"]
        assert "temple" in categories["religious"]

    def test_landmark_rarities_constants(self): pass
        """Test that landmark rarities are properly defined."""
        rarities = LandmarkService.LANDMARK_RARITIES
        
        assert rarities["common"] == 0.5
        assert rarities["uncommon"] == 0.3
        assert rarities["rare"] == 0.15
        assert rarities["legendary"] == 0.05
        
        # Check that probabilities sum to 1.0
        total_prob = sum(rarities.values())
        assert abs(total_prob - 1.0) < 0.001

    def test_bonus_strength_constants(self): pass
        """Test that bonus strength values are properly defined."""
        strengths = LandmarkService.BONUS_STRENGTH
        
        assert strengths["common"] == 1.0
        assert strengths["uncommon"] == 1.5
        assert strengths["rare"] == 2.0
        assert strengths["legendary"] == 3.0

    def test_max_landmarks_constants(self): pass
        """Test that max landmarks by POI type are properly defined."""
        max_landmarks = LandmarkService.MAX_LANDMARKS
        
        assert max_landmarks[POIType.CITY] == 5
        assert max_landmarks[POIType.TOWN] == 3
        assert max_landmarks[POIType.VILLAGE] == 2
        assert max_landmarks[POIType.OUTPOST] == 1
        assert max_landmarks[POIType.RUINS] == 2
        assert max_landmarks[POIType.DUNGEON] == 2
        assert max_landmarks["default"] == 1

    def test_get_max_landmarks_known_type(self, sample_poi): pass
        """Test getting max landmarks for known POI type."""
        result = LandmarkService.get_max_landmarks(sample_poi)
        assert result == 2  # VILLAGE type

    def test_get_max_landmarks_unknown_type(self): pass
        """Test getting max landmarks for unknown POI type."""
        poi = Mock(spec=PointOfInterest)
        poi.poi_type = "unknown_type"
        
        result = LandmarkService.get_max_landmarks(poi)
        assert result == 1  # default value

    def test_get_landmarks_empty_list(self, sample_poi): pass
        """Test getting landmarks from POI with empty list."""
        result = LandmarkService.get_landmarks(sample_poi)
        assert result == []

    def test_get_landmarks_no_attribute(self): pass
        """Test getting landmarks from POI without landmarks attribute."""
        poi = Mock(spec=PointOfInterest)
        # Don't set landmarks attribute
        
        result = LandmarkService.get_landmarks(poi)
        assert result == []

    def test_get_landmarks_invalid_attribute(self): pass
        """Test getting landmarks from POI with invalid landmarks attribute."""
        poi = Mock(spec=PointOfInterest)
        poi.landmarks = "not_a_list"
        
        result = LandmarkService.get_landmarks(poi)
        assert result == []

    def test_get_landmarks_with_data(self, poi_with_landmarks): pass
        """Test getting landmarks from POI with existing landmarks."""
        result = LandmarkService.get_landmarks(poi_with_landmarks)
        
        assert len(result) == 1
        assert result[0]["id"] == "landmark_1"
        assert result[0]["type"] == "monument"
        assert result[0]["name"] == "Victory Monument"

    @patch('uuid.uuid4')
    @patch('backend.systems.poi.services.landmark_service.datetime')
    def test_add_landmark_basic(self, mock_datetime, mock_uuid, sample_poi): pass
        """Test basic landmark addition."""
        mock_uuid.return_value = Mock()
        mock_uuid.return_value.__str__ = Mock(return_value="test-uuid")
        mock_datetime.utcnow.return_value.isoformat.return_value = "2023-01-01T00:00:00"
        
        updated_poi, landmark = LandmarkService.add_landmark(
            sample_poi, "monument", name="Test Monument"
        )
        
        assert updated_poi == sample_poi
        assert landmark is not None
        assert landmark["id"] == "test-uuid"
        assert landmark["type"] == "monument"
        assert landmark["name"] == "Test Monument"
        assert landmark["category"] == "cultural"  # monument is in cultural category
        assert landmark["rarity"] == "common"  # default
        assert len(sample_poi.landmarks) == 1
        assert sample_poi.update_timestamp.called

    def test_add_landmark_at_max_capacity(self, sample_poi): pass
        """Test adding landmark when POI is at max capacity."""
        # Fill POI to max capacity (2 for village)
        sample_poi.landmarks = [{"id": "1"}, {"id": "2"}]
        
        updated_poi, landmark = LandmarkService.add_landmark(
            sample_poi, "monument"
        )
        
        assert updated_poi == sample_poi
        assert landmark is None
        assert len(sample_poi.landmarks) == 2  # No change

    def test_add_landmark_no_landmarks_attribute(self): pass
        """Test adding landmark to POI without landmarks attribute."""
        poi = Mock(spec=PointOfInterest)
        poi.id = "poi_no_landmarks"
        poi.name = "Test POI"
        poi.poi_type = POIType.VILLAGE
        poi.update_timestamp = Mock()
        # Don't set landmarks attribute
        
        with patch('uuid.uuid4') as mock_uuid, \
             patch('backend.systems.poi.services.landmark_service.datetime') as mock_datetime: pass
            mock_uuid.return_value = Mock()
            mock_uuid.return_value.__str__ = Mock(return_value="test-uuid")
            mock_datetime.utcnow.return_value.isoformat.return_value = "2023-01-01T00:00:00"
            
            updated_poi, landmark = LandmarkService.add_landmark(
                poi, "monument"
            )
        
        assert hasattr(poi, 'landmarks')
        assert isinstance(poi.landmarks, list)
        assert len(poi.landmarks) == 1
        assert landmark is not None

    def test_add_landmark_with_all_parameters(self, sample_poi): pass
        """Test adding landmark with all parameters specified."""
        bonuses = {"cultural_value": 2.0, "tourism": 1.5}
        
        with patch('uuid.uuid4') as mock_uuid, \
             patch('backend.systems.poi.services.landmark_service.datetime') as mock_datetime: pass
            mock_uuid.return_value = Mock()
            mock_uuid.return_value.__str__ = Mock(return_value="test-uuid")
            mock_datetime.utcnow.return_value.isoformat.return_value = "2023-01-01T00:00:00"
            
            updated_poi, landmark = LandmarkService.add_landmark(
                sample_poi,
                landmark_type="statue",
                name="Hero Statue",
                category="cultural",
                rarity="rare",
                description="A statue of a legendary hero",
                bonuses=bonuses
            )
        
        assert landmark["type"] == "statue"
        assert landmark["name"] == "Hero Statue"
        assert landmark["category"] == "cultural"
        assert landmark["rarity"] == "rare"
        assert landmark["description"] == "A statue of a legendary hero"
        assert landmark["bonuses"] == bonuses

    def test_add_landmark_unknown_type_gets_natural_category(self, sample_poi): pass
        """Test that unknown landmark type gets natural category."""
        with patch('uuid.uuid4') as mock_uuid, \
             patch('backend.systems.poi.services.landmark_service.datetime') as mock_datetime: pass
            mock_uuid.return_value = Mock()
            mock_uuid.return_value.__str__ = Mock(return_value="test-uuid")
            mock_datetime.utcnow.return_value.isoformat.return_value = "2023-01-01T00:00:00"
            
            updated_poi, landmark = LandmarkService.add_landmark(
                sample_poi, "unknown_landmark_type"
            )
        
        assert landmark["category"] == "natural"  # default category

    @patch('backend.systems.poi.services.landmark_service.LandmarkService.generate_landmark_name')
    def test_add_landmark_generates_name_when_not_provided(self, mock_generate_name, sample_poi): pass
        """Test that landmark name is generated when not provided."""
        mock_generate_name.return_value = "Generated Name"
        
        with patch('uuid.uuid4') as mock_uuid, \
             patch('backend.systems.poi.services.landmark_service.datetime') as mock_datetime: pass
            mock_uuid.return_value = Mock()
            mock_uuid.return_value.__str__ = Mock(return_value="test-uuid")
            mock_datetime.utcnow.return_value.isoformat.return_value = "2023-01-01T00:00:00"
            
            updated_poi, landmark = LandmarkService.add_landmark(
                sample_poi, "monument"
            )
        
        mock_generate_name.assert_called_once_with("monument", "Test Village")
        assert landmark["name"] == "Generated Name"

    @patch('backend.systems.poi.services.landmark_service.LandmarkService.generate_landmark_description')
    def test_add_landmark_generates_description_when_not_provided(self, mock_generate_desc, sample_poi): pass
        """Test that landmark description is generated when not provided."""
        mock_generate_desc.return_value = "Generated Description"
        
        with patch('uuid.uuid4') as mock_uuid, \
             patch('backend.systems.poi.services.landmark_service.datetime') as mock_datetime: pass
            mock_uuid.return_value = Mock()
            mock_uuid.return_value.__str__ = Mock(return_value="test-uuid")
            mock_datetime.utcnow.return_value.isoformat.return_value = "2023-01-01T00:00:00"
            
            updated_poi, landmark = LandmarkService.add_landmark(
                sample_poi, "monument"
            )
        
        mock_generate_desc.assert_called_once_with("monument", "common", "Test Village")
        assert landmark["description"] == "Generated Description"

    @patch('backend.systems.poi.services.landmark_service.LandmarkService.generate_landmark_bonuses')
    def test_add_landmark_generates_bonuses_when_not_provided(self, mock_generate_bonuses, sample_poi): pass
        """Test that landmark bonuses are generated when not provided."""
        mock_generate_bonuses.return_value = {"cultural_value": 1.0}
        
        with patch('uuid.uuid4') as mock_uuid, \
             patch('backend.systems.poi.services.landmark_service.datetime') as mock_datetime: pass
            mock_uuid.return_value = Mock()
            mock_uuid.return_value.__str__ = Mock(return_value="test-uuid")
            mock_datetime.utcnow.return_value.isoformat.return_value = "2023-01-01T00:00:00"
            
            updated_poi, landmark = LandmarkService.add_landmark(
                sample_poi, "monument"
            )
        
        mock_generate_bonuses.assert_called_once_with("monument", "cultural", "common")
        assert landmark["bonuses"] == {"cultural_value": 1.0}

    def test_remove_landmark_success(self, poi_with_landmarks): pass
        """Test successful landmark removal."""
        updated_poi, success = LandmarkService.remove_landmark(
            poi_with_landmarks, "landmark_1"
        )
        
        assert updated_poi == poi_with_landmarks
        assert success is True
        assert len(poi_with_landmarks.landmarks) == 0
        assert poi_with_landmarks.update_timestamp.called

    def test_remove_landmark_not_found(self, poi_with_landmarks): pass
        """Test removing non-existent landmark."""
        updated_poi, success = LandmarkService.remove_landmark(
            poi_with_landmarks, "nonexistent_id"
        )
        
        assert updated_poi == poi_with_landmarks
        assert success is False
        assert len(poi_with_landmarks.landmarks) == 1  # No change

    def test_remove_landmark_no_landmarks(self, sample_poi): pass
        """Test removing landmark from POI with no landmarks."""
        updated_poi, success = LandmarkService.remove_landmark(
            sample_poi, "any_id"
        )
        
        assert updated_poi == sample_poi
        assert success is False

    def test_generate_landmark_name_monument(self): pass
        """Test generating landmark name for monument."""
        result = LandmarkService.generate_landmark_name("monument", "Test Village")
        
        # Should be a reasonable length and contain monument
        assert len(result) > 5
        assert "monument" in result.lower()

    def test_generate_landmark_name_waterfall(self): pass
        """Test generating landmark name for waterfall."""
        result = LandmarkService.generate_landmark_name("waterfall", "Mountain Town")
        
        assert len(result) > 5
        assert "waterfall" in result.lower()

    def test_generate_landmark_description_common_rarity(self): pass
        """Test generating landmark description for common rarity."""
        result = LandmarkService.generate_landmark_description(
            "monument", "common", "Test Village"
        )
        
        assert "Test Village" in result
        assert len(result) > 10

    def test_generate_landmark_description_legendary_rarity(self): pass
        """Test generating landmark description for legendary rarity."""
        result = LandmarkService.generate_landmark_description(
            "monument", "legendary", "Test Village"
        )
        
        assert "Test Village" in result
        assert len(result) > 10
        # Legendary descriptions should contain "legends" or "wonder"
        assert "legends" in result.lower() or "wonder" in result.lower()

    def test_generate_landmark_bonuses_cultural_common(self): pass
        """Test generating bonuses for cultural landmark with common rarity."""
        result = LandmarkService.generate_landmark_bonuses(
            "monument", "cultural", "common"
        )
        
        assert isinstance(result, dict)
        assert len(result) > 0
        # Should have cultural-related bonuses (population_growth or reputation_gain)
        assert any(key in ["population_growth", "reputation_gain"] for key in result.keys())

    def test_generate_landmark_bonuses_economic_rare(self): pass
        """Test generating bonuses for economic landmark with rare rarity."""
        result = LandmarkService.generate_landmark_bonuses(
            "market", "economic", "rare"
        )
        
        assert isinstance(result, dict)
        assert len(result) > 0
        # Should have economic-related bonuses
        assert any("trade" in key.lower() or "economic" in key.lower() for key in result.keys())

    def test_generate_landmark_bonuses_magical_legendary(self): pass
        """Test generating bonuses for magical landmark with legendary rarity."""
        result = LandmarkService.generate_landmark_bonuses(
            "wizard_tower", "magical", "legendary"
        )
        
        assert isinstance(result, dict)
        assert len(result) > 0
        # Should have magical-related bonuses
        assert any("magic" in key.lower() or "mana" in key.lower() for key in result.keys())

    def test_get_specific_landmark_bonus_market(self): pass
        """Test getting specific bonuses for market landmark."""
        result = LandmarkService.get_specific_landmark_bonus("market", 2.0)
        
        assert isinstance(result, dict)
        assert "trade_value" in result
        assert "merchant_count" in result
        assert result["trade_value"] == 0.25 * 2.0
        assert result["merchant_count"] == 0.15 * 2.0

    def test_get_specific_landmark_bonus_fortress(self): pass
        """Test getting specific bonuses for fortress landmark."""
        result = LandmarkService.get_specific_landmark_bonus("fortress", 1.5)
        
        assert isinstance(result, dict)
        assert "defense_rating" in result
        assert "garrison_size" in result
        assert result["defense_rating"] == 0.3 * 1.5
        assert result["garrison_size"] == 0.2 * 1.5

    def test_get_specific_landmark_bonus_temple(self): pass
        """Test getting specific bonuses for temple landmark."""
        result = LandmarkService.get_specific_landmark_bonus("temple", 1.0)
        
        assert isinstance(result, dict)
        assert "faith_gain" in result
        assert "pilgrim_visitors" in result
        assert result["faith_gain"] == 0.25 * 1.0
        assert result["pilgrim_visitors"] == 0.15 * 1.0

    def test_get_specific_landmark_bonus_unknown_type(self): pass
        """Test getting specific bonuses for unknown landmark type."""
        result = LandmarkService.get_specific_landmark_bonus("unknown_type", 1.0)
        
        assert result is None

    def test_calculate_landmark_effects_no_landmarks(self, sample_poi): pass
        """Test calculating effects for POI with no landmarks."""
        result = LandmarkService.calculate_landmark_effects(sample_poi)
        
        assert result == {}

    def test_calculate_landmark_effects_single_landmark(self, poi_with_landmarks): pass
        """Test calculating effects for POI with single landmark."""
        result = LandmarkService.calculate_landmark_effects(poi_with_landmarks)
        
        assert "cultural_value" in result
        assert result["cultural_value"] == 1.0

    def test_calculate_landmark_effects_multiple_landmarks(self, sample_poi): pass
        """Test calculating effects for POI with multiple landmarks."""
        sample_poi.landmarks = [
            {
                "bonuses": {"cultural_value": 1.0, "tourism": 0.5}
            },
            {
                "bonuses": {"cultural_value": 1.5, "defense": 2.0}
            }
        ]
        
        result = LandmarkService.calculate_landmark_effects(sample_poi)
        
        assert result["cultural_value"] == 2.5  # 1.0 + 1.5
        assert result["tourism"] == 0.5
        assert result["defense"] == 2.0

    def test_calculate_landmark_effects_no_bonuses(self, sample_poi): pass
        """Test calculating effects for landmarks without bonuses."""
        sample_poi.landmarks = [
            {"id": "landmark_1"},  # No bonuses key
            {"bonuses": {}}  # Empty bonuses
        ]
        
        result = LandmarkService.calculate_landmark_effects(sample_poi)
        
        assert result == {}

    @patch('random.choice')
    @patch('backend.systems.poi.services.landmark_service.LandmarkService.select_rarity')
    @patch('backend.systems.poi.services.landmark_service.LandmarkService.select_weighted_category')
    @patch('backend.systems.poi.services.landmark_service.LandmarkService.add_landmark')
    def test_generate_random_landmark_basic(self, mock_add, mock_select_cat, mock_select_rarity, mock_choice, sample_poi): pass
        """Test generating random landmark with basic parameters."""
        mock_select_rarity.return_value = "uncommon"
        mock_select_cat.return_value = "cultural"
        mock_choice.return_value = "monument"
        mock_add.return_value = (sample_poi, {"id": "test_landmark"})
        
        result_poi, result_landmark = LandmarkService.generate_random_landmark(sample_poi)
        
        mock_add.assert_called_once_with(
            poi=sample_poi,
            landmark_type="monument",
            category="cultural",
            rarity="uncommon"
        )
        assert result_poi == sample_poi
        assert result_landmark == {"id": "test_landmark"}

    def test_generate_random_landmark_at_max_capacity(self, sample_poi): pass
        """Test generating random landmark when POI is at max capacity."""
        # Fill POI to max capacity (2 for village)
        sample_poi.landmarks = [{"id": "1"}, {"id": "2"}]
        
        result_poi, result_landmark = LandmarkService.generate_random_landmark(sample_poi)
        
        assert result_poi == sample_poi
        assert result_landmark is None

    @patch('random.choice')
    @patch('backend.systems.poi.services.landmark_service.LandmarkService.select_rarity')
    @patch('backend.systems.poi.services.landmark_service.LandmarkService.select_weighted_category')
    @patch('backend.systems.poi.services.landmark_service.LandmarkService.add_landmark')
    def test_generate_random_landmark_with_terrain(self, mock_add, mock_select_cat, mock_select_rarity, mock_choice, sample_poi): pass
        """Test generating random landmark with terrain context."""
        mock_select_rarity.return_value = "common"
        mock_select_cat.return_value = "natural"
        mock_choice.return_value = "waterfall"
        mock_add.return_value = (sample_poi, {"id": "test_landmark"})
        
        result_poi, result_landmark = LandmarkService.generate_random_landmark(
            sample_poi, terrain_type="mountain"
        )
        
        # Should have called select_weighted_category with adjusted weights
        mock_select_cat.assert_called_once()
        weights = mock_select_cat.call_args[0][0]
        assert weights["natural"] > 1.0  # Should be boosted for mountain terrain

    @patch('random.choice')
    @patch('backend.systems.poi.services.landmark_service.LandmarkService.select_rarity')
    @patch('backend.systems.poi.services.landmark_service.LandmarkService.select_weighted_category')
    @patch('backend.systems.poi.services.landmark_service.LandmarkService.add_landmark')
    def test_generate_random_landmark_with_culture(self, mock_add, mock_select_cat, mock_select_rarity, mock_choice, sample_poi): pass
        """Test generating random landmark with culture context."""
        mock_select_rarity.return_value = "common"
        mock_select_cat.return_value = "cultural"
        mock_choice.return_value = "monument"
        mock_add.return_value = (sample_poi, {"id": "test_landmark"})
        
        result_poi, result_landmark = LandmarkService.generate_random_landmark(
            sample_poi, culture="imperial"
        )
        
        # Should have called select_weighted_category with adjusted weights
        mock_select_cat.assert_called_once()
        weights = mock_select_cat.call_args[0][0]
        assert weights["cultural"] > 1.0  # Should be boosted for imperial culture
        assert weights["military"] > 1.0  # Should be boosted for imperial culture

    @patch('random.random')
    def test_select_rarity_common(self, mock_random): pass
        """Test selecting common rarity."""
        mock_random.return_value = 0.3  # Within common range (0.5)
        
        result = LandmarkService.select_rarity()
        
        assert result == "common"

    @patch('random.random')
    def test_select_rarity_uncommon(self, mock_random): pass
        """Test selecting uncommon rarity."""
        mock_random.return_value = 0.7  # Within uncommon range (0.5 + 0.3 = 0.8)
        
        result = LandmarkService.select_rarity()
        
        assert result == "uncommon"

    @patch('random.random')
    def test_select_rarity_rare(self, mock_random): pass
        """Test selecting rare rarity."""
        mock_random.return_value = 0.9  # Within rare range (0.8 + 0.15 = 0.95)
        
        result = LandmarkService.select_rarity()
        
        assert result == "rare"

    @patch('random.random')
    def test_select_rarity_legendary(self, mock_random): pass
        """Test selecting legendary rarity."""
        mock_random.return_value = 0.99  # Within legendary range (0.95 + 0.05 = 1.0)
        
        result = LandmarkService.select_rarity()
        
        assert result == "legendary"

    @patch('random.random')
    def test_select_weighted_category_basic(self, mock_random): pass
        """Test selecting weighted category with equal weights."""
        weights = {"natural": 1.0, "cultural": 1.0}
        mock_random.return_value = 0.3  # Should select natural (first 50%)
        
        result = LandmarkService.select_weighted_category(weights)
        
        assert result == "natural"

    @patch('random.random')
    def test_select_weighted_category_weighted(self, mock_random): pass
        """Test selecting weighted category with different weights."""
        weights = {"natural": 1.0, "cultural": 3.0}  # Cultural is 3x more likely
        mock_random.return_value = 0.8  # Should select cultural
        
        result = LandmarkService.select_weighted_category(weights)
        
        assert result == "cultural"

    def test_apply_landmark_effects_no_landmarks(self, sample_poi): pass
        """Test applying effects for POI with no landmarks."""
        result = LandmarkService.apply_landmark_effects(sample_poi)
        
        assert result == {}
        assert hasattr(sample_poi, 'metadata')
        assert sample_poi.metadata["landmark_effects"] == {}
        assert sample_poi.update_timestamp.called

    def test_apply_landmark_effects_with_landmarks(self, poi_with_landmarks): pass
        """Test applying effects for POI with landmarks."""
        result = LandmarkService.apply_landmark_effects(poi_with_landmarks)
        
        assert hasattr(poi_with_landmarks, 'metadata')
        assert "landmark_effects" in poi_with_landmarks.metadata
        assert poi_with_landmarks.metadata["landmark_effects"]["cultural_value"] == 1.0
        assert poi_with_landmarks.update_timestamp.called

    def test_apply_landmark_effects_resource_production(self, sample_poi): pass
        """Test applying effects with resource production bonus."""
        sample_poi.landmarks = [
            {"bonuses": {"resource_production": 1.5}}
        ]
        
        result = LandmarkService.apply_landmark_effects(sample_poi)
        
        assert "resource_modifier" in result
        assert result["resource_modifier"] == 1.5

    def test_apply_landmark_effects_population_growth(self, sample_poi): pass
        """Test applying effects with population growth bonus."""
        sample_poi.landmarks = [
            {"bonuses": {"population_growth": 0.8}}
        ]
        
        result = LandmarkService.apply_landmark_effects(sample_poi)
        
        assert "population_growth_modifier" in result
        assert result["population_growth_modifier"] == 0.8

    def test_apply_landmark_effects_no_metadata_attribute(self): pass
        """Test applying effects to POI without metadata attribute."""
        poi = Mock(spec=PointOfInterest)
        poi.landmarks = [{"bonuses": {"cultural_value": 1.0}}]
        poi.update_timestamp = Mock()
        # Don't set metadata attribute
        
        result = LandmarkService.apply_landmark_effects(poi)
        
        assert hasattr(poi, 'metadata')
        assert isinstance(poi.metadata, dict)
        assert "landmark_effects" in poi.metadata

    def test_edge_cases_empty_category_list(self): pass
        """Test handling of empty category list."""
        # Temporarily modify categories for testing
        original_categories = LandmarkService.LANDMARK_CATEGORIES.copy()
        LandmarkService.LANDMARK_CATEGORIES["test_empty"] = []
        
        try: pass
            with patch('random.choice') as mock_choice: pass
                mock_choice.side_effect = IndexError("list index out of range")
                
                # This should not crash
                with patch('backend.systems.poi.services.landmark_service.LandmarkService.select_weighted_category') as mock_select: pass
                    mock_select.return_value = "test_empty"
                    
                    with patch('backend.systems.poi.services.landmark_service.LandmarkService.select_rarity') as mock_rarity: pass
                        mock_rarity.return_value = "common"
                        
                        poi = Mock(spec=PointOfInterest)
                        poi.landmarks = []
                        poi.poi_type = POIType.VILLAGE
                        
                        # Should handle the error gracefully
                        try: pass
                            LandmarkService.generate_random_landmark(poi)
                        except IndexError: pass
                            pass  # Expected to fail gracefully
        finally: pass
            # Restore original categories
            LandmarkService.LANDMARK_CATEGORIES = original_categories

    def test_landmark_integration_full_workflow(self, sample_poi): pass
        """Test full landmark workflow integration."""
        # Add a landmark
        with patch('uuid.uuid4') as mock_uuid, \
             patch('backend.systems.poi.services.landmark_service.datetime') as mock_datetime: pass
            mock_uuid.return_value = Mock()
            mock_uuid.return_value.__str__ = Mock(return_value="test-uuid")
            mock_datetime.utcnow.return_value.isoformat.return_value = "2023-01-01T00:00:00"
            
            updated_poi, landmark = LandmarkService.add_landmark(
                sample_poi, "market", rarity="rare"
            )
        
        # Calculate effects
        effects = LandmarkService.calculate_landmark_effects(sample_poi)
        assert len(effects) > 0
        
        # Apply effects
        applied = LandmarkService.apply_landmark_effects(sample_poi)
        assert sample_poi.metadata["landmark_effects"] == effects
        
        # Remove landmark
        removed_poi, success = LandmarkService.remove_landmark(sample_poi, "test-uuid")
        assert success is True
        assert len(sample_poi.landmarks) == 0

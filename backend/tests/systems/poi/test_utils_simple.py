from typing import Type
"""
Tests for backend.systems.poi.utils

This module contains tests for POI utility functions.
"""

import pytest
from unittest.mock import Mock
import math

from backend.systems.poi.utils import (
    calculate_distance,
    calculate_poi_distance,
    is_poi_accessible,
    generate_poi_name,
    normalize_poi_type,
    calculate_resource_production,
    get_closest_pois,
    find_poi_neighbors,
    calculate_poi_influence_range,
    is_poi_in_region,
    determine_interaction_type_from_state,
)
from backend.systems.poi.models import POIState, POIInteractionType


class TestUtilsFunctions:
    """Simple tests for POI utility functions."""

    def test_calculate_distance(self):
        """Test basic distance calculation."""
        distance = calculate_distance((0, 0), (3, 4))
        assert distance == 5.0

    def test_calculate_poi_distance_same_region(self):
        """Test POI distance calculation in same region."""
        poi1 = Mock()
        poi1.region_id = "region_1"
        poi1.position = {"x": 0, "y": 0}
        
        poi2 = Mock()
        poi2.region_id = "region_1"
        poi2.position = {"x": 3, "y": 4}
        
        distance = calculate_poi_distance(poi1, poi2)
        assert distance == 5.0

    def test_calculate_poi_distance_different_regions(self):
        """Test POI distance calculation in different regions."""
        poi1 = Mock(spec=['region_id'])
        poi1.region_id = "region_1"
        
        poi2 = Mock(spec=['region_id'])
        poi2.region_id = "region_2"
        
        distance = calculate_poi_distance(poi1, poi2)
        assert distance == 9999.0

    def test_is_poi_accessible(self):
        """Test POI accessibility check."""
        poi = Mock()
        poi.level = 1
        poi.current_state = POIState.NORMAL
        
        result = is_poi_accessible(poi, character_level=3)
        assert result is True

    def test_generate_poi_name(self):
        """Test POI name generation."""
        name = generate_poi_name("dungeon")
        assert isinstance(name, str)
        assert len(name) > 0

    def test_normalize_poi_type(self):
        """Test POI type normalization."""
        result = normalize_poi_type("TEMPLE")
        assert result == "temple"

    def test_calculate_resource_production(self):
        """Test resource production calculation."""
        poi = Mock()
        poi.poi_type = "city"
        poi.population = 1000
        poi.current_state = POIState.NORMAL
        poi.tags = []
        
        production = calculate_resource_production(poi)
        assert isinstance(production, dict)
        assert "food" in production

    def test_get_closest_pois(self):
        """Test getting closest POIs."""
        pois = [Mock(coordinates=(1, 1)), Mock(coordinates=(5, 5))]
        result = get_closest_pois(0, 0, pois, max_distance=10, limit=2)
        assert isinstance(result, list)

    def test_find_poi_neighbors(self):
        """Test finding POI neighbors."""
        poi1 = Mock()
        poi1.id = "poi_1"
        poi1.x = 0
        poi1.y = 0
        poi1.coordinates = (0, 0)
        
        poi2 = Mock()
        poi2.id = "poi_2"
        poi2.x = 1
        poi2.y = 1
        poi2.coordinates = (1, 1)
        poi2.position = {'x': 1, 'y': 1}
        
        pois = [poi1, poi2]
        
        result = find_poi_neighbors("poi_1", pois, radius=5)
        assert isinstance(result, list)

    def test_calculate_poi_influence_range(self):
        """Test POI influence range calculation."""
        poi = Mock()
        poi.poi_type = "city"
        poi.population = 1000
        
        range_val = calculate_poi_influence_range(poi)
        assert isinstance(range_val, float)
        assert range_val > 0

    def test_is_poi_in_region(self):
        """Test POI region checking."""
        poi = Mock(region_id="region_1")
        result = is_poi_in_region(poi, "region_1")
        assert result is True

    def test_determine_interaction_type_from_state(self):
        """Test interaction type determination."""
        result = determine_interaction_type_from_state("normal", "city")
        assert result == POIInteractionType.SOCIAL
        
        result = determine_interaction_type_from_state("dungeon", "dungeon")
        assert result == POIInteractionType.COMBAT
        
        result = determine_interaction_type_from_state("abandoned", "village")
        assert result == POIInteractionType.NEUTRAL 
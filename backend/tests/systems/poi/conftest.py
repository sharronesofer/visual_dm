from backend.systems.poi.models import PointOfInterest
from backend.systems.poi.models import PointOfInterest
from backend.systems.poi.models import PointOfInterest
from backend.systems.poi.models import PointOfInterest
from backend.systems.poi.models import PointOfInterest
from backend.systems.poi.models import PointOfInterest
from typing import Type
"""
POI-specific test fixtures.
"""

import pytest
from datetime import datetime
from backend.systems.poi.models import (
    PointOfInterest,
    POIType,
    POIState,
    POIInteractionType,
)


@pytest.fixture
def city_poi():
    """Fixture for a city POI."""
    return PointOfInterest(
        id="test_city_poi_id",
        name="Test City",
        description="A test city for testing",
        region_id="test_region_1",
        coordinates=(10.0, 10.0),
        position={"x": 10, "y": 10},
        poi_type=POIType.CITY,
        current_state=POIState.NORMAL,
        interaction_type=POIInteractionType.SOCIAL,
        population=1000,
        max_population=1500,
        claimed_region_hex_ids=["hex_1", "hex_2"],
        tags=["urban", "civilized"],
    )


@pytest.fixture
def town_poi():
    """Fixture for a town POI."""
    return PointOfInterest(
        id="test_town_poi_id",
        name="Test Town",
        description="A test town for testing",
        region_id="test_region_1",
        coordinates=(5.0, 5.0),
        position={"x": 5, "y": 5},
        poi_type=POIType.TOWN,
        current_state=POIState.NORMAL,
        interaction_type=POIInteractionType.SOCIAL,
        population=300,
        max_population=500,
        claimed_region_hex_ids=["hex_3"],
        tags=["rural", "peaceful"],
    )


@pytest.fixture
def village_poi():
    """Fixture for a village POI."""
    return PointOfInterest(
        id="test_village_poi_id",
        name="Test Village",
        description="A test village for testing",
        region_id="test_region_2",
        coordinates=(15.0, 15.0),
        position={"x": 15, "y": 15},
        poi_type=POIType.VILLAGE,
        current_state=POIState.NORMAL,
        interaction_type=POIInteractionType.SOCIAL,
        population=100,
        max_population=200,
        claimed_region_hex_ids=[],
        tags=["rural", "small"],
    )


@pytest.fixture
def ruins_poi():
    """Fixture for a ruins POI."""
    return PointOfInterest(
        id="test_ruins_poi_id",
        name="Ancient Ruins",
        description="Ancient ruins for testing",
        region_id="test_region_3",
        poi_type=POIType.RUINS,
        current_state=POIState.RUINS,
        interaction_type=POIInteractionType.NEUTRAL,
        population=0,
        max_population=0,
        claimed_region_hex_ids=[],
        tags=["ancient", "mysterious"],
    )


@pytest.fixture
def dungeon_poi():
    """Fixture for a dungeon POI."""
    return PointOfInterest(
        id="test_dungeon_poi_id",
        name="Dark Dungeon",
        description="A dark dungeon for testing",
        region_id="test_region_4",
        poi_type=POIType.DUNGEON,
        current_state=POIState.DUNGEON,
        interaction_type=POIInteractionType.COMBAT,
        population=0,
        max_population=0,
        claimed_region_hex_ids=[],
        tags=["dark", "dangerous"],
    )

from backend.systems.poi.models import PointOfInterest
from backend.systems.poi.services import MetropolitanSpreadService
from backend.systems.economy.models import Resource
from backend.systems.poi.models import PointOfInterest
from backend.systems.poi.services import MetropolitanSpreadService
from backend.systems.economy.models import Resource
from backend.systems.poi.models import PointOfInterest
from backend.systems.poi.services import MetropolitanSpreadService
from backend.systems.economy.models import Resource
from backend.systems.poi.models import PointOfInterest
from backend.systems.poi.services import MetropolitanSpreadService
from backend.systems.economy.models import Resource
from backend.systems.poi.models import PointOfInterest
from backend.systems.poi.services import MetropolitanSpreadService
from backend.systems.economy.models import Resource
from backend.systems.poi.models import PointOfInterest
from backend.systems.poi.services import MetropolitanSpreadService
from backend.systems.economy.models import Resource
import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime
from typing import Any, Type, List, Dict, Optional, Union

from backend.systems.poi.services import (
    POIService,
    POIStateService,
    MetropolitanSpreadService,
)
from backend.systems.poi.models import (
    PointOfInterest,
    POIType,
    POIState,
    POIInteractionType,
)
from backend.systems.poi.schemas import (
    POICreationSchema,
    POIUpdateSchema,
    POIStateTransitionSchema,
)


class TestPOIService:
    """Test suite for POI Service."""

    def test_create_poi(self, mock_event_dispatcher):
        """Test creating a new POI."""
        # Setup
        creation_schema = POICreationSchema(
            name="New Test POI",
            region_id="test_region_1",
            poi_type="city",
            description="A new test POI",
            tags=["test", "urban"],
            population=500,
            max_population=1000,
        )

        # Execute
        poi = POIService.create_poi(creation_schema)

        # Verify
        assert poi.name == "New Test POI"
        assert poi.region_id == "test_region_1"
        assert poi.poi_type == POIType.CITY
        assert poi.description == "A new test POI"
        assert set(poi.tags) == {"test", "urban"}
        assert poi.population == 500
        assert poi.max_population == 1000
        assert poi.current_state == POIState.NORMAL  # Default
        assert isinstance(poi.id, str)
        assert isinstance(poi.created_at, datetime)
        assert isinstance(poi.updated_at, datetime)

    def test_update_poi(self, city_poi, mock_event_dispatcher):
        """Test updating a POI."""
        # Setup
        original_name = city_poi.name
        updates = {
            "name": "Updated Name",
            "description": "Updated description",
            "population": 250,
        }

        # Execute
        result = POIService.update_poi(city_poi, updates)

        # Verify
        assert result is city_poi  # Same object returned
        assert result.name == "Updated Name"
        assert result.description == "Updated description"
        assert result.population == 250
        assert result.region_id == "test_region_1"  # Unchanged
        assert result.poi_type == POIType.CITY  # Unchanged

    def test_attach_npcs_to_poi(self, city_poi):
        """Test attaching NPCs to a POI."""
        # Setup
        npc_ids = ["npc_1", "npc_2", "npc_3"]
        original_npc_count = len(city_poi.npcs)

        # Execute
        result = POIService.attach_npcs_to_poi(city_poi, npc_ids)

        # Verify
        assert result is city_poi
        assert len(result.npcs) == original_npc_count + 3
        for npc_id in npc_ids:
            assert npc_id in result.npcs

    def test_check_state_transition(self, city_poi):
        """Test checking if a POI should transition states."""
        # Setup - high damage should trigger transition
        damage_level = 0.8

        # Execute
        new_state = POIService.check_state_transition(city_poi, damage_level)

        # Verify
        assert new_state is not None
        assert new_state in [POIState.DECLINING, POIState.ABANDONED, POIState.RUINS]

    def test_calculate_resource_production(self, city_poi):
        """Test calculating resource production for a POI."""
        # Execute
        production = POIService.calculate_resource_production(city_poi)

        # Verify
        assert isinstance(production, dict)
        # The actual values depend on ResourceManagementService implementation
        # but we can verify it returns a dictionary

    def test_generate_poi_tilemap(self, city_poi):
        """Test generating a tilemap for a POI."""
        # Execute
        tilemap = POIService.generate_poi_tilemap(city_poi)

        # Verify
        assert isinstance(tilemap, dict)
        # The actual structure depends on TilemapService implementation
        # but we can verify it returns a dictionary

    def test_calculate_distance_between_pois(self, city_poi, town_poi):
        """Test calculating distance between two POIs."""
        # Execute
        distance = POIService.calculate_distance_between_pois(city_poi, town_poi)

        # Verify
        assert isinstance(distance, float)
        assert distance >= 0.0

    def test_find_nearby_pois(self, city_poi, town_poi, village_poi):
        """Test finding POIs near another POI."""
        # Setup
        all_pois = [town_poi, village_poi]
        max_distance = 30.0

        # Execute
        nearby_pois = POIService.find_nearby_pois(city_poi, all_pois, max_distance)

        # Verify
        assert isinstance(nearby_pois, list)
        # All returned POIs should be within max_distance
        for poi in nearby_pois:
            distance = POIService.calculate_distance_between_pois(city_poi, poi)
            assert distance <= max_distance

    def test_claim_region_hex(self, city_poi):
        """Test claiming a region hex for a POI."""
        # Setup
        original_hex_count = len(city_poi.claimed_region_hex_ids)
        new_hex = "new_hex_id_123"

        # Execute
        result = POIService.claim_region_hex(city_poi, new_hex)

        # Verify
        assert result is city_poi
        assert new_hex in result.claimed_region_hex_ids
        assert len(result.claimed_region_hex_ids) == original_hex_count + 1

    def test_unclaim_region_hex(self, city_poi):
        """Test unclaiming a region hex from a POI."""
        # Setup
        hex_to_remove = city_poi.claimed_region_hex_ids[0]
        original_hex_count = len(city_poi.claimed_region_hex_ids)

        # Execute
        result = POIService.unclaim_region_hex(city_poi, hex_to_remove)

        # Verify
        assert result is city_poi
        assert hex_to_remove not in result.claimed_region_hex_ids
        assert len(result.claimed_region_hex_ids) == original_hex_count - 1


class TestPOIStateService:
    """Test suite for POI State Service."""

    def test_transition_state(self, city_poi, mock_event_dispatcher):
        """Test transitioning a POI to a new state."""
        # Setup
        new_state = POIState.DECLINING
        reason = "Economic downturn"
        original_state = city_poi.current_state

        # Execute
        result = POIStateService.transition_state(city_poi, new_state, reason)

        # Verify
        assert result is city_poi
        assert result.current_state == POIState.DECLINING
        assert result.current_state != original_state

    def test_transition_to_ruins(self, city_poi, mock_event_dispatcher):
        """Test transitioning a POI to ruins state through proper sequence."""
        # Setup - must go through declining -> abandoned -> ruins

        # First transition to declining
        POIStateService.transition_state(
            city_poi, POIState.DECLINING, "Economic downturn"
        )
        assert city_poi.current_state == POIState.DECLINING

        # Then to abandoned
        POIStateService.transition_state(
            city_poi, POIState.ABANDONED, "Population left"
        )
        assert city_poi.current_state == POIState.ABANDONED

        # Finally to ruins
        result = POIStateService.transition_state(
            city_poi, POIState.RUINS, "Destroyed in war"
        )

        # Verify
        assert result is city_poi
        assert result.current_state == POIState.RUINS
        assert result.interaction_type == POIInteractionType.NEUTRAL
        assert result.population == 0  # Population reset to 0

    def test_transition_to_dungeon(self, ruins_poi, mock_event_dispatcher):
        """Test transitioning a POI to dungeon state."""
        # Setup
        new_state = POIState.DUNGEON
        reason = "Monsters moved in"

        # Execute
        result = POIStateService.transition_state(ruins_poi, new_state, reason)

        # Verify
        assert result is ruins_poi
        assert result.current_state == POIState.DUNGEON
        assert result.interaction_type == POIInteractionType.COMBAT
        assert result.population == 0

    def test_evaluate_state_damage(self, city_poi):
        """Test evaluating state based on damage level."""
        # Setup - high damage should trigger ruins
        damage_level = 0.8

        # Execute
        new_state = POIStateService.evaluate_state(city_poi, damage_level)

        # Verify
        assert new_state == POIState.RUINS

    def test_evaluate_state_population(self, city_poi):
        """Test evaluating state based on population."""
        # Setup - set population to very low
        city_poi.population = 0

        # Execute
        new_state = POIStateService.evaluate_state(city_poi)

        # Verify
        assert new_state == POIState.ABANDONED

    def test_apply_war_damage(self, city_poi, mock_event_dispatcher):
        """Test applying war damage to a POI."""
        # Setup - use damage that triggers valid transition (declining)
        damage_severity = (
            0.4  # Above declining threshold (0.3) but below abandoned (0.6)
        )
        original_population = city_poi.population

        # Execute
        result = POIStateService.apply_war_damage(city_poi, damage_severity)

        # Verify
        assert result is city_poi
        assert result.population < original_population  # Population should decrease
        assert "damage_history" in result.metadata
        assert "current_damage_level" in result.metadata
        assert result.metadata["current_damage_level"] == damage_severity
        # Should transition to declining state due to damage level
        assert result.current_state == POIState.DECLINING

    def test_update_population(self, city_poi, mock_event_dispatcher):
        """Test updating POI population."""
        # Setup
        new_population = 1200

        # Execute
        result = POIStateService.update_population(city_poi, new_population)

        # Verify
        assert result is city_poi
        assert result.population == new_population


class TestMetropolitanSpreadService:
    """Test suite for Metropolitan Spread Service."""

    def test_is_metropolis(self, city_poi):
        """Test checking if a POI is a metropolis."""
        # Setup - add metropolis tag and sufficient population
        city_poi.tags.append("metropolis")
        city_poi.population = 200  # Above MIN_METROPOLITAN_POPULATION

        # Execute
        result = MetropolitanSpreadService.is_metropolis(city_poi)

        # Verify
        assert result is True

    def test_is_not_metropolis_wrong_type(self, village_poi):
        """Test that non-city POIs are not metropolis."""
        # Setup
        village_poi.tags.append("metropolis")
        village_poi.population = 200

        # Execute
        result = MetropolitanSpreadService.is_metropolis(village_poi)

        # Verify
        assert result is False  # Wrong POI type

    def test_is_not_metropolis_low_population(self, city_poi):
        """Test that low population cities are not metropolis."""
        # Setup
        city_poi.tags.append("metropolis")
        city_poi.population = 50  # Below MIN_METROPOLITAN_POPULATION

        # Execute
        result = MetropolitanSpreadService.is_metropolis(city_poi)

        # Verify
        assert result is False  # Low population

    def test_setup_metropolis(self, city_poi, mock_event_dispatcher):
        """Test setting up a POI as a metropolis."""
        # Setup
        adjacent_hex_ids = ["hex_a", "hex_b", "hex_c"]

        # Execute
        result = MetropolitanSpreadService.setup_metropolis(city_poi, adjacent_hex_ids)

        # Verify
        assert result is city_poi
        assert "metropolis" in [tag.lower() for tag in result.tags]
        assert (
            result.population >= MetropolitanSpreadService.MIN_METROPOLITAN_POPULATION
        )
        assert (
            len(result.claimed_region_hex_ids) <= 3
        )  # MAX claimed hexes for metropolis

    def test_claim_region_hex(self, city_poi):
        """Test claiming a region hex."""
        # Setup
        hex_id = "test_hex_123"
        original_count = len(city_poi.claimed_region_hex_ids)

        # Execute
        result = MetropolitanSpreadService.claim_region_hex(city_poi, hex_id)

        # Verify
        assert result is city_poi
        assert hex_id in result.claimed_region_hex_ids
        assert len(result.claimed_region_hex_ids) == original_count + 1

    def test_unclaim_region_hex(self, city_poi):
        """Test unclaiming a region hex."""
        # Setup
        hex_to_remove = city_poi.claimed_region_hex_ids[0]
        original_count = len(city_poi.claimed_region_hex_ids)

        # Execute
        result = MetropolitanSpreadService.unclaim_region_hex(city_poi, hex_to_remove)

        # Verify
        assert result is city_poi
        assert hex_to_remove not in result.claimed_region_hex_ids
        assert len(result.claimed_region_hex_ids) == original_count - 1

    def test_calculate_sprawl_metrics(self, city_poi):
        """Test calculating sprawl metrics for a POI."""
        # Setup
        city_poi.tags.append("metropolis")
        city_poi.population = 200

        # Execute
        metrics = MetropolitanSpreadService.calculate_sprawl_metrics(city_poi)

        # Verify
        assert isinstance(metrics, dict)
        assert "is_metropolis" in metrics
        assert "claimed_hex_count" in metrics
        assert "max_claimable_hexes" in metrics
        assert "tier" in metrics

    def test_check_population_qualifies_for_metropolis(self, city_poi):
        """Test checking if population qualifies for metropolis."""
        # Setup - sufficient population
        city_poi.population = 200

        # Execute
        result = MetropolitanSpreadService.check_population_qualifies_for_metropolis(
            city_poi
        )

        # Verify
        assert result is True

        # Setup - insufficient population
        city_poi.population = 50

        # Execute
        result = MetropolitanSpreadService.check_population_qualifies_for_metropolis(
            city_poi
        )

        # Verify
        assert result is False

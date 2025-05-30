from backend.systems.economy.models import Resource
from backend.systems.population.models import POIPopulation
from backend.systems.population.service import PopulationService
from backend.systems.economy.models import Resource
from backend.systems.population.models import POIPopulation
from backend.systems.population.service import PopulationService
from backend.systems.economy.models import Resource
from backend.systems.population.models import POIPopulation
from backend.systems.population.service import PopulationService
from backend.systems.economy.models import Resource
from backend.systems.population.models import POIPopulation
from backend.systems.population.service import PopulationService
from backend.systems.economy.models import Resource
from backend.systems.population.models import POIPopulation
from backend.systems.population.service import PopulationService
from backend.systems.economy.models import Resource
from backend.systems.population.models import POIPopulation
from backend.systems.population.service import PopulationService
from typing import Type
from typing import List
"""
Comprehensive tests for the Population Service module.

This module provides comprehensive tests for the PopulationService class,
covering all major functionality to achieve 90% coverage.
"""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime
from typing import Dict, List

from backend.systems.population.service import PopulationService
from backend.systems.population.models import (
    POIPopulation,
    POIType,
    POIState,
    PopulationConfig,
)


@pytest.fixture
async def population_service():
    """Create a fresh PopulationService instance for testing."""
    # Reset the singleton instance
    PopulationService._instance = None
    service = PopulationService()
    await service.initialize()
    return service


@pytest.fixture
def sample_population():
    """Create a sample POI population for testing."""
    return POIPopulation(
        poi_id="test_city",
        name="Test City",
        poi_type=POIType.CITY,
        current_population=1000,
        target_population=1500,
        base_rate=5.0,
        state=POIState.NORMAL,
        last_updated=datetime.utcnow(),
        metadata={}
    )


@pytest.fixture
def sample_ruins():
    """Create a sample ruins POI for testing."""
    return POIPopulation(
        poi_id="test_ruins",
        name="Test Ruins",
        poi_type=POIType.CITY,
        current_population=0,
        target_population=1,  # Minimum valid value for validation
        base_rate=0.0,
        state=POIState.RUINS,
        last_updated=datetime.utcnow(),
        metadata={}
    )


class TestPopulationServiceBasicOperations:
    """Tests for basic CRUD operations."""

    async def test_create_population(self, population_service, sample_population):
        """Test creating a new population."""
        service = population_service
        
        # Create population
        result = await service.create_population(sample_population)
        
        assert result.poi_id == "test_city"
        assert result.name == "Test City"
        assert result.poi_type == POIType.CITY
        assert service.populations["test_city"] == sample_population

    async def test_get_population_exists(self, population_service, sample_population):
        """Test getting an existing population."""
        service = population_service
        await service.create_population(sample_population)
        
        result = await service.get_population("test_city")
        
        assert result is not None
        assert result.poi_id == "test_city"
        assert result.name == "Test City"

    async def test_get_population_not_exists(self, population_service):
        """Test getting a non-existent population."""
        service = population_service
        
        result = await service.get_population("nonexistent")
        
        assert result is None

    async def test_get_all_populations(self, population_service, sample_population):
        """Test getting all populations."""
        service = population_service
        
        # Initially empty
        populations = await service.get_all_populations()
        assert len(populations) == 0
        
        # Add a population
        await service.create_population(sample_population)
        populations = await service.get_all_populations()
        assert len(populations) == 1
        assert populations[0].poi_id == "test_city"

    async def test_set_global_multiplier(self, population_service):
        """Test setting the global multiplier."""
        service = population_service
        
        result = await service.set_global_multiplier(1.5)
        
        assert result == 1.5
        assert service.config.global_multiplier == 1.5

    async def test_set_base_rate(self, population_service):
        """Test setting base rate for a POI type."""
        service = population_service
        
        result = await service.set_base_rate(POIType.CITY, 10.0)
        
        assert isinstance(result, dict)
        assert result[POIType.CITY] == 10.0
        assert service.config.base_rates[POIType.CITY] == 10.0

    @patch("backend.systems.population.service.calculate_growth_rate")
    @patch("backend.systems.population.service.calculate_next_state")
    async def test_monthly_update_growth(self, mock_next_state, mock_growth_rate, population_service):
        """Test monthly update with population growth."""
        # Setup mock returns
        mock_growth_rate.return_value = 3.33  # This will floor to 3
        mock_next_state.return_value = POIState.NORMAL
        
        service = population_service
        
        # Create a population for testing
        population = POIPopulation(
            poi_id="test_city",
            name="Test City",
            poi_type=POIType.CITY,
            current_population=1000,
            target_population=1500,
            base_rate=5.0,
            state=POIState.NORMAL,
        )
        
        # Add to service
        await service.create_population(population)
        
        # Process monthly update
        events = await service.monthly_update()
        
        # Check results
        updated_pop = await service.get_population("test_city")
        assert updated_pop.current_population == 1003  # 1000 + floor(3.33) = 1003
        assert len(events) == 1
        assert events[0].new_population == 1003

    async def test_delete_population_success(self, population_service, sample_population):
        """Test deleting an existing population."""
        service = population_service
        await service.create_population(sample_population)
        
        result = await service.delete_population("test_city")
        
        assert result is True
        assert "test_city" not in service.populations

    async def test_delete_population_not_exists(self, population_service):
        """Test deleting a non-existent population."""
        service = population_service
        
        result = await service.delete_population("nonexistent")
        
        assert result is False


class TestPopulationServiceUpdates:
    """Tests for population update operations."""

    async def test_update_population_success(self, population_service, sample_population):
        """Test updating an existing population."""
        service = population_service
        await service.create_population(sample_population)
        
        # Modify the population
        updated_pop = POIPopulation(
            poi_id="test_city",
            name="Test City Updated",
            poi_type=POIType.CITY,
            current_population=1200,
            target_population=1800,
            base_rate=6.0,
            state=POIState.NORMAL,
            last_updated=datetime.utcnow(),
            metadata={"updated": True}
        )
        
        result = await service.update_population("test_city", updated_pop)
        
        assert result is not None
        assert result.current_population == 1200
        assert result.name == "Test City Updated"
        assert len(service.events) == 1  # Population change event

    async def test_update_population_with_state_change(self, population_service, sample_population):
        """Test updating population with state change."""
        service = population_service
        await service.create_population(sample_population)
        
        # Update to declining state
        updated_pop = POIPopulation(
            poi_id="test_city",
            name="Test City",
            poi_type=POIType.CITY,
            current_population=800,
            target_population=1500,
            base_rate=5.0,
            state=POIState.DECLINING,
            last_updated=datetime.utcnow(),
            metadata={}
        )
        
        result = await service.update_population("test_city", updated_pop)
        
        assert result is not None
        assert result.state == POIState.DECLINING
        assert len(service.events) == 1  # One event contains both population and state change
        assert service.events[0].old_state == POIState.NORMAL
        assert service.events[0].new_state == POIState.DECLINING

    async def test_update_population_not_exists(self, population_service):
        """Test updating a non-existent population."""
        service = population_service
        
        updated_pop = POIPopulation(
            poi_id="nonexistent",
            name="Nonexistent",
            poi_type=POIType.CITY,
            current_population=1000,
            target_population=1500,
            base_rate=5.0,
            state=POIState.NORMAL,
            last_updated=datetime.utcnow(),
            metadata={}
        )
        
        result = await service.update_population("nonexistent", updated_pop)
        
        assert result is None


class TestPopulationServiceWarImpact:
    """Tests for war impact handling."""

    @patch("backend.systems.population.service.calculate_war_impact")
    async def test_handle_war_impact_success(self, mock_war_impact, population_service, sample_population):
        """Test handling war impact on a population."""
        mock_war_impact.return_value = 300  # 30% population loss
        
        service = population_service
        await service.create_population(sample_population)
        
        result = await service.handle_war_impact("test_city", "war_123", 0.5)
        
        assert result is not None
        assert result.current_population == 700  # 1000 - 300
        mock_war_impact.assert_called_once()

    @patch("backend.systems.population.service.calculate_war_impact")
    async def test_handle_war_impact_state_transition(self, mock_war_impact, population_service, sample_population):
        """Test war impact causing state transition."""
        mock_war_impact.return_value = 850  # Heavy damage causing ruins
        
        service = population_service
        await service.create_population(sample_population)
        
        result = await service.handle_war_impact("test_city", "war_123", 0.9)
        
        assert result is not None
        assert result.current_population == 150  # 1000 - 850
        assert result.state == POIState.RUINS  # Should transition to ruins

    async def test_handle_war_impact_not_exists(self, population_service):
        """Test handling war impact on non-existent population."""
        service = population_service
        
        result = await service.handle_war_impact("nonexistent", "war_123", 0.5)
        
        assert result is None


class TestPopulationServiceCatastropheImpact:
    """Tests for catastrophe impact handling."""

    @patch("backend.systems.population.service.calculate_catastrophe_impact")
    async def test_handle_catastrophe_success(self, mock_catastrophe_impact, population_service, sample_population):
        """Test handling catastrophe impact on a population."""
        mock_catastrophe_impact.return_value = 200  # 20% population loss
        
        service = population_service
        await service.create_population(sample_population)
        
        result = await service.handle_catastrophe("test_city", "earthquake", 0.3)
        
        assert result is not None
        assert result.current_population == 800  # 1000 - 200
        mock_catastrophe_impact.assert_called_once()

    @patch("backend.systems.population.service.calculate_catastrophe_impact")
    async def test_handle_catastrophe_severe_impact(self, mock_catastrophe_impact, population_service, sample_population):
        """Test handling catastrophe with severe impact causing state transition."""
        mock_catastrophe_impact.return_value = 900  # 90% population loss
        
        service = population_service
        await service.create_population(sample_population)
        
        result = await service.handle_catastrophe("test_city", "earthquake", 0.9)
        
        assert result is not None
        assert result.current_population < 1000  # Should reduce population
        assert result.state == POIState.DECLINING  # Should transition to declining with severe impact
        assert "catastrophe_history" in result.metadata

    async def test_handle_catastrophe_not_exists(self, population_service):
        """Test handling catastrophe on non-existent population."""
        service = population_service
        
        result = await service.handle_catastrophe("nonexistent", "earthquake", 0.5)
        
        assert result is None


class TestPopulationServiceDungeonConversion:
    """Tests for dungeon conversion functionality."""

    async def test_convert_ruins_to_dungeon_success(self, population_service, sample_ruins):
        """Test converting ruins to dungeon successfully."""
        service = population_service
        await service.create_population(sample_ruins)
        
        result = await service.convert_ruins_to_dungeon("test_ruins", "undead")
        
        assert result is not None
        assert result.state == POIState.DUNGEON
        assert result.current_population == 0
        assert "dungeon_type" in result.metadata
        assert result.metadata["dungeon_type"] == "undead"
        assert "dungeon_difficulty" in result.metadata
        assert "treasure_level" in result.metadata
        assert "conversion_date" in result.metadata

    async def test_convert_ruins_to_dungeon_auto_monster(self, population_service, sample_ruins):
        """Test converting ruins to dungeon with auto-generated monster type."""
        service = population_service
        await service.create_population(sample_ruins)
        
        result = await service.convert_ruins_to_dungeon("test_ruins")  # No monster type provided
        
        assert result is not None
        assert result.state == POIState.DUNGEON
        assert result.current_population == 0
        assert "dungeon_type" in result.metadata  # Auto-generated when no monster_type provided
        assert "dungeon_difficulty" in result.metadata
        assert "treasure_level" in result.metadata
        assert "conversion_date" in result.metadata

    async def test_convert_ruins_to_dungeon_not_ruins(self, population_service, sample_population):
        """Test converting non-ruins POI fails."""
        service = population_service
        await service.create_population(sample_population)
        
        result = await service.convert_ruins_to_dungeon("test_city", "undead")
        
        assert result is None

    async def test_convert_ruins_to_dungeon_not_exists(self, population_service):
        """Test converting non-existent ruins fails."""
        service = population_service
        
        result = await service.convert_ruins_to_dungeon("nonexistent", "undead")
        
        assert result is None


class TestPopulationServiceRepopulation:
    """Tests for repopulation functionality."""

    async def test_start_repopulation_from_ruins(self, population_service, sample_ruins):
        """Test starting repopulation from ruins."""
        service = population_service
        await service.create_population(sample_ruins)
        
        result = await service.start_repopulation("test_ruins", 50)
        
        assert result is not None
        assert result.state == POIState.REPOPULATING
        assert result.current_population == 50
        assert result.base_rate > 0  # Should have positive growth rate

    async def test_start_repopulation_from_abandoned(self, population_service):
        """Test starting repopulation from abandoned state."""
        abandoned_pop = POIPopulation(
            poi_id="test_abandoned",
            name="Test Abandoned",
            poi_type=POIType.VILLAGE,
            current_population=5,
            target_population=200,
            base_rate=0.0,
            state=POIState.ABANDONED,
            last_updated=datetime.utcnow(),
            metadata={}
        )
        
        service = population_service
        await service.create_population(abandoned_pop)
        
        result = await service.start_repopulation("test_abandoned", 25)
        
        assert result is not None
        assert result.state == POIState.REPOPULATING
        assert result.current_population == 25

    async def test_start_repopulation_invalid_state(self, population_service, sample_population):
        """Test starting repopulation on invalid state fails."""
        service = population_service
        await service.create_population(sample_population)
        
        result = await service.start_repopulation("test_city", 100)
        
        assert result is None

    async def test_start_repopulation_not_exists(self, population_service):
        """Test starting repopulation on non-existent POI fails."""
        service = population_service
        
        result = await service.start_repopulation("nonexistent", 50)
        
        assert result is None


class TestPopulationServicePOITypeUpdate:
    """Tests for POI type update functionality."""

    async def test_update_poi_type_success(self, population_service, sample_population):
        """Test updating POI type successfully."""
        service = population_service
        await service.create_population(sample_population)
        
        result = await service.update_poi_type("test_city", POIType.OUTPOST)
        
        assert result is not None
        assert result.poi_type == POIType.OUTPOST
        # Should update base rate based on new type
        assert result.base_rate == service.config.base_rates.get(POIType.OUTPOST, 1.0)

    async def test_update_poi_type_not_exists(self, population_service):
        """Test updating POI type on non-existent POI fails."""
        service = population_service
        
        result = await service.update_poi_type("nonexistent", POIType.OUTPOST)
        
        assert result is None


class TestPopulationServiceResourceManagement:
    """Tests for resource management functionality."""

    async def test_update_resource_impact_success(self, population_service, sample_population):
        """Test updating resource impact successfully."""
        service = population_service
        await service.create_population(sample_population)
        
        resource_impact = {"food": 1.2, "water": 0.8}
        
        result = await service.update_resource_impact("test_city", resource_impact)
        
        assert result is not None
        assert result.resource_impact == resource_impact

    async def test_update_resource_impact_not_exists(self, population_service):
        """Test updating resource impact on non-existent POI fails."""
        service = population_service
        
        result = await service.update_resource_impact("nonexistent", {"food": 1.0})
        
        assert result is None

    async def test_calculate_resource_consumption_success(self, population_service, sample_population):
        """Test calculating resource consumption successfully."""
        service = population_service
        await service.create_population(sample_population)
        
        # First set resource impact rates
        resource_impact = {"food": 0.1, "water": 0.05}
        await service.update_resource_impact("test_city", resource_impact)
        
        consumption = await service.calculate_resource_consumption("test_city")
        
        assert "food" in consumption
        assert "water" in consumption
        # With 1000 population and 0.1 rate: 1000 * 0.1 = 100
        assert consumption["food"] == 100.0
        # With 1000 population and 0.05 rate: 1000 * 0.05 = 50
        assert consumption["water"] == 50.0

    async def test_calculate_resource_consumption_not_exists(self, population_service):
        """Test calculating resource consumption for non-existent POI."""
        service = population_service
        
        consumption = await service.calculate_resource_consumption("nonexistent")
        
        assert consumption == {}

    async def test_calculate_total_resource_consumption(self, population_service, sample_population):
        """Test calculating total resource consumption across all POIs."""
        service = population_service
        
        # Create first POI with resource impact
        await service.create_population(sample_population)
        await service.update_resource_impact("test_city", {"food": 0.1, "water": 0.05})
        
        # Create second POI
        second_population = POIPopulation(
            poi_id="test_town",
            name="Test Town",
            poi_type=POIType.TOWN,
            current_population=500,
            target_population=1000,
            base_rate=3.0,
            state=POIState.NORMAL,
            last_updated=datetime.utcnow(),
            metadata={}
        )
        await service.create_population(second_population)
        await service.update_resource_impact("test_town", {"food": 0.08, "materials": 0.02})
        
        total_consumption = await service.calculate_total_resource_consumption()
        
        assert "food" in total_consumption
        # test_city: 1000 * 0.1 = 100, test_town: 500 * 0.08 = 40, total = 140
        assert total_consumption["food"] == 140.0
        assert "water" in total_consumption
        # Only test_city has water: 1000 * 0.05 = 50
        assert total_consumption["water"] == 50.0
        assert "materials" in total_consumption
        # Only test_town has materials: 500 * 0.02 = 10
        assert total_consumption["materials"] == 10.0

    @patch("backend.systems.population.service.calculate_resource_shortage_impact")
    async def test_handle_resource_shortage_success(self, mock_shortage_impact, population_service, sample_population):
        """Test handling resource shortage."""
        mock_shortage_impact.return_value = 100  # 10% population loss
        
        service = population_service
        await service.create_population(sample_population)
        
        result = await service.handle_resource_shortage("test_city", "food", 0.5)
        
        assert result is not None
        assert result.current_population == 900  # 1000 - 100
        mock_shortage_impact.assert_called_once()

    @patch("backend.systems.population.service.calculate_resource_shortage_impact")
    async def test_handle_resource_shortage_severe(self, mock_shortage_impact, population_service, sample_population):
        """Test handling severe resource shortage."""
        mock_shortage_impact.return_value = 600  # 60% population loss
        
        service = population_service
        await service.create_population(sample_population)
        
        result = await service.handle_resource_shortage("test_city", "water", 0.8)
        
        assert result is not None
        assert result.current_population == 400  # 1000 - 600
        assert result.state == POIState.DECLINING  # Should transition

    async def test_handle_resource_shortage_not_exists(self, population_service):
        """Test handling resource shortage on non-existent POI."""
        service = population_service
        
        result = await service.handle_resource_shortage("nonexistent", "food", 0.5)
        
        assert result is None


class TestPopulationServiceStatus:
    """Tests for status and reporting functionality."""

    async def test_get_poi_status_success(self, population_service, sample_population):
        """Test getting POI status successfully."""
        service = population_service
        await service.create_population(sample_population)
        
        status = await service.get_poi_status("test_city")
        
        assert status["exists"] is True
        assert "current_population" in status
        assert "target_population" in status
        assert "state" in status
        assert "type" in status
        assert "name" in status
        assert status["poi_id"] == "test_city"
        assert status["current_population"] == 1000

    async def test_get_poi_status_not_exists(self, population_service):
        """Test getting status for non-existent POI."""
        service = population_service
        
        status = await service.get_poi_status("nonexistent")
        
        assert status["exists"] is False
        assert status["poi_id"] == "nonexistent"
        assert "message" in status

    async def test_get_population_events_no_limit(self, population_service, sample_population):
        """Test getting population events without limit."""
        service = population_service
        await service.create_population(sample_population)
        
        # Update the population to generate an event
        updated_pop = POIPopulation(
            poi_id="test_city",
            name="Test City",
            poi_type=POIType.CITY,
            current_population=1200,
            target_population=1500,
            base_rate=5.0,
            state=POIState.NORMAL,
            last_updated=datetime.utcnow(),
            metadata={}
        )
        await service.update_population("test_city", updated_pop)
        
        events = await service.get_population_events()
        
        assert len(events) > 0
        assert isinstance(events[0], dict)
        assert "poi_id" in events[0]
        assert "old_population" in events[0]
        assert "new_population" in events[0]
        assert "change_type" in events[0]

    async def test_get_population_events_with_limit(self, population_service, sample_population):
        """Test getting population events with limit."""
        service = population_service
        await service.create_population(sample_population)
        
        # Trigger multiple events
        for i in range(5):
            updated_pop = POIPopulation(
                poi_id="test_city",
                name="Test City",
                poi_type=POIType.CITY,
                current_population=1000 + i,
                target_population=1500,
                base_rate=5.0,
                state=POIState.NORMAL,
                last_updated=datetime.utcnow(),
                metadata={}
            )
            await service.update_population("test_city", updated_pop)
        
        events = await service.get_population_events(limit=3)
        
        assert isinstance(events, list)
        assert len(events) <= 3

    async def test_get_config(self, population_service):
        """Test getting population configuration."""
        service = population_service
        
        config = await service.get_config()
        
        assert isinstance(config, PopulationConfig)
        assert hasattr(config, 'global_multiplier')
        assert hasattr(config, 'base_rates')


class TestPopulationServiceMigration:
    """Test migration functionality."""

    @pytest.mark.asyncio
    async def test_handle_migration_success(self, population_service):
        """Test successful migration between POIs."""
        # Create source POI with population
        source = POIPopulation(
            poi_id="source_poi",
            name="Source City",
            poi_type=POIType.CITY,
            current_population=1000,
            target_population=2000,
            min_population=100,
            base_rate=1.5,
            state=POIState.NORMAL,
        )
        
        # Create destination POI
        destination = POIPopulation(
            poi_id="dest_poi",
            name="Destination City", 
            poi_type=POIType.CITY,
            current_population=500,
            target_population=2000,
            min_population=100,
            base_rate=1.5,
            state=POIState.NORMAL,
        )
        
        await population_service.create_population(source)
        await population_service.create_population(destination)
        
        # Perform migration
        result_source, result_dest = await population_service.handle_migration(
            "source_poi", "dest_poi", 200, "economic opportunity"
        )
        
        # Verify populations updated
        assert result_source.current_population == 800  # 1000 - 200
        assert result_dest.current_population == 700    # 500 + 200
        
        # Verify migration history recorded
        assert "migration_history" in result_source.metadata
        assert "migration_history" in result_dest.metadata
        assert len(result_source.metadata["migration_history"]) == 1
        assert len(result_dest.metadata["migration_history"]) == 1
        
        # Verify migration details
        source_migration = result_source.metadata["migration_history"][0]
        assert source_migration["direction"] == "outgoing"
        assert source_migration["amount"] == 200
        assert source_migration["partner"] == "dest_poi"
        assert source_migration["reason"] == "economic opportunity"
        
        dest_migration = result_dest.metadata["migration_history"][0]
        assert dest_migration["direction"] == "incoming"
        assert dest_migration["amount"] == 200
        assert dest_migration["partner"] == "source_poi"

    @pytest.mark.asyncio
    async def test_handle_migration_insufficient_population(self, population_service):
        """Test migration with insufficient source population."""
        source = POIPopulation(
            poi_id="source_small",
            name="Small Village",
            poi_type=POIType.VILLAGE,
            current_population=50,  # Less than migration amount
            target_population=200,
            min_population=10,
            base_rate=1.0,
            state=POIState.NORMAL,
        )
        
        destination = POIPopulation(
            poi_id="dest_city",
            name="Big City",
            poi_type=POIType.CITY,
            current_population=1000,
            target_population=3000,
            min_population=100,
            base_rate=1.5,
            state=POIState.NORMAL,
        )
        
        await population_service.create_population(source)
        await population_service.create_population(destination)
        
        # Try to migrate more than available
        result_source, result_dest = await population_service.handle_migration(
            "source_small", "dest_city", 100, "forced evacuation"
        )
        
        # Should only migrate available population
        assert result_source.current_population == 0   # 50 - 50 (all available)
        assert result_dest.current_population == 1050  # 1000 + 50

    @pytest.mark.asyncio
    async def test_handle_migration_source_not_found(self, population_service):
        """Test migration when source POI doesn't exist."""
        destination = POIPopulation(
            poi_id="dest_exists",
            name="Destination",
            poi_type=POIType.CITY,
            current_population=500,
            target_population=1000,
            min_population=50,
            base_rate=1.0,
            state=POIState.NORMAL,
        )
        
        await population_service.create_population(destination)
        
        result_source, result_dest = await population_service.handle_migration(
            "nonexistent_source", "dest_exists", 100, "test"
        )
        
        assert result_source is None
        assert result_dest is not None
        assert result_dest.poi_id == "dest_exists"

    @pytest.mark.asyncio
    async def test_handle_migration_both_not_found(self, population_service):
        """Test migration when both POIs don't exist."""
        result_source, result_dest = await population_service.handle_migration(
            "nonexistent_source", "nonexistent_dest", 100, "test"
        )
        
        assert result_source is None
        assert result_dest is None


class TestPopulationServiceSeasonalEffects:
    """Test seasonal effect functionality."""

    @pytest.mark.asyncio
    async def test_handle_seasonal_effect_growth_modifier(self, population_service):
        """Test seasonal effect with growth modifier."""
        # Setup a population
        population = POIPopulation(
            poi_id="city1",
            name="Test City",
            poi_type=POIType.CITY,
            current_population=1000,
            target_population=2000,
            state=POIState.NORMAL,
        )
        await population_service.create_population(population)

        # Apply growth seasonal effect (effect_strength > 1.0)
        result = await population_service.handle_seasonal_effect(
            "city1", "spring", 1.2, 3  # 20% growth boost for 3 months
        )

        assert result is not None
        assert result.poi_id == "city1"
        assert result.current_population > 1000  # Population should increase
        assert result.current_population == int(1000 * 1.2)  # 1200
        assert "seasonal_history" in result.metadata
        assert len(result.metadata["seasonal_history"]) == 1
        
        history = result.metadata["seasonal_history"][0]
        assert history["season"] == "spring"
        assert history["effect_type"] == "growth_boost"
        assert history["effect_strength"] == 1.2
        assert history["duration_months"] == 3
        assert history["old_population"] == 1000
        assert history["new_population"] == 1200

    @pytest.mark.asyncio
    async def test_handle_seasonal_effect_death_modifier(self, population_service):
        """Test seasonal effect with death rate modifier."""
        # Setup a population
        population = POIPopulation(
            poi_id="city1",
            name="Test City",
            poi_type=POIType.CITY,
            current_population=1000,
            target_population=2000,
            state=POIState.NORMAL,
        )
        await population_service.create_population(population)

        # Apply winter seasonal effect (effect_strength < 1.0)
        result = await population_service.handle_seasonal_effect(
            "city1", "winter", 0.8, 3  # 20% population reduction for 3 months
        )

        assert result is not None
        assert result.poi_id == "city1"
        assert result.current_population < 1000  # Population should decrease
        assert result.current_population == int(1000 * 0.8)  # 800
        assert "seasonal_history" in result.metadata
        assert len(result.metadata["seasonal_history"]) == 1
        
        history = result.metadata["seasonal_history"][0]
        assert history["season"] == "winter"
        assert history["effect_type"] == "growth_reduction"
        assert history["effect_strength"] == 0.8
        assert history["duration_months"] == 3
        assert history["old_population"] == 1000
        assert history["new_population"] == 800

    @pytest.mark.asyncio
    async def test_handle_seasonal_effect_resource_efficiency(self, population_service):
        """Test seasonal effect with neutral effect (no population change)."""
        # Setup a population
        population = POIPopulation(
            poi_id="city1",
            name="Test City",
            poi_type=POIType.CITY,
            current_population=1000,
            target_population=2000,
            state=POIState.NORMAL,
        )
        await population_service.create_population(population)

        # Apply neutral seasonal effect (effect_strength = 1.0)
        result = await population_service.handle_seasonal_effect(
            "city1", "autumn", 1.0, 2  # Neutral effect for 2 months
        )

        assert result is not None
        assert result.poi_id == "city1"
        assert result.current_population == 1000  # Population should stay the same
        assert "seasonal_history" in result.metadata
        assert len(result.metadata["seasonal_history"]) == 1
        
        history = result.metadata["seasonal_history"][0]
        assert history["season"] == "autumn"
        assert history["effect_type"] == "neutral"
        assert history["effect_strength"] == 1.0
        assert history["duration_months"] == 2
        assert history["old_population"] == 1000
        assert history["new_population"] == 1000

    @pytest.mark.asyncio
    async def test_handle_seasonal_effect_unknown_type(self, population_service):
        """Test seasonal effect with extreme growth values."""
        # Setup a population
        population = POIPopulation(
            poi_id="city1",
            name="Test City",
            poi_type=POIType.CITY,
            current_population=1000,
            target_population=2000,
            state=POIState.NORMAL,
        )
        await population_service.create_population(population)

        # Apply extreme growth seasonal effect
        result = await population_service.handle_seasonal_effect(
            "city1", "magical_spring", 2.0, 1  # Double population for 1 month
        )

        assert result is not None
        assert result.poi_id == "city1"
        assert result.current_population == 2000  # Population doubled
        assert "seasonal_history" in result.metadata
        assert len(result.metadata["seasonal_history"]) == 1
        
        history = result.metadata["seasonal_history"][0]
        assert history["season"] == "magical_spring"
        assert history["effect_type"] == "growth_boost"
        assert history["effect_strength"] == 2.0
        assert history["duration_months"] == 1

    @pytest.mark.asyncio
    async def test_handle_seasonal_effect_poi_not_found(self, population_service):
        """Test seasonal effect when POI doesn't exist."""
        result = await population_service.handle_seasonal_effect(
            "nonexistent", "spring", 1.0, 1  # No effect for 1 month
        )
        
        assert result is None 
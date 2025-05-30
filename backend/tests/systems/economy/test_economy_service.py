from backend.systems.events.dispatcher import EventDispatcher
from backend.systems.economy.models import Resource
from backend.systems.economy.repositories import EconomyRepository
from backend.systems.events.dispatcher import EventDispatcher
from backend.systems.economy.models import Resource
from backend.systems.economy.repositories import EconomyRepository
from backend.systems.events.dispatcher import EventDispatcher
from backend.systems.economy.models import Resource
from backend.systems.economy.repositories import EconomyRepository
from backend.systems.events.dispatcher import EventDispatcher
from backend.systems.economy.models import Resource
from backend.systems.economy.repositories import EconomyRepository
from backend.systems.events.dispatcher import EventDispatcher
from backend.systems.economy.models import Resource
from backend.systems.economy.repositories import EconomyRepository
from backend.systems.events.dispatcher import EventDispatcher
from backend.systems.economy.models import Resource
from backend.systems.economy.repositories import EconomyRepository
from typing import Type
"""
Tests for the economy service module.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from backend.systems.economy.services.economy_service import EconomyService
from backend.systems.economy.models.economic_metric import EconomicMetric, MetricType
from backend.systems.economy.models.resource import Resource, ResourceType
from backend.systems.economy.repositories.economy_repository import EconomyRepository
from backend.systems.events import EventDispatcher


@pytest.fixture
def mock_repository():
    """Create a mock repository for testing."""
    repo = AsyncMock(spec=EconomyRepository)
    return repo


@pytest.fixture
def mock_event_dispatcher():
    """Create a mock event dispatcher for testing."""
    dispatcher = AsyncMock(spec=EventDispatcher)
    dispatcher.publish = AsyncMock()
    return dispatcher


@pytest.fixture
def economy_service(mock_repository, mock_event_dispatcher):
    """Create an economy service instance for testing."""
    return EconomyService(mock_repository, mock_event_dispatcher)


@pytest.fixture
def sample_resource():
    """Create a sample resource for testing."""
    # Create a mock resource object with the fields we need
    resource = MagicMock()
    resource.id = 1
    resource.name = "Gold"
    resource.type = ResourceType.GOLD.value
    resource.price = 100.0
    resource.description = "Gold resource"
    return resource


@pytest.fixture
def sample_supply_metric():
    """Create a sample supply metric for testing."""
    return EconomicMetric(
        id=1,
        metric_type=MetricType.SUPPLY,
        value=80.0,
        resource_id=1,
        region_id=None,
        faction_id=None,
        timestamp=datetime.utcnow()
    )


@pytest.fixture
def sample_demand_metric():
    """Create a sample demand metric for testing."""
    return EconomicMetric(
        id=2,
        metric_type=MetricType.DEMAND,
        value=120.0,
        resource_id=1,
        region_id=None,
        faction_id=None,
        timestamp=datetime.utcnow()
    )


class TestEconomyService:
    """Test suite for the EconomyService class."""

    @pytest.mark.asyncio
    async def test_update_supply_demand_with_existing_metrics(
        self, economy_service, mock_repository, mock_event_dispatcher, sample_resource, 
        sample_supply_metric, sample_demand_metric
    ):
        """Test supply/demand update with existing metrics."""
        # Setup mocks
        mock_repository.get_resource.return_value = sample_resource
        mock_repository.get_latest_metric.side_effect = [
            sample_supply_metric,  # supply metric
            sample_demand_metric   # demand metric
        ]
        mock_repository.save_metric = AsyncMock()

        # Execute
        supply, demand = await economy_service.update_supply_demand(1)

        # Verify
        assert supply == 80.0
        assert demand == 120.0
        assert mock_repository.get_resource.call_count == 1
        assert mock_repository.get_latest_metric.call_count == 2
        assert mock_repository.save_metric.call_count == 2
        assert mock_event_dispatcher.publish.call_count == 1

        # Check event content
        event_call = mock_event_dispatcher.publish.call_args[0][0]
        assert event_call["event_type"] == "resource.supply_demand_updated"
        assert event_call["resource_id"] == 1
        assert event_call["supply"] == 80.0
        assert event_call["demand"] == 120.0

    @pytest.mark.asyncio
    async def test_update_supply_demand_with_no_existing_metrics(
        self, economy_service, mock_repository, mock_event_dispatcher, sample_resource
    ):
        """Test supply/demand update with no existing metrics (defaults)."""
        # Setup mocks
        mock_repository.get_resource.return_value = sample_resource
        mock_repository.get_latest_metric.return_value = None
        mock_repository.save_metric = AsyncMock()

        # Execute
        supply, demand = await economy_service.update_supply_demand(1)

        # Verify defaults are used
        assert supply == 100.0
        assert demand == 100.0
        assert mock_repository.save_metric.call_count == 2

    @pytest.mark.asyncio
    async def test_update_supply_demand_resource_not_found(
        self, economy_service, mock_repository
    ):
        """Test supply/demand update when resource doesn't exist."""
        # Setup mocks
        mock_repository.get_resource.return_value = None

        # Execute and verify exception
        with pytest.raises(ValueError, match="Resource with ID 999 not found"):
            await economy_service.update_supply_demand(999)

    @pytest.mark.asyncio
    async def test_adjust_price_basic(
        self, economy_service, mock_repository, mock_event_dispatcher, sample_resource,
        sample_supply_metric, sample_demand_metric
    ):
        """Test basic price adjustment based on supply/demand."""
        # Setup mocks
        mock_repository.get_resource.return_value = sample_resource
        mock_repository.get_latest_metric.side_effect = [
            sample_supply_metric,  # supply metric
            sample_demand_metric   # demand metric
        ]
        mock_repository.save_metric = AsyncMock()

        # Execute
        new_price = await economy_service.adjust_price(1)

        # Verify price calculation
        # supply_demand_ratio = 80.0 / 120.0 = 0.667
        # new_price = 100.0 * (2.0 - 0.667) = 133.3
        expected_price = 100.0 * (2.0 - (80.0 / 120.0))
        assert abs(new_price - expected_price) < 0.01

        # Verify price adjustment event
        price_event_call = None
        for call in mock_event_dispatcher.publish.call_args_list:
            event = call[0][0]
            if event["event_type"] == "resource.price_adjusted":
                price_event_call = event
                break
        
        assert price_event_call is not None
        assert price_event_call["resource_id"] == 1
        assert price_event_call["old_price"] == 100.0

    @pytest.mark.asyncio
    async def test_adjust_price_minimum_threshold(
        self, economy_service, mock_repository, sample_resource
    ):
        """Test price adjustment respects minimum threshold."""
        # Setup very high supply, low demand scenario
        high_supply_metric = EconomicMetric(
            metric_type=MetricType.SUPPLY, value=1000.0, resource_id=1
        )
        low_demand_metric = EconomicMetric(
            metric_type=MetricType.DEMAND, value=10.0, resource_id=1
        )
        
        mock_repository.get_resource.return_value = sample_resource
        mock_repository.get_latest_metric.side_effect = [
            high_supply_metric,
            low_demand_metric
        ]
        mock_repository.save_metric = AsyncMock()

        # Execute
        new_price = await economy_service.adjust_price(1)

        # Verify minimum price threshold (50% of base value)
        min_price = sample_resource.price * 0.5
        assert new_price >= min_price

    @pytest.mark.asyncio
    async def test_transfer_resources_success(
        self, economy_service, mock_repository, mock_event_dispatcher
    ):
        """Test successful resource transfer between regions."""
        # Setup mocks
        mock_repository.get_resource_amount.return_value = 150.0  # Source has enough
        mock_repository.update_resource_amount = AsyncMock()
        mock_repository.get_latest_metric.return_value = EconomicMetric(
            metric_type=MetricType.TRADE_VOLUME, value=100.0, resource_id=1
        )
        mock_repository.save_metric = AsyncMock()

        # Mock the adjust_price method
        with patch.object(economy_service, 'adjust_price', new_callable=AsyncMock) as mock_adjust:
            mock_adjust.return_value = 110.0

            # Execute
            result = await economy_service.transfer_resources(
                source_region_id=1, target_region_id=2, resource_id=1, amount=50.0
            )

            # Verify success
            assert result is True
            
            # Verify resource amount updates
            assert mock_repository.update_resource_amount.call_count == 2
            
            # Check source deduction
            source_call = mock_repository.update_resource_amount.call_args_list[0]
            assert source_call[1]["region_id"] == 1
            assert source_call[1]["resource_id"] == 1
            assert source_call[1]["amount_change"] == -50.0
            
            # Check target addition
            target_call = mock_repository.update_resource_amount.call_args_list[1]
            assert target_call[1]["region_id"] == 2
            assert target_call[1]["resource_id"] == 1
            assert target_call[1]["amount_change"] == 50.0

            # Verify trade volume update
            mock_repository.save_metric.assert_called()
            trade_metric_call = mock_repository.save_metric.call_args_list[-1][0][0]
            assert trade_metric_call.metric_type == MetricType.TRADE_VOLUME
            assert trade_metric_call.value == 150.0  # 100.0 + 50.0

            # Verify trade event
            trade_event_call = None
            for call in mock_event_dispatcher.publish.call_args_list:
                event = call[0][0]
                if event["event_type"] == "resource.traded":
                    trade_event_call = event
                    break
            
            assert trade_event_call is not None
            assert trade_event_call["source_region_id"] == 1
            assert trade_event_call["target_region_id"] == 2
            assert trade_event_call["resource_id"] == 1
            assert trade_event_call["amount"] == 50.0

    @pytest.mark.asyncio
    async def test_transfer_resources_insufficient_amount(
        self, economy_service, mock_repository
    ):
        """Test resource transfer failure due to insufficient amount."""
        # Setup mocks - source doesn't have enough
        mock_repository.get_resource_amount.return_value = 30.0  # Less than requested 50.0

        # Execute
        result = await economy_service.transfer_resources(
            source_region_id=1, target_region_id=2, resource_id=1, amount=50.0
        )

        # Verify failure
        assert result is False
        
        # Verify no updates were made
        mock_repository.update_resource_amount.assert_not_called()

    @pytest.mark.asyncio
    async def test_modify_supply_demand_from_event(
        self, economy_service, mock_repository, sample_supply_metric, sample_demand_metric
    ):
        """Test supply/demand modification from world events."""
        # Setup mocks
        mock_repository.get_latest_metric.side_effect = [
            sample_supply_metric,  # supply metric
            sample_demand_metric   # demand metric
        ]
        mock_repository.save_metric = AsyncMock()

        # Mock the adjust_price method
        with patch.object(economy_service, 'adjust_price', new_callable=AsyncMock) as mock_adjust:
            mock_adjust.return_value = 120.0

            # Execute with event modifiers
            event = {
                "resource_id": 1,
                "supply_modifier": -0.2,  # 20% decrease in supply
                "demand_modifier": 0.3    # 30% increase in demand
            }
            
            await economy_service.modify_supply_demand_from_event(event)

            # Verify metric saves
            assert mock_repository.save_metric.call_count == 2
            
            # Check supply metric (80.0 * (1 - 0.2) = 64.0)
            supply_call = mock_repository.save_metric.call_args_list[0][0][0]
            assert supply_call.metric_type == MetricType.SUPPLY
            assert supply_call.value == 64.0
            
            # Check demand metric (120.0 * (1 + 0.3) = 156.0)
            demand_call = mock_repository.save_metric.call_args_list[1][0][0]
            assert demand_call.metric_type == MetricType.DEMAND
            assert demand_call.value == 156.0
            
            # Verify price adjustment was called
            mock_adjust.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_modify_supply_demand_from_event_no_resource_id(
        self, economy_service, mock_repository
    ):
        """Test event modification with no resource_id does nothing."""
        # Execute with event missing resource_id
        event = {
            "supply_modifier": -0.2,
            "demand_modifier": 0.3
        }
        
        await economy_service.modify_supply_demand_from_event(event)

        # Verify no repository calls were made
        mock_repository.get_latest_metric.assert_not_called()
        mock_repository.save_metric.assert_not_called()

    @pytest.mark.asyncio
    async def test_modify_supply_demand_from_event_with_defaults(
        self, economy_service, mock_repository
    ):
        """Test event modification with default modifier values."""
        # Setup mocks with no existing metrics
        mock_repository.get_latest_metric.return_value = None
        mock_repository.save_metric = AsyncMock()

        # Mock the adjust_price method
        with patch.object(economy_service, 'adjust_price', new_callable=AsyncMock):
            # Execute with minimal event (defaults to 0 modifiers)
            event = {"resource_id": 1}
            
            await economy_service.modify_supply_demand_from_event(event)

            # Verify default values used (100.0 * (1 + 0) = 100.0)
            assert mock_repository.save_metric.call_count == 2
            
            supply_call = mock_repository.save_metric.call_args_list[0][0][0]
            assert supply_call.value == 100.0
            
            demand_call = mock_repository.save_metric.call_args_list[1][0][0]
            assert demand_call.value == 100.0

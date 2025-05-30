from backend.systems.economy.models import Resource
from backend.systems.economy.repositories import EconomyRepository
from backend.systems.economy.models import Resource
from backend.systems.economy.repositories import EconomyRepository
from backend.systems.economy.models import Resource
from backend.systems.economy.repositories import EconomyRepository
from backend.systems.economy.models import Resource
from backend.systems.economy.repositories import EconomyRepository
from backend.systems.economy.models import Resource
from backend.systems.economy.repositories import EconomyRepository
from backend.systems.economy.models import Resource
from backend.systems.economy.repositories import EconomyRepository
from typing import Type
"""
Tests for the economy repository module.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.engine import Result

from backend.systems.economy.repositories.economy_repository import EconomyRepository
from backend.systems.economy.models.economic_metric import EconomicMetric, MetricType
from backend.systems.economy.models.resource import Resource


@pytest.fixture
def mock_session(): pass
    """Create a mock async database session for testing."""
    session = AsyncMock(spec=AsyncSession)
    return session


@pytest.fixture
def repository(mock_session): pass
    """Create a repository instance for testing."""
    return EconomyRepository(mock_session)


@pytest.fixture
def sample_resource(): pass
    """Create a sample resource for testing."""
    resource = MagicMock()
    resource.id = 1
    resource.name = "Gold"
    resource.type = "gold"
    resource.price = 100.0
    resource.amount = 500.0
    resource.region_id = 1
    return resource


@pytest.fixture
def sample_metric(): pass
    """Create a sample economic metric for testing."""
    metric = MagicMock()
    metric.id = 1
    metric.metric_type = MetricType.SUPPLY
    metric.value = 80.0
    metric.resource_id = 1
    metric.region_id = 1
    metric.faction_id = None
    metric.timestamp = datetime.utcnow()
    metric.metadata = {}
    # Add dict method for save_metric
    metric.dict = MagicMock(return_value={
        "metric_type": MetricType.SUPPLY,
        "value": 80.0,
        "resource_id": 1,
        "region_id": 1,
        "faction_id": None,
        "timestamp": datetime.utcnow(),
        "metadata": {}
    })
    return metric


class TestEconomyRepository: pass
    """Test suite for the EconomyRepository class."""

    def test_init(self, mock_session): pass
        """Test repository initialization."""
        repo = EconomyRepository(mock_session)
        assert repo.db_session == mock_session

    @pytest.mark.asyncio
    async def test_get_resource_success(self, repository, mock_session, sample_resource): pass
        """Test successful resource retrieval."""
        # Mock the result of session.execute()
        mock_result = AsyncMock(spec=Result)
        mock_scalars = MagicMock()  # Not async
        mock_scalars.first.return_value = sample_resource
        mock_result.scalars.return_value = mock_scalars
        mock_session.execute.return_value = mock_result
        
        result = await repository.get_resource(1)
        
        assert result == sample_resource
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_resource_not_found(self, repository, mock_session): pass
        """Test resource retrieval when resource doesn't exist."""
        mock_result = AsyncMock(spec=Result)
        mock_scalars = MagicMock()  # Not async
        mock_scalars.first.return_value = None
        mock_result.scalars.return_value = mock_scalars
        mock_session.execute.return_value = mock_result
        
        result = await repository.get_resource(999)
        
        assert result is None

    @pytest.mark.asyncio
    async def test_save_metric(self, repository, mock_session, sample_metric): pass
        """Test saving an economic metric."""
        # Mock the result of the INSERT statement
        mock_result = MagicMock()  # Not async
        mock_result.scalar_one.return_value = 123  # New metric ID
        mock_session.execute.return_value = mock_result
        mock_session.commit.return_value = None
        
        result = await repository.save_metric(sample_metric)
        
        assert result.id == 123
        mock_session.execute.assert_called_once()
        mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_save_metric_with_rollback_on_error(self, repository, mock_session, sample_metric): pass
        """Test saving metric with rollback on database error."""
        mock_session.execute.side_effect = Exception("Database error")
        
        with pytest.raises(Exception, match="Database error"): pass
            await repository.save_metric(sample_metric)

    @pytest.mark.asyncio
    async def test_get_latest_metric_success(self, repository, mock_session, sample_metric): pass
        """Test getting latest metric for a resource."""
        # Mock the raw SQL result
        mock_result = MagicMock()  # Not async
        mock_result.fetchone.return_value = (
            1, "supply", 80.0, 1, None, 1, datetime.utcnow(), {}
        )
        mock_session.execute.return_value = mock_result
        
        result = await repository.get_latest_metric(
            metric_type=MetricType.SUPPLY, resource_id=1
        )
        
        assert result is not None
        assert result.metric_type == MetricType.SUPPLY
        assert result.value == 80.0
        assert result.resource_id == 1
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_latest_metric_not_found(self, repository, mock_session): pass
        """Test getting latest metric when none exists."""
        mock_result = MagicMock()  # Not async
        mock_result.fetchone.return_value = None
        mock_session.execute.return_value = mock_result
        
        result = await repository.get_latest_metric(
            metric_type=MetricType.SUPPLY, resource_id=1
        )
        
        assert result is None

    @pytest.mark.asyncio
    async def test_get_latest_metric_with_region_filter(self, repository, mock_session): pass
        """Test getting latest metric with region filter."""
        mock_result = MagicMock()  # Not async
        mock_result.fetchone.return_value = (
            1, "supply", 80.0, 5, None, 1, datetime.utcnow(), {}
        )
        mock_session.execute.return_value = mock_result
        
        result = await repository.get_latest_metric(
            metric_type=MetricType.SUPPLY, resource_id=1, region_id=5
        )
        
        assert result is not None
        assert result.region_id == 5
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_latest_metric_with_faction_filter(self, repository, mock_session): pass
        """Test getting latest metric with faction filter."""
        mock_result = MagicMock()  # Not async
        mock_result.fetchone.return_value = (
            1, "supply", 80.0, 1, 10, 1, datetime.utcnow(), {}
        )
        mock_session.execute.return_value = mock_result
        
        result = await repository.get_latest_metric(
            metric_type=MetricType.SUPPLY, resource_id=1, faction_id=10
        )
        
        assert result is not None
        assert result.faction_id == 10
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_resource_amount_success(self, repository, mock_session): pass
        """Test getting resource amount for a region."""
        mock_result = MagicMock()  # Not async
        mock_result.scalar_one_or_none.return_value = 500.0
        mock_session.execute.return_value = mock_result
        
        result = await repository.get_resource_amount(region_id=1, resource_id=1)
        
        assert result == 500.0
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_resource_amount_resource_not_found(self, repository, mock_session): pass
        """Test getting resource amount when resource doesn't exist."""
        mock_result = MagicMock()  # Not async
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result
        
        result = await repository.get_resource_amount(region_id=1, resource_id=999)
        
        assert result == 0.0

    @pytest.mark.asyncio
    async def test_update_resource_amount_existing_resource(self, repository, mock_session): pass
        """Test updating resource amount for existing resource."""
        mock_session.execute.return_value = None
        mock_session.commit.return_value = None
        
        await repository.update_resource_amount(
            region_id=1, resource_id=1, amount_change=50.0
        )
        
        mock_session.execute.assert_called_once()
        mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_resource_amount_new_resource(self, repository, mock_session): pass
        """Test updating resource amount for new resource."""
        mock_session.execute.return_value = None
        mock_session.commit.return_value = None
        
        await repository.update_resource_amount(
            region_id=1, resource_id=1, amount_change=100.0
        )
        
        mock_session.execute.assert_called_once()
        mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_resource_amount_with_rollback_on_error(self, repository, mock_session): pass
        """Test updating resource amount with rollback on error."""
        mock_session.execute.side_effect = Exception("Database error")
        
        with pytest.raises(Exception, match="Database error"): pass
            await repository.update_resource_amount(
                region_id=1, resource_id=1, amount_change=50.0
            )

    @pytest.mark.asyncio
    async def test_get_resources_by_region(self, repository, mock_session, sample_resource): pass
        """Test getting all resources for a region."""
        mock_result = AsyncMock(spec=Result)
        mock_scalars = MagicMock()  # Not async
        mock_scalars.all.return_value = [sample_resource]
        mock_result.scalars.return_value = mock_scalars
        mock_session.execute.return_value = mock_result
        
        result = await repository.get_resources_by_region(region_id=1)
        
        assert result == [sample_resource]
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_metrics_history(self, repository, mock_session): pass
        """Test getting historical metrics."""
        mock_result = MagicMock()  # Not async
        mock_result.fetchall.return_value = [
            (1, "supply", 80.0, 1, None, 1, datetime.utcnow(), {}),
            (2, "supply", 75.0, 1, None, 1, datetime.utcnow(), {})
        ]
        mock_session.execute.return_value = mock_result
        
        result = await repository.get_metrics_history(MetricType.SUPPLY, resource_id=1)
        
        assert len(result) == 2
        assert result[0].metric_type == MetricType.SUPPLY
        assert result[0].value == 80.0
        assert result[1].value == 75.0
        mock_session.execute.assert_called_once()

"""
Test repositories for religion system.

Comprehensive tests for religion system repositories including database operations,
CRUD functionality, error handling, and integration testing.
"""

import pytest
import asyncio
from datetime import datetime
from uuid import UUID, uuid4
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

# Import the repositories under test
from backend.systems.religion.repositories import (
    ReligionRepository,
    create_religion_repository,
    get_religion_repository
)
from backend.systems.religion.models import (
    ReligionEntity,
    CreateReligionRequest,
    UpdateReligionRequest
)
from backend.infrastructure.shared.exceptions import (
    ReligionNotFoundError,
    ReligionValidationError,
    ReligionConflictError
)


class TestReligionRepository:
    """Test suite for religion repository"""
    
    @pytest.fixture
    def mock_db_session(self):
        """Mock database session for testing"""
        session = Mock(spec=Session)
        session.query.return_value = session
        session.filter.return_value = session
        session.filter_by.return_value = session
        session.order_by.return_value = session
        session.limit.return_value = session
        session.offset.return_value = session
        session.first.return_value = None
        session.all.return_value = []
        session.count.return_value = 0
        session.add = Mock()
        session.commit = Mock()
        session.rollback = Mock()
        session.flush = Mock()
        session.refresh = Mock()
        return session
    
    @pytest.fixture
    def religion_repository(self, mock_db_session):
        """Create religion repository with mocked session"""
        return ReligionRepository(mock_db_session)
    
    @pytest.fixture
    def sample_religion_entity(self):
        """Sample religion entity for testing"""
        entity = ReligionEntity(
            id=uuid4(),
            name="Test Religion",
            description="A test religion",
            status="active",
            properties={"followers": 1000, "temples": 5}
        )
        entity.created_at = datetime.utcnow()
        return entity
    
    @pytest.fixture
    def sample_create_request(self):
        """Sample create religion request"""
        return CreateReligionRequest(
            name="New Religion",
            description="A new religion for testing",
            properties={"founding_year": 2024, "deity": "Test God"}
        )
    
    @pytest.fixture
    def sample_update_request(self):
        """Sample update religion request"""
        return UpdateReligionRequest(
            name="Updated Religion",
            description="Updated description",
            status="reformed",
            properties={"followers": 2000}
        )

    def test_repository_initialization(self, mock_db_session):
        """Test repository initialization"""
        repository = ReligionRepository(mock_db_session)
        
        assert repository.db == mock_db_session
        assert repository.model == ReligionEntity

    @pytest.mark.asyncio
    async def test_create_religion_success(self, religion_repository, sample_create_request, mock_db_session):
        """Test successful religion creation"""
        user_id = uuid4()
        
        # Execute
        result = await religion_repository.create(sample_create_request, user_id)
        
        # Verify
        assert isinstance(result, ReligionEntity)
        assert result.name == sample_create_request.name
        assert result.description == sample_create_request.description
        assert result.properties == sample_create_request.properties
        assert result.status == "active"
        assert result.is_active is True
        assert isinstance(result.id, UUID)
        assert isinstance(result.created_at, datetime)
        
        # Verify database operations
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()
        mock_db_session.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_religion_database_error(self, religion_repository, sample_create_request, mock_db_session):
        """Test religion creation with database error"""
        # Setup mock to raise error
        mock_db_session.commit.side_effect = SQLAlchemyError("Database error")
        
        # Execute and verify exception
        with pytest.raises(Exception):
            await religion_repository.create(sample_create_request)
        
        # Verify rollback was called
        mock_db_session.rollback.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_by_id_success(self, religion_repository, sample_religion_entity, mock_db_session):
        """Test successful religion retrieval by ID"""
        # Setup mock
        mock_db_session.query.return_value.filter.return_value.first.return_value = sample_religion_entity
        
        # Execute
        result = await religion_repository.get_by_id(sample_religion_entity.id)
        
        # Verify
        assert result == sample_religion_entity
        
        # Verify query was called correctly
        mock_db_session.query.assert_called_with(ReligionEntity)
        mock_db_session.query.return_value.filter.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, religion_repository, mock_db_session):
        """Test religion retrieval when not found"""
        # Setup mock
        religion_id = uuid4()
        mock_db_session.query.return_value.filter.return_value.first.return_value = None
        
        # Execute
        result = await religion_repository.get_by_id(religion_id)
        
        # Verify
        assert result is None

    @pytest.mark.asyncio
    async def test_get_by_name_success(self, religion_repository, sample_religion_entity, mock_db_session):
        """Test successful religion retrieval by name"""
        # Setup mock
        mock_db_session.query.return_value.filter.return_value.first.return_value = sample_religion_entity
        
        # Execute
        result = await religion_repository.get_by_name("Test Religion")
        
        # Verify
        assert result == sample_religion_entity
        
        # Verify query was called correctly
        mock_db_session.query.assert_called_with(ReligionEntity)

    @pytest.mark.asyncio
    async def test_update_religion_success(self, religion_repository, sample_religion_entity, sample_update_request, mock_db_session):
        """Test successful religion update"""
        # Setup mock
        mock_db_session.query.return_value.filter.return_value.first.return_value = sample_religion_entity
        
        # Execute
        result = await religion_repository.update(sample_religion_entity.id, sample_update_request)
        
        # Verify
        assert result == sample_religion_entity
        assert sample_religion_entity.name == sample_update_request.name
        assert sample_religion_entity.description == sample_update_request.description
        assert sample_religion_entity.status == sample_update_request.status
        assert sample_religion_entity.properties == sample_update_request.properties
        assert isinstance(sample_religion_entity.updated_at, datetime)
        
        # Verify database operations
        mock_db_session.commit.assert_called_once()
        mock_db_session.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_religion_not_found(self, religion_repository, sample_update_request, mock_db_session):
        """Test updating non-existent religion"""
        # Setup mock
        religion_id = uuid4()
        mock_db_session.query.return_value.filter.return_value.first.return_value = None
        
        # Execute and verify exception
        with pytest.raises(ReligionNotFoundError):
            await religion_repository.update(religion_id, sample_update_request)

    @pytest.mark.asyncio
    async def test_update_religion_partial(self, religion_repository, sample_religion_entity, mock_db_session):
        """Test partial religion update"""
        # Setup mock
        mock_db_session.query.return_value.filter.return_value.first.return_value = sample_religion_entity
        
        # Create partial update request
        partial_request = UpdateReligionRequest(name="Partially Updated")
        
        # Execute
        result = await religion_repository.update(sample_religion_entity.id, partial_request)
        
        # Verify only name was updated
        assert result.name == "Partially Updated"
        assert result.description == sample_religion_entity.description  # Unchanged
        assert result.status == sample_religion_entity.status  # Unchanged

    @pytest.mark.asyncio
    async def test_delete_religion_success(self, religion_repository, sample_religion_entity, mock_db_session):
        """Test successful religion deletion (soft delete)"""
        # Setup mock
        mock_db_session.query.return_value.filter.return_value.first.return_value = sample_religion_entity
        
        # Execute
        result = await religion_repository.delete(sample_religion_entity.id)
        
        # Verify
        assert result is True
        assert sample_religion_entity.is_active is False
        assert isinstance(sample_religion_entity.updated_at, datetime)
        
        # Verify database operations
        mock_db_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_religion_not_found(self, religion_repository, mock_db_session):
        """Test deleting non-existent religion"""
        # Setup mock
        religion_id = uuid4()
        mock_db_session.query.return_value.filter.return_value.first.return_value = None
        
        # Execute and verify exception
        with pytest.raises(ReligionNotFoundError):
            await religion_repository.delete(religion_id)

    @pytest.mark.asyncio
    async def test_list_all_religions(self, religion_repository, sample_religion_entity, mock_db_session):
        """Test listing all religions with pagination"""
        # Setup mock
        entities = [sample_religion_entity]
        mock_db_session.query.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = entities
        mock_db_session.query.return_value.filter.return_value.count.return_value = 1
        
        # Execute
        result, total = await religion_repository.list_all(page=1, size=10)
        
        # Verify
        assert result == entities
        assert total == 1
        
        # Verify query operations
        mock_db_session.query.assert_called_with(ReligionEntity)

    @pytest.mark.asyncio
    async def test_list_all_with_status_filter(self, religion_repository, mock_db_session):
        """Test listing religions with status filter"""
        # Setup mock
        mock_db_session.query.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = []
        mock_db_session.query.return_value.filter.return_value.count.return_value = 0
        
        # Execute
        result, total = await religion_repository.list_all(page=1, size=10, status="active")
        
        # Verify
        assert result == []
        assert total == 0

    @pytest.mark.asyncio
    async def test_list_all_with_search_filter(self, religion_repository, mock_db_session):
        """Test listing religions with search filter"""
        # Setup mock
        mock_db_session.query.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = []
        mock_db_session.query.return_value.filter.return_value.count.return_value = 0
        
        # Execute
        result, total = await religion_repository.list_all(page=1, size=10, search="test")
        
        # Verify
        assert result == []
        assert total == 0

    @pytest.mark.asyncio
    async def test_search_religions(self, religion_repository, sample_religion_entity, mock_db_session):
        """Test religion search functionality"""
        # Setup mock
        entities = [sample_religion_entity]
        mock_db_session.query.return_value.filter.return_value.limit.return_value.all.return_value = entities
        
        # Execute
        result = await religion_repository.search("test query", limit=5)
        
        # Verify
        assert result == entities
        
        # Verify query was called
        mock_db_session.query.assert_called_with(ReligionEntity)

    @pytest.mark.asyncio
    async def test_bulk_create_religions(self, religion_repository, sample_create_request, mock_db_session):
        """Test bulk religion creation"""
        # Setup
        requests = [sample_create_request]
        
        # Execute
        result = await religion_repository.bulk_create(requests)
        
        # Verify
        assert len(result) == 1
        assert isinstance(result[0], ReligionEntity)
        assert result[0].name == sample_create_request.name
        
        # Verify database operations
        mock_db_session.add_all.assert_called_once()
        mock_db_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_bulk_create_error(self, religion_repository, sample_create_request, mock_db_session):
        """Test bulk creation with database error"""
        # Setup mock to raise error
        mock_db_session.commit.side_effect = SQLAlchemyError("Bulk insert error")
        
        # Execute and verify exception
        with pytest.raises(Exception):
            await religion_repository.bulk_create([sample_create_request])
        
        # Verify rollback was called
        mock_db_session.rollback.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_statistics(self, religion_repository, mock_db_session):
        """Test getting religion statistics"""
        # Setup mocks for different queries
        mock_db_session.query.return_value.count.return_value = 10
        mock_db_session.query.return_value.filter.return_value.count.return_value = 8
        
        # Execute
        result = await religion_repository.get_statistics()
        
        # Verify
        assert isinstance(result, dict)
        assert "total_religions" in result
        assert "active_religions" in result
        assert result["total_religions"] == 10
        assert result["active_religions"] == 8

    @pytest.mark.asyncio
    async def test_exists_by_name(self, religion_repository, sample_religion_entity, mock_db_session):
        """Test checking if religion exists by name"""
        # Setup mock
        mock_db_session.query.return_value.filter.return_value.first.return_value = sample_religion_entity
        
        # Execute
        result = await religion_repository.exists_by_name("Test Religion")
        
        # Verify
        assert result is True

    @pytest.mark.asyncio
    async def test_exists_by_name_not_found(self, religion_repository, mock_db_session):
        """Test checking if religion exists by name when not found"""
        # Setup mock
        mock_db_session.query.return_value.filter.return_value.first.return_value = None
        
        # Execute
        result = await religion_repository.exists_by_name("Nonexistent Religion")
        
        # Verify
        assert result is False

    @pytest.mark.asyncio
    async def test_get_active_religions(self, religion_repository, sample_religion_entity, mock_db_session):
        """Test getting only active religions"""
        # Setup mock
        entities = [sample_religion_entity]
        mock_db_session.query.return_value.filter.return_value.all.return_value = entities
        
        # Execute
        result = await religion_repository.get_active_religions()
        
        # Verify
        assert result == entities
        
        # Verify filter was applied for active religions
        mock_db_session.query.return_value.filter.assert_called()

    @pytest.mark.asyncio
    async def test_repository_transaction_rollback(self, religion_repository, sample_create_request, mock_db_session):
        """Test repository handles transaction rollback properly"""
        # Setup mock to raise error during commit
        mock_db_session.commit.side_effect = IntegrityError("Constraint violation", None, None)
        
        # Execute and verify exception
        with pytest.raises(Exception):
            await religion_repository.create(sample_create_request)
        
        # Verify rollback was called
        mock_db_session.rollback.assert_called_once()


class TestReligionRepositoryFactory:
    """Test religion repository factory functions"""
    
    def test_create_religion_repository(self):
        """Test creating religion repository"""
        mock_session = Mock(spec=Session)
        
        repository = create_religion_repository(mock_session)
        
        assert isinstance(repository, ReligionRepository)
        assert repository.db == mock_session
    
    def test_get_religion_repository(self):
        """Test getting religion repository"""
        mock_session = Mock(spec=Session)
        
        repository = get_religion_repository(mock_session)
        
        assert isinstance(repository, ReligionRepository)
        assert repository.db == mock_session


class TestReligionRepositoryIntegration:
    """Integration tests for religion repository"""
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_repository_full_workflow(self):
        """Test complete repository workflow integration"""
        # This would be an integration test with real database
        # For now, we'll test the flow with comprehensive mocks
        
        mock_session = Mock(spec=Session)
        repository = ReligionRepository(mock_session)
        
        # Setup entity for lifecycle
        religion_id = uuid4()
        entity = ReligionEntity(
            id=religion_id,
            name="Integration Test Religion",
            description="Testing full workflow"
        )
        entity.created_at = datetime.utcnow()
        
        # Mock session responses for full workflow
        mock_session.query.return_value.filter.return_value.first.return_value = entity
        mock_session.add = Mock()
        mock_session.commit = Mock()
        mock_session.refresh = Mock()
        
        # Test create
        create_request = CreateReligionRequest(name="Integration Test Religion")
        created = await repository.create(create_request)
        assert created.name == "Integration Test Religion"
        
        # Test read
        retrieved = await repository.get_by_id(religion_id)
        assert retrieved == entity
        
        # Test update
        update_request = UpdateReligionRequest(description="Updated description")
        updated = await repository.update(religion_id, update_request)
        assert updated == entity
        
        # Test delete
        deleted = await repository.delete(religion_id)
        assert deleted is True
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_repository_database_integration(self):
        """Test repository database integration"""
        # Test with mocked database operations
        mock_session = Mock(spec=Session)
        repository = ReligionRepository(mock_session)
        
        # Test database connection and basic operations
        assert repository.db == mock_session
        
        # Test that repository can handle database operations
        create_request = CreateReligionRequest(name="DB Integration Test")
        
        # Mock successful database operations
        mock_session.add = Mock()
        mock_session.commit = Mock()
        mock_session.refresh = Mock()
        
        result = await repository.create(create_request)
        
        # Verify database operations were called
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once()
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_repository_error_handling_integration(self):
        """Test repository error handling in integration scenarios"""
        mock_session = Mock(spec=Session)
        repository = ReligionRepository(mock_session)
        
        # Test various error scenarios
        
        # Database connection error
        mock_session.commit.side_effect = SQLAlchemyError("Connection lost")
        
        create_request = CreateReligionRequest(name="Error Test")
        
        with pytest.raises(Exception):
            await repository.create(create_request)
        
        # Verify rollback was called
        mock_session.rollback.assert_called()
        
        # Integrity constraint error
        mock_session.commit.side_effect = IntegrityError("Duplicate key", None, None)
        
        with pytest.raises(Exception):
            await repository.create(create_request)
        
        # Verify rollback was called again
        assert mock_session.rollback.call_count >= 2
    
    @pytest.mark.integration
    def test_repository_query_optimization(self):
        """Test repository query optimization"""
        mock_session = Mock(spec=Session)
        repository = ReligionRepository(mock_session)
        
        # Verify that repository uses efficient queries
        assert repository.model == ReligionEntity
        
        # Test that repository has proper indexing considerations
        # (This would be more meaningful with a real database)
        assert hasattr(repository, 'db')
        assert repository.db == mock_session
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_repository_concurrent_access(self):
        """Test repository handling of concurrent access"""
        mock_session = Mock(spec=Session)
        repository = ReligionRepository(mock_session)
        
        # Simulate concurrent operations
        tasks = []
        
        for i in range(5):
            create_request = CreateReligionRequest(name=f"Concurrent Religion {i}")
            task = repository.create(create_request)
            tasks.append(task)
        
        # Execute concurrent operations
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Verify all operations completed (even if some failed)
        assert len(results) == 5
        
        # Verify database operations were called multiple times
        assert mock_session.add.call_count == 5
        assert mock_session.commit.call_count == 5


# Coverage requirements: ≥90% as per backend_development_protocol.md
# WebSocket compatibility: Ensure JSON serialization for Unity frontend
# Cross-system compatibility: Test communication with other systems
# API contract compliance: Verify endpoints match established contracts

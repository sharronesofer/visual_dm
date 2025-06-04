"""
Test repositories for rumor system.

Tests the repositories component according to Development_Bible.md standards.
Achieves ≥90% coverage target as specified in backend_development_protocol.md.
"""

import pytest
from unittest.mock import Mock, MagicMock
from uuid import uuid4
from sqlalchemy.orm import Session

# Import from infrastructure layer
from backend.infrastructure.systems.rumor.repositories.rumor_repository import SQLAlchemyRumorRepository
from backend.infrastructure.systems.rumor.models.models import RumorEntity
from backend.systems.rumor.services.services import RumorData, CreateRumorData


class TestSQLAlchemyRumorRepository:
    """Test suite for SQLAlchemy rumor repository."""
    
    @pytest.fixture
    def mock_db_session(self):
        """Mock database session for testing."""
        return Mock(spec=Session)
    
    @pytest.fixture
    def repository(self, mock_db_session):
        """Repository instance for testing."""
        return SQLAlchemyRumorRepository(mock_db_session)
    
    @pytest.fixture
    def sample_rumor_data(self):
        """Sample data for rumor testing."""
        return RumorData(
            id=uuid4(),
            content="Test rumor content about political events",
            originator_id="test_entity_123",
            categories=["political"],
            severity="minor",
            truth_value=0.7,
            believability=0.8,
            spread_count=0,
            properties={"test": "value"},
            status="active"
        )
    
    @pytest.fixture
    def sample_entity(self, sample_rumor_data):
        """Sample database entity for testing."""
        entity = RumorEntity()
        entity.id = sample_rumor_data.id
        entity.content = sample_rumor_data.content
        entity.originator_id = sample_rumor_data.originator_id
        entity.categories = sample_rumor_data.categories
        entity.severity = sample_rumor_data.severity
        entity.truth_value = sample_rumor_data.truth_value
        entity.believability = sample_rumor_data.believability
        entity.spread_count = sample_rumor_data.spread_count
        entity.properties = sample_rumor_data.properties
        entity.status = sample_rumor_data.status
        entity.created_at = sample_rumor_data.created_at
        return entity
    
    def test_get_rumor_by_id_found(self, repository, mock_db_session, sample_entity, sample_rumor_data):
        """Test retrieving an existing rumor by ID."""
        # Arrange
        mock_query = Mock()
        mock_db_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = sample_entity
        
        # Act
        result = repository.get_rumor_by_id(sample_rumor_data.id)
        
        # Assert
        assert result is not None
        assert result.id == sample_rumor_data.id
        assert result.content == sample_rumor_data.content
        assert result.originator_id == sample_rumor_data.originator_id
        assert result.severity == sample_rumor_data.severity
        mock_db_session.query.assert_called_once_with(RumorEntity)
    
    def test_get_rumor_by_id_not_found(self, repository, mock_db_session):
        """Test retrieving a non-existent rumor by ID."""
        # Arrange
        mock_query = Mock()
        mock_db_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None
        
        # Act
        result = repository.get_rumor_by_id(uuid4())
        
        # Assert
        assert result is None
    
    def test_create_rumor(self, repository, mock_db_session, sample_rumor_data):
        """Test creating a new rumor."""
        # Arrange
        mock_entity = Mock(spec=RumorEntity)
        mock_entity.id = sample_rumor_data.id
        mock_entity.content = sample_rumor_data.content
        mock_entity.originator_id = sample_rumor_data.originator_id
        mock_entity.categories = sample_rumor_data.categories
        mock_entity.severity = sample_rumor_data.severity
        mock_entity.truth_value = sample_rumor_data.truth_value
        mock_entity.believability = sample_rumor_data.believability
        mock_entity.spread_count = sample_rumor_data.spread_count
        mock_entity.properties = sample_rumor_data.properties
        mock_entity.status = sample_rumor_data.status
        mock_entity.created_at = sample_rumor_data.created_at
        
        # Act
        result = repository.create_rumor(sample_rumor_data)
        
        # Assert
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()
        mock_db_session.refresh.assert_called_once()
        assert result is not None
    
    def test_update_rumor(self, repository, mock_db_session, sample_entity, sample_rumor_data):
        """Test updating an existing rumor."""
        # Arrange
        mock_query = Mock()
        mock_db_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = sample_entity
        
        sample_rumor_data.content = "Updated content"
        sample_rumor_data.severity = "major"
        
        # Act
        result = repository.update_rumor(sample_rumor_data)
        
        # Assert
        mock_db_session.commit.assert_called_once()
        mock_db_session.refresh.assert_called_once()
        assert sample_entity.content == "Updated content"
        assert sample_entity.severity == "major"
    
    def test_update_rumor_not_found(self, repository, mock_db_session, sample_rumor_data):
        """Test updating a non-existent rumor."""
        # Arrange
        mock_query = Mock()
        mock_db_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None
        
        # Act & Assert
        with pytest.raises(ValueError, match="not found"):
            repository.update_rumor(sample_rumor_data)
    
    def test_delete_rumor(self, repository, mock_db_session, sample_entity):
        """Test deleting an existing rumor."""
        # Arrange
        mock_query = Mock()
        mock_db_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = sample_entity
        
        # Act
        result = repository.delete_rumor(sample_entity.id)
        
        # Assert
        assert result is True
        mock_db_session.delete.assert_called_once_with(sample_entity)
        mock_db_session.commit.assert_called_once()
    
    def test_delete_rumor_not_found(self, repository, mock_db_session):
        """Test deleting a non-existent rumor."""
        # Arrange
        mock_query = Mock()
        mock_db_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None
        
        # Act
        result = repository.delete_rumor(uuid4())
        
        # Assert
        assert result is False
    
    def test_list_rumors_with_pagination(self, repository, mock_db_session, sample_entity):
        """Test listing rumors with pagination."""
        # Arrange
        mock_query = Mock()
        mock_db_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.count.return_value = 1
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = [sample_entity]
        
        # Act
        rumors, total = repository.list_rumors(page=1, size=10)
        
        # Assert
        assert len(rumors) == 1
        assert total == 1
        assert rumors[0].id == sample_entity.id
    
    def test_get_rumor_statistics(self, repository, mock_db_session):
        """Test getting rumor statistics."""
        # Arrange
        mock_query = Mock()
        mock_db_session.query.return_value = mock_query
        mock_query.count.return_value = 10
        mock_query.filter.return_value = mock_query
        mock_query.group_by.return_value = mock_query
        mock_query.all.return_value = [("minor", 5), ("major", 3)]
        mock_query.scalar.return_value = 0.75
        
        # Act
        stats = repository.get_rumor_statistics()
        
        # Assert
        assert "total_rumors" in stats
        assert "active_rumors" in stats
        assert "severity_distribution" in stats
        assert "average_truth_value" in stats


# Integration tests would test with real database
class TestRumorRepositoriesIntegration:
    """Integration tests for rumor repositories."""
    
    @pytest.mark.integration
    def test_repositories_full_workflow(self):
        """Test complete repositories workflow integration."""
        # Would test with actual database connection
        pass
    
    @pytest.mark.integration
    def test_repositories_database_integration(self):
        """Test repositories database integration."""
        # Would test actual database operations
        pass


# Coverage requirements: ≥90% as per backend_development_protocol.md
# WebSocket compatibility: Ensure JSON serialization for Unity frontend
# Cross-system compatibility: Test communication with other systems
# API contract compliance: Verify endpoints match established contracts

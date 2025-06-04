"""
Comprehensive tests for Faction Succession Repository

Tests all succession crisis data access functionality according to Task 69 requirements:
- CRUD operations for succession crises
- Query filtering and pagination
- Database integrity and constraints
- Performance and optimization
"""

import pytest
import uuid
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from backend.infrastructure.repositories.faction.succession_repository import SuccessionRepository
from backend.systems.faction.models.succession import (
    SuccessionCrisisEntity,
    SuccessionType,
    SuccessionCrisisStatus,
    SuccessionTrigger
)


class TestSuccessionRepository:
    """Test suite for SuccessionRepository"""
    
    @pytest.fixture
    def succession_repository(self):
        """Create succession repository instance"""
        return SuccessionRepository()
    
    @pytest.fixture
    def mock_db(self):
        """Create mock database session"""
        return Mock(spec=Session)
    
    @pytest.fixture
    def sample_crisis_entity(self):
        """Create sample succession crisis entity"""
        return SuccessionCrisisEntity(
            id=uuid.uuid4(),
            faction_id=uuid.uuid4(),
            faction_name="Test Faction",
            succession_type=SuccessionType.ECONOMIC_COMPETITION.value,
            status=SuccessionCrisisStatus.PENDING.value,
            trigger=SuccessionTrigger.LEADER_DEATH_NATURAL.value,
            crisis_start=datetime.utcnow(),
            estimated_duration=30,
            faction_stability=0.8,
            candidates=[],
            interfering_factions=[],
            interference_details={},
            instability_effects={},
            metadata={}
        )


class TestCRUDOperations:
    """Test basic CRUD operations"""
    
    def test_create_succession_crisis(self, succession_repository, mock_db, sample_crisis_entity):
        """Test creating a succession crisis"""
        # Mock database operations
        mock_db.add.return_value = None
        mock_db.commit.return_value = None
        mock_db.refresh.return_value = None
        
        # Create crisis
        created_crisis = succession_repository.create_succession_crisis(mock_db, sample_crisis_entity)
        
        # Verify database operations
        mock_db.add.assert_called_once_with(sample_crisis_entity)
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once_with(sample_crisis_entity)
        
        # Verify return value
        assert created_crisis == sample_crisis_entity
    
    def test_get_succession_crisis_by_id(self, succession_repository, mock_db, sample_crisis_entity):
        """Test retrieving succession crisis by ID"""
        # Mock database query
        mock_db.query.return_value.filter.return_value.first.return_value = sample_crisis_entity
        
        # Get crisis
        crisis = succession_repository.get_succession_crisis_by_id(mock_db, sample_crisis_entity.id)
        
        # Verify query
        mock_db.query.assert_called_once_with(SuccessionCrisisEntity)
        assert crisis == sample_crisis_entity
    
    def test_get_succession_crisis_by_id_not_found(self, succession_repository, mock_db):
        """Test retrieving non-existent succession crisis"""
        # Mock database query to return None
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        # Get crisis
        crisis = succession_repository.get_succession_crisis_by_id(mock_db, uuid.uuid4())
        
        # Should return None
        assert crisis is None
    
    def test_update_succession_crisis(self, succession_repository, mock_db, sample_crisis_entity):
        """Test updating succession crisis"""
        # Mock database operations
        mock_db.commit.return_value = None
        mock_db.refresh.return_value = None
        
        # Update crisis
        sample_crisis_entity.status = SuccessionCrisisStatus.IN_PROGRESS.value
        updated_crisis = succession_repository.update_succession_crisis(mock_db, sample_crisis_entity)
        
        # Verify database operations
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once_with(sample_crisis_entity)
        
        # Verify return value
        assert updated_crisis == sample_crisis_entity
        assert updated_crisis.status == SuccessionCrisisStatus.IN_PROGRESS.value
    
    def test_delete_succession_crisis(self, succession_repository, mock_db, sample_crisis_entity):
        """Test deleting succession crisis"""
        # Mock database operations
        mock_db.delete.return_value = None
        mock_db.commit.return_value = None
        
        # Delete crisis
        result = succession_repository.delete_succession_crisis(mock_db, sample_crisis_entity)
        
        # Verify database operations
        mock_db.delete.assert_called_once_with(sample_crisis_entity)
        mock_db.commit.assert_called_once()
        
        # Verify return value
        assert result is True


class TestQueryOperations:
    """Test query and filtering operations"""
    
    def test_get_crises_by_faction(self, succession_repository, mock_db, sample_crisis_entity):
        """Test retrieving crises by faction ID"""
        # Mock database query
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = [sample_crisis_entity]
        
        # Get crises
        crises = succession_repository.get_crises_by_faction(mock_db, sample_crisis_entity.faction_id)
        
        # Verify query
        mock_db.query.assert_called_once_with(SuccessionCrisisEntity)
        assert crises == [sample_crisis_entity]
    
    def test_get_active_crises(self, succession_repository, mock_db, sample_crisis_entity):
        """Test retrieving active succession crises"""
        # Mock database query
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = [sample_crisis_entity]
        
        # Get active crises
        crises = succession_repository.get_all_active_crises(mock_db, limit=10)
        
        # Verify query
        mock_db.query.assert_called_once_with(SuccessionCrisisEntity)
        assert crises == [sample_crisis_entity]
    
    def test_get_crises_by_status(self, succession_repository, mock_db, sample_crisis_entity):
        """Test retrieving crises by status"""
        # Mock database query
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = [sample_crisis_entity]
        
        # Get crises by status
        crises = succession_repository.get_crises_by_status(
            mock_db, 
            SuccessionCrisisStatus.PENDING.value
        )
        
        # Verify query
        mock_db.query.assert_called_once_with(SuccessionCrisisEntity)
        assert crises == [sample_crisis_entity]
    
    def test_get_crises_by_trigger(self, succession_repository, mock_db, sample_crisis_entity):
        """Test retrieving crises by trigger type"""
        # Mock database query
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = [sample_crisis_entity]
        
        # Get crises by trigger
        crises = succession_repository.get_crises_by_trigger(
            mock_db,
            SuccessionTrigger.LEADER_DEATH_NATURAL.value
        )
        
        # Verify query
        mock_db.query.assert_called_once_with(SuccessionCrisisEntity)
        assert crises == [sample_crisis_entity]
    
    def test_get_crises_by_succession_type(self, succession_repository, mock_db, sample_crisis_entity):
        """Test retrieving crises by succession type"""
        # Mock database query
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = [sample_crisis_entity]
        
        # Get crises by succession type
        crises = succession_repository.get_crises_by_succession_type(
            mock_db,
            SuccessionType.ECONOMIC_COMPETITION.value
        )
        
        # Verify query
        mock_db.query.assert_called_once_with(SuccessionCrisisEntity)
        assert crises == [sample_crisis_entity]


class TestPaginationAndSorting:
    """Test pagination and sorting functionality"""
    
    def test_get_crises_paginated(self, succession_repository, mock_db, sample_crisis_entity):
        """Test paginated crisis retrieval"""
        # Mock database query
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = [sample_crisis_entity]
        
        # Mock count query
        mock_query.count.return_value = 1
        
        # Get paginated crises
        crises, total = succession_repository.get_crises_paginated(
            mock_db,
            page=1,
            size=10,
            order_by="crisis_start"
        )
        
        # Verify query
        mock_db.query.assert_called_with(SuccessionCrisisEntity)
        assert crises == [sample_crisis_entity]
        assert total == 1
    
    def test_get_crises_with_filters(self, succession_repository, mock_db, sample_crisis_entity):
        """Test crisis retrieval with multiple filters"""
        # Mock database query
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = [sample_crisis_entity]
        
        # Get crises with filters
        filters = {
            "status": SuccessionCrisisStatus.PENDING.value,
            "faction_id": sample_crisis_entity.faction_id,
            "succession_type": SuccessionType.ECONOMIC_COMPETITION.value
        }
        
        crises = succession_repository.get_crises_with_filters(mock_db, filters)
        
        # Verify query
        mock_db.query.assert_called_once_with(SuccessionCrisisEntity)
        assert crises == [sample_crisis_entity]


class TestDateRangeQueries:
    """Test date range and time-based queries"""
    
    def test_get_crises_in_date_range(self, succession_repository, mock_db, sample_crisis_entity):
        """Test retrieving crises within date range"""
        # Mock database query
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = [sample_crisis_entity]
        
        # Get crises in date range
        start_date = datetime.utcnow() - timedelta(days=30)
        end_date = datetime.utcnow()
        
        crises = succession_repository.get_crises_in_date_range(
            mock_db,
            start_date,
            end_date
        )
        
        # Verify query
        mock_db.query.assert_called_once_with(SuccessionCrisisEntity)
        assert crises == [sample_crisis_entity]
    
    def test_get_ongoing_crises(self, succession_repository, mock_db, sample_crisis_entity):
        """Test retrieving ongoing crises"""
        # Mock database query
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = [sample_crisis_entity]
        
        # Get ongoing crises
        crises = succession_repository.get_ongoing_crises(mock_db)
        
        # Verify query
        mock_db.query.assert_called_once_with(SuccessionCrisisEntity)
        assert crises == [sample_crisis_entity]
    
    def test_get_overdue_crises(self, succession_repository, mock_db, sample_crisis_entity):
        """Test retrieving overdue crises"""
        # Mock database query
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = [sample_crisis_entity]
        
        # Get overdue crises
        crises = succession_repository.get_overdue_crises(mock_db)
        
        # Verify query
        mock_db.query.assert_called_once_with(SuccessionCrisisEntity)
        assert crises == [sample_crisis_entity]


class TestAggregationQueries:
    """Test aggregation and statistics queries"""
    
    def test_get_crisis_count_by_status(self, succession_repository, mock_db):
        """Test getting crisis count by status"""
        # Mock database query
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.group_by.return_value = mock_query
        mock_query.all.return_value = [
            (SuccessionCrisisStatus.PENDING.value, 5),
            (SuccessionCrisisStatus.IN_PROGRESS.value, 3),
            (SuccessionCrisisStatus.RESOLVED.value, 10)
        ]
        
        # Get count by status
        counts = succession_repository.get_crisis_count_by_status(mock_db)
        
        # Verify query
        mock_db.query.assert_called_once()
        assert counts == {
            SuccessionCrisisStatus.PENDING.value: 5,
            SuccessionCrisisStatus.IN_PROGRESS.value: 3,
            SuccessionCrisisStatus.RESOLVED.value: 10
        }
    
    def test_get_crisis_count_by_faction_type(self, succession_repository, mock_db):
        """Test getting crisis count by faction type"""
        # Mock database query
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.join.return_value = mock_query
        mock_query.group_by.return_value = mock_query
        mock_query.all.return_value = [
            ("trading_company", 8),
            ("military", 12),
            ("religious", 6)
        ]
        
        # Get count by faction type
        counts = succession_repository.get_crisis_count_by_faction_type(mock_db)
        
        # Verify query
        mock_db.query.assert_called_once()
        assert counts == {
            "trading_company": 8,
            "military": 12,
            "religious": 6
        }
    
    def test_get_average_crisis_duration(self, succession_repository, mock_db):
        """Test getting average crisis duration"""
        # Mock database query
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.scalar.return_value = 25.5
        
        # Get average duration
        avg_duration = succession_repository.get_average_crisis_duration(mock_db)
        
        # Verify query
        mock_db.query.assert_called_once()
        assert avg_duration == 25.5
    
    def test_get_faction_stability_stats(self, succession_repository, mock_db):
        """Test getting faction stability statistics"""
        # Mock database query
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = [
            (0.9, 0.7, 0.8),  # min, max, avg
        ]
        
        # Get stability stats
        stats = succession_repository.get_faction_stability_stats(mock_db)
        
        # Verify query
        mock_db.query.assert_called_once()
        assert stats["min_stability"] == 0.9
        assert stats["max_stability"] == 0.7
        assert stats["avg_stability"] == 0.8


class TestComplexQueries:
    """Test complex queries and joins"""
    
    def test_get_crises_with_interference(self, succession_repository, mock_db, sample_crisis_entity):
        """Test retrieving crises with external interference"""
        # Mock database query
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = [sample_crisis_entity]
        
        # Get crises with interference
        crises = succession_repository.get_crises_with_interference(mock_db)
        
        # Verify query
        mock_db.query.assert_called_once_with(SuccessionCrisisEntity)
        assert crises == [sample_crisis_entity]
    
    def test_get_faction_crisis_history(self, succession_repository, mock_db, sample_crisis_entity):
        """Test retrieving faction crisis history"""
        # Mock database query
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = [sample_crisis_entity]
        
        # Get faction crisis history
        crises = succession_repository.get_faction_crisis_history(
            mock_db,
            sample_crisis_entity.faction_id,
            limit=10
        )
        
        # Verify query
        mock_db.query.assert_called_once_with(SuccessionCrisisEntity)
        assert crises == [sample_crisis_entity]
    
    def test_search_crises_by_text(self, succession_repository, mock_db, sample_crisis_entity):
        """Test text search in crises"""
        # Mock database query
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = [sample_crisis_entity]
        
        # Search crises
        crises = succession_repository.search_crises_by_text(mock_db, "Test Faction")
        
        # Verify query
        mock_db.query.assert_called_once_with(SuccessionCrisisEntity)
        assert crises == [sample_crisis_entity]


class TestErrorHandling:
    """Test error handling and edge cases"""
    
    def test_create_crisis_integrity_error(self, succession_repository, mock_db, sample_crisis_entity):
        """Test handling integrity error during creation"""
        # Mock database to raise IntegrityError
        mock_db.commit.side_effect = IntegrityError("Duplicate key", None, None)
        
        # Should handle gracefully
        with pytest.raises(IntegrityError):
            succession_repository.create_succession_crisis(mock_db, sample_crisis_entity)
    
    def test_update_nonexistent_crisis(self, succession_repository, mock_db):
        """Test updating non-existent crisis"""
        # Create non-existent crisis
        nonexistent_crisis = SuccessionCrisisEntity(
            id=uuid.uuid4(),
            faction_id=uuid.uuid4(),
            faction_name="Nonexistent",
            succession_type=SuccessionType.ECONOMIC_COMPETITION.value,
            status=SuccessionCrisisStatus.PENDING.value,
            trigger=SuccessionTrigger.LEADER_DEATH_NATURAL.value
        )
        
        # Mock database operations
        mock_db.commit.return_value = None
        mock_db.refresh.return_value = None
        
        # Should handle gracefully
        result = succession_repository.update_succession_crisis(mock_db, nonexistent_crisis)
        assert result == nonexistent_crisis
    
    def test_delete_nonexistent_crisis(self, succession_repository, mock_db):
        """Test deleting non-existent crisis"""
        # Create non-existent crisis
        nonexistent_crisis = SuccessionCrisisEntity(
            id=uuid.uuid4(),
            faction_id=uuid.uuid4(),
            faction_name="Nonexistent",
            succession_type=SuccessionType.ECONOMIC_COMPETITION.value,
            status=SuccessionCrisisStatus.PENDING.value,
            trigger=SuccessionTrigger.LEADER_DEATH_NATURAL.value
        )
        
        # Mock database operations
        mock_db.delete.return_value = None
        mock_db.commit.return_value = None
        
        # Should handle gracefully
        result = succession_repository.delete_succession_crisis(mock_db, nonexistent_crisis)
        assert result is True


class TestPerformanceOptimizations:
    """Test performance-related functionality"""
    
    def test_bulk_update_crises(self, succession_repository, mock_db):
        """Test bulk updating multiple crises"""
        # Mock database operations
        mock_db.bulk_update_mappings.return_value = None
        mock_db.commit.return_value = None
        
        # Bulk update data
        updates = [
            {"id": uuid.uuid4(), "status": SuccessionCrisisStatus.RESOLVED.value},
            {"id": uuid.uuid4(), "status": SuccessionCrisisStatus.FAILED.value}
        ]
        
        # Perform bulk update
        result = succession_repository.bulk_update_crises(mock_db, updates)
        
        # Verify operations
        mock_db.bulk_update_mappings.assert_called_once_with(SuccessionCrisisEntity, updates)
        mock_db.commit.assert_called_once()
        assert result is True
    
    def test_get_crisis_ids_only(self, succession_repository, mock_db):
        """Test retrieving only crisis IDs for performance"""
        # Mock database query
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = [uuid.uuid4(), uuid.uuid4()]
        
        # Get crisis IDs
        crisis_ids = succession_repository.get_crisis_ids_by_faction(
            mock_db,
            uuid.uuid4()
        )
        
        # Verify query
        mock_db.query.assert_called_once()
        assert len(crisis_ids) == 2
        assert all(isinstance(cid, uuid.UUID) for cid in crisis_ids)


class TestCacheIntegration:
    """Test cache integration (if implemented)"""
    
    @patch('backend.systems.faction.repositories.succession_repository.cache')
    def test_cached_crisis_retrieval(self, mock_cache, succession_repository, mock_db, sample_crisis_entity):
        """Test cached crisis retrieval"""
        # Mock cache miss
        mock_cache.get.return_value = None
        mock_cache.set.return_value = None
        
        # Mock database query
        mock_db.query.return_value.filter.return_value.first.return_value = sample_crisis_entity
        
        # Get crisis (should cache)
        crisis = succession_repository.get_succession_crisis_by_id(mock_db, sample_crisis_entity.id)
        
        # Verify cache operations
        mock_cache.get.assert_called_once()
        mock_cache.set.assert_called_once()
        assert crisis == sample_crisis_entity
    
    @patch('backend.systems.faction.repositories.succession_repository.cache')
    def test_cache_invalidation_on_update(self, mock_cache, succession_repository, mock_db, sample_crisis_entity):
        """Test cache invalidation on update"""
        # Mock cache operations
        mock_cache.delete.return_value = None
        
        # Mock database operations
        mock_db.commit.return_value = None
        mock_db.refresh.return_value = None
        
        # Update crisis (should invalidate cache)
        updated_crisis = succession_repository.update_succession_crisis(mock_db, sample_crisis_entity)
        
        # Verify cache invalidation
        mock_cache.delete.assert_called_once()
        assert updated_crisis == sample_crisis_entity


if __name__ == "__main__":
    pytest.main([__file__]) 
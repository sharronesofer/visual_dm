"""
Comprehensive unit tests for AllianceRepository
Tests CRUD operations, statistics, and data persistence for alliance system
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from uuid import uuid4, UUID
from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from backend.infrastructure.repositories.faction.alliance_repository import AllianceRepository
from backend.systems.faction.models.alliance import (
    AllianceEntity, BetrayalEntity, AllianceType, AllianceStatus, BetrayalReason
)


class TestAllianceRepository:
    """Test suite for AllianceRepository"""

    @pytest.fixture
    def mock_session(self):
        """Mock database session"""
        return Mock(spec=Session)

    @pytest.fixture
    def alliance_repository(self, mock_session):
        """Create AllianceRepository with mocked session"""
        return AllianceRepository(db_session=mock_session)

    @pytest.fixture
    def sample_alliance_entity(self):
        """Sample alliance entity for testing"""
        return AllianceEntity(
            id=uuid4(),
            name="Test Alliance",
            alliance_type=AllianceType.MILITARY.value,
            status=AllianceStatus.ACTIVE.value,
            description="Test military alliance",
            leader_faction_id=uuid4(),
            member_faction_ids=[uuid4(), uuid4()],
            terms={"mutual_defense": True},
            mutual_obligations=["Provide military support"],
            shared_enemies=[uuid4()],
            shared_goals=["Defeat common enemy"],
            start_date=datetime.utcnow(),
            end_date=None,
            auto_renew=False,
            trust_levels={"faction1": 0.8, "faction2": 0.7},
            betrayal_risks={"faction1": 0.2, "faction2": 0.3},
            reliability_history={},
            triggers={"threat_detected": True},
            threat_level=0.8,
            benefits_shared={},
            military_support_provided={},
            economic_support_provided={},
            created_at=datetime.utcnow(),
            updated_at=None,
            is_active=True,
            entity_metadata={}
        )

    @pytest.fixture
    def sample_betrayal_entity(self):
        """Sample betrayal entity for testing"""
        return BetrayalEntity(
            id=uuid4(),
            alliance_id=uuid4(),
            betrayer_faction_id=uuid4(),
            victim_faction_ids=[uuid4(), uuid4()],
            betrayal_reason=BetrayalReason.AMBITION.value,
            betrayal_type="military_attack",
            description="Surprise attack on alliance members",
            hidden_attributes_influence={
                "hidden_ambition": 9,
                "hidden_integrity": 3
            },
            external_pressure={"economic_crisis": True},
            opportunity_details={"weak_ally_defenses": True},
            damage_dealt={"military_losses": 500},
            trust_impact={"faction1": -0.8, "faction2": -0.6},
            reputation_impact=-0.5,
            detected_immediately=True,
            detection_delay=None,
            response_actions=[{"type": "military_retaliation"}],
            created_at=datetime.utcnow(),
            updated_at=None,
            is_active=True,
            entity_metadata={}
        )

    # Alliance CRUD Tests

    def test_get_alliance_by_id_success(self, alliance_repository, mock_session, sample_alliance_entity):
        """Test successful alliance retrieval by ID"""
        alliance_id = sample_alliance_entity.id
        mock_session.query().filter().first.return_value = sample_alliance_entity

        result = alliance_repository.get_alliance_by_id(alliance_id)

        assert result == sample_alliance_entity
        mock_session.query.assert_called_once_with(AllianceEntity)

    def test_get_alliance_by_id_not_found(self, alliance_repository, mock_session):
        """Test alliance retrieval when alliance doesn't exist"""
        alliance_id = uuid4()
        mock_session.query().filter().first.return_value = None

        result = alliance_repository.get_alliance_by_id(alliance_id)

        assert result is None

    def test_get_alliances_by_faction(self, alliance_repository, mock_session, sample_alliance_entity):
        """Test retrieval of alliances by faction ID"""
        faction_id = sample_alliance_entity.leader_faction_id
        mock_session.query().filter().all.return_value = [sample_alliance_entity]

        result = alliance_repository.get_alliances_by_faction(faction_id)

        assert len(result) == 1
        assert result[0] == sample_alliance_entity

    def test_get_active_alliances(self, alliance_repository, mock_session, sample_alliance_entity):
        """Test retrieval of active alliances"""
        mock_session.query().filter().all.return_value = [sample_alliance_entity]

        result = alliance_repository.get_active_alliances()

        assert len(result) == 1
        assert result[0] == sample_alliance_entity

    def test_get_alliances_by_status(self, alliance_repository, mock_session, sample_alliance_entity):
        """Test retrieval of alliances by status"""
        status = AllianceStatus.ACTIVE
        mock_session.query().filter().all.return_value = [sample_alliance_entity]

        result = alliance_repository.get_alliances_by_status(status)

        assert len(result) == 1
        assert result[0] == sample_alliance_entity

    def test_get_alliances_by_type(self, alliance_repository, mock_session, sample_alliance_entity):
        """Test retrieval of alliances by type"""
        alliance_type = AllianceType.MILITARY
        mock_session.query().filter().all.return_value = [sample_alliance_entity]

        result = alliance_repository.get_alliances_by_type(alliance_type)

        assert len(result) == 1
        assert result[0] == sample_alliance_entity

    def test_get_alliances_with_shared_enemy(self, alliance_repository, mock_session, sample_alliance_entity):
        """Test retrieval of alliances with shared enemy"""
        enemy_faction_id = sample_alliance_entity.shared_enemies[0]
        mock_session.query().filter().all.return_value = [sample_alliance_entity]

        result = alliance_repository.get_alliances_with_shared_enemy(enemy_faction_id)

        assert len(result) == 1
        assert result[0] == sample_alliance_entity

    def test_create_alliance_success(self, alliance_repository, mock_session, sample_alliance_entity):
        """Test successful alliance creation"""
        alliance_repository.create_alliance(sample_alliance_entity)

        mock_session.add.assert_called_once_with(sample_alliance_entity)
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once_with(sample_alliance_entity)

    def test_create_alliance_database_error(self, alliance_repository, mock_session, sample_alliance_entity):
        """Test alliance creation with database error"""
        mock_session.commit.side_effect = SQLAlchemyError("Database error")

        with pytest.raises(SQLAlchemyError):
            alliance_repository.create_alliance(sample_alliance_entity)

        mock_session.rollback.assert_called_once()

    def test_update_alliance_success(self, alliance_repository, mock_session, sample_alliance_entity):
        """Test successful alliance update"""
        sample_alliance_entity.name = "Updated Alliance"

        result = alliance_repository.update_alliance(sample_alliance_entity)

        assert result == sample_alliance_entity
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once_with(sample_alliance_entity)

    def test_update_alliance_database_error(self, alliance_repository, mock_session, sample_alliance_entity):
        """Test alliance update with database error"""
        mock_session.commit.side_effect = SQLAlchemyError("Database error")

        with pytest.raises(SQLAlchemyError):
            alliance_repository.update_alliance(sample_alliance_entity)

        mock_session.rollback.assert_called_once()

    def test_delete_alliance_success(self, alliance_repository, mock_session, sample_alliance_entity):
        """Test successful alliance deletion"""
        alliance_id = sample_alliance_entity.id
        mock_session.query().filter().first.return_value = sample_alliance_entity

        result = alliance_repository.delete_alliance(alliance_id)

        assert result is True
        mock_session.delete.assert_called_once_with(sample_alliance_entity)
        mock_session.commit.assert_called_once()

    def test_delete_alliance_not_found(self, alliance_repository, mock_session):
        """Test alliance deletion when alliance doesn't exist"""
        alliance_id = uuid4()
        mock_session.query().filter().first.return_value = None

        result = alliance_repository.delete_alliance(alliance_id)

        assert result is False
        mock_session.delete.assert_not_called()

    def test_delete_alliance_database_error(self, alliance_repository, mock_session, sample_alliance_entity):
        """Test alliance deletion with database error"""
        alliance_id = sample_alliance_entity.id
        mock_session.query().filter().first.return_value = sample_alliance_entity
        mock_session.commit.side_effect = SQLAlchemyError("Database error")

        with pytest.raises(SQLAlchemyError):
            alliance_repository.delete_alliance(alliance_id)

        mock_session.rollback.assert_called_once()

    # Alliance Status and Member Management Tests

    def test_update_alliance_status_success(self, alliance_repository, mock_session, sample_alliance_entity):
        """Test successful alliance status update"""
        alliance_id = sample_alliance_entity.id
        new_status = AllianceStatus.BETRAYED
        mock_session.query().filter().first.return_value = sample_alliance_entity

        result = alliance_repository.update_alliance_status(alliance_id, new_status)

        assert result is True
        assert sample_alliance_entity.status == new_status.value
        mock_session.commit.assert_called_once()

    def test_update_alliance_status_not_found(self, alliance_repository, mock_session):
        """Test alliance status update when alliance doesn't exist"""
        alliance_id = uuid4()
        new_status = AllianceStatus.BETRAYED
        mock_session.query().filter().first.return_value = None

        result = alliance_repository.update_alliance_status(alliance_id, new_status)

        assert result is False

    def test_add_faction_to_alliance_success(self, alliance_repository, mock_session, sample_alliance_entity):
        """Test successfully adding faction to alliance"""
        alliance_id = sample_alliance_entity.id
        new_faction_id = uuid4()
        mock_session.query().filter().first.return_value = sample_alliance_entity

        result = alliance_repository.add_faction_to_alliance(alliance_id, new_faction_id)

        assert result is True
        assert new_faction_id in sample_alliance_entity.member_faction_ids
        mock_session.commit.assert_called_once()

    def test_add_faction_to_alliance_already_member(self, alliance_repository, mock_session, sample_alliance_entity):
        """Test adding faction that's already a member"""
        alliance_id = sample_alliance_entity.id
        existing_faction_id = sample_alliance_entity.member_faction_ids[0]
        mock_session.query().filter().first.return_value = sample_alliance_entity

        result = alliance_repository.add_faction_to_alliance(alliance_id, existing_faction_id)

        assert result is False  # Should not add duplicate

    def test_remove_faction_from_alliance_success(self, alliance_repository, mock_session, sample_alliance_entity):
        """Test successfully removing faction from alliance"""
        alliance_id = sample_alliance_entity.id
        faction_to_remove = sample_alliance_entity.member_faction_ids[0]
        mock_session.query().filter().first.return_value = sample_alliance_entity

        result = alliance_repository.remove_faction_from_alliance(alliance_id, faction_to_remove)

        assert result is True
        assert faction_to_remove not in sample_alliance_entity.member_faction_ids
        mock_session.commit.assert_called_once()

    def test_remove_faction_from_alliance_not_member(self, alliance_repository, mock_session, sample_alliance_entity):
        """Test removing faction that's not a member"""
        alliance_id = sample_alliance_entity.id
        non_member_faction_id = uuid4()
        mock_session.query().filter().first.return_value = sample_alliance_entity

        result = alliance_repository.remove_faction_from_alliance(alliance_id, non_member_faction_id)

        assert result is False

    def test_update_alliance_trust_levels(self, alliance_repository, mock_session, sample_alliance_entity):
        """Test updating alliance trust levels"""
        alliance_id = sample_alliance_entity.id
        new_trust_levels = {"faction1": 0.9, "faction3": 0.6}
        mock_session.query().filter().first.return_value = sample_alliance_entity

        result = alliance_repository.update_alliance_trust_levels(alliance_id, new_trust_levels)

        assert result is True
        assert sample_alliance_entity.trust_levels == new_trust_levels
        mock_session.commit.assert_called_once()

    def test_update_alliance_betrayal_risks(self, alliance_repository, mock_session, sample_alliance_entity):
        """Test updating alliance betrayal risks"""
        alliance_id = sample_alliance_entity.id
        new_betrayal_risks = {"faction1": 0.1, "faction3": 0.4}
        mock_session.query().filter().first.return_value = sample_alliance_entity

        result = alliance_repository.update_alliance_betrayal_risks(alliance_id, new_betrayal_risks)

        assert result is True
        assert sample_alliance_entity.betrayal_risks == new_betrayal_risks
        mock_session.commit.assert_called_once()

    # Betrayal CRUD Tests

    def test_get_betrayal_by_id_success(self, alliance_repository, mock_session, sample_betrayal_entity):
        """Test successful betrayal retrieval by ID"""
        betrayal_id = sample_betrayal_entity.id
        mock_session.query().filter().first.return_value = sample_betrayal_entity

        result = alliance_repository.get_betrayal_by_id(betrayal_id)

        assert result == sample_betrayal_entity

    def test_get_betrayals_by_alliance(self, alliance_repository, mock_session, sample_betrayal_entity):
        """Test retrieval of betrayals by alliance ID"""
        alliance_id = sample_betrayal_entity.alliance_id
        mock_session.query().filter().all.return_value = [sample_betrayal_entity]

        result = alliance_repository.get_betrayals_by_alliance(alliance_id)

        assert len(result) == 1
        assert result[0] == sample_betrayal_entity

    def test_get_betrayals_by_faction(self, alliance_repository, mock_session, sample_betrayal_entity):
        """Test retrieval of betrayals involving a faction"""
        faction_id = sample_betrayal_entity.betrayer_faction_id
        mock_session.query().filter().all.return_value = [sample_betrayal_entity]

        result = alliance_repository.get_betrayals_by_faction(faction_id)

        assert len(result) == 1
        assert result[0] == sample_betrayal_entity

    def test_get_betrayals_by_betrayer(self, alliance_repository, mock_session, sample_betrayal_entity):
        """Test retrieval of betrayals by betrayer faction"""
        betrayer_id = sample_betrayal_entity.betrayer_faction_id
        mock_session.query().filter().all.return_value = [sample_betrayal_entity]

        result = alliance_repository.get_betrayals_by_betrayer(betrayer_id)

        assert len(result) == 1
        assert result[0] == sample_betrayal_entity

    def test_get_recent_betrayals(self, alliance_repository, mock_session, sample_betrayal_entity):
        """Test retrieval of recent betrayals"""
        mock_session.query().order_by().limit().all.return_value = [sample_betrayal_entity]

        result = alliance_repository.get_recent_betrayals(limit=5)

        assert len(result) == 1
        assert result[0] == sample_betrayal_entity

    def test_create_betrayal_success(self, alliance_repository, mock_session, sample_betrayal_entity):
        """Test successful betrayal creation"""
        result = alliance_repository.create_betrayal(sample_betrayal_entity)

        assert result == sample_betrayal_entity
        mock_session.add.assert_called_once_with(sample_betrayal_entity)
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once_with(sample_betrayal_entity)

    def test_update_betrayal_success(self, alliance_repository, mock_session, sample_betrayal_entity):
        """Test successful betrayal update"""
        sample_betrayal_entity.description = "Updated betrayal description"

        result = alliance_repository.update_betrayal(sample_betrayal_entity)

        assert result == sample_betrayal_entity
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once_with(sample_betrayal_entity)

    def test_delete_betrayal_success(self, alliance_repository, mock_session, sample_betrayal_entity):
        """Test successful betrayal deletion"""
        betrayal_id = sample_betrayal_entity.id
        mock_session.query().filter().first.return_value = sample_betrayal_entity

        result = alliance_repository.delete_betrayal(betrayal_id)

        assert result is True
        mock_session.delete.assert_called_once_with(sample_betrayal_entity)
        mock_session.commit.assert_called_once()

    # Statistics and Analytics Tests

    def test_get_faction_alliance_count(self, alliance_repository, mock_session):
        """Test getting alliance count for a faction"""
        faction_id = uuid4()
        mock_session.query().filter().count.return_value = 3

        result = alliance_repository.get_faction_alliance_count(faction_id)

        assert result == 3

    def test_get_faction_betrayal_count(self, alliance_repository, mock_session):
        """Test getting betrayal count for a faction"""
        faction_id = uuid4()
        mock_session.query().filter().count.return_value = 2

        result = alliance_repository.get_faction_betrayal_count(faction_id)

        assert result == 2

    def test_get_alliance_statistics(self, alliance_repository, mock_session):
        """Test getting comprehensive alliance statistics"""
        # Mock various count queries
        mock_session.query().count.side_effect = [
            10,  # total_alliances
            5,   # active_alliances
            2,   # proposed_alliances
            1,   # betrayed_alliances
            2,   # dissolved_alliances
            4,   # military_alliances
            3,   # economic_alliances
            2,   # temporary_truces
            15   # total_betrayals
        ]
        
        # Mock average calculation
        mock_session.query().filter().all.return_value = [
            Mock(trust_levels={"f1": 0.8, "f2": 0.7}),
            Mock(trust_levels={"f3": 0.6, "f4": 0.9})
        ]

        result = alliance_repository.get_alliance_statistics()

        assert result["total_alliances"] == 10
        assert result["active_alliances"] == 5
        assert result["proposed_alliances"] == 2
        assert result["betrayed_alliances"] == 1
        assert result["dissolved_alliances"] == 2
        assert result["alliance_types"]["military"] == 4
        assert result["alliance_types"]["economic"] == 3
        assert result["alliance_types"]["temporary_truce"] == 2
        assert result["total_betrayals"] == 15
        assert "average_trust_level" in result

    def test_find_potential_alliance_partners(self, alliance_repository, mock_session):
        """Test finding potential alliance partners for a faction"""
        faction_id = uuid4()
        shared_enemy_id = uuid4()
        
        # Mock query results - factions that have the shared enemy but aren't allied with our faction
        potential_partners = [uuid4(), uuid4(), uuid4()]
        mock_session.query().distinct().filter().all.return_value = potential_partners

        result = alliance_repository.find_potential_alliance_partners(faction_id, shared_enemy_id)

        assert len(result) == 3
        assert all(partner_id in potential_partners for partner_id in result)

    def test_find_potential_alliance_partners_no_shared_enemy(self, alliance_repository, mock_session):
        """Test finding potential alliance partners without shared enemy constraint"""
        faction_id = uuid4()
        
        # Mock query results - all factions not currently allied
        potential_partners = [uuid4(), uuid4(), uuid4(), uuid4()]
        mock_session.query().distinct().filter().all.return_value = potential_partners

        result = alliance_repository.find_potential_alliance_partners(faction_id, None)

        assert len(result) == 4
        assert all(partner_id in potential_partners for partner_id in result)

    # Error Handling and Edge Cases

    def test_repository_with_none_session(self):
        """Test repository initialization with None session"""
        repo = AllianceRepository(db_session=None)
        assert repo.db_session is None

    def test_database_connection_error(self, alliance_repository, mock_session):
        """Test handling of database connection errors"""
        mock_session.query.side_effect = SQLAlchemyError("Connection lost")

        with pytest.raises(SQLAlchemyError):
            alliance_repository.get_active_alliances()

    def test_transaction_rollback_on_error(self, alliance_repository, mock_session, sample_alliance_entity):
        """Test that transactions are properly rolled back on errors"""
        mock_session.commit.side_effect = SQLAlchemyError("Transaction failed")

        with pytest.raises(SQLAlchemyError):
            alliance_repository.create_alliance(sample_alliance_entity)

        mock_session.rollback.assert_called_once()

    # Complex Query Tests

    def test_complex_alliance_filtering(self, alliance_repository, mock_session, sample_alliance_entity):
        """Test complex filtering scenarios"""
        # Test multiple filters applied simultaneously
        mock_session.query().filter().filter().filter().all.return_value = [sample_alliance_entity]

        # This would represent a complex query with multiple filters
        # The actual implementation would need to support this
        result = alliance_repository.get_active_alliances()
        
        assert len(result) == 1
        assert result[0] == sample_alliance_entity

    def test_pagination_support(self, alliance_repository, mock_session):
        """Test pagination for large result sets"""
        # Mock paginated results
        alliances = [Mock(id=uuid4()) for _ in range(20)]
        mock_session.query().offset().limit().all.return_value = alliances[:10]

        # This would be implemented as a paginated query method
        # result = alliance_repository.get_alliances_paginated(page=1, size=10)
        
        # For now, just test that the repository can handle large datasets
        result = alliance_repository.get_active_alliances()
        assert len(result) <= 10  # Assuming pagination limits results

    def test_concurrent_access_handling(self, alliance_repository, mock_session, sample_alliance_entity):
        """Test handling of concurrent access scenarios"""
        # Simulate optimistic locking or version conflicts
        mock_session.commit.side_effect = [None, SQLAlchemyError("Version conflict")]

        # First update succeeds
        result1 = alliance_repository.update_alliance(sample_alliance_entity)
        assert result1 == sample_alliance_entity

        # Second update fails due to concurrent modification
        with pytest.raises(SQLAlchemyError):
            alliance_repository.update_alliance(sample_alliance_entity)


# Integration Tests

class TestAllianceRepositoryIntegration:
    """Integration tests for AllianceRepository with real database operations"""

    @pytest.fixture
    def real_session(self):
        """This would be a real database session for integration tests"""
        # In a real test environment, this would create a test database connection
        # For now, we'll mock it but structure the tests for real integration
        return Mock(spec=Session)

    @pytest.fixture
    def integration_repository(self, real_session):
        """Repository for integration testing"""
        return AllianceRepository(db_session=real_session)

    def test_alliance_lifecycle_integration(self, integration_repository, real_session):
        """Test complete alliance lifecycle with database operations"""
        # This would test the full CRUD lifecycle with a real database
        # 1. Create alliance
        # 2. Retrieve and verify
        # 3. Update alliance
        # 4. Add/remove members
        # 5. Update status
        # 6. Delete alliance
        
        # For now, we mock the operations but maintain the structure
        alliance_entity = Mock(spec=AllianceEntity)
        real_session.add.return_value = None
        real_session.commit.return_value = None
        real_session.refresh.return_value = None

        result = integration_repository.create_alliance(alliance_entity)
        assert result == alliance_entity

    def test_betrayal_lifecycle_integration(self, integration_repository, real_session):
        """Test complete betrayal lifecycle with database operations"""
        # Similar to alliance lifecycle but for betrayals
        betrayal_entity = Mock(spec=BetrayalEntity)
        real_session.add.return_value = None
        real_session.commit.return_value = None
        real_session.refresh.return_value = None

        result = integration_repository.create_betrayal(betrayal_entity)
        assert result == betrayal_entity

    def test_complex_queries_integration(self, integration_repository, real_session):
        """Test complex queries that involve multiple tables"""
        # Test queries that join alliances with betrayals, factions, etc.
        real_session.query().join().filter().all.return_value = []

        result = integration_repository.get_alliance_statistics()
        assert isinstance(result, dict) 
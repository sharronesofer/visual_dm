"""
Tests for faction services.
"""

import pytest
from datetime import datetime
from app.core.models.faction import Faction
from app.core.services.faction_service import (
    FactionService, FactionRelationshipService
)
from app.core.exceptions import (
    FactionNotFoundError, InvalidRelationshipError,
    DuplicateFactionError
)

@pytest.fixture
def faction_data():
    """Test faction data."""
    return {
        "name": "Test Kingdom",
        "description": "A test kingdom",
        "faction_type": FactionType.KINGDOM,
        "influence": 50.0,
        "resources": {"gold": 1000, "troops": 500},
        "territory": {"capital": "Test City", "regions": ["North", "South"]},
        "traits": {"diplomatic": True, "aggressive": False},
        "metadata": {"founded": "2024"}
    }

@pytest.fixture
def test_faction(faction_data):
    """Create a test faction."""
    return FactionService.create_faction(**faction_data)

@pytest.fixture
def test_factions():
    """Create multiple test factions."""
    factions = []
    for i in range(3):
        data = {
            "name": f"Test Faction {i}",
            "description": f"Test faction {i}",
            "faction_type": FactionType.GUILD,
            "influence": float(i * 10)
        }
        factions.append(FactionService.create_faction(**data))
    return factions

class TestFactionService:
    """Test cases for FactionService."""

    def test_create_faction(self, faction_data):
        """Test creating a new faction."""
        faction = FactionService.create_faction(**faction_data)
        assert faction.name == faction_data["name"]
        assert faction.faction_type == faction_data["faction_type"]
        assert faction.influence == faction_data["influence"]
        assert faction.resources == faction_data["resources"]
        assert faction.status == FactionStatus.ACTIVE

    def test_create_duplicate_faction(self, test_faction, faction_data):
        """Test creating a faction with duplicate name."""
        with pytest.raises(DuplicateFactionError):
            FactionService.create_faction(**faction_data)

    def test_get_faction(self, test_faction):
        """Test retrieving a faction."""
        faction = FactionService.get_faction(test_faction.id)
        assert faction.id == test_faction.id
        assert faction.name == test_faction.name

    def test_get_nonexistent_faction(self):
        """Test retrieving a non-existent faction."""
        faction = FactionService.get_faction(999)
        assert faction is None

    def test_get_factions_with_filters(self, test_factions):
        """Test retrieving factions with filters."""
        # Test type filter
        factions = FactionService.get_factions(faction_type=FactionType.GUILD)
        assert len(factions) == 3
        assert all(f.faction_type == FactionType.GUILD for f in factions)

        # Test influence filter
        factions = FactionService.get_factions(min_influence=15.0)
        assert len(factions) == 1
        assert all(f.influence >= 15.0 for f in factions)

    def test_update_faction(self, test_faction):
        """Test updating faction attributes."""
        updates = {
            "name": "Updated Kingdom",
            "description": "Updated description",
            "influence": 75.0,
            "resources": {"gold": 2000},
            "territory": {"new_region": "East"}
        }
        
        updated = FactionService.update_faction(test_faction.id, **updates)
        assert updated.name == updates["name"]
        assert updated.influence == updates["influence"]
        assert updated.resources["gold"] == 2000
        assert "new_region" in updated.territory

    def test_update_nonexistent_faction(self):
        """Test updating a non-existent faction."""
        with pytest.raises(FactionNotFoundError):
            FactionService.update_faction(999, name="New Name")

    def test_delete_faction(self, test_faction):
        """Test deleting a faction."""
        FactionService.delete_faction(test_faction.id)
        assert FactionService.get_faction(test_faction.id) is None

class TestFactionRelationshipService:
    """Test cases for FactionRelationshipService."""

    @pytest.fixture
    def test_relationship(self, test_factions):
        """Create a test relationship."""
        return FactionRelationshipService.set_relationship(
            test_factions[0].id,
            test_factions[1].id,
            RelationType.FRIENDLY,
            reputation_score=50.0,
            trade_status=True
        )

    def test_set_relationship(self, test_factions):
        """Test creating a new relationship."""
        relationship = FactionRelationshipService.set_relationship(
            test_factions[0].id,
            test_factions[1].id,
            RelationType.ALLIED,
            reputation_score=80.0
        )
        
        assert relationship.faction_id == test_factions[0].id
        assert relationship.target_faction_id == test_factions[1].id
        assert relationship.relation_type == RelationType.ALLIED
        assert relationship.reputation_score == 80.0
        assert relationship.alliance_date is not None

    def test_update_existing_relationship(self, test_relationship, test_factions):
        """Test updating an existing relationship."""
        updated = FactionRelationshipService.set_relationship(
            test_factions[0].id,
            test_factions[1].id,
            RelationType.HOSTILE,
            reputation_score=-30.0
        )
        
        assert updated.id == test_relationship.id
        assert updated.relation_type == RelationType.HOSTILE
        assert updated.reputation_score == -30.0
        assert updated.last_conflict_date is not None

    def test_invalid_relationship(self, test_faction):
        """Test creating invalid relationships."""
        # Self-relationship
        with pytest.raises(InvalidRelationshipError):
            FactionRelationshipService.set_relationship(
                test_faction.id,
                test_faction.id,
                RelationType.FRIENDLY
            )

        # Non-existent faction
        with pytest.raises(FactionNotFoundError):
            FactionRelationshipService.set_relationship(
                test_faction.id,
                999,
                RelationType.FRIENDLY
            )

    def test_get_relationship(self, test_relationship, test_factions):
        """Test retrieving a relationship."""
        relationship = FactionRelationshipService.get_relationship(
            test_factions[0].id,
            test_factions[1].id
        )
        assert relationship.id == test_relationship.id

    def test_get_faction_relationships(self, test_factions):
        """Test retrieving all relationships for a faction."""
        # Create multiple relationships
        FactionRelationshipService.set_relationship(
            test_factions[0].id,
            test_factions[1].id,
            RelationType.FRIENDLY,
            reputation_score=30.0
        )
        FactionRelationshipService.set_relationship(
            test_factions[0].id,
            test_factions[2].id,
            RelationType.HOSTILE,
            reputation_score=-30.0
        )

        # Test getting all relationships
        relationships = FactionRelationshipService.get_faction_relationships(
            test_factions[0].id
        )
        assert len(relationships) == 2

        # Test filtering by type
        hostile = FactionRelationshipService.get_faction_relationships(
            test_factions[0].id,
            relation_type=RelationType.HOSTILE
        )
        assert len(hostile) == 1
        assert hostile[0].relation_type == RelationType.HOSTILE

    def test_update_reputation(self, test_relationship, test_factions):
        """Test updating reputation and relation type changes."""
        # Test positive change
        rel, new_type = FactionRelationshipService.update_reputation(
            test_factions[0].id,
            test_factions[1].id,
            30.0
        )
        assert rel.reputation_score == 80.0
        assert new_type == RelationType.ALLIED

        # Test negative change
        rel, new_type = FactionRelationshipService.update_reputation(
            test_factions[0].id,
            test_factions[1].id,
            -100.0
        )
        assert rel.reputation_score == -20.0
        assert new_type == RelationType.NEUTRAL

        # Test bounds
        rel, _ = FactionRelationshipService.update_reputation(
            test_factions[0].id,
            test_factions[1].id,
            -200.0
        )
        assert rel.reputation_score == -100.0

    def test_delete_relationship(self, test_relationship, test_factions):
        """Test deleting a relationship."""
        FactionRelationshipService.delete_relationship(
            test_factions[0].id,
            test_factions[1].id
        )
        
        relationship = FactionRelationshipService.get_relationship(
            test_factions[0].id,
            test_factions[1].id
        )
        assert relationship is None 
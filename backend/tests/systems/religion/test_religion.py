from backend.systems.shared.database.base import Base
from backend.systems.religion.models import Religion
from backend.systems.religion.services import ReligionService
from backend.systems.shared.database.base import Base
from backend.systems.religion.models import Religion
from backend.systems.religion.services import ReligionService
from backend.systems.religion.models import Religion
from backend.systems.religion.services import ReligionService
from backend.systems.religion.models import Religion
from backend.systems.religion.services import ReligionService
from backend.systems.religion.models import Religion
from backend.systems.religion.services import ReligionService
from backend.systems.religion.models import Religion
from backend.systems.religion.services import ReligionService
from typing import Type
from typing import List
"""
Tests for the religion system.
"""

import pytest
import os
import uuid
from typing import Dict, List

from backend.systems.religion import (
    Religion,
    ReligionType,
    ReligionMembership,
    ReligionResponse,
    ReligionService,
    get_religion_service,
    calculate_devotion_change,
    calculate_religion_compatibility,
)


class TestReligionModels:
    """Test religion model functionality."""

    def test_religion_creation(self):
        """Test creating a Religion object."""
        religion = Religion(
            id=str(uuid.uuid4()),
            name="Test Religion",
            description="A test religion",
            type=ReligionType.POLYTHEISTIC,
            tenets=["Be good", "Do good"],
            holy_places=["Temple"],
            region_ids=["region1"],
            created_at="2023-01-01T00:00:00",
            updated_at="2023-01-01T00:00:00",
        )

        assert religion.name == "Test Religion"
        assert religion.type == ReligionType.POLYTHEISTIC
        assert len(religion.tenets) == 2
        assert "Temple" in religion.holy_places

    def test_religion_membership(self):
        """Test creating a ReligionMembership object."""
        membership = ReligionMembership(
            id=str(uuid.uuid4()),
            entity_id="entity123",
            religion_id="religion123",
            devotion_level=75,
            is_public=True,
            role="priest",
            joined_at="2023-01-01T00:00:00",
            updated_at="2023-01-01T00:00:00",
        )

        assert membership.entity_id == "entity123"
        assert membership.religion_id == "religion123"
        assert membership.devotion_level == 75
        assert membership.is_public is True
        assert membership.role == "priest"


class TestReligionService:
    """Test religion service functionality."""

    @pytest.fixture
    def service(self):
        """Provide a religion service instance."""
        # Make sure we test with a temporary data file
        os.environ["RELIGION_DATA_PATH"] = "test_religions.json"
        os.environ["RELIGION_MEMBERSHIP_DATA_PATH"] = "test_memberships.json"

        service = ReligionService()
        yield service

        # Cleanup
        if os.path.exists("test_religions.json"):
            os.remove("test_religions.json")
        if os.path.exists("test_memberships.json"):
            os.remove("test_memberships.json")

    def test_create_religion(self, service):
        """Test creating a religion."""
        religion_data = {
            "name": "Test Faith",
            "description": "A test religion",
            "type": ReligionType.MONOTHEISTIC,
            "tenets": ["Worship one deity", "Be kind"],
            "holy_places": ["Great Temple"],
            "region_ids": ["region1", "region2"],
        }

        religion = service.create_religion(religion_data)

        assert religion.name == "Test Faith"
        assert religion.type == ReligionType.MONOTHEISTIC
        assert len(religion.tenets) == 2
        assert len(religion.region_ids) == 2

    def test_get_religion(self, service):
        """Test retrieving a religion."""
        # Create a religion first
        religion_data = {
            "name": "Retrieval Test",
            "description": "A retrievable religion",
            "type": ReligionType.ANIMISTIC,
            "tenets": ["Honor nature"],
        }

        created = service.create_religion(religion_data)
        retrieved = service.get_religion(created.id)

        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.name == "Retrieval Test"

    def test_create_membership(self, service):
        """Test creating a religion membership."""
        # Create a religion first
        religion = service.create_religion(
            {
                "name": "Membership Test",
                "description": "Testing memberships",
                "type": ReligionType.CULT,
            }
        )

        membership_data = {
            "entity_id": "character123",
            "religion_id": religion.id,
            "devotion_level": 50,
            "is_public": True,
            "role": "acolyte",
        }

        membership = service.create_membership(membership_data)

        assert membership.entity_id == "character123"
        assert membership.religion_id == religion.id
        assert membership.devotion_level == 50
        assert membership.role == "acolyte"

    def test_update_devotion(self, service):
        """Test updating devotion level."""
        # Setup
        religion = service.create_religion(
            {
                "name": "Devotion Test",
                "description": "Testing devotion changes",
                "type": ReligionType.ANCESTOR,
            }
        )

        membership = service.create_membership(
            {
                "entity_id": "character456",
                "religion_id": religion.id,
                "devotion_level": 40,
            }
        )

        # Test increase
        service.update_devotion("character456", religion.id, 15)
        updated = service.get_membership("character456", religion.id)

        assert updated is not None
        assert updated.devotion_level == 55  # 40 + 15

        # Test decrease
        service.update_devotion("character456", religion.id, -20)
        updated = service.get_membership("character456", religion.id)

        assert updated.devotion_level == 35  # 55 - 20


class TestReligionUtils:
    """Test religion utility functions."""

    def test_calculate_devotion_change(self):
        """Test devotion change calculation."""
        # Base case - no factors
        result = calculate_devotion_change(10, {})
        assert result == 10  # No change

        # With positive factors
        result = calculate_devotion_change(10, {"festival": 0.5, "donation": 0.2})
        assert result == 17  # 10 * (1 + 0.5 + 0.2)

        # With negative factors
        result = calculate_devotion_change(10, {"scandal": -0.3, "absence": -0.1})
        assert result == 6  # 10 * (1 - 0.3 - 0.1)

        # Mixed factors
        result = calculate_devotion_change(10, {"festival": 0.5, "scandal": -0.3})
        assert result == 12  # 10 * (1 + 0.5 - 0.3)

    def test_calculate_religion_compatibility(self):
        """Test religion compatibility calculation."""
        religion1 = Religion(
            id="1",
            name="Sun Faith",
            description="Sun worship",
            type=ReligionType.POLYTHEISTIC,
            tenets=["Honor the sun", "Light candles at dusk"],
            holy_places=["Sun Temple", "Mountain Top"],
            tags=["sun", "light", "fire"],
            created_at="2023-01-01T00:00:00",
            updated_at="2023-01-01T00:00:00",
        )

        religion2 = Religion(
            id="2",
            name="Moon Faith",
            description="Moon worship",
            type=ReligionType.POLYTHEISTIC,
            tenets=["Honor the moon", "Light candles at dusk"],
            holy_places=["Moon Temple", "Mountain Top"],
            tags=["moon", "night", "darkness"],
            created_at="2023-01-01T00:00:00",
            updated_at="2023-01-01T00:00:00",
        )

        # Same type, some shared elements
        compatibility = calculate_religion_compatibility(religion1, religion2)
        assert 0.8 < compatibility < 1.0  # Base + some shared elements

        # Different types
        religion3 = Religion(
            id="3",
            name="One God",
            description="Monotheistic faith",
            type=ReligionType.MONOTHEISTIC,
            tenets=["One deity", "Daily prayer"],
            holy_places=["Temple"],
            tags=["structured", "doctrine"],
            created_at="2023-01-01T00:00:00",
            updated_at="2023-01-01T00:00:00",
        )

        compatibility = calculate_religion_compatibility(religion1, religion3)
        assert compatibility < 0.5  # Less compatible

from backend.systems.shared.database.base import Base
from backend.systems.events.dispatcher import EventDispatcher
from backend.systems.economy.models import Resource
from backend.systems.shared.database.base import Base
from backend.systems.events.dispatcher import EventDispatcher
from backend.systems.economy.models import Resource
from backend.systems.events.dispatcher import EventDispatcher
from backend.systems.economy.models import Resource
from backend.systems.events.dispatcher import EventDispatcher
from backend.systems.economy.models import Resource
from backend.systems.events.dispatcher import EventDispatcher
from backend.systems.economy.models import Resource
from backend.systems.events.dispatcher import EventDispatcher
from backend.systems.economy.models import Resource

# Import EventBase and EventDispatcher with fallbacks
try:
    from backend.systems.events import EventBase, EventDispatcher
except ImportError:
    # Fallback for tests or when events system isn't available
    class EventBase:
        def __init__(self, **data):
            for key, value in data.items():
                setattr(self, key, value)
    
    class EventDispatcher:
        @classmethod
        def get_instance(cls):
            return cls()
        
        def dispatch(self, event):
            pass
        
        def publish(self, event):
            pass
        
        def emit(self, event):
            pass

"""
Fixtures for equipment system tests.
This module provides shared fixtures that can be used across multiple test files.
"""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock

# Import necessary models to ensure SQLAlchemy can find them for relationships
from backend.systems.shared.models.base import Base
from backend.systems.region.models import Region
from backend.systems.faction.models.faction import Faction, FactionRelationship
from backend.systems.economy.models.resource import Resource
from backend.systems.economy.models.market import Market
from backend.systems.economy.models.commodity_future import CommodityFuture
from backend.systems.character.core.character_model import Character
from backend.systems.inventory.models.item import Item


@pytest.fixture
def mock_db_session():
    """Create a mock database session."""
    with patch("backend.core.database.db") as mock_db:
        mock_db.session = MagicMock()
        # Add common methods to the session
        mock_db.session.query = MagicMock(return_value=MagicMock())
        mock_db.session.add = MagicMock()
        mock_db.session.commit = MagicMock()
        mock_db.session.refresh = MagicMock()
        mock_db.session.rollback = MagicMock()
        yield mock_db


@pytest.fixture
def mock_event_dispatcher():
    """Create a mock event dispatcher."""
    with patch(
        "backend.app.core.events.event_dispatcher.EventDispatcher"
    ) as mock_dispatcher_class:
        mock_dispatcher_instance = MagicMock()
        mock_dispatcher_instance.publish_sync = MagicMock()
        mock_dispatcher_instance.publish_async = AsyncMock()
        mock_dispatcher_class.get_instance.return_value = mock_dispatcher_instance
        yield mock_dispatcher_instance


@pytest.fixture
def sample_equipment_data():
    """Return sample equipment data."""
    return {
        "id": 1,
        "character_id": 100,
        "slot": "weapon",
        "item_id": 1001,
        "current_durability": 90.0,
        "max_durability": 100.0,
        "equipped_at": "2023-09-15T12:00:00",
        "is_broken": False,
    }


@pytest.fixture
def sample_equipment_set_data():
    """Return sample equipment set data."""
    return {
        "id": 1,
        "name": "Warrior Set",
        "description": "A set of warrior equipment",
        "item_ids": [1001, 1002, 1003, 1004],
        "set_bonuses": {
            "2": {"stat_bonus": {"strength": 1}},
            "4": {"stat_bonus": {"strength": 2, "dexterity": 1}},
        },
    }


@pytest.fixture
def sample_item_data():
    """Return sample item data as would be provided by the item system."""
    return {
        "id": 1001,
        "name": "Steel Sword",
        "type": "weapon",
        "stats": {"damage": 10, "durability": 100},
        "properties": {"material": "steel", "two_handed": False},
        "rarity": "common",
        "value": 100,
        "effects": [
            {
                "name": "Sharp Edge",
                "identified": True,
                "description": "Increases damage by 2",
            },
            {
                "name": "Quality Steel",
                "identified": False,
                "description": "Increases durability by 20%",
            },
        ],
    }


@pytest.fixture
def sample_character_equipment():
    """Return a sample of all equipment for a character."""
    return [
        {
            "id": 1,
            "character_id": 100,
            "slot": "weapon",
            "item_id": 1001,
            "current_durability": 90.0,
            "max_durability": 100.0,
        },
        {
            "id": 2,
            "character_id": 100,
            "slot": "chest",
            "item_id": 1002,
            "current_durability": 80.0,
            "max_durability": 100.0,
        },
        {
            "id": 3,
            "character_id": 100,
            "slot": "legs",
            "item_id": 1003,
            "current_durability": 95.0,
            "max_durability": 100.0,
        },
    ]

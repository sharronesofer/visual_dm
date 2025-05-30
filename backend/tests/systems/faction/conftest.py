from backend.systems.shared.database.base import Base
from backend.systems.events.dispatcher import EventDispatcher
from backend.systems.shared.database.base import Base
from backend.systems.events.dispatcher import EventDispatcher
from backend.systems.events.dispatcher import EventDispatcher
from backend.systems.events.dispatcher import EventDispatcher
from backend.systems.events.dispatcher import EventDispatcher
from backend.systems.events.dispatcher import EventDispatcher
import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

from backend.systems.faction.models.faction import Faction
from backend.systems.faction.models.faction import FactionRelationship
from backend.systems.faction.repositories.faction_repository import FactionRepository
from backend.systems.faction.repositories.faction_repository import FactionRelationshipRepository
from backend.systems.events.event_dispatcher import EventDispatcher


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

@pytest.fixture
def mock_db():
    """Create a mock database session."""
    mock = AsyncMock()
    mock.fetch_all = AsyncMock()
    mock.fetch_one = AsyncMock()
    mock.insert = AsyncMock()
    mock.update = AsyncMock()
    mock.delete = AsyncMock()
    return mock

@pytest.fixture
def mock_event_dispatcher():
    """Create a mock for the event dispatcher."""
    mock = MagicMock(spec=EventDispatcher)
    mock.publish = MagicMock()
    return mock

@pytest.fixture
def sample_faction():
    """Create a sample faction for testing."""
    return Faction(
        id="faction-123",
        name="Iron Legion",
        type="MILITARY",
        description="A militaristic faction focused on conquest",
        alignment="LAWFUL_EVIL",
        influence=75,
        territories=["region-1", "region-2"],
        resources={"gold": 1000, "iron": 500},
        members=["npc-234", "npc-345"],
        tension={"faction-456": 85, "faction-789": 40},
        war_state={"faction-456": "ACTIVE_WAR", "faction-789": "NEUTRAL"},
        is_active=True,
        affinity={"npc-234": 90, "npc-345": 85},
        membership_logic={"join_threshold": 60, "leave_threshold": 30},
        tension_decay_rate=0.1,
        created_at=datetime.now().isoformat(),
        updated_at=datetime.now().isoformat()
    )

@pytest.fixture
def sample_relationship():
    """Create a sample faction relationship for testing."""
    return FactionRelationship(
        source_faction_id="faction-123",
        target_faction_id="faction-456",
        type="HOSTILE",
        tension=85,
        war_state="ACTIVE_WAR",
        last_interaction_date=datetime.now().isoformat(),
        treaties=[],
        shared_territory_ids=[],
        historical_conflicts=[],
        created_at=datetime.now().isoformat(),
        updated_at=datetime.now().isoformat()
    )

@pytest.fixture
def faction_repository(mock_db):
    """Create a FactionRepository instance with a mock database."""
    return FactionRepository(db=mock_db)

@pytest.fixture
def relationship_repository(mock_db):
    """Create a FactionRelationshipRepository instance with a mock database."""
    return FactionRelationshipRepository(db=mock_db) 
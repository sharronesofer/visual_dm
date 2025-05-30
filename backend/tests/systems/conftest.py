from backend.systems.shared.database.base import Base
from backend.systems.events.dispatcher import EventDispatcher
from backend.systems.shared.database.base import Base
from backend.systems.events.dispatcher import EventDispatcher

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
Common pytest fixtures for all tests.
"""

import os
import sys
import asyncio
import pytest
import json
import warnings
from unittest.mock import MagicMock, AsyncMock, patch
from pathlib import Path

# Configure pytest-asyncio
def pytest_configure(config):
    """Configure pytest."""
    # Set the fixture loop scope to function
    config.option.asyncio_default_fixture_loop_scope = "function"
    
    # Filter warnings
    warnings.filterwarnings("ignore", category=RuntimeWarning, message="coroutine .* was never awaited")
    warnings.filterwarnings("ignore", category=DeprecationWarning, message="It is deprecated to return a value") 

# Ensure the backend directory is in the path
backend_dir = str(Path(__file__).parent.parent.parent)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# Import necessary backend modules
try:
    from backend.systems.events.event_dispatcher import EventDispatcher
    from backend.systems.storage.storage_service import StorageManager
except ImportError:
    # Create stub implementations for basic testing if modules aren't available
    # This allows some tests to run even if the full backend isn't set up
    print(
        "WARNING: Some backend modules could not be imported. Using stub implementations."
    )

    class EventDispatcher:
        """Stub event dispatcher for testing."""

        def __init__(self):
            self.listeners = {}
            self.middlewares = []

        def subscribe(self, event_type, listener):
            """Subscribe to an event type."""
            if event_type not in self.listeners:
                self.listeners[event_type] = []
            self.listeners[event_type].append(listener)

        def publish(self, event):
            """Publish an event."""
            event_type = getattr(event, "event_type", None)
            if event_type in self.listeners:
                for listener in self.listeners[event_type]:
                    listener(event)

        def add_middleware(self, middleware):
            """Add middleware to the dispatcher."""
            self.middlewares.append(middleware)


@pytest.fixture
def temp_directory():
    """Create a temporary directory for test data."""
    import tempfile

    temp_dir = tempfile.TemporaryDirectory()
    yield temp_dir.name
    temp_dir.cleanup()


@pytest.fixture
def event_dispatcher():
    """Create a new event dispatcher for testing."""
    dispatcher = EventDispatcher()
    yield dispatcher


# =========================================================
# Root directory fixtures
# =========================================================
@pytest.fixture
def tests_root_dir():
    """Return the path to the tests directory."""
    return Path(__file__).parent


@pytest.fixture
def backend_root_dir():
    """Return the path to the backend directory."""
    return Path(__file__).parent.parent.parent


@pytest.fixture
def data_dir():
    """Return the path to the data directory."""
    return Path(__file__).parent.parent.parent / "data"


# =========================================================
# Mock service fixtures
# =========================================================
@pytest.fixture
def mock_event_dispatcher():
    """Fixture for mock event dispatcher."""
    mock = MagicMock(spec=EventDispatcher)

    # Add any specific method mocks here
    mock.publish.return_value = None
    mock.subscribe.return_value = None

    # Return singleton instance
    mock.get_instance.return_value = mock

    with patch("backend.systems.events.EventDispatcher", return_value=mock):
        with patch(
            "backend.systems.events.EventDispatcher.get_instance", return_value=mock
        ):
            yield mock


@pytest.fixture
def mock_storage():
    """Fixture for mock storage manager."""
    mock = MagicMock(spec=StorageManager)

    # Mock common methods
    # Use AsyncMock for async methods
    mock.get = AsyncMock(return_value={})
    mock.set = AsyncMock(return_value=None)
    mock.delete = AsyncMock(return_value=None)
    mock.list = AsyncMock(return_value=[])
    mock.exists = AsyncMock(return_value=False)

    # Specific JSON methods
    mock.get_memory_file = AsyncMock(return_value=json.dumps({"memories": []}))
    mock.save_memory_file = AsyncMock(return_value=None)

    yield mock


@pytest.fixture
def mock_gpt_client():
    """Fixture for mock GPT client."""
    mock = MagicMock()

    # Mock GPT completion
    mock.complete.return_value = "This is a mock GPT response."

    # Mock embeddings
    mock.embed_text.return_value = [0.1] * 10  # 10-dim vector
    mock.embed_texts.return_value = [[0.1] * 10 for _ in range(5)]  # 5 vectors

    yield mock


# =========================================================
# Sample data fixtures
# =========================================================
@pytest.fixture
def sample_memory_data():
    """Sample memory data for testing."""
    return {
        "char1": [
            {
                "id": "mem1",
                "content": "This is a test memory",
                "importance": 0.7,
                "created_at": "2023-01-01T00:00:00Z",
            },
            {
                "id": "mem2",
                "content": "This is another test memory",
                "importance": 0.5,
                "created_at": "2023-01-02T00:00:00Z",
            },
        ]
    }


@pytest.fixture
def sample_rumor_data():
    """Sample rumor data for testing."""
    return [
        {
            "id": "rumor1",
            "content": "This is a test rumor",
            "truth_value": 0.8,
            "spread_count": 3,
            "created_at": "2023-01-01T00:00:00Z",
        },
        {
            "id": "rumor2",
            "content": "This is another test rumor",
            "truth_value": 0.6,
            "spread_count": 5,
            "created_at": "2023-01-02T00:00:00Z",
        },
    ]


@pytest.fixture
def sample_motif_data():
    """Sample motif data for testing."""
    return {
        "motifs": [
            {
                "id": "motif1",
                "name": "test_motif",
                "description": "A test motif",
                "weight": 0.8,
                "category": "test",
            }
        ]
    }


@pytest.fixture
def reset_singletons():
    """Reset singleton instances before each test."""
    # Reset any singleton instances that might interfere with tests
    yield
    # Cleanup after test if needed


@pytest.fixture
def mock_dependencies():
    """Fixture that mocks common dependencies."""
    with patch("backend.systems.events.EventDispatcher") as mock_dispatcher:
        with patch("backend.systems.storage.storage_service.StorageManager") as mock_storage:
            mock_dispatcher.get_instance.return_value = MagicMock()
            mock_storage.get_instance.return_value = MagicMock()
            yield {
                'event_dispatcher': mock_dispatcher,
                'storage_manager': mock_storage
            } 
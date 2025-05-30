from backend.systems.data.registry import GameDataRegistry
from backend.systems.shared.database.base import Base
from backend.systems.data.registry import GameDataRegistry
from backend.systems.shared.database.base import Base
from backend.systems.data.registry import GameDataRegistry
from backend.systems.data.registry import GameDataRegistry
from backend.systems.data.registry import GameDataRegistry
from backend.systems.data.registry import GameDataRegistry
import pytest
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import StaticPool
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
import warnings
import pytest_asyncio
import sys
import logging

# Import necessary models
from backend.systems.shared.models.base import Base
from backend.systems.auth_user.models.user_models import User, Role, Permission

# Import models that might cause schema conflicts
from backend.systems.faction.models.faction import Faction, FactionRelationship
from backend.systems.region.models import Region

# Configure pytest-asyncio


@pytest.fixture(scope="function")
def db_engine():
    """Create an in-memory SQLite database engine for testing."""
    # Using memory DB with check_same_thread=False for testing
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False
    )
    
    # Create all tables
    Base.metadata.create_all(engine)
    
    yield engine
    
    # Drop all tables after test
    Base.metadata.drop_all(engine)


@pytest.fixture(scope="function")
def db_session(db_engine):
    """Create a new database session for a test."""
    # Create a session factory
    session_factory = sessionmaker(bind=db_engine)
    _session = scoped_session(session_factory)
    
    session = _session()
    
    yield session
    
    # Close and rollback the session after test
    session.close()
    _session.remove()


# Note: We're removing the custom event_loop fixture since it's already provided by pytest-asyncio
# and redefining it leads to warnings. The default pytest-asyncio event_loop is sufficient.
# If needed, we can use the @pytest.mark.asyncio(scope="function") decorator to control scope.


@pytest.fixture
def mock_auth_middleware():
    """Fixture to mock the authentication middleware."""
    with pytest.MonkeyPatch.context() as monkeypatch:
        async def mock_get_current_user(*args, **kwargs):
            return {
                "id": "test_user_id",
                "email": "test@example.com",
                "roles": ["admin"],
                "permissions": ["test_permission"]
            }
            
        # Patch the dependency in your application
        monkeypatch.setattr(
            "backend.systems.auth_user.services.auth_service.get_current_active_user", 
            mock_get_current_user
        )
        yield


# Patch the logger to suppress biome-related warnings
@pytest.fixture(scope="session", autouse=True)
def patch_loggers():
    """Patch all relevant loggers to suppress biome-related warnings."""
    # Save original logging levels
    loggers_to_patch = [
        "backend.systems.data.loaders.game_data_registry",
        "backend.systems.region.router",
        "backend.systems.world_generation.biome_utils",
        "backend.systems.loot.data_access",
        "backend.systems.world_state.utils.terrain_generator",
        "backend.systems.region.generators",
        "backend.systems.region.service",
        "backend.systems.world_state.world_utils",
        "backend.systems.world_generation.seed_loader",
    ]
    
    original_levels = {}
    
    # Capture original logging levels and set to ERROR to suppress warnings
    for logger_name in loggers_to_patch:
        logger = logging.getLogger(logger_name)
        original_levels[logger_name] = logger.level
        logger.setLevel(logging.ERROR)
    
    # Also suppress root logger warnings related to biomes
    root_logger = logging.getLogger()
    original_root_handler = None
    
    # Add a filter to the root logger's handlers
    for handler in root_logger.handlers:
        if hasattr(handler, 'addFilter'):
            original_root_handler = handler
            
            def biome_filter(record):
                # Skip any biome-related warnings
                if record.levelno == logging.WARNING:
                    msg = record.getMessage()
                    if any(term in msg for term in [
                        "land_types.json", 
                        "biome data", 
                        "adjacency.json", 
                        "adjacency rules",
                        "items directory",
                        "Biome file not found",
                    ]):
                        return False
                return True
            
            handler.addFilter(biome_filter)
    
    yield
    
    # Restore original logging levels
    for logger_name, level in original_levels.items():
        logging.getLogger(logger_name).setLevel(level)
    
    # Remove the filter
    if original_root_handler:
        for handler in root_logger.handlers:
            handler.removeFilter(biome_filter)

# Mock the GameDataRegistry to prevent biome/land_types warnings
class MockGameDataRegistry:
    def __init__(self, *args, **kwargs):
        pass
        
    def load_all(self):
        pass
    
    def get_land_types(self):
        return {}
        
    def get_adjacency_rules(self):
        return {}

# Patch the GameDataRegistry class before any tests run
@pytest.fixture(scope="session", autouse=True)
def patch_game_data_registry():
    """Patch GameDataRegistry to suppress biome-related warnings."""
    with patch("backend.systems.data.GameDataRegistry", MockGameDataRegistry):
        yield

# Suppress any other region-related warnings
@pytest.fixture(scope="session", autouse=True)
def suppress_region_warnings():
    """Suppress print warnings about region and land_types."""
    with patch("builtins.print") as mock_print:
        def filtered_print(*args, **kwargs):
            # Check if this is a warning message we want to suppress
            if args and isinstance(args[0], str):
                if any(term in args[0] for term in [
                    "land_types.json", 
                    "biome data", 
                    "adjacency.json", 
                    "adjacency rules",
                    "items directory"
                ]):
                    return
            # Pass through other print statements
            original_print(*args, **kwargs)
            
        original_print = mock_print.side_effect
        mock_print.side_effect = filtered_print
        yield

# Suppress warnings about missing biome files since they're unrelated to auth tests
@pytest.fixture(scope="session", autouse=True)
def suppress_biome_warnings():
    """Suppress warnings about missing biome and land_types files for auth tests."""
    # Save original showwarning
    original_showwarning = warnings.showwarning
    
    def custom_showwarning(message, category, filename, lineno, file=None, line=None):
        # Filter out specific warnings related to biome data
        message_str = str(message)
        if any(term in message_str for term in [
            "land_types.json", 
            "biome data", 
            "adjacency.json", 
            "adjacency rules",
            "items directory"
        ]):
            return
        # Show other warnings normally
        original_showwarning(message, category, filename, lineno, file, line)
    
    # Replace showwarning
    warnings.showwarning = custom_showwarning
    
    yield
    
    # Restore original showwarning
    warnings.showwarning = original_showwarning
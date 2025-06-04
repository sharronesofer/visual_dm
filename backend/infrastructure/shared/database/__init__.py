"""
Shared database components for business logic systems.

This module provides database access and session management for business logic
systems, using local base implementations.
"""

# Import from local base module to avoid circular imports
from .base import Base, BaseModel
from .session import get_db, MockSession
from .manager import DatabaseManager, get_database_manager, sync_database

# Create a simple alias function instead of importing to avoid circular imports
def get_async_session():
    """Get async database session - placeholder to avoid circular imports"""
    from backend.infrastructure.database import get_async_db
    return get_async_db()

# Alias for backward compatibility
get_async_db = get_async_session

class MockDatabase:
    """Mock database with key-value interface for testing."""
    
    def __init__(self):
        self._data = {}
    
    async def set(self, key: str, value: dict) -> bool:
        """Set a key-value pair."""
        self._data[key] = value
        return True
    
    async def get(self, key: str) -> dict:
        """Get a value by key."""
        return self._data.get(key)
    
    async def delete(self, key: str) -> bool:
        """Delete a key-value pair."""
        if key in self._data:
            del self._data[key]
            return True
        return False
    
    def clear(self) -> None:
        """Clear all data."""
        self._data.clear()

# Create a global mock database instance
mock_db = MockDatabase()

# Re-export for compatibility
__all__ = [
    'Base',
    'BaseModel',
    'get_db',
    'get_async_session',
    'mock_db',
    'DatabaseManager',
    'get_database_manager',
    'sync_database',
] 
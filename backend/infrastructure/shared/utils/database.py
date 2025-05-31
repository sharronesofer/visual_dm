"""
Shared database module for backward compatibility.
"""

# Re-export everything from the database package
from backend.infrastructure.database import (
    Base, 
    BaseModel,
    TimestampMixin, 
    UUIDMixin,
    GUID,
    get_db,
    get_async_db,
    SessionLocal,
    AsyncSessionLocal,
    engine,
    async_engine
)

__all__ = [
    "Base", 
    "BaseModel",
    "TimestampMixin", 
    "UUIDMixin",
    "GUID",
    "get_db",
    "get_async_db",
    "SessionLocal",
    "AsyncSessionLocal",
    "engine",
    "async_engine"
]

"""
Infrastructure Database Package

Centralized database configuration, session management, and utilities
for all systems.
"""

from .database_service import DatabaseService, get_database_service, database_session, get_db
from .async_setup import AsyncSessionLocal, get_async_db

__all__ = [
    "DatabaseService",
    "get_database_service", 
    "database_session",
    "get_db",
    "AsyncSessionLocal",
    "get_async_db",
    "Base",
    "BaseModel"
]

# Import the essential database components that exist
try:
    from backend.infrastructure.shared.database.base import Base, BaseModel, UUIDMixin, TimestampMixin, GUID
except ImportError:
    # Fallback - define Base here if shared doesn't exist
    from sqlalchemy.orm import declarative_base
    from sqlalchemy import Column, DateTime, String
    from sqlalchemy.dialects.postgresql import UUID
    from sqlalchemy.sql import func
    import uuid
    
    Base = declarative_base()
    
    class BaseModel(Base):
        """Base model with common fields for all tables."""
        __abstract__ = True
        
        id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
        created_at = Column(DateTime(timezone=True), server_default=func.now())
        updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Provide aliases for compatibility
    UUIDMixin = BaseModel
    TimestampMixin = BaseModel
    GUID = UUID

try:
    from backend.infrastructure.shared.database.session import get_db, get_async_db
except ImportError:
    # Fallback if shared session doesn't exist
    def get_db():
        """Placeholder database dependency."""
        pass
    
    async def get_async_db():
        """Placeholder async database dependency."""
        pass

# Try to import from local database modules if they exist
try:
    from .session import get_db as local_get_db, get_async_db as local_get_async_db
    if local_get_db:
        get_db = local_get_db
    if local_get_async_db:
        get_async_db = local_get_async_db
except ImportError:
    pass

try:
    from .database import engine, DATABASE_URL
except ImportError:
    # Provide defaults if database module doesn't exist
    engine = None
    DATABASE_URL = "sqlite:///./app.db"

# Add get_db_session alias for compatibility
def get_db_session():
    """Alias for get_db for compatibility."""
    return get_db()

async def get_async_db_session():
    """Alias for get_async_db for compatibility."""
    return await get_async_db()

# Add SessionManager class
class SessionManager:
    """Database session manager for handling database connections."""
    
    def __init__(self, database_url: str = None):
        self.database_url = database_url or DATABASE_URL
        self.engine = engine
    
    def get_session(self):
        """Get database session."""
        return get_db()
    
    async def get_async_session(self):
        """Get async database session."""
        return await get_async_db()

# Create db alias for get_db
db = get_db


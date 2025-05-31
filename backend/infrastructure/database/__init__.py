"""
Database utilities and session management.
"""

# Import the essential database components that exist
try:
    from backend.infrastructure.shared.database.base import Base, BaseModel, UUIDMixin, TimestampMixin, GUID
except ImportError:
    # Fallback - define Base here if shared doesn't exist
    from sqlalchemy.ext.declarative import declarative_base
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
    from backend.infrastructure.shared.database.session import get_db
except ImportError:
    # Fallback if shared session doesn't exist
    def get_db():
        """Placeholder database dependency."""
        pass

# Try to import from local database modules if they exist
try:
    from .session import get_db as local_get_db
    if local_get_db:
        get_db = local_get_db
except ImportError:
    pass

try:
    from .database import engine, DATABASE_URL
except ImportError:
    # Provide defaults if database module doesn't exist
    engine = None
    DATABASE_URL = "sqlite:///./app.db"

__all__ = [
    'Base',
    'BaseModel',
    'UUIDMixin',
    'TimestampMixin',
    'GUID',
    'get_db',
    'engine',
    'DATABASE_URL'
] 
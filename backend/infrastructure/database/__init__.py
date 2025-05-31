"""
Database utilities and session management.
"""

# Import the essential database components that exist
try:
    from backend.infrastructure.shared.database.base import Base
except ImportError:
    # Fallback - define Base here if shared doesn't exist
    from sqlalchemy.ext.declarative import declarative_base
    Base = declarative_base()

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
    'get_db',
    'engine',
    'DATABASE_URL'
] 
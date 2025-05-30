"""
Database utilities and session management.
"""

try:
    from .session import get_db_session, create_session, close_session
except ImportError:
    # Fallback database session functions
    def get_db_session():
        """Get database session - fallback implementation."""
        return None
    
    def create_session():
        """Create new database session - fallback implementation."""
        return None
    
    def close_session(session):
        """Close database session - fallback implementation."""
        pass

__all__ = ['get_db_session', 'create_session', 'close_session'] 
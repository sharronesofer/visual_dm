from backend.systems.shared.database.session import get_db_session
from backend.systems.shared.database.session import get_db_session
from backend.systems.shared.database.session import get_db_session
from backend.systems.shared.database.session import get_db_session
from backend.systems.shared.database.session import get_db_session
from backend.systems.shared.database.session import get_db_session
import pytest
from unittest.mock import MagicMock, patch, PropertyMock
import sys

from backend.systems.character.services.character_service import CharacterService

# Mock the database module since we're only testing initialization logic
sys.modules['backend.systems.shared.database.database_objects'] = MagicMock()


class TestCharacterServiceDbInit:
    """Tests for character service database session initialization."""

    def test_init_with_provided_session(self):
        """Test initialization with a provided database session."""
        mock_session = MagicMock()
        service = CharacterService(db_session=mock_session)
        assert service.db == mock_session

    @patch('backend.systems.character.services.character_service.db')
    def test_init_with_callable_session(self, mock_db):
        """Test initialization with a callable db.session."""
        # Set up mock for callable db.session
        mock_session = MagicMock()
        mock_db.session = MagicMock(return_value=mock_session)
        
        # Ensure db.session is callable
        assert callable(mock_db.session)
        
        service = CharacterService()
        assert service.db == mock_session
        mock_db.session.assert_called_once()

    @patch('backend.systems.character.services.character_service.db')
    def test_init_with_property_session(self, mock_db):
        """Test initialization with a db.session property."""
        # Set up mock for db.session property with a name that won't trigger callable detection
        mock_session = MagicMock(name="property_value")
        
        # Directly patch the property without using PropertyMock
        # Set db.session as a simple attribute
        mock_db.session = mock_session
        
        # Create the service
        service = CharacterService()
        
        # Verify the correct session was assigned
        # Use the exact same object identity check
        assert service.db is mock_session

    @patch('backend.systems.character.services.character_service.db')
    @patch('backend.systems.character.services.character_service.get_db_session')
    def test_init_with_fallback_session(self, mock_get_db, mock_db):
        """Test initialization with fallback to get_db_session."""
        # Make db.session inaccessible
        del mock_db.session
        
        # Set up mock for get_db_session
        mock_session = MagicMock()
        mock_get_db.return_value = iter([mock_session])
        
        service = CharacterService()
        assert service.db == mock_session
        mock_get_db.assert_called_once()

    @patch('backend.systems.character.services.character_service.db')
    @patch('backend.systems.character.services.character_service.get_db_session')
    def test_init_with_exception_fallback(self, mock_get_db, mock_db):
        """Test initialization with exception handling to get_db_session."""
        # Make db.session raise an exception when accessed
        type(mock_db).session = property(lambda x: exec('raise Exception("Test exception")'))
        
        # Set up mock for get_db_session
        mock_session = MagicMock()
        mock_get_db.return_value = iter([mock_session])
        
        service = CharacterService()
        assert service.db == mock_session
        mock_get_db.assert_called_once() 
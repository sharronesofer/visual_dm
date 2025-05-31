"""
Test configuration for event_base system
"""

import pytest
from unittest.mock import Mock
from sqlalchemy.orm import Session

# REMOVED: deprecated event_base import


@pytest.fixture
def mock_db_session():
    """Mock database session"""
    return Mock(spec=Session)


@pytest.fixture
def event_base_service(mock_db_session):
    """Create event_base service with mocked dependencies"""
    return Event_BaseService(mock_db_session)

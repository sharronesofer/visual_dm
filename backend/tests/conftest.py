import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Create an in-memory SQLite database for testing
@pytest.fixture(scope="session")
def test_db_engine():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    yield engine

@pytest.fixture(scope="function")
def test_db(test_db_engine):
    connection = test_db_engine.connect()
    transaction = connection.begin()
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=connection)
    
    db = TestingSessionLocal()
    
    yield db
    
    # Clean up after test
    transaction.rollback()
    connection.close()

@pytest.fixture(scope="function") 
def mock_client():
    """Mock client for tests that don't need the full FastAPI app"""
    from unittest.mock import Mock
    return Mock()

@pytest.fixture(scope="function")
def mock_db_session():
    """Mock database session for tests that don't need real database"""
    from unittest.mock import Mock
    return Mock() 
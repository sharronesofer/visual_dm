"""
Pytest configuration for Flask application tests.
"""

import os
import pytest
from flask import Flask
from app import create_app
from app.config_test import test_config
from app.core.database import db as _db

@pytest.fixture(scope='session')
def app():
    """Create a Flask app configured for testing."""
    # Create the application with test config
    app = create_app(test_config)
    
    # Create an application context
    with app.app_context():
        # Create tables
        _db.create_all()
        
        yield app
        
        # Clean up
        _db.session.remove()
        _db.drop_all()

@pytest.fixture(scope='function')
def db(app):
    """
    Get a database instance for each test function.
    This allows test isolation.
    """
    # Connect to the database
    with app.app_context():
        _db.create_all()
        
        yield _db
        
        # Clean up after test
        _db.session.rollback()
        _db.session.close()
        _db.drop_all()
        _db.create_all()

@pytest.fixture(scope='function')
def client(app):
    """Get a test client for the app."""
    with app.test_client() as client:
        yield client 
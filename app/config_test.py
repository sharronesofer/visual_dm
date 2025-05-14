"""
Testing configuration for Flask application.
This configuration is specifically for use during tests to minimize dependencies 
and prevent tests from hitting production resources.
"""

import os
from datetime import timedelta
from app.config import Config

class TestConfig(Config):
    """
    Test configuration - minimal setup with in-memory SQLite database.
    """
    TESTING = True
    DEBUG = True
    
    # Use in-memory database for testing
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Disable CSRF protection for testing
    WTF_CSRF_ENABLED = False
    
    # Authentication settings for tests
    SECRET_KEY = 'test-secret-key'
    JWT_SECRET_KEY = 'test-jwt-secret-key'
    
    # Cache settings for tests
    CACHE_TYPE = 'simple'  # Use simple in-memory cache
    
    # Disable email
    MAIL_SERVER = None
    
    # Reset required fields validation
    def __init__(self):
        """Skip validation for testing environment."""
        pass  # Skip the parent __init__ which validates env vars
        
test_config = TestConfig() 
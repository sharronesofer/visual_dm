"""
Flask extensions management module.
Handles initialization and configuration of all Flask extensions.
"""

from typing import Any
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_mail import Mail
from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import logging

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
cors = CORS()
mail = Mail()
cache = Cache()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

logger = logging.getLogger(__name__)

def init_extensions(app: Flask) -> None:
    """
    Initialize all Flask extensions with the application.
    
    Args:
        app: The Flask application instance
        
    Raises:
        RuntimeError: If extension initialization fails
    """
    try:
        # Initialize database
        logger.info("Initializing database extension...")
        db.init_app(app)
        
        # Initialize migrations
        logger.info("Initializing migrations extension...")
        migrate.init_app(app, db)
        
        # Initialize CORS
        logger.info("Initializing CORS extension...")
        cors.init_app(app, resources={
            r"/api/*": {
                "origins": app.config.get('CORS_ORIGINS', '*'),
                "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                "allow_headers": ["Content-Type", "Authorization"]
            }
        })
        
        # Initialize mail
        logger.info("Initializing mail extension...")
        mail.init_app(app)
        
        # Initialize cache
        logger.info("Initializing cache extension...")
        cache.init_app(app, config={
            'CACHE_TYPE': app.config.get('CACHE_TYPE', 'simple'),
            'CACHE_DEFAULT_TIMEOUT': app.config.get('CACHE_DEFAULT_TIMEOUT', 300)
        })
        
        # Initialize rate limiter
        logger.info("Initializing rate limiter extension...")
        limiter.init_app(app)
        
        logger.info("All extensions initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize extensions: {str(e)}")
        raise RuntimeError(f"Extension initialization failed: {str(e)}")

def get_extension(name: str) -> Any:
    """
    Get an extension instance by name.
    
    Args:
        name: The name of the extension to retrieve
        
    Returns:
        The extension instance
        
    Raises:
        ValueError: If the extension name is invalid
    """
    extensions = {
        'db': db,
        'migrate': migrate,
        'cors': cors,
        'mail': mail,
        'cache': cache,
        'limiter': limiter
    }
    
    if name not in extensions:
        raise ValueError(f"Invalid extension name: {name}")
        
    return extensions[name] 
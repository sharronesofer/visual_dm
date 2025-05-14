"""
Application factory module.
Handles application creation, configuration, and initialization.
"""

import os
import logging
from typing import Optional
from flask import Flask
from app.core.config import Config
from app.extensions import init_extensions, db
from app.core.utils.error_handlers import register_error_handlers
from app.core.utils.logging_utils import setup_logging

logger = logging.getLogger(__name__)

def create_app(config_name: Optional[str] = None) -> Flask:
    """
    Create and configure the Flask application.
    
    Args:
        config_name: The name of the configuration to use
        
    Returns:
        Flask: The configured Flask application
        
    Raises:
        RuntimeError: If application creation fails
    """
    try:
        # Create Flask application
        app = Flask(__name__)
        
        # Load configuration
        if config_name is None:
            config_name = os.getenv('FLASK_ENV', 'development')
        app.config.from_object(Config)
        
        # Setup logging
        setup_logging(app)
        logger.info(f"Application created with {config_name} configuration")
        
        # Initialize extensions
        init_extensions(app)
        
        # Register error handlers
        register_error_handlers(app)
        
        # Register blueprints
        _register_blueprints(app)
        
        # Register CLI commands
        _register_commands(app)
        
        # Setup context processors
        _setup_context_processors(app)
        
        logger.info("Application initialization completed successfully")
        return app
        
    except Exception as e:
        logger.error(f"Failed to create application: {str(e)}")
        raise RuntimeError(f"Application creation failed: {str(e)}")

def _register_blueprints(app: Flask) -> None:
    """Register all application blueprints."""
    try:
        from app.api.v1 import api_bp
        from app.auth import auth_bp
        from app.admin import admin_bp
        
        app.register_blueprint(api_bp, url_prefix='/api/v1')
        app.register_blueprint(auth_bp, url_prefix='/auth')
        app.register_blueprint(admin_bp, url_prefix='/admin')
        
        logger.info("Blueprints registered successfully")
    except Exception as e:
        logger.error(f"Failed to register blueprints: {str(e)}")
        raise

def _register_commands(app: Flask) -> None:
    """Register CLI commands."""
    try:
        from app.core.commands import init_db, seed_db, create_admin
        
        app.cli.add_command(init_db)
        app.cli.add_command(seed_db)
        app.cli.add_command(create_admin)
        
        logger.info("CLI commands registered successfully")
    except Exception as e:
        logger.error(f"Failed to register CLI commands: {str(e)}")
        raise

def _setup_context_processors(app: Flask) -> None:
    """Setup template context processors."""
    try:
        @app.context_processor
        def inject_config():
            """Inject configuration into templates."""
            return {
                'app_name': app.config.get('APP_NAME', 'Visual DM'),
                'app_version': app.config.get('APP_VERSION', '1.0.0')
            }
            
        logger.info("Context processors setup successfully")
    except Exception as e:
        logger.error(f"Failed to setup context processors: {str(e)}")
        raise 
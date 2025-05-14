"""
Visual DM application initialization.
"""

import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, current_user
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from app.config import Config
from app.core.database import db, init_db
from app.core.utils.cache import init_cache, RedisCache
from app.core.utils.db_pool import init_db_pool, ConnectionPoolManager
from app.core.utils.monitoring import PerformanceMonitor
from app.core.utils.http_cache import HTTPCache
from app.core.utils.cache_warmer import init_cache_warmer
from app.core.swagger import init_swagger
from app.core.models.user import User  # Import User model for Flask-Login
from app.core.models.character import Character
## from app.core.routes.building_routes import building_routes
## from app.core.routes.character_routes import character_routes  # Temporarily commented to unblock tests
## from app.core.routes.game_routes import game_routes
## from app.core.routes.map_routes import map_routes
## from app.core.routes.npc_routes import npc_routes
## from app.core.routes.quest_routes import quest_routes
## from app.core.routes.world_routes import world_routes
## from app.core.routes.code_routes import code_routes
from flask_socketio import SocketIO
from redis import Redis
from .extensions import db
from .utils.logging import setup_logging
from .utils.error_handlers import register_error_handlers
## from app.api.routes.version_control import version_control_bp
## from app.core.routes.auth_routes import auth_bp
## from app.core.utils.email import mail

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

socketio = SocketIO()
redis_client = None

@login_manager.user_loader
def load_user(user_id):
    """Load user by ID."""
    return User.query.get(int(user_id))

def create_app(config=None):
    """
    Create Flask application instance.
    
    Args:
        config: Configuration object or path
        
    Returns:
        Flask application instance
    """
    # Create Flask app
    app = Flask(__name__)
    
    # Load configuration
    if config is None:
        # Load default configuration
        app.config.from_object('app.config.default')
        
        # Override with instance configuration
        if app.config.get('ENV') == 'production':
            app.config.from_object('app.config.production')
        else:
            app.config.from_object('app.config.development')
    else:
        # Load custom configuration
        app.config.from_object(config)
    
    # Initialize extensions
    CORS(app)
    ## mail.init_app(app)
    init_db(app)
    
    # Register blueprints
    ## app.register_blueprint(auth_bp, url_prefix='/api/auth')
    
    return app

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Log startup
logger.info("Visual DM startup")

# Create the application instance
app = create_app()

# Make the app instance available for import
__all__ = ['app', 'create_app', 'login_manager']

if __name__ == "__main__":
    app.run()

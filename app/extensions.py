"""
Centralized Flask extensions management.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO
from flask_apscheduler import APScheduler
from typing import Optional, Dict, Any
from redis import Redis

# Initialize all Flask extensions without binding to app
db = SQLAlchemy()
migrate = Migrate()
cors = CORS()
jwt = JWTManager()
socketio = SocketIO()
scheduler = APScheduler()
redis_client = None

def init_extensions(app, config: Optional[Dict[str, Any]] = None):
    """
    Initialize all Flask extensions with the application.
    
    Args:
        app: Flask application instance
        config: Optional configuration dictionary to override app.config
    """
    # Initialize database
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Initialize security
    jwt.init_app(app)
    
    # Initialize CORS
    cors.init_app(app)
    
    # Initialize WebSocket
    socketio.init_app(app, cors_allowed_origins="*")
    
    # Initialize scheduler if not in testing mode
    if not app.config.get('TESTING', False):
        scheduler.init_app(app)
        scheduler.start()
    
    # Create database tables if they don't exist
    with app.app_context():
        db.create_all() 
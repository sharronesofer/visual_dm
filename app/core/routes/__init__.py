"""
Core routes package initialization.
"""

from flask import Blueprint
from .health import health_bp
from .global_state import global_state_bp
from .dm import dm_bp
from .regions import regions_bp
from .quest_routes import quest_bp

# Create a parent blueprint for all core routes
core_bp = Blueprint('core', __name__)

def register_routes(app):
    """Register all core route blueprints with the Flask application.
    
    Args:
        app: Flask application instance
    """
    # Register core blueprints with URL prefixes
    app.register_blueprint(health_bp, url_prefix='/api/v1')
    app.register_blueprint(global_state_bp, url_prefix='/api/v1/global_state')
    app.register_blueprint(dm_bp, url_prefix='/api/v1/dm')
    app.register_blueprint(regions_bp, url_prefix='/api/v1/regions')

    # Import and register other blueprints
    from app.combat.combat_routes import combat_bp
    from app.characters.character_routes import character_bp
    from app.world.world_routes import world_bp
    from app.social.social_routes import social_bp
    from app.npcs.npc_routes import npc_bp
    from app.arc.arc_routes import arc_bp

    # Register other blueprints with URL prefixes
    app.register_blueprint(combat_bp, url_prefix='/api/v1/combat')
    app.register_blueprint(character_bp, url_prefix='/api/v1/character')
    app.register_blueprint(world_bp, url_prefix='/api/v1/world')
    app.register_blueprint(social_bp, url_prefix='/api/v1/social')
    app.register_blueprint(quest_bp, url_prefix='/api/v1/quests')
    app.register_blueprint(npc_bp, url_prefix='/api/v1/npcs')
    app.register_blueprint(arc_bp, url_prefix='/api/v1/arc')

    # ... existing code ... 
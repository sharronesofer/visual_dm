"""
Visual DM Backend Application
"""

import logging
import sys
from typing import Dict, Any, Optional, List
from flask import Flask, jsonify, request
from app.world.world_utils import process_world_tick, cleanup_old_events
import os
from dotenv import load_dotenv
from pathlib import Path
from app.core.utils.firebase_utils import initialize_firebase
from app.core.utils.config_utils import Config, config
from app.core.utils.health_check import HealthCheck
from app.extensions import init_extensions, scheduler
from fastapi import FastAPI
from visual_client.game.world import WorldState

def create_app(config_name_or_object=None):
    """Create and configure the Flask application.
    
    Args:
        config_name_or_object: Can be one of:
            - String naming a config object ('development', 'testing', 'production')
            - The actual config object
            - Dictionary with config values
    """
    app = Flask(__name__)
    
    # Load configuration
    if config_name_or_object is None:
        config_name_or_object = os.getenv('FLASK_ENV', 'development')
        
    if isinstance(config_name_or_object, dict):
        app.config.update(config_name_or_object)
    elif isinstance(config_name_or_object, str):
        app.config.from_object(config[config_name_or_object])
    else:
        app.config.from_object(config_name_or_object or config['default'])
    
    # Set database URI
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///visual_dm.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize all extensions
    init_extensions(app)
    
    # Initialize Firebase
    initialize_firebase(testing=app.config.get('TESTING', False))
    
    # Initialize health check
    health_check = HealthCheck(app)
    
    # Register blueprints
    from app.characters.character_routes import character_bp
    from app.combat.combat_routes import combat_bp
    from app.inventory.inventory_routes import inventory_bp
    from app.social.faction_routes import faction_bp
    from app.npcs.npc_routes import npc_bp
    from app.quests.quest_routes import quest_bp
    from app.world.world_routes import world_bp
    from app.core.services.ai import ai_bp
    from app.core.services.firebase import firebase_bp
    from app.core.routes.automation_routes import automation_bp
    
    app.register_blueprint(character_bp, url_prefix='/api/v1/characters')
    app.register_blueprint(combat_bp, url_prefix='/api/v1/combat')
    app.register_blueprint(inventory_bp, url_prefix='/api/v1/inventory')
    app.register_blueprint(faction_bp, url_prefix='/api/v1/factions')
    app.register_blueprint(npc_bp, url_prefix='/api/v1/npcs')
    app.register_blueprint(quest_bp, url_prefix='/api/v1/quests')
    app.register_blueprint(world_bp, url_prefix='/api/v1/world')
    app.register_blueprint(ai_bp, url_prefix='/api/v1/ai')
    app.register_blueprint(firebase_bp, url_prefix='/api/v1/firebase')
    app.register_blueprint(automation_bp, url_prefix='/api/v1/automation')
    
    # Add scheduled jobs if not testing
    if not app.config.get('TESTING', False):
        scheduler.add_job(
            process_world_tick,
            trigger="cron",
            hour=0,
            minute=5,
            id='world_tick'
        )
        scheduler.add_job(
            cleanup_old_events,
            trigger="cron",
            hour=0,
            minute=10,
            id='cleanup_events'
        )
    
    @app.route('/health', methods=['GET'])
    def health_check():
        """Health check endpoint."""
        return jsonify(health_check.run_checks())
    
    return app

# Create the application instance
app = create_app('development')

# === Run App ===
if __name__ == "__main__":
    try:
        app.run(debug=True, port=5050)
    except Exception as e:
        logging.error(f"Failed to start application: {str(e)}")
        sys.exit(1)

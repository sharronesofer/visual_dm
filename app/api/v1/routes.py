"""
API v1 routes.
"""

from flask import jsonify
from app.api.v1 import api_bp
from fastapi import APIRouter
from app.api.routes import cleanup
from app.auth.auth_routes import auth_bp
from app.api.world_routes import world_bp
from app.api.npc_routes import npc_bp
from app.api.quest_routes import quest_bp
from app.api.location_routes import location_bp
from app.api.combat_routes import combat_bp
from app.api.item_routes import item_bp

@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'ok',
        'message': 'API is running'
    })

router = APIRouter()

# Include cleanup routes
router.include_router(
    cleanup.router,
    prefix="/cleanup",
    tags=["cleanup"]
)

api_bp.register_blueprint(auth_bp, url_prefix='/auth')
api_bp.register_blueprint(world_bp, url_prefix='')
api_bp.register_blueprint(npc_bp, url_prefix='')
api_bp.register_blueprint(quest_bp, url_prefix='')
api_bp.register_blueprint(location_bp, url_prefix='')
api_bp.register_blueprint(combat_bp, url_prefix='')
api_bp.register_blueprint(item_bp, url_prefix='') 
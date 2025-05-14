"""
API initialization and blueprint registration.
"""

from flask import Blueprint
from app.api.routes import npc_version

# Create API blueprint
api = Blueprint('api', __name__)

# Register route blueprints
api.register_blueprint(npc_version.bp, url_prefix='/api/v1')

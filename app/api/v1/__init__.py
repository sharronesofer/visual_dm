"""
API v1 blueprint.
"""

from flask import Blueprint

api_bp = Blueprint('api_v1', __name__)

# Import routes after blueprint creation to avoid circular imports
from app.api.v1 import routes 
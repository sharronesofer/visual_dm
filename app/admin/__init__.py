"""
Admin blueprint.
"""

from flask import Blueprint

admin_bp = Blueprint('admin', __name__)

# Import routes after blueprint creation to avoid circular imports
from app.admin import routes 
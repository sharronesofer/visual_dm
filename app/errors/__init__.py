"""
Error handling blueprint.
"""

from flask import Blueprint

bp = Blueprint('errors', __name__)

from app.errors import handlers  # Import handlers after creating blueprint to avoid circular imports 
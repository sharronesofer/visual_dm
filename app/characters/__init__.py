"""
Characters blueprint initialization.
"""

from flask import Blueprint

character_bp = Blueprint('characters', __name__)

from . import character_routes
from . import character_builder_class

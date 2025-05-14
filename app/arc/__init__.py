"""
Arc module for managing character story arcs.
"""

from flask import Blueprint

arc_bp = Blueprint('arc', __name__)

from . import arc_routes 
from flask import Blueprint

social_bp = Blueprint('social', __name__)

from . import social_routes 
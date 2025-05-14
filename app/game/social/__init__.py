"""Social module for handling character interactions and relationships."""

from flask import Blueprint

social_bp = Blueprint('social', __name__)

from . import routes  # noqa 
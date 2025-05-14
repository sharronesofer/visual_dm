from flask import Blueprint

combat_bp = Blueprint('combat', __name__)

from . import combat_routes
from . import combat_utils

from flask import Blueprint

item_bp = Blueprint('item', __name__)

# Optionally import routes if they exist
try:
    from . import item_routes
except ImportError:
    pass 
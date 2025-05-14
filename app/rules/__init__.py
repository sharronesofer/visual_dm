from flask import Blueprint

rule_bp = Blueprint('rule', __name__)

# Optionally import routes if they exist
try:
    from . import rules_routes
except ImportError:
    pass

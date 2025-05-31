# This file is intentionally left empty to make the directory a proper Python package 

from backend.infrastructure.auth.auth_user.routers import bp as auth_bp
from backend.infrastructure.auth.auth_user.models import bp as user_bp

def register_endpoints(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp) 
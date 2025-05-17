from flask import Flask
from flask_cors import CORS
from .world import world_bp
from backend.app.api.v1.api import init_api
from backend.app.middleware.cors import setup_cors

def create_app():
    app = Flask(__name__)
    CORS(app)
    
    # Register blueprints
    app.register_blueprint(world_bp, url_prefix='/api/v1/world')
    
    setup_cors(app)
    
    init_api(app)
    
    return app 
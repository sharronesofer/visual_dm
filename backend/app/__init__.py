from flask import Flask
from flask_cors import CORS
from .world import world_bp

def create_app():
    app = Flask(__name__)
    CORS(app)
    
    # Register blueprints
    app.register_blueprint(world_bp, url_prefix='/api/v1/world')
    
    return app 
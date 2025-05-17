from flask_cors import CORS

def setup_cors(app):
    # Allow all origins for development; restrict in production
    CORS(app, resources={r"/api/*": {"origins": "*"}}) 
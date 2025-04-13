from flask import Blueprint
from app.characters.character_routes import character_bp

player_bp = Blueprint("player", __name__)
player_bp.register_blueprint(character_bp)
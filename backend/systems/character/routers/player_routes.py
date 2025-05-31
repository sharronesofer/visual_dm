
#This file serves purely as a blueprint aggregator, re-registering character_bp under a broader player_bp namespace. It doesn’t define its own routes or perform any logic.

from fastapi import APIRouter as APIRouter
from backend.systems.character.character_routes import character_bp

player_bp = Blueprint("player", __name__)
player_bp.register_blueprint(character_bp)


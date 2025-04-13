from flask import Blueprint
from app.npc.npc_rumor_routes import rumor_bp
from app.npc.npc_relationships_routes import npc_relationship_bp
from app.npc.npc_character_routes import npc_bp  # this is a sub-blueprint

npc_routes_bp = Blueprint("npc_routes", __name__)

npc_routes_bp.register_blueprint(rumor_bp)
npc_routes_bp.register_blueprint(npc_relationship_bp)
npc_routes_bp.register_blueprint(npc_bp)

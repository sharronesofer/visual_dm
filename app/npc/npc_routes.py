from flask import Blueprint
from app.npc.npc_loyalty_routes import loyalty_bp
from app.npc.npc_rumor_routes import rumor_bp
from app.npc.npc_relationships_routes import relationship_bp
from app.npc.npc_character_routes import npc_char_bp

npc_bp = Blueprint("npc", __name__)

npc_bp.register_blueprint(loyalty_bp)
npc_bp.register_blueprint(rumor_bp)
npc_bp.register_blueprint(relationship_bp)
npc_bp.register_blueprint(npc_char_bp)

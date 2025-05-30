#This module acts as a master blueprint aggregator, bundling:
#rumor_bp – NPC rumor spread/response
#npc_relationship_bp – party recruitment, motif tick, loyalty shifts
#npc_bp – CRUD and core state access
#It is a structural entry point for Flask-based modular routing of the NPC system.

from flask import Blueprint
from app.npc.npc_rumor_routes import rumor_bp
from app.npc.npc_relationships_routes import npc_relationship_bp
from app.npc.npc_character_routes import npc_bp  # this is a sub-blueprint

npc_routes_bp = Blueprint("npc_routes", __name__)

npc_routes_bp.register_blueprint(rumor_bp)
npc_routes_bp.register_blueprint(npc_relationship_bp)
npc_routes_bp.register_blueprint(npc_bp)


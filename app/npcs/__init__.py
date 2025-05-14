from flask import Blueprint

npc_bp = Blueprint('npc', __name__)

from . import npc_routes 
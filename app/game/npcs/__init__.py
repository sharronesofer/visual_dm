"""NPC module for handling non-player character interactions and management."""

from flask import Blueprint

npc_bp = Blueprint('npcs', __name__)

from . import routes  # noqa 
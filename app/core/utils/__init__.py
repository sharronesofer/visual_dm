"""
Core utilities for the application.
"""

from app.core.utils.firebase_utils import (
    initialize_firebase,
    get_firestore_client,
    get_firebase_db,
    get_firebase_auth,
    get_firebase_storage,
    get_firebase_app
)

from app.core.utils.json_utils import load_json, save_json

from app.core.utils.gpt.client import GPTClient
from app.core.utils.gpt.flavor import gpt_flavor_identify_effect, gpt_flavor_reveal_full_item
from app.core.utils.gpt.utils import get_goodwill_label, log_usage

from app.core.utils.start_game_routes import start_game_bp
# from app.core.utils.world_tick_utils import tick_world_day  # Temporarily commented for Alembic migration

__all__ = [
    'initialize_firebase',
    'get_firestore_client',
    'get_firebase_db',
    'get_firebase_auth',
    'get_firebase_storage',
    'get_firebase_app',
    'load_json',
    'save_json',
    'GPTClient',
    'gpt_flavor_identify_effect',
    'gpt_flavor_reveal_full_item',
    'get_goodwill_label',
    'log_usage',
    'start_game_bp',
    'tick_world_day'
]

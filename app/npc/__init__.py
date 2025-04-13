from .npc_builder_class import NPCBuilder
from app.npc.npc_loyalty_utils import (
    build_npc_from_input,
    save_npc_to_firebase,
    load_npc_from_firebase
)

from .npc_loyalty_utils import (
    apply_loyalty_event,
    apply_qualifying_event,
)

from app.npc.npc_loyalty_utils import LoyaltyManager

from .npc_loyalty_routes import loyalty_bp
# If you later make a top-level npc_routes.py:
# from .npc_routes import npc_bp

__all__ = [
    "NPCBuilder",
    "build_npc_from_input",
    "save_npc_to_firebase",
    "load_npc_from_firebase",
    "apply_loyalty_event",
    "apply_qualifying_event",
    "LoyaltyManager",
    "loyalty_bp"
]

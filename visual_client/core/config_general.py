# visual_client/core/config_general.py

# Global attribute list (used in multiple systems)
ATTRIBUTES = ["STR", "DEX", "CON", "INT", "WIS", "CHA"]

# Default screen dimensions
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FONT_SIZE = 24

# Backend server URL (can be overridden for deployment)
SERVER_URL = "http://localhost:5050"

# Color palette (standardized RGB values for UI)
COLORS = {
    "text": (255, 255, 255),
    "highlight": (255, 255, 0),
    "background": (30, 30, 60),
    "secondary": (180, 180, 200),
    "good": (0, 255, 0),
    "warning": (255, 180, 0),
    "error": (255, 60, 60),
    "accent": (180, 255, 200),
    "accent2": (180, 180, 255)
}

# Default tile and visual marker for new characters
DEFAULT_TILE = "0_0"

# System phase tag (useful for debugging and modular feature flags)
SYSTEM_PHASE = "0.5"

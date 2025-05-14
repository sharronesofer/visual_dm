"""
Asset management for the Visual DM game client.
"""

from pathlib import Path

# Asset paths
BASE_DIR = Path(__file__).resolve().parent
TILES_DIR = BASE_DIR / "tiles"
FONTS_DIR = BASE_DIR / "fonts"

__all__ = ['TILES_DIR', 'FONTS_DIR'] 
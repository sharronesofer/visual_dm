"""
Event system utility components.

This package contains utility classes and functions to assist with
event handling, management, and integration throughout the system.
"""

from .terrain_manager import TerrainManager
from .tile_loader import TileLoader
from .rules_loader import RulesLoader
from .error_utils import ScreenError, handle_error
from .screen_utils import ScreenManager
from .input_utils import InputHandler
from .render_utils import Renderer
from .asset_utils import AssetManager
from .coordinates import GlobalCoord, LocalCoord, CoordinateSystem, coordinate_system
from .floating_origin import FloatingOrigin, floating_origin
from . import coordinate_utils
from . import coordinate_validation
from .manager import EventManager
from .batching import (
    EventBatch, 
    EventBatcher, 
    register_batch, 
    add_event, 
    start_batching, 
    stop_batching
)
from .plugins import (
    EventPlugin,
    PluginManager,
    register_plugin,
    enable_plugin,
    disable_plugin,
    load_plugins
)

__all__ = [
    'TerrainManager',
    'TileLoader',
    'RulesLoader',
    'ScreenError',
    'handle_error',
    'ScreenManager',
    'InputHandler',
    'Renderer',
    'AssetManager',
    'GlobalCoord',
    'LocalCoord',
    'CoordinateSystem',
    'coordinate_system',
    'FloatingOrigin',
    'floating_origin',
    'coordinate_utils',
    'coordinate_validation',
    'EventManager',
    'EventBatch',
    'EventBatcher',
    'register_batch',
    'add_event',
    'start_batching',
    'stop_batching',
    'EventPlugin',
    'PluginManager',
    'register_plugin',
    'enable_plugin',
    'disable_plugin',
    'load_plugins'
] 
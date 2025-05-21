"""
Event Plugin System
------------------
Provides support for modular event handling through a plugin architecture.

This system enables extension of the event system through pluggable modules
that can register custom event types, handlers, and middleware. Plugins
are loaded dynamically and can be enabled/disabled at runtime.
"""

import asyncio
import importlib
import inspect
import json
import logging
import os
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Type, Union

from ..base import EventBase
from ..dispatcher import EventDispatcher

logger = logging.getLogger(__name__)

class EventPlugin:
    """
    Base class for event system plugins.
    
    Plugins provide a way to extend the event system with custom
    event handlers, middleware, and event types. They can be
    enabled/disabled at runtime.
    """
    
    def __init__(self, name: str, description: str = ""):
        """
        Initialize a new event plugin.
        
        Args:
            name: Unique plugin identifier
            description: Human-readable description
        """
        self.name = name
        self.description = description
        self.enabled = False
        self.version = "1.0.0"
        self.dependencies = []
        self._subscriptions = []
        self._middleware = []
        self._dispatcher = None
    
    async def initialize(self, dispatcher: EventDispatcher) -> bool:
        """
        Initialize the plugin with the event dispatcher.
        
        This is called when the plugin is first registered.
        Override to customize initialization.
        
        Args:
            dispatcher: The event dispatcher instance
            
        Returns:
            bool: True if initialization was successful
        """
        self._dispatcher = dispatcher
        return True
    
    async def enable(self) -> bool:
        """
        Enable the plugin, registering all handlers and middleware.
        
        Override to customize enabling behavior.
        
        Returns:
            bool: True if successfully enabled
        """
        if self.enabled:
            return True
            
        if not self._dispatcher:
            logger.error(f"Plugin {self.name} not initialized")
            return False
        
        try:
            # Register handlers
            for event_type, handler, priority in self._subscriptions:
                self._dispatcher.subscribe(event_type, handler, priority)
            
            # Register middleware
            for middleware in self._middleware:
                self._dispatcher.add_middleware(middleware)
                
            self.enabled = True
            logger.info(f"Plugin {self.name} enabled")
            return True
        except Exception as e:
            logger.error(f"Error enabling plugin {self.name}: {e}")
            return False
    
    async def disable(self) -> bool:
        """
        Disable the plugin, unregistering all handlers and middleware.
        
        Override to customize disabling behavior.
        
        Returns:
            bool: True if successfully disabled
        """
        if not self.enabled:
            return True
            
        if not self._dispatcher:
            logger.error(f"Plugin {self.name} not initialized")
            return False
        
        try:
            # Unregister handlers
            for event_type, handler, _ in self._subscriptions:
                self._dispatcher.unsubscribe(event_type, handler)
            
            # Middleware can't be unregistered in current architecture
            # This would require dispatcher changes
            
            self.enabled = False
            logger.info(f"Plugin {self.name} disabled")
            return True
        except Exception as e:
            logger.error(f"Error disabling plugin {self.name}: {e}")
            return False
    
    def register_handler(self, 
                       event_type: Type[EventBase], 
                       handler: Callable, 
                       priority: int = 0) -> None:
        """
        Register an event handler to be enabled/disabled with the plugin.
        
        Args:
            event_type: Type of events to handle
            handler: Function to handle events
            priority: Handler priority (higher executes first)
        """
        self._subscriptions.append((event_type, handler, priority))
        
        # If already enabled, register immediately
        if self.enabled and self._dispatcher:
            self._dispatcher.subscribe(event_type, handler, priority)
    
    def register_middleware(self, middleware: Any) -> None:
        """
        Register middleware to be enabled/disabled with the plugin.
        
        Args:
            middleware: Middleware instance to register
        """
        self._middleware.append(middleware)
        
        # If already enabled, register immediately
        if self.enabled and self._dispatcher:
            self._dispatcher.add_middleware(middleware)
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        Get plugin metadata.
        
        Returns:
            Dict with plugin information
        """
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "enabled": self.enabled,
            "dependencies": self.dependencies,
            "handlers": [
                {
                    "event_type": event_type.__name__,
                    "handler": handler.__name__,
                    "priority": priority
                }
                for event_type, handler, priority in self._subscriptions
            ],
            "middleware": [str(middleware) for middleware in self._middleware]
        }


class PluginManager:
    """
    Manages loading, enabling, and disabling event plugins.
    
    This singleton class provides a central registry for all event
    plugins and handles their lifecycle management.
    """
    
    _instance = None
    
    @classmethod
    def get_instance(cls) -> 'PluginManager':
        """Get the singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def __init__(self):
        """Initialize the plugin manager."""
        if PluginManager._instance is not None:
            raise RuntimeError("PluginManager is a singleton. Use get_instance() instead.")
            
        self._plugins: Dict[str, EventPlugin] = {}
        self._config_dir = os.environ.get('EVENT_PLUGINS_CONFIG', 'config/plugins')
        self._dispatcher = EventDispatcher.get_instance()
        
        # Ensure config directory exists
        Path(self._config_dir).mkdir(parents=True, exist_ok=True)
        
        logger.info("Plugin manager initialized")
    
    async def register_plugin(self, plugin: EventPlugin) -> bool:
        """
        Register a new plugin with the system.
        
        Args:
            plugin: The plugin to register
            
        Returns:
            bool: True if registration was successful
        """
        if plugin.name in self._plugins:
            logger.warning(f"Plugin {plugin.name} already registered")
            return False
        
        try:
            if await plugin.initialize(self._dispatcher):
                self._plugins[plugin.name] = plugin
                logger.info(f"Plugin {plugin.name} registered")
                
                # Check if plugin should be auto-enabled
                config = self._load_plugin_config(plugin.name)
                if config.get('auto_enable', False):
                    await self.enable_plugin(plugin.name)
                
                return True
            else:
                logger.error(f"Failed to initialize plugin {plugin.name}")
                return False
        except Exception as e:
            logger.error(f"Error registering plugin {plugin.name}: {e}")
            return False
    
    async def unregister_plugin(self, plugin_name: str) -> bool:
        """
        Unregister a plugin from the system.
        
        Args:
            plugin_name: Name of plugin to unregister
            
        Returns:
            bool: True if unregistration was successful
        """
        if plugin_name not in self._plugins:
            logger.warning(f"Plugin {plugin_name} not registered")
            return False
        
        plugin = self._plugins[plugin_name]
        try:
            # Disable if currently enabled
            if plugin.enabled:
                await plugin.disable()
            
            del self._plugins[plugin_name]
            logger.info(f"Plugin {plugin_name} unregistered")
            return True
        except Exception as e:
            logger.error(f"Error unregistering plugin {plugin_name}: {e}")
            return False
    
    async def enable_plugin(self, plugin_name: str) -> bool:
        """
        Enable a registered plugin.
        
        Args:
            plugin_name: Name of plugin to enable
            
        Returns:
            bool: True if successfully enabled
        """
        if plugin_name not in self._plugins:
            logger.warning(f"Plugin {plugin_name} not registered")
            return False
        
        plugin = self._plugins[plugin_name]
        if plugin.enabled:
            return True
        
        # Check and enable dependencies first
        for dependency in plugin.dependencies:
            if dependency not in self._plugins:
                logger.error(f"Plugin {plugin_name} depends on {dependency}, which is not registered")
                return False
            
            dep_plugin = self._plugins[dependency]
            if not dep_plugin.enabled:
                if not await self.enable_plugin(dependency):
                    logger.error(f"Failed to enable dependency {dependency} for plugin {plugin_name}")
                    return False
        
        # Enable the plugin
        success = await plugin.enable()
        if success:
            # Update config
            config = self._load_plugin_config(plugin_name)
            config['enabled'] = True
            self._save_plugin_config(plugin_name, config)
        
        return success
    
    async def disable_plugin(self, plugin_name: str) -> bool:
        """
        Disable a registered plugin.
        
        Args:
            plugin_name: Name of plugin to disable
            
        Returns:
            bool: True if successfully disabled
        """
        if plugin_name not in self._plugins:
            logger.warning(f"Plugin {plugin_name} not registered")
            return False
        
        plugin = self._plugins[plugin_name]
        if not plugin.enabled:
            return True
        
        # Check for dependent plugins that need to be disabled first
        for other_name, other_plugin in self._plugins.items():
            if other_plugin.enabled and plugin_name in other_plugin.dependencies:
                await self.disable_plugin(other_name)
        
        # Disable the plugin
        success = await plugin.disable()
        if success:
            # Update config
            config = self._load_plugin_config(plugin_name)
            config['enabled'] = False
            self._save_plugin_config(plugin_name, config)
        
        return success
    
    async def load_plugins_from_directory(self, 
                                         directory: str, 
                                         auto_enable: bool = False) -> List[str]:
        """
        Load all plugins from a directory.
        
        Args:
            directory: Directory containing plugin modules
            auto_enable: Whether to enable plugins after loading
            
        Returns:
            List of successfully loaded plugin names
        """
        loaded_plugins = []
        
        try:
            # Ensure directory exists
            plugin_dir = Path(directory)
            if not plugin_dir.exists() or not plugin_dir.is_dir():
                logger.error(f"Plugin directory {directory} not found")
                return loaded_plugins
            
            # Add to Python path if needed
            if directory not in os.sys.path:
                os.sys.path.append(directory)
            
            # Find all potential plugin modules
            for item in plugin_dir.iterdir():
                if item.is_file() and item.name.endswith('.py') and not item.name.startswith('_'):
                    module_name = item.stem
                    try:
                        # Import the module
                        module = importlib.import_module(module_name)
                        
                        # Find plugin classes
                        for attr_name in dir(module):
                            attr = getattr(module, attr_name)
                            if (inspect.isclass(attr) and 
                                issubclass(attr, EventPlugin) and 
                                attr is not EventPlugin):
                                
                                # Instantiate the plugin
                                plugin = attr()
                                if await self.register_plugin(plugin):
                                    loaded_plugins.append(plugin.name)
                                    
                                    # Enable if requested
                                    if auto_enable:
                                        await self.enable_plugin(plugin.name)
                    except Exception as e:
                        logger.error(f"Error loading plugin from {module_name}: {e}")
        
        except Exception as e:
            logger.error(f"Error loading plugins from directory {directory}: {e}")
        
        return loaded_plugins
    
    def get_plugin(self, plugin_name: str) -> Optional[EventPlugin]:
        """
        Get a plugin by name.
        
        Args:
            plugin_name: Name of plugin to get
            
        Returns:
            EventPlugin or None if not found
        """
        return self._plugins.get(plugin_name)
    
    def get_all_plugins(self) -> Dict[str, EventPlugin]:
        """
        Get all registered plugins.
        
        Returns:
            Dict mapping plugin names to plugin instances
        """
        return self._plugins.copy()
    
    def get_enabled_plugins(self) -> Dict[str, EventPlugin]:
        """
        Get all enabled plugins.
        
        Returns:
            Dict mapping plugin names to plugin instances
        """
        return {name: plugin for name, plugin in self._plugins.items() if plugin.enabled}
    
    def _load_plugin_config(self, plugin_name: str) -> Dict[str, Any]:
        """
        Load plugin configuration.
        
        Args:
            plugin_name: Name of the plugin
            
        Returns:
            Dict with plugin configuration
        """
        config_path = Path(self._config_dir) / f"{plugin_name}.json"
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading config for plugin {plugin_name}: {e}")
        
        # Default config
        return {
            "enabled": False,
            "auto_enable": False
        }
    
    def _save_plugin_config(self, plugin_name: str, config: Dict[str, Any]) -> bool:
        """
        Save plugin configuration.
        
        Args:
            plugin_name: Name of the plugin
            config: Configuration dict
            
        Returns:
            bool: True if successfully saved
        """
        try:
            config_path = Path(self._config_dir) / f"{plugin_name}.json"
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error saving config for plugin {plugin_name}: {e}")
            return False


# Example plugin implementation
class ExamplePlugin(EventPlugin):
    """Example plugin demonstrating the plugin system."""
    
    def __init__(self):
        """Initialize the example plugin."""
        super().__init__(
            name="example_plugin",
            description="Example plugin demonstrating the event plugin system"
        )
        self.version = "1.0.0"
    
    async def initialize(self, dispatcher: EventDispatcher) -> bool:
        """Initialize plugin and register handlers."""
        await super().initialize(dispatcher)
        
        # Register handlers (will be enabled when plugin is enabled)
        from ..event_types import UserLoggedInEvent
        self.register_handler(UserLoggedInEvent, self.handle_user_login)
        
        return True
    
    async def handle_user_login(self, event: Any) -> None:
        """Example event handler."""
        logger.info(f"Example plugin: User logged in - {event}")


# Convenience functions to work with the singleton

async def register_plugin(plugin: EventPlugin) -> bool:
    """
    Register a plugin with the system.
    
    Args:
        plugin: Plugin to register
        
    Returns:
        bool: True if successful
    """
    manager = PluginManager.get_instance()
    return await manager.register_plugin(plugin)

async def enable_plugin(plugin_name: str) -> bool:
    """
    Enable a registered plugin.
    
    Args:
        plugin_name: Name of plugin to enable
        
    Returns:
        bool: True if successful
    """
    manager = PluginManager.get_instance()
    return await manager.enable_plugin(plugin_name)

async def disable_plugin(plugin_name: str) -> bool:
    """
    Disable a registered plugin.
    
    Args:
        plugin_name: Name of plugin to disable
        
    Returns:
        bool: True if successful
    """
    manager = PluginManager.get_instance()
    return await manager.disable_plugin(plugin_name)

async def load_plugins(directory: str, auto_enable: bool = False) -> List[str]:
    """
    Load plugins from a directory.
    
    Args:
        directory: Directory containing plugin modules
        auto_enable: Whether to enable plugins after loading
        
    Returns:
        List of loaded plugin names
    """
    manager = PluginManager.get_instance()
    return await manager.load_plugins_from_directory(directory, auto_enable) 
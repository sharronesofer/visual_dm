"""
Event Plugin System API
----------------------
FastAPI router for managing event system plugins through REST endpoints.

This module provides a REST API for listing, enabling, disabling, and loading
event plugins, allowing remote management of the plugin system.
"""

import os
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks

from ..utils.plugins import PluginManager, EventPlugin

router = APIRouter(prefix="/api/events/plugins", tags=["event_plugins"])

@router.get("/", response_model=List[Dict[str, Any]])
async def list_plugins():
    """
    List all registered plugins and their status.
    
    Returns:
        List of plugin metadata dictionaries
    """
    plugin_manager = PluginManager.get_instance()
    plugins = plugin_manager.get_all_plugins()
    
    # Convert to list of metadata dictionaries
    return [plugin.get_metadata() for plugin in plugins.values()]

@router.get("/{plugin_name}", response_model=Dict[str, Any])
async def get_plugin(plugin_name: str):
    """
    Get detailed information about a specific plugin.
    
    Args:
        plugin_name: Name of the plugin to retrieve
        
    Returns:
        Plugin metadata dictionary
        
    Raises:
        HTTPException: If plugin not found (404)
    """
    plugin_manager = PluginManager.get_instance()
    plugin = plugin_manager.get_plugin(plugin_name)
    
    if not plugin:
        raise HTTPException(status_code=404, detail=f"Plugin '{plugin_name}' not found")
    
    return plugin.get_metadata()

@router.post("/{plugin_name}/enable", response_model=Dict[str, Any])
async def enable_plugin_endpoint(plugin_name: str):
    """
    Enable a plugin.
    
    Args:
        plugin_name: Name of the plugin to enable
        
    Returns:
        Updated plugin metadata
        
    Raises:
        HTTPException: If plugin not found (404) or cannot be enabled (400)
    """
    plugin_manager = PluginManager.get_instance()
    plugin = plugin_manager.get_plugin(plugin_name)
    
    if not plugin:
        raise HTTPException(status_code=404, detail=f"Plugin '{plugin_name}' not found")
    
    success = await plugin_manager.enable_plugin(plugin_name)
    if not success:
        raise HTTPException(status_code=400, detail=f"Failed to enable plugin '{plugin_name}'")
    
    return plugin.get_metadata()

@router.post("/{plugin_name}/disable", response_model=Dict[str, Any])
async def disable_plugin_endpoint(plugin_name: str):
    """
    Disable a plugin.
    
    Args:
        plugin_name: Name of the plugin to disable
        
    Returns:
        Updated plugin metadata
        
    Raises:
        HTTPException: If plugin not found (404) or cannot be disabled (400)
    """
    plugin_manager = PluginManager.get_instance()
    plugin = plugin_manager.get_plugin(plugin_name)
    
    if not plugin:
        raise HTTPException(status_code=404, detail=f"Plugin '{plugin_name}' not found")
    
    success = await plugin_manager.disable_plugin(plugin_name)
    if not success:
        raise HTTPException(status_code=400, detail=f"Failed to disable plugin '{plugin_name}'")
    
    return plugin.get_metadata()

@router.post("/load", response_model=List[str])
async def load_plugins_endpoint(directory: str, auto_enable: bool = False, background_tasks: BackgroundTasks = None):
    """
    Load plugins from a directory.
    
    Args:
        directory: Path to directory containing plugin modules
        auto_enable: Whether to enable loaded plugins automatically
        background_tasks: FastAPI background tasks object
        
    Returns:
        List of loaded plugin names
        
    Raises:
        HTTPException: If directory not found (404)
    """
    if not os.path.exists(directory) or not os.path.isdir(directory):
        raise HTTPException(status_code=404, detail=f"Plugin directory '{directory}' not found")
    
    plugin_manager = PluginManager.get_instance()
    
    # Load plugins in the background if background_tasks is provided
    if background_tasks:
        # Create a temporary function for the background task
        async def load_plugins_background():
            await plugin_manager.load_plugins_from_directory(directory, auto_enable)
        
        background_tasks.add_task(load_plugins_background)
        return ["Loading plugins in background..."]
    else:
        # Load plugins synchronously
        loaded_plugins = await plugin_manager.load_plugins_from_directory(directory, auto_enable)
        return loaded_plugins

@router.get("/enabled", response_model=List[Dict[str, Any]])
async def list_enabled_plugins():
    """
    List all currently enabled plugins.
    
    Returns:
        List of plugin metadata dictionaries for enabled plugins
    """
    plugin_manager = PluginManager.get_instance()
    plugins = plugin_manager.get_enabled_plugins()
    
    # Convert to list of metadata dictionaries
    return [plugin.get_metadata() for plugin in plugins.values()]

@router.post("/{plugin_name}/auto_enable", response_model=Dict[str, Any])
async def set_auto_enable(plugin_name: str, auto_enable: bool = True):
    """
    Set whether a plugin should be automatically enabled on startup.
    
    Args:
        plugin_name: Name of the plugin
        auto_enable: Whether to auto-enable the plugin
        
    Returns:
        Updated plugin configuration
        
    Raises:
        HTTPException: If plugin not found (404)
    """
    plugin_manager = PluginManager.get_instance()
    plugin = plugin_manager.get_plugin(plugin_name)
    
    if not plugin:
        raise HTTPException(status_code=404, detail=f"Plugin '{plugin_name}' not found")
    
    # Load existing config
    config = plugin_manager._load_plugin_config(plugin_name)
    
    # Update auto_enable setting
    config['auto_enable'] = auto_enable
    plugin_manager._save_plugin_config(plugin_name, config)
    
    return {
        "name": plugin_name,
        "auto_enable": auto_enable,
        "enabled": plugin.enabled,
        "config": config
    } 
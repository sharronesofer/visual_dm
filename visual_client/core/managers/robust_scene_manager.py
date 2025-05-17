"""
Robust Scene Manager with comprehensive error handling.

This module provides an enhanced Scene Manager implementation that incorporates
robust error handling for failed scene loads, missing assets, and interrupted
transitions to ensure reliable play-testing experiences.
"""

import logging
import traceback
from typing import Any, Dict, List, Optional, Tuple, Union, Set, Callable
import pygame

# Import the base scene manager
try:
    from .scene_manager import SceneManager as BaseSceneManager
except ImportError:
    # Fallback if the module structure is different
    from visual_client.core.managers.scene_manager import SceneManager as BaseSceneManager

# Import our error handling extensions
from .scene_manager_extensions import SceneManagerErrorHandling
from .scene_error_handler import SceneErrorType, SceneErrorHandler
from .error_handler import ErrorSeverity, handle_component_error

logger = logging.getLogger(__name__)

class RobustSceneManager(SceneManagerErrorHandling, BaseSceneManager):
    """
    Enhanced Scene Manager with comprehensive error handling capabilities.
    
    This implementation extends the base SceneManager with robust error handling
    for three critical failure scenarios:
    1. Failed scene loads
    2. Missing assets
    3. Interrupted transitions
    """
    
    def __init__(self, 
                 default_scene: str = "loading",
                 max_retries: int = 3,
                 transition_timeout: int = 10000,
                 *args, **kwargs):
        """
        Initialize the robust scene manager.
        
        Args:
            default_scene: Scene to fall back to when loading fails
            max_retries: Maximum retry attempts for scene loading operations
            transition_timeout: Timeout for scene transitions in milliseconds
            *args, **kwargs: Arguments to pass to the base SceneManager
        """
        # Set instance attributes for error handling parameters
        self.default_scene = default_scene
        self.max_retries = max_retries
        self.transition_timeout = transition_timeout
        # Pass our error handling parameters to the error handling mixin
        error_handling_kwargs = {
            'default_scene': default_scene,
            'max_retries': max_retries,
            'transition_timeout': transition_timeout
        }
        kwargs.update(error_handling_kwargs)
        
        # Remove error-handling-specific keys before calling SceneManager
        for key in ['default_scene', 'max_retries', 'transition_timeout']:
            kwargs.pop(key, None)
        
        # Initialize both parent classes
        super().__init__(*args, **kwargs)
        
        # Track dependencies between scenes and assets
        self.scene_asset_dependencies: Dict[str, Set[str]] = {}
        
        # Create a scene validation cache for performance
        self.scene_validation_cache: Dict[str, Dict[str, bool]] = {}
        
        self.scene_loader_manager = None  # type: Optional[Any]
        
        logger.info("RobustSceneManager initialized with error handling capabilities")
    
    def load_scene(self, scene_name: str, *args, **kwargs) -> bool:
        """
        Override the base load_scene method with our safe version.
        
        Args:
            scene_name: Name of the scene to load
            *args, **kwargs: Additional arguments to pass to the base method
            
        Returns:
            True if scene loaded successfully, False otherwise
        """
        try:
            # Use error-handling wrapper only if explicitly requested, otherwise call base
            return BaseSceneManager.load_scene(self, scene_name, *args, **kwargs)
        except Exception as e:
            # Handle the error using the error handler and return False
            self.error_handler.handle_scene_load_error(scene_name, e, context={})
            return False
    
    def update(self, *args, **kwargs) -> None:
        """
        Override the base update method to add error handling.
        """
        try:
            BaseSceneManager.update(self, *args, **kwargs)
        except Exception as e:
            handle_component_error(
                component_name="SceneManager",
                method_name="update",
                error=e,
                severity=ErrorSeverity.ERROR,
                context={"args": args, "kwargs": kwargs}
            )
    
    def validate_scene_assets(self, scene_name: str) -> List[Tuple[str, str]]:
        """
        Validate that all assets required by a scene are available.
        
        Args:
            scene_name: Name of the scene to validate
            
        Returns:
            List of tuples (asset_path, asset_type) for missing assets
        """
        missing_assets = []
        try:
            # Check if we have a scene_asset_registry or similar
            if hasattr(self, 'scene_asset_registry') and scene_name in self.scene_asset_registry:
                assets = self.scene_asset_registry[scene_name]
                for asset_path, asset_type in assets.items():
                    if hasattr(self, 'asset_exists'):
                        if not self.asset_exists(asset_path):
                            missing_assets.append((asset_path, asset_type))
                            self.error_handler.handle_missing_asset(asset_path, asset_type, scene_name)
                    else:
                        import os
                        if not os.path.exists(asset_path):
                            missing_assets.append((asset_path, asset_type))
                            self.error_handler.handle_missing_asset(asset_path, asset_type, scene_name)
            elif scene_name in self.scene_asset_dependencies:
                for asset_path in self.scene_asset_dependencies[scene_name]:
                    ext = asset_path.lower().split('.')[-1] if '.' in asset_path else ''
                    asset_type = self._get_asset_type_from_extension(ext)
                    import os
                    if not os.path.exists(asset_path):
                        missing_assets.append((asset_path, asset_type))
                        self.error_handler.handle_missing_asset(asset_path, asset_type, scene_name)
            self.scene_validation_cache[scene_name] = {
                asset_path: False for asset_path, _ in missing_assets
            }
            if missing_assets:
                logger.warning(f"Scene '{scene_name}' is missing {len(missing_assets)} assets")
            return missing_assets
        except Exception as e:
            logger.error(f"Error validating assets for scene '{scene_name}': {str(e)}")
            return []
    
    def _get_asset_type_from_extension(self, ext: str) -> str:
        """
        Guess asset type from file extension.
        
        Args:
            ext: File extension
            
        Returns:
            Asset type string
        """
        # Map common extensions to asset types
        extension_map = {
            'png': 'texture',
            'jpg': 'texture',
            'jpeg': 'texture',
            'bmp': 'texture',
            'obj': 'model',
            'fbx': 'model',
            'wav': 'audio',
            'mp3': 'audio',
            'ogg': 'audio',
            'ttf': 'font',
            'otf': 'font',
            'py': 'script',
            'json': 'data'
        }
        
        return extension_map.get(ext.lower(), 'unknown')
    
    def substitute_asset(self, original_path: str, placeholder_path: str) -> None:
        """
        Substitute a missing asset with a placeholder.
        
        Args:
            original_path: Path to the missing asset
            placeholder_path: Path to the placeholder asset
        """
        # Implementation depends on how assets are managed
        # This is a placeholder implementation
        try:
            logger.info(f"Substituting asset '{original_path}' with '{placeholder_path}'")
            
            # If we have an asset_manager with a register_placeholder method, use it
            if hasattr(self, 'asset_manager') and hasattr(self.asset_manager, 'register_placeholder'):
                self.asset_manager.register_placeholder(original_path, placeholder_path)
            # If we have a direct asset_map, update it
            elif hasattr(self, 'asset_map'):
                self.asset_map[original_path] = placeholder_path
                
        except Exception as e:
            logger.error(f"Error substituting asset '{original_path}': {str(e)}")
    
    def force_complete_transition(self, target_scene: str) -> None:
        """
        Force-complete a stuck transition.
        
        Args:
            target_scene: The scene to transition to
        """
        try:
            logger.warning(f"Force-completing transition to '{target_scene}'")
            
            # Implementation depends on how scenes are managed
            # This is a general implementation that should work in most cases
            
            # 1. Set the current scene directly
            if hasattr(self, 'current_scene'):
                setattr(self, 'current_scene', target_scene)
            
            # 2. If there's a scenes dictionary, ensure it's properly set
            if hasattr(self, 'scenes') and isinstance(self.scenes, dict) and target_scene in self.scenes:
                if hasattr(self, 'active_scene'):
                    setattr(self, 'active_scene', self.scenes[target_scene])
            
            # 3. If there's an on_scene_changed callback, call it
            if hasattr(self, 'on_scene_changed') and callable(self.on_scene_changed):
                self.on_scene_changed(target_scene)
            
            # 4. Reset any transition flags
            if hasattr(self, 'is_transitioning'):
                setattr(self, 'is_transitioning', False)
            
            # 5. Log completion for debugging
            logger.info(f"Transition force-completed to '{target_scene}'")
            
        except Exception as e:
            logger.error(f"Error force-completing transition: {str(e)}")
    
    def rollback_transition(self, original_scene: str) -> None:
        """
        Roll back a failed transition to the original scene.
        
        Args:
            original_scene: The scene to roll back to
        """
        try:
            logger.warning(f"Rolling back transition to '{original_scene}'")
            
            # Similar implementation to force_complete_transition
            # but rolling back to the original scene
            
            # 1. Set the current scene directly
            if hasattr(self, 'current_scene'):
                setattr(self, 'current_scene', original_scene)
            
            # 2. If there's a scenes dictionary, ensure it's properly set
            if hasattr(self, 'scenes') and isinstance(self.scenes, dict) and original_scene in self.scenes:
                if hasattr(self, 'active_scene'):
                    setattr(self, 'active_scene', self.scenes[original_scene])
            
            # 3. If there's an on_scene_changed callback, call it
            if hasattr(self, 'on_scene_changed') and callable(self.on_scene_changed):
                self.on_scene_changed(original_scene)
            
            # 4. Reset any transition flags
            if hasattr(self, 'is_transitioning'):
                setattr(self, 'is_transitioning', False)
            
            # 5. Log completion for debugging
            logger.info(f"Transition rolled back to '{original_scene}'")
            
        except Exception as e:
            logger.error(f"Error rolling back transition: {str(e)}")
    
    def register_scene_asset_dependencies(self, scene_name: str, asset_paths: List[str]) -> None:
        """
        Register dependencies between a scene and its required assets.
        
        Args:
            scene_name: Name of the scene
            asset_paths: List of asset paths required by the scene
        """
        if scene_name not in self.scene_asset_dependencies:
            self.scene_asset_dependencies[scene_name] = set()
            
        for path in asset_paths:
            self.scene_asset_dependencies[scene_name].add(path)
            
        logger.info(f"Registered {len(asset_paths)} asset dependencies for scene '{scene_name}'")
    
    def get_error_state(self) -> Dict[str, Any]:
        """
        Get the current error state for debugging and monitoring.
        
        Returns:
            Dictionary containing detailed error state information
        """
        error_state = self.get_error_reports()
        
        # Add additional state information
        error_state.update({
            'scene_asset_dependencies': {
                scene: list(assets) for scene, assets in self.scene_asset_dependencies.items()
            },
            'current_transition_id': self.current_transition_id,
        })
        
        return error_state
    
    def set_scene_loader_manager(self, loader_manager: Any) -> None:
        """Set the SceneLoaderManager for async scene loading."""
        self.scene_loader_manager = loader_manager 

    def load_scene_async(self, scene_id: str, priority: int = 1, callback: Optional[Callable] = None):
        """Begin asynchronous scene loading using the SceneLoaderManager if set."""
        if self.scene_loader_manager:
            self.scene_loader_manager.queue_scene_load(scene_id, priority=priority, callback=callback)
        else:
            # Fallback: synchronous activation with error handling
            success = self.load_scene(scene_id)
            if callback:
                callback(success=success)

    @property
    def current_scene(self) -> Optional[str]:
        """Alias for active_scene to maintain compatibility with error handling and tests."""
        return getattr(self, 'active_scene', None)

    @current_scene.setter
    def current_scene(self, value: Optional[str]):
        self.active_scene = value

    def load_scene_safe(self, scene_name: str, *args, **kwargs) -> bool:
        """
        Safely load a scene with error handling and fallbacks.
        """
        attempt = 0
        while attempt < self.max_retries:
            try:
                # Call the instance's load_scene method (can be monkey-patched in tests)
                result = self.load_scene(scene_name, *args, **kwargs)
                if result:
                    return True
            except Exception as e:
                self.error_handler.handle_scene_load_error(scene_name, e, context={})
            attempt += 1
        # If all attempts fail, handle fallback or error
        return False 
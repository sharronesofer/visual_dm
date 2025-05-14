"""
Error handling extensions for the Scene Management System.

This module applies the specialized error handling functionality to the
existing Scene Manager implementation, enhancing it with robust error
handling for failed scene loads, missing assets, and interrupted transitions.
"""

import logging
import os
import time
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

import pygame

from .error_handler import ErrorSeverity, handle_component_error
from .scene_error_handler import SceneErrorHandler

logger = logging.getLogger(__name__)

class SceneManagerErrorHandling:
    """Mixin class to add error handling functionality to SceneManager."""
    
    def __init__(self, *args, **kwargs):
        """Initialize error handling components."""
        # Initialize error handler
        self.error_handler = SceneErrorHandler(
            default_scene=kwargs.get('default_scene', 'loading'),
            max_retries=kwargs.get('max_retries', 3),
            transition_timeout=kwargs.get('transition_timeout', 10000)
        )
        
        # Track current transition
        self.current_transition_id = None
        
        # Ensure placeholder assets exist
        self._ensure_placeholder_assets()
        
        # Call parent initialization if needed
        super().__init__(*args, **kwargs)
        
    def _ensure_placeholder_assets(self) -> None:
        """Ensure placeholder assets for missing resources exist."""
        placeholder_dir = os.path.join('visual_client', 'assets', 'placeholders')
        
        # Check if basic placeholders exist
        missing_texture_path = os.path.join(placeholder_dir, 'missing_texture.png')
        
        if not os.path.exists(missing_texture_path):
            logger.warning("Placeholder assets not found. Creating placeholders...")
            
            # Try to create them using the placeholder script
            placeholder_script = os.path.join(placeholder_dir, 'create_placeholders.py')
            
            if os.path.exists(placeholder_script):
                try:
                    import subprocess
                    subprocess.run(['python', placeholder_script], 
                                  check=True, 
                                  stdout=subprocess.PIPE, 
                                  stderr=subprocess.PIPE)
                    logger.info("Successfully created placeholder assets")
                except Exception as e:
                    logger.error(f"Failed to create placeholder assets: {str(e)}")
                    
                    # Create a minimal placeholder texture if script fails
                    try:
                        os.makedirs(placeholder_dir, exist_ok=True)
                        
                        # Create a simple colored surface as a minimal fallback
                        surface = pygame.Surface((64, 64))
                        surface.fill((255, 0, 255))  # Magenta for missing textures
                        
                        # Draw checkerboard pattern
                        for y in range(0, 64, 8):
                            for x in range(0, 64, 8):
                                if (x // 8 + y // 8) % 2 == 0:
                                    pygame.draw.rect(surface, (0, 0, 0), (x, y, 8, 8))
                        
                        pygame.image.save(surface, missing_texture_path)
                        logger.info(f"Created minimal placeholder texture at {missing_texture_path}")
                    except Exception as e2:
                        logger.error(f"Failed to create minimal placeholder texture: {str(e2)}")
            else:
                logger.error(f"Placeholder script not found at {placeholder_script}")
    
    def load_scene_safe(self, scene_name: str, *args, **kwargs) -> bool:
        """
        Safely load a scene with error handling and fallbacks.
        
        Args:
            scene_name: Name of the scene to load
            *args, **kwargs: Arguments to pass to the actual load_scene method
            
        Returns:
            True if scene loaded successfully, False otherwise
        """
        try:
            # Start transition tracking
            if hasattr(self, 'current_scene'):
                current_scene = getattr(self, 'current_scene', 'unknown')
                self.current_transition_id = self.error_handler.start_transition(
                    from_scene=current_scene,
                    to_scene=scene_name
                )
            
            # Try to validate assets before loading (if asset validation exists)
            if hasattr(self, 'validate_scene_assets'):
                self.error_handler.update_transition(
                    self.current_transition_id, 
                    "validating_assets"
                )
                
                try:
                    missing_assets = self.validate_scene_assets(scene_name)
                    if missing_assets:
                        for asset_path, asset_type in missing_assets:
                            # Get placeholder and substitute
                            placeholder = self.error_handler.handle_missing_asset(
                                asset_path=asset_path,
                                asset_type=asset_type,
                                scene_name=scene_name
                            )
                            
                            # If we have an asset substitution method, use it
                            if hasattr(self, 'substitute_asset'):
                                self.substitute_asset(asset_path, placeholder)
                except Exception as validate_error:
                    logger.error(f"Asset validation failed: {str(validate_error)}")
                    # Continue with loading, we'll handle missing assets as they occur
            
            # Update transition status
            if self.current_transition_id:
                self.error_handler.update_transition(
                    self.current_transition_id, 
                    "loading_scene"
                )
            
            # Call the actual load_scene method
            original_activate_scene = super().activate_scene
            result = original_activate_scene(scene_name)
            
            # Mark transition as complete if successful
            if self.current_transition_id:
                self.error_handler.complete_transition(
                    self.current_transition_id, 
                    success=True
                )
                self.current_transition_id = None
                
            return result
            
        except Exception as e:
            logger.error(f"Error loading scene '{scene_name}': {str(e)}")
            
            # Mark transition as failed
            if self.current_transition_id:
                self.error_handler.complete_transition(
                    self.current_transition_id, 
                    success=False
                )
                self.current_transition_id = None
            
            # Handle error with error_handler
            fallback_scene = self.error_handler.handle_scene_load_error(
                scene_name=scene_name,
                error=e,
                context={'args': args, 'kwargs': kwargs}
            )
            
            if fallback_scene == scene_name:
                # Retry the same scene
                logger.info(f"Retrying scene load for '{scene_name}'")
                return self.load_scene_safe(scene_name, *args, **kwargs)
            else:
                # Load fallback scene
                logger.info(f"Loading fallback scene '{fallback_scene}'")
                try:
                    # Load the fallback scene, but avoid infinite recursion
                    if hasattr(self, 'activate_scene'):
                        fallback_result = super().activate_scene(fallback_scene)
                        return fallback_result
                    else:
                        logger.error("Cannot load fallback scene - activate_scene method not found")
                        return False
                except Exception as fallback_error:
                    logger.critical(f"Failed to load fallback scene '{fallback_scene}': {str(fallback_error)}")
                    # At this point, we're in a bad state
                    handle_component_error(
                        error=fallback_error,
                        component_name="SceneManager",
                        severity=ErrorSeverity.CRITICAL,
                        context={'scene': fallback_scene, 'fallback_for': scene_name}
                    )
                    return False
    
    def update_safe(self, *args, **kwargs) -> None:
        """
        Safe version of the update method with error handling.
        
        Args:
            *args, **kwargs: Arguments to pass to the actual update method
        """
        try:
            # Check for transition timeout
            if self.current_transition_id:
                timed_out, transition_data = self.error_handler.check_transition_timeout()
                if timed_out:
                    # Handle timeout - try to force completion or rollback
                    logger.warning("Scene transition timed out, attempting to force completion")
                    self._handle_transition_timeout(transition_data)
            
            # Call original update method
            original_update = super().update
            original_update(*args, **kwargs)
            
        except Exception as e:
            logger.error(f"Error in scene update: {str(e)}")
            handle_component_error(
                error=e,
                component_name="SceneManager",
                severity=ErrorSeverity.MEDIUM,
                context={'args': args, 'kwargs': kwargs}
            )
            
            # Continue execution - better to have a partially updated frame than crash
    
    def _handle_transition_timeout(self, transition_data: Dict[str, Any]) -> None:
        """
        Handle a timed out transition by forcing completion or rolling back.
        
        Args:
            transition_data: Data about the transition that timed out
        """
        try:
            # Get destination scene
            to_scene = transition_data.get('to_scene')
            from_scene = transition_data.get('from_scene')
            
            # Determine if we're closer to completing or starting the transition
            events = transition_data.get('events', [])
            
            # Check if we reached loading_scene stage
            reached_loading = any(e.get('event') == 'loading_scene' for e in events)
            
            if reached_loading:
                # We're closer to completing - try to force complete
                logger.info(f"Forcing completion of transition to '{to_scene}'")
                
                # If we have a force_complete method, use it
                if hasattr(self, 'force_complete_transition'):
                    self.force_complete_transition(to_scene)
                else:
                    # Otherwise try to directly set the scene
                    if hasattr(self, 'current_scene'):
                        setattr(self, 'current_scene', to_scene)
                        logger.info(f"Forced scene to '{to_scene}'")
            else:
                # We're closer to the start - roll back
                logger.info(f"Rolling back transition to '{from_scene}'")
                
                # If we have a rollback method, use it
                if hasattr(self, 'rollback_transition'):
                    self.rollback_transition(from_scene)
                else:
                    # Otherwise try to directly reset the scene
                    if hasattr(self, 'current_scene'):
                        setattr(self, 'current_scene', from_scene)
                        logger.info(f"Reset scene to '{from_scene}'")
            
            # Reset transition tracking
            self.current_transition_id = None
            self.error_handler.force_complete_transition()
            
        except Exception as e:
            logger.error(f"Error handling transition timeout: {str(e)}")
            # Clear the transition state to avoid getting stuck
            self.current_transition_id = None
            self.error_handler.force_complete_transition()
    
    def handle_missing_asset(self, asset_path: str, asset_type: str) -> str:
        """
        Handle a missing asset during runtime.
        
        Args:
            asset_path: Path to the missing asset
            asset_type: Type of the missing asset (texture, model, audio, etc.)
            
        Returns:
            Path to the placeholder asset to use
        """
        current_scene = getattr(self, 'current_scene', 'unknown') if hasattr(self, 'current_scene') else 'unknown'
        
        return self.error_handler.handle_missing_asset(
            asset_path=asset_path,
            asset_type=asset_type,
            scene_name=current_scene
        )
    
    def get_error_reports(self) -> Dict[str, Any]:
        """
        Get error reports for debugging and monitoring.
        
        Returns:
            Dictionary containing error reports
        """
        return {
            'missing_assets': self.error_handler.get_missing_assets_report(),
            'transition_history': self.error_handler.get_transition_history(),
            'load_attempts': self.error_handler.load_attempts
        }
    
    def reset_error_tracking(self) -> None:
        """Reset all error tracking data."""
        self.error_handler.reset_load_attempts()
        self.current_transition_id = None 
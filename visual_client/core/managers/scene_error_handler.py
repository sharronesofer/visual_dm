"""
Specialized error handling for the Scene Management System.

This module extends the base error handling system with specific capabilities 
for gracefully managing scene-related failures including failed scene loads,
missing assets, and interrupted transitions.
"""

import logging
import time
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
import pygame

from .error_handler import handle_component_error, ErrorSeverity

logger = logging.getLogger(__name__)

class SceneErrorType(Enum):
    """Types of errors that can occur in the Scene Management System."""
    SCENE_LOAD_FAILURE = "scene_load_failure"
    MISSING_ASSET = "missing_asset"
    TRANSITION_INTERRUPTED = "transition_interrupted"
    TRANSITION_TIMEOUT = "transition_timeout"
    INITIALIZATION_FAILURE = "initialization_failure"
    STATE_CORRUPTION = "state_corruption"

class SceneErrorHandler:
    """Specialized error handler for Scene Management System."""
    
    def __init__(self, 
                 default_scene: str = "loading", 
                 max_retries: int = 3,
                 transition_timeout: int = 10000):
        """
        Initialize the scene error handler.
        
        Args:
            default_scene: Scene to fall back to when loading fails
            max_retries: Maximum number of retry attempts for scene loading
            transition_timeout: Timeout in milliseconds for scene transitions
        """
        self.default_scene = default_scene
        self.max_retries = max_retries
        self.transition_timeout = transition_timeout
        
        # Track scene load attempts
        self.load_attempts: Dict[str, int] = {}
        
        # Track missing assets
        self.missing_assets: Dict[str, List[str]] = {}
        
        # Track transition state
        self.transition_history: List[Dict[str, Any]] = []
        self.active_transition: Optional[Dict[str, Any]] = None
        
        # Placeholder assets by type
        self.placeholder_assets: Dict[str, str] = {
            "texture": "visual_client/assets/placeholders/missing_texture.png",
            "model": "visual_client/assets/placeholders/missing_model.obj",
            "audio": "visual_client/assets/placeholders/silent_audio.wav",
            "font": "visual_client/assets/placeholders/default_font.ttf",
            "script": "visual_client/assets/placeholders/empty_script.py",
        }
        
    def handle_scene_load_error(self, 
                               scene_name: str, 
                               error: Exception, 
                               context: Optional[Dict[str, Any]] = None) -> str:
        """
        Handle scene loading errors with appropriate fallback mechanisms.
        
        Args:
            scene_name: Name of the scene that failed to load
            error: The exception that occurred
            context: Additional context about the error
            
        Returns:
            Name of the scene to load instead (default or another fallback)
        """
        # Track load attempts
        if scene_name not in self.load_attempts:
            self.load_attempts[scene_name] = 1
        else:
            self.load_attempts[scene_name] += 1
            
        attempt = self.load_attempts[scene_name]
        
        error_context = {
            "scene": scene_name,
            "attempt": attempt,
            "max_retries": self.max_retries,
        }
        if context:
            error_context.update(context)
            
        # Determine severity based on attempts
        if attempt <= self.max_retries:
            severity = ErrorSeverity.MEDIUM
            logger.error(f"Scene load error for '{scene_name}' (Attempt {attempt}/{self.max_retries}): {str(error)}")
        else:
            severity = ErrorSeverity.HIGH
            logger.critical(f"Scene load failed after {self.max_retries} attempts for '{scene_name}': {str(error)}")
            
        # Log error with standard handler
        handle_component_error(
            error=error,
            component_name="SceneManager",
            severity=severity,
            context=error_context
        )
        
        # Determine if we should retry or fall back
        if attempt < self.max_retries:
            logger.info(f"Retrying scene load for '{scene_name}' (Attempt {attempt+1}/{self.max_retries})")
            return scene_name  # Retry the same scene
        else:
            logger.warning(f"Falling back to default scene '{self.default_scene}' after failed attempts to load '{scene_name}'")
            self.load_attempts[scene_name] = 0  # Reset counter for future attempts
            return self.default_scene
    
    def handle_missing_asset(self, 
                            asset_path: str, 
                            asset_type: str, 
                            scene_name: str) -> str:
        """
        Handle missing assets by providing fallback placeholders.
        
        Args:
            asset_path: Path to the missing asset
            asset_type: Type of the missing asset (texture, model, audio, etc.)
            scene_name: Name of the scene trying to load the asset
            
        Returns:
            Path to the placeholder asset to use instead
        """
        # Normalize scene_name to 'unknown' if None
        key = scene_name if scene_name is not None else 'unknown'
        if key not in self.missing_assets:
            self.missing_assets[key] = []
        if asset_path not in self.missing_assets[key]:
            self.missing_assets[key].append(asset_path)
            
        # Log the missing asset
        logger.warning(f"Missing {asset_type} asset in scene '{scene_name}': {asset_path}")
        
        # Get placeholder based on type or use default
        placeholder = self.placeholder_assets.get(asset_type.lower(), 
                                                self.placeholder_assets["texture"])
        
        logger.info(f"Using placeholder for missing {asset_type}: {placeholder}")
        return placeholder
    
    def start_transition(self, from_scene: str, to_scene: str) -> int:
        """
        Start tracking a scene transition.
        
        Args:
            from_scene: Source scene name
            to_scene: Destination scene name
            
        Returns:
            Transition ID for reference
        """
        transition_id = len(self.transition_history) + 1
        
        transition = {
            "id": transition_id,
            "from_scene": from_scene,
            "to_scene": to_scene,
            "start_time": time.time(),
            "end_time": None,
            "status": "in_progress",
            "events": [{
                "time": time.time(),
                "event": "started"
            }]
        }
        
        self.active_transition = transition
        self.transition_history.append(transition)
        
        return transition_id
    
    def update_transition(self, transition_id: int, event: str, data: Optional[Dict[str, Any]] = None) -> None:
        """
        Update a transition with an event.
        
        Args:
            transition_id: ID of the transition to update
            event: Event name (e.g., "loading_assets", "unloading_old_scene")
            data: Additional event data
        """
        for transition in self.transition_history:
            if transition["id"] == transition_id:
                transition["events"].append({
                    "time": time.time(),
                    "event": event,
                    "data": data
                })
                return
                
        logger.warning(f"Attempted to update non-existent transition: {transition_id}")
    
    def complete_transition(self, transition_id: int, success: bool = True) -> None:
        """
        Mark a transition as complete.
        
        Args:
            transition_id: ID of the transition to complete
            success: Whether the transition completed successfully
        """
        for transition in self.transition_history:
            if transition["id"] == transition_id:
                transition["end_time"] = time.time()
                transition["status"] = "completed" if success else "failed"
                transition["events"].append({
                    "time": time.time(),
                    "event": "completed" if success else "failed"
                })
                
                if self.active_transition and self.active_transition["id"] == transition_id:
                    self.active_transition = None
                return
                
        logger.warning(f"Attempted to complete non-existent transition: {transition_id}")
    
    def check_transition_timeout(self) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Check if the current transition has timed out.
        
        Returns:
            Tuple of (has_timed_out, transition_data)
        """
        if not self.active_transition:
            return False, None
            
        elapsed = (time.time() - self.active_transition["start_time"]) * 1000  # Convert to ms
        
        if elapsed > self.transition_timeout:
            transition_data = dict(self.active_transition)  # Copy to avoid modification issues
            
            # Log timeout
            logger.error(f"Scene transition from '{self.active_transition['from_scene']}' " +
                       f"to '{self.active_transition['to_scene']}' timed out after {elapsed:.2f}ms")
            
            # Update transition status
            self.active_transition["status"] = "timeout"
            self.active_transition["events"].append({
                "time": time.time(),
                "event": "timeout",
                "elapsed_ms": elapsed
            })
            
            return True, transition_data
            
        return False, None
    
    def force_complete_transition(self) -> Optional[Dict[str, Any]]:
        """
        Force-complete the current transition when it's stuck.
        
        Returns:
            The transition data that was force-completed, or None if no active transition
        """
        if not self.active_transition:
            return None
            
        transition_data = dict(self.active_transition)  # Copy
        
        # Log forced completion
        logger.warning(f"Forcing completion of stuck transition from '{self.active_transition['from_scene']}' " +
                     f"to '{self.active_transition['to_scene']}'")
        
        # Update transition status
        self.active_transition["end_time"] = time.time()
        self.active_transition["status"] = "force_completed"
        self.active_transition["events"].append({
            "time": time.time(),
            "event": "force_completed"
        })
        
        self.active_transition = None
        return transition_data
    
    def get_transition_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent transition history for debugging.
        
        Args:
            limit: Maximum number of transitions to return
            
        Returns:
            List of recent transitions
        """
        return self.transition_history[-limit:] if self.transition_history else []
    
    def get_missing_assets_report(self) -> Dict[str, List[str]]:
        """
        Get a report of all missing assets by scene.
        
        Returns:
            Dictionary of scene names to lists of missing asset paths
        """
        return self.missing_assets
    
    def reset_load_attempts(self, scene_name: Optional[str] = None) -> None:
        """
        Reset load attempt counters.
        
        Args:
            scene_name: Specific scene to reset, or all scenes if None
        """
        if scene_name:
            if scene_name in self.load_attempts:
                self.load_attempts[scene_name] = 0
        else:
            self.load_attempts = {} 
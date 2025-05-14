"""
Resource management system for game assets.
"""

import os
import json
import shutil
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from .error_handler import handle_component_error, ErrorSeverity

logger = logging.getLogger(__name__)

class ResourceManager:
    """Manages game resources and assets."""
    
    def __init__(self, data_dir: str = "data"):
        """Initialize the resource manager.
        
        Args:
            data_dir: Directory for game data
        """
        try:
            self.data_dir = Path(data_dir)
            self.data_dir.mkdir(parents=True, exist_ok=True)
            
            # Create subdirectories
            self.saves_dir = self.data_dir / "saves"
            self.saves_dir.mkdir(exist_ok=True)
            
            self.screenshots_dir = self.data_dir / "screenshots"
            self.screenshots_dir.mkdir(exist_ok=True)
            
            self.cache_dir = self.data_dir / "cache"
            self.cache_dir.mkdir(exist_ok=True)
            
            # Initialize resource cache
            self.resource_cache: Dict[str, Any] = {}
            
            # Load resource index
            self.resource_index = self._load_resource_index()
            
            logger.info("Resource manager initialized")
            
        except Exception as e:
            handle_component_error(
                "ResourceManager",
                "__init__",
                e,
                ErrorSeverity.CRITICAL
            )
            raise
            
    def _load_resource_index(self) -> Dict[str, Any]:
        """Load resource index from file.
        
        Returns:
            Resource index dictionary
        """
        try:
            index_path = self.data_dir / "resource_index.json"
            if index_path.exists():
                with open(index_path, "r") as f:
                    return json.load(f)
            return {}
            
        except Exception as e:
            handle_component_error(
                "ResourceManager",
                "_load_resource_index",
                e,
                ErrorSeverity.ERROR
            )
            return {}
            
    def _save_resource_index(self) -> None:
        """Save resource index to file."""
        try:
            index_path = self.data_dir / "resource_index.json"
            with open(index_path, "w") as f:
                json.dump(self.resource_index, f, indent=4)
                
        except Exception as e:
            handle_component_error(
                "ResourceManager",
                "_save_resource_index",
                e,
                ErrorSeverity.ERROR
            )
            
    def save_game(self, save_name: str, data: Dict[str, Any]) -> bool:
        """Save game state.
        
        Args:
            save_name: Name of save file
            data: Game state data
            
        Returns:
            True if successful, False otherwise
        """
        try:
            save_path = self.saves_dir / f"{save_name}.json"
            with open(save_path, "w") as f:
                json.dump(data, f, indent=4)
                
            # Update resource index
            self.resource_index[f"save:{save_name}"] = {
                "path": str(save_path),
                "type": "save",
                "timestamp": str(save_path.stat().st_mtime)
            }
            self._save_resource_index()
            
            logger.info(f"Game saved: {save_name}")
            return True
            
        except Exception as e:
            handle_component_error(
                "ResourceManager",
                "save_game",
                e,
                ErrorSeverity.ERROR,
                {"save_name": save_name}
            )
            return False
            
    def load_game(self, save_name: str) -> Optional[Dict[str, Any]]:
        """Load game state.
        
        Args:
            save_name: Name of save file
            
        Returns:
            Game state data if successful, None otherwise
        """
        try:
            save_path = self.saves_dir / f"{save_name}.json"
            if not save_path.exists():
                logger.warning(f"Save file not found: {save_name}")
                return None
                
            with open(save_path, "r") as f:
                data = json.load(f)
                
            logger.info(f"Game loaded: {save_name}")
            return data
            
        except Exception as e:
            handle_component_error(
                "ResourceManager",
                "load_game",
                e,
                ErrorSeverity.ERROR,
                {"save_name": save_name}
            )
            return None
            
    def delete_save(self, save_name: str) -> bool:
        """Delete save file.
        
        Args:
            save_name: Name of save file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            save_path = self.saves_dir / f"{save_name}.json"
            if save_path.exists():
                save_path.unlink()
                
                # Update resource index
                self.resource_index.pop(f"save:{save_name}", None)
                self._save_resource_index()
                
                logger.info(f"Save deleted: {save_name}")
                return True
                
            return False
            
        except Exception as e:
            handle_component_error(
                "ResourceManager",
                "delete_save",
                e,
                ErrorSeverity.ERROR,
                {"save_name": save_name}
            )
            return False
            
    def list_saves(self) -> List[Dict[str, Any]]:
        """List all save files.
        
        Returns:
            List of save file information
        """
        try:
            saves = []
            for entry in self.saves_dir.glob("*.json"):
                save_name = entry.stem
                saves.append({
                    "name": save_name,
                    "path": str(entry),
                    "timestamp": str(entry.stat().st_mtime)
                })
            return saves
            
        except Exception as e:
            handle_component_error(
                "ResourceManager",
                "list_saves",
                e,
                ErrorSeverity.ERROR
            )
            return []
            
    def save_screenshot(self, image_data: bytes, name: Optional[str] = None) -> Optional[str]:
        """Save screenshot.
        
        Args:
            image_data: Screenshot image data
            name: Optional screenshot name
            
        Returns:
            Screenshot path if successful, None otherwise
        """
        try:
            if name:
                filename = f"{name}.png"
            else:
                # Generate unique filename
                import time
                filename = f"screenshot_{int(time.time())}.png"
                
            screenshot_path = self.screenshots_dir / filename
            
            with open(screenshot_path, "wb") as f:
                f.write(image_data)
                
            # Update resource index
            self.resource_index[f"screenshot:{filename}"] = {
                "path": str(screenshot_path),
                "type": "screenshot",
                "timestamp": str(screenshot_path.stat().st_mtime)
            }
            self._save_resource_index()
            
            logger.info(f"Screenshot saved: {filename}")
            return str(screenshot_path)
            
        except Exception as e:
            handle_component_error(
                "ResourceManager",
                "save_screenshot",
                e,
                ErrorSeverity.ERROR,
                {"name": name}
            )
            return None
            
    def get_resource(self, resource_id: str) -> Optional[Dict[str, Any]]:
        """Get resource information.
        
        Args:
            resource_id: Resource identifier
            
        Returns:
            Resource information if found, None otherwise
        """
        try:
            return self.resource_index.get(resource_id)
            
        except Exception as e:
            handle_component_error(
                "ResourceManager",
                "get_resource",
                e,
                ErrorSeverity.ERROR,
                {"resource_id": resource_id}
            )
            return None
            
    def cache_resource(self, resource_id: str, data: Any) -> bool:
        """Cache resource data.
        
        Args:
            resource_id: Resource identifier
            data: Resource data
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.resource_cache[resource_id] = data
            return True
            
        except Exception as e:
            handle_component_error(
                "ResourceManager",
                "cache_resource",
                e,
                ErrorSeverity.ERROR,
                {"resource_id": resource_id}
            )
            return False
            
    def get_cached_resource(self, resource_id: str) -> Optional[Any]:
        """Get cached resource data.
        
        Args:
            resource_id: Resource identifier
            
        Returns:
            Cached resource data if found, None otherwise
        """
        try:
            return self.resource_cache.get(resource_id)
            
        except Exception as e:
            handle_component_error(
                "ResourceManager",
                "get_cached_resource",
                e,
                ErrorSeverity.ERROR,
                {"resource_id": resource_id}
            )
            return None
            
    def clear_cache(self) -> None:
        """Clear resource cache."""
        try:
            self.resource_cache.clear()
            logger.info("Resource cache cleared")
            
        except Exception as e:
            handle_component_error(
                "ResourceManager",
                "clear_cache",
                e,
                ErrorSeverity.ERROR
            )
            
    def cleanup(self) -> None:
        """Clean up resource manager."""
        try:
            # Save resource index
            self._save_resource_index()
            
            # Clear cache
            self.clear_cache()
            
            # Clean up temporary files
            if self.cache_dir.exists():
                shutil.rmtree(self.cache_dir)
                self.cache_dir.mkdir()
                
            logger.info("Resource manager cleaned up")
            
        except Exception as e:
            handle_component_error(
                "ResourceManager",
                "cleanup",
                e,
                ErrorSeverity.ERROR
            ) 
"""
Asset management utilities for the Visual DM game client.
"""

import pygame
import os
from typing import Dict, Optional, Tuple
from pathlib import Path
from .error_utils import handle_error

class AssetManager:
    """Manages game assets like images and sounds."""
    
    def __init__(self):
        """Initialize the asset manager."""
        self.images: Dict[str, pygame.Surface] = {}
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        self.music: Dict[str, str] = {}
        self.base_path = Path(__file__).parent.parent / "assets"
        
    def load_image(self, path: str) -> Optional[pygame.Surface]:
        """Load an image from file.
        
        Args:
            path: Path to image file
            
        Returns:
            Optional[pygame.Surface]: Loaded image or None if failed
        """
        try:
            if path in self.images:
                return self.images[path]
                
            full_path = self.base_path / path
            if not full_path.exists():
                handle_error(FileNotFoundError(f"Image not found: {path}"))
                return None
                
            image = pygame.image.load(str(full_path)).convert_alpha()
            self.images[path] = image
            return image
        except Exception as e:
            handle_error(e, {"path": path})
            return None
            
    def load_sound(self, path: str) -> Optional[pygame.mixer.Sound]:
        """Load a sound from file.
        
        Args:
            path: Path to sound file
            
        Returns:
            Optional[pygame.mixer.Sound]: Loaded sound or None if failed
        """
        try:
            if path in self.sounds:
                return self.sounds[path]
                
            full_path = self.base_path / path
            if not full_path.exists():
                handle_error(FileNotFoundError(f"Sound not found: {path}"))
                return None
                
            sound = pygame.mixer.Sound(str(full_path))
            self.sounds[path] = sound
            return sound
        except Exception as e:
            handle_error(e, {"path": path})
            return None
            
    def load_music(self, path: str) -> bool:
        """Load music from file.
        
        Args:
            path: Path to music file
            
        Returns:
            bool: True if successful
        """
        try:
            if path in self.music:
                return True
                
            full_path = self.base_path / path
            if not full_path.exists():
                handle_error(FileNotFoundError(f"Music not found: {path}"))
                return False
                
            self.music[path] = str(full_path)
            return True
        except Exception as e:
            handle_error(e, {"path": path})
            return False
            
    def play_sound(self, path: str) -> None:
        """Play a sound.
        
        Args:
            path: Path to sound file
        """
        try:
            sound = self.load_sound(path)
            if sound:
                sound.play()
        except Exception as e:
            handle_error(e, {"path": path})
            
    def play_music(self, path: str, loop: int = -1) -> None:
        """Play music.
        
        Args:
            path: Path to music file
            loop: Number of times to loop (-1 for infinite)
        """
        try:
            if self.load_music(path):
                pygame.mixer.music.load(self.music[path])
                pygame.mixer.music.play(loop)
        except Exception as e:
            handle_error(e, {"path": path, "loop": loop})
            
    def stop_music(self) -> None:
        """Stop playing music."""
        try:
            pygame.mixer.music.stop()
        except Exception as e:
            handle_error(e)
            
    def set_music_volume(self, volume: float) -> None:
        """Set music volume.
        
        Args:
            volume: Volume level (0.0 to 1.0)
        """
        try:
            pygame.mixer.music.set_volume(max(0.0, min(1.0, volume)))
        except Exception as e:
            handle_error(e, {"volume": volume})
            
    def set_sound_volume(self, volume: float) -> None:
        """Set sound volume.
        
        Args:
            volume: Volume level (0.0 to 1.0)
        """
        try:
            for sound in self.sounds.values():
                sound.set_volume(max(0.0, min(1.0, volume)))
        except Exception as e:
            handle_error(e, {"volume": volume}) 
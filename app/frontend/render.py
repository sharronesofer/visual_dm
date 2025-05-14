"""
Frontend rendering system.
"""

import pygame
from typing import Dict, Optional, List, Tuple, Any
from dataclasses import dataclass
from enum import Enum, auto

class AnimationType(Enum):
    """Types of animations available in the game."""
    IDLE = auto()
    WALK = auto()
    RUN = auto()
    ATTACK = auto()
    CAST = auto()
    HURT = auto()
    DEATH = auto()

@dataclass
class AnimationFrame:
    """Single frame of an animation."""
    surface: pygame.Surface
    duration: int  # Duration in milliseconds

class Animation:
    """Handles a single animation sequence."""
    
    def __init__(self, frames: List[AnimationFrame], loop: bool = True):
        """Initialize animation with frames."""
        self.frames = frames
        self.current_frame = 0
        self.time_accumulated = 0
        self.loop = loop
        self.finished = False
        
    def update(self, dt: int) -> pygame.Surface:
        """
        Update animation state and return current frame.
        
        Args:
            dt: Time elapsed since last update in milliseconds
            
        Returns:
            pygame.Surface: Current frame surface
        """
        if self.finished:
            return self.frames[-1].surface
            
        self.time_accumulated += dt
        current_frame = self.frames[self.current_frame]
        
        while self.time_accumulated >= current_frame.duration:
            self.time_accumulated -= current_frame.duration
            self.current_frame += 1
            
            if self.current_frame >= len(self.frames):
                if self.loop:
                    self.current_frame = 0
                else:
                    self.current_frame = len(self.frames) - 1
                    self.finished = True
                    break
                    
        return self.frames[self.current_frame].surface

class AnimationManager:
    """Manages all animations for game entities."""
    
    def __init__(self):
        """Initialize animation manager."""
        self.animations: Dict[str, Dict[AnimationType, Animation]] = {}
        
    def load_animation(self, entity_id: str, anim_type: AnimationType, 
                      spritesheet: pygame.Surface, frame_count: int,
                      frame_width: int, frame_height: int, 
                      frame_duration: int, loop: bool = True) -> None:
        """
        Load animation frames from a spritesheet.
        
        Args:
            entity_id: Unique identifier for the entity
            anim_type: Type of animation
            spritesheet: Surface containing all animation frames
            frame_count: Number of frames in animation
            frame_width: Width of each frame
            frame_height: Height of each frame
            frame_duration: Duration of each frame in milliseconds
            loop: Whether animation should loop
        """
        frames = []
        for i in range(frame_count):
            x = i * frame_width
            frame_rect = pygame.Rect(x, 0, frame_width, frame_height)
            frame_surface = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
            frame_surface.blit(spritesheet, (0, 0), frame_rect)
            frames.append(AnimationFrame(frame_surface, frame_duration))
            
        if entity_id not in self.animations:
            self.animations[entity_id] = {}
            
        self.animations[entity_id][anim_type] = Animation(frames, loop)
        
    def get_animation(self, entity_id: str, anim_type: AnimationType) -> Optional[Animation]:
        """Get animation for entity and type."""
        return self.animations.get(entity_id, {}).get(anim_type)
        
    def update(self, dt: int) -> None:
        """Update all active animations."""
        for animations in self.animations.values():
            for animation in animations.values():
                animation.update(dt)

class SpriteManager:
    """Manages sprite loading and caching."""
    
    def __init__(self):
        self.sprites: Dict[str, pygame.Surface] = {}
        self.animations: Dict[str, Dict[str, List[pygame.Surface]]] = {}
        
    def load_sprite(self, sprite_name: str, path: str) -> None:
        """Load a sprite from a file."""
        try:
            sprite = pygame.image.load(path).convert_alpha()
            self.sprites[sprite_name] = sprite
        except pygame.error as e:
            print(f"Error loading sprite {sprite_name}: {e}")
            
    def load_animation(self, animation_name: str, frames: Dict[str, List[str]]) -> None:
        """Load an animation sequence."""
        self.animations[animation_name] = {}
        for state, frame_paths in frames.items():
            self.animations[animation_name][state] = []
            for path in frame_paths:
                try:
                    frame = pygame.image.load(path).convert_alpha()
                    self.animations[animation_name][state].append(frame)
                except pygame.error as e:
                    print(f"Error loading animation frame {path}: {e}")
                    
    def get_sprite(self, sprite_name: str) -> Optional[pygame.Surface]:
        """Get a sprite by name."""
        return self.sprites.get(sprite_name)
        
    def get_animation_frame(self, animation_name: str, state: str, frame_index: int) -> Optional[pygame.Surface]:
        """Get a specific animation frame."""
        if animation_name in self.animations and state in self.animations[animation_name]:
            frames = self.animations[animation_name][state]
            if 0 <= frame_index < len(frames):
                return frames[frame_index]
        return None

class Renderer:
    """Base renderer class for game objects."""
    
    def __init__(self, screen):
        self.screen = screen
        
    def render(self, *args, **kwargs):
        """Render the object to the screen."""
        raise NotImplementedError("Subclasses must implement render()")

class SceneRenderer(Renderer):
    """Renders game scenes."""
    
    def render(self, scene):
        """Render a scene to the screen."""
        # Clear screen
        self.screen.fill((0, 0, 0))
        
        # Render scene background
        if scene.background:
            self.screen.blit(scene.background, (0, 0))
            
        # Render scene objects
        for obj in scene.objects:
            obj.render(self.screen)

class CharacterRenderer(Renderer):
    """Renders characters."""
    
    def render(self, character, x, y):
        """Render a character at the specified position."""
        if character.sprite:
            self.screen.blit(character.sprite, (x, y))
            
        # Render character name
        font = pygame.font.Font(None, 24)
        text = font.render(character.name, True, (255, 255, 255))
        self.screen.blit(text, (x, y - 20))

class UIRenderer(Renderer):
    """Renders UI elements."""
    
    def render(self, ui_elements):
        """Render UI elements to the screen."""
        for element in ui_elements:
            element.render(self.screen)

class GameRenderer:
    """Handles rendering of game elements."""
    
    def __init__(self):
        self.scene_renderer = None
        self.character_renderer = None
        self.ui_renderer = None
        
    def render_scene(self, scene_data: dict) -> None:
        """Render the current scene."""
        if self.scene_renderer:
            self.scene_renderer.render(scene_data)
            
    def render_character(self, character_data: dict) -> None:
        """Render a character."""
        if self.character_renderer:
            self.character_renderer.render(character_data)
            
    def render_ui(self, ui_data: dict) -> None:
        """Render UI elements."""
        if self.ui_renderer:
            self.ui_renderer.render(ui_data)
            
    def update_renderers(self, scene_renderer=None, character_renderer=None, ui_renderer=None) -> None:
        """Update renderer instances."""
        if scene_renderer:
            self.scene_renderer = scene_renderer
        if character_renderer:
            self.character_renderer = character_renderer
        if ui_renderer:
            self.ui_renderer = ui_renderer 

class Camera:
    """Camera for handling viewport and scrolling."""
    
    def __init__(self, width: int, height: int):
        """
        Initialize camera.
        
        Args:
            width: Viewport width
            height: Viewport height
        """
        self.rect = pygame.Rect(0, 0, width, height)
        self.world_size = (width, height)  # Default to viewport size
        self.target = None
        self.lerp_speed = 0.1  # Camera smoothing factor
        
    def set_world_size(self, width: int, height: int) -> None:
        """Set the size of the world the camera can move in."""
        self.world_size = (width, height)
        
    def set_target(self, target) -> None:
        """Set the target for the camera to follow."""
        self.target = target
        
    def update(self) -> None:
        """Update camera position."""
        if not self.target:
            return
            
        # Calculate target center position
        target_x = self.target.rect.centerx - self.rect.width // 2
        target_y = self.target.rect.centery - self.rect.height // 2
        
        # Smooth camera movement
        self.rect.x += (target_x - self.rect.x) * self.lerp_speed
        self.rect.y += (target_y - self.rect.y) * self.lerp_speed
        
        # Clamp to world bounds
        self.rect.clamp_ip(pygame.Rect(0, 0, *self.world_size))
        
    def apply(self, entity) -> pygame.Rect:
        """
        Apply camera offset to an entity.
        
        Args:
            entity: Game entity with a rect attribute
            
        Returns:
            pygame.Rect: Entity's position relative to camera
        """
        return entity.rect.move(-self.rect.x, -self.rect.y)
        
    def apply_rect(self, rect: pygame.Rect) -> pygame.Rect:
        """
        Apply camera offset to a rect.
        
        Args:
            rect: Rectangle to offset
            
        Returns:
            pygame.Rect: Rectangle position relative to camera
        """
        return rect.move(-self.rect.x, -self.rect.y)
        
    def apply_point(self, x: int, y: int) -> Tuple[int, int]:
        """
        Apply camera offset to a point.
        
        Args:
            x: X coordinate
            y: Y coordinate
            
        Returns:
            Tuple[int, int]: Point position relative to camera
        """
        return (x - self.rect.x, y - self.rect.y) 
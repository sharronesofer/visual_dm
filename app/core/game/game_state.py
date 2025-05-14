"""
Game state management system.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import pygame
from app.core.models.character import Character
from app.core.models.world_state import WorldState
from app.core.save.save_manager import SaveManager
from app.core.ui.ui_manager import UIManager
from app.core.rules.balance_constants import *

@dataclass
class GameState:
    """Class for managing the overall game state."""
    
    # Core components
    player: Character
    world_state: WorldState
    save_manager: SaveManager
    ui_manager: UIManager
    
    # State tracking
    current_scene: str = "main_menu"
    previous_scene: str = ""
    is_paused: bool = False
    debug_mode: bool = False
    
    # Game clock and timing
    clock: pygame.time.Clock = field(default_factory=pygame.time.Clock)
    frame_count: int = 0
    last_update: datetime = field(default_factory=datetime.utcnow)
    delta_time: float = 0.0
    
    # Scene-specific state
    scene_data: Dict[str, Any] = field(default_factory=dict)
    active_quests: List[Dict] = field(default_factory=list)
    active_events: List[Dict] = field(default_factory=list)
    
    # Performance monitoring
    fps: float = 60.0
    frame_times: List[float] = field(default_factory=list)
    
    def __post_init__(self):
        """Initialize additional components after dataclass initialization."""
        self.frame_times = []
        pygame.init()
        self.clock = pygame.time.Clock()
    
    def update(self) -> None:
        """Update the game state."""
        # Update timing
        current_time = datetime.utcnow()
        self.delta_time = (current_time - self.last_update).total_seconds()
        self.last_update = current_time
        self.frame_count += 1
        
        # Update FPS tracking
        self.frame_times.append(self.delta_time)
        if len(self.frame_times) > 60:  # Keep last 60 frames
            self.frame_times.pop(0)
        self.fps = 1.0 / (sum(self.frame_times) / len(self.frame_times))
        
        # Update world state
        if not self.is_paused:
            # Update all world management systems (World Management System)
            self.world_state.update_all_systems(hours=1)
            # Update active quests and events
            self._update_quests()
            self._update_events()
        
        # Update UI
        self.ui_manager.update(self.delta_time)
        
        # Cap frame rate
        self.clock.tick(MAX_FPS)
    
    def transition_to(self, scene_name: str, **kwargs) -> None:
        """Transition to a new scene."""
        self.previous_scene = self.current_scene
        self.current_scene = scene_name
        
        # Store scene-specific data
        self.scene_data[scene_name] = kwargs
        
        # Trigger scene initialization
        self.ui_manager.load_scene(scene_name, **kwargs)
    
    def save_game(self, save_name: str, description: str = "") -> bool:
        """Save the current game state."""
        game_state_data = {
            'player': self.player.to_dict(),
            'world_state': self.world_state.to_dict(),
            'current_scene': self.current_scene,
            'active_quests': self.active_quests,
            'active_events': self.active_events,
            'scene_data': self.scene_data
        }
        
        try:
            self.save_manager.create_save(
                name=save_name,
                description=description,
                player_id=str(self.player.id),
                character_id=self.player.id,
                game_state=game_state_data
            )
            return True
        except Exception as e:
            if self.debug_mode:
                print(f"Error saving game: {e}")
            return False
    
    def load_game(self, save_id: str) -> bool:
        """Load a saved game state."""
        save = self.save_manager.load_save(save_id)
        if not save:
            return False
        
        try:
            game_state = save.game_state
            self.player = Character.from_dict(game_state['player'])
            self.world_state = WorldState.from_dict(game_state['world_state'])
            self.current_scene = game_state['current_scene']
            self.active_quests = game_state['active_quests']
            self.active_events = game_state['active_events']
            self.scene_data = game_state['scene_data']
            
            # Transition to the loaded scene
            self.transition_to(self.current_scene, **self.scene_data.get(self.current_scene, {}))
            return True
        except Exception as e:
            if self.debug_mode:
                print(f"Error loading game: {e}")
            return False
    
    def toggle_pause(self) -> None:
        """Toggle the game's pause state."""
        self.is_paused = not self.is_paused
        if self.is_paused:
            self.ui_manager.show_pause_menu()
        else:
            self.ui_manager.hide_pause_menu()
    
    def _update_quests(self) -> None:
        """Update active quests."""
        for quest in self.active_quests:
            if quest.get('status') == 'active':
                self._check_quest_objectives(quest)
    
    def _check_quest_objectives(self, quest: Dict) -> None:
        """Check and update quest objectives."""
        objectives = quest.get('objectives', [])
        completed = all(obj.get('completed', False) for obj in objectives)
        
        if completed and quest.get('status') == 'active':
            quest['status'] = 'completed'
            self._award_quest_rewards(quest)
    
    def _award_quest_rewards(self, quest: Dict) -> None:
        """Award rewards for completed quests."""
        rewards = quest.get('rewards', {})
        
        # Award experience
        if 'experience' in rewards:
            self.player.gain_experience(rewards['experience'])
        
        # Award items
        if 'items' in rewards:
            for item in rewards['items']:
                self.player.inventory.add_item(item['id'], item.get('quantity', 1))
        
        # Award gold
        if 'gold' in rewards:
            self.player.gold += rewards['gold']
    
    def _update_events(self) -> None:
        """Update active world events."""
        current_time = datetime.utcnow()
        
        # Filter out expired events and process active ones
        active_events = []
        for event in self.active_events:
            if event.get('end_time') and datetime.fromisoformat(event['end_time']) <= current_time:
                self._handle_event_completion(event)
            else:
                active_events.append(event)
        
        self.active_events = active_events
    
    def _handle_event_completion(self, event: Dict) -> None:
        """Handle the completion of a world event."""
        event_type = event.get('type')
        
        if event_type == 'weather':
            self.world_state.update_weather()
        elif event_type == 'faction':
            self.world_state.update_faction_relation(
                event['faction_id'],
                event.get('relation_change', 0)
            )
    
    def get_performance_stats(self) -> Dict[str, float]:
        """Get current performance statistics."""
        return {
            'fps': self.fps,
            'frame_time': self.delta_time * 1000,  # Convert to milliseconds
            'average_frame_time': (sum(self.frame_times) / len(self.frame_times)) * 1000
        }
    
    def cleanup(self) -> None:
        """Clean up resources before shutting down."""
        pygame.quit()
        # Additional cleanup as needed 
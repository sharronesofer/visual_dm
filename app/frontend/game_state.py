"""
Frontend game state management.
"""

import pygame
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict, field
from enum import Enum
from pydantic import BaseModel, Field

class GameScene(str, Enum):
    MAIN_MENU = "main_menu"
    CHARACTER_CREATION = "character_creation"
    GAME = "game"
    COMBAT = "combat"
    INVENTORY = "inventory"
    DIALOGUE = "dialogue"
    SETTINGS = "settings"

@dataclass
class SaveData:
    """Data structure for save game data."""
    save_id: str
    character_id: str
    timestamp: str
    game_state: Dict[str, Any]
    location: Dict[str, Any]
    inventory: Dict[str, Any]
    quests: List[Dict[str, Any]]

class GameState(BaseModel):
    """Game state model."""
    
    ui_state: Dict = Field(
        default_factory=lambda: {
            "active_panel": None,
            "current_screen": "main_menu",
            "dialogues": [],
            "notifications": []
        }
    )
    world_state: Dict = Field(
        default_factory=lambda: {
            "current_region": None,
            "discovered_locations": [],
            "active_events": []
        }
    )
    player_state: Dict = Field(
        default_factory=lambda: {
            "character": None,
            "party": [],
            "inventory": [],
            "quests": []
        }
    )
    system_state: Dict = Field(
        default_factory=lambda: {
            "time": datetime.now(),
            "paused": False,
            "debug_mode": False
        }
    )
    
    def transition_to(self, new_state: str, data: Optional[Dict] = None) -> None:
        """Transition to a new game state."""
        if data is None:
            data = {}
        self.ui_state["current_screen"] = new_state
        self.ui_state.update(data.get("ui_state", {}))
        self.world_state.update(data.get("world_state", {}))
        self.player_state.update(data.get("player_state", {}))
        self.system_state.update(data.get("system_state", {}))

class GameLoop:
    """Main game loop handling updates and rendering."""
    def __init__(self, state: GameState):
        self.state = state
        self.running = False
        self.fps = 60
        self.clock = pygame.time.Clock()

    def start(self):
        """Start the game loop."""
        pygame.init()
        self.running = True
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(self.fps)

    def stop(self):
        """Stop the game loop."""
        self.running = False
        pygame.quit()

    def handle_events(self):
        """Handle pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.stop()
            elif event.type == pygame.KEYDOWN:
                self.handle_keydown(event)

    def handle_keydown(self, event):
        """Handle key press events."""
        if event.key == pygame.K_ESCAPE:
            if self.state.ui_state["current_screen"] != GameScene.MAIN_MENU:
                self.state.transition_to(GameScene.MAIN_MENU)

    def update(self):
        """Update game state."""
        delta_time = self.clock.get_time() / 1000.0
        self.state.system_state["time"] = datetime.now()

    def render(self):
        """Render the current game state."""
        # This will be implemented by the renderer
        pass

class StateManager:
    """Manages game state transitions and persistence."""
    def __init__(self):
        self.current_state = GameState()
        self.state_history = []

    def push_state(self, new_state: str, data: Optional[Dict] = None) -> None:
        """Push a new state onto the stack."""
        self.state_history.append(self.current_state)
        self.current_state.transition_to(new_state, data)

    def pop_state(self) -> None:
        """Pop the current state from the stack."""
        if self.state_history:
            self.current_state = self.state_history.pop()

class SaveManager:
    """Manages game save data."""
    
    def __init__(self, save_dir: str = "saves"):
        """Initialize save manager with save directory."""
        self.save_dir = save_dir
        os.makedirs(save_dir, exist_ok=True)
        
    def save_game(self, save_data: SaveData) -> bool:
        """
        Save the current game state.
        
        Args:
            save_data: SaveData object containing game state
            
        Returns:
            bool: True if save successful, False otherwise
        """
        try:
            save_path = os.path.join(self.save_dir, f"{save_data.save_id}.json")
            with open(save_path, 'w') as f:
                json.dump(asdict(save_data), f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving game: {e}")
            return False
            
    def load_game(self, save_id: str) -> Optional[SaveData]:
        """
        Load a saved game state.
        
        Args:
            save_id: ID of save to load
            
        Returns:
            Optional[SaveData]: Loaded save data or None if not found
        """
        try:
            save_path = os.path.join(self.save_dir, f"{save_id}.json")
            with open(save_path, 'r') as f:
                data = json.load(f)
            return SaveData(**data)
        except Exception as e:
            print(f"Error loading save {save_id}: {e}")
            return None
            
    def list_saves(self) -> List[str]:
        """List all available save files."""
        saves = []
        for filename in os.listdir(self.save_dir):
            if filename.endswith('.json'):
                saves.append(filename[:-5])  # Remove .json extension
        return saves
        
    def delete_save(self, save_id: str) -> bool:
        """Delete a save file."""
        try:
            save_path = os.path.join(self.save_dir, f"{save_id}.json")
            os.remove(save_path)
            return True
        except Exception as e:
            print(f"Error deleting save {save_id}: {e}")
            return False 
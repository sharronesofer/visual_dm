from typing import List, Optional
from .storage import Storage
from .config import Config
from .errors import GameEngineError

class PlayerState:
    """Represents the state of a player in the game."""
    def __init__(self, name: str, position: tuple = (0, 0)):
        self.name = name
        self.position = position
        self.health = 100
        self.inventory: List[str] = []

class WorldState:
    """Represents the state of the game world."""
    def __init__(self):
        self.turn = 0
        self.map_data = {}  # Could be expanded to a grid or graph

class GameState:
    """Encapsulates the full game state, including player and world."""
    def __init__(self, player: PlayerState, world: WorldState):
        self.player = player
        self.world = world
        self.is_running = True

class GameEngine:
    """Main game engine class for running the game loop and managing state."""
    def __init__(self, config: Optional[Config] = None, storage: Optional[Storage] = None):
        self.config = config or Config()
        self.storage = storage or Storage()
        self.state = GameState(PlayerState("Player1"), WorldState())

    def run(self):
        """Main game loop stub."""
        try:
            while self.state.is_running:
                self.process_turn()
        except GameEngineError as e:
            print(f"Game error: {e}")
            self.state.is_running = False

    def process_turn(self):
        """Process a single turn of the game (stub)."""
        self.state.world.turn += 1
        # Game logic goes here
        print(f"Turn {self.state.world.turn}")
        # Example: Save state every 10 turns
        if self.state.world.turn % 10 == 0:
            self.storage.save_state(self.state)
        # Example: End after 100 turns
        if self.state.world.turn >= 100:
            self.state.is_running = False 
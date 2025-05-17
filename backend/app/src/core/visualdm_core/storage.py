import json
import os
from typing import Any
from .errors import StorageError

class Storage:
    """Handles saving and loading game state to local JSON files."""
    def __init__(self, save_path: str = "game_state.json"):
        self.save_path = save_path

    def save_state(self, state: Any) -> None:
        try:
            with open(self.save_path, "w") as f:
                json.dump(self._serialize_state(state), f, indent=2)
        except Exception as e:
            raise StorageError(f"Failed to save state: {e}")

    def load_state(self) -> Any:
        if not os.path.exists(self.save_path):
            raise StorageError("No saved state found.")
        try:
            with open(self.save_path, "r") as f:
                data = json.load(f)
            return self._deserialize_state(data)
        except Exception as e:
            raise StorageError(f"Failed to load state: {e}")

    def delete_state(self) -> None:
        try:
            if os.path.exists(self.save_path):
                os.remove(self.save_path)
        except Exception as e:
            raise StorageError(f"Failed to delete state: {e}")

    def _serialize_state(self, state: Any) -> dict:
        # Simple serialization for GameState; expand as needed
        return {
            "player": {
                "name": state.player.name,
                "position": state.player.position,
                "health": state.player.health,
                "inventory": state.player.inventory,
            },
            "world": {
                "turn": state.world.turn,
                "map_data": state.world.map_data,
            },
        }

    def _deserialize_state(self, data: dict) -> Any:
        # Simple deserialization for GameState; expand as needed
        from .game import PlayerState, WorldState, GameState
        player = PlayerState(
            name=data["player"]["name"],
            position=tuple(data["player"]["position"]),
        )
        player.health = data["player"]["health"]
        player.inventory = data["player"]["inventory"]
        world = WorldState()
        world.turn = data["world"]["turn"]
        world.map_data = data["world"]["map_data"]
        return GameState(player, world) 
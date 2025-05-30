import json
import os
from typing import Any, Dict
from .errors import ConfigError

class Config:
    """Loads and stores configuration for the game engine."""
    def __init__(self, config_path: str = "config.json"):
        self.config_path = config_path
        self.data: Dict[str, Any] = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r") as f:
                    return json.load(f)
            except Exception as e:
                raise ConfigError(f"Failed to load config: {e}")
        # Defaults
        return {
            "mode": "local",  # or "cloud"
            "save_path": "game_state.json",
            "cloud_storage": None,
        }

    def get(self, key: str, default: Any = None) -> Any:
        return self.data.get(key, default)

    def is_cloud_mode(self) -> bool:
        return self.data.get("mode", "local") == "cloud" 
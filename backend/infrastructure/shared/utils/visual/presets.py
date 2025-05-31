from typing import Dict, Any, List, Optional
import datetime

class CharacterPresetManager:
    """
    Manages character customization presets, including CRUD operations and metadata.
    """
    def __init__(self):
        self.presets: Dict[str, Dict[str, Any]] = {}  # preset_id -> preset data

    def create_preset(self, name: str, customization: Dict[str, Any], tags: Optional[List[str]] = None) -> str:
        preset_id = f"preset_{len(self.presets) + 1}"
        self.presets[preset_id] = {
            "name": name,
            "customization": customization,
            "tags": tags or [],
            "created": datetime.datetime.utcnow().isoformat(),
            "modified": datetime.datetime.utcnow().isoformat(),
        }
        return preset_id

    def get_preset(self, preset_id: str) -> Optional[Dict[str, Any]]:
        return self.presets.get(preset_id)

    def update_preset(self, preset_id: str, customization: Dict[str, Any]):
        if preset_id in self.presets:
            self.presets[preset_id]["customization"] = customization
            self.presets[preset_id]["modified"] = datetime.datetime.utcnow().isoformat()

    def delete_preset(self, preset_id: str):
        if preset_id in self.presets:
            del self.presets[preset_id]

    def list_presets(self, tag: Optional[str] = None) -> List[Dict[str, Any]]:
        if tag:
            return [p for p in self.presets.values() if tag in p["tags"]]
        return list(self.presets.values()) 
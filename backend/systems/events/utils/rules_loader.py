import os
import json
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RulesLoader:
    def __init__(self):
        # Set base_path to app/data/rules
        workspace_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
        self.base_path = os.path.join(workspace_root, "app/data/rules")
        self.game_rules_path = os.path.join(workspace_root, "visual_client/game/rules")
        self.cache = {}
        self._races = None
        self._feats = None
        self._skills = None
        self._attributes = None
        self._kits = None
        
    def _load_json_file(self, filename: str, use_game_rules=False) -> dict:
        """Load a JSON file from the rules directory."""
        path = os.path.join(self.game_rules_path if use_game_rules else self.base_path, filename)
        if not os.path.exists(path):
            logger.warning(f"File not found: {path}")
            return {}
            
        try:
            with open(path, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading {filename}: {e}")
            return {}
            
    def _extract_named_pairs(self, data: dict) -> list:
        """Extract name-description pairs from JSON data."""
        if isinstance(data, dict):
            return [(name, info.get("description", "")) for name, info in data.items()]
        elif isinstance(data, list):
            return [(entry.get("name", "Unnamed"), entry.get("description", "")) for entry in data]
        else:
            return []
            
    def get_races(self) -> list:
        """Get list of races with descriptions."""
        if not self._races:
            races_data = self._load_json_file("races.json")
            self._races = [(name, data.get("description", "")) for name, data in races_data.items()]
        return self._races
        
    def get_race_data(self, race_name):
        races_data = self._load_json_file("races.json")
        return races_data.get(race_name, {})
        
    def get_feats(self) -> list:
        """Get list of feats with descriptions."""
        if "feats" not in self.cache:
            feats_data = self._load_json_file("feats.json", use_game_rules=True)
            if isinstance(feats_data, list):
                self.cache["feats"] = [(feat["name"], feat.get("description", "")) for feat in feats_data]
            else:
                self.cache["feats"] = self._extract_named_pairs(feats_data)
        return self.cache["feats"]
        
    def get_skills(self) -> list:
        """Get list of skills with descriptions."""
        if "skills" not in self.cache:
            self.cache["skills"] = self._extract_named_pairs(self._load_json_file("skills.json"))
        return self.cache["skills"]
        
    def get_backgrounds(self) -> list:
        """Get list of backgrounds with descriptions."""
        if "backgrounds" not in self.cache:
            self.cache["backgrounds"] = self._extract_named_pairs(self._load_json_file("backgrounds.json"))
        return self.cache["backgrounds"]
        
    def get_kits(self) -> list:
        """Get list of starter kits with descriptions."""
        if "kits" not in self.cache:
            self.cache["kits"] = self._extract_named_pairs(self._load_json_file("starter_kits.json"))
        return self.cache["kits"]
        
    def get_skill_data(self, skill_name: str) -> dict:
        """Get detailed data for a specific skill."""
        if "skills_data" not in self.cache:
            self.cache["skills_data"] = self._load_json_file("skills.json")
        return self.cache["skills_data"].get(skill_name, {})

    def get_feat_data(self, feat_name: str) -> dict:
        """Get detailed data for a specific feat."""
        if "feats_data" not in self.cache:
            feats_data = self._load_json_file("feats.json", use_game_rules=True)
            if isinstance(feats_data, list):
                self.cache["feats_data"] = {feat["name"]: feat for feat in feats_data}
            else:
                self.cache["feats_data"] = feats_data
        return self.cache["feats_data"].get(feat_name, {})


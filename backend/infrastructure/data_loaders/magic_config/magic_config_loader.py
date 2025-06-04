"""
Magic System Configuration Loader

This module handles loading and validating magic system configuration from JSON files.
Separated from business logic to isolate file I/O and technical concerns.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from functools import lru_cache


class MagicConfigLoader:
    """Handles loading magic system configuration from JSON files"""
    
    def __init__(self, config_base_path: Optional[Path] = None):
        """Initialize with config path"""
        if config_base_path is None:
            # Default to data/systems/magic
            self.config_path = Path(__file__).parent.parent.parent.parent.parent / "data" / "systems" / "magic"
        else:
            self.config_path = config_base_path
        
        self._spells_cache = None
        self._domains_cache = None
        self._combat_rules_cache = None
        self._concentration_rules_cache = None
    
    def _load_json_file(self, filename: str) -> Dict[str, Any]:
        """Load and parse a JSON file"""
        file_path = self.config_path / filename
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Magic config file not found: {file_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in magic config file {filename}: {e}")
    
    @lru_cache(maxsize=1)
    def load_spells(self) -> Dict[str, Any]:
        """Load spell definitions from JSON"""
        if self._spells_cache is None:
            data = self._load_json_file("spells.json")
            self._spells_cache = data.get("spells", {})
        return self._spells_cache
    
    @lru_cache(maxsize=1)
    def load_magic_domains(self) -> Dict[str, Any]:
        """Load magic domain definitions from JSON"""
        if self._domains_cache is None:
            data = self._load_json_file("magic_domains.json")
            self._domains_cache = data.get("magic_domains", {})
        return self._domains_cache
    
    @lru_cache(maxsize=1)
    def load_combat_rules(self) -> Dict[str, Any]:
        """Load spell school combat rules from JSON"""
        if self._combat_rules_cache is None:
            data = self._load_json_file("spell_school_combat_rules.json")
            self._combat_rules_cache = data.get("spell_school_combat_rules", {})
        return self._combat_rules_cache
    
    @lru_cache(maxsize=1)
    def load_concentration_rules(self) -> Dict[str, Any]:
        """Load concentration rules from JSON"""
        if self._concentration_rules_cache is None:
            data = self._load_json_file("concentration_rules.json")
            self._concentration_rules_cache = data.get("concentration_rules", {})
        return self._concentration_rules_cache
    
    def reload_all_configs(self):
        """Clear cache and reload all configurations"""
        self._spells_cache = None
        self._domains_cache = None
        self._combat_rules_cache = None
        self._concentration_rules_cache = None
        # Clear LRU cache
        self.load_spells.cache_clear()
        self.load_magic_domains.cache_clear()
        self.load_combat_rules.cache_clear()
        self.load_concentration_rules.cache_clear()
    
    def validate_configs(self) -> List[str]:
        """Validate all magic configurations and return any errors"""
        errors = []
        
        try:
            spells = self.load_spells()
            if not isinstance(spells, dict):
                errors.append("Spells configuration is not a dictionary")
        except Exception as e:
            errors.append(f"Failed to load spells: {e}")
        
        try:
            domains = self.load_magic_domains()
            if not isinstance(domains, dict):
                errors.append("Magic domains configuration is not a dictionary")
        except Exception as e:
            errors.append(f"Failed to load magic domains: {e}")
        
        try:
            combat_rules = self.load_combat_rules()
            if not isinstance(combat_rules, dict):
                errors.append("Combat rules configuration is not a dictionary")
        except Exception as e:
            errors.append(f"Failed to load combat rules: {e}")
        
        try:
            concentration_rules = self.load_concentration_rules()
            if not isinstance(concentration_rules, dict):
                errors.append("Concentration rules configuration is not a dictionary")
        except Exception as e:
            errors.append(f"Failed to load concentration rules: {e}")
        
        return errors
    
    def get_spell(self, spell_name: str) -> Optional[Dict[str, Any]]:
        """Get a specific spell configuration"""
        spells = self.load_spells()
        return spells.get(spell_name)
    
    def get_domain(self, domain_name: str) -> Optional[Dict[str, Any]]:
        """Get a specific magic domain configuration"""
        domains = self.load_magic_domains()
        return domains.get(domain_name)
    
    def list_spells(self) -> List[str]:
        """Get list of all available spell names"""
        spells = self.load_spells()
        return list(spells.keys())
    
    def list_domains(self) -> List[str]:
        """Get list of all available domain names"""
        domains = self.load_magic_domains()
        return list(domains.keys())


# Global instance for easy access
_magic_config_loader = None

def get_magic_config_loader() -> MagicConfigLoader:
    """Get the global magic configuration loader instance"""
    global _magic_config_loader
    if _magic_config_loader is None:
        _magic_config_loader = MagicConfigLoader()
    return _magic_config_loader

def create_magic_config_loader(config_path: Optional[Path] = None) -> MagicConfigLoader:
    """Create a new magic configuration loader instance"""
    return MagicConfigLoader(config_path) 
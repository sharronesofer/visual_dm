"""
Configuration loader for arc system JSON configurations.
Loads templates, mappings, and business rules from the new multi-tier directory structure.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from functools import lru_cache

logger = logging.getLogger(__name__)

class ArcConfigLoader:
    """Utility class for loading JSON configuration files from multi-tier structure"""
    
    def __init__(self, project_root: Optional[str] = None):
        """Initialize the config loader
        
        Args:
            project_root: Path to the project root directory (auto-detected if not provided)
        """
        if project_root:
            self.project_root = Path(project_root)
        else:
            # Find project root by looking for common project files
            current_dir = Path(__file__).resolve()
            self.project_root = self._find_project_root(current_dir)
        
        # Set up the new multi-tier structure paths
        self.data_root = self.project_root / "data"
        self.public_dir = self.data_root / "public"
        self.system_dir = self.data_root / "system"
        
        # Specific template directories
        self.arc_templates_dir = self.public_dir / "templates" / "arc"
        self.quest_templates_dir = self.public_dir / "templates" / "quest"
        self.arc_config_dir = self.system_dir / "config" / "arc"
        
        logger.info(f"ArcConfigLoader initialized with multi-tier structure:")
        logger.info(f"  Public templates: {self.public_dir}")
        logger.info(f"  System config: {self.system_dir}")
    
    def _find_project_root(self, start_path: Path) -> Path:
        """Find the project root directory by looking for marker files"""
        markers = [".git", "requirements.txt", "pyproject.toml", ".gitignore", "data"]
        
        current = start_path
        while current != current.parent:
            if any((current / marker).exists() for marker in markers):
                return current
            current = current.parent
        
        # Fallback to start_path if no markers found
        logger.warning(f"Could not find project root, using {start_path}")
        return start_path
    
    @lru_cache(maxsize=20)
    def load_config(self, config_name: str, config_type: str = "auto") -> Dict[str, Any]:
        """Load a configuration file by name and type
        
        Args:
            config_name: Name of the config file (without .json extension)
            config_type: Type of config ('public', 'system', 'auto')
            
        Returns:
            Dict containing the configuration data
            
        Raises:
            FileNotFoundError: If the config file doesn't exist
            json.JSONDecodeError: If the config file is invalid JSON
        """
        config_path = self._resolve_config_path(config_name, config_type)
        
        if not config_path.exists():
            logger.error(f"Configuration file not found: {config_path}")
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        try:
            with open(config_path, 'r', encoding='utf-8') as file:
                config_data = json.load(file)
                logger.info(f"Loaded configuration: {config_name} from {config_path}")
                return config_data
                
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in configuration file {config_path}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error loading configuration file {config_path}: {e}")
            raise
    
    def _resolve_config_path(self, config_name: str, config_type: str) -> Path:
        """Resolve the path to a configuration file based on its type"""
        
        # Auto-detection based on config name
        if config_type == "auto":
            if config_name == "arc_templates":
                return self.arc_templates_dir / f"{config_name}.json"
            elif config_name == "quest_tag_mappings":
                return self.quest_templates_dir / f"{config_name}.json"
            elif config_name == "arc_business_rules":
                return self.arc_config_dir / f"{config_name}.json"
            else:
                # Default to system config for unknown configs
                return self.arc_config_dir / f"{config_name}.json"
        
        # Explicit type specification
        elif config_type == "public":
            if config_name.startswith("arc_"):
                return self.arc_templates_dir / f"{config_name}.json"
            elif config_name.startswith("quest_"):
                return self.quest_templates_dir / f"{config_name}.json"
            else:
                return self.public_dir / f"{config_name}.json"
        
        elif config_type == "system":
            return self.arc_config_dir / f"{config_name}.json"
        
        else:
            raise ValueError(f"Unknown config type: {config_type}")
    
    def load_arc_templates(self) -> Dict[str, Any]:
        """Load arc templates configuration (public/builder-modifiable)"""
        config = self.load_config("arc_templates", "public")
        return config.get("templates", {})
    
    def load_quest_tag_mappings(self) -> Dict[str, Any]:
        """Load quest tag mappings configuration (public/builder-modifiable)"""
        return self.load_config("quest_tag_mappings", "public")
    
    def load_business_rules(self) -> Dict[str, Any]:
        """Load business rules configuration (system internal)"""
        return self.load_config("arc_business_rules", "system")
    
    def get_tag_mappings(self) -> Dict[str, list]:
        """Get the tag mappings for quest generation"""
        config = self.load_quest_tag_mappings()
        return config.get("tag_mappings", {})
    
    def get_keyword_mappings(self) -> Dict[str, list]:
        """Get the keyword mappings for tag extraction"""
        config = self.load_quest_tag_mappings()
        return config.get("keyword_mappings", {})
    
    def get_quest_templates(self) -> Dict[str, Any]:
        """Get the quest templates for quest generation"""
        config = self.load_quest_tag_mappings()
        return config.get("quest_templates", {})
    
    def get_validation_rules(self) -> Dict[str, Any]:
        """Get validation rules for arcs (system internal)"""
        config = self.load_business_rules()
        return config.get("validation_rules", {})
    
    def get_defaults(self) -> Dict[str, Any]:
        """Get default values for arc creation (system internal)"""
        config = self.load_business_rules()
        return config.get("defaults", {})
    
    def get_progression_rules(self) -> Dict[str, Any]:
        """Get progression rules for arc tracking (system internal)"""
        config = self.load_business_rules()
        return config.get("progression_rules", {})
    
    def get_generation_settings(self) -> Dict[str, Any]:
        """Get settings for arc generation (system internal)"""
        config = self.load_business_rules()
        return config.get("generation_settings", {})
    
    def get_integration_rules(self) -> Dict[str, Any]:
        """Get integration rules for cross-system functionality (system internal)"""
        config = self.load_business_rules()
        return config.get("integration_rules", {})
    
    def get_security_settings(self) -> Dict[str, Any]:
        """Get security settings (system internal)"""
        config = self.load_business_rules()
        return config.get("security_settings", {})
    
    def reload_all(self) -> None:
        """Clear the cache and reload all configurations"""
        self.load_config.cache_clear()
        logger.info("Cleared configuration cache")
    
    def list_available_configs(self) -> Dict[str, list]:
        """List all available configuration files by type"""
        configs = {
            "public": [],
            "system": []
        }
        
        # Public configs
        if self.arc_templates_dir.exists():
            configs["public"].extend([f.stem for f in self.arc_templates_dir.glob("*.json")])
        if self.quest_templates_dir.exists():
            configs["public"].extend([f.stem for f in self.quest_templates_dir.glob("*.json")])
        
        # System configs
        if self.arc_config_dir.exists():
            configs["system"].extend([f.stem for f in self.arc_config_dir.glob("*.json")])
        
        return configs
    
    def validate_config_files(self) -> Dict[str, bool]:
        """Validate that all expected configuration files exist and are valid JSON"""
        results = {}
        
        expected_configs = [
            ("arc_templates", "public"),
            ("quest_tag_mappings", "public"),
            ("arc_business_rules", "system")
        ]
        
        for config_name, config_type in expected_configs:
            try:
                self.load_config(config_name, config_type)
                results[config_name] = True
            except Exception as e:
                logger.error(f"Validation failed for {config_name}: {e}")
                results[config_name] = False
        
        return results
    
    def get_access_level(self, config_name: str) -> str:
        """Get the access level for a configuration file"""
        if config_name.startswith("arc_templates") or config_name.startswith("quest_tag_mappings"):
            return "public"
        else:
            return "system"

# Global instance for backward compatibility
arc_config_loader = ArcConfigLoader()

# Convenience functions
def load_arc_templates() -> Dict[str, Any]:
    """Load arc templates from configuration"""
    return arc_config_loader.load_arc_templates()

def load_tag_mappings() -> Dict[str, Any]:
    """Load tag mappings from configuration"""
    return arc_config_loader.get_tag_mappings()

def load_business_rules() -> Dict[str, Any]:
    """Load business rules from configuration"""
    return arc_config_loader.load_business_rules()

def validate_all_configs() -> Dict[str, bool]:
    """Validate all configuration files"""
    return arc_config_loader.validate_config_files() 
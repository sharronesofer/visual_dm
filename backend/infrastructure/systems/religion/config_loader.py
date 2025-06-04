"""
Religion System Configuration Loader - Technical Infrastructure

This module handles the technical aspects of loading religion system configuration
files from JSON data sources. This is infrastructure code that handles I/O operations.
"""

import logging
import json
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
import random

logger = logging.getLogger(__name__)

def load_religion_config(filename: str, fallback_data: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Load religion configuration file with fallback to hardcoded data.
    
    Args:
        filename: Name of the JSON file to load
        fallback_data: Fallback data if file doesn't exist
    
    Returns:
        Configuration dictionary
    """
    try:
        # Try to load from data/systems/religion/ first
        config_path = Path("data/systems/religion") / filename
        if config_path.exists():
            with open(config_path, 'r') as f:
                data = json.load(f)
                logger.info(f"Loaded religion config from {config_path}")
                return data
        
        # Try infrastructure data loading if available
        try:
            from backend.infrastructure.datautils import load_data
            data = load_data(filename)
            logger.info(f"Loaded religion config from infrastructure: {filename}")
            return data
        except (ImportError, FileNotFoundError, json.JSONDecodeError):
            pass
            
    except Exception as e:
        logger.warning(f"Could not load religion config {filename}: {e}")
    
    # Return fallback data or empty dict
    if fallback_data:
        logger.info(f"Using fallback data for {filename}")
        return fallback_data
    else:
        logger.warning(f"No fallback data available for {filename}, returning empty dict")
        return {}

def reload_all_religion_configs() -> Dict[str, Dict[str, Any]]:
    """
    Reload all religion configuration files.
    
    Returns:
        Dictionary containing all loaded configurations
    """
    logger.info("Reloading religion configuration...")
    
    configs = {
        "religion_config": load_religion_config("religion_config.json"),
        "narrative_templates": load_religion_config("narrative_templates.json"),
        "influence_rules": load_religion_config("influence_rules.json"), 
        "practices_templates": load_religion_config("practices_templates.json")
    }
    
    logger.info("Religion configuration reloaded successfully")
    return configs

def validate_religion_config(configs: Dict[str, Dict[str, Any]]) -> Dict[str, List[str]]:
    """
    Validate the loaded configuration for completeness and consistency.
    
    Args:
        configs: Dictionary of loaded configurations
        
    Returns:
        Dictionary of validation errors by config file
    """
    errors = {
        "religion_config": [],
        "narrative_templates": [],
        "influence_rules": [],
        "practices_templates": []
    }
    
    religion_config = configs.get("religion_config", {})
    narrative_templates = configs.get("narrative_templates", {})
    influence_rules = configs.get("influence_rules", {})
    practices_templates = configs.get("practices_templates", {})
    
    # Validate religion_config
    if not religion_config:
        errors["religion_config"].append("Configuration file not loaded")
    else:
        if "religion_types" not in religion_config:
            errors["religion_config"].append("Missing religion_types section")
        if "devotion_modifiers" not in religion_config:
            errors["religion_config"].append("Missing devotion_modifiers section")
        if "compatibility_factors" not in religion_config:
            errors["religion_config"].append("Missing compatibility_factors section")
    
    # Validate narrative_templates
    if not narrative_templates:
        errors["narrative_templates"].append("Configuration file not loaded")
    else:
        required_sections = ["conversion_templates", "devotion_change_narratives", "religious_event_templates"]
        for section in required_sections:
            if section not in narrative_templates:
                errors["narrative_templates"].append(f"Missing {section} section")
    
    # Validate influence_rules
    if not influence_rules:
        errors["influence_rules"].append("Configuration file not loaded")
    else:
        required_sections = ["spread_mechanics", "influence_calculations", "regional_modifiers"]
        for section in required_sections:
            if section not in influence_rules:
                errors["influence_rules"].append(f"Missing {section} section")
    
    # Validate practices_templates
    if not practices_templates:
        errors["practices_templates"].append("Configuration file not loaded")
    else:
        required_sections = ["practice_templates", "festival_templates"]
        for section in required_sections:
            if section not in practices_templates:
                errors["practices_templates"].append(f"Missing {section} section")
    
    return {k: v for k, v in errors.items() if v}  # Only return sections with errors

def format_narrative_template(
    template: str, 
    format_kwargs: Dict[str, Any]
) -> str:
    """
    Format a narrative template with provided variables.
    Technical utility for template formatting.
    
    Args:
        template: Template string with format placeholders
        format_kwargs: Variables to format into the template
        
    Returns:
        Formatted narrative string
    """
    try:
        return template.format(**format_kwargs)
    except KeyError as e:
        logger.warning(f"Missing format key {e} for template: {template}")
        return template

def select_random_template(templates: List[str]) -> str:
    """
    Select a random template from a list.
    Technical utility for template selection.
    
    Args:
        templates: List of template strings
        
    Returns:
        Randomly selected template
    """
    if not templates:
        return "A generic event occurred."
    return random.choice(templates)

__all__ = [
    "load_religion_config",
    "reload_all_religion_configs", 
    "validate_religion_config",
    "format_narrative_template",
    "select_random_template"
] 
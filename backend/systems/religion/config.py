"""
Religion System Configuration - Business Logic

This module provides business logic configuration services for the religion system.
Technical infrastructure components for loading JSON have been moved to 
backend.infrastructure.systems.religion.config_loader.
"""

import logging
from typing import Dict, Any, List, Optional, Union
import random

# Import technical infrastructure for config loading
try:
    from backend.infrastructure.systems.religion.config_loader import (
        load_religion_config,
        reload_all_religion_configs,
        validate_religion_config as validate_config_technical,
        format_narrative_template,
        select_random_template
    )
    HAS_CONFIG_LOADER = True
except ImportError:
    HAS_CONFIG_LOADER = False

logger = logging.getLogger(__name__)

# Load all religion configurations via infrastructure
if HAS_CONFIG_LOADER:
    configs = reload_all_religion_configs()
    religion_config = configs["religion_config"]
    narrative_templates = configs["narrative_templates"]
    influence_rules = configs["influence_rules"]
    practices_templates = configs["practices_templates"]
else:
    religion_config = {}
    narrative_templates = {}
    influence_rules = {}
    practices_templates = {}

# Religion type constants (simple string constants, no complex enum)
RELIGION_TYPES = {
    "MONOTHEISTIC": "monotheistic",
    "POLYTHEISTIC": "polytheistic", 
    "ANIMISTIC": "animistic",
    "DUALISTIC": "dualistic",
    "ANCESTOR_WORSHIP": "ancestor_worship"
}

def get_religion_types() -> Dict[str, Dict[str, Any]]:
    """Get all available religion types from configuration"""
    if religion_config and "religion_types" in religion_config:
        return religion_config["religion_types"]
    
    # Fallback data
    return {
        "monotheistic": {
            "name": "Monotheistic",
            "description": "Worship of a single deity",
            "compatibility_base": 0.2,
            "conversion_difficulty": 0.8,
            "schism_resistance": 0.9,
            "influence_spread_rate": 0.6
        },
        "polytheistic": {
            "name": "Polytheistic", 
            "description": "Worship of multiple deities",
            "compatibility_base": 0.6,
            "conversion_difficulty": 0.4,
            "schism_resistance": 0.5,
            "influence_spread_rate": 0.8
        },
        "animistic": {
            "name": "Animistic",
            "description": "Belief in spiritual forces in nature",
            "compatibility_base": 0.7,
            "conversion_difficulty": 0.3,
            "schism_resistance": 0.3,
            "influence_spread_rate": 0.9
        }
    }

def get_religion_type_info(religion_type: str) -> Dict[str, Any]:
    """
    Get information about a specific religion type.
    
    Args:
        religion_type: Type of religion (e.g., 'monotheistic')
        
    Returns:
        Religion type configuration dictionary
    """
    types_config = get_religion_types()
    return types_config.get(religion_type, {
        "name": religion_type.title(),
        "description": f"A {religion_type} religion",
        "compatibility_base": 0.5,
        "conversion_difficulty": 0.5,
        "schism_resistance": 0.5,
        "influence_spread_rate": 0.5
    })

def get_devotion_modifiers() -> Dict[str, Dict[str, Any]]:
    """Get devotion modifier configuration"""
    if religion_config and "devotion_modifiers" in religion_config:
        return religion_config["devotion_modifiers"]
    
    # Fallback data
    return {
        "prayer": {"base_change": 0.05, "max_per_day": 0.15},
        "ritual": {"base_change": 0.1, "max_per_day": 0.3},
        "pilgrimage": {"base_change": 0.2, "cooldown_days": 30},
        "transgression": {"base_change": -0.15, "severity_multiplier": 2.0},
        "doubt": {"base_change": -0.05, "compound_rate": 1.1}
    }

def get_compatibility_factors() -> Dict[str, float]:
    """Get religion compatibility factors"""
    if religion_config and "compatibility_factors" in religion_config:
        return religion_config["compatibility_factors"]
    
    # Fallback data
    return {
        "same_type": 0.3,
        "shared_deities": 0.4,
        "conflicting_tenets": -0.6,
        "historical_conflict": -0.8,
        "cultural_similarity": 0.2
    }

def calculate_devotion_change(
    current_devotion: float,
    action_type: str,
    intensity: float = 1.0,
    **kwargs
) -> float:
    """
    Calculate devotion level changes based on actions using configuration.
    Business logic for devotion calculations.
    
    Args:
        current_devotion: Current devotion level (0.0 to 1.0)
        action_type: Type of action affecting devotion
        intensity: Intensity multiplier for the change
        **kwargs: Additional parameters (e.g., severity for transgressions)
        
    Returns:
        New devotion level
    """
    modifiers = get_devotion_modifiers()
    
    if action_type not in modifiers:
        logger.warning(f"Unknown devotion action type: {action_type}")
        return current_devotion
    
    modifier_config = modifiers[action_type]
    base_change = modifier_config.get("base_change", 0.0)
    
    # Apply intensity
    change = base_change * intensity
    
    # Apply special modifiers
    if "severity_multiplier" in modifier_config and "severity" in kwargs:
        change *= modifier_config["severity_multiplier"] * kwargs["severity"]
    
    if "compound_rate" in modifier_config and current_devotion > 0:
        change *= modifier_config["compound_rate"]
    
    # Calculate new devotion with bounds
    new_devotion = max(0.0, min(1.0, current_devotion + change))
    
    return new_devotion

def check_religion_compatibility(
    religion1_type: str, 
    religion2_type: str,
    shared_factors: Optional[List[str]] = None,
    conflict_factors: Optional[List[str]] = None
) -> float:
    """
    Check compatibility between two religions using configuration.
    Business logic for religion compatibility calculations.
    
    Args:
        religion1_type: Type of first religion
        religion2_type: Type of second religion
        shared_factors: List of shared factors (e.g., shared_deities)
        conflict_factors: List of conflict factors (e.g., historical_conflict)
        
    Returns:
        Compatibility score (0.0 to 1.0)
    """
    types_config = get_religion_types()
    compatibility_factors = get_compatibility_factors()
    
    religion1_info = get_religion_type_info(religion1_type)
    religion2_info = get_religion_type_info(religion2_type)
    
    # Start with base compatibility for the types
    base_compat = (religion1_info.get("compatibility_base", 0.5) + 
                   religion2_info.get("compatibility_base", 0.5)) / 2
    
    # Apply same type bonus
    if religion1_type == religion2_type:
        base_compat += compatibility_factors.get("same_type", 0.0)
    
    # Apply shared factors
    if shared_factors:
        for factor in shared_factors:
            if factor in compatibility_factors:
                base_compat += compatibility_factors[factor]
    
    # Apply conflict factors  
    if conflict_factors:
        for factor in conflict_factors:
            if factor in compatibility_factors:
                base_compat += compatibility_factors[factor]  # These should be negative
    
    # Ensure result is within bounds
    return max(0.0, min(1.0, base_compat))

def get_narrative_template(
    template_type: str, 
    category: str,
    subcategory: Optional[str] = None,
    **format_kwargs
) -> str:
    """
    Get a narrative template from configuration and format it.
    Business logic for narrative generation.
    
    Args:
        template_type: Type of template (e.g., 'conversion_templates')
        category: Category within the type (e.g., 'voluntary')
        subcategory: Optional subcategory (e.g., for devotion narratives: action type)
        **format_kwargs: Variables to format into the template
        
    Returns:
        Formatted narrative string
    """
    if subcategory:
        # For nested templates like devotion_change_narratives -> increase -> prayer
        templates = narrative_templates.get(template_type, {}).get(category, {}).get(subcategory, [])
    else:
        # For flat templates like conversion_templates -> voluntary
        templates = narrative_templates.get(template_type, {}).get(category, [])
    
    if not templates:
        return f"A {category} {template_type.replace('_templates', '')} occurred."
    
    # Use infrastructure for template selection and formatting
    if HAS_CONFIG_LOADER:
        template = select_random_template(templates)
        return format_narrative_template(template, format_kwargs)
    else:
        # Fallback without infrastructure
        template = random.choice(templates)
        try:
            return template.format(**format_kwargs)
        except KeyError as e:
            logger.warning(f"Missing format key {e} for template: {template}")
            return template

def get_regional_modifier(region_type: str, modifier_type: str) -> float:
    """
    Get regional modifier from influence rules configuration.
    Business logic for regional influence calculations.
    
    Args:
        region_type: Type of region (e.g., 'urban', 'rural')
        modifier_type: Type of modifier (e.g., 'spread_rate', 'resistance')
        
    Returns:
        Modifier value
    """
    regional_modifiers = influence_rules.get("regional_modifiers", {})
    
    if region_type not in regional_modifiers:
        return 1.0  # Default neutral modifier
    
    return regional_modifiers[region_type].get(modifier_type, 1.0)

def get_practice_template(frequency: str, practice_name: str) -> Dict[str, Any]:
    """
    Get a religious practice template from configuration.
    Business logic for practice template retrieval.
    
    Args:
        frequency: Practice frequency (e.g., 'daily', 'weekly')
        practice_name: Name of the practice
        
    Returns:
        Practice configuration dictionary
    """
    practice_templates_config = practices_templates.get("practice_templates", {})
    frequency_practices = practice_templates_config.get(frequency, {})
    
    return frequency_practices.get(practice_name, {})

def get_festival_template(festival_name: str) -> Dict[str, Any]:
    """
    Get a festival template from configuration.
    Business logic for festival template retrieval.
    
    Args:
        festival_name: Name of the festival
        
    Returns:
        Festival configuration dictionary
    """
    festival_templates_config = practices_templates.get("festival_templates", {})
    return festival_templates_config.get(festival_name, {})

def reload_religion_config():
    """Reload all religion configuration files via infrastructure."""
    global religion_config, narrative_templates, influence_rules, practices_templates
    
    if not HAS_CONFIG_LOADER:
        logger.warning("Config loader infrastructure not available")
        return
    
    logger.info("Reloading religion configuration...")
    
    # Reload all configs via infrastructure
    configs = reload_all_religion_configs()
    religion_config = configs["religion_config"]
    narrative_templates = configs["narrative_templates"]
    influence_rules = configs["influence_rules"]
    practices_templates = configs["practices_templates"]
    
    logger.info("Religion configuration reloaded successfully")

def validate_config() -> Dict[str, List[str]]:
    """
    Validate the loaded configuration for completeness and consistency.
    Business logic wrapper around infrastructure validation.
    
    Returns:
        Dictionary of validation errors by config file
    """
    if not HAS_CONFIG_LOADER:
        return {"infrastructure": ["Config loader infrastructure not available"]}
    
    configs = {
        "religion_config": religion_config,
        "narrative_templates": narrative_templates,
        "influence_rules": influence_rules,
        "practices_templates": practices_templates
    }
    
    return validate_config_technical(configs)

__all__ = [
    "RELIGION_TYPES",
    "religion_config",
    "narrative_templates", 
    "influence_rules",
    "practices_templates",
    "get_religion_types",
    "get_religion_type_info",
    "get_devotion_modifiers",
    "get_compatibility_factors",
    "calculate_devotion_change",
    "check_religion_compatibility",
    "get_narrative_template",
    "get_regional_modifier",
    "get_practice_template",
    "get_festival_template",
    "reload_religion_config",
    "validate_config"
] 
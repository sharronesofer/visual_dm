"""
Config validation utility for motif system.

Validates motif_config.json against code models and enum definitions.
"""

import json
from typing import Dict, List, Set, Tuple
from pathlib import Path

from backend.infrastructure.systems.motif.models import MotifCategory, MotifScope, MotifLifecycle


def load_motif_config() -> Dict:
    """Load the motif configuration file."""
    config_path = Path("data/systems/motif/motif_config.json")
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Motif config not found at {config_path}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in motif config: {e}")


def validate_motif_categories(config: Dict) -> List[str]:
    """Validate that all motif categories in code have config entries."""
    errors = []
    
    # Get all categories from code
    code_categories = set(category.value.upper() for category in MotifCategory)
    
    # Get categories from action mapping
    action_mapping = config.get("action_to_motif_mapping", {})
    mapped_categories = set(action_mapping.values())
    
    # Get categories from name generation
    name_generation = config.get("name_generation", {})
    name_gen_categories = set(name_generation.keys())
    
    # Check for missing categories in action mapping
    missing_from_action = code_categories - mapped_categories
    if missing_from_action:
        errors.append(f"Missing motif categories in action_to_motif_mapping: {missing_from_action}")
    
    # Check for missing categories in name generation
    missing_from_names = code_categories - name_gen_categories
    if missing_from_names:
        errors.append(f"Missing motif categories in name_generation: {missing_from_names}")
    
    # Check for extra categories in config
    extra_in_action = mapped_categories - code_categories
    if extra_in_action:
        errors.append(f"Extra motif categories in action_to_motif_mapping: {extra_in_action}")
    
    extra_in_names = name_gen_categories - code_categories
    if extra_in_names:
        errors.append(f"Extra motif categories in name_generation: {extra_in_names}")
    
    return errors


def validate_theme_relationships(config: Dict) -> List[str]:
    """Validate theme relationships are logically consistent."""
    errors = []
    
    theme_relationships = config.get("theme_relationships", {})
    opposing_pairs = theme_relationships.get("opposing_pairs", [])
    complementary_pairs = theme_relationships.get("complementary_pairs", [])
    
    # Check for themes that appear in both opposing and complementary
    opposing_themes = set()
    complementary_themes = set()
    
    for pair in opposing_pairs:
        if len(pair) == 2:
            opposing_themes.update(pair)
            # Check for conflicts within the same pair
            if pair[0] == pair[1]:
                errors.append(f"Theme cannot oppose itself: {pair[0]}")
    
    for pair in complementary_pairs:
        if len(pair) == 2:
            complementary_themes.update(pair)
            # Check for conflicts within the same pair
            if pair[0] == pair[1]:
                errors.append(f"Theme cannot complement itself: {pair[0]}")
    
    # Check for overlapping opposing and complementary relationships
    # Note: This is actually allowed in some cases (e.g., "darkness" can oppose "light" but complement "mystery")
    # So we'll just warn about direct conflicts
    
    # Check for duplicate pairs
    opposing_normalized = [tuple(sorted(pair)) for pair in opposing_pairs if len(pair) == 2]
    if len(opposing_normalized) != len(set(opposing_normalized)):
        errors.append("Duplicate opposing pairs found")
    
    complementary_normalized = [tuple(sorted(pair)) for pair in complementary_pairs if len(pair) == 2]
    if len(complementary_normalized) != len(set(complementary_normalized)):
        errors.append("Duplicate complementary pairs found")
    
    return errors


def validate_chaos_events(config: Dict) -> List[str]:
    """Validate chaos events are properly structured."""
    errors = []
    
    chaos_events = config.get("chaos_events", {})
    
    # Check that all categories have events
    for category, events in chaos_events.items():
        if not isinstance(events, list):
            errors.append(f"Chaos events for category '{category}' must be a list")
            continue
        
        if not events:
            errors.append(f"Chaos events category '{category}' is empty")
            continue
        
        # Check that all events are strings
        for i, event in enumerate(events):
            if not isinstance(event, str):
                errors.append(f"Chaos event {i} in category '{category}' must be a string")
            elif not event.strip():
                errors.append(f"Chaos event {i} in category '{category}' is empty")
    
    return errors


def validate_name_generation(config: Dict) -> List[str]:
    """Validate name generation templates are complete."""
    errors = []
    
    name_generation = config.get("name_generation", {})
    
    for category, templates in name_generation.items():
        if not isinstance(templates, dict):
            errors.append(f"Name generation for category '{category}' must be a dict")
            continue
        
        # Check required fields
        if "base_names" not in templates:
            errors.append(f"Missing 'base_names' for category '{category}'")
        elif not isinstance(templates["base_names"], list) or not templates["base_names"]:
            errors.append(f"'base_names' for category '{category}' must be a non-empty list")
        
        if "modifiers" not in templates:
            errors.append(f"Missing 'modifiers' for category '{category}'")
        elif not isinstance(templates["modifiers"], list) or not templates["modifiers"]:
            errors.append(f"'modifiers' for category '{category}' must be a non-empty list")
    
    return errors


def validate_settings(config: Dict) -> List[str]:
    """Validate settings are within reasonable ranges."""
    errors = []
    
    settings = config.get("settings", {})
    
    # Check required settings
    required_settings = [
        "default_chaos_weight",
        "max_concurrent_motifs_per_region",
        "motif_decay_rate_days",
        "chaos_trigger_threshold",
        "motif_interaction_radius",
        "cache_duration_minutes",
        "default_motif_intensity",
        "max_motif_intensity",
        "min_motif_intensity"
    ]
    
    for setting in required_settings:
        if setting not in settings:
            errors.append(f"Missing required setting: {setting}")
    
    # Validate specific settings
    if "default_motif_intensity" in settings and "min_motif_intensity" in settings and "max_motif_intensity" in settings:
        default_intensity = settings["default_motif_intensity"]
        min_intensity = settings["min_motif_intensity"]
        max_intensity = settings["max_motif_intensity"]
        
        if not (min_intensity <= default_intensity <= max_intensity):
            errors.append(f"default_motif_intensity ({default_intensity}) must be between min ({min_intensity}) and max ({max_intensity})")
    
    # Check reasonable ranges
    checks = [
        ("default_chaos_weight", 0.0, 1.0),
        ("motif_decay_rate_days", 0.0, 1.0),
        ("chaos_trigger_threshold", 1.0, 10.0),
        ("min_motif_intensity", 1, 10),
        ("max_motif_intensity", 1, 10),
        ("default_motif_intensity", 1, 10)
    ]
    
    for setting_name, min_val, max_val in checks:
        if setting_name in settings:
            value = settings[setting_name]
            if not isinstance(value, (int, float)) or not (min_val <= value <= max_val):
                errors.append(f"{setting_name} ({value}) must be between {min_val} and {max_val}")
    
    return errors


def validate_motif_config() -> Tuple[bool, List[str]]:
    """
    Validate the entire motif configuration.
    
    Returns:
        Tuple of (is_valid, error_messages)
    """
    try:
        config = load_motif_config()
    except (FileNotFoundError, ValueError) as e:
        return False, [str(e)]
    
    all_errors = []
    
    # Run all validations
    all_errors.extend(validate_motif_categories(config))
    all_errors.extend(validate_theme_relationships(config))
    all_errors.extend(validate_chaos_events(config))
    all_errors.extend(validate_name_generation(config))
    all_errors.extend(validate_settings(config))
    
    return len(all_errors) == 0, all_errors


def main():
    """Run config validation and print results."""
    is_valid, errors = validate_motif_config()
    
    if is_valid:
        print("✅ Motif configuration is valid!")
    else:
        print("❌ Motif configuration has errors:")
        for error in errors:
            print(f"  - {error}")
    
    return 0 if is_valid else 1


if __name__ == "__main__":
    exit(main()) 
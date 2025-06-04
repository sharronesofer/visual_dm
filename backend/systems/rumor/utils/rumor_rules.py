"""
Rumor System Rules and Configuration
-----------------------------------
Business logic for rumor mechanics, moved from backend.systems.rules.

This module provides rumor-specific configuration and calculation functions
that were previously mixed into the general rules system.
"""

from typing import Dict, Any, Optional, Protocol


# Business Logic Protocols (dependency injection)
class RumorConfigProvider(Protocol):
    """Protocol for rumor configuration loading"""
    
    def load_json_config(self, filename: str, fallback_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Load JSON configuration with fallback"""
        ...


# Default configuration provider (will be injected)
_config_provider: Optional[RumorConfigProvider] = None


def set_rumor_config_provider(provider: RumorConfigProvider) -> None:
    """
    Set the configuration provider for dependency injection.
    
    Args:
        provider: Configuration provider instance
    """
    global _config_provider
    _config_provider = provider


def _get_config(filename: str, fallback_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Get configuration using the injected provider or fallback to empty dict.
    
    Args:
        filename: Configuration file name
        fallback_data: Fallback data if loading fails
        
    Returns:
        Configuration dictionary
    """
    if _config_provider:
        return _config_provider.load_json_config(filename, fallback_data)
    return fallback_data or {}


# Legacy rumor system constants (maintained for backward compatibility)
_legacy_rumor_constants = {
    # Rumor Decay
    "base_decay_rate": 0.05,
    "decay_severity_factors": {
        "trivial": 1.5,   # Decays 50% faster
        "minor": 1.2,     # Decays 20% faster
        "moderate": 1.0,  # Normal decay rate
        "major": 0.8,     # Decays 20% slower
        "critical": 0.6   # Decays 40% slower
    },
    
    # Rumor Mutation
    "base_mutation_chance": 0.2,
    "mutation_severity_factors": {
        "trivial": 1.5,   # 50% more likely to mutate
        "minor": 1.2,     # 20% more likely to mutate
        "moderate": 1.0,  # Normal mutation rate
        "major": 0.8,     # 20% less likely to mutate
        "critical": 0.6   # 40% less likely to mutate
    },
    "mutation_spread_factor_max": 2.0,
    "mutation_spread_factor_scaling": 50,
    
    # Rumor Spread
    "spread_radius_base": 10,
    "spread_severity_modifiers": {
        "trivial": 0.7,   # 30% reduced spread
        "minor": 0.9,     # 10% reduced spread
        "moderate": 1.0,  # Normal spread
        "major": 1.2,     # 20% increased spread
        "critical": 1.5   # 50% increased spread
    },
    "spread_saturation_factor": 0.8,
    "believability_thresholds": {
        "trivial": 0.3,
        "minor": 0.4,
        "moderate": 0.5,
        "major": 0.6,
        "critical": 0.7
    },
    
    # NPC Behavior
    "max_rumors_per_npc": 20,
    "trust_threshold_for_sharing": 3,
    "belief_accuracy_trust_scaling": 0.2,
    "rumor_distortion_chance": 0.05,
    "fabrication_chance": 0.01,
    "faction_bias_increment": 1
}


def _build_rumor_constants() -> Dict[str, Any]:
    """Build the rumor constants from JSON config and legacy fallbacks."""
    constants = _legacy_rumor_constants.copy()
    
    # Load configuration using dependency injection
    rumor_config = _get_config("rumor_config.json")
    
    # Override with JSON config values if available
    if rumor_config:
        # Handle both flat and nested structures
        if "decay" in rumor_config:
            # Nested structure - flatten for backward compatibility
            if "base_daily_rate" in rumor_config["decay"]:
                constants["base_decay_rate"] = rumor_config["decay"]["base_daily_rate"]
            if "severity_factors" in rumor_config["decay"]:
                constants["decay_severity_factors"] = rumor_config["decay"]["severity_factors"]
                
        if "mutation" in rumor_config:
            if "base_chance" in rumor_config["mutation"]:
                constants["base_mutation_chance"] = rumor_config["mutation"]["base_chance"]
            if "severity_modifiers" in rumor_config["mutation"]:
                constants["mutation_severity_factors"] = rumor_config["mutation"]["severity_modifiers"]
            if "spread_factor_max" in rumor_config["mutation"]:
                constants["mutation_spread_factor_max"] = rumor_config["mutation"]["spread_factor_max"]
            if "spread_factor_scaling" in rumor_config["mutation"]:
                constants["mutation_spread_factor_scaling"] = rumor_config["mutation"]["spread_factor_scaling"]
                
        if "spread" in rumor_config:
            if "radius_base" in rumor_config["spread"]:
                constants["spread_radius_base"] = rumor_config["spread"]["radius_base"]
            if "severity_radius_modifiers" in rumor_config["spread"]:
                constants["spread_severity_modifiers"] = rumor_config["spread"]["severity_radius_modifiers"]
            if "saturation_factor" in rumor_config["spread"]:
                constants["spread_saturation_factor"] = rumor_config["spread"]["saturation_factor"]
            if "believability_thresholds" in rumor_config["spread"]:
                constants["believability_thresholds"] = rumor_config["spread"]["believability_thresholds"]
                
        if "npc_behavior" in rumor_config:
            constants.update(rumor_config["npc_behavior"])
        
        # Also update with flat values for any keys that match directly
        for key, value in rumor_config.items():
            if not isinstance(value, dict) and key in constants:
                constants[key] = value
    
    return constants


# Lazy-loaded constants (rebuilt when config changes)
_rumor_constants: Optional[Dict[str, Any]] = None


def get_rumor_constants() -> Dict[str, Any]:
    """Get rumor constants, building them if necessary."""
    global _rumor_constants
    if _rumor_constants is None:
        _rumor_constants = _build_rumor_constants()
    return _rumor_constants


def reload_rumor_config():
    """
    Reload rumor configuration from JSON files.
    Clears cached constants to force rebuilding from new config.
    """
    global _rumor_constants
    _rumor_constants = None


# Rumor System Business Logic Functions

def get_rumor_decay_rate(severity: str, days_inactive: int = 1) -> float:
    """
    Calculate rumor decay rate based on severity and time inactive.
    
    Args:
        severity: Rumor severity ('trivial', 'minor', 'moderate', 'major', 'critical')
        days_inactive: Number of days the rumor has been inactive
    
    Returns:
        Decay rate as a float
    """
    constants = get_rumor_constants()
    
    base_rate = constants.get("base_decay_rate", 0.05)
    severity_factors = constants.get("decay_severity_factors", {})
    severity_factor = severity_factors.get(severity, 1.0)
    
    return base_rate * severity_factor * days_inactive


def get_rumor_mutation_chance(severity: str, spread_count: int = 0) -> float:
    """
    Calculate rumor mutation chance based on severity and spread count.
    
    Args:
        severity: Rumor severity
        spread_count: Number of times the rumor has spread
    
    Returns:
        Mutation chance as a float (0-1)
    """
    constants = get_rumor_constants()
    
    base_chance = constants.get("base_mutation_chance", 0.2)
    severity_factors = constants.get("mutation_severity_factors", {})
    severity_factor = severity_factors.get(severity, 1.0)
    
    # Apply spread factor
    max_factor = constants.get("mutation_spread_factor_max", 2.0)
    scaling = constants.get("mutation_spread_factor_scaling", 50)
    spread_factor = min(max_factor, 1 + (spread_count / scaling))
    
    return min(1.0, base_chance * severity_factor * spread_factor)


def get_rumor_spread_radius(severity: str, days_active: int = 1) -> int:
    """
    Calculate rumor spread radius based on severity and activity time.
    
    Args:
        severity: Rumor severity
        days_active: Number of days the rumor has been active
    
    Returns:
        Spread radius in distance units
    """
    constants = get_rumor_constants()
    
    base_radius = constants.get("spread_radius_base", 10)
    severity_modifiers = constants.get("spread_severity_modifiers", {})
    severity_modifier = severity_modifiers.get(severity, 1.0)
    
    # Apply saturation factor for long-running rumors
    saturation_factor = constants.get("spread_saturation_factor", 0.8)
    time_factor = 1 + (days_active * saturation_factor)
    
    return int(base_radius * severity_modifier * time_factor)


def get_rumor_believability_threshold(severity: str, relationship_strength: float = 0.0) -> float:
    """
    Calculate believability threshold for a rumor based on severity and relationships.
    
    Args:
        severity: Rumor severity
        relationship_strength: Strength of relationship between characters (-1 to 1)
    
    Returns:
        Believability threshold as a float (0-1)
    """
    constants = get_rumor_constants()
    
    thresholds = constants.get("believability_thresholds", {})
    base_threshold = thresholds.get(severity, 0.5)
    
    # Adjust based on relationship strength
    # Positive relationships lower the threshold (easier to believe)
    # Negative relationships raise the threshold (harder to believe)
    relationship_adjustment = -relationship_strength * 0.2
    
    return max(0.0, min(1.0, base_threshold + relationship_adjustment))


def get_npc_rumor_behavior(behavior_key: str) -> Any:
    """
    Get NPC rumor behavior constants.
    
    Args:
        behavior_key: Key for the behavior constant
    
    Returns:
        Behavior constant value
    """
    constants = get_rumor_constants()
    return constants.get(behavior_key)


def get_rumor_config(section: str = None) -> Dict[str, Any]:
    """
    Get rumor configuration section or entire config.
    
    Args:
        section: Optional section name to retrieve
    
    Returns:
        Configuration dictionary or section
    """
    constants = get_rumor_constants()
    
    if section:
        return constants.get(section, {})
    return constants 
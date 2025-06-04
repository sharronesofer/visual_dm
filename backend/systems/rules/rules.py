"""
Core Rules Module - Pure Business Logic
---------------------------------------
Game rules, balance constants, and standardized calculations.
Provides game mechanics and balance values without I/O dependencies.

Note: Rumor-specific logic has been moved to backend.systems.rumor.utils.rumor_rules
for better separation of concerns.
"""

from typing import Dict, Any, List, Optional, Protocol

# Business Logic Protocols (dependency injection)
class RulesConfigProvider(Protocol):
    """Protocol for rules configuration loading"""
    
    def load_json_config(self, filename: str, fallback_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Load JSON configuration with fallback"""
        ...


# Default configuration provider (will be injected)
_config_provider: Optional[RulesConfigProvider] = None


def set_config_provider(provider: RulesConfigProvider) -> None:
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


# Legacy balance constants (maintained for backward compatibility)
# These will be overridden by JSON config if available
_legacy_constants = {
    # Character Creation
    "starting_gold": 100,
    "starting_level": 1,
    "max_level": 20,
    "min_ability": -3,    # Custom system: attributes are -3 to +5
    "max_ability": 5,     # Custom system: attributes are -3 to +5
    "default_ability": 0, # Custom system: 0 is average
    
    # Combat
    "base_ac": 10,
    "base_hp": 8,
    "base_speed": 30,
    
    # Experience and Leveling
    "xp_thresholds": [
        0, 300, 900, 2700, 6500, 14000, 23000, 34000, 48000, 64000,
        85000, 100000, 120000, 140000, 165000, 195000, 225000, 265000, 305000, 355000
    ],
    
    # Racial Modifiers (custom system)
    "racial_bonuses": {
        "human": {"all_attributes": 1},
        "elf": {"dexterity": 2, "intelligence": 1},
        "dwarf": {"constitution": 2, "strength": 1},
        "halfling": {"dexterity": 2, "charisma": 1},
        "orc": {"strength": 2, "constitution": 1, "intelligence": -1},
        "gnome": {"intelligence": 2, "constitution": 1},
        "tiefling": {"charisma": 2, "intelligence": 1}
    },
    
    # Hit Points (ability-based system, no classes)
    "default_hit_die": 12,  # d12 as per rules_directives.md: HP = Level × (1d12 + CON)
    
    # Equipment
    "equipment_weight_limits": {
        "light": 5,
        "medium": 15,
        "heavy": 25
    },
    
    # Currency
    "currency_conversion": {
        "copper": 1,
        "silver": 10,
        "electrum": 50,
        "gold": 100,
        "platinum": 1000
    }
}


def _build_balance_constants() -> Dict[str, Any]:
    """Build the balance constants from JSON config and legacy fallbacks."""
    constants = _legacy_constants.copy()
    
    # Load configuration using dependency injection
    balance_config = _get_config("balance_constants.json")
    
    # Override with JSON config values if available
    if balance_config:
        # Flatten the JSON structure for backward compatibility
        for section, values in balance_config.items():
            if isinstance(values, dict):
                constants.update(values)
            else:
                constants[section] = values
        
        # Map specific JSON keys to legacy keys
        if "character_creation" in balance_config:
            char_creation = balance_config["character_creation"]
            constants.update(char_creation)
            # Map new attribute keys to legacy ability keys for backward compatibility
            if "min_attribute" in char_creation:
                constants["min_ability"] = char_creation["min_attribute"]
            if "max_attribute" in char_creation:
                constants["max_ability"] = char_creation["max_attribute"]
            if "default_attribute" in char_creation:
                constants["default_ability"] = char_creation["default_attribute"]
        
        if "combat" in balance_config:
            combat = balance_config["combat"]
            constants.update(combat)
            # Map weight_limits to legacy key
            if "weight_limits" in balance_config.get("equipment", {}):
                constants["equipment_weight_limits"] = balance_config["equipment"]["weight_limits"]
        
        if "progression" in balance_config:
            progression = balance_config["progression"]
            constants.update(progression)
        
        if "currency" in balance_config and "conversion_rates" in balance_config["currency"]:
            constants["currency_conversion"] = balance_config["currency"]["conversion_rates"]
    
    return constants


# Lazy-loaded constants (rebuilt when config changes)
_balance_constants: Optional[Dict[str, Any]] = None


def get_balance_constants() -> Dict[str, Any]:
    """Get balance constants, building them if necessary."""
    global _balance_constants
    if _balance_constants is None:
        _balance_constants = _build_balance_constants()
    return _balance_constants


# Business Logic Functions (Pure Calculations)

def calculate_ability_modifier(attribute_score: int) -> int:
    """
    In this system, attribute scores ARE the modifiers (-3 to +5).
    No separation between score and bonus - just return the score directly.
    
    Args:
        attribute_score: The attribute modifier (-3 to +5)
    
    Returns:
        The same value (attribute scores are modifiers in this system)
    """
    # Clamp to valid range
    return max(-3, min(5, attribute_score))


def calculate_hp_for_level(level: int, constitution_modifier: int) -> int:
    """
    Calculate hit points for a character at a given level using the standardized system.
    HP = Level × (average d12 + CON modifier) as per rules_directives.md
    
    This is the CANONICAL hit point calculation - all other systems should use this.
    
    Args:
        level: Character level
        constitution_modifier: Constitution modifier
    
    Returns:
        Total hit points
    """
    # Load formulas configuration using dependency injection
    formulas_config = _get_config("formulas.json")
    
    # Check if we have a formula from JSON config
    if (formulas_config and 
        "character_stats" in formulas_config and 
        "hit_points" in formulas_config["character_stats"]):
        
        # Use rounded average d12 (7) from JSON config
        dice_averages = formulas_config.get("dice", {}).get("rounded_averages", {})
        average_d12 = dice_averages.get("d12", 7)
    else:
        # Fallback to hardcoded average
        average_d12 = 7
    
    return level * (average_d12 + constitution_modifier)


def calculate_mana_points(level: int, intelligence_modifier: int) -> int:
    """
    Calculate mana points for a character at a given level.
    MP = Level × (average d8 + INT modifier)
    
    Args:
        level: Character level
        intelligence_modifier: Intelligence modifier
    
    Returns:
        Total mana points
    """
    # Load formulas configuration using dependency injection
    formulas_config = _get_config("formulas.json")
    
    # Check if we have a formula from JSON config
    if (formulas_config and 
        "character_stats" in formulas_config and 
        "mana_points" in formulas_config["character_stats"]):
        
        # Use rounded average d8 (5) from JSON config
        dice_averages = formulas_config.get("dice", {}).get("rounded_averages", {})
        average_d8 = dice_averages.get("d8", 5)
    else:
        # Fallback to hardcoded average
        average_d8 = 5
    
    return level * (average_d8 + intelligence_modifier)


def get_starting_equipment(background=None):
    """Get starting equipment for a character background"""
    try:
        equipment_config = _rules_data.get('starting_equipment', {})
        
        # If no background specified, return default equipment
        if background is None:
            return equipment_config.get("default_equipment", ["basic clothing", "backpack", "50 gold pieces"])
        
        # Look for specific background
        backgrounds = equipment_config.get("backgrounds", {})
        if background in backgrounds:
            return backgrounds[background].get("equipment", [])
        
        # If specific background not found, try case variations
        for bg_key, bg_data in backgrounds.items():
            if bg_key.lower() == background.lower():
                return bg_data.get("equipment", [])
        
        # If background still not found, return default
        return equipment_config.get("default_equipment", ["basic clothing", "backpack", "50 gold pieces"])
    
    except Exception:
        # Standard starting equipment fallbacks for custom system
        STARTING_EQUIPMENT_FALLBACK = {
            'default_equipment': ['basic clothing', 'backpack', '50 gold pieces'],
            'backgrounds': {
                'village_guard': {
                    'equipment': ['worn sword', 'leather vest', 'guard badge', 'basic clothing', 'belt pouch'],
                    'description': 'Former village protector with basic combat gear'
                },
                'wandering_merchant': {
                    'equipment': ['trade ledger', 'measuring scales', 'merchant clothes', 'coin purse', 'travel pack'],
                    'description': 'Traveling trader with business tools'
                },
                'forest_dweller': {
                    'equipment': ['hunting knife', 'herb pouch', 'rough clothing', 'survival kit'],
                    'description': 'Wilderness survivor with outdoor gear'
                },
                'scholar_apprentice': {
                    'equipment': ['writing kit', 'research notes', 'simple robes', 'book satchel'],
                    'description': 'Student of knowledge with academic tools'
                },
                'tavern_worker': {
                    'equipment': ['serving tray', 'bar rag', 'work clothes', 'tip pouch'],
                    'description': 'Hospitality worker with service tools'
                },
                'street_performer': {
                    'equipment': ['musical instrument', 'colorful outfit', 'performance props', 'collection hat'],
                    'description': 'Entertainer with performance gear'
                }
            }
        }
        
        if background is None:
            return STARTING_EQUIPMENT_FALLBACK['default_equipment']
        
        # Look for specific background in fallback
        backgrounds = STARTING_EQUIPMENT_FALLBACK['backgrounds']
        if background in backgrounds:
            return backgrounds[background]['equipment']
        
        # Try case variations
        for bg_key, bg_data in backgrounds.items():
            if bg_key.lower() == background.lower():
                return bg_data['equipment']
        
        # Return default if not found
        return STARTING_EQUIPMENT_FALLBACK['default_equipment']


def get_formula_info(formula_name: str) -> Dict[str, Any]:
    """
    Get information about a specific formula.
    
    Args:
        formula_name: Name of the formula to look up
    
    Returns:
        Formula information dictionary
    """
    # Load formulas configuration using dependency injection
    formulas_config = _get_config("formulas.json")
    
    if formulas_config and "formulas" in formulas_config:
        return formulas_config["formulas"].get(formula_name, {})
    
    return {}


def reload_config():
    """
    Reload configuration from JSON files.
    Clears cached constants to force rebuilding from new config.
    """
    global _balance_constants
    _balance_constants = None


# For backward compatibility, create a balance_constants object-like interface
class _BalanceConstantsProxy:
    """Proxy object to maintain backward compatibility with balance_constants dict access."""
    
    def __getitem__(self, key: str):
        return get_balance_constants()[key]
    
    def get(self, key: str, default=None):
        return get_balance_constants().get(key, default)
    
    def keys(self):
        return get_balance_constants().keys()
    
    def values(self):
        return get_balance_constants().values()
    
    def items(self):
        return get_balance_constants().items()
    
    def __contains__(self, key: str):
        return key in get_balance_constants()


# Remove the function definition - just keep the proxy
# Actually create the proxy instance for dict-like access
balance_constants = _BalanceConstantsProxy() 
# JSON Configuration System Guide

## Overview

The Visual DM project has migrated from hard-coded enum values to a flexible JSON-based configuration system. This provides data-driven content management, allowing game mechanics to be adjusted without code changes.

## Architecture

### Configuration Loader

The `JSONConfigLoader` class (`backend/infrastructure/data/json_config_loader.py`) serves as the central hub for loading and accessing all JSON configurations:

```python
from backend.infrastructure.data.json_config_loader import get_config_loader

# Get the singleton instance
config_loader = get_config_loader()

# Access faction data
faction_data = config_loader.get_faction_type("merchant")
```

### Configuration Files

All configuration files are stored in the `/data` directory with the following structure:

```
data/
├── systems/
│   ├── faction/
│   │   └── faction_config.json
│   ├── magic/
│   │   └── damage_types.json
│   ├── population/
│   │   └── settlement_types.json
│   ├── economy/
│   │   └── resource_types.json
│   ├── region/
│   │   └── region_types.json
│   └── chaos/
│       └── chaos_config.json
└── biomes/
    └── biome_types_extended.json
```

## Configuration Types

### 1. Faction System (`data/systems/faction/faction_config.json`)

Replaces the old `FactionType`, `FactionAlignment`, and `DiplomaticStance` enums.

**Usage:**
```python
from backend.infrastructure.schemas.faction.faction_types import (
    validate_faction_type,
    get_faction_type_data,
    get_valid_faction_types
)

# Validate a faction type
if validate_faction_type("merchant"):
    faction_data = get_faction_type_data("merchant")
    print(faction_data["name"])  # "Merchant Consortium"

# Get all valid faction types
all_types = get_valid_faction_types()
```

**Configuration Structure:**
```json
{
  "version": "1.0.0",
  "description": "Faction system configurations",
  "faction_types": {
    "merchant": {
      "name": "Merchant Consortium",
      "description": "Trade-focused organization",
      "attributes": {
        "hierarchy": "corporate",
        "territoriality": "low",
        "wealth_focus": "high"
      },
      "typical_goals": ["trade_expansion", "profit_maximization"]
    }
  }
}
```

### 2. Magic System (`data/systems/magic/damage_types.json`)

Replaces the old `DamageType` enum with rich elemental damage mechanics.

**Usage:**
```python
from backend.systems.magic.spell_rules import (
    validate_damage_type,
    get_damage_type_data,
    get_environmental_damage_modifier
)

# Get damage type data
fire_data = get_damage_type_data("fire")
elemental_effects = fire_data["elemental_effects"]

# Get environmental modifiers
underwater_modifier = get_environmental_damage_modifier("fire", "underwater")
```

**Features:**
- Elemental properties and interactions
- Environmental damage modifiers
- Resistance/vulnerability relationships
- Spell combination effects

### 3. Settlement System (`data/systems/population/settlement_types.json`)

Replaces the old `SettlementType` enum with detailed population mechanics.

**Configuration Structure:**
```json
{
  "settlement_types": {
    "village": {
      "name": "Village",
      "population_range": [50, 500],
      "governance": {
        "type": "council",
        "complexity": "simple"
      },
      "economic_focus": ["agriculture", "crafts"],
      "infrastructure_level": 2
    }
  }
}
```

### 4. Resource System (`data/systems/economy/resource_types.json`)

Replaces the old `ResourceType` enum with comprehensive economic mechanics.

**Usage:**
```python
from backend.systems.region.models import (
    validate_resource_type,
    get_resource_type_data,
    ResourceNode
)

# Create a resource node with validation
node = ResourceNode(
    resource_type="iron",
    abundance=0.8,
    quality=0.7,
    accessibility=0.9
)

# Value calculation uses JSON configuration modifiers
value = node.calculate_value()
```

### 5. Region System (`data/systems/region/region_types.json`)

Replaces the old `RegionType` enum with detailed governance systems.

**Features:**
- Territorial management rules
- Governance hierarchies
- Economic systems
- Cultural characteristics

### 6. Biome System (`data/biomes/biome_types_extended.json`)

Replaces the old `BiomeType` enum with environmental mechanics.

**Usage:**
```python
from backend.systems.region.models import (
    validate_biome_type,
    get_biome_type_data,
    RegionProfile
)

# Create region profile with biome validation
profile = RegionProfile(
    dominant_biome="temperate_forest",
    secondary_biomes=["grassland"]
)

# Habitability calculation uses biome modifiers
habitability = profile.calculate_habitability()
```

### 7. Chaos System (`data/systems/chaos/chaos_config.json`)

Replaces the old `ChaosLevel` enum with dynamic chaos mechanics.

**Features:**
- Stability modifiers
- Manifestation systems
- Mitigation strategies
- Progression thresholds

## Development Guide

### Adding New Configuration Types

1. **Create JSON File**: Add your configuration file to the appropriate directory under `/data`.

2. **Update Loader**: Add methods to `JSONConfigLoader` to access your new configuration:

```python
@lru_cache(maxsize=128)
def get_your_config_type(self, config_id: str) -> Optional[Dict[str, Any]]:
    """Get your configuration data by ID"""
    return self._cache['your_config']['your_types'].get(config_id)

def get_all_your_config_types(self) -> Dict[str, Dict[str, Any]]:
    """Get all your configuration data"""
    return self._cache['your_config']['your_types']
```

3. **Add Validation**: Create validation functions:

```python
def validate_your_config_type(config_id: str) -> bool:
    """Validate your configuration ID"""
    return validate_config_id(config_id, ConfigurationType.YOUR_CONFIG)
```

4. **Update Models**: Modify your models to use string IDs instead of enums:

```python
@dataclass
class YourModel:
    config_type: str  # Instead of YourConfigEnum
    
    def __post_init__(self):
        if not validate_your_config_type(self.config_type):
            raise ValueError(f"Invalid config type: {self.config_type}")
```

### Backwards Compatibility

The system maintains backwards compatibility through the `JSONConfigEnum` class:

```python
# Old enum-style access still works
faction_type = FactionType.MERCHANT  # Returns "merchant" string
damage_type = DamageType.FIRE       # Returns "fire" string

# Iteration still works
for faction_type in FactionType:
    print(faction_type)

# Membership testing still works
if "merchant" in FactionType:
    print("Merchant faction type exists")
```

### Testing

Comprehensive tests are provided in `backend/tests/test_json_configurations.py`:

```bash
# Run configuration tests
python -m pytest backend/tests/test_json_configurations.py -v

# Test specific functionality
python -m pytest backend/tests/test_json_configurations.py::TestJSONConfigLoader::test_faction_configuration_loading -v
```

## Migration Guide

### From Enums to JSON

Use the migration script to transition existing data:

```bash
# Run full migration
python backend/scripts/migrate_enums_to_json.py --database-url="your_db_url"

# Dry run (no database changes)
python backend/scripts/migrate_enums_to_json.py --dry-run

# Validation only
python backend/scripts/migrate_enums_to_json.py --validate-only
```

### Code Migration Patterns

**Before (Enum-based):**
```python
from enum import Enum

class FactionType(Enum):
    MERCHANT = "merchant"
    MILITARY = "military"

# Usage
faction = create_faction(faction_type=FactionType.MERCHANT)
```

**After (JSON-based):**
```python
from backend.infrastructure.data.json_config_loader import get_config_loader

# Usage with validation
if validate_faction_type("merchant"):
    faction = create_faction(faction_type="merchant")
    
# Access rich configuration data
config_loader = get_config_loader()
merchant_data = config_loader.get_faction_type("merchant")
hierarchy = merchant_data["attributes"]["hierarchy"]
```

## Configuration Schema

### Standard Fields

All configuration files should include:

```json
{
  "version": "1.0.0",
  "description": "Human-readable description",
  "extends": "optional_base_config.json",
  "last_updated": "2024-01-01T00:00:00Z",
  "your_config_section": {
    "config_id": {
      "name": "Display Name",
      "description": "Detailed description",
      "category": "classification",
      "properties": {},
      "modifiers": {},
      "interactions": {}
    }
  }
}
```

### Validation Requirements

1. **Unique IDs**: Configuration IDs must be unique within their type
2. **Required Fields**: `name` and `description` are required for all configs
3. **Valid References**: Any references to other configurations must be valid
4. **Numeric Ranges**: Numeric values should be within reasonable ranges
5. **Enum Values**: String values from fixed sets should be validated

## Benefits

### For Developers

- **Type Safety**: Validation ensures configuration IDs are valid
- **Rich Data**: Access to detailed configuration properties
- **Easy Testing**: Mock configurations for unit tests
- **Hot Reloading**: Configurations can be reloaded without code changes

### For Content Creators

- **No Code Changes**: Modify game mechanics by editing JSON files
- **Version Control**: Track configuration changes with Git
- **Easy Validation**: JSON schema validation prevents errors
- **Documentation**: Self-documenting configuration files

### For Game Masters

- **Campaign Customization**: Adjust mechanics for specific campaigns
- **Mod Support**: Easy creation of configuration mods
- **Balancing**: Fine-tune game balance without developer intervention
- **Experimentation**: Try new mechanics rapidly

## Performance Considerations

### Caching

- **LRU Cache**: Frequently accessed configurations are cached
- **Singleton Pattern**: Single configuration loader instance
- **Lazy Loading**: Configurations loaded only when needed
- **Memory Efficient**: Only active configurations kept in memory

### Optimization Tips

1. **Batch Access**: Load multiple configurations together
2. **Validate Once**: Cache validation results for repeated use
3. **Minimal Reloading**: Only reload configurations when necessary
4. **Profile Usage**: Monitor configuration access patterns

## Troubleshooting

### Common Issues

**Configuration Not Found:**
```python
# Check if configuration exists
if not config_loader.validate_id("unknown_id", "faction_type"):
    valid_ids = config_loader.get_faction_type_ids()
    print(f"Valid faction types: {valid_ids}")
```

**Invalid JSON:**
```bash
# Validate JSON syntax
python -m json.tool data/systems/faction/faction_config.json
```

**Migration Issues:**
```bash
# Check migration status
python backend/scripts/migrate_enums_to_json.py --validate-only
```

### Debug Mode

Enable debug logging to trace configuration loading:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Configuration loading will now show detailed logs
config_loader = get_config_loader()
```

## Future Enhancements

### Planned Features

1. **Dynamic Reloading**: Hot-reload configurations during development
2. **Schema Validation**: JSON Schema validation for all configurations
3. **Configuration UI**: Web interface for editing configurations
4. **Version Management**: Support for configuration versioning
5. **Mod System**: Plugin system for configuration mods

### Extension Points

The system is designed for easy extension:

- **New Config Types**: Add new configuration categories
- **Custom Validators**: Implement domain-specific validation
- **Cache Strategies**: Customize caching behavior
- **Loading Sources**: Support for database, API, or other sources

## Conclusion

The JSON configuration system provides a flexible, maintainable foundation for Visual DM's game mechanics. By separating configuration from code, we enable rapid iteration, easier testing, and better collaboration between developers and content creators.

For questions or contributions, please refer to the development documentation or open an issue in the project repository. 
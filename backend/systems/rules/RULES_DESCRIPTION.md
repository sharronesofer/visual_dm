# Rules System Description

## Overview
The Rules system serves as the core foundation for all game mechanics in Visual DM. It defines the mathematical formulas, balance constants, and standardized calculations that determine how characters grow, gain abilities, and interact with the game world. Think of it as the "rulebook" that all other systems consult when they need to know how strong a character should be, how much health they have, or what equipment they start with.

**Status: MODERNIZED** - The system has been updated with JSON-driven configuration, canonical calculations, and removal of class system references.

## System Architecture

### Logical Subsystems

#### 1. **JSON Configuration System** (`data/systems/rules/` directory)
- **Purpose**: Provides designer-friendly configuration files for all game rules and balance values
- **Role**: Separates game balance data from code logic, enabling non-programmers to tune game mechanics
- **Files**: 
  - `balance_constants.json` - Core numerical values for game balance
  - `starting_equipment.json` - Background-based equipment assignments
  - `formulas.json` - Mathematical formulas with documentation

#### 2. **Core Balance Constants Engine** (JSON-backed with fallbacks)
- **Purpose**: Contains all the fundamental numerical values that define game balance
- **Role**: Acts as a centralized configuration for character creation, combat mechanics, leveling progression, and equipment systems
- **Examples**: Starting gold (100), maximum character level (20), base armor class (10), currency conversion rates
- **Innovation**: Now loads from JSON with intelligent fallbacks to hardcoded values

#### 3. **Canonical Calculation Engine** (Standardized Functions)
- **Purpose**: Provides standardized mathematical formulas for character statistics
- **Role**: Ensures all systems use the same calculations for character abilities, hit points, and progression
- **Key Functions**: 
  - Attribute score to modifier conversion (custom -3 to +5 system)
  - Hit point calculation based on level and constitution (standardized d12 system)
  - Mana point calculation for spellcasters
  - Starting equipment determination based on background

#### 4. **Legacy Compatibility Layer** (Backward compatibility)
- **Purpose**: Maintains compatibility with existing code while encouraging migration to new system
- **Role**: Provides deprecation warnings and delegation to canonical system
- **Functions**: Bridges old infrastructure calls to new canonical system

## Business Logic Breakdown

### Character Creation Rules
**What it does**: Establishes the starting conditions for new characters in the game world using the classless ability-based system.

- **Starting Resources**: Every new character begins with 100 gold pieces and starts at level 1
- **Attribute Scores**: Character attributes must fall between -3 (very weak) and +5 (superhuman), with 0 being average capability
- **Equipment Assignment**: Characters receive different starting gear based on their background story (village guards get worn swords, merchants get trade ledgers, etc.)
- **Attribute Allocation**: Characters start with 7 attributes at creation and gain 3 more per level
- **Why it matters**: This creates fair, balanced starting conditions and ensures all characters begin their adventures on equal footing

### Character Progression Rules  
**What it does**: Defines how characters become more powerful as they gain experience using standardized formulas.

- **Experience Thresholds**: Uses predefined XP thresholds for consistent level progression (300 for level 2, 355,000 for level 20)
- **Hit Point Calculation**: Uses the CANONICAL formula: `Level × (7 + Constitution modifier)` where 7 is the average of a d12
- **Mana Point Calculation**: Uses the formula: `Level × 5 + Intelligence modifier × Level` where 5 is the average of a d8
- **Why it matters**: This creates predictable, balanced progression where characters genuinely become more capable heroes over time

### Racial Characteristics
**What it does**: Defines the inherent strengths and weaknesses of different fantasy races.

- **Stat Modifications**: Each race has natural tendencies (elves are more dexterous and intelligent, dwarves are stronger and more resilient, orcs are powerful but less intelligent)
- **Human Versatility**: Humans receive a small bonus to all attributes, representing their adaptability
- **JSON Configuration**: Racial bonuses are now defined in JSON for easy designer modification
- **Why it matters**: This gives players meaningful choices during character creation and reflects the fantasy world's diversity

### Economic System Rules
**What it does**: Establishes the relative value of different currencies and equipment weights.

- **Currency Exchange**: Defines how many copper pieces equal a silver piece (10:1), gold piece (100:1), etc.
- **Equipment Limits**: Sets realistic weight categories for armor and gear (light armor under 5 pounds, heavy armor up to 25 pounds)
- **JSON Configuration**: Currency rates and weight limits are now configurable via JSON
- **Why it matters**: This creates a believable economy where players must make strategic choices about what to carry and spend

### Combat Foundation
**What it does**: Provides the mathematical backbone for all combat calculations using the classless system.

- **Base Statistics**: Every character starts with 10 armor class, configurable base hit points, and 30 feet of movement speed
- **Attribute Modifiers**: Uses the custom -3 to +5 attribute system where attributes ARE the modifiers
- **Hit Point System**: Uses d12 as the standard hit die with deterministic calculation for consistency
- **Why it matters**: This ensures combat feels fair and predictable while still allowing for character customization

## Integration with Broader Codebase

### Character System Dependencies
**How it's used**: The Character system imports balance constants and calculation functions from the canonical rules system to create and level up characters.

**Impact of changes**: If hit point calculations change in the JSON config, it would immediately affect:
- How much health characters gain when leveling up
- The relative power balance between different character builds

### Economy System Integration
**How it's used**: The Economy system references starting gold and currency conversion rates from the JSON configuration.

**Impact of changes**: Modifying these values in JSON would affect:
- How wealthy new characters feel at the start of the game
- The relative costs of items in shops
- The value of treasure found during adventures

### Combat System Dependencies
**How it's used**: Combat systems use attribute modifiers and base statistics from the canonical calculation functions.

**Impact of changes**: Altering formulas in JSON config would change:
- How often attacks hit their targets
- How much damage characters can absorb
- The tactical importance of different character builds

### Equipment and Inventory Systems
**How it's used**: These systems check weight limits and starting equipment lists from the JSON configuration.

**Impact of changes**: Modifying equipment rules in JSON would affect:
- How much gear characters can realistically transport
- What advantages different backgrounds provide
- The strategic importance of equipment choices

## Maintenance Concerns - RESOLVED

### ✅ Fixed: Inconsistent Hit Point Calculations
**Previous Problem**: Different modules used d8, d10, d12 with various calculation methods.

**Solution Implemented**:
- Standardized on d12 with average value (7) across all systems
- Created canonical `calculate_hp_for_level(level, constitution_modifier)` function
- Updated all systems to use the canonical calculation
- Added formula documentation in JSON config

### ✅ Fixed: Duplicated Balance Constants
**Previous Problem**: Multiple files defined their own versions of balance constants.

**Solution Implemented**:
- Created single JSON configuration source
- Updated all systems to import from canonical rules system
- Deprecated duplicate constant definitions with warnings
- Maintained backward compatibility through delegation

### ✅ Fixed: Class System References
**Previous Problem**: Code still referenced "fighter", "wizard" despite classless design.

**Solution Implemented**:
- Removed all class-based equipment and hit point calculations
- Updated tests to reflect background-based equipment system
- Replaced class-based functions with background-based equivalents
- Updated documentation to reflect ability-based progression

## Opportunities for Modular Cleanup - IMPLEMENTED

### ✅ Implemented: JSON Balance Constants
**What was done**: Created `data/systems/rules/balance_constants.json` with all game balance values.

**Benefits realized**:
- Game designers can adjust character progression, starting resources, and racial bonuses without touching code
- Different game modes can use different balance files
- Playtesting can easily try different values to find optimal game balance
- Version control tracks exactly what balance changes were made

### ✅ Implemented: JSON Equipment Templates  
**What was done**: Created `data/systems/rules/starting_equipment.json` organized by background.

**Benefits realized**:
- Content creators can easily add new backgrounds with unique starting gear
- Equipment can be balanced independently of code releases
- Different campaigns can use different equipment sets
- Equipment names are separated from code for easier localization

### ✅ Implemented: JSON Formula Documentation
**What was done**: Created `data/systems/rules/formulas.json` with mathematical formulas and their explanations.

**Benefits realized**:
- Designers can understand exactly how game mechanics work
- Formula changes are documented and version controlled
- Multiple formula variants can be supported for different game modes
- Non-programmers can propose balance changes with clear documentation

### ✅ Implemented: Configuration-Driven System
**What was done**: Rules system now loads from JSON first, falls back to code constants.

**Benefits realized**:
- Zero-downtime configuration changes during development
- A/B testing of different rule sets
- Community can propose and test balance changes through configuration files
- System supports multiple rule variants for different game modes

## Developer Usage

### Importing the Canonical System
```python
from backend.systems.rules.rules import (
    balance_constants,
    calculate_hp_for_level,
    calculate_mana_points,
    get_starting_equipment,
    get_formula_info
)
```

### Using Standardized Calculations
```python
# Always use canonical calculations
hp = calculate_hp_for_level(level=5, constitution_modifier=2)
mp = calculate_mana_points(level=5, intelligence_modifier=3)
equipment = get_starting_equipment("acolyte")
```

### Accessing Configuration
```python
# Configuration is automatically loaded from JSON
starting_gold = balance_constants['starting_gold']
xp_thresholds = balance_constants['xp_thresholds']
racial_bonuses = balance_constants['racial_bonuses']['elf']
```

## Summary of Improvements

The Rules system has been successfully modernized with:

1. **JSON-driven configuration** for designer-friendly balance tuning
2. **Canonical calculation functions** that eliminate inconsistencies
3. **Removal of class system references** in favor of ability-based progression
4. **Deprecation of duplicate systems** with clear migration paths
5. **Comprehensive documentation** for both developers and designers
6. **Backward compatibility** to ensure existing code continues working

This transformation converts the Rules system from a hardcoded foundation into a flexible, configuration-driven system that can adapt to different playstyles and balance needs without requiring programmer intervention. The system now serves as a model for how other game systems should be structured. 
# Combat System Description

## Overview

The combat system for Visual DM provides turn-based tactical combat functionality with rich action management, status effect tracking, and narrative integration. The system is designed to support both traditional D&D-style combat mechanics and modern game design patterns with extensive customization options.

**Recent Improvements (Updated):**
- ✅ **Configuration-Driven Design**: Replaced hardcoded values with JSON configuration files
- ✅ **Database Abstraction**: Implemented proper database abstraction layer replacing Firebase TODOs
- ✅ **Improved Error Handling**: Added comprehensive error handling with proper exception raising
- ✅ **Consistent Field Handling**: Fixed dual HP field handling inconsistencies
- ✅ **Enhanced Action Validation**: Replaced placeholder code with comprehensive action validation logic
- ✅ **Modular Configuration**: Created data-driven action definitions and status effects

---

## 1. Logical Subsystems

### **Core Combat Management (`combat_utils.py`)**
- **Role**: Provides the fundamental combat operations and state management
- **Purpose**: Handles combat initialization, damage calculations, and basic combat resolution
- **Key Functions**: Starting combat encounters, rolling initiative, calculating hit/miss outcomes, applying damage to characters
- **Improvements**: Now uses configuration system for all values, improved error handling, consistent field access

### **Configuration System (`config_loader.py` & `config.json`)**
- **Role**: Centralized configuration management for combat mechanics
- **Purpose**: Replaces hardcoded values with configurable settings, enabling easy customization without code changes
- **Key Functions**: Loading configuration from JSON, providing safe access to config values, handling field mappings for consistent data access

### **Action System (`utils/action_system.py`)**
- **Role**: Manages the action economy and validates what actions characters can take
- **Purpose**: Enforces D&D-style action rules (standard, bonus, reaction, movement actions) and tracks action usage per turn
- **Key Functions**: Defining available actions, validating action usage, executing actions with proper economy tracking
- **Improvements**: Replaced placeholder validation with comprehensive logic based on character abilities, equipment, status effects

### **Action Definitions (`actions.json`)**
- **Role**: Data-driven action configuration
- **Purpose**: Defines all combat actions in JSON format for easy modification by non-programmers
- **Categories**: Basic actions, spell actions, bonus actions, reactions, class-specific abilities, environmental actions

### **Turn Management (`utils/turn_queue.py`)**
- **Role**: Controls the order and flow of combat turns
- **Purpose**: Maintains initiative order, handles turn advancement, and provides hooks for turn-based events
- **Key Functions**: Sorting characters by initiative, advancing to next turn, handling delayed actions

### **Status Effects (`utils/status_effects_utils.py`)**
- **Role**: Manages temporary effects that modify character abilities or states
- **Purpose**: Applies, tracks, and removes timed effects like buffs, debuffs, and conditions
- **Key Functions**: Applying effects with duration, decreasing effect timers each turn, removing expired effects
- **Improvements**: Added database abstraction, improved error handling, configuration integration

### **Status Effects Configuration (`status_effects.json`)**
- **Role**: Data-driven status effect definitions
- **Purpose**: Defines all status effects in JSON format with categories: conditions, buffs, damage over time, healing over time, temporary effects

### **Narrative Integration (`utils/combat_narrative_utils.py`)**
- **Role**: Converts mechanical combat actions into storytelling elements
- **Purpose**: Generates AI-powered descriptions of combat events and maintains combat logs for storytelling
- **Key Functions**: Creating vivid action descriptions, logging combat events, formatting combat summaries
- **Improvements**: Added database abstraction, improved error handling, configuration-driven logging

---

## 2. Business Logic in Simple Terms

### **Configuration-Driven Mechanics**

**Combat Configuration**: All game mechanics values are now stored in `config.json`, including default character stats, dice systems, action economy rules, effect durations, and field mappings. This allows game masters to customize combat rules by editing a simple JSON file instead of requiring code changes.

**Dynamic Action Loading**: Actions are defined in `actions.json` and can be loaded at runtime. Game masters can create custom spells, abilities, and attacks by adding entries to the JSON file. Each action specifies its requirements, resource costs, range, and effects.

**Comprehensive Status Effects**: Status effects are defined in `status_effects.json` with detailed effect descriptions, durations, and mechanical impacts. Effects are categorized by type (conditions, buffs, damage over time) and include stackability and dispellability rules.

### **Enhanced Core Combat Management**

**Improved Combat Initialization**: The system now validates all inputs and provides detailed error messages. Initiative calculation uses configurable dice settings, and all character data access goes through configuration-aware helper methods that handle multiple field name variations.

**Advanced Damage Calculation**: Added support for critical hits (natural 20s), critical misses (natural 1s), and configurable damage thresholds. The system parses complex dice notation and applies minimum damage rules from configuration.

**Consistent Character Data Handling**: Fixed the dual HP field issue by implementing configuration-aware field accessors. The system now correctly updates all HP-related fields (`hp`, `HP`, `max_hp`, etc.) consistently across different data formats.

### **Sophisticated Action Validation**

**Dynamic Action Availability**: Replaced placeholder code with comprehensive validation that considers character level, class, equipment, abilities, status effects, and resource costs. The system dynamically determines which actions each character can perform based on their current state.

**Status Effect Integration**: Actions are blocked or modified based on active status effects. For example, stunned characters cannot take most actions, silenced characters cannot cast spells, and grappled characters cannot move.

**Resource Management**: The system tracks spell slots, class resources (rage uses, action surge), and other limited-use abilities. Actions automatically check resource availability before allowing use.

### **Database Abstraction Layer**

**Persistent Storage Interface**: Implemented database adapter classes that provide a clean interface for persistence operations. These adapters can be easily replaced with different database implementations (Firebase, PostgreSQL, etc.) without changing combat logic.

**Graceful Fallbacks**: When database operations fail, the system continues functioning with in-memory data and logs warnings about persistence failures.

---

## 3. Integration with Broader Codebase

### **Configuration System Integration**
The combat configuration integrates with environment variables and can be reloaded at runtime. This allows for live-tuning of combat mechanics during gameplay testing.

### **Database Integration (Improved)**
The new database abstraction layer provides clean interfaces for:
- Combat state persistence
- Status effect tracking across sessions
- Narrative event logging
- NPC memory updates

### **Modular Action System**
Actions can now be dynamically loaded from JSON files, allowing:
- Community-created content
- Easy balance updates
- Custom campaign rules
- Rapid prototyping of new abilities

### **Enhanced AI Integration**
The narrative system now gracefully handles AI service failures and provides fallback descriptions when the LLM is unavailable.

---

## 4. Maintenance Concerns ✅ **RESOLVED**

### **~~Database Integration TODOs~~ ✅ FIXED**
- ~~Database integration TODOs have been replaced with proper database abstraction classes~~
- ✅ Implemented `DatabaseAdapter` and `NarrativeDatabase` classes with clear interfaces
- ✅ All database operations now go through abstraction layer for easy replacement

### **~~Placeholder Code~~ ✅ FIXED**
- ~~Action system placeholder implementation has been completely replaced~~
- ✅ Implemented comprehensive action validation based on character capabilities
- ✅ Added support for equipment requirements, class restrictions, level gates, and status effect interactions

### **~~Consistency Issues~~ ✅ FIXED**
- ~~Dual HP field handling has been resolved with configuration-aware accessors~~
- ✅ Implemented unified field access methods that handle multiple field name variations
- ✅ All HP updates now consistently modify all relevant fields

### **~~Error Handling Gaps~~ ✅ IMPROVED**
- ✅ Replaced broad try/except blocks with specific error handling
- ✅ Added proper input validation with descriptive error messages
- ✅ Implemented proper exception raising instead of error dictionaries

### **~~Magic Numbers and Hardcoded Values~~ ✅ ELIMINATED**
- ✅ All hardcoded values moved to `config.json`
- ✅ Default stats, dice configurations, and thresholds are now configurable
- ✅ Action economy rules and effect durations are configuration-driven

---

## 5. Enhanced Modular Cleanup ✅ **IMPLEMENTED**

### **Combat Configuration JSON ✅ IMPLEMENTED**
```json
{
  "default_stats": { "hp": 20, "ac": 10, "movement_speed": 30.0 },
  "dice_systems": { "initiative": "1d20", "default_damage": "1d6" },
  "action_economy": { "standard_actions_per_turn": 1, "bonus_actions_per_turn": 1 },
  "combat_mechanics": { "critical_hit_threshold": 20, "unconscious_hp_threshold": 0 },
  "field_mappings": { "hp_fields": ["hp", "HP"], "ac_fields": ["ac", "AC"] }
}
```

**Benefits Realized**: Game masters can now customize combat rules, dice systems, and mechanics without any programming knowledge. The system supports different rulesets and house rules through simple configuration changes.

### **Action Definition JSON ✅ IMPLEMENTED**
```json
{
  "basic_actions": { "melee_attack": { "requirements": ["weapon_equipped"], "tags": ["attack", "melee"] } },
  "spell_actions": { "fireball": { "resource_cost": {"spell_slot_3": 1}, "requirements": ["spell_level_3"] } },
  "class_specific": { "rage": { "requirements": ["class_barbarian", "level_1"] } }
}
```

**Benefits Realized**: Non-programmers can create custom actions, spells, and abilities. Community content can be easily shared and imported. Balance changes require no code deployment.

### **Status Effect Configuration ✅ IMPLEMENTED**
```json
{
  "conditions": { "stunned": { "effects": [{"type": "block_actions"}], "dispellable": true } },
  "buffs": { "haste": { "effects": [{"type": "speed_multiplier", "value": 2}] } },
  "damage_over_time": { "burning": { "effects": [{"type": "damage_over_time", "damage_type": "fire"}] } }
}
```

**Benefits Realized**: Status effects can be easily modified, new conditions can be added without code changes, and effect behavior is consistent and documented.

---

## 6. Performance & Scalability Improvements

### **Efficient Configuration Loading**
- Configuration is loaded once and cached with reload capability
- Merge algorithms ensure all required keys exist with sensible defaults
- Dot notation access provides clean, performant config queries

### **Optimized Action Validation**
- Action validation uses efficient data structures and early exit patterns
- Combatant data extraction is cached per validation cycle
- Status effect checks use optimized lookups

### **Memory Management**
- Combat logs are automatically trimmed to prevent memory bloat
- Configuration objects use efficient data structures
- Database operations are batched where possible

---

## 7. Future Enhancement Opportunities

### **Advanced Action System**
- Conditional actions that trigger based on complex game state
- Action chains and combo systems
- Dynamic action generation based on equipment combinations

### **Enhanced Status Effects**
- Multi-layered effect stacking rules
- Conditional effect triggers
- Status effect interactions and synergies

### **Configuration Extensions**
- Visual configuration editor for non-technical users
- Configuration validation and testing tools
- Hot-swappable configuration during gameplay

The combat system has been transformed from a basic implementation with hardcoded values and placeholder logic into a sophisticated, configuration-driven system that supports extensive customization while maintaining robust error handling and consistent behavior. All major maintenance concerns have been addressed, and the system now provides a solid foundation for future enhancements. 
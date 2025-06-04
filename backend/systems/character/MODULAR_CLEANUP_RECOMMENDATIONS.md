# Character System Modular Cleanup Recommendations

This document outlines specific opportunities to move hardcoded data and business rules into JSON configuration files, making the system more maintainable and allowing non-developers to modify game behavior.

## 1. Character Validation Rules → JSON Configuration

### Current Issue
Character validation rules are hardcoded in `CharacterBuilder.is_valid()`:
```python
if len(self.selected_feats) > 7:
    print(f"❌ Validation: Too many feats ({len(self.selected_feats)} > 7)")
if len(self.selected_skills) > 18:
    print(f"❌ Validation: Too many skills ({len(self.selected_skills)} > 18)")
```

### Recommended Solution
Create `data/character/validation_rules.json`:
```json
{
  "character_limits": {
    "max_feats_level_1": 7,
    "max_feats_per_level": 3,
    "max_skills": 18,
    "max_skill_rank": 20,
    "attribute_point_buy_total": 27,
    "min_attribute_value": 8,
    "max_attribute_value": 15
  },
  "validation_rules": {
    "required_fields": ["character_name", "race"],
    "name_min_length": 2,
    "name_max_length": 50,
    "name_forbidden_patterns": ["^admin", "^dm", "^gm"],
    "race_must_exist": true,
    "skills_must_exist": true
  }
}
```

### Benefits
- Game designers can adjust character limits without code changes
- Easy A/B testing of different balance configurations
- Prevents hardcoded magic numbers scattered throughout the codebase

## 2. Character Progression Rules → JSON Configuration

### Current Issue
Character progression calculations are hardcoded:
```python
"HP": level * (12 + calculate_ability_modifier(CON)),
"MP": (level * 8) + (calculate_ability_modifier(INT) * level),
"AC": 10 + calculate_ability_modifier(DEX),
```

### Recommended Solution
Create `data/character/progression_rules.json`:
```json
{
  "derived_stats": {
    "hit_points": {
      "base_per_level": 12,
      "constitution_modifier": true,
      "formula": "level * (base_per_level + CON_modifier)"
    },
    "magic_points": {
      "base_per_level": 8,
      "intelligence_scaling": true,
      "formula": "(level * base_per_level) + (INT_modifier * level)"
    },
    "armor_class": {
      "base_value": 10,
      "dexterity_modifier": true,
      "formula": "base_value + DEX_modifier"
    }
  },
  "level_progression": {
    "max_level": 20,
    "xp_requirements": [0, 300, 900, 2700, 6500, 14000, 23000, 34000, 48000, 64000],
    "feat_progression": [7, 10, 13, 16, 19],
    "skill_points_per_level": 4,
    "ability_score_improvements": [4, 8, 12, 16, 19]
  }
}
```

### Benefits
- Easy balance tweaking for different game modes
- Support for custom character advancement rules
- Clear documentation of how character stats are calculated

## 3. Hidden Personality Traits → JSON Configuration

### Current Issue
Personality generation is hardcoded with fixed lists:
```python
"core_motivation": random.choice([
    "Power", "Knowledge", "Revenge", "Redemption", "Adventure"
])
```

### Recommended Solution
Create `data/character/personality_traits.json`:
```json
{
  "trait_categories": {
    "core_motivations": {
      "weights": {
        "Power": 10,
        "Knowledge": 15,
        "Revenge": 8,
        "Redemption": 12,
        "Adventure": 20,
        "Family": 18,
        "Justice": 14,
        "Survival": 16,
        "Faith": 10,
        "Freedom": 17
      }
    },
    "secret_fears": {
      "weights": {
        "Abandonment": 12,
        "Failure": 15,
        "Death": 10,
        "Exposure": 8,
        "Powerlessness": 14,
        "Loss": 16,
        "Betrayal": 13,
        "Insignificance": 11,
        "Corruption": 9,
        "Isolation": 12
      }
    },
    "moral_compass_options": [
      "Ends justify means",
      "Honor above all", 
      "Protect the innocent",
      "Survival first",
      "Greater good",
      "Personal loyalty",
      "Divine will",
      "Natural order",
      "Individual freedom",
      "Perfect justice"
    ]
  },
  "personality_generation": {
    "use_weighted_selection": true,
    "allow_contradictory_traits": false,
    "min_traits_per_category": 1,
    "max_traits_per_category": 3
  }
}
```

### Benefits
- Narrative designers can add new personality traits without programming
- Weighted selection allows for more realistic personality distributions
- Easy customization for different game themes or settings

## 4. Prerequisite System → JSON Configuration

### Current Issue
Feat prerequisites are loaded from JSON but not properly validated:
```python
# TODO: Add prerequisite checking logic here
for prereq in feat.get("prerequisites", []):
    pass
```

### Recommended Solution
Enhance `data/builders/content/abilities.json` and create validation engine:
```json
{
  "feats": [
    {
      "name": "Combat Reflexes",
      "description": "Gain +2 initiative bonus",
      "prerequisites": [
        {
          "type": "attribute",
          "attribute": "DEX",
          "minimum_value": 13
        }
      ]
    },
    {
      "name": "Spell Focus",
      "description": "Increase spell save DC by 1",
      "prerequisites": [
        {
          "type": "feat",
          "required_feat": "Arcane Focus"
        },
        {
          "type": "level",
          "minimum_level": 3
        }
      ]
    }
  ]
}
```

Create `data/character/prerequisite_rules.json`:
```json
{
  "prerequisite_types": {
    "attribute": {
      "validator": "check_attribute_value",
      "error_message": "Requires {attribute} {minimum_value}+"
    },
    "feat": {
      "validator": "check_has_feat", 
      "error_message": "Requires feat: {required_feat}"
    },
    "level": {
      "validator": "check_character_level",
      "error_message": "Requires character level {minimum_level}+"
    },
    "skill": {
      "validator": "check_skill_rank",
      "error_message": "Requires {skill} skill rank {minimum_rank}+"
    }
  }
}
```

### Benefits
- Complex prerequisite chains become data-driven
- Easy to add new prerequisite types without code changes
- Clear error messages for players when prerequisites aren't met

## 5. Starting Equipment Packages → Enhanced JSON Configuration

### Current Issue
Starter kits are basic JSON but lack variety and customization:
```json
{
  "name": "Warrior Kit",
  "gold": 50,
  "equipment": ["Sword", "Shield", "Leather Armor"]
}
```

### Recommended Solution
Create `data/character/starter_packages.json`:
```json
{
  "starter_packages": {
    "warrior_basic": {
      "name": "Basic Warrior",
      "description": "Standard equipment for beginning fighters",
      "prerequisites": {
        "min_strength": 13
      },
      "gold": {
        "base_amount": 50,
        "random_bonus": "2d10"
      },
      "equipment": [
        {
          "category": "weapon",
          "choices": ["longsword", "battleaxe", "warhammer"],
          "selection_type": "choose_one"
        },
        {
          "category": "armor",
          "item": "leather_armor",
          "auto_equip": true
        },
        {
          "category": "shield", 
          "item": "wooden_shield",
          "condition": "if_one_handed_weapon"
        }
      ],
      "consumables": [
        {"item": "healing_potion", "quantity": 2},
        {"item": "rations", "quantity": 7}
      ]
    }
  },
  "equipment_rules": {
    "auto_equip_armor": true,
    "auto_equip_weapons": true,
    "stack_consumables": true,
    "validate_prerequisites": true
  }
}
```

### Benefits
- Rich starter package configuration without hardcoding
- Conditional equipment based on character choices
- Easy creation of themed starter packages for different backgrounds

## Implementation Strategy

### Phase 1: High Impact, Low Risk
1. **Character Validation Rules** - Move hardcoded limits to JSON
2. **Personality Traits** - Convert to weighted JSON configuration

### Phase 2: Moderate Impact, Moderate Risk  
3. **Progression Rules** - Extract stat calculation formulas
4. **Starter Equipment** - Enhanced package system

### Phase 3: High Impact, High Risk
5. **Prerequisite System** - Implement full validation engine

### Code Structure Changes

#### New Configuration Loader
```python
class CharacterConfigLoader:
    """Loads and validates character configuration from JSON files"""
    
    @staticmethod
    def load_validation_rules() -> Dict[str, Any]:
        return load_json('data/character/validation_rules.json')
    
    @staticmethod  
    def load_progression_rules() -> Dict[str, Any]:
        return load_json('data/character/progression_rules.json')
        
    @staticmethod
    def load_personality_config() -> Dict[str, Any]:
        return load_json('data/character/personality_traits.json')
```

#### Enhanced Validation Engine
```python
class CharacterValidator:
    """Validates character data against JSON configuration rules"""
    
    def __init__(self, config_loader: CharacterConfigLoader):
        self.rules = config_loader.load_validation_rules()
        
    def validate_character(self, builder: CharacterBuilder) -> List[str]:
        """Returns list of validation errors"""
        errors = []
        # Implementation based on JSON rules
        return errors
```

## Maintenance Benefits Summary

### For Developers
- Reduced hardcoded magic numbers
- Clearer separation of business logic and configuration
- Easier unit testing with mock configurations
- More maintainable codebase

### For Game Designers  
- No programming required to adjust character balance
- Easy A/B testing of different rule sets
- Rapid prototyping of new character options
- Clear documentation of game rules in JSON format

### For Players
- More consistent game balance
- Better error messages when character creation fails
- Potential for mod support through configuration overrides

## Risk Mitigation

### Validation
- JSON schema validation for all configuration files
- Runtime validation with fallback to hardcoded defaults
- Comprehensive unit tests for configuration loading

### Performance
- Configuration caching to avoid repeated file reads
- Lazy loading of configuration data
- Minimal runtime impact through preprocessing

### Backwards Compatibility
- Gradual migration approach
- Fallback to hardcoded values if JSON loading fails
- Version-controlled configuration schemas 
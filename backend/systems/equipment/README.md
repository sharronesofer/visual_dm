# Visual DM Equipment & Enchanting System

A comprehensive equipment management system for Visual DM featuring innovative learn-by-disenchanting mechanics, quality-based durability, and AI-driven content generation.

## 🌟 Features

### Core Equipment System
- **Quality Tiers**: Basic, Military, Noble with different durability and value multipliers
- **Time-Based Durability**: Automatic degradation over time based on quality
- **Rarity System**: Common, Rare, Epic, Legendary with varying ability counts
- **Ability Progression**: Level-gated ability revelation system
- **Set Bonuses**: Thematic equipment sets with synergistic bonuses

### Revolutionary Enchanting System
- **Learn-by-Disenchanting**: Must sacrifice items to learn new enchantments
- **Rarity Progression**: Basic → Military → Noble → Legendary access levels
- **Abilities Integration**: "Arcane Manipulation" ability governs enchanting capability
- **Risk/Reward Mechanics**: Failed disenchanting destroys items
- **Mastery System**: Enchantments improve with repeated application
- **Economic Stakes**: High costs prevent exploitation

### AI-Driven Features
- **Semantic Set Detection**: GPT-powered thematic grouping via embedding similarity
- **Dynamic Content**: AI generates enchantment descriptions and effects
- **Thematic Coherence**: Prevents weird combinations through AI validation

## 🏗️ Architecture

### Directory Structure
```
backend/systems/equipment/
├── models/
│   └── enchanting.py          # Core enchanting data models
├── services/
│   ├── enchanting_service.py  # Enchanting business logic
│   ├── equipment_quality.py   # Quality/durability management
│   └── durability_service.py  # Time-based degradation
├── repositories/
│   ├── enchanting_repository.py   # Enchanting data persistence
│   └── equipment_repository.py    # Equipment data persistence
├── routers/
│   ├── enchanting_router.py   # Enchanting API endpoints
│   └── __init__.py            # Main equipment API
├── schemas/
│   ├── enchanting_schemas.py  # Pydantic validation schemas
│   └── __init__.py           # Equipment schemas
├── events/
│   └── __init__.py           # Equipment event system
├── data/
│   └── sample_enchantments.json  # Example enchantments
└── examples/
    └── enchanting_demo.py     # Complete demo script
```

### Core Components

#### 1. Enchanting Models (`models/enchanting.py`)
- `EnchantmentDefinition`: Defines learnable enchantments
- `LearnedEnchantment`: Character's learned enchantments with mastery
- `DisenchantmentAttempt`: Records disenchanting attempts
- `EnchantmentApplication`: Records enchantment applications
- `CharacterEnchantingProfile`: Complete character progression

#### 2. Enchanting Service (`services/enchanting_service.py`)
- Risk calculation for disenchanting attempts
- Success probability based on skill and item quality
- Enchantment application with mastery progression
- Integration with economy and character systems

#### 3. Repository Pattern (`repositories/`)
- Clean data access abstraction
- JSON-based persistence (easily swappable)
- Character progression tracking
- Attempt/application history

#### 4. API Layer (`routers/`)
- RESTful endpoints for all enchanting operations
- Comprehensive request/response validation
- Error handling and event publishing
- Integration with main equipment API

## 🚀 Quick Start

### 1. Installation
```bash
# Install dependencies
pip install fastapi pydantic uuid pathlib

# Initialize the equipment system
cd backend/systems/equipment/
```

### 2. Run the Demo
```bash
python examples/enchanting_demo.py
```

This will demonstrate:
- Character learning enchantments by disenchanting items
- Applying learned enchantments to new equipment  
- Progression tracking and mastery system
- Equipment durability and quality mechanics

### 3. API Usage

Start the FastAPI server and use the enchanting endpoints:

```python
import requests

# Disenchant an item to learn enchantments
response = requests.post("/equipment/enchanting/disenchant", json={
    "character_id": "uuid-here",
    "item_id": "uuid-here", 
    "item_data": {
        "name": "Burning Sword",
        "quality": "military",
        "enchantments": ["flame_weapon"]
    },
    "arcane_manipulation_level": 5,
    "character_level": 10
})

# Apply learned enchantment to item
response = requests.post("/equipment/enchanting/enchant", json={
    "character_id": "uuid-here",
    "item_id": "uuid-here",
    "item_data": {"name": "Plain Armor", "quality": "basic", "type": "armor"},
    "enchantment_id": "flame_weapon",
    "gold_available": 1000
})
```

## 📖 API Documentation

### Enchanting Endpoints

#### `POST /equipment/enchanting/disenchant`
Attempt to learn enchantments by disenchanting an item.

**Request:**
```json
{
  "character_id": "uuid",
  "item_id": "uuid", 
  "item_data": {
    "name": "string",
    "quality": "basic|military|noble",
    "enchantments": ["enchantment_id_1", "enchantment_id_2"]
  },
  "arcane_manipulation_level": "integer (0-10)",
  "character_level": "integer (1-20)",
  "target_enchantment": "optional enchantment_id"
}
```

**Response:**
```json
{
  "success": "boolean",
  "outcome": "success_learned|success_known|partial_success|failure_safe|failure_destroyed|critical_failure",
  "enchantment_learned": "enchantment_id or null",
  "item_destroyed": "boolean",
  "experience_gained": "integer",
  "additional_consequences": ["string array"],
  "attempt_id": "uuid"
}
```

#### `POST /equipment/enchanting/enchant`
Apply a learned enchantment to an item.

**Request:**
```json
{
  "character_id": "uuid",
  "item_id": "uuid",
  "item_data": {
    "name": "string",
    "quality": "basic|military|noble", 
    "type": "weapon|armor|accessory|tool"
  },
  "enchantment_id": "string",
  "gold_available": "integer"
}
```

**Response:**
```json
{
  "success": "boolean",
  "cost_paid": "integer", 
  "final_power_level": "integer (1-100) or null",
  "mastery_increased": "boolean",
  "failure_reason": "string or null",
  "materials_lost": "boolean",
  "application_id": "uuid"
}
```

#### `GET /equipment/enchanting/character/{character_id}/available`
Get enchantments available for application to a specific item.

#### `GET /equipment/enchanting/item/learnable`
Get enchantments that can be learned from disenchanting an item.

#### `GET /equipment/enchanting/character/{character_id}/profile`
Get complete enchanting profile and statistics for a character.

### Equipment Endpoints

#### `POST /equipment/`
Create new equipment with quality-based properties.

#### `GET /equipment/{equipment_id}`
Get equipment details with current durability and revealed abilities.

#### `GET /equipment/`
List equipment with filtering options.

#### `DELETE /equipment/{equipment_id}`
Permanently delete equipment.

## 🔧 Configuration

### Environment Variables
```bash
# Core API Settings
ANTHROPIC_API_KEY=your_api_key_here    # Required for AI features
MODEL=claude-3-opus-20240229           # Claude model to use
MAX_TOKENS=8192                        # Max tokens for AI responses
TEMPERATURE=0.7                        # AI response creativity

# Enchanting Settings  
DEFAULT_SUBTASKS=5                     # Default subtasks for expansion
DEFAULT_PRIORITY=medium                # Default task priority
PERPLEXITY_API_KEY=your_key_here      # For research features
PERPLEXITY_MODEL=sonar-medium-online  # Perplexity model

# Data Storage
DATA_DIR=data/equipment               # Equipment data storage
ENCHANTING_DATA_DIR=data/enchanting   # Enchanting data storage
```

### Quality Configuration
Quality tiers are configured in `services/equipment_quality.py`:

```python
QUALITY_CONFIG = {
    "basic": {
        "durability_weeks": 1,      # Degrades in 1 week
        "repair_cost": 500,         # 500 gold base repair
        "value_multiplier": 1.0     # 1x base value
    },
    "military": {
        "durability_weeks": 2,      # Degrades in 2 weeks  
        "repair_cost": 750,         # 750 gold base repair
        "value_multiplier": 3.0     # 3x base value
    },
    "noble": {
        "durability_weeks": 4,      # Degrades in 4 weeks
        "repair_cost": 1500,        # 1500 gold base repair  
        "value_multiplier": 6.0     # 6x base value
    }
}
```

### Enchantment Configuration
Sample enchantments are defined in `data/sample_enchantments.json`. You can add custom enchantments by following the schema:

```json
{
  "enchantments": {
    "custom_enchant": {
      "id": "custom_enchant",
      "name": "Custom Enchantment",
      "description": "Description of what it does",
      "school": "elemental|protective|enhancement|utility|combat|mystical",
      "rarity": "basic|military|noble|legendary",
      "min_arcane_manipulation": 1,
      "base_cost": 500,
      "min_item_quality": "basic",
      "compatible_item_types": ["weapon", "armor"],
      "thematic_tags": ["fire", "damage"],
      "power_scaling": {
        "base_effect": 10.0,
        "effect_per_mastery": 2.0
      }
    }
  }
}
```

## 🎯 Integration Points

### Character System
- **Arcane Manipulation Ability**: Governs enchanting success rates
- **Character Level**: Affects identification limits and experience
- **Gold/Economy**: Required for enchantment applications

### Combat System  
- **Enchantment Effects**: Apply bonuses during combat calculations
- **Durability Loss**: Combat damage affects equipment condition
- **Set Bonuses**: Provide combat advantages

### Crafting System
- **Material Requirements**: Some enchantments require specific materials
- **Repair Materials**: Different qualities need different repair components

### Magic System
- **School Synergy**: Enchantment schools align with spell schools
- **Mana Integration**: Some enchantments affect mana costs/regeneration

## 🧪 Testing & Development

### Running Tests
```bash
# Run the demo to test all components
python examples/enchanting_demo.py

# Test specific components
python -m pytest tests/test_enchanting.py   # (when tests are added)
```

### Adding New Features

1. **New Enchantment Schools**: Add to `EnchantmentSchool` enum in `models/enchanting.py`
2. **New Quality Tiers**: Update `QUALITY_CONFIG` in `services/equipment_quality.py`  
3. **New Enchantments**: Add to `data/sample_enchantments.json` or register programmatically
4. **New API Endpoints**: Add to appropriate router in `routers/`

### Data Inspection
The system generates JSON files for easy inspection:
```bash
# View character enchanting profile
cat data/enchanting/profiles/{character_id}.json

# View equipment items  
cat data/equipment/items/{item_id}.json

# View disenchantment history
cat data/enchanting/attempts/{character_id}.json
```

## 🤝 Contributing

1. Follow the existing code structure and patterns
2. Add comprehensive docstrings to all functions
3. Update this README when adding major features
4. Consider the integration points with other Visual DM systems
5. Test thoroughly with the demo script

## 📄 License

Part of the Visual DM project. See main project license for details.

---

**🎮 Ready to enchant some equipment?** Run the demo script and watch the magic happen!

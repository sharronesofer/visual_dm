# Data Models Documentation

**Version:** 1.0.0
**Last Updated:** 2023-11-15
**Status:** Active

## Overview

This document provides comprehensive documentation for all data models, entity relationships, and database structures used in the Visual DM system. It serves as the authoritative reference for developers working with the persistence layer.

## Entity Relationship Diagram

![Entity Relationship Diagram](./diagrams/entity_relationship_diagram.png)

## Core Data Models

### Items

The `items` table stores information about all game items that can be acquired, used, or traded within the game.

#### Schema Definition

| Column Name | Data Type | Constraints | Description |
|-------------|-----------|-------------|-------------|
| id | UUID | PRIMARY KEY, DEFAULT gen_random_uuid() | Unique identifier for the item |
| name | VARCHAR(100) | NOT NULL | Name of the item |
| description | TEXT | NOT NULL | Detailed description of the item |
| type | item_type (ENUM) | NOT NULL | Type category of the item |
| weight | DECIMAL(10,2) | NOT NULL, CHECK (weight >= 0) | Weight of the item in game units |
| value | INTEGER | NOT NULL, CHECK (value >= 0) | Base value of the item in currency units |
| base_attributes | JSONB | NOT NULL, DEFAULT '{}' | JSON object containing item statistics |
| rarity_id | INTEGER | FOREIGN KEY | Reference to rarity tier |
| created_at | TIMESTAMP WITH TIME ZONE | DEFAULT CURRENT_TIMESTAMP | Creation timestamp |
| updated_at | TIMESTAMP WITH TIME ZONE | DEFAULT CURRENT_TIMESTAMP | Last update timestamp |

#### Indexes

| Index Name | Columns | Type | Purpose |
|------------|---------|------|---------|
| PRIMARY KEY | id | B-tree | Unique identifier lookup |
| idx_items_type | type | B-tree | Filter items by type |
| idx_items_name | name | B-tree | Search items by name |
| idx_items_value | value | B-tree | Sort/filter by value |
| idx_items_rarity | rarity_id | B-tree | Join with rarity table |

#### Enum Types

**item_type**
- `WEAPON`: Offensive equipment
- `ARMOR`: Defensive equipment
- `POTION`: Consumable with temporary effects
- `SCROLL`: One-time use magical item
- `MATERIAL`: Crafting components
- `TREASURE`: Valuable collectibles
- `KEY`: Items used to access locked areas or containers
- `QUEST`: Items related to quests
- `MISC`: Miscellaneous items

#### Triggers

- `update_items_updated_at`: Updates the `updated_at` field whenever an item is modified

#### Example Queries

```sql
-- Get all legendary weapons
SELECT i.* FROM items i
JOIN rarity_tiers r ON i.rarity_id = r.id
WHERE i.type = 'WEAPON' AND r.name = 'LEGENDARY';

-- Find items with specific stat
SELECT * FROM items
WHERE base_attributes->>'strength' IS NOT NULL AND (base_attributes->>'strength')::int > 10;
```

### Rarity Tiers

The `rarity_tiers` table defines the different levels of item rarity which affect item properties, appearance, and value.

#### Schema Definition

| Column Name | Data Type | Constraints | Description |
|-------------|-----------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Auto-incrementing identifier |
| name | item_rarity (ENUM) | NOT NULL, UNIQUE | Name of the rarity tier |
| probability | DECIMAL(5,4) | NOT NULL, CHECK (probability > 0 AND probability <= 1) | Chance of item having this rarity |
| value_multiplier | DECIMAL(10,2) | NOT NULL, CHECK (value_multiplier > 0) | Multiplication factor for item value |
| color_hex | VARCHAR(7) | NOT NULL, CHECK (color_hex ~ '^#[0-9A-Fa-f]{6}$') | Hex color code for UI display |
| created_at | TIMESTAMP WITH TIME ZONE | DEFAULT CURRENT_TIMESTAMP | Creation timestamp |

#### Enum Types

**item_rarity**
- `COMMON`: Standard items (white)
- `UNCOMMON`: Better than average items (green)
- `RARE`: Hard to find items (blue)
- `EPIC`: Very rare and powerful items (purple)
- `LEGENDARY`: Extremely rare and powerful items (orange)

#### Default Values

The system is pre-configured with the following rarity tiers:

| Name | Probability | Value Multiplier | Color |
|------|-------------|------------------|-------|
| COMMON | 0.6000 | 1.00 | #FFFFFF (White) |
| UNCOMMON | 0.2500 | 2.00 | #1EFF00 (Green) |
| RARE | 0.1000 | 5.00 | #0070DD (Blue) |
| EPIC | 0.0400 | 10.00 | #A335EE (Purple) |
| LEGENDARY | 0.0100 | 20.00 | #FF8000 (Orange) |

## Data Validation Rules

### Items Validation

1. Item weight must be non-negative
2. Item value must be non-negative
3. Item name must be between 1 and 100 characters
4. Item type must be one of the predefined enum values
5. Item base_attributes must be valid JSON

### Rarity Validation

1. Rarity probability must be between 0 and 1 (exclusive and inclusive respectively)
2. Value multiplier must be positive
3. Color hex must be a valid 6-digit hex color code preceded by #
4. Rarity name must be one of the predefined enum values

## Relationships

### Item to Rarity (Many-to-One)

Each item has one rarity tier, while each rarity tier can be associated with multiple items.

```
items.rarity_id → rarity_tiers.id
```

## Future Schema Extensions

The following extensions are planned for future development:

1. **Character Data**:
   - Character attributes and stats
   - Character progression and experience
   - Character appearance and customization

2. **Inventory Management**:
   - Player inventory tables
   - Container contents
   - Item stacking and quantity tracking

3. **World Components**:
   - Location data models
   - Environment properties
   - Scene configurations

4. **Quest System**:
   - Quest objectives and progress tracking
   - Quest rewards and dependencies
   - Quest state machine

5. **Combat System**:
   - Combat abilities and effects
   - Damage calculations and modifiers
   - Combat logs and results

## Change History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2023-11-15 | DB Architecture Team | Initial documentation |

## Best Practices

### JSON/JSONB Field Usage

- Use JSONB fields (like `base_attributes`) for flexible attributes that may vary between items
- Index frequently queried JSON paths using GIN indexes
- Validate JSON structure before insertion to maintain data integrity
- Use JSON path operators for efficient querying

### UUID Primary Keys

- Use UUID primary keys for tables that may require data migration or distributed generation
- Always use the `gen_random_uuid()` function from the pgcrypto extension for secure generation
- Index UUID columns used in frequent lookups

### Enum Types

- Use PostgreSQL enum types for fields with a predefined set of values
- Document all possible enum values in this documentation
- When adding new enum values, use ALTER TYPE commands and update this documentation 
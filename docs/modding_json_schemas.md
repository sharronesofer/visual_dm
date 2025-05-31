# Modding JSON Schemas: Visual DM

This document defines the canonical JSON schemas for all modular game data categories, enabling robust modding and world customization. Each schema is based on the audit in `hardcoded_data_audit.md`, the structure in `modular_data_for_modding.md`, and canonical lists/requirements in `Development_Bible.md`.

---

## Biomes/Regions (land_types.json)
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "BiomeType",
  "type": "object",
  "properties": {
    "id": { "type": "string", "description": "Unique biome ID (e.g., 'forest')" },
    "name": { "type": "string", "description": "Display name" },
    "description": { "type": "string" },
    "tags": { "type": "array", "items": { "type": "string" }, "description": "Biome tags (e.g., 'wet', 'cold')" },
    "color": { "type": "string", "description": "Hex color for map display" },
    "motif_weights": { "type": "object", "additionalProperties": { "type": "number" }, "description": "Motif weighting for this biome" }
  },
  "required": ["id", "name"]
}
```

**Example:**
```json
{
  "id": "forest",
  "name": "Forest",
  "description": "Dense woodland, high biodiversity.",
  "tags": ["wet", "temperate"],
  "color": "#228B22",
  "motif_weights": { "discovery": 0.2, "prosperity": 0.1 }
}
```

---

## Weapons (weapons.json)
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Weapon",
  "type": "object",
  "properties": {
    "id": { "type": "string" },
    "name": { "type": "string" },
    "damage_dice": { "type": "string", "description": "e.g. '1d8'" },
    "damage_type": { "type": "string" },
    "weapon_type": { "type": "string" },
    "properties": { "type": "array", "items": { "type": "string" } },
    "weight": { "type": "number" },
    "cost": { "type": "number" },
    "range_normal": { "type": ["number", "null"] },
    "range_long": { "type": ["number", "null"] },
    "versatile_damage": { "type": ["string", "null"] }
  },
  "required": ["id", "name", "damage_dice", "damage_type", "weapon_type"]
}
```

**Example:**
```json
{
  "id": "longsword",
  "name": "Longsword",
  "damage_dice": "1d8",
  "damage_type": "slashing",
  "weapon_type": "martial melee",
  "properties": ["versatile"],
  "weight": 3.0,
  "cost": 15,
  "range_normal": null,
  "range_long": null,
  "versatile_damage": "1d10"
}
```

---

## Armor (armor.json)
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Armor",
  "type": "object",
  "properties": {
    "id": { "type": "string" },
    "name": { "type": "string" },
    "armor_class": { "type": "number" },
    "slot": { "type": "string" },
    "weight": { "type": "number" },
    "cost": { "type": "number" },
    "rarity": { "type": "string" },
    "attributes": { "type": "object", "additionalProperties": true }
  },
  "required": ["id", "name", "armor_class", "slot"]
}
```

**Example:**
```json
{
  "id": "chainmail",
  "name": "Chain Mail",
  "armor_class": 16,
  "slot": "body",
  "weight": 40,
  "cost": 75,
  "rarity": "common",
  "attributes": { "stealth_disadvantage": true }
}
```

---

## Items (items.json)
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Item",
  "type": "object",
  "properties": {
    "id": { "type": "string" },
    "name": { "type": "string" },
    "type": { "type": "string" },
    "rarity": { "type": "string" },
    "value": { "type": "number" },
    "weight": { "type": "number" },
    "properties": { "type": "object", "additionalProperties": true },
    "stats": { "type": "object", "additionalProperties": true },
    "usage_effects": { "type": "array", "items": { "type": "object" } },
    "is_quest_item": { "type": "boolean" },
    "is_stackable": { "type": "boolean" },
    "max_stack_size": { "type": "number" },
    "is_equippable": { "type": "boolean" },
    "is_consumable": { "type": "boolean" },
    "is_tradable": { "type": "boolean" }
  },
  "required": ["id", "name", "type"]
}
```

**Example:**
```json
{
  "id": "healing_potion",
  "name": "Potion of Healing",
  "type": "consumable",
  "rarity": "common",
  "value": 50,
  "weight": 0.5,
  "properties": {},
  "stats": { "heal": 10 },
  "usage_effects": [{ "effect": "heal", "amount": 10 }],
  "is_quest_item": false,
  "is_stackable": true,
  "max_stack_size": 10,
  "is_equippable": false,
  "is_consumable": true,
  "is_tradable": true
}
```

---

## Races (races.json)
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Race",
  "type": "object",
  "properties": {
    "id": { "type": "string" },
    "name": { "type": "string" },
    "description": { "type": "string" },
    "size": { "type": "string" },
    "speed": { "type": "number" },
    "ability_score_increases": { "type": "object", "additionalProperties": { "type": "number" } },
    "racial_traits": { "type": "array", "items": { "type": "string" } },
    "languages": { "type": "array", "items": { "type": "string" } },
    "subraces": { "type": "array", "items": { "type": "object" } },
    "age_range": { "type": "object", "properties": { "min": { "type": "number" }, "max": { "type": "number" } } },
    "alignment_tendencies": { "type": "string" },
    "height_range": { "type": "object", "properties": { "min": { "type": "number" }, "max": { "type": "number" } } },
    "weight_range": { "type": "object", "properties": { "min": { "type": "number" }, "max": { "type": "number" } } }
  },
  "required": ["id", "name", "size", "speed"]
}
```

**Example:**
```json
{
  "id": "elf",
  "name": "Elf",
  "description": "Graceful, long-lived, attuned to magic.",
  "size": "Medium",
  "speed": 30,
  "ability_score_increases": { "dexterity": 2 },
  "racial_traits": ["Darkvision", "Keen Senses"],
  "languages": ["Common", "Elvish"],
  "subraces": [],
  "age_range": { "min": 100, "max": 750 },
  "alignment_tendencies": "Chaotic Good",
  "height_range": { "min": 5.0, "max": 6.5 },
  "weight_range": { "min": 100, "max": 150 }
}
```

---

## (Additional schemas for: POI/building_types, resources, trade_goods, spells, abilities, effects, quest_templates, motifs, sprite_manifest, animation, dialogue_templates, combat_rules, effect_types, worldgen_rules, spawn, religion, diplomacy, technology, custom_rules) -- to be added as migration proceeds.

---

## Notes
- All schemas are versioned and extensible.
- Use these as the basis for all modular data in data/builders/.
- Validate all JSON files against these schemas before loading.
- Update this document as new categories are modularized. 
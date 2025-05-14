# Asset Structure & Naming Conventions

This document defines the folder hierarchy, naming conventions, and guidelines for all sprite and animation assets in the project. Follow these standards to ensure consistency and ease of asset management.

## Folder Hierarchy

```
assets/
  characters/
    idle/
    walk/
    attack/
    death/
    special/
    head/
    torso/
    arms/
    legs/
    accessories/
  equipment/
    weapons/
    armor/
    consumables/
  regions/
    terrain/
    buildings/
    decorations/
    background/
  combat/
    overlays/      # Combat-specific overlay effects
    effects/       # Attack and ability effects
    indicators/    # Movement and range indicators
    status/        # Unit status effect indicators
  poi/
    markers/       # Points of interest markers
    interactions/  # POI interaction indicators
```

### Folder Explanations
- **characters/**: All character sprites and animation frames, organized by animation type and body part.
- **equipment/**: All equipment, item, and gear assets, organized by type.
- **regions/**: All environment and region assets, organized by asset type.
- **combat/**: All combat-specific assets and effects, organized by functionality.
- **poi/**: All points of interest assets and indicators, organized by type.

## Naming Conventions

- Use lowercase and underscores for all file and folder names.
- Animation frames: `character_[animation]_[frame].png` (e.g., `character_walk_001.png`)
- Body parts: `character_[part]_[variant].png` (e.g., `character_head_01.png`)
- Weapons: `weapon_[type]_[variant].png` (e.g., `weapon_sword_001.png`)
- Armor: `armor_[type]_[variant].png` (e.g., `armor_helmet_01.png`)
- Consumables: `consumable_[type]_[variant].png` (e.g., `consumable_potion_01.png`)
- Terrain: `terrain_[type]_[variant].png` (e.g., `terrain_forest_01.png`)
- Buildings: `building_[type]_[variant].png` (e.g., `building_castle_01.png`)
- Decorations: `decoration_[type]_[variant].png` (e.g., `decoration_tree_01.png`)
- Backgrounds: `background_[name].png` (e.g., `background_sunset.png`)
- Combat overlays: `combat_overlay_[type]_[variant].png` (e.g., `combat_overlay_range_01.png`)
- Combat effects: `combat_effect_[type]_[frame].png` (e.g., `combat_effect_fireball_001.png`)
- Combat indicators: `combat_indicator_[type]_[variant].png` (e.g., `combat_indicator_movement_01.png`)
- Status effects: `status_effect_[type]_[frame].png` (e.g., `status_effect_poison_001.png`)
- POI markers: `poi_marker_[type]_[variant].png` (e.g., `poi_marker_quest_01.png`)
- POI interactions: `poi_interaction_[type]_[variant].png` (e.g., `poi_interaction_dialog_01.png`)

## File Formats & Size Constraints

- **Sprites and animations**: PNG format, 32-bit color, transparent background
- **Recommended sizes**:
  - Character sprites: 64x64 px or 128x128 px
  - Equipment: 32x32 px or 64x64 px
  - Terrain tiles: 32x32 px
  - Decorations/buildings: variable, but use powers of two when possible
  - Combat overlays: 128x128 px
  - Combat effects: 64x64 px or 128x128 px
  - Combat indicators: 64x64 px
  - Status effects: 32x32 px
  - POI markers: 32x32 px
  - POI interactions: 32x32 px
- **Animation frames**: Use sequential numbering (e.g., 001, 002, 003)

## Guidelines for Adding New Assets

1. Place new assets in the correct subfolder according to type.
2. Name files according to the conventions above.
3. Use PNG format with transparent backgrounds.
4. For new animation types or asset categories, update this document and the relevant README.md.
5. Test new assets with the asset loader to ensure compatibility.

## Examples

- `assets/characters/idle/character_idle_001.png`
- `assets/characters/head/character_head_01.png`
- `assets/equipment/weapons/weapon_sword_001.png`
- `assets/regions/terrain/terrain_forest_01.png`
- `assets/regions/buildings/building_castle_01.png`
- `assets/combat/overlays/combat_overlay_range_01.png`
- `assets/combat/effects/combat_effect_fireball_001.png`
- `assets/combat/indicators/combat_indicator_movement_01.png`
- `assets/combat/status/status_effect_poison_001.png`
- `assets/poi/markers/poi_marker_quest_01.png`
- `assets/poi/interactions/poi_interaction_dialog_01.png`

---

For questions or updates, contact the art or engineering lead. 
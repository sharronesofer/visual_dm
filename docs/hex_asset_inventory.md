# Hex-Based Map Asset Inventory (Draft)

This document lists all required asset categories for both region and combat/POI hex maps, including technical specifications, style guidelines, and implementation requirements.

## Asset Categories

| Asset Type          | Example(s)                   | Dimensions (px) | Color Palette          | Style Notes                      | Region/Combat Usage |
|--------------------|-----------------------------|-----------------|-----------------------|----------------------------------|-------------------|
| Base Terrain       | Grass, Water, Forest        | 64x64          | Natural (#2E7D32, #1976D2) | Tileable, soft edges         | Both              |
| Elevation Overlay  | Hills, Mountains, Cliffs    | 64x64          | Grayscale + Tint (#000000 @ 20%) | Height-indicating shading | Both              |
| Terrain Features   | Rocks, Trees, Bushes        | 32x32, 64x64   | Natural (#795548, #33691E) | Varied shapes, organic       | Both              |
| Terrain Overlay    | Fog, Highlight, Path        | 64x64          | White (#FFFFFF @ 40%), Yellow (#FFD700 @ 60%) | Semi-transparent | Both              |
| Structure          | Village, Castle, Ruins      | 64x64          | Stone (#9E9E9E), Wood (#795548) | Isometric, shadowed      | Both              |
| Unit/Character     | Player, NPC, Enemy          | 64x64          | Faction (see color table) | Distinct silhouettes         | Both              |
| Resource Node      | Gold, Wood, Food            | 32x32          | Gold (#FFD700), Brown (#795548) | Iconic, readable        | Both              |
| POI Indicator      | Shrine, Dungeon, Quest      | 32x32          | Varies (see color table) | Simple, high-contrast        | Both              |
| Status Effect      | Poison, Stun, Buff          | 32x32          | Green (#4CAF50), Purple (#9C27B0) | Overlay badge         | Combat            |
| Action Effect      | Spell, Attack, Heal         | 64x64          | Bright (see effects table) | Particle or frame-based     | Combat            |
| UI Element         | Hex Selector, Cursor        | 32x32, 64x64   | UI theme (#2196F3 @ 60%) | High-contrast, visible       | Both              |
| Weather Effect     | Rain, Snow, Fog             | 64x64          | Blue (#BBDEFB), White (#FFFFFF) | Animated, transparent  | Both              |
| Transition FX      | Fade, Zoom, Slide           | 128x128+       | Black (#000000), White (#FFFFFF) | Smooth transitions    | Both              |
| Combat Overlay     | Cover, Movement Range       | 64x64          | UI (#2196F3 @ 40%)      | Semi-transparent, tactical     | Combat            |
| Line of Sight      | Vision Cone, Range Circle   | 64x64          | UI (#FFC107 @ 50%)      | Clear boundaries              | Combat            |
| Area Effect        | Spell Area, Attack Range    | 64x64          | UI (#F44336 @ 40%)      | Pattern-based, tactical       | Combat            |
| Asset Variation    | Grass1, Grass2, etc.        | 64x64          | Base palette variations  | Subtle differences           | Both              |
| Pathfinding       | Path Preview, Movement Cost | 32x32          | UI (#4CAF50 @ 60%)      | Clear direction indicators    | Both              |
| Territory Control | Faction Borders, Influence  | 64x64          | Faction colors @ 30%     | Clear ownership indication   | Both              |
| Day/Night Cycle   | Dawn, Day, Dusk, Night     | 64x64          | Time-based overlays      | Gradual transitions         | Both              |
| Season Variation  | Spring, Summer, Fall, Winter| 64x64          | Seasonal palettes        | Distinct seasonal looks     | Both              |
| Environmental Hazard| Fire, Poison, Ice         | 32x32, 64x64   | Hazard-specific colors   | Clear danger indication    | Both              |

## Technical Requirements

### Color Palettes

**Faction Colors:**
- Player Faction: #1976D2 (Blue)
- Allied Faction: #4CAF50 (Green)
- Enemy Faction: #F44336 (Red)
- Neutral Faction: #9E9E9E (Gray)
- Special Faction: #9C27B0 (Purple)

**UI Theme:**
- Primary: #2196F3 (Blue)
- Secondary: #FFC107 (Amber)
- Success: #4CAF50 (Green)
- Warning: #FF9800 (Orange)
- Danger: #F44336 (Red)
- Info: #00BCD4 (Cyan)
- Neutral: #9E9E9E (Gray)

**Effect Colors:**
- Healing: #4CAF50 (Green)
- Damage: #F44336 (Red)
- Magic: #9C27B0 (Purple)
- Buff: #2196F3 (Blue)
- Debuff: #FF9800 (Orange)

### Animation Specifications

**Frame Requirements:**
- Combat Effects: 8-12 frames @ 30fps
- Weather Effects: 16-24 frames @ 24fps
- UI Animations: 4-8 frames @ 30fps
- Transitions: 12-16 frames @ 60fps

**Particle System Limits:**
- Maximum particles per effect: 100
- Maximum concurrent effects: 10
- Particle lifetime: 0.5-2.0 seconds
- Emission rate: 10-50 particles/second

### File Naming Convention

Format: `category_subtype_variant_size.png`

Example:
- terrain_grass_01_64.png
- effect_fire_01_32.png
- ui_selector_blue_64.png

### Texture Atlas Specifications

**Region Atlas:**
- Dimensions: 2048x2048
- Format: PNG-8 with alpha
- Maximum individual sprite size: 128x128
- Padding: 2px between sprites

**Combat Atlas:**
- Dimensions: 1024x1024
- Format: PNG-8 with alpha
- Maximum individual sprite size: 64x64
- Padding: 1px between sprites

**UI Atlas:**
- Dimensions: 512x512
- Format: PNG-8 with alpha
- Maximum individual sprite size: 64x64
- Padding: 1px between sprites

### Memory Budgets

**Per Category (Maximum):**
- Terrain: 8MB
- Effects: 4MB
- UI Elements: 2MB
- Characters: 4MB
- Weather: 2MB
- Overlays: 2MB

### Mobile Platform Requirements

**Compression Settings:**
- PNG-8 for UI and icons
- DXT5/BC3 for terrain and effects
- ETC2 for Android devices
- ASTC 4x4 for iOS devices

**Performance Targets:**
- Maximum texture memory: 128MB
- Maximum draw calls per frame: 100
- Target frame rate: 60fps
- Minimum frame rate: 30fps

## Implementation Notes

- Region and combat maps share many base assets but may use different detail levels
- Weather effects should properly interact with terrain and structure assets
- Status and combat effects need clear visual hierarchy to avoid confusion
- UI elements should remain visible and functional at all zoom levels
- Transition effects should smoothly handle both zoom and state changes
- Pathfinding visualizations should clearly indicate movement costs and restrictions
- Line of sight and area effects should work with the fog of war system
- Asset variations should be used strategically to break up visual repetition

## Asset Organization

- Assets will be organized in a directory structure matching the categories above
- Each category will have its own sprite sheet/texture atlas
- Variations will be numbered consistently (e.g., grass_01, grass_02)
- Combat-specific assets will be kept in separate directories for easier management
- Weather and effect animations will be organized by type and severity

## Performance Considerations

- Texture atlases will be optimized for minimal draw calls
- LOD (Level of Detail) variants will be provided for region-level zoom
- Particle effects will be designed for efficient batching
- Animation frame counts will be optimized for memory usage
- Asset dimensions will be standardized for efficient memory use on mobile platforms

This inventory should be reviewed and updated as new requirements emerge during development. Asset creation should prioritize the most frequently used elements first, particularly the base terrain and UI elements needed for core gameplay functionality. 
# Terrain Sprite Sheet: fantasyhextiles_v3.png

This directory contains the main terrain sprite sheet for the Visual DM client.

## Sprite Sheet Overview
- **File:** `fantasyhextiles_v3.png`
- **Format:** PNG, grid-based hex tiles
- **Usage:** All terrain types for the hex-based map are sourced from this sheet.

## Supported Terrain Types
The following terrain types are supported and should be represented in the sprite sheet:

| Terrain Type | Example Variations           | Notes                                 |
|--------------|-----------------------------|---------------------------------------|
| plains       | grass, wildflowers          | Default walkable terrain              |
| forest       | dense, sparse, autumn       | May include seasonal variations       |
| mountain     | rocky, snowy, volcanic      | Impassable or high movement cost      |
| water        | river, lake, ocean          | Includes shallow/deep variants        |
| desert       | sand, dunes, oasis          | May include rocky desert              |
| swamp        | marsh, bog, reeds           | Difficult terrain, may be impassable  |
| urban        | village, city, ruins        | For settlements and POIs              |
| tundra       | snow, ice, permafrost       | Optional, for cold regions            |
| coast        | beach, cliffs               | Transition between land and water     |
| dungeon      | cave, ruins, underground    | For special map areas                 |

## Naming and Organization
- Each tile in the sheet should be consistently sized (e.g., 64x64 or 128x128 px per hex tile).
- Variations for each terrain type should be grouped together.
- Transition tiles (e.g., grass-to-forest, water-to-coast) should be included for seamless blending.
- Use clear layer ordering: base terrain, overlays (features), transitions.

## Integration Notes
- The asset manager loads this sheet and slices tiles by grid position.
- Terrain type mapping is handled in code (see `TerrainType` enums in both Python and TypeScript).
- To add new terrain types or variations, update this README and the sprite sheet accordingly.

## Artist Guidelines
- Maintain a consistent art style and color palette.
- Ensure all tiles align perfectly for seamless map rendering.
- Provide at least 2-3 variations per terrain type for visual diversity.
- Save the sprite sheet in lossless PNG format.

---

_Last updated: 2024-06-09_ 
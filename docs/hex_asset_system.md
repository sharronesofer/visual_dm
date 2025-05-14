# Hex-Based Asset Management System Documentation

## Overview
This document provides technical specifications, organization structure, naming conventions, integration guidelines, and best practices for the hex-based asset management system used in terrain generation and variation.

---

## 1. Asset Organization Structure

```
/assets/
  /terrain/
    /base/         # Base terrain tiles (e.g., grass, water, sand, etc.)
    /features/     # Terrain features (trees, rocks, bushes, flowers)
    /overlays/     # Overlays (elevation, shadows, transitions)
    /variations/   # Seasonal and weather variations
```

### Example File Layout
```
assets/terrain/base/grass_01.png
assets/terrain/base/water_03.png
assets/terrain/features/tree_oak_02.png
assets/terrain/overlays/shadow_north_01.png
assets/terrain/variations/winter_grass_01.png
assets/terrain/variations/rain_tree_oak_02.png
```

---

## 2. Asset Specifications

- **Dimensions:** 64x64 pixels, RGBA (transparent background)
- **Format:** PNG (lossless, supports alpha)
- **Naming Convention:**
  - Base: `<terrain_type>_<variation_num:02d>.png`
  - Feature: `<feature_type>_<variation_num:02d>.png`
  - Overlay: `<overlay_type>_<direction>_<variation_num:02d>.png`
  - Variation: `<season|weather>_<asset_name>.png`
- **Color Palettes:** Distinct for each terrain/feature type; see code for palette details
- **Alignment:** Centered for compositing; overlays designed for hex grid alignment

---

## 3. Integration Guidelines

### Loading Assets
- Use the `AssetManager` class (`src/assets/AssetManager.ts`) for all asset loading and caching.
- Example: Load all grass terrain variations:
  ```typescript
  const assetManager = new AssetManager();
  const grassTiles = await assetManager.loadTerrainSet('grass');
  ```
- Batch load features or overlays similarly:
  ```typescript
  const trees = await assetManager.loadFeatureVariations('tree_oak');
  const shadows = await assetManager.loadBatch([
    '/assets/terrain/overlays/shadow_north_01.png',
    '/assets/terrain/overlays/shadow_east_01.png',
  ]);
  ```
- Load seasonal/weather variations:
  ```typescript
  const winterGrass = await assetManager.loadSeasonalVariations('grass_01.png');
  ```

### Caching & Memory Management
- The AssetManager uses LRU eviction to manage memory.
- Default cache size is 200 assets; can be configured in the constructor.
- Preload common assets at game start for smoother gameplay.
- Unload assets not needed for current scene to free memory.

### Error Handling
- AssetManager provides fallback images for missing/corrupt assets.
- Errors are logged with context for debugging.

### Compositing
- All assets are 64x64 and centered, allowing easy compositing:
  - Place base terrain, then overlay features and overlays as needed.
  - Use alpha blending for overlays (elevation, shadow, fog, etc.).

---

## 4. Performance Optimization Tips
- Preload assets for visible map regions before rendering.
- Use batch loading for groups of assets to minimize network requests.
- Adjust cache size based on device memory constraints.
- Use overlays and variations to reduce the number of unique base assets needed.
- Profile asset loading and cache hit rates during development.

---

## 5. Visual Guides

### Example: Compositing a Hex Tile
1. **Base Terrain:** `grass_01.png`
2. **Feature:** `tree_oak_02.png`
3. **Overlay:** `shadow_north_01.png`
4. **Variation:** `winter_grass_01.png` (if in winter season)

Layer order:
```
[Variation/Seasonal] (optional)
[Overlay] (e.g., shadow/elevation)
[Feature] (e.g., tree, rock)
[Base Terrain]
```

---

## 6. Troubleshooting
- **Missing Asset:** Check file path and naming convention; AssetManager will use fallback if not found.
- **Visual Artifacts:** Ensure all assets are 64x64 and use correct alpha channel.
- **Performance Issues:** Profile cache size and asset loading patterns; increase cache or optimize preloading.
- **Compositing Misalignment:** Verify all assets are centered and overlays are designed for hex grid.

---

## 7. Best Practices
- Use the provided Python scripts for asset generation to ensure consistency.
- Keep asset directories organized and avoid duplicate names.
- Document any new asset types or naming conventions in this file.
- Regularly review and update integration code to match asset structure changes.

---

## 8. References
- See `tools/asset_generation/` for asset generation scripts.
- See `src/assets/AssetManager.ts` for asset loading/caching implementation.
- For questions or issues, consult this documentation or contact the asset pipeline maintainer. 
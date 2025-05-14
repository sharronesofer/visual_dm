// characterSpriteLoader.ts
// Utility to load all assets for a CharacterSprite using SpriteManager and asset index

import CharacterSprite, { CharacterSpriteLayerType, CharacterSpriteLayer } from './CharacterSprite';
import { characterAssetIndex, CharacterAssetMeta } from './characterAssetIndex';
import SpriteManager, { Sprite } from '../services/SpriteManager';

/**
 * Map of layer type to loaded sprite frames for that layer.
 */
export type CharacterSpriteLoadedAssets = {
  [layer in CharacterSpriteLayerType]?: Sprite[];
};

/**
 * Loads all assets for a CharacterSprite for a given animation (e.g., 'idle', 'walk').
 * Uses SpriteManager and characterAssetIndex. Handles missing assets gracefully.
 * @param sprite CharacterSprite instance
 * @param animationTag Animation tag to load (e.g., 'idle', 'walk', 'attack')
 * @returns Promise<CharacterSpriteLoadedAssets>
 */
export async function loadCharacterSpriteAssets(
  sprite: CharacterSprite,
  animationTag: string
): Promise<CharacterSpriteLoadedAssets> {
  const manager = SpriteManager.getInstance();
  const loaded: CharacterSpriteLoadedAssets = {};
  for (const layer of sprite.getOrderedLayers()) {
    // Find asset meta for this layer and animation
    const index = characterAssetIndex[layer.type];
    if (!index) continue;
    // Try to find a variant matching the asset key
    const variants = Object.entries(index).find(([variant]) => layer.asset.includes(variant));
    if (!variants) {
      console.warn(`No asset variant found for layer ${layer.type} asset ${layer.asset}`);
      continue;
    }
    const [variant, metas] = variants;
    // Find meta for the requested animationTag
    const meta = metas.find(m => m.tags?.includes(animationTag));
    if (!meta) {
      console.warn(`No asset meta for ${layer.type} variant ${variant} animation ${animationTag}`);
      continue;
    }
    // Load sprite or sprite sheet
    try {
      let frames: Sprite[];
      if (meta.frames > 1) {
        frames = await manager.loadSpriteSheet(meta.path, layer.frame ?? 32, layer.frame ?? 32); // Default 32x32
      } else {
        const sprite = await manager.loadSprite(meta.path);
        frames = [sprite];
      }
      loaded[layer.type] = frames;
    } catch (e) {
      console.warn(`Failed to load asset for ${layer.type} ${variant}:`, e);
    }
  }
  return loaded;
}

// CharacterSpriteAnimator.ts
// Synchronizes animation frames across all character sprite layers

import { CharacterSpriteLoadedAssets } from './characterSpriteLoader';
import { CharacterSpriteLayerType } from './CharacterSprite';
import { Sprite, applyTintToSprite } from '../services/SpriteManager';

/**
 * CharacterSpriteAnimator synchronizes animation frames across all layers.
 */
export class CharacterSpriteAnimator {
  private assets: CharacterSpriteLoadedAssets;

  /**
   * @param assets Loaded assets for all layers (from loader)
   */
  constructor(assets: CharacterSpriteLoadedAssets) {
    this.assets = assets;
  }

  /**
   * Get the current frame for each layer at a given animation tick, applying tints if provided.
   * @param tick Animation tick (frame index)
   * @param tints Optional map of layer type to tint
   * @returns Map of layer type to Sprite for this tick
   */
  public getFrameForTick(
    tick: number,
    tints?: {
      [layer in CharacterSpriteLayerType]?:
        | string
        | { r: number; g: number; b: number; a?: number };
    }
  ): { [layer in CharacterSpriteLayerType]?: Sprite } {
    const frameMap: { [layer in CharacterSpriteLayerType]?: Sprite } = {};
    for (const layerType of Object.keys(this.assets) as CharacterSpriteLayerType[]) {
      const frames = this.assets[layerType];
      if (!frames || frames.length === 0) continue;
      let sprite: Sprite;
      if (frames.length === 1) {
        sprite = frames[0];
      } else {
        const idx = tick % frames.length;
        sprite = frames[idx];
      }
      // Apply tint if provided
      const tint = tints?.[layerType];
      frameMap[layerType] = tint ? applyTintToSprite(sprite, tint) : sprite;
    }
    return frameMap;
  }
}

export default CharacterSpriteAnimator;

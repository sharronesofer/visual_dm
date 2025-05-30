from typing import Any, Dict



/**
 * CharacterSpriteAnimator synchronizes animation frames across all layers.
 */
class CharacterSpriteAnimator {
  private assets: CharacterSpriteLoadedAssets
  /**
   * @param assets Loaded assets for all layers (from loader)
   */
  constructor(assets: CharacterSpriteLoadedAssets) {
    this.assets = assets
  }
  /**
   * Get the current frame for each layer at a given animation tick, applying tints if provided.
   * @param tick Animation tick (frame index)
   * @param tints Optional map of layer type to tint
   * @returns Map of layer type to Sprite for this tick
   */
  public getFrameForTick(
    tick: float,
    tints?: {
      [layer in CharacterSpriteLayerType]?:
        | string
        | { r: float; g: float; b: float; a?: float }
    }
  ): { [layer in CharacterSpriteLayerType]?: Sprite } {
    const frameMap: Dict[str, Any] = {}
    for (const layerType of Object.keys(this.assets) as CharacterSpriteLayerType[]) {
      const frames = this.assets[layerType]
      if (!frames || frames.length === 0) continue
      let sprite: Sprite
      if (frames.length === 1) {
        sprite = frames[0]
      } else {
        const idx = tick % frames.length
        sprite = frames[idx]
      }
      const tint = tints?.[layerType]
      frameMap[layerType] = tint ? applyTintToSprite(sprite, tint) : sprite
    }
    return frameMap
  }
}
default CharacterSpriteAnimator
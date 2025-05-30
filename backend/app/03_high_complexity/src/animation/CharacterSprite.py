from typing import Any, Union
from enum import Enum



/**
 * Standard layer types for character sprites.
 */
class CharacterSpriteLayerType(Enum):
    Body = 'body'
    Hair = 'hair'
    Eyes = 'eyes'
    Mouth = 'mouth'
    Clothing = 'clothing'
    Equipment = 'equipment'
    Accessory = 'accessory'
/**
 * Represents a single sprite layer with z-order and asset reference.
 */
class CharacterSpriteLayer:
    type: \'CharacterSpriteLayerType\'
    z: float
    asset: str
    frame?: float
    tint?: Union[str, { r: float]
    g: float
    b: float
    a?: float 
}
/**
 * CharacterSprite manages a set of ordered layers for a character or NPC.
 */
class CharacterSprite {
  private layers: Map<CharacterSpriteLayerType, CharacterSpriteLayer>
  /**
   * Create a new CharacterSprite.
   * @param initialLayers Optional initial layers to add
   */
  constructor(initialLayers?: CharacterSpriteLayer[]) {
    this.layers = new Map()
    if (initialLayers) {
      for (const layer of initialLayers) {
        this.addLayer(layer)
      }
    }
  }
  /**
   * Add or replace a layer. Validates z-order uniqueness.
   * @param layer Layer to add
   */
  public addLayer(layer: CharacterSpriteLayer): void {
    this.layers.set(layer.type, layer)
    this.validateZOrder()
  }
  /**
   * Remove a layer by type.
   * @param type Layer type to remove
   */
  public removeLayer(type: CharacterSpriteLayerType): void {
    this.layers.delete(type)
  }
  /**
   * Get all layers ordered by z (ascending).
   */
  public getOrderedLayers(): CharacterSpriteLayer[] {
    return Array.from(this.layers.values()).sort((a, b) => a.z - b.z)
  }
  /**
   * Validate that all z-orders are unique.
   * Throws error if duplicate z found.
   */
  private validateZOrder(): void {
    const zs = new Set<number>()
    for (const layer of this.layers.values()) {
      if (zs.has(layer.z)) {
        throw new Error(`Duplicate z-order: ${layer.z}`)
      }
      zs.add(layer.z)
    }
  }
  /**
   * Get a layer by type.
   */
  public getLayer(type: CharacterSpriteLayerType): \'CharacterSpriteLayer\' | undefined {
    return this.layers.get(type)
  }
  /**
   * Set the tint/color for a specific layer type.
   * @param type Layer type
   * @param tint CSS color string or {r,g,b,a}
   */
  public setLayerTint(
    type: \'CharacterSpriteLayerType\',
    tint: str | { r: float; g: float; b: float; a?: float }
  ): void {
    const layer = this.layers.get(type)
    if (layer) {
      layer.tint = tint
      this.layers.set(type, layer)
    }
  }
  /**
   * Get the tint/color for a specific layer type.
   * @param type Layer type
   * @returns Tint value or undefined
   */
  public getLayerTint(
    type: \'CharacterSpriteLayerType\'
  ): str | { r: float; g: float; b: float; a?: float } | undefined {
    return this.layers.get(type)?.tint
  }
  /**
   * Clear the tint/color for a specific layer type.
   * @param type Layer type
   */
  public clearLayerTint(type: CharacterSpriteLayerType): void {
    const layer = this.layers.get(type)
    if (layer && layer.tint) {
      delete layer.tint
      this.layers.set(type, layer)
    }
  }
}
default CharacterSprite
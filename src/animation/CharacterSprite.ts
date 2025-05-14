// CharacterSprite.ts
// Foundation for modular, layered character sprites

/**
 * Standard layer types for character sprites.
 */
export enum CharacterSpriteLayerType {
  Body = 'body',
  Hair = 'hair',
  Eyes = 'eyes',
  Mouth = 'mouth',
  Clothing = 'clothing',
  Equipment = 'equipment',
  Accessory = 'accessory',
  // Add more as needed
}

/**
 * Represents a single sprite layer with z-order and asset reference.
 */
export interface CharacterSpriteLayer {
  type: CharacterSpriteLayerType;
  z: number;
  asset: string; // Path or key to sprite asset
  frame?: number; // Animation frame index (optional)
  tint?: string | { r: number; g: number; b: number; a?: number }; // Optional per-layer tint
}

/**
 * CharacterSprite manages a set of ordered layers for a character or NPC.
 */
export class CharacterSprite {
  private layers: Map<CharacterSpriteLayerType, CharacterSpriteLayer>;

  /**
   * Create a new CharacterSprite.
   * @param initialLayers Optional initial layers to add
   */
  constructor(initialLayers?: CharacterSpriteLayer[]) {
    this.layers = new Map();
    if (initialLayers) {
      for (const layer of initialLayers) {
        this.addLayer(layer);
      }
    }
  }

  /**
   * Add or replace a layer. Validates z-order uniqueness.
   * @param layer Layer to add
   */
  public addLayer(layer: CharacterSpriteLayer): void {
    // Ensure only one layer per type
    this.layers.set(layer.type, layer);
    this.validateZOrder();
  }

  /**
   * Remove a layer by type.
   * @param type Layer type to remove
   */
  public removeLayer(type: CharacterSpriteLayerType): void {
    this.layers.delete(type);
  }

  /**
   * Get all layers ordered by z (ascending).
   */
  public getOrderedLayers(): CharacterSpriteLayer[] {
    return Array.from(this.layers.values()).sort((a, b) => a.z - b.z);
  }

  /**
   * Validate that all z-orders are unique.
   * Throws error if duplicate z found.
   */
  private validateZOrder(): void {
    const zs = new Set<number>();
    for (const layer of this.layers.values()) {
      if (zs.has(layer.z)) {
        throw new Error(`Duplicate z-order: ${layer.z}`);
      }
      zs.add(layer.z);
    }
  }

  /**
   * Get a layer by type.
   */
  public getLayer(type: CharacterSpriteLayerType): CharacterSpriteLayer | undefined {
    return this.layers.get(type);
  }

  /**
   * Set the tint/color for a specific layer type.
   * @param type Layer type
   * @param tint CSS color string or {r,g,b,a}
   */
  public setLayerTint(
    type: CharacterSpriteLayerType,
    tint: string | { r: number; g: number; b: number; a?: number }
  ): void {
    const layer = this.layers.get(type);
    if (layer) {
      layer.tint = tint;
      this.layers.set(type, layer);
    }
  }

  /**
   * Get the tint/color for a specific layer type.
   * @param type Layer type
   * @returns Tint value or undefined
   */
  public getLayerTint(
    type: CharacterSpriteLayerType
  ): string | { r: number; g: number; b: number; a?: number } | undefined {
    return this.layers.get(type)?.tint;
  }

  /**
   * Clear the tint/color for a specific layer type.
   * @param type Layer type
   */
  public clearLayerTint(type: CharacterSpriteLayerType): void {
    const layer = this.layers.get(type);
    if (layer && layer.tint) {
      delete layer.tint;
      this.layers.set(type, layer);
    }
  }
}

export default CharacterSprite;

import { Point, LightSource, Tile } from './types';

export class LightingSystem {
  private lightSources: Map<string, LightSource> = new Map();
  private lightingCache: Map<string, number> = new Map();
  private readonly maxLightLevel: number = 1.0;
  private readonly minLightLevel: number = 0.1;
  private readonly ambientLight: number = 0.2;

  constructor() {}

  private getLightKey(x: number, y: number): string {
    return `${x},${y}`;
  }

  public addLightSource(source: LightSource): void {
    this.lightSources.set(source.position.x + ',' + source.position.y, source);
    this.invalidateCache();
  }

  public removeLightSource(x: number, y: number): void {
    this.lightSources.delete(x + ',' + y);
    this.invalidateCache();
  }

  public updateLightSource(source: LightSource): void {
    const key = source.position.x + ',' + source.position.y;
    if (this.lightSources.has(key)) {
      this.lightSources.set(key, source);
      this.invalidateCache();
    }
  }

  private invalidateCache(): void {
    this.lightingCache.clear();
  }

  private calculateDistance(p1: Point, p2: Point): number {
    const dx = p2.x - p1.x;
    const dy = p2.y - p1.y;
    return Math.sqrt(dx * dx + dy * dy);
  }

  private calculateLightIntensity(tile: Point, source: LightSource): number {
    const distance = this.calculateDistance(tile, source.position);
    if (distance > source.radius) {
      return 0;
    }

    // Linear falloff with distance
    const intensity = (1 - distance / source.radius) * source.intensity;
    return Math.max(0, Math.min(this.maxLightLevel, intensity));
  }

  public calculateTileLighting(tile: Tile): number {
    const key = this.getLightKey(tile.position.x, tile.position.y);
    let lighting = this.lightingCache.get(key);

    if (lighting === undefined) {
      lighting = this.ambientLight;

      for (const source of this.lightSources.values()) {
        const intensity = this.calculateLightIntensity(tile.position, source);
        // Additive blending of light sources
        lighting = Math.min(this.maxLightLevel, lighting + intensity);
      }

      // Apply elevation effects
      const elevationFactor = 1 + (tile.elevation / 10); // Higher elevation gets more light
      lighting *= elevationFactor;

      // Clamp final value
      lighting = Math.max(this.minLightLevel, Math.min(this.maxLightLevel, lighting));

      this.lightingCache.set(key, lighting);
    }

    return lighting;
  }

  public getLightColor(tile: Tile): string {
    const lighting = this.calculateTileLighting(tile);
    const nearestSource = this.findNearestLightSource(tile.position);
    
    if (!nearestSource) {
      // Convert ambient light level to grayscale
      const value = Math.floor(lighting * 255);
      return `rgb(${value},${value},${value})`;
    }

    // Blend light source color with ambient light
    const color = this.parseColor(nearestSource.color);
    const r = Math.floor(color.r * lighting);
    const g = Math.floor(color.g * lighting);
    const b = Math.floor(color.b * lighting);
    
    return `rgb(${r},${g},${b})`;
  }

  private findNearestLightSource(position: Point): LightSource | null {
    let nearest: LightSource | null = null;
    let minDistance = Infinity;

    for (const source of this.lightSources.values()) {
      const distance = this.calculateDistance(position, source.position);
      if (distance < minDistance && distance <= source.radius) {
        minDistance = distance;
        nearest = source;
      }
    }

    return nearest;
  }

  private parseColor(color: string): { r: number, g: number, b: number } {
    // Handle hex color
    if (color.startsWith('#')) {
      const hex = color.slice(1);
      return {
        r: parseInt(hex.slice(0, 2), 16),
        g: parseInt(hex.slice(2, 4), 16),
        b: parseInt(hex.slice(4, 6), 16)
      };
    }

    // Handle rgb/rgba color
    const match = color.match(/^rgba?\((\d+),\s*(\d+),\s*(\d+)/);
    if (match) {
      return {
        r: parseInt(match[1]),
        g: parseInt(match[2]),
        b: parseInt(match[3])
      };
    }

    // Default to white if color format is not recognized
    return { r: 255, g: 255, b: 255 };
  }

  public clear(): void {
    this.lightSources.clear();
    this.lightingCache.clear();
  }
} 
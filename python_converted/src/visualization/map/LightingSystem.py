from typing import Any


class LightingSystem {
  private lightSources: Map<string, LightSource> = new Map()
  private lightingCache: Map<string, number> = new Map()
  private readonly maxLightLevel: float = 1.0
  private readonly minLightLevel: float = 0.1
  private readonly ambientLight: float = 0.2
  constructor() {}
  private getLightKey(x: float, y: float): str {
    return `${x},${y}`
  }
  public addLightSource(source: LightSource): void {
    this.lightSources.set(source.position.x + ',' + source.position.y, source)
    this.invalidateCache()
  }
  public removeLightSource(x: float, y: float): void {
    this.lightSources.delete(x + ',' + y)
    this.invalidateCache()
  }
  public updateLightSource(source: LightSource): void {
    const key = source.position.x + ',' + source.position.y
    if (this.lightSources.has(key)) {
      this.lightSources.set(key, source)
      this.invalidateCache()
    }
  }
  private invalidateCache(): void {
    this.lightingCache.clear()
  }
  private calculateDistance(p1: Point, p2: Point): float {
    const dx = p2.x - p1.x
    const dy = p2.y - p1.y
    return Math.sqrt(dx * dx + dy * dy)
  }
  private calculateLightIntensity(tile: Point, source: LightSource): float {
    const distance = this.calculateDistance(tile, source.position)
    if (distance > source.radius) {
      return 0
    }
    const intensity = (1 - distance / source.radius) * source.intensity
    return Math.max(0, Math.min(this.maxLightLevel, intensity))
  }
  public calculateTileLighting(tile: Tile): float {
    const key = this.getLightKey(tile.position.x, tile.position.y)
    let lighting = this.lightingCache.get(key)
    if (lighting === undefined) {
      lighting = this.ambientLight
      for (const source of this.lightSources.values()) {
        const intensity = this.calculateLightIntensity(tile.position, source)
        lighting = Math.min(this.maxLightLevel, lighting + intensity)
      }
      const elevationFactor = 1 + (tile.elevation / 10) 
      lighting *= elevationFactor
      lighting = Math.max(this.minLightLevel, Math.min(this.maxLightLevel, lighting))
      this.lightingCache.set(key, lighting)
    }
    return lighting
  }
  public getLightColor(tile: Tile): str {
    const lighting = this.calculateTileLighting(tile)
    const nearestSource = this.findNearestLightSource(tile.position)
    if (!nearestSource) {
      const value = Math.floor(lighting * 255)
      return `rgb(${value},${value},${value})`
    }
    const color = this.parseColor(nearestSource.color)
    const r = Math.floor(color.r * lighting)
    const g = Math.floor(color.g * lighting)
    const b = Math.floor(color.b * lighting)
    return `rgb(${r},${g},${b})`
  }
  private findNearestLightSource(position: Point): LightSource | null {
    let nearest: LightSource | null = null
    let minDistance = Infinity
    for (const source of this.lightSources.values()) {
      const distance = this.calculateDistance(position, source.position)
      if (distance < minDistance && distance <= source.radius) {
        minDistance = distance
        nearest = source
      }
    }
    return nearest
  }
  private parseColor(color: str): { r: float, g: float, b: float } {
    if (color.startsWith('#')) {
      const hex = color.slice(1)
      return {
        r: parseInt(hex.slice(0, 2), 16),
        g: parseInt(hex.slice(2, 4), 16),
        b: parseInt(hex.slice(4, 6), 16)
      }
    }
    const match = color.match(/^rgba?\((\d+),\s*(\d+),\s*(\d+)/)
    if (match) {
      return {
        r: parseInt(match[1]),
        g: parseInt(match[2]),
        b: parseInt(match[3])
      }
    }
    return { r: 255, g: 255, b: 255 }
  }
  public clear(): void {
    this.lightSources.clear()
    this.lightingCache.clear()
  }
} 
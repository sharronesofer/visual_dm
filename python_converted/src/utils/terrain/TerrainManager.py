from typing import Any


class TerrainManager {
  private terrainData: TerrainData
  constructor(terrainData: TerrainData) {
    this.terrainData = terrainData
  }
  public reset(): void {
    this.terrainData = {
      heightMap: Array(this.terrainData.heightMap.length).fill(null)
        .map(() => Array(this.terrainData.heightMap[0].length).fill(0)),
      features: [],
      buildableAreas: []
    }
  }
  public addFeature(feature: TerrainFeature): void {
    this.terrainData.features.push(feature)
  }
  public getTerrainAt(position: Coordinates): TerrainFeatureType {
    for (const feature of this.terrainData.features) {
      if (
        position.x >= feature.position.x &&
        position.x < feature.position.x + feature.size.width &&
        position.y >= feature.position.y &&
        position.y < feature.position.y + feature.size.height
      ) {
        return feature.type
      }
    }
    return TerrainFeatureType.PLAIN
  }
  public getElevationAt(position: Coordinates): float {
    return this.terrainData.heightMap[position.y][position.x]
  }
  public setElevationAt(position: Coordinates, elevation: float): void {
    this.terrainData.heightMap[position.y][position.x] = elevation
  }
  public getTerrainData(): TerrainData {
    return this.terrainData
  }
} 
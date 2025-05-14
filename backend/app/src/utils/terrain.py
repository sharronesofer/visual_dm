from typing import Any, Dict, List
from enum import Enum


  TerrainData, 
  TerrainFeature, 
  TerrainFeatureType,
  BuildableArea,
  TerrainAnalysisResult,
  TerrainModification,
  TerrainModificationType
} from '../types/terrain'
{ TerrainModificationType }
class TerrainAnalysisResult:
    slope: float
    elevation: float
    nearbyFeatures: List[TerrainFeature]
    buildabilityScore: float
    environmentalImpact: float
class TerrainModification:
    position: GridPosition
    type: \'TerrainModificationType\'
    params: Dict[str, Any>
class TerrainModificationType(Enum):
    LEVEL = 'LEVEL'
    SMOOTH = 'SMOOTH'
    RAMP = 'RAMP'
    FOUNDATION = 'FOUNDATION'
class TerrainManager {
  private heightMap: List[number][]
  private features: List[TerrainFeature]
  private buildableAreas: List[BuildableArea]
  private readonly MAX_SLOPE = 30 
  private readonly MIN_FEATURE_DISTANCE = 2 
  private readonly ANALYSIS_CACHE_SIZE = 1000
  private analysisCache: Map<string, TerrainAnalysisResult>
  constructor(terrainData: TerrainData) {
    this.heightMap = terrainData.heightMap
    this.features = terrainData.features
    this.buildableAreas = terrainData.buildableAreas
    this.analysisCache = new Map()
  }
  public analyzeTerrain(position: GridPosition, radius: float = 1): \'TerrainAnalysisResult\' {
    const cacheKey = this.getCacheKey(position, radius)
    const cached = this.analysisCache.get(cacheKey)
    if (cached) return cached
    const result: \'TerrainAnalysisResult\' = {
      slope: this.calculateSlope(position, radius),
      elevation: this.getElevation(position),
      nearbyFeatures: this.findNearbyFeatures(position, radius),
      buildabilityScore: 0,
      environmentalImpact: 0
    }
    result.buildabilityScore = this.calculateBuildabilityScore(result)
    result.environmentalImpact = this.calculateEnvironmentalImpact(position, radius)
    this.cacheAnalysisResult(cacheKey, result)
    return result
  }
  public modifyTerrain(modification: TerrainModification): void {
    const { position, type, params } = modification
    switch (type) {
      case TerrainModificationType.LEVEL:
        this.levelTerrain(position, params.heightDelta || 0, params.preserveFeatures || false)
        break
      case TerrainModificationType.SMOOTH:
        this.smoothTerrain(position, params.smoothingRadius || 1)
        break
      case TerrainModificationType.RAMP:
        this.createRamp(position, params.heightDelta || 0)
        break
      case TerrainModificationType.FOUNDATION:
        this.adjustFoundation(position)
        break
    }
    this.invalidateAnalysisCache(position, params.smoothingRadius || 1)
  }
  public findBuildableArea(
    size: Dict[str, Any],
    preferredFeatures: List[TerrainFeatureType] = []
  ): BuildableArea | null {
    const sortedAreas = [...this.buildableAreas]
      .filter(area => area.size.width >= size.width && area.size.height >= size.height)
      .sort((a, b) => {
        const aScore = this.calculateAreaSuitability(a, preferredFeatures)
        const bScore = this.calculateAreaSuitability(b, preferredFeatures)
        return bScore - aScore
      })
    return sortedAreas[0] || null
  }
  private calculateSlope(position: GridPosition, radius: float): float {
    let maxSlope = 0
    for (let dx = -radius; dx <= radius; dx++) {
      for (let dy = -radius; dy <= radius; dy++) {
        if (dx === 0 && dy === 0) continue
        const neighborPos = { x: position.x + dx, y: position.y + dy }
        if (!this.isValidPosition(neighborPos)) continue
        const heightDiff = Math.abs(
          this.getElevation(position) - this.getElevation(neighborPos)
        )
        const distance = Math.sqrt(dx * dx + dy * dy)
        const slope = Math.atan(heightDiff / distance) * (180 / Math.PI)
        maxSlope = Math.max(maxSlope, slope)
      }
    }
    return maxSlope
  }
  private calculateBuildabilityScore(analysis: TerrainAnalysisResult): float {
    const slopeScore = Math.max(0, 1 - analysis.slope / this.MAX_SLOPE)
    const featureScore = Math.max(0, 1 - analysis.nearbyFeatures.length * 0.2)
    return slopeScore * 0.7 + featureScore * 0.3
  }
  private calculateEnvironmentalImpact(position: GridPosition, radius: float): float {
    const features = this.findNearbyFeatures(position, radius)
    let impact = 0
    features.forEach(feature => {
      const distance = this.calculateDistance(position, feature.position)
      const featureImpact = this.getFeatureImpactWeight(feature.type) / Math.max(1, distance)
      impact += featureImpact
    })
    return Math.min(1, impact)
  }
  private getFeatureImpactWeight(type: TerrainFeatureType): float {
    switch (type) {
      case TerrainFeatureType.WATER: return 1.0
      case TerrainFeatureType.FOREST: return 0.8
      case TerrainFeatureType.CLIFF: return 0.6
      case TerrainFeatureType.MOUNTAIN: return 0.4
      case TerrainFeatureType.VALLEY: return 0.3
      default: return 0.1
    }
  }
  private levelTerrain(position: GridPosition, heightDelta: float, preserveFeatures: bool): void {
    const radius = 1
    if (preserveFeatures && this.hasNearbyFeatures(position, radius)) {
      return
    }
    for (let dx = -radius; dx <= radius; dx++) {
      for (let dy = -radius; dy <= radius; dy++) {
        const pos = { x: position.x + dx, y: position.y + dy }
        if (this.isValidPosition(pos)) {
          this.setElevation(pos, this.getElevation(position) + heightDelta)
        }
      }
    }
  }
  private smoothTerrain(position: GridPosition, radius: float): void {
    const originalHeight = this.getElevation(position)
    let sum = 0
    let count = 0
    for (let dx = -radius; dx <= radius; dx++) {
      for (let dy = -radius; dy <= radius; dy++) {
        const pos = { x: position.x + dx, y: position.y + dy }
        if (this.isValidPosition(pos)) {
          sum += this.getElevation(pos)
          count++
        }
      }
    }
    const averageHeight = sum / count
    this.setElevation(position, (originalHeight + averageHeight) / 2)
  }
  private createRamp(position: GridPosition, heightDelta: float): void {
    const radius = 2
    for (let dx = -radius; dx <= radius; dx++) {
      for (let dy = -radius; dy <= radius; dy++) {
        const pos = { x: position.x + dx, y: position.y + dy }
        if (!this.isValidPosition(pos)) continue
        const distance = Math.sqrt(dx * dx + dy * dy)
        const gradientFactor = 1 - (distance / radius)
        const adjustment = heightDelta * gradientFactor
        this.setElevation(pos, this.getElevation(pos) + adjustment)
      }
    }
  }
  private adjustFoundation(position: GridPosition): void {
    const radius = 1
    const targetHeight = this.getElevation(position)
    for (let dx = -radius; dx <= radius; dx++) {
      for (let dy = -radius; dy <= radius; dy++) {
        const pos = { x: position.x + dx, y: position.y + dy }
        if (!this.isValidPosition(pos)) continue
        const currentHeight = this.getElevation(pos)
        const adjustment = (targetHeight - currentHeight) * 0.5
        this.setElevation(pos, currentHeight + adjustment)
      }
    }
  }
  private findNearbyFeatures(position: GridPosition, radius: float): TerrainFeature[] {
    return this.features.filter(feature => {
      const distance = this.calculateDistance(position, feature.position)
      return distance <= radius
    })
  }
  private hasNearbyFeatures(position: GridPosition, radius: float): bool {
    return this.findNearbyFeatures(position, radius).length > 0
  }
  private calculateDistance(a: GridPosition, b: GridPosition): float {
    return Math.sqrt(Math.pow(b.x - a.x, 2) + Math.pow(b.y - a.y, 2))
  }
  private calculateAreaSuitability(
    area: BuildableArea,
    preferredFeatures: List[TerrainFeatureType]
  ): float {
    const center: GridPosition = {
      x: area.position.x + Math.floor(area.size.width / 2),
      y: area.position.y + Math.floor(area.size.height / 2)
    }
    const analysis = this.analyzeTerrain(center, Math.max(area.size.width, area.size.height))
    let score = analysis.buildabilityScore
    const hasPreferredFeatures = analysis.nearbyFeatures.some(
      feature => preferredFeatures.includes(feature.type)
    )
    if (hasPreferredFeatures) score *= 1.2
    return score
  }
  private getElevation(position: GridPosition): float {
    if (!this.isValidPosition(position)) return 0
    return this.heightMap[position.y][position.x]
  }
  private setElevation(position: GridPosition, height: float): void {
    if (!this.isValidPosition(position)) return
    this.heightMap[position.y][position.x] = height
  }
  private isValidPosition(position: GridPosition): bool {
    return position.x >= 0 && 
           position.x < this.heightMap[0].length &&
           position.y >= 0 && 
           position.y < this.heightMap.length
  }
  private getCacheKey(position: GridPosition, radius: float): str {
    return `${position.x},${position.y},${radius}`
  }
  private cacheAnalysisResult(key: str, result: TerrainAnalysisResult): void {
    if (this.analysisCache.size >= this.ANALYSIS_CACHE_SIZE) {
      const firstKey = this.analysisCache.keys().next().value
      this.analysisCache.delete(firstKey)
    }
    this.analysisCache.set(key, result)
  }
  private invalidateAnalysisCache(position: GridPosition, radius: float): void {
    for (const key of this.analysisCache.keys()) {
      const [x, y] = key.split(',').map(Number)
      const distance = this.calculateDistance(position, { x, y })
      if (distance <= radius) {
        this.analysisCache.delete(key)
      }
    }
  }
  public toSerializedData(): Any {
    return {
      heightMap: this.heightMap,
      features: this.features,
      buildableAreas: this.buildableAreas,
      analysisCache: Array.from(this.analysisCache.entries())
    }
  }
  public static fromSerializedData(data: Any): \'TerrainManager\' {
    const manager = new TerrainManager(
      data.heightMap,
      data.features,
      data.buildableAreas
    )
    manager.analysisCache = new Map(data.analysisCache)
    return manager
  }
} 
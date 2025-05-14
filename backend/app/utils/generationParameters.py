from typing import Any, Dict, List


class BuildingDistribution:
    density: float
    organizationFactor: float
    buildingCounts: Dict[str, float>
    minSpacing: float
    roadDensity: float
class GenerationParameters:
    poiDangerLevel: float
    poiCategory: POICategory
    narrativeContext: List[str]
    areaSizeConstraints: GridDimensions
class GenerationParametersCalculator {
  private readonly BASE_DENSITY = 0.3
  private readonly DANGER_DENSITY_FACTOR = 0.02
  private readonly MIN_BUILDING_COUNT = 3
  private readonly MAX_BUILDING_COUNT = 15
  public calculateBuildingDistribution(params: GenerationParameters): \'BuildingDistribution\' {
    const distribution: \'BuildingDistribution\' = {
      density: this.calculateBaseDensity(params),
      organizationFactor: this.calculateOrganizationFactor(params.poiCategory),
      buildingCounts: this.calculateBuildingCounts(params),
      minSpacing: this.calculateMinSpacing(params),
      roadDensity: this.calculateRoadDensity(params)
    }
    this.applyNarrativeModifiers(distribution, params)
    this.validateAndAdjustDistribution(distribution, params)
    return distribution
  }
  private calculateBaseDensity(params: GenerationParameters): float {
    let density = this.BASE_DENSITY
    density += params.poiDangerLevel * this.DANGER_DENSITY_FACTOR
    const areaSize = params.areaSizeConstraints.width * params.areaSizeConstraints.height
    const sizeFactor = Math.min(1, Math.max(0.5, Math.log10(areaSize) / 4))
    density *= sizeFactor
    switch (params.poiCategory) {
      case POICategory.SOCIAL:
        density *= 1.2 
        break
      case POICategory.DUNGEON:
        density *= 0.8 
        break
      case POICategory.EXPLORATION:
        density *= 0.6 
        break
    }
    return Math.min(1, Math.max(0.1, density))
  }
  private calculateOrganizationFactor(category: POICategory): float {
    switch (category) {
      case POICategory.SOCIAL:
        return 0.8 
      case POICategory.DUNGEON:
        return 0.5 
      case POICategory.EXPLORATION:
        return 0.2 
    }
  }
  private calculateBuildingCounts(params: GenerationParameters): Map<string, number> {
    const counts = new Map<string, number>()
    const areaSize = params.areaSizeConstraints.width * params.areaSizeConstraints.height
    const baseBuildingCount = Math.floor(
      Math.min(
        this.MAX_BUILDING_COUNT,
        Math.max(
          this.MIN_BUILDING_COUNT,
          (areaSize * this.calculateBaseDensity(params)) / 100
        )
      )
    )
    switch (params.poiCategory) {
      case POICategory.SOCIAL:
        counts.set('Inn', Math.ceil(baseBuildingCount * 0.2))
        counts.set('Shop', Math.ceil(baseBuildingCount * 0.3))
        counts.set('Tavern', Math.ceil(baseBuildingCount * 0.2))
        counts.set('GuildHall', Math.ceil(baseBuildingCount * 0.1))
        counts.set('NPCHome', Math.floor(baseBuildingCount * 0.2))
        break
      case POICategory.DUNGEON:
        counts.set('EnemyLair', Math.ceil(baseBuildingCount * 0.3))
        counts.set('PuzzleRoom', Math.ceil(baseBuildingCount * 0.2))
        counts.set('TreasureChamber', Math.ceil(baseBuildingCount * 0.2))
        counts.set('TrapRoom', Math.floor(baseBuildingCount * 0.3))
        break
      case POICategory.EXPLORATION:
        counts.set('Ruins', Math.ceil(baseBuildingCount * 0.3))
        counts.set('Campsite', Math.ceil(baseBuildingCount * 0.2))
        counts.set('Landmark', Math.ceil(baseBuildingCount * 0.2))
        counts.set('ResourceNode', Math.floor(baseBuildingCount * 0.3))
        break
    }
    return counts
  }
  private calculateMinSpacing(params: GenerationParameters): float {
    const baseSpacing = Math.round(2 * this.calculateOrganizationFactor(params.poiCategory))
    const density = this.calculateBaseDensity(params)
    return Math.max(1, Math.round(baseSpacing * (1 - density)))
  }
  private calculateRoadDensity(params: GenerationParameters): float {
    let roadDensity = this.calculateOrganizationFactor(params.poiCategory)
    switch (params.poiCategory) {
      case POICategory.SOCIAL:
        roadDensity *= 1.2 
        break
      case POICategory.DUNGEON:
        roadDensity *= 0.8 
        break
      case POICategory.EXPLORATION:
        roadDensity *= 0.5 
        break
    }
    const areaSize = params.areaSizeConstraints.width * params.areaSizeConstraints.height
    const sizeFactor = Math.min(1, Math.max(0.5, Math.log10(areaSize) / 4))
    roadDensity *= sizeFactor
    return Math.min(1, Math.max(0.1, roadDensity))
  }
  private applyNarrativeModifiers(distribution: \'BuildingDistribution\', params: GenerationParameters): void {
    for (const context of params.narrativeContext) {
      const lowerContext = context.toLowerCase()
      if (lowerContext.includes('crowded') || lowerContext.includes('bustling')) {
        distribution.density *= 1.2
      } else if (lowerContext.includes('sparse') || lowerContext.includes('empty')) {
        distribution.density *= 0.8
      }
      if (lowerContext.includes('planned') || lowerContext.includes('organized')) {
        distribution.organizationFactor = Math.min(1, distribution.organizationFactor * 1.2)
      } else if (lowerContext.includes('chaotic') || lowerContext.includes('disorganized')) {
        distribution.organizationFactor *= 0.8
      }
      if (lowerContext.includes('connected') || lowerContext.includes('accessible')) {
        distribution.roadDensity = Math.min(1, distribution.roadDensity * 1.2)
      } else if (lowerContext.includes('isolated') || lowerContext.includes('remote')) {
        distribution.roadDensity *= 0.8
      }
      this.adjustBuildingCountsForContext(distribution.buildingCounts, lowerContext)
    }
  }
  private adjustBuildingCountsForContext(counts: Map<string, number>, context: str): void {
    if (context.includes('commercial') || context.includes('trade')) {
      this.modifyBuildingCount(counts, 'Shop', 1.3)
      this.modifyBuildingCount(counts, 'Tavern', 1.2)
    } else if (context.includes('residential')) {
      this.modifyBuildingCount(counts, 'NPCHome', 1.5)
      this.modifyBuildingCount(counts, 'Inn', 0.8)
    } else if (context.includes('dangerous')) {
      this.modifyBuildingCount(counts, 'EnemyLair', 1.3)
      this.modifyBuildingCount(counts, 'TrapRoom', 1.2)
    } else if (context.includes('ancient') || context.includes('historic')) {
      this.modifyBuildingCount(counts, 'Ruins', 1.4)
      this.modifyBuildingCount(counts, 'Landmark', 1.2)
    }
  }
  private modifyBuildingCount(counts: Map<string, number>, buildingType: str, factor: float): void {
    const currentCount = counts.get(buildingType)
    if (currentCount !== undefined) {
      counts.set(buildingType, Math.max(1, Math.round(currentCount * factor)))
    }
  }
  private validateAndAdjustDistribution(distribution: \'BuildingDistribution\', params: GenerationParameters): void {
    distribution.density = Math.min(1, Math.max(0.1, distribution.density))
    distribution.organizationFactor = Math.min(1, Math.max(0.1, distribution.organizationFactor))
    distribution.roadDensity = Math.min(1, Math.max(0.1, distribution.roadDensity))
    const maxSpacing = Math.min(
      params.areaSizeConstraints.width,
      params.areaSizeConstraints.height
    ) / 4
    distribution.minSpacing = Math.min(maxSpacing, distribution.minSpacing)
    let totalBuildings = 0
    for (const [type, count] of distribution.buildingCounts) {
      totalBuildings += count
    }
    if (totalBuildings > this.MAX_BUILDING_COUNT) {
      const scaleFactor = this.MAX_BUILDING_COUNT / totalBuildings
      for (const [type, count] of distribution.buildingCounts) {
        distribution.buildingCounts.set(type, Math.max(1, Math.round(count * scaleFactor)))
      }
    }
  }
} 
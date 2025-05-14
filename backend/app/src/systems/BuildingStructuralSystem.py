from typing import Any, List


  BuildingStructure, 
  BuildingElement, 
  Wall,
  BuildingPhysics,
  BUILDING_PHYSICS_DEFAULTS
} from '../types/building'
class BuildingStructuralSystem {
  private physics: BuildingPhysics
  constructor(physics: Partial<BuildingPhysics> = {}) {
    this.physics = {
      ...BUILDING_PHYSICS_DEFAULTS,
      ...physics
    }
  }
  /**
   * Calculate the structural integrity of a building
   */
  calculateIntegrity(structure: BuildingStructure): float {
    const loadBearingWalls = Array.from(structure.elements.values())
      .filter((element): element is Wall => 
        element.type === 'wall' && element.isLoadBearing
      )
    if (loadBearingWalls.length < this.physics.minSupportPoints) {
      return 0
    }
    let integrity = this.calculateSupportPointIntegrity(structure.supportPoints, loadBearingWalls)
    integrity *= this.calculateElementsHealthFactor(structure)
    integrity *= this.calculateWeightDistribution(structure)
    return Math.max(0, Math.min(this.physics.maxIntegrity, integrity))
  }
  /**
   * Calculate integrity based on support points and load-bearing walls
   */
  private calculateSupportPointIntegrity(
    supportPoints: List[Position], 
    loadBearingWalls: List[Wall]
  ): float {
    let supportIntegrity = 0
    for (const point of supportPoints) {
      const hasSupport = loadBearingWalls.some(wall => 
        this.isNearby(point, wall.position)
      )
      if (hasSupport) {
        supportIntegrity += 100 / supportPoints.length
      }
    }
    return supportIntegrity
  }
  /**
   * Calculate factor based on the health of all building elements
   */
  private calculateElementsHealthFactor(structure: BuildingStructure): float {
    let totalHealth = 0
    let totalMaxHealth = 0
    for (const element of structure.elements.values()) {
      totalHealth += element.health
      totalMaxHealth += element.maxHealth
    }
    return totalMaxHealth > 0 ? totalHealth / totalMaxHealth : 0
  }
  /**
   * Calculate factor based on weight distribution
   */
  private calculateWeightDistribution(structure: BuildingStructure): float {
    let weightFactor = 1.0
    const elements = Array.from(structure.elements.values())
    const totalWeight = elements.reduce((sum, element) => 
      sum + this.physics.materialProperties[element.material].weight, 0
    )
    const centerOfMass = this.calculateCenterOfMass(elements)
    for (const point of structure.supportPoints) {
      const distance = this.calculateDistance(point, centerOfMass)
      if (distance > 5) { 
        weightFactor *= 0.9
      }
    }
    return weightFactor
  }
  /**
   * Calculate the center of mass for a set of building elements
   */
  private calculateCenterOfMass(elements: List[BuildingElement]): Position {
    let totalWeight = 0
    let weightedX = 0
    let weightedY = 0
    for (const element of elements) {
      const weight = this.physics.materialProperties[element.material].weight
      totalWeight += weight
      weightedX += element.position.x * weight
      weightedY += element.position.y * weight
    }
    return {
      x: weightedX / totalWeight,
      y: weightedY / totalWeight
    }
  }
  /**
   * Check if a position is nearby another position (within 1 unit)
   */
  private isNearby(a: Position, b: Position): bool {
    return this.calculateDistance(a, b) <= 1
  }
  /**
   * Calculate distance between two positions
   */
  private calculateDistance(a: Position, b: Position): float {
    const dx = a.x - b.x
    const dy = a.y - b.y
    return Math.sqrt(dx * dx + dy * dy)
  }
  /**
   * Predict integrity impact of a modification
   */
  predictModificationImpact(
    structure: BuildingStructure,
    elementToModify: BuildingElement,
    newHealth: float
  ): float {
    const modifiedStructure: BuildingStructure = {
      ...structure,
      elements: new Map(structure.elements)
    }
    const modifiedElement = {
      ...elementToModify,
      health: newHealth
    }
    modifiedStructure.elements.set(elementToModify.id, modifiedElement)
    return this.calculateIntegrity(modifiedStructure)
  }
  /**
   * Check if removing an element would compromise structural integrity
   */
  wouldCompromiseStructure(
    structure: BuildingStructure,
    elementToRemove: BuildingElement
  ): bool {
    const modifiedStructure: BuildingStructure = {
      ...structure,
      elements: new Map(structure.elements)
    }
    modifiedStructure.elements.delete(elementToRemove.id)
    const newIntegrity = this.calculateIntegrity(modifiedStructure)
    return newIntegrity < structure.integrity * 0.75
  }
  /**
   * Get recommended repair locations to improve structural integrity
   */
  getRecommendedRepairs(structure: BuildingStructure): BuildingElement[] {
    const repairs: List[BuildingElement] = []
    const elements = Array.from(structure.elements.values())
    const damagedElements = elements
      .filter(element => element.health < element.maxHealth)
      .sort((a, b) => 
        (a.maxHealth - a.health) - (b.maxHealth - b.health)
      )
    for (const element of damagedElements) {
      if (element.type === 'wall' && (element as Wall).isLoadBearing) {
        repairs.push(element)
      }
    }
    for (const element of damagedElements) {
      if (!repairs.includes(element)) {
        repairs.push(element)
      }
    }
    return repairs
  }
} 
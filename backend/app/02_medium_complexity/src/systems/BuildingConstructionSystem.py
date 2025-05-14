from typing import Any, Dict



  BuildingStructure, 
  BuildingElement,
  Wall,
  Door,
  Window,
  MaterialType,
  BuildingPhysics,
  BUILDING_PHYSICS_DEFAULTS
} from '../types/building'
class ConstructionCost:
    materials: Dict[str, Any]
class BuildingConstructionSystem {
  private physics: BuildingPhysics
  private structuralSystem: BuildingStructuralSystem
  constructor(
    physics: Partial<BuildingPhysics> = {},
    structuralSystem?: BuildingStructuralSystem
  ) {
    this.physics = {
      ...BUILDING_PHYSICS_DEFAULTS,
      ...physics
    }
    this.structuralSystem = structuralSystem || new BuildingStructuralSystem(physics)
  }
  /**
   * Add a new wall to the structure
   */
  addWall(
    structure: BuildingStructure,
    position: Position,
    material: MaterialType,
    isLoadBearing: bool = false
  ): BuildingStructure {
    const wall: Wall = {
      id: uuidv4(),
      type: 'wall',
      position,
      material,
      health: this.getMaxHealth(material),
      maxHealth: this.getMaxHealth(material),
      thickness: 1,
      height: 3,
      isLoadBearing
    }
    return this.addElement(structure, wall)
  }
  /**
   * Add a new door to the structure
   */
  addDoor(
    structure: BuildingStructure,
    position: Position,
    material: MaterialType
  ): BuildingStructure {
    const door: Door = {
      id: uuidv4(),
      type: 'door',
      position,
      material,
      health: this.getMaxHealth(material),
      maxHealth: this.getMaxHealth(material),
      isOpen: false,
      isLocked: false
    }
    return this.addElement(structure, door)
  }
  /**
   * Add a new window to the structure
   */
  addWindow(
    structure: BuildingStructure,
    position: Position,
    material: MaterialType
  ): BuildingStructure {
    const window: Window = {
      id: uuidv4(),
      type: 'window',
      position,
      material,
      health: this.getMaxHealth(material),
      maxHealth: this.getMaxHealth(material),
      isBroken: false,
      isBarricaded: false
    }
    return this.addElement(structure, window)
  }
  /**
   * Remove an element from the structure
   */
  removeElement(
    structure: BuildingStructure,
    elementId: str
  ): BuildingStructure {
    const modifiedStructure = this.createStructureCopy(structure)
    modifiedStructure.elements.delete(elementId)
    modifiedStructure.integrity = this.structuralSystem.calculateIntegrity(modifiedStructure)
    return modifiedStructure
  }
  /**
   * Calculate construction costs for a new element
   */
  calculateConstructionCost(
    elementType: 'wall' | 'door' | 'window',
    material: MaterialType,
    isLoadBearing: bool = false
  ): \'ConstructionCost\' {
    const materialProps = this.physics.materialProperties[material]
    const baseAmount = elementType === 'wall' ? 2 : 1
    const loadBearingMultiplier = isLoadBearing ? 1.5 : 1
    return {
      materials: Dict[str, Any],
      time: baseAmount * materialProps.repairDifficulty * 60, 
      laborCost: baseAmount * materialProps.repairDifficulty * 100 
    }
  }
  /**
   * Check if construction is possible at a position
   */
  canBuildAt(
    structure: BuildingStructure,
    position: Position,
    elementType: 'wall' | 'door' | 'window'
  ): bool {
    const isOccupied = Array.from(structure.elements.values()).some(
      element => 
        element.position.x === position.x && 
        element.position.y === position.y
    )
    if (isOccupied) {
      return false
    }
    switch (elementType) {
      case 'door':
      case 'window':
        return this.hasAdjacentWall(structure, position)
      default:
        return true
    }
  }
  /**
   * Private helper methods
   */
  private addElement(
    structure: BuildingStructure,
    element: BuildingElement
  ): BuildingStructure {
    if (!this.canBuildAt(structure, element.position, element.type)) {
      throw new Error(`Cannot build ${element.type} at position ${JSON.stringify(element.position)}`)
    }
    const modifiedStructure = this.createStructureCopy(structure)
    modifiedStructure.elements.set(element.id, element)
    modifiedStructure.integrity = this.structuralSystem.calculateIntegrity(modifiedStructure)
    return modifiedStructure
  }
  private getMaxHealth(material: MaterialType): float {
    return this.physics.materialProperties[material].durability * 100
  }
  private hasAdjacentWall(structure: BuildingStructure, position: Position): bool {
    const adjacentPositions = [
      { x: position.x - 1, y: position.y },
      { x: position.x + 1, y: position.y },
      { x: position.x, y: position.y - 1 },
      { x: position.x, y: position.y + 1 }
    ]
    return Array.from(structure.elements.values()).some(
      element =>
        element.type === 'wall' &&
        adjacentPositions.some(
          adj => element.position.x === adj.x && element.position.y === adj.y
        )
    )
  }
  private createStructureCopy(structure: BuildingStructure): BuildingStructure {
    return {
      ...structure,
      elements: new Map(structure.elements)
    }
  }
} 
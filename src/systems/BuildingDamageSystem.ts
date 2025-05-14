import { 
  BuildingElement, 
  BuildingStructure,
  BuildingPhysics,
  BUILDING_PHYSICS_DEFAULTS,
  MaterialType
} from '../types/building';
import { BuildingStructuralSystem } from './BuildingStructuralSystem';

export type DamageType = 'impact' | 'fire' | 'explosion';

export interface DamageEvent {
  type: DamageType;
  amount: number;
  position: { x: number; y: number };
  radius?: number; // For area damage
}

export class BuildingDamageSystem {
  private physics: BuildingPhysics;
  private structuralSystem: BuildingStructuralSystem;

  constructor(
    physics: Partial<BuildingPhysics> = {},
    structuralSystem?: BuildingStructuralSystem
  ) {
    this.physics = {
      ...BUILDING_PHYSICS_DEFAULTS,
      ...physics
    };
    this.structuralSystem = structuralSystem || new BuildingStructuralSystem(physics);
  }

  /**
   * Apply damage to a building structure
   */
  applyDamage(structure: BuildingStructure, damageEvent: DamageEvent): BuildingStructure {
    const affectedElements = this.getAffectedElements(structure, damageEvent);
    const modifiedStructure = this.createStructureCopy(structure);

    for (const element of affectedElements) {
      const damage = this.calculateDamage(element, damageEvent);
      const newHealth = Math.max(0, element.health - damage);
      
      const modifiedElement = {
        ...element,
        health: newHealth
      };
      
      modifiedStructure.elements.set(element.id, modifiedElement);
    }

    // Update overall structure integrity
    modifiedStructure.integrity = this.structuralSystem.calculateIntegrity(modifiedStructure);

    return modifiedStructure;
  }

  /**
   * Repair a building element
   */
  repairElement(
    structure: BuildingStructure,
    elementId: string,
    amount: number
  ): BuildingStructure {
    const element = structure.elements.get(elementId);
    if (!element) {
      return structure;
    }

    const modifiedStructure = this.createStructureCopy(structure);
    const newHealth = Math.min(element.maxHealth, element.health + amount);
    
    const modifiedElement = {
      ...element,
      health: newHealth
    };
    
    modifiedStructure.elements.set(elementId, modifiedElement);
    modifiedStructure.integrity = this.structuralSystem.calculateIntegrity(modifiedStructure);

    return modifiedStructure;
  }

  /**
   * Get elements affected by a damage event
   */
  private getAffectedElements(
    structure: BuildingStructure,
    damageEvent: DamageEvent
  ): BuildingElement[] {
    const elements = Array.from(structure.elements.values());

    if (damageEvent.radius && damageEvent.radius > 0) {
      // Area damage
      return elements.filter(element => 
        this.isInRadius(element.position, damageEvent.position, damageEvent.radius!)
      );
    } else {
      // Single point damage
      return elements.filter(element =>
        element.position.x === damageEvent.position.x &&
        element.position.y === damageEvent.position.y
      );
    }
  }

  /**
   * Calculate actual damage based on material properties and damage type
   */
  private calculateDamage(element: BuildingElement, damageEvent: DamageEvent): number {
    const materialProps = this.physics.materialProperties[element.material];
    const resistance = materialProps.resistance[damageEvent.type];
    
    // Base damage reduced by material resistance
    let damage = damageEvent.amount * (1 - resistance);

    // Distance falloff for area damage
    if (damageEvent.radius) {
      const distance = this.calculateDistance(element.position, damageEvent.position);
      const falloff = 1 - (distance / damageEvent.radius);
      damage *= Math.max(0, falloff);
    }

    return damage;
  }

  /**
   * Check if a position is within a radius of another position
   */
  private isInRadius(
    point: { x: number; y: number },
    center: { x: number; y: number },
    radius: number
  ): boolean {
    return this.calculateDistance(point, center) <= radius;
  }

  /**
   * Calculate distance between two points
   */
  private calculateDistance(
    a: { x: number; y: number },
    b: { x: number; y: number }
  ): number {
    const dx = a.x - b.x;
    const dy = a.y - b.y;
    return Math.sqrt(dx * dx + dy * dy);
  }

  /**
   * Create a deep copy of a building structure
   */
  private createStructureCopy(structure: BuildingStructure): BuildingStructure {
    return {
      ...structure,
      elements: new Map(structure.elements)
    };
  }

  /**
   * Get repair cost for an element
   */
  getRepairCost(element: BuildingElement): number {
    const damageTaken = element.maxHealth - element.health;
    const materialCost = this.physics.materialProperties[element.material].weight;
    return damageTaken * materialCost;
  }

  /**
   * Check if an element can be repaired
   */
  canRepair(element: BuildingElement): boolean {
    return element.health < element.maxHealth;
  }

  /**
   * Get optimal repair material for an element
   */
  getOptimalRepairMaterial(element: BuildingElement): MaterialType {
    // By default, use the same material
    return element.material;
  }

  /**
   * Estimate time to repair an element
   */
  estimateRepairTime(element: BuildingElement): number {
    const damageTaken = element.maxHealth - element.health;
    const materialComplexity = this.physics.materialProperties[element.material].weight;
    // Base time unit is seconds
    return damageTaken * materialComplexity * 2;
  }
} 
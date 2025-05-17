import { Position } from '../core/interfaces/types/common';
import {
  BuildingStructure,
  BuildingElement,
  Wall,
  BuildingPhysics,
  BUILDING_PHYSICS_DEFAULTS
} from '../core/interfaces/types/building';
import { RepairAndMaintenanceSystem } from './RepairAndMaintenanceSystem';

export class BuildingStructuralSystem {
  private physics: BuildingPhysics;
  private repairSystem: RepairAndMaintenanceSystem;

  constructor(physics: Partial<BuildingPhysics> = {}) {
    this.physics = {
      ...BUILDING_PHYSICS_DEFAULTS,
      ...physics
    };
    this.repairSystem = new RepairAndMaintenanceSystem();
  }

  /**
   * Calculate the structural integrity of a building
   */
  calculateIntegrity(structure: BuildingStructure): number {
    // Get all load-bearing walls
    const loadBearingWalls = Array.from(structure.elements.values())
      .filter((element): element is Wall =>
        element && typeof element === 'object' && 'type' in element && element.type === 'wall' && (element as any).isLoadBearing
      );

    // Check if we have minimum required support points
    if (loadBearingWalls.length < this.physics.minSupportPoints) {
      return 0;
    }

    // Calculate base integrity from support points
    let integrity = this.calculateSupportPointIntegrity(structure.supportPoints, loadBearingWalls);

    // Factor in the health of all elements
    integrity *= this.calculateElementsHealthFactor(structure);

    // Factor in weight distribution
    integrity *= this.calculateWeightDistribution(structure);

    // Ensure integrity is within bounds
    return Math.max(0, Math.min(this.physics.maxIntegrity, integrity));
  }

  /**
   * Calculate integrity based on support points and load-bearing walls
   */
  private calculateSupportPointIntegrity(
    supportPoints: Position[],
    loadBearingWalls: Wall[]
  ): number {
    let supportIntegrity = 0;

    // Check each support point has at least one nearby load-bearing wall
    for (const point of supportPoints) {
      const hasSupport = loadBearingWalls.some(wall =>
        this.isNearby(point, wall.position)
      );

      if (hasSupport) {
        supportIntegrity += 100 / supportPoints.length;
      }
    }

    return supportIntegrity;
  }

  /**
   * Calculate factor based on the health of all building elements
   */
  private calculateElementsHealthFactor(structure: BuildingStructure): number {
    let totalHealth = 0;
    let totalMaxHealth = 0;

    for (const element of structure.elements.values()) {
      if (element && typeof element === 'object' && 'health' in element && 'maxHealth' in element) {
        totalHealth += (element as any).health;
        totalMaxHealth += (element as any).maxHealth;
      }
    }

    return totalMaxHealth > 0 ? totalHealth / totalMaxHealth : 0;
  }

  /**
   * Calculate factor based on weight distribution
   */
  private calculateWeightDistribution(structure: BuildingStructure): number {
    let weightFactor = 1.0;
    const elements = Array.from(structure.elements.values());

    // Calculate total weight and center of mass
    const totalWeight = elements.reduce((sum, element) =>
      sum + (element && typeof element === 'object' && 'material' in element && this.physics.materialProperties[(element as any).material] ? this.physics.materialProperties[(element as any).material].weight : 0), 0
    );

    const centerOfMass = this.calculateCenterOfMass(elements);

    // Check weight distribution relative to support points
    for (const point of structure.supportPoints) {
      const distance = this.calculateDistance(point, centerOfMass);
      // Reduce integrity if center of mass is far from support points
      if (distance > 5) { // Arbitrary threshold
        weightFactor *= 0.9;
      }
    }

    return weightFactor;
  }

  /**
   * Calculate the center of mass for a set of building elements
   */
  private calculateCenterOfMass(elements: BuildingElement[]): Position {
    let totalWeight = 0;
    let weightedX = 0;
    let weightedY = 0;

    for (const element of elements) {
      if (element && typeof element === 'object' && 'material' in element && 'position' in element && this.physics.materialProperties[(element as any).material]) {
        const weight = this.physics.materialProperties[(element as any).material].weight;
        totalWeight += weight;
        weightedX += (element as any).position.x * weight;
        weightedY += (element as any).position.y * weight;
      }
    }

    return {
      x: totalWeight > 0 ? weightedX / totalWeight : 0,
      y: totalWeight > 0 ? weightedY / totalWeight : 0
    };
  }

  /**
   * Check if a position is nearby another position (within 1 unit)
   */
  private isNearby(a: Position, b: Position): boolean {
    return this.calculateDistance(a, b) <= 1;
  }

  /**
   * Calculate distance between two positions
   */
  private calculateDistance(a: Position, b: Position): number {
    if (!a || !b || typeof a.x !== 'number' || typeof a.y !== 'number' || typeof b.x !== 'number' || typeof b.y !== 'number') {
      return Infinity;
    }
    const dx = a.x - b.x;
    const dy = a.y - b.y;
    return Math.sqrt(dx * dx + dy * dy);
  }

  /**
   * Predict integrity impact of a modification
   */
  predictModificationImpact(
    structure: BuildingStructure,
    elementToModify: BuildingElement,
    newHealth: number
  ): number {
    // Create a copy of the structure
    const modifiedStructure: BuildingStructure = {
      ...structure,
      elements: new Map(structure.elements)
    };

    // Apply the modification
    const modifiedElement = {
      ...elementToModify,
      health: newHealth
    };
    modifiedStructure.elements.set(elementToModify.id, modifiedElement);

    // Calculate new integrity
    return this.calculateIntegrity(modifiedStructure);
  }

  /**
   * Check if removing an element would compromise structural integrity
   */
  wouldCompromiseStructure(
    structure: BuildingStructure,
    elementToRemove: BuildingElement
  ): boolean {
    // Create a copy of the structure without the element
    const modifiedStructure: BuildingStructure = {
      ...structure,
      elements: new Map(structure.elements)
    };
    modifiedStructure.elements.delete(elementToRemove.id);

    // Calculate integrity without the element
    const newIntegrity = this.calculateIntegrity(modifiedStructure);

    // Consider it compromised if integrity drops by more than 25%
    return newIntegrity < structure.integrity * 0.75;
  }

  /**
   * Get recommended repair locations to improve structural integrity
   */
  getRecommendedRepairs(structure: BuildingStructure): BuildingElement[] {
    const repairs: BuildingElement[] = [];
    const elements = Array.from(structure.elements.values());

    // Sort elements by their health deficit (damaged elements first)
    const damagedElements = elements
      .filter(element => element.health < element.maxHealth)
      .sort((a, b) =>
        (a.maxHealth - a.health) - (b.maxHealth - b.health)
      );

    // Prioritize load-bearing walls
    for (const element of damagedElements) {
      if (element.type === 'wall' && (element as Wall).isLoadBearing) {
        repairs.push(element);
      }
    }

    // Add other damaged elements
    for (const element of damagedElements) {
      if (!repairs.includes(element)) {
        repairs.push(element);
      }
    }

    return repairs;
  }

  /**
   * Apply maintenance effects to a building
   */
  applyMaintenanceEffects(structure: BuildingStructure): void {
    this.repairSystem.applyMaintenanceEffects(structure);
  }

  /**
   * Trigger a vendor repair workflow for a building
   */
  triggerVendorRepair(structure: BuildingStructure, vendorId: string): { cost: number; vendorId: string } {
    return this.repairSystem.requestVendorRepair(structure, vendorId);
  }

  /**
   * Confirm a vendor repair for a building
   */
  confirmVendorRepair(structure: BuildingStructure, vendorId: string): void {
    this.repairSystem.confirmVendorRepair(structure, vendorId);
  }

  /**
   * Get maintenance status of a building
   */
  getMaintenanceStatus(structure: BuildingStructure): string {
    return (structure as any).maintenanceStatus || 'unknown';
  }
} 
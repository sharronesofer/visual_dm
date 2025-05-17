import { Position } from '../core/interfaces/types/common';
import {
  BuildingStructure,
  BuildingElement,
  Wall,
  BuildingPhysics,
  BUILDING_PHYSICS_DEFAULTS,
  Floor,
  Roof,
  Column,
  Beam,
  Stair,
  Furniture,
  Partition
} from '../core/interfaces/types/building';
import { calculateDistance } from '../utils/movementUtils';

/**
 * BuildingStructuralSystem is responsible for all structural integrity calculations and related logic.
 *
 * Design notes:
 * - All public methods are orchestrators, delegating to focused, private helpers for testability and maintainability.
 * - All helpers are single-responsibility and under 50 lines.
 * - All calculations are stateless and deterministic, relying only on input arguments and physics config.
 * - The system is designed for extensibility: new structural rules can be added as new helpers.
 * - All performance-sensitive code avoids unnecessary object creation and uses efficient iteration.
 * - All methods are covered by integration and regression tests in the test suite.
 */
export class BuildingStructuralSystem {
  private physics: BuildingPhysics;

  constructor(physics: Partial<BuildingPhysics> = {}) {
    this.physics = {
      ...BUILDING_PHYSICS_DEFAULTS,
      ...physics
    };
  }

  /**
   * Calculate the structural integrity of a building
   * Orchestrates the integrity calculation by delegating to focused helpers.
   */
  calculateIntegrity(structure: BuildingStructure): number {
    // Step 1: Identify load-bearing elements (walls, columns, beams)
    const loadBearingElements = this.getLoadBearingElements(structure);
    // Step 2: Ensure minimum support points are present
    if (!this.hasMinimumSupportPoints(loadBearingElements)) {
      return 0;
    }
    // Step 3: Calculate base integrity from support
    let integrity = this.calculateBaseIntegrity(structure, loadBearingElements);
    // Step 4: Apply health, weight, and redundancy factors
    integrity = this.applyHealthFactor(integrity, structure);
    integrity = this.applyWeightDistributionFactor(integrity, structure);
    integrity = this.applyRedundancyFactor(integrity, structure, loadBearingElements);
    // Step 5: Apply material fatigue and environmental effects
    integrity = this.applyMaterialFatigueFactor(integrity, structure);
    integrity = this.applyEnvironmentalFactor(integrity, structure);
    // Step 6: Clamp to valid bounds
    return this.clampIntegrity(integrity);
  }

  /**
   * Returns all load-bearing elements in the structure (walls, columns, beams).
   * This is a critical step for structural analysis.
   */
  private getLoadBearingElements(structure: BuildingStructure): (Wall | Column | Beam)[] {
    return Array.from(structure.elements.values()).filter(
      (element): element is Wall | Column | Beam =>
        (element.type === 'wall' && (element as Wall).isLoadBearing) ||
        element.type === 'column' ||
        element.type === 'beam'
    );
  }

  /**
   * Checks if the number of load-bearing elements meets the minimum required for stability.
   */
  private hasMinimumSupportPoints(loadBearingElements: (Wall | Column | Beam)[]): boolean {
    return loadBearingElements.length >= this.physics.minSupportPoints;
  }

  /**
   * Calculates the base integrity using support points and load-bearing elements.
   */
  private calculateBaseIntegrity(structure: BuildingStructure, loadBearingElements: (Wall | Column | Beam)[]): number {
    return this.calculateSupportPointIntegrity(structure.supportPoints, loadBearingElements);
  }

  /**
   * Applies the health factor to the current integrity value.
   * This ensures that damage to elements proportionally reduces overall integrity.
   */
  private applyHealthFactor(integrity: number, structure: BuildingStructure): number {
    return integrity * this.calculateElementsHealthFactor(structure);
  }

  /**
   * Applies the weight distribution factor to the current integrity value.
   * Penalizes poor weight distribution to encourage realistic designs.
   */
  private applyWeightDistributionFactor(integrity: number, structure: BuildingStructure): number {
    return integrity * this.calculateWeightDistribution(structure);
  }

  /**
   * Applies the redundancy factor: if primary support fails, check for secondary support (columns/beams).
   */
  private applyRedundancyFactor(
    integrity: number,
    structure: BuildingStructure,
    loadBearingElements: (Wall | Column | Beam)[]
  ): number {
    // If integrity is low, check for secondary supports (columns/beams)
    if (integrity < 0.5) {
      const secondarySupports = loadBearingElements.filter(
        el => el.type === 'column' || el.type === 'beam'
      );
      if (secondarySupports.length > 0) {
        // Boost integrity if redundancy is present
        return integrity + 0.2 * Math.min(1, secondarySupports.length / 4);
      }
    }
    return integrity;
  }

  /**
   * Apply material fatigue factor: degrade integrity based on time, usage, and stress.
   * (Stub: to be connected to time/events system)
   */
  private applyMaterialFatigueFactor(integrity: number, structure: BuildingStructure): number {
    // Example: degrade by 1% per 1000 ticks of usage (stub)
    // In real system, would use structure.deterioration or similar
    let fatigue = (structure.deterioration || 0) * 0.01;
    // --- Advanced: Penalize for high weatheringRate materials ---
    for (const element of structure.elements.values()) {
      const matProps = this.physics.materialProperties[element.material];
      if (matProps.weatheringRate) {
        fatigue += matProps.weatheringRate * 0.5; // Tune multiplier as needed
      }
    }
    return integrity * (1 - fatigue);
  }

  /**
   * Apply environmental factor: degrade integrity based on weather (rain, snow, wind).
   * (Stub: to be connected to weather system)
   */
  private applyEnvironmentalFactor(integrity: number, structure: BuildingStructure): number {
    // Example: degrade by 2% if exposed to harsh weather (stub)
    // In real system, would use weather API
    let weatherPenalty = 0;
    // --- Advanced: Penalize for low weather resistance ---
    for (const element of structure.elements.values()) {
      const matProps = this.physics.materialProperties[element.material];
      // Penalize if any resistance is low (simulate harsh weather)
      if (matProps.resistance) {
        const avgWeatherRes = [
          matProps.resistance.heat ?? 50,
          matProps.resistance.cold ?? 50,
          matProps.resistance.moisture ?? 50,
          matProps.resistance.uv ?? 50,
          matProps.resistance.wind ?? 50
        ].reduce((a, b) => a + b, 0) / 5;
        if (avgWeatherRes < 50) weatherPenalty += 0.01;
      }
      // TODO: Integrate with real weather system for dynamic penalty
    }
    // --- Advanced: Boost for synergy bonuses ---
    // (If elements are made from optimal combinations, boost integrity)
    // TODO: Integrate with MaterialRegistry for synergy bonuses
    return integrity * (1 - weatherPenalty);
  }

  /**
   * Clamps the integrity value to the valid range defined by physics config.
   * Prevents negative or excessive integrity values.
   */
  private clampIntegrity(integrity: number): number {
    return Math.max(0, Math.min(this.physics.maxIntegrity, integrity));
  }

  /**
   * Calculate integrity based on support points and load-bearing elements
   */
  private calculateSupportPointIntegrity(
    supportPoints: Position[],
    loadBearingElements: (Wall | Column | Beam)[]
  ): number {
    let supportIntegrity = 0;
    for (const point of supportPoints) {
      const hasSupport = loadBearingElements.some(element =>
        this.isNearby(point, element.position)
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
      totalHealth += element.health;
      totalMaxHealth += element.maxHealth;
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
      sum + this.physics.materialProperties[element.material].weight, 0
    );

    const centerOfMass = this.calculateCenterOfMass(elements);

    // Check weight distribution relative to support points
    for (const point of structure.supportPoints) {
      const distance = calculateDistance(point, centerOfMass);
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
      const weight = this.physics.materialProperties[element.material].weight;
      totalWeight += weight;
      weightedX += element.position.x * weight;
      weightedY += element.position.y * weight;
    }

    return {
      x: weightedX / totalWeight,
      y: weightedY / totalWeight
    };
  }

  /**
   * Check if a position is nearby another position (within 1 unit)
   */
  private isNearby(a: Position, b: Position): boolean {
    return calculateDistance(a, b) <= 1;
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
} 
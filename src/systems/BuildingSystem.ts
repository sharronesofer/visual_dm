import { v4 as uuidv4 } from 'uuid';
import { 
  BuildingStructure, 
  BuildingElement,
  MaterialType,
  BuildingPhysics,
  BUILDING_PHYSICS_DEFAULTS
} from '../types/building';
import { Position } from '../types/common';
import { BuildingStructuralSystem } from './BuildingStructuralSystem';
import { BuildingDamageSystem, DamageEvent } from './BuildingDamageSystem';
import { BuildingConstructionSystem, ConstructionCost } from './BuildingConstructionSystem';

export class BuildingSystem {
  private structures: Map<string, BuildingStructure> = new Map();
  private structuralSystem: BuildingStructuralSystem;
  private damageSystem: BuildingDamageSystem;
  private constructionSystem: BuildingConstructionSystem;

  constructor(physics: Partial<BuildingPhysics> = {}) {
    const fullPhysics = {
      ...BUILDING_PHYSICS_DEFAULTS,
      ...physics
    };

    this.structuralSystem = new BuildingStructuralSystem(fullPhysics);
    this.damageSystem = new BuildingDamageSystem(fullPhysics, this.structuralSystem);
    this.constructionSystem = new BuildingConstructionSystem(fullPhysics, this.structuralSystem);
  }

  /**
   * Create a new empty building structure
   */
  createStructure(): string {
    const structure: BuildingStructure = {
      id: uuidv4(),
      elements: new Map(),
      integrity: 1
    };

    this.structures.set(structure.id, structure);
    return structure.id;
  }

  /**
   * Get a building structure by ID
   */
  getStructure(id: string): BuildingStructure | undefined {
    return this.structures.get(id);
  }

  /**
   * Delete a building structure
   */
  deleteStructure(id: string): boolean {
    return this.structures.delete(id);
  }

  /**
   * Construction Methods
   */
  addWall(
    structureId: string,
    position: Position,
    material: MaterialType,
    isLoadBearing: boolean = false
  ): boolean {
    const structure = this.structures.get(structureId);
    if (!structure) return false;

    try {
      const updatedStructure = this.constructionSystem.addWall(
        structure,
        position,
        material,
        isLoadBearing
      );
      this.structures.set(structureId, updatedStructure);
      return true;
    } catch (error) {
      console.error('Failed to add wall:', error);
      return false;
    }
  }

  addDoor(
    structureId: string,
    position: Position,
    material: MaterialType
  ): boolean {
    const structure = this.structures.get(structureId);
    if (!structure) return false;

    try {
      const updatedStructure = this.constructionSystem.addDoor(
        structure,
        position,
        material
      );
      this.structures.set(structureId, updatedStructure);
      return true;
    } catch (error) {
      console.error('Failed to add door:', error);
      return false;
    }
  }

  addWindow(
    structureId: string,
    position: Position,
    material: MaterialType
  ): boolean {
    const structure = this.structures.get(structureId);
    if (!structure) return false;

    try {
      const updatedStructure = this.constructionSystem.addWindow(
        structure,
        position,
        material
      );
      this.structures.set(structureId, updatedStructure);
      return true;
    } catch (error) {
      console.error('Failed to add window:', error);
      return false;
    }
  }

  removeElement(structureId: string, elementId: string): boolean {
    const structure = this.structures.get(structureId);
    if (!structure) return false;

    try {
      const updatedStructure = this.constructionSystem.removeElement(
        structure,
        elementId
      );
      this.structures.set(structureId, updatedStructure);
      return true;
    } catch (error) {
      console.error('Failed to remove element:', error);
      return false;
    }
  }

  /**
   * Damage Methods
   */
  applyDamage(structureId: string, damageEvent: DamageEvent): boolean {
    const structure = this.structures.get(structureId);
    if (!structure) return false;

    try {
      const updatedStructure = this.damageSystem.applyDamage(structure, damageEvent);
      this.structures.set(structureId, updatedStructure);
      return true;
    } catch (error) {
      console.error('Failed to apply damage:', error);
      return false;
    }
  }

  repairElement(
    structureId: string,
    elementId: string,
    amount: number
  ): boolean {
    const structure = this.structures.get(structureId);
    if (!structure) return false;

    try {
      const updatedStructure = this.damageSystem.repairElement(
        structure,
        elementId,
        amount
      );
      this.structures.set(structureId, updatedStructure);
      return true;
    } catch (error) {
      console.error('Failed to repair element:', error);
      return false;
    }
  }

  /**
   * Utility Methods
   */
  calculateConstructionCost(
    elementType: 'wall' | 'door' | 'window',
    material: MaterialType,
    isLoadBearing: boolean = false
  ): ConstructionCost {
    return this.constructionSystem.calculateConstructionCost(
      elementType,
      material,
      isLoadBearing
    );
  }

  canBuildAt(
    structureId: string,
    position: Position,
    elementType: 'wall' | 'door' | 'window'
  ): boolean {
    const structure = this.structures.get(structureId);
    if (!structure) return false;

    return this.constructionSystem.canBuildAt(structure, position, elementType);
  }

  getRepairCost(structureId: string, elementId: string): number | undefined {
    const structure = this.structures.get(structureId);
    if (!structure) return undefined;

    const element = structure.elements.get(elementId);
    if (!element) return undefined;

    return this.damageSystem.getRepairCost(element);
  }

  estimateRepairTime(structureId: string, elementId: string): number | undefined {
    const structure = this.structures.get(structureId);
    if (!structure) return undefined;

    const element = structure.elements.get(elementId);
    if (!element) return undefined;

    return this.damageSystem.estimateRepairTime(element);
  }

  getStructureIntegrity(structureId: string): number | undefined {
    const structure = this.structures.get(structureId);
    return structure?.integrity;
  }

  getAllStructures(): BuildingStructure[] {
    return Array.from(this.structures.values());
  }
} 
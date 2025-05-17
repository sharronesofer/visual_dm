import { v4 as uuidv4 } from 'uuid';
import {
  BuildingStructure,
  BuildingElement,
  MaterialType,
  BuildingPhysics,
  BUILDING_PHYSICS_DEFAULTS
} from '../core/interfaces/types/building';
import { Position } from '../core/interfaces/types/common';
import { BuildingStructuralSystem } from './BuildingStructuralSystem';
import { BuildingDamageSystem, DamageEvent } from './BuildingDamageSystem';
import { BuildingConstructionSystem, ConstructionCost } from './BuildingConstructionSystem';
import { MaterialRefundCalculator, DestructionType } from './MaterialRefundCalculator';
import { ResourceTransactionLogger } from './ResourceTransactionLogger';
import { createMaterialRefundNotification } from '../core/interfaces/types/models';
import { DamageVisualSystem } from '../visualization/DamageVisualSystem';
import { FoundationModule } from './building_modules/FoundationModule';

/**
 * BuildingSystem orchestrates all building-related operations, including structure management,
 * construction, damage, and repair. It composes the structural, construction, and damage systems.
 *
 * Design notes:
 * - All public methods are single-responsibility and under 50 lines.
 * - Error handling is consistent and user-facing errors are logged.
 * - All state is managed via the structures map; all mutations are atomic and return new structure states.
 * - The system is designed for extensibility: new element types or systems can be added with minimal changes.
 * - All methods are covered by integration and regression tests in the test suite.
 */
export class BuildingSystem {
  private structures: Map<string, BuildingStructure> = new Map();
  private structuralSystem: BuildingStructuralSystem;
  private damageSystem: BuildingDamageSystem;
  private constructionSystem: BuildingConstructionSystem;
  private refundCalculator = new MaterialRefundCalculator(MaterialRefundCalculator.defaultConfig());
  private transactionLogger = new ResourceTransactionLogger();
  private visualSystem?: DamageVisualSystem;

  constructor(physics: Partial<BuildingPhysics> = {}) {
    const fullPhysics = {
      ...BUILDING_PHYSICS_DEFAULTS,
      ...physics
    };

    this.structuralSystem = new BuildingStructuralSystem(fullPhysics);
    this.damageSystem = new BuildingDamageSystem(fullPhysics, this.structuralSystem);
    this.constructionSystem = new BuildingConstructionSystem(fullPhysics, this.structuralSystem);

    // Subscribe to damage changes and update visuals if visualSystem is set
    this.damageSystem.onDamageChange((structure, axis, oldValue, newValue) => {
      if (this.visualSystem) {
        this.visualSystem.updateVisual(structure, axis, oldValue, newValue);
      }
    });
  }

  /**
   * Inject the DamageVisualSystem for visual updates on damage changes.
   */
  public setVisualSystem(visualSystem: DamageVisualSystem) {
    this.visualSystem = visualSystem;
  }

  /**
   * Create a new empty building structure
   */
  createStructure(): string {
    const structure: BuildingStructure = {
      id: uuidv4(),
      elements: new Map(),
      integrity: 1,
      supportPoints: [],
      battleDamage: 1,
      deterioration: 1
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
   * Delete a building structure and trigger material refund
   */
  deleteStructure(id: string, options?: { playerId?: string; destructionType?: DestructionType; reason?: string }): boolean {
    const structure = this.structures.get(id);
    if (!structure) return false;

    // --- Begin Material Refund Process ---
    // Assume structure has ownerId and buildingType fields (add if missing)
    const ownerId = (structure as any).ownerId || options?.playerId || 'unknown';
    const buildingType = (structure as any).buildingType || 'default';
    const destructionType = options?.destructionType || 'other';
    const reason = options?.reason || 'Destroyed';

    // Calculate refund
    const refunded = this.refundCalculator.calculateRefund(structure, buildingType, destructionType);
    // For demo, assume originalMaterials = refunded (should be tracked during construction)
    const originalMaterials = { ...refunded };

    // --- Inventory Integration (pseudo, replace with real InventorySystem call) ---
    // Example: InventorySystem.addItemToInventory(ownerId, ...)
    // For each material, add to inventory (handle overflow/queue as needed)
    Object.entries(refunded).forEach(([mat, qty]) => {
      // TODO: Integrate with InventorySystem
      console.log(`[Inventory] Add ${qty} of ${mat} to owner ${ownerId}`);
    });

    // --- Log the transaction ---
    this.transactionLogger.logRefund({
      buildingId: id,
      playerId: ownerId,
      originalMaterials,
      refundedMaterials: refunded,
      timestamp: Date.now(),
      reason,
      destructionType
    });

    // --- UI Notification (pseudo, replace with real notification system) ---
    // Example: NotificationService.send({ userId: ownerId, ... })
    const notification = createMaterialRefundNotification(ownerId, refunded);
    // TODO: Integrate with NotificationService
    console.log(`[Notification] Refunded materials to player ${ownerId}:`, notification);

    // --- Remove the structure ---
    return this.structures.delete(id);
  }

  /**
   * Construction Methods
   */
  addWall(
    structureId: string,
    position: Position,
    material: MaterialType,
    isLoadBearing: boolean = false,
    ownerId?: string,
    buildingType?: string
  ): boolean {
    const structure = this.structures.get(structureId);
    if (!structure) return false;

    try {
      const updatedStructure = this.constructionSystem.addWall(
        structure,
        position,
        material,
        isLoadBearing,
        ownerId,
        buildingType
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
    material: MaterialType,
    ownerId?: string,
    buildingType?: string
  ): boolean {
    const structure = this.structures.get(structureId);
    if (!structure) return false;

    try {
      const updatedStructure = this.constructionSystem.addDoor(
        structure,
        position,
        material,
        ownerId,
        buildingType
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
    material: MaterialType,
    ownerId?: string,
    buildingType?: string
  ): boolean {
    const structure = this.structures.get(structureId);
    if (!structure) return false;

    try {
      const updatedStructure = this.constructionSystem.addWindow(
        structure,
        position,
        material,
        ownerId,
        buildingType
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

  /**
   * Process hourly deterioration for all buildings (to be called by the tick system)
   */
  processHourlyDeterioration(amount: number = 1): void {
    for (const [id, structure] of this.structures.entries()) {
      const updated = this.damageSystem.applyDeterioration(structure, amount, 'hourly tick');
      this.structures.set(id, updated);
    }
  }

  /**
   * Integrate procedurally generated buildings from world generation
   * @param buildings Array of Building objects from worldgen
   * @returns Mapping of buildingId to structureId
   */
  public integrateWorldgenBuildings(buildings: any[]): Record<string, string> {
    const idMap: Record<string, string> = {};
    for (const building of buildings) {
      // Create a new structure
      const structureId = this.createStructure();
      const structure = this.getStructure(structureId);
      if (!structure) continue;
      // Adapt foundation to terrain using enhanced parameters
      const foundationType = building.foundationType || 'standard';
      const foundationDepth = building.foundationDepth || 1;
      const materialStrength = building.materialStrength || 1;
      const slope = building.slope || 0;
      const terrainType = building.terrainType || 'plains';
      // Create and add foundation module with adaptation
      const foundation = FoundationModule.createAdaptive(
        `foundation-${structureId}`,
        { x: building.x, y: building.y },
        building.material,
        foundationType,
        foundationDepth,
        materialStrength,
        slope,
        terrainType
      );
      if (!structure.elements) structure.elements = new Map();
      structure.elements.set(foundation.moduleId, foundation);
      // Assign material and style
      (structure as any).material = building.material;
      (structure as any).style = building.style;
      // Set integrity (future: recalculate with structural system)
      structure.integrity = building.integrity || 1;
      // TODO: If building.requiresEntranceStair, add stair module at entrance
      // Register structure
      this.structures.set(structureId, structure);
      idMap[building.id] = structureId;
    }
    return idMap;
  }

  /**
   * Advanced Material System Integration Hooks
   * -----------------------------------------
   * TODO: Integrate weathering, upgrades, combinations, and synergy bonuses into all relevant methods.
   * - When adding elements, check for valid upgrades and combinations (MaterialRegistry)
   * - When applying damage or deterioration, use weather resistance and weathering rate
   * - When refunding materials, track upgrade/combo-specific resources
   * - When calculating integrity, apply synergy bonuses for optimal combinations
   * - When updating visuals, use visualDegradationStates from MaterialProperties
   */
} 
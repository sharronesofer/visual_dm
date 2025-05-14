import { Position } from '../types/common';
import { BuildingType } from '../worldgen/interior/types';

export interface BuildingModification {
  id: string;
  type: 'add' | 'remove' | 'modify';
  position: Position;
  buildingType?: BuildingType;
  modificationData: {
    walls?: {
      add?: Position[];
      remove?: Position[];
      modify?: Array<{
        position: Position;
        material: string;
        health: number;
      }>;
    };
    doors?: {
      add?: Array<{
        position: Position;
        type: 'wooden' | 'metal' | 'reinforced';
      }>;
      remove?: Position[];
      modify?: Array<{
        position: Position;
        locked: boolean;
        health: number;
      }>;
    };
    windows?: {
      add?: Array<{
        position: Position;
        type: 'glass' | 'barred' | 'reinforced';
      }>;
      remove?: Position[];
      modify?: Array<{
        position: Position;
        broken: boolean;
        barricaded: boolean;
      }>;
    };
  };
}

export class BuildingModificationSystem {
  private modifications: Map<string, BuildingModification> = new Map();
  private modificationHistory: BuildingModification[] = [];
  
  constructor() {}

  /**
   * Apply a modification to a building
   */
  applyModification(modification: BuildingModification): boolean {
    try {
      // Validate modification
      if (!this.validateModification(modification)) {
        return false;
      }

      // Store modification
      this.modifications.set(modification.id, modification);
      this.modificationHistory.push(modification);

      // Apply the changes
      switch (modification.type) {
        case 'add':
          return this.handleAddModification(modification);
        case 'remove':
          return this.handleRemoveModification(modification);
        case 'modify':
          return this.handleModifyModification(modification);
        default:
          return false;
      }
    } catch (error) {
      console.error('Error applying building modification:', error);
      return false;
    }
  }

  /**
   * Validate a proposed modification
   */
  private validateModification(modification: BuildingModification): boolean {
    // Check for required fields
    if (!modification.id || !modification.type || !modification.position) {
      return false;
    }

    // Validate position is within map bounds
    // TODO: Add map bounds check

    // Validate modification data based on type
    switch (modification.type) {
      case 'add':
        return this.validateAddModification(modification);
      case 'remove':
        return this.validateRemoveModification(modification);
      case 'modify':
        return this.validateModifyModification(modification);
      default:
        return false;
    }
  }

  /**
   * Handle adding new building elements
   */
  private handleAddModification(modification: BuildingModification): boolean {
    const { walls, doors, windows } = modification.modificationData;

    if (walls?.add) {
      // Add new walls
      for (const wallPos of walls.add) {
        // TODO: Implement wall addition logic
        // This will interact with the physics system and update visuals
      }
    }

    if (doors?.add) {
      // Add new doors
      for (const door of doors.add) {
        // TODO: Implement door addition logic
        // This will need to handle door type and properties
      }
    }

    if (windows?.add) {
      // Add new windows
      for (const window of windows.add) {
        // TODO: Implement window addition logic
        // This will need to handle window type and properties
      }
    }

    return true;
  }

  /**
   * Handle removing building elements
   */
  private handleRemoveModification(modification: BuildingModification): boolean {
    const { walls, doors, windows } = modification.modificationData;

    if (walls?.remove) {
      // Remove walls
      for (const wallPos of walls.remove) {
        // TODO: Implement wall removal logic
        // This will need to handle structural integrity checks
      }
    }

    if (doors?.remove) {
      // Remove doors
      for (const doorPos of doors.remove) {
        // TODO: Implement door removal logic
      }
    }

    if (windows?.remove) {
      // Remove windows
      for (const windowPos of windows.remove) {
        // TODO: Implement window removal logic
      }
    }

    return true;
  }

  /**
   * Handle modifying existing building elements
   */
  private handleModifyModification(modification: BuildingModification): boolean {
    const { walls, doors, windows } = modification.modificationData;

    if (walls?.modify) {
      // Modify walls
      for (const wall of walls.modify) {
        // TODO: Implement wall modification logic
        // This will handle material changes and damage
      }
    }

    if (doors?.modify) {
      // Modify doors
      for (const door of doors.modify) {
        // TODO: Implement door modification logic
        // This will handle locking/unlocking and damage
      }
    }

    if (windows?.modify) {
      // Modify windows
      for (const window of windows.modify) {
        // TODO: Implement window modification logic
        // This will handle breaking and barricading
      }
    }

    return true;
  }

  /**
   * Validate add modifications
   */
  private validateAddModification(modification: BuildingModification): boolean {
    const { walls, doors, windows } = modification.modificationData;

    // Ensure we have at least one type of addition
    if (!walls?.add && !doors?.add && !windows?.add) {
      return false;
    }

    // TODO: Add more specific validation rules
    // - Check for collisions with existing elements
    // - Verify structural integrity
    // - Check resource requirements

    return true;
  }

  /**
   * Validate remove modifications
   */
  private validateRemoveModification(modification: BuildingModification): boolean {
    const { walls, doors, windows } = modification.modificationData;

    // Ensure we have at least one type of removal
    if (!walls?.remove && !doors?.remove && !windows?.remove) {
      return false;
    }

    // TODO: Add more specific validation rules
    // - Check if elements exist
    // - Verify structural integrity after removal
    // - Check for dependent elements

    return true;
  }

  /**
   * Validate modify modifications
   */
  private validateModifyModification(modification: BuildingModification): boolean {
    const { walls, doors, windows } = modification.modificationData;

    // Ensure we have at least one type of modification
    if (!walls?.modify && !doors?.modify && !windows?.modify) {
      return false;
    }

    // TODO: Add more specific validation rules
    // - Verify elements exist
    // - Check material compatibility
    // - Validate modification parameters

    return true;
  }

  /**
   * Get modification by ID
   */
  getModification(id: string): BuildingModification | undefined {
    return this.modifications.get(id);
  }

  /**
   * Get all modifications for a position
   */
  getModificationsAtPosition(position: Position): BuildingModification[] {
    return Array.from(this.modifications.values()).filter(mod => 
      mod.position.x === position.x && mod.position.y === position.y
    );
  }

  /**
   * Get modification history
   */
  getModificationHistory(): BuildingModification[] {
    return [...this.modificationHistory];
  }

  /**
   * Clear all modifications
   */
  clearModifications(): void {
    this.modifications.clear();
    this.modificationHistory = [];
  }
} 
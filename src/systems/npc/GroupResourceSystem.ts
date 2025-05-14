import { Group } from '../../types/npc/group';
import { GroupManager } from './GroupManager';

export interface Resource {
  id: string;
  type: string;
  name: string;
  quantity: number;
  value: number;
  location?: { x: number; y: number };
}

export interface Territory {
  id: string;
  name: string;
  controllingGroupId: string;
  contestedBy: string[];
  boundaries: {
    topLeft: { x: number; y: number };
    bottomRight: { x: number; y: number };
  };
  resources: Resource[];
  controlScore: number; // 0-100
  lastClaimed: number;
}

export class GroupResourceSystem {
  private groupManager: GroupManager;
  private resources: Map<string, Resource>;
  private territories: Map<string, Territory>;
  private groupResources: Map<string, Set<string>>; // groupId -> resourceIds
  
  constructor(groupManager: GroupManager) {
    this.groupManager = groupManager;
    this.resources = new Map();
    this.territories = new Map();
    this.groupResources = new Map();
  }

  /**
   * Add a resource to the system
   */
  public addResource(resource: Resource): void {
    this.resources.set(resource.id, resource);
  }

  /**
   * Assign a resource to a group
   */
  public assignResourceToGroup(resourceId: string, groupId: string): boolean {
    const resource = this.resources.get(resourceId);
    const group = this.groupManager.getGroup(groupId);
    
    if (!resource || !group) return false;

    if (!this.groupResources.has(groupId)) {
      this.groupResources.set(groupId, new Set());
    }

    this.groupResources.get(groupId)?.add(resourceId);
    return true;
  }

  /**
   * Remove a resource from a group
   */
  public removeResourceFromGroup(resourceId: string, groupId: string): boolean {
    const groupResources = this.groupResources.get(groupId);
    if (!groupResources) return false;

    return groupResources.delete(resourceId);
  }

  /**
   * Get all resources owned by a group
   */
  public getGroupResources(groupId: string): Resource[] {
    const resourceIds = this.groupResources.get(groupId);
    if (!resourceIds) return [];

    return Array.from(resourceIds)
      .map(id => this.resources.get(id))
      .filter((r): r is Resource => r !== undefined);
  }

  /**
   * Add a new territory
   */
  public addTerritory(territory: Territory): void {
    this.territories.set(territory.id, territory);
  }

  /**
   * Claim a territory for a group
   */
  public claimTerritory(
    territoryId: string,
    groupId: string,
    force: number
  ): boolean {
    const territory = this.territories.get(territoryId);
    const group = this.groupManager.getGroup(groupId);
    
    if (!territory || !group) return false;

    // If territory is unclaimed, claim it immediately
    if (!territory.controllingGroupId) {
      territory.controllingGroupId = groupId;
      territory.controlScore = force;
      territory.lastClaimed = Date.now();
      return true;
    }

    // If territory is claimed, need sufficient force to contest
    if (force > territory.controlScore) {
      // Transfer control
      territory.controllingGroupId = groupId;
      territory.controlScore = force;
      territory.lastClaimed = Date.now();
      territory.contestedBy = [];
      return true;
    } else if (force >= territory.controlScore * 0.5) {
      // Contest the territory
      if (!territory.contestedBy.includes(groupId)) {
        territory.contestedBy.push(groupId);
      }
      return true;
    }

    return false;
  }

  /**
   * Check if a point is within a territory
   */
  public isPointInTerritory(x: number, y: number, territoryId: string): boolean {
    const territory = this.territories.get(territoryId);
    if (!territory) return false;

    return (
      x >= territory.boundaries.topLeft.x &&
      x <= territory.boundaries.bottomRight.x &&
      y >= territory.boundaries.topLeft.y &&
      y <= territory.boundaries.bottomRight.y
    );
  }

  /**
   * Get territories controlled by a group
   */
  public getGroupTerritories(groupId: string): Territory[] {
    return Array.from(this.territories.values())
      .filter(t => t.controllingGroupId === groupId);
  }

  /**
   * Get territories contested by a group
   */
  public getContestedTerritories(groupId: string): Territory[] {
    return Array.from(this.territories.values())
      .filter(t => t.contestedBy.includes(groupId));
  }

  /**
   * Calculate total resource value for a group
   */
  public calculateGroupWealth(groupId: string): number {
    const resources = this.getGroupResources(groupId);
    return resources.reduce((total, r) => total + (r.value * r.quantity), 0);
  }

  /**
   * Transfer resources between groups
   */
  public transferResources(
    fromGroupId: string,
    toGroupId: string,
    resourceIds: string[]
  ): boolean {
    const fromGroup = this.groupManager.getGroup(fromGroupId);
    const toGroup = this.groupManager.getGroup(toGroupId);
    
    if (!fromGroup || !toGroup) return false;

    const fromResources = this.groupResources.get(fromGroupId);
    if (!fromResources) return false;

    // Verify all resources exist and are owned by fromGroup
    if (!resourceIds.every(id => fromResources.has(id))) return false;

    // Perform transfer
    if (!this.groupResources.has(toGroupId)) {
      this.groupResources.set(toGroupId, new Set());
    }
    
    const toResources = this.groupResources.get(toGroupId)!;
    resourceIds.forEach(id => {
      fromResources.delete(id);
      toResources.add(id);
    });

    return true;
  }

  /**
   * Update territory control scores periodically
   */
  public updateTerritoryControl(): void {
    const now = Date.now();
    
    this.territories.forEach(territory => {
      // Increase control score over time for controlling group
      if (territory.controllingGroupId) {
        const timeFactor = (now - territory.lastClaimed) / (24 * 60 * 60 * 1000); // Days
        territory.controlScore = Math.min(100, territory.controlScore + timeFactor);
      }

      // Remove old contested claims
      territory.contestedBy = territory.contestedBy.filter(groupId => {
        const group = this.groupManager.getGroup(groupId);
        return group && !this.groupManager.isGroupInactive(groupId);
      });
    });
  }

  /**
   * Clean up resources and territories for disbanded groups
   */
  public cleanupDisbandedGroup(groupId: string): void {
    // Remove group's resource ownership
    this.groupResources.delete(groupId);

    // Remove group from territory control
    this.territories.forEach(territory => {
      if (territory.controllingGroupId === groupId) {
        territory.controllingGroupId = '';
        territory.controlScore = 0;
      }
      territory.contestedBy = territory.contestedBy.filter(id => id !== groupId);
    });
  }

  /**
   * Get all territories
   */
  public getTerritories(): Map<string, Territory> {
    return this.territories;
  }

  /**
   * Get all resources
   */
  public getResources(): Map<string, Resource> {
    return this.resources;
  }
} 
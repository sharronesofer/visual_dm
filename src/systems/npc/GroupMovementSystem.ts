import { Group } from '../../types/npc/group';
import { NPCData, NPCPosition } from '../../types/npc/npc';
import { GroupManager } from './GroupManager';
import { SpatialGrid } from '../../utils/SpatialGrid';
import { GroupRole } from '../../types/npc/group';
import { PathfindingSystem } from '../../types/grid';
import { GridPosition } from '../../types/grid';

interface MovementTarget {
  x: number;
  y: number;
  priority: number;
  deadline?: number;
}

interface FormationSlot {
  relativePosition: NPCPosition;
  memberId?: string;
  role?: GroupRole;
}

export class GroupMovementSystem {
  private groupManager: GroupManager;
  private spatialGrid: SpatialGrid;
  private pathfinding: PathfindingSystem;
  private groupTargets: Map<string, MovementTarget>;
  private groupFormations: Map<string, FormationSlot[]>;
  private groupPaths: Map<string, GridPosition[]>;
  private readonly FORMATION_SPACING = 2; // Units between members
  private readonly PATH_RECALCULATION_INTERVAL = 1000; // ms
  private readonly OBSTACLE_CHECK_RADIUS = 3; // Cells to check for obstacles
  
  constructor(
    groupManager: GroupManager,
    gridSize: number = 100,
    pathfinding: PathfindingSystem
  ) {
    this.groupManager = groupManager;
    this.spatialGrid = new SpatialGrid(gridSize);
    this.pathfinding = pathfinding;
    this.groupTargets = new Map();
    this.groupFormations = new Map();
    this.groupPaths = new Map();
  }

  /**
   * Set a movement target for a group
   */
  public setGroupTarget(
    groupId: string,
    target: MovementTarget
  ): boolean {
    const group = this.groupManager.getGroup(groupId);
    if (!group) return false;

    this.groupTargets.set(groupId, target);
    this.updateFormation(groupId);
    
    // Calculate initial path
    this.recalculateGroupPath(groupId);
    
    return true;
  }

  /**
   * Clear a group's movement target
   */
  public clearGroupTarget(groupId: string): void {
    this.groupTargets.delete(groupId);
  }

  /**
   * Update positions for all group members
   */
  public update(npcs: Map<string, NPCData>, speed: number = 1): void {
    // Process each group's movement
    this.groupTargets.forEach((target, groupId) => {
      const group = this.groupManager.getGroup(groupId);
      if (!group) return;

      // Skip if target has expired
      if (target.deadline && Date.now() > target.deadline) {
        this.groupTargets.delete(groupId);
        this.groupPaths.delete(groupId);
        return;
      }

      // Check if path needs recalculation
      const path = this.groupPaths.get(groupId);
      if (!path || this.shouldRecalculatePath(groupId)) {
        this.recalculateGroupPath(groupId);
      }

      // Update each member's position
      group.members.forEach((member, memberId) => {
        const npc = npcs.get(memberId);
        if (!npc) return;

        const targetPos = this.getMemberTargetPosition(groupId, memberId, target);
        if (!targetPos) return;

        // Calculate new position using formation and path
        const newPos = this.calculateFormationPosition(
          npc.position,
          targetPos,
          speed,
          groupId,
          memberId
        );
        
        // Update NPC position
        npc.position = newPos;
        this.spatialGrid.updateEntity(memberId, newPos);
      });
    });
  }

  /**
   * Calculate new position considering formation and obstacles
   */
  private calculateFormationPosition(
    current: NPCPosition,
    target: NPCPosition,
    speed: number,
    groupId: string,
    memberId: string
  ): NPCPosition {
    const path = this.groupPaths.get(groupId);
    if (!path || path.length === 0) {
      return this.calculateMovementVector(current, target, speed);
    }

    // Find the appropriate path segment for this member
    const formationSlots = this.groupFormations.get(groupId) || [];
    const memberSlot = formationSlots.find(slot => slot.memberId === memberId);
    if (!memberSlot) {
      return this.calculateMovementVector(current, target, speed);
    }

    // Adjust path point based on formation position
    const nextPathPoint = path[0];
    const adjustedTarget = {
      x: nextPathPoint.x + memberSlot.relativePosition.x,
      y: nextPathPoint.y + memberSlot.relativePosition.y
    };

    // Check for nearby obstacles
    const obstacles = this.checkNearbyObstacles(current);
    if (obstacles > 0) {
      // Apply obstacle avoidance behavior
      return this.calculateObstacleAvoidance(current, adjustedTarget, speed, obstacles);
    }

    return this.calculateMovementVector(current, adjustedTarget, speed);
  }

  /**
   * Check for obstacles in the immediate vicinity
   */
  private checkNearbyObstacles(position: NPCPosition): number {
    let obstacleCount = 0;
    
    // Check surrounding cells
    for (let dx = -this.OBSTACLE_CHECK_RADIUS; dx <= this.OBSTACLE_CHECK_RADIUS; dx++) {
      for (let dy = -this.OBSTACLE_CHECK_RADIUS; dy <= this.OBSTACLE_CHECK_RADIUS; dy++) {
        const checkPos = { x: position.x + dx, y: position.y + dy };
        const entities = this.spatialGrid.getEntitiesInCell(checkPos);
        obstacleCount += entities.length;
      }
    }

    return obstacleCount;
  }

  /**
   * Calculate position adjustment for obstacle avoidance
   */
  private calculateObstacleAvoidance(
    current: NPCPosition,
    target: NPCPosition,
    speed: number,
    obstacleCount: number
  ): NPCPosition {
    // Calculate base movement vector
    const baseVector = this.calculateMovementVector(current, target, speed);
    
    // Calculate avoidance vector (move away from obstacles)
    const avoidanceWeight = Math.min(obstacleCount * 0.2, 0.8); // Cap at 80% influence
    
    // Find least crowded direction
    let bestDirection = { x: 0, y: 0 };
    let minObstacles = Infinity;
    
    const directions = [
      { x: 1, y: 0 }, { x: -1, y: 0 }, { x: 0, y: 1 }, { x: 0, y: -1 },
      { x: 1, y: 1 }, { x: 1, y: -1 }, { x: -1, y: 1 }, { x: -1, y: -1 }
    ];

    for (const dir of directions) {
      const checkPos = {
        x: current.x + dir.x,
        y: current.y + dir.y
      };
      const obstacles = this.checkNearbyObstacles(checkPos);
      if (obstacles < minObstacles) {
        minObstacles = obstacles;
        bestDirection = dir;
      }
    }

    // Combine base movement with avoidance
    return {
      x: baseVector.x * (1 - avoidanceWeight) + bestDirection.x * avoidanceWeight * speed,
      y: baseVector.y * (1 - avoidanceWeight) + bestDirection.y * avoidanceWeight * speed
    };
  }

  /**
   * Recalculate path for a group
   */
  private recalculateGroupPath(groupId: string): void {
    const group = this.groupManager.getGroup(groupId);
    const target = this.groupTargets.get(groupId);
    if (!group || !target) return;

    const groupCenter = this.getGroupCenter(groupId);
    if (!groupCenter) return;

    // Calculate path using enhanced pathfinding
    const path = this.pathfinding.findGroupPath(
      { x: Math.round(groupCenter.x), y: Math.round(groupCenter.y) },
      { x: target.x, y: target.y },
      {
        groupSize: group.members.size,
        formationWidth: Math.ceil(Math.sqrt(group.members.size)),
        formationSpacing: this.FORMATION_SPACING,
        predictiveAvoidance: true
      }
    );

    this.groupPaths.set(groupId, path);
  }

  /**
   * Check if path needs recalculation
   */
  private shouldRecalculatePath(groupId: string): boolean {
    const group = this.groupManager.getGroup(groupId);
    const path = this.groupPaths.get(groupId);
    if (!group || !path) return true;

    // Check if any member is too far from their formation position
    const formationSlots = this.groupFormations.get(groupId) || [];
    for (const [memberId, _] of group.members) {
      const memberPos = this.spatialGrid.getEntityPosition(memberId);
      const slot = formationSlots.find(s => s.memberId === memberId);
      if (!memberPos || !slot) continue;

      const targetPos = {
        x: path[0].x + slot.relativePosition.x,
        y: path[0].y + slot.relativePosition.y
      };

      const distance = Math.sqrt(
        Math.pow(memberPos.x - targetPos.x, 2) +
        Math.pow(memberPos.y - targetPos.y, 2)
      );

      if (distance > this.FORMATION_SPACING * 2) {
        return true;
      }
    }

    return false;
  }

  /**
   * Check if a group has reached its target
   */
  public hasReachedTarget(groupId: string, threshold: number = 1): boolean {
    const group = this.groupManager.getGroup(groupId);
    const target = this.groupTargets.get(groupId);
    
    if (!group || !target) return false;

    // Check if all members are within threshold distance of their formation positions
    return Array.from(group.members.keys()).every(memberId => {
      const npc = this.spatialGrid.getEntityPosition(memberId);
      const targetPos = this.getMemberTargetPosition(groupId, memberId, target);
      
      if (!npc || !targetPos) return false;

      const dx = targetPos.x - npc.x;
      const dy = targetPos.y - npc.y;
      const distance = Math.sqrt(dx * dx + dy * dy);
      
      return distance <= threshold;
    });
  }

  /**
   * Get the average position of a group
   */
  public getGroupCenter(groupId: string): NPCPosition | null {
    const group = this.groupManager.getGroup(groupId);
    if (!group) return null;

    const memberPositions = Array.from(group.members.keys())
      .map(id => this.spatialGrid.getEntityPosition(id))
      .filter((pos): pos is NPCPosition => pos !== undefined);

    if (memberPositions.length === 0) return null;

    return {
      x: memberPositions.reduce((sum, pos) => sum + pos.x, 0) / memberPositions.length,
      y: memberPositions.reduce((sum, pos) => sum + pos.y, 0) / memberPositions.length
    };
  }

  /**
   * Clean up when a group is disbanded
   */
  public cleanupGroup(groupId: string): void {
    this.groupTargets.delete(groupId);
    this.groupFormations.delete(groupId);
  }

  /**
   * Update formation slots for a group
   */
  private updateFormation(groupId: string): void {
    const group = this.groupManager.getGroup(groupId);
    if (!group) return;

    const slots: FormationSlot[] = [];
    const size = group.members.size;
    const cols = Math.ceil(Math.sqrt(size));
    const rows = Math.ceil(size / cols);

    // Create grid of formation slots
    for (let row = 0; row < rows; row++) {
      for (let col = 0; col < cols; col++) {
        slots.push({
          relativePosition: {
            x: (col - (cols - 1) / 2) * this.FORMATION_SPACING,
            y: (row - (rows - 1) / 2) * this.FORMATION_SPACING
          }
        });
      }
    }

    // Sort members by role (leader first, then by role priority)
    const sortedMembers = Array.from(group.members.entries())
      .sort(([_, a], [__, b]) => {
        if (a.role === GroupRole.LEADER) return -1;
        if (b.role === GroupRole.LEADER) return 1;
        return (a.role || '').localeCompare(b.role || '');
      });

    // Leader gets center slot
    const centerSlot = slots.reduce((best, slot, index) => {
      const distFromCenter = Math.sqrt(
        slot.relativePosition.x ** 2 + slot.relativePosition.y ** 2
      );
      if (distFromCenter < Math.sqrt(
        best.slot.relativePosition.x ** 2 + best.slot.relativePosition.y ** 2
      )) {
        return { slot, index };
      }
      return best;
    }, { slot: slots[0], index: 0 });

    slots[centerSlot.index].memberId = sortedMembers[0][0];

    // Assign remaining slots spiraling outward
    const unassignedSlots = slots.filter((_, i) => i !== centerSlot.index);
    let assigned = 1;

    for (let i = 1; i < sortedMembers.length; i++) {
      const [memberId, member] = sortedMembers[i];
      const slot = unassignedSlots[i - 1];
      if (slot) {
        slot.memberId = memberId;
        slot.role = member.role;
        assigned++;
      }
    }

    this.groupFormations.set(groupId, slots);
  }

  /**
   * Get target position for a group member
   */
  private getMemberTargetPosition(
    groupId: string,
    memberId: string,
    groupTarget: MovementTarget
  ): NPCPosition | null {
    const formation = this.groupFormations.get(groupId);
    if (!formation) return null;

    const slot = formation.find(s => s.memberId === memberId);
    if (!slot) return null;

    return {
      x: groupTarget.x + slot.relativePosition.x,
      y: groupTarget.y + slot.relativePosition.y
    };
  }

  /**
   * Calculate movement vector between two positions
   */
  private calculateMovementVector(
    current: NPCPosition,
    target: NPCPosition,
    speed: number
  ): NPCPosition {
    const dx = target.x - current.x;
    const dy = target.y - current.y;
    const distance = Math.sqrt(dx * dx + dy * dy);

    if (distance <= speed) {
      return target;
    }

    return {
      x: current.x + (dx / distance) * speed,
      y: current.y + (dy / distance) * speed
    };
  }
} 
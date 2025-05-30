from typing import Any, Dict, List


class MovementTarget:
    x: float
    y: float
    priority: float
    deadline?: float
class FormationSlot:
    relativePosition: NPCPosition
    memberId?: str
    role?: GroupRole
class GroupMovementSystem {
  private groupManager: GroupManager
  private spatialGrid: SpatialGrid
  private pathfinding: PathfindingSystem
  private groupTargets: Map<string, MovementTarget>
  private groupFormations: Map<string, FormationSlot[]>
  private groupPaths: Map<string, GridPosition[]>
  private readonly FORMATION_SPACING = 2 
  private readonly PATH_RECALCULATION_INTERVAL = 1000 
  private readonly OBSTACLE_CHECK_RADIUS = 3 
  constructor(
    groupManager: GroupManager,
    gridSize: float = 100,
    pathfinding: PathfindingSystem
  ) {
    this.groupManager = groupManager
    this.spatialGrid = new SpatialGrid(gridSize)
    this.pathfinding = pathfinding
    this.groupTargets = new Map()
    this.groupFormations = new Map()
    this.groupPaths = new Map()
  }
  /**
   * Set a movement target for a group
   */
  public setGroupTarget(
    groupId: str,
    target: \'MovementTarget\'
  ): bool {
    const group = this.groupManager.getGroup(groupId)
    if (!group) return false
    this.groupTargets.set(groupId, target)
    this.updateFormation(groupId)
    this.recalculateGroupPath(groupId)
    return true
  }
  /**
   * Clear a group's movement target
   */
  public clearGroupTarget(groupId: str): void {
    this.groupTargets.delete(groupId)
  }
  /**
   * Update positions for all group members
   */
  public update(npcs: Map<string, NPCData>, speed: float = 1): void {
    this.groupTargets.forEach((target, groupId) => {
      const group = this.groupManager.getGroup(groupId)
      if (!group) return
      if (target.deadline && Date.now() > target.deadline) {
        this.groupTargets.delete(groupId)
        this.groupPaths.delete(groupId)
        return
      }
      const path = this.groupPaths.get(groupId)
      if (!path || this.shouldRecalculatePath(groupId)) {
        this.recalculateGroupPath(groupId)
      }
      group.members.forEach((member, memberId) => {
        const npc = npcs.get(memberId)
        if (!npc) return
        const targetPos = this.getMemberTargetPosition(groupId, memberId, target)
        if (!targetPos) return
        const newPos = this.calculateFormationPosition(
          npc.position,
          targetPos,
          speed,
          groupId,
          memberId
        )
        npc.position = newPos
        this.spatialGrid.updateEntity(memberId, newPos)
      })
    })
  }
  /**
   * Calculate new position considering formation and obstacles
   */
  private calculateFormationPosition(
    current: NPCPosition,
    target: NPCPosition,
    speed: float,
    groupId: str,
    memberId: str
  ): NPCPosition {
    const path = this.groupPaths.get(groupId)
    if (!path || path.length === 0) {
      return this.calculateMovementVector(current, target, speed)
    }
    const formationSlots = this.groupFormations.get(groupId) || []
    const memberSlot = formationSlots.find(slot => slot.memberId === memberId)
    if (!memberSlot) {
      return this.calculateMovementVector(current, target, speed)
    }
    const nextPathPoint = path[0]
    const adjustedTarget = {
      x: nextPathPoint.x + memberSlot.relativePosition.x,
      y: nextPathPoint.y + memberSlot.relativePosition.y
    }
    const obstacles = this.checkNearbyObstacles(current)
    if (obstacles > 0) {
      return this.calculateObstacleAvoidance(current, adjustedTarget, speed, obstacles)
    }
    return this.calculateMovementVector(current, adjustedTarget, speed)
  }
  /**
   * Check for obstacles in the immediate vicinity
   */
  private checkNearbyObstacles(position: NPCPosition): float {
    let obstacleCount = 0
    for (let dx = -this.OBSTACLE_CHECK_RADIUS; dx <= this.OBSTACLE_CHECK_RADIUS; dx++) {
      for (let dy = -this.OBSTACLE_CHECK_RADIUS; dy <= this.OBSTACLE_CHECK_RADIUS; dy++) {
        const checkPos = { x: position.x + dx, y: position.y + dy }
        const entities = this.spatialGrid.getEntitiesInCell(checkPos)
        obstacleCount += entities.length
      }
    }
    return obstacleCount
  }
  /**
   * Calculate position adjustment for obstacle avoidance
   */
  private calculateObstacleAvoidance(
    current: NPCPosition,
    target: NPCPosition,
    speed: float,
    obstacleCount: float
  ): NPCPosition {
    const baseVector = this.calculateMovementVector(current, target, speed)
    const avoidanceWeight = Math.min(obstacleCount * 0.2, 0.8) 
    let bestDirection = { x: 0, y: 0 }
    let minObstacles = Infinity
    const directions = [
      { x: 1, y: 0 }, { x: -1, y: 0 }, { x: 0, y: 1 }, { x: 0, y: -1 },
      { x: 1, y: 1 }, { x: 1, y: -1 }, { x: -1, y: 1 }, { x: -1, y: -1 }
    ]
    for (const dir of directions) {
      const checkPos = {
        x: current.x + dir.x,
        y: current.y + dir.y
      }
      const obstacles = this.checkNearbyObstacles(checkPos)
      if (obstacles < minObstacles) {
        minObstacles = obstacles
        bestDirection = dir
      }
    }
    return {
      x: baseVector.x * (1 - avoidanceWeight) + bestDirection.x * avoidanceWeight * speed,
      y: baseVector.y * (1 - avoidanceWeight) + bestDirection.y * avoidanceWeight * speed
    }
  }
  /**
   * Recalculate path for a group
   */
  private recalculateGroupPath(groupId: str): void {
    const group = this.groupManager.getGroup(groupId)
    const target = this.groupTargets.get(groupId)
    if (!group || !target) return
    const groupCenter = this.getGroupCenter(groupId)
    if (!groupCenter) return
    const path = this.pathfinding.findGroupPath(
      { x: Math.round(groupCenter.x), y: Math.round(groupCenter.y) },
      { x: target.x, y: target.y },
      {
        groupSize: group.members.size,
        formationWidth: Math.ceil(Math.sqrt(group.members.size)),
        formationSpacing: this.FORMATION_SPACING,
        predictiveAvoidance: true
      }
    )
    this.groupPaths.set(groupId, path)
  }
  /**
   * Check if path needs recalculation
   */
  private shouldRecalculatePath(groupId: str): bool {
    const group = this.groupManager.getGroup(groupId)
    const path = this.groupPaths.get(groupId)
    if (!group || !path) return true
    const formationSlots = this.groupFormations.get(groupId) || []
    for (const [memberId, _] of group.members) {
      const memberPos = this.spatialGrid.getEntityPosition(memberId)
      const slot = formationSlots.find(s => s.memberId === memberId)
      if (!memberPos || !slot) continue
      const targetPos = {
        x: path[0].x + slot.relativePosition.x,
        y: path[0].y + slot.relativePosition.y
      }
      const distance = Math.sqrt(
        Math.pow(memberPos.x - targetPos.x, 2) +
        Math.pow(memberPos.y - targetPos.y, 2)
      )
      if (distance > this.FORMATION_SPACING * 2) {
        return true
      }
    }
    return false
  }
  /**
   * Check if a group has reached its target
   */
  public hasReachedTarget(groupId: str, threshold: float = 1): bool {
    const group = this.groupManager.getGroup(groupId)
    const target = this.groupTargets.get(groupId)
    if (!group || !target) return false
    return Array.from(group.members.keys()).every(memberId => {
      const npc = this.spatialGrid.getEntityPosition(memberId)
      const targetPos = this.getMemberTargetPosition(groupId, memberId, target)
      if (!npc || !targetPos) return false
      const dx = targetPos.x - npc.x
      const dy = targetPos.y - npc.y
      const distance = Math.sqrt(dx * dx + dy * dy)
      return distance <= threshold
    })
  }
  /**
   * Get the average position of a group
   */
  public getGroupCenter(groupId: str): NPCPosition | null {
    const group = this.groupManager.getGroup(groupId)
    if (!group) return null
    const memberPositions = Array.from(group.members.keys())
      .map(id => this.spatialGrid.getEntityPosition(id))
      .filter((pos): pos is NPCPosition => pos !== undefined)
    if (memberPositions.length === 0) return null
    return {
      x: memberPositions.reduce((sum, pos) => sum + pos.x, 0) / memberPositions.length,
      y: memberPositions.reduce((sum, pos) => sum + pos.y, 0) / memberPositions.length
    }
  }
  /**
   * Clean up when a group is disbanded
   */
  public cleanupGroup(groupId: str): void {
    this.groupTargets.delete(groupId)
    this.groupFormations.delete(groupId)
  }
  /**
   * Update formation slots for a group
   */
  private updateFormation(groupId: str): void {
    const group = this.groupManager.getGroup(groupId)
    if (!group) return
    const slots: List[FormationSlot] = []
    const size = group.members.size
    const cols = Math.ceil(Math.sqrt(size))
    const rows = Math.ceil(size / cols)
    for (let row = 0; row < rows; row++) {
      for (let col = 0; col < cols; col++) {
        slots.push({
          relativePosition: Dict[str, Any]
        })
      }
    }
    const sortedMembers = Array.from(group.members.entries())
      .sort(([_, a], [__, b]) => {
        if (a.role === GroupRole.LEADER) return -1
        if (b.role === GroupRole.LEADER) return 1
        return (a.role || '').localeCompare(b.role || '')
      })
    const centerSlot = slots.reduce((best, slot, index) => {
      const distFromCenter = Math.sqrt(
        slot.relativePosition.x ** 2 + slot.relativePosition.y ** 2
      )
      if (distFromCenter < Math.sqrt(
        best.slot.relativePosition.x ** 2 + best.slot.relativePosition.y ** 2
      )) {
        return { slot, index }
      }
      return best
    }, { slot: slots[0], index: 0 })
    slots[centerSlot.index].memberId = sortedMembers[0][0]
    const unassignedSlots = slots.filter((_, i) => i !== centerSlot.index)
    let assigned = 1
    for (let i = 1; i < sortedMembers.length; i++) {
      const [memberId, member] = sortedMembers[i]
      const slot = unassignedSlots[i - 1]
      if (slot) {
        slot.memberId = memberId
        slot.role = member.role
        assigned++
      }
    }
    this.groupFormations.set(groupId, slots)
  }
  /**
   * Get target position for a group member
   */
  private getMemberTargetPosition(
    groupId: str,
    memberId: str,
    groupTarget: \'MovementTarget\'
  ): NPCPosition | null {
    const formation = this.groupFormations.get(groupId)
    if (!formation) return null
    const slot = formation.find(s => s.memberId === memberId)
    if (!slot) return null
    return {
      x: groupTarget.x + slot.relativePosition.x,
      y: groupTarget.y + slot.relativePosition.y
    }
  }
  /**
   * Calculate movement vector between two positions
   */
  private calculateMovementVector(
    current: NPCPosition,
    target: NPCPosition,
    speed: float
  ): NPCPosition {
    const dx = target.x - current.x
    const dy = target.y - current.y
    const distance = Math.sqrt(dx * dx + dy * dy)
    if (distance <= speed) {
      return target
    }
    return {
      x: current.x + (dx / distance) * speed,
      y: current.y + (dy / distance) * speed
    }
  }
} 
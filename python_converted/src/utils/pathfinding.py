from typing import Any, List


class PathCache:
    path: List[GridPosition]
    timestamp: float
    category?: POICategory
class GroupPathfindingOptions:
    groupSize?: float
    formationWidth?: float
    formationSpacing?: float
    predictiveAvoidance?: bool
class CategoryPathRules:
    preferredTypes: List[CellType]
    avoidTypes: List[CellType]
    weightMultiplier: float
class PathfindingSystem {
  private gridManager: GridManager
  private collisionSystem: CollisionSystem
  private pathCache: Map<string, PathCache>
  private readonly CACHE_DURATION = 5000 
  private categoryRules: Record<POICategory, CategoryPathRules>
  private readonly PREDICTIVE_LOOKAHEAD = 3
  constructor(gridManager: GridManager, collisionSystem: CollisionSystem) {
    this.gridManager = gridManager
    this.collisionSystem = collisionSystem
    this.pathCache = new Map()
    this.categoryRules = {
      [POICategory.SOCIAL]: {
        preferredTypes: [CellType.ROAD, CellType.EMPTY],
        avoidTypes: [CellType.WALL, CellType.BLOCKED],
        weightMultiplier: 1.0
      },
      [POICategory.DUNGEON]: {
        preferredTypes: [CellType.EMPTY],
        avoidTypes: [CellType.ROAD],
        weightMultiplier: 1.5
      },
      [POICategory.EXPLORATION]: {
        preferredTypes: [CellType.EMPTY, CellType.ROAD],
        avoidTypes: [CellType.BLOCKED],
        weightMultiplier: 0.8
      }
    }
  }
  /**
   * Find a path between two points
   */
  public findPath(
    start: GridPosition,
    end: GridPosition,
    predictiveAvoidance: bool = false
  ): GridPosition[] {
    const openSet: List[PathfindingNode] = []
    const closedSet: Set<string> = new Set()
    const startNode: PathfindingNode = {
      position: start,
      gCost: 0,
      hCost: this.calculateHeuristic(start, end)
    }
    openSet.push(startNode)
    while (openSet.length > 0) {
      const currentNode = this.getLowestFCostNode(openSet)
      if (this.isSamePosition(currentNode.position, end)) {
        return this.reconstructPath(currentNode)
      }
      this.removeFromArray(openSet, currentNode)
      closedSet.add(this.positionToString(currentNode.position))
      const neighbors = this.getWalkableNeighbors(currentNode.position)
      for (const neighbor of neighbors) {
        if (closedSet.has(this.positionToString(neighbor))) {
          continue
        }
        let newGCost = currentNode.gCost + this.getNodeCost({
          position: neighbor,
          gCost: 0,
          hCost: 0
        })
        if (predictiveAvoidance) {
          newGCost += this.calculatePredictiveCollisionCost(neighbor)
        }
        const neighborNode = openSet.find(node => 
          this.isSamePosition(node.position, neighbor)
        )
        if (!neighborNode) {
          openSet.push({
            position: neighbor,
            gCost: newGCost,
            hCost: this.calculateHeuristic(neighbor, end),
            parent: currentNode
          })
        } else if (newGCost < neighborNode.gCost) {
          const updatedNode = {
            ...neighborNode,
            gCost: newGCost,
            parent: currentNode
          }
          const index = openSet.indexOf(neighborNode)
          openSet[index] = updatedNode
        }
      }
    }
    return [] 
  }
  public invalidateCache(position: GridPosition, radius: float = 1): void {
    const now = Date.now()
    this.pathCache.forEach((cache, key) => {
      const isAffected = cache.path.some(point => 
        Math.abs(point.x - position.x) <= radius &&
        Math.abs(point.y - position.y) <= radius
      )
      if (isAffected) {
        this.pathCache.delete(key)
      }
    })
    this.cleanCache(now)
  }
  public updatePathSegment(
    path: List[GridPosition],
    startIndex: float,
    endIndex: float,
    category?: POICategory
  ): GridPosition[] {
    if (startIndex >= endIndex || startIndex < 0 || endIndex >= path.length) {
      return path
    }
    const start = path[startIndex]
    const end = path[endIndex]
    const newSegment = this.calculatePath(start, end, category)
    if (newSegment.length === 0) return path
    return [
      ...path.slice(0, startIndex),
      ...newSegment.slice(1, -1), 
      ...path.slice(endIndex)
    ]
  }
  /**
   * Find a path suitable for group movement
   */
  public findGroupPath(
    start: GridPosition,
    end: GridPosition,
    options: \'GroupPathfindingOptions\'
  ): GridPosition[] {
    const {
      groupSize = 1,
      formationWidth = 1,
      formationSpacing = 2,
      predictiveAvoidance = true
    } = options
    const groupWidth = formationWidth * formationSpacing
    const groupHeight = Math.ceil(groupSize / formationWidth) * formationSpacing
    const originalGetNodeCost = this.getNodeCost.bind(this)
    this.getNodeCost = (node: PathfindingNode): float => {
      let cost = originalGetNodeCost(node)
      const dimensions = {
        width: groupWidth,
        height: groupHeight
      }
      const collisions = this.collisionSystem.findCollisions(
        { x: node.position.x, y: node.position.y },
        dimensions
      )
      if (collisions.length > 0) {
        cost += collisions.length * 2
      }
      const terrainCost = this.getTerrainCost(node)
      cost += terrainCost * Math.sqrt(groupSize)
      return cost
    }
    const path = this.findPath(start, end, predictiveAvoidance)
    this.getNodeCost = originalGetNodeCost
    return path
  }
  /**
   * Get terrain-based cost for a node
   */
  private getTerrainCost(node: PathfindingNode): float {
    const cell = this.gridManager.getCellAt(node.position)
    if (!cell) return Infinity
    switch (cell.cellType) {
      case CellType.ROUGH:
        return 2
      case CellType.WATER:
        return 3
      case CellType.WALL:
      case CellType.BLOCKED:
        return Infinity
      default:
        return 1
    }
  }
  private calculatePath(
    start: GridPosition,
    end: GridPosition,
    category?: POICategory,
    groupOptions?: {
      groupWidth: float
      groupHeight: float
      predictiveAvoidance: bool
      formationSpacing: float
    }
  ): GridPosition[] {
    const openSet: List[PathfindingNode] = []
    const closedSet: Set<string> = new Set()
    const startNode: PathfindingNode = {
      position: start,
      gCost: 0,
      hCost: this.calculateHeuristic(start, end, category)
    }
    openSet.push(startNode)
    while (openSet.length > 0) {
      const currentNode = this.getLowestFCostNode(openSet)
      if (this.isSamePosition(currentNode.position, end)) {
        return this.reconstructPath(currentNode)
      }
      this.removeFromArray(openSet, currentNode)
      closedSet.add(this.positionToString(currentNode.position))
      const neighbors = this.getWalkableNeighbors(currentNode.position, category, groupOptions)
      for (const neighbor of neighbors) {
        if (closedSet.has(this.positionToString(neighbor))) {
          continue
        }
        const movementCost = this.calculateMovementCost(
          currentNode.position,
          neighbor,
          category,
          groupOptions
        )
        const gCost = currentNode.gCost + movementCost
        const neighborNode = openSet.find(node => 
          this.isSamePosition(node.position, neighbor)
        )
        if (!neighborNode) {
          openSet.push({
            position: neighbor,
            gCost,
            hCost: this.calculateHeuristic(neighbor, end, category),
            parent: currentNode
          })
        } else if (gCost < neighborNode.gCost) {
          neighborNode.gCost = gCost
          neighborNode.parent = currentNode
        }
      }
    }
    return [] 
  }
  private calculateMovementCost(
    from: GridPosition,
    to: GridPosition,
    category?: POICategory,
    groupOptions?: {
      groupWidth: float
      groupHeight: float
      predictiveAvoidance: bool
      formationSpacing: float
    }
  ): float {
    const cell = this.gridManager.getCellAt(to)
    if (!cell) return Infinity
    let cost = 1 
    if (category) {
      const rules = this.categoryRules[category]
      if (rules.preferredTypes.includes(cell.cellType)) {
        cost *= 0.8 
      }
      if (rules.avoidTypes.includes(cell.cellType)) {
        cost *= 2.0 
      }
      cost *= rules.weightMultiplier
    }
    if (groupOptions) {
      const { groupWidth, groupHeight, predictiveAvoidance } = groupOptions
      const formationCollisions = this.checkFormationCollisions(to, groupWidth, groupHeight)
      if (formationCollisions > 0) {
        cost *= (1 + formationCollisions * 0.5) 
      }
      if (predictiveAvoidance) {
        const futureCost = this.calculatePredictiveCollisionCost(to)
        cost += futureCost
      }
    } else {
      const collisions = this.collisionSystem.findCollisions(to, { width: 1, height: 1 })
      if (collisions.length > 0) {
        cost *= 1.5 
      }
    }
    return cost
  }
  private checkFormationCollisions(
    position: GridPosition,
    width: float,
    height: float
  ): float {
    let collisionCount = 0
    for (let x = position.x; x <= position.x + width; x++) {
      for (let y = position.y; y <= position.y + height; y++) {
        const collisions = this.collisionSystem.findCollisions(
          { x, y },
          { width: 1, height: 1 }
        )
        collisionCount += collisions.length
      }
    }
    return collisionCount
  }
  private calculatePredictiveCollisionCost(position: GridPosition): float {
    let predictiveCost = 0
    for (let step = 1; step <= this.PREDICTIVE_LOOKAHEAD; step++) {
      const searchDimensions = {
        width: 1 + step,
        height: 1 + step
      }
      const collisions = this.collisionSystem.findCollisions(
        {
          x: position.x - Math.floor(step / 2),
          y: position.y - Math.floor(step / 2)
        },
        searchDimensions
      )
      if (collisions.length > 0) {
        predictiveCost += (collisions.length * 0.2) / step
      }
    }
    return predictiveCost
  }
  private calculateHeuristic(
    start: GridPosition,
    end: GridPosition,
    category?: POICategory
  ): float {
    let base = Math.abs(start.x - end.x) + Math.abs(start.y - end.y)
    if (category) {
      const rules = this.categoryRules[category]
      base *= rules.weightMultiplier
    }
    return base
  }
  private getWalkableNeighbors(
    position: GridPosition,
    category?: POICategory,
    groupOptions?: {
      groupWidth: float
      groupHeight: float
      predictiveAvoidance: bool
      formationSpacing: float
    }
  ): GridPosition[] {
    const neighbors: List[GridPosition] = []
    const directions = [
      { x: 0, y: -1 },  
      { x: 1, y: 0 },   
      { x: 0, y: 1 },   
      { x: -1, y: 0 },  
      { x: 1, y: -1 },  
      { x: 1, y: 1 },   
      { x: -1, y: 1 },  
      { x: -1, y: -1 }  
    ]
    for (const dir of directions) {
      const newPos = {
        x: position.x + dir.x,
        y: position.y + dir.y
      }
      const cell = this.gridManager.getCellAt(newPos)
      if (!cell) continue
      if (category) {
        const rules = this.categoryRules[category]
        if (rules.avoidTypes.includes(cell.cellType)) continue
      }
      if (groupOptions) {
        const { groupWidth, groupHeight } = groupOptions
        let formationWalkable = true
        for (let x = newPos.x; x <= newPos.x + groupWidth && formationWalkable; x++) {
          for (let y = newPos.y; y <= newPos.y + groupHeight && formationWalkable; y++) {
            const formationCell = this.gridManager.getCellAt({ x, y })
            if (!formationCell || !formationCell.walkable) {
              formationWalkable = false
            }
          }
        }
        if (!formationWalkable) continue
      }
      if (cell.walkable) {
        neighbors.push(newPos)
      }
    }
    return neighbors
  }
  private getCacheKey(
    start: GridPosition,
    end: GridPosition,
    category?: POICategory
  ): str {
    return `${start.x},${start.y}-${end.x},${end.y}${category ? `-${category}` : ''}`
  }
  private getValidCachedPath(key: str): GridPosition[] | null {
    const cached = this.pathCache.get(key)
    if (!cached) return null
    const age = Date.now() - cached.timestamp
    if (age > this.CACHE_DURATION) {
      this.pathCache.delete(key)
      return null
    }
    for (const point of cached.path) {
      const cell = this.gridManager.getCellAt(point)
      if (!cell || !cell.walkable || cell.isOccupied) {
        this.pathCache.delete(key)
        return null
      }
    }
    return cached.path
  }
  private cleanCache(now: float = Date.now()): void {
    for (const [key, cache] of this.pathCache.entries()) {
      if (now - cache.timestamp > this.CACHE_DURATION) {
        this.pathCache.delete(key)
      }
    }
  }
  private getLowestFCostNode(nodes: List[PathfindingNode]): PathfindingNode {
    let lowest = nodes[0]
    for (let i = 1; i < nodes.length; i++) {
      const fCost = nodes[i].gCost + nodes[i].hCost
      const lowestFCost = lowest.gCost + lowest.hCost
      if (fCost < lowestFCost || (fCost === lowestFCost && nodes[i].hCost < lowest.hCost)) {
        lowest = nodes[i]
      }
    }
    return lowest
  }
  private reconstructPath(endNode: PathfindingNode): GridPosition[] {
    const path: List[GridPosition] = []
    let currentNode: PathfindingNode | undefined = endNode
    while (currentNode) {
      path.unshift(currentNode.position)
      currentNode = currentNode.parent
    }
    return path
  }
  private removeFromArray(arr: List[PathfindingNode], item: PathfindingNode): void {
    const index = arr.findIndex(node => 
      this.isSamePosition(node.position, item.position)
    )
    if (index !== -1) {
      arr.splice(index, 1)
    }
  }
  private isSamePosition(a: GridPosition, b: GridPosition): bool {
    return a.x === b.x && a.y === b.y
  }
  private positionToString(pos: GridPosition): str {
    return `${pos.x},${pos.y}`
  }
  /**
   * Get the cost of moving to a node
   */
  private getNodeCost(node: PathfindingNode): float {
    const cell = this.gridManager.getCellAt(node.position)
    if (!cell) return Infinity
    let cost = 1
    cost += this.getTerrainCost(node)
    const collisions = this.collisionSystem.findCollisions(
      node.position,
      { width: 1, height: 1 }
    )
    if (collisions.length > 0) {
      cost += collisions.length
    }
    return cost
  }
} 
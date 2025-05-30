from typing import Any, Dict, List



class PathfindingSystem {
  private gridManager: GridManager
  constructor(gridManager: GridManager) {
    this.gridManager = gridManager
  }
  public findPath(start: GridPosition, end: GridPosition): GridPosition[] {
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
        const gCost = currentNode.gCost + 1
        const neighborNode = openSet.find(node => 
          this.isSamePosition(node.position, neighbor)
        )
        if (!neighborNode) {
          openSet.push({
            position: neighbor,
            gCost,
            hCost: this.calculateHeuristic(neighbor, end),
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
  public isPathPossible(start: GridPosition, end: GridPosition): bool {
    return this.findPath(start, end).length > 0
  }
  public findAccessibleArea(start: GridPosition, maxDistance: float): Set<string> {
    const accessible = new Set<string>()
    const queue: Dict[str, Any][] = [
      { position: start, distance: 0 }
    ]
    while (queue.length > 0) {
      const current = queue.shift()!
      const posStr = this.positionToString(current.position)
      if (accessible.has(posStr)) continue
      accessible.add(posStr)
      if (current.distance >= maxDistance) continue
      const neighbors = this.getWalkableNeighbors(current.position)
      for (const neighbor of neighbors) {
        const neighborStr = this.positionToString(neighbor)
        if (!accessible.has(neighborStr)) {
          queue.push({
            position: neighbor,
            distance: current.distance + 1
          })
        }
      }
    }
    return accessible
  }
  private calculateHeuristic(start: GridPosition, end: GridPosition): float {
    return Math.abs(start.x - end.x) + Math.abs(start.y - end.y)
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
  private getWalkableNeighbors(position: GridPosition): GridPosition[] {
    const neighbors: List[GridPosition] = []
    const directions = [
      { x: 0, y: -1 },  
      { x: 1, y: 0 },   
      { x: 0, y: 1 },   
      { x: -1, y: 0 }   
    ]
    for (const dir of directions) {
      const newPos = {
        x: position.x + dir.x,
        y: position.y + dir.y
      }
      const cell = this.gridManager.getCellAt(newPos)
      if (cell && cell.walkable && !cell.isOccupied) {
        neighbors.push(newPos)
      }
    }
    return neighbors
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
} 
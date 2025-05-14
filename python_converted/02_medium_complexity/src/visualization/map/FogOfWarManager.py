from typing import Any, List



class FogOfWarManager {
  private visibilityMap: List[boolean][]
  private exploredMap: List[boolean][]
  constructor(private mapData: MapData) {
    this.visibilityMap = Array(mapData.size.height).fill(false).map(() => 
      Array(mapData.size.width).fill(false)
    )
    this.exploredMap = Array(mapData.size.height).fill(false).map(() => 
      Array(mapData.size.width).fill(false)
    )
  }
  private isInBounds(x: float, y: float): bool {
    return x >= 0 && x < this.mapData.size.width && y >= 0 && y < this.mapData.size.height
  }
  private calculateLineOfSight(from: Point, to: Point): bool {
    let x0 = Math.floor(from.x)
    let y0 = Math.floor(from.y)
    const x1 = Math.floor(to.x)
    const y1 = Math.floor(to.y)
    const dx = Math.abs(x1 - x0)
    const dy = Math.abs(y1 - y0)
    const sx = x0 < x1 ? 1 : -1
    const sy = y0 < y1 ? 1 : -1
    let err = dx - dy
    while (true) {
      if (!this.isInBounds(x0, y0)) {
        return false
      }
      const tile = this.mapData.tiles[y0][x0]
      const elevation = tile.elevation
      const fromElevation = this.mapData.tiles[Math.floor(from.y)][Math.floor(from.x)].elevation
      const toElevation = this.mapData.tiles[y1][x1].elevation
      const expectedElevation = fromElevation + (toElevation - fromElevation) * 
        (Math.sqrt((x0 - from.x) ** 2 + (y0 - from.y) ** 2) / 
         Math.sqrt((to.x - from.x) ** 2 + (to.y - from.y) ** 2))
      if (elevation > expectedElevation + 1) { 
        return false
      }
      if (x0 === x1 && y0 === y1) {
        break
      }
      const e2 = 2 * err
      if (e2 > -dy) {
        err -= dy
        x0 += sx
      }
      if (e2 < dx) {
        err += dx
        y0 += sy
      }
    }
    return true
  }
  public updateVisibility(viewerPosition: Point, viewRadius: float): void {
    for (let y = 0; y < this.mapData.size.height; y++) {
      for (let x = 0; x < this.mapData.size.width; x++) {
        this.visibilityMap[y][x] = false
      }
    }
    const startX = Math.max(0, Math.floor(viewerPosition.x - viewRadius))
    const startY = Math.max(0, Math.floor(viewerPosition.y - viewRadius))
    const endX = Math.min(this.mapData.size.width, Math.ceil(viewerPosition.x + viewRadius))
    const endY = Math.min(this.mapData.size.height, Math.ceil(viewerPosition.y + viewRadius))
    for (let y = startY; y < endY; y++) {
      for (let x = startX; x < endX; x++) {
        const distance = Math.sqrt(
          (x - viewerPosition.x) ** 2 + 
          (y - viewerPosition.y) ** 2
        )
        if (distance <= viewRadius) {
          if (this.calculateLineOfSight(viewerPosition, { x, y })) {
            this.visibilityMap[y][x] = true
            this.exploredMap[y][x] = true
          }
        }
      }
    }
  }
  public updateVisibilityMultipleViewers(viewers: Array<{ position: Point, radius: float }>): void {
    for (let y = 0; y < this.mapData.size.height; y++) {
      for (let x = 0; x < this.mapData.size.width; x++) {
        this.visibilityMap[y][x] = false
      }
    }
    for (const viewer of viewers) {
      this.updateVisibility(viewer.position, viewer.radius)
    }
  }
  public isVisible(x: float, y: float): bool {
    return this.isInBounds(x, y) && this.visibilityMap[y][x]
  }
  public isExplored(x: float, y: float): bool {
    return this.isInBounds(x, y) && this.exploredMap[y][x]
  }
  public getTileVisibility(tile: Tile): { visible: bool, explored: bool } {
    const x = Math.floor(tile.position.x)
    const y = Math.floor(tile.position.y)
    return {
      visible: this.isVisible(x, y),
      explored: this.isExplored(x, y)
    }
  }
  public revealArea(center: Point, radius: float): void {
    const startX = Math.max(0, Math.floor(center.x - radius))
    const startY = Math.max(0, Math.floor(center.y - radius))
    const endX = Math.min(this.mapData.size.width, Math.ceil(center.x + radius))
    const endY = Math.min(this.mapData.size.height, Math.ceil(center.y + radius))
    for (let y = startY; y < endY; y++) {
      for (let x = startX; x < endX; x++) {
        const distance = Math.sqrt(
          (x - center.x) ** 2 + 
          (y - center.y) ** 2
        )
        if (distance <= radius) {
          this.visibilityMap[y][x] = true
          this.exploredMap[y][x] = true
        }
      }
    }
  }
  public clear(): void {
    for (let y = 0; y < this.mapData.size.height; y++) {
      for (let x = 0; x < this.mapData.size.width; x++) {
        this.visibilityMap[y][x] = false
        this.exploredMap[y][x] = false
      }
    }
  }
} 
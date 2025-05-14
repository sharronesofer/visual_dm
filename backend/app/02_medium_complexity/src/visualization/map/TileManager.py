from typing import Any, Dict, List



class TileManager {
  private tiles: Map<string, Tile> = new Map()
  private tilePool: List[Tile] = []
  private readonly poolSize: float = 1000
  constructor(private mapData: MapData) {
    this.initializeTilePool()
  }
  private initializeTilePool(): void {
    for (let i = 0; i < this.poolSize; i++) {
      this.tilePool.push({
        id: `pool-${i}`,
        type: TerrainType.GRASS,
        position: Dict[str, Any],
        elevation: 0,
        walkable: true,
        explored: false,
        visible: false,
      })
    }
  }
  private getTileKey(x: float, y: float): str {
    return `${x},${y}`
  }
  private getTileFromPool(): Tile | undefined {
    return this.tilePool.pop()
  }
  private returnTileToPool(tile: Tile): void {
    if (this.tilePool.length < this.poolSize) {
      this.tilePool.push(tile)
    }
  }
  public loadTile(x: float, y: float): Tile | null {
    if (x < 0 || y < 0 || x >= this.mapData.size.width || y >= this.mapData.size.height) {
      return null
    }
    const key = this.getTileKey(x, y)
    let tile = this.tiles.get(key)
    if (!tile) {
      tile = this.getTileFromPool()
      if (!tile) {
        return null
      }
      const mapTile = this.mapData.tiles[y][x]
      tile.id = mapTile.id
      tile.type = mapTile.type
      tile.position = { x, y }
      tile.elevation = mapTile.elevation
      tile.walkable = mapTile.walkable
      tile.explored = mapTile.explored
      tile.visible = mapTile.visible
      this.tiles.set(key, tile)
    }
    return tile
  }
  public unloadTile(x: float, y: float): void {
    const key = this.getTileKey(x, y)
    const tile = this.tiles.get(key)
    if (tile) {
      this.returnTileToPool(tile)
      this.tiles.delete(key)
    }
  }
  public updateTileVisibility(x: float, y: float, visible: bool): void {
    const key = this.getTileKey(x, y)
    const tile = this.tiles.get(key)
    if (tile) {
      tile.visible = visible
      if (visible) {
        tile.explored = true
      }
    }
  }
  public getTilesInViewport(viewportStart: Point, viewportSize: Size): Tile[] {
    const visibleTiles: List[Tile] = []
    const startX = Math.max(0, Math.floor(viewportStart.x))
    const startY = Math.max(0, Math.floor(viewportStart.y))
    const endX = Math.min(this.mapData.size.width, Math.ceil(viewportStart.x + viewportSize.width))
    const endY = Math.min(this.mapData.size.height, Math.ceil(viewportStart.y + viewportSize.height))
    for (let y = startY; y < endY; y++) {
      for (let x = startX; x < endX; x++) {
        const tile = this.loadTile(x, y)
        if (tile) {
          visibleTiles.push(tile)
        }
      }
    }
    return visibleTiles
  }
  public unloadTilesOutsideViewport(viewportStart: Point, viewportSize: Size, buffer: float = 2): void {
    const startX = Math.max(0, Math.floor(viewportStart.x - buffer))
    const startY = Math.max(0, Math.floor(viewportStart.y - buffer))
    const endX = Math.min(this.mapData.size.width, Math.ceil(viewportStart.x + viewportSize.width + buffer))
    const endY = Math.min(this.mapData.size.height, Math.ceil(viewportStart.y + viewportSize.height + buffer))
    for (const [key, tile] of this.tiles.entries()) {
      const { x, y } = tile.position
      if (x < startX || x >= endX || y < startY || y >= endY) {
        this.unloadTile(x, y)
      }
    }
  }
  public clear(): void {
    for (const tile of this.tiles.values()) {
      this.returnTileToPool(tile)
    }
    this.tiles.clear()
  }
} 
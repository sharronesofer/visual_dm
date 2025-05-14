from typing import Any, Dict, List


class Tile:
    type: str
    walkable: bool
    description?: str
    texture?: str
class MapChunk:
    x: float
    y: float
    width: float
    height: float
    tiles: Dict[str, Tile>
    entities: Dict[str, Any>
    lastAccessed: float
class MapService {
  private static instance: \'MapService\'
  private isFetching: bool
  private constructor() {
    this.isFetching = false
  }
  public static getInstance(): \'MapService\' {
    if (!MapService.instance) {
      MapService.instance = new MapService()
    }
    return MapService.instance
  }
  private getChunkKey(x: float, y: float): { x: float; y: float } {
    const store = useMapStore.getState()
    const chunkX = Math.floor(x / store.chunkSize)
    const chunkY = Math.floor(y / store.chunkSize)
    return { x: chunkX, y: chunkY }
  }
  private async fetchChunk(x: float, y: float): Promise<Omit<MapChunk, 'lastAccessed'>> {
    const store = useMapStore.getState()
    const response = await fetch(`/api/map/chunk?x=${x}&y=${y}&size=${store.chunkSize}`)
    if (!response.ok) {
      throw new Error('Failed to fetch map chunk')
    }
    return await response.json()
  }
  private async processPrefetchQueue(): Promise<void> {
    const store = useMapStore.getState()
    if (this.isFetching || store.activeChunks.size === 0) return
    this.isFetching = true
    const [nextChunkKey] = store.activeChunks
    store.activeChunks.delete(nextChunkKey)
    try {
      const key = deserializeChunkKey(nextChunkKey)
      if (!store.getChunk(key)) {
        const chunk = await this.fetchChunk(key.x * store.chunkSize, key.y * store.chunkSize)
        store.setChunk(key, { ...chunk, isLoading: false })
      }
    } catch (error) {
      console.warn('Failed to prefetch chunk:', error)
    } finally {
      this.isFetching = false
      if (store.activeChunks.size > 0) {
        setTimeout(() => this.processPrefetchQueue(), 100)
      }
    }
  }
  private queueAdjacentChunks(centerX: float, centerY: float): void {
    const store = useMapStore.getState()
    const radius = 1 
    for (let dy = -radius; dy <= radius; dy++) {
      for (let dx = -radius; dx <= radius; dx++) {
        if (dx === 0 && dy === 0) continue
        const key = this.getChunkKey(
          centerX + dx * store.chunkSize,
          centerY + dy * store.chunkSize
        )
        if (!store.getChunk(key)) {
          store.activeChunks.add(`${key.x},${key.y}`)
        }
      }
    }
    this.processPrefetchQueue()
  }
  public async getMapData(position: Position): Promise<{
    tiles: Record<string, Tile>
    entities: Record<string, any>
    visibleArea: List[Position]
  }> {
    const store = useMapStore.getState()
    const chunkKey = this.getChunkKey(position.x, position.y)
    let chunk = store.getChunk(chunkKey)
    if (!chunk) {
      try {
        const newChunk = await this.fetchChunk(position.x, position.y)
        store.setChunk(chunkKey, { ...newChunk, isLoading: false })
        chunk = store.getChunk(chunkKey)
      } catch (error) {
        console.error('Error fetching map chunk:', error)
        store.setError(error instanceof Error ? error.message : 'Failed to fetch map chunk')
        throw error
      }
    }
    this.queueAdjacentChunks(position.x, position.y)
    const visibleArea = this.calculateVisibleArea(position, 5)
    store.setVisibleArea(visibleArea)
    store.clearInactiveChunks()
    return {
      tiles: chunk!.tiles,
      entities: chunk!.entities,
      visibleArea,
    }
  }
  private calculateVisibleArea(center: Position, radius: float): Position[] {
    const visibleArea: List[Position] = []
    for (let y = center.y - radius; y <= center.y + radius; y++) {
      for (let x = center.x - radius; x <= center.x + radius; x++) {
        if (this.isInRange(center, { x, y }, radius)) {
          visibleArea.push({ x, y })
        }
      }
    }
    return visibleArea
  }
  private isInRange(center: Position, point: Position, radius: float): bool {
    const dx = center.x - point.x
    const dy = center.y - point.y
    return Math.sqrt(dx * dx + dy * dy) <= radius
  }
  public getChunkForPosition(position: Position): \'MapChunk\' | undefined {
    const key = this.getChunkKey(position.x, position.y)
    return useMapStore.getState().getChunk(key)
  }
}
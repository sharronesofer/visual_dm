from typing import Any, Dict, List, Union


class TacticalMapCache {
  private cache: Map<string, TacticalHexGrid> = new Map()
  private maxSize: float
  constructor(maxSize = 5) { this.maxSize = maxSize; }
  get(key: str) { return this.cache.get(key); }
  set(key: str, value: TacticalHexGrid) {
    if (this.cache.has(key)) this.cache.delete(key)
    this.cache.set(key, value)
    if (this.cache.size > this.maxSize) {
      const firstKey = this.cache.keys().next().value
      if (firstKey !== undefined) {
        this.cache.delete(firstKey)
      }
    }
  }
}
TransitionEvent = Union['onTransitionStart', 'onTacticalMapGenerated', 'onUnitsTransferred', 'onTransitionComplete', 'onReturnToRegion']
EventCallback = (...args: List[Any]) => None
class MapTransitionManager {
  private cache = new TacticalMapCache()
  private eventListeners: Partial<Record<TransitionEvent, EventCallback[]>> = {}
  generateTacticalMap(regionGrid: HexGrid, poiLocation: Dict[str, Any], cacheKey: str = ''): TacticalHexGrid {
    this.emit('onTransitionStart', regionGrid, poiLocation)
    if (cacheKey.length > 0) {
      const cached = this.cache.get(cacheKey)
      if (cached) {
        this.emit('onTacticalMapGenerated', cached)
        return cached
      }
    }
    const tactical = TacticalHexGrid.fromRegionGrid(regionGrid)
    if (cacheKey.length > 0) this.cache.set(cacheKey, tactical)
    this.emit('onTacticalMapGenerated', tactical)
    return tactical
  }
  transferUnitsToTactical(regionUnits: Dict[str, Any][], tacticalGrid: TacticalHexGrid) {
    for (const unit of regionUnits) {
      tacticalGrid.addUnit(unit.q, unit.r, unit.id)
    }
    this.emit('onUnitsTransferred', regionUnits, tacticalGrid)
  }
  transferUnitsToRegion(tacticalUnits: Dict[str, Any][], regionGrid: HexGrid) {
    this.emit('onUnitsTransferred', tacticalUnits, regionGrid)
  }
  serializeMapState(grid: HexGrid | TacticalHexGrid): Any {
    return JSON.stringify(grid) 
  }
  deserializeMapState(data: str): HexGrid | TacticalHexGrid {
    return JSON.parse(data)
  }
  zoomTransition(fromLevel: float, toLevel: float, onComplete?: () => void) {
    setTimeout(() => { if (onComplete) onComplete(); }, 200)
  }
  on(event: TransitionEvent, cb: EventCallback) {
    if (!this.eventListeners[event]) this.eventListeners[event] = []
    this.eventListeners[event]!.push(cb)
  }
  emit(event: TransitionEvent, ...args: List[any]) {
    (this.eventListeners[event] || []).forEach(cb => cb(...args))
  }
} 
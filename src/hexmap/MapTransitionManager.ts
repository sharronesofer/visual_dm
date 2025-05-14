// MapTransitionManager.ts
// Handles transitions between region and tactical (combat/POI) maps

import { HexGrid } from './HexGrid';
import { TacticalHexGrid } from './TacticalHexGrid';

// Simple LRU cache for tactical maps
class TacticalMapCache {
  private cache: Map<string, TacticalHexGrid> = new Map();
  private maxSize: number;
  constructor(maxSize = 5) { this.maxSize = maxSize; }
  get(key: string) { return this.cache.get(key); }
  set(key: string, value: TacticalHexGrid) {
    if (this.cache.has(key)) this.cache.delete(key);
    this.cache.set(key, value);
    if (this.cache.size > this.maxSize) {
      const firstKey = this.cache.keys().next().value;
      if (firstKey !== undefined) {
        this.cache.delete(firstKey);
      }
    }
  }
}

export type TransitionEvent = 'onTransitionStart' | 'onTacticalMapGenerated' | 'onUnitsTransferred' | 'onTransitionComplete' | 'onReturnToRegion';

type EventCallback = (...args: any[]) => void;

export class MapTransitionManager {
  private cache = new TacticalMapCache();
  private eventListeners: Partial<Record<TransitionEvent, EventCallback[]>> = {};

  // Generate tactical map from region grid and POI location
  generateTacticalMap(regionGrid: HexGrid, poiLocation: {q: number, r: number}, cacheKey: string = ''): TacticalHexGrid {
    this.emit('onTransitionStart', regionGrid, poiLocation);
    if (cacheKey.length > 0) {
      const cached = this.cache.get(cacheKey);
      if (cached) {
        this.emit('onTacticalMapGenerated', cached);
        return cached;
      }
    }
    const tactical = TacticalHexGrid.fromRegionGrid(regionGrid);
    if (cacheKey.length > 0) this.cache.set(cacheKey, tactical);
    this.emit('onTacticalMapGenerated', tactical);
    return tactical;
  }

  // Transfer units from region to tactical map
  transferUnitsToTactical(regionUnits: {id: string, q: number, r: number}[], tacticalGrid: TacticalHexGrid) {
    for (const unit of regionUnits) {
      tacticalGrid.addUnit(unit.q, unit.r, unit.id);
    }
    this.emit('onUnitsTransferred', regionUnits, tacticalGrid);
  }

  // Transfer units from tactical map back to region
  transferUnitsToRegion(tacticalUnits: {id: string, q: number, r: number}[], regionGrid: HexGrid) {
    // Example: update regionGrid with new unit positions
    // (Assume regionGrid has a method to update unit positions if needed)
    this.emit('onUnitsTransferred', tacticalUnits, regionGrid);
  }

  // Serialize map state
  serializeMapState(grid: HexGrid | TacticalHexGrid): any {
    return JSON.stringify(grid); // For now, use JSON; can be extended
  }

  // Deserialize map state
  deserializeMapState(data: string): HexGrid | TacticalHexGrid {
    // Needs to know which type to restore; stub for now
    return JSON.parse(data);
  }

  // Zoom transition utility (stub for UI integration)
  zoomTransition(fromLevel: number, toLevel: number, onComplete?: () => void) {
    // Could trigger animation, then call onComplete
    setTimeout(() => { if (onComplete) onComplete(); }, 200);
  }

  // Event system
  on(event: TransitionEvent, cb: EventCallback) {
    if (!this.eventListeners[event]) this.eventListeners[event] = [];
    this.eventListeners[event]!.push(cb);
  }
  emit(event: TransitionEvent, ...args: any[]) {
    (this.eventListeners[event] || []).forEach(cb => cb(...args));
  }
} 
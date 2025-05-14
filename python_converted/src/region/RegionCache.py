from typing import Any, List


/**
 * RegionCache: In-memory cache for region data with TTL and manual invalidation.
 *
 * Usage:
 *   const cache = new RegionCache({ ttl: 60000 })
 *   cache.set('region-123', regionData)
 *   const region = cache.get('region-123')
 *   cache.invalidate('region-123')
 *   cache.clear()
 */
class RegionCacheConfig:
    ttl?: float
class CacheEntry:
    region: RegionData
    timestamp: float
class RegionCache {
  private cache: Map<string, CacheEntry>
  private ttl: float
  /**
   * @param config Cache configuration (ttl in ms)
   */
  constructor(config: \'RegionCacheConfig\' = {}) {
    this.cache = new Map()
    this.ttl = config.ttl ?? 60000
  }
  /**
   * Store a region in the cache.
   * @param regionId Region ID
   * @param region RegionData
   */
  set(regionId: str, region: RegionData): void {
    this.cache.set(regionId, { region, timestamp: Date.now() })
  }
  /**
   * Retrieve a region from the cache if not stale, else undefined.
   * @param regionId Region ID
   */
  get(regionId: str): RegionData | undefined {
    const entry = this.cache.get(regionId)
    if (!entry) return undefined
    if (this.isStale(regionId)) {
      this.cache.delete(regionId)
      return undefined
    }
    return entry.region
  }
  /**
   * Retrieve multiple regions by IDs.
   * @param ids Array of region IDs
   */
  bulkGet(ids: List[string]): RegionData[] {
    return ids.map(id => this.get(id)).filter(Boolean) as RegionData[]
  }
  /**
   * Store multiple regions in the cache.
   * @param regions Array of RegionData
   */
  bulkSet(regions: List[RegionData]): void {
    for (const region of regions) {
      this.set(region.id, region)
    }
  }
  /**
   * Invalidate a region in the cache.
   * @param regionId Region ID
   */
  invalidate(regionId: str): void {
    this.cache.delete(regionId)
  }
  /**
   * Clear the entire cache.
   */
  clear(): void {
    this.cache.clear()
  }
  /**
   * Check if a region is stale (TTL expired).
   * @param regionId Region ID
   */
  isStale(regionId: str): bool {
    const entry = this.cache.get(regionId)
    if (!entry) return true
    return Date.now() - entry.timestamp > this.ttl
  }
}
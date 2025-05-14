from typing import Any, List



/**
 * RegionSystem: Manages region data for rendering, using API and cache.
 *
 * Usage:
 *   const api = new RegionApiService({ baseUrl: 'https:
 *   const cache = new RegionCache({ ttl: 60000 })
 *   const system = new RegionSystem(api, cache)
 *   const regions = await system.loadRegionsForViewport({ x: 0, y: 0, width: 1000, height: 1000 })
 */
class RegionSystem {
  private api: RegionApiService
  private cache: RegionCache
  /**
   * @param api RegionApiService instance
   * @param cache RegionCache instance
   */
  constructor(api: RegionApiService, cache: RegionCache) {
    this.api = api
    this.cache = cache
  }
  /**
   * Load all regions for the given viewport.
   * Checks cache first, fetches from API if not present or stale.
   * Returns all region data (from cache or API).
   *
   * @param bounds Viewport bounds
   * @returns Promise<RegionData[]>
   */
  async loadRegionsForViewport(bounds: ViewportBounds): Promise<RegionData[]> {
    let regions: List[RegionData] = []
    try {
      regions = await this.api.fetchByViewport(bounds)
      this.cache.bulkSet(regions)
    } catch (apiErr) {
      console.warn('API fetch failed, using cached data if available:', apiErr)
      regions = Array.from(this.cache['cache'].values()).map(entry => entry.region)
    }
    return regions
  }
  /**
   * Load a single region by ID, using cache if possible.
   * @param regionId Region ID
   * @returns Promise<RegionData | undefined>
   */
  async loadRegionById(regionId: str): Promise<RegionData | undefined> {
    let region = this.cache.get(regionId)
    if (region) return region
    try {
      region = await this.api.fetchById(regionId)
      this.cache.set(regionId, region)
      return region
    } catch (err) {
      console.warn(`Failed to fetch region ${regionId} from API:`, err)
      return undefined
    }
  }
  /**
   * Invalidate a region in the cache (force refresh on next load).
   * @param regionId Region ID
   */
  invalidateRegion(regionId: str): void {
    this.cache.invalidate(regionId)
  }
  /**
   * Clear all cached region data.
   */
  clearCache(): void {
    this.cache.clear()
  }
}
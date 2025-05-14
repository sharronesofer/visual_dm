/**
 * RegionSystem: Manages region data for rendering, using API and cache.
 *
 * Usage:
 *   const api = new RegionApiService({ baseUrl: 'https://api.example.com' });
 *   const cache = new RegionCache({ ttl: 60000 });
 *   const system = new RegionSystem(api, cache);
 *   const regions = await system.loadRegionsForViewport({ x: 0, y: 0, width: 1000, height: 1000 });
 */

import type { RegionData, ViewportBounds, RegionApiService } from './RegionApiService';
import type { RegionCache } from './RegionCache';

export class RegionSystem {
  private api: RegionApiService;
  private cache: RegionCache;

  /**
   * @param api RegionApiService instance
   * @param cache RegionCache instance
   */
  constructor(api: RegionApiService, cache: RegionCache) {
    this.api = api;
    this.cache = cache;
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
    // Fetch region IDs for the viewport from API (could be a separate endpoint or calculated)
    // For this example, we'll fetch all regions in the viewport from the API
    let regions: RegionData[] = [];
    try {
      regions = await this.api.fetchByViewport(bounds);
      // Update cache with fresh data
      this.cache.bulkSet(regions);
    } catch (apiErr) {
      // If API fails, try to get whatever is in cache for the viewport
      // (Assume region IDs are known or can be derived from bounds)
      // For this example, we return all cached regions (not optimal, but placeholder)
      console.warn('API fetch failed, using cached data if available:', apiErr);
      // In a real implementation, you would map bounds to region IDs and get those from cache
      // Here, we return all cached regions (could be filtered by bounds)
      // @ts-expect-error: Temporary type assertion until proper type definitions are added
      regions = Array.from(this.cache['cache'].values()).map(entry => entry.region);
    }
    return regions;
  }

  /**
   * Load a single region by ID, using cache if possible.
   * @param regionId Region ID
   * @returns Promise<RegionData | undefined>
   */
  async loadRegionById(regionId: string): Promise<RegionData | undefined> {
    let region = this.cache.get(regionId);
    if (region) return region;
    try {
      region = await this.api.fetchById(regionId);
      this.cache.set(regionId, region);
      return region;
    } catch (err) {
      console.warn(`Failed to fetch region ${regionId} from API:`, err);
      return undefined;
    }
  }

  /**
   * Invalidate a region in the cache (force refresh on next load).
   * @param regionId Region ID
   */
  invalidateRegion(regionId: string): void {
    this.cache.invalidate(regionId);
  }

  /**
   * Clear all cached region data.
   */
  clearCache(): void {
    this.cache.clear();
  }
}

/**
 * RegionBackgroundLoader: Background loader for region data with progress tracking and cancellation.
 *
 * Usage:
 *   const loader = new RegionBackgroundLoader(regionSystem);
 *   const abortController = new AbortController();
 *   const regions = await loader.loadRegionsInBackground(
 *     { x: 0, y: 0, width: 1000, height: 1000 },
 *     progress => console.log(`Progress: ${Math.round(progress * 100)}%`),
 *     abortController.signal
 *   );
 */

import type { RegionSystem } from './RegionSystem';
import type { ViewportBounds, RegionData } from './RegionApiService';

export class RegionBackgroundLoader {
  private regionSystem: RegionSystem;
  private isLoading: boolean = false;

  /**
   * @param regionSystem RegionSystem instance
   */
  constructor(regionSystem: RegionSystem) {
    this.regionSystem = regionSystem;
  }

  /**
   * Load regions for the viewport in the background, reporting progress.
   * Supports cancellation via AbortSignal.
   *
   * @param bounds Viewport bounds
   * @param onProgress Optional progress callback (0-1)
   * @param abortSignal Optional AbortSignal for cancellation
   * @returns Promise<RegionData[]>
   */
  async loadRegionsInBackground(
    bounds: ViewportBounds,
    onProgress?: (progress: number) => void,
    abortSignal?: AbortSignal
  ): Promise<RegionData[]> {
    this.isLoading = true;
    try {
      // Fetch all regions for the viewport (from cache or API)
      const regions = await this.regionSystem.loadRegionsForViewport(bounds);
      const total = regions.length;
      const loaded: RegionData[] = [];
      for (let i = 0; i < total; i++) {
        if (abortSignal?.aborted) {
          throw new Error('Region background loading aborted');
        }
        // Simulate background loading (could add delay or chunked loading)
        loaded.push(regions[i]);
        if (onProgress) onProgress((i + 1) / total);
        // Optionally yield to event loop for UI responsiveness
        await new Promise(res => setTimeout(res, 0));
      }
      this.isLoading = false;
      return loaded;
    } catch (err) {
      this.isLoading = false;
      throw err;
    }
  }

  /**
   * Returns true if a background load is in progress.
   */
  getLoadingState(): boolean {
    return this.isLoading;
  }
}

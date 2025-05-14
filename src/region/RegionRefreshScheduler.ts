/**
 * RegionRefreshScheduler: Handles periodic refresh and viewport-based loading of region data.
 *
 * Usage:
 *   const scheduler = new RegionRefreshScheduler(regionSystem, backgroundLoader);
 *   scheduler.startPeriodicRefresh(60000); // Refresh every 60s
 *   scheduler.onViewportChange({ x: 0, y: 0, width: 1000, height: 1000 });
 *   await scheduler.manualRefresh();
 *   scheduler.stopPeriodicRefresh();
 */

import type { RegionSystem } from './RegionSystem';
import type { RegionBackgroundLoader } from './RegionBackgroundLoader';
import type { ViewportBounds } from './RegionApiService';

export class RegionRefreshScheduler {
  private regionSystem: RegionSystem;
  private backgroundLoader: RegionBackgroundLoader;
  private refreshIntervalId: NodeJS.Timeout | null = null;
  private lastViewport: ViewportBounds | null = null;
  private throttleTimeout: NodeJS.Timeout | null = null;
  private throttleDelay: number = 500; // ms

  /**
   * @param regionSystem RegionSystem instance
   * @param backgroundLoader RegionBackgroundLoader instance
   */
  constructor(regionSystem: RegionSystem, backgroundLoader: RegionBackgroundLoader) {
    this.regionSystem = regionSystem;
    this.backgroundLoader = backgroundLoader;
  }

  /**
   * Start periodic refresh at the given interval (ms).
   * @param intervalMs Refresh interval in milliseconds
   */
  startPeriodicRefresh(intervalMs: number): void {
    this.stopPeriodicRefresh();
    this.refreshIntervalId = setInterval(() => {
      this.manualRefresh().catch(console.error);
    }, intervalMs);
  }

  /**
   * Stop the periodic refresh.
   */
  stopPeriodicRefresh(): void {
    if (this.refreshIntervalId) {
      clearInterval(this.refreshIntervalId);
      this.refreshIntervalId = null;
    }
  }

  /**
   * Handle viewport changes and trigger background loading (throttled).
   * @param bounds New viewport bounds
   */
  onViewportChange(bounds: ViewportBounds): void {
    this.lastViewport = bounds;
    if (this.throttleTimeout) clearTimeout(this.throttleTimeout);
    this.throttleTimeout = setTimeout(() => {
      this.backgroundLoader.loadRegionsInBackground(bounds, undefined).catch(console.error);
    }, this.throttleDelay);
  }

  /**
   * Manually trigger a refresh of the current viewport.
   */
  async manualRefresh(): Promise<void> {
    if (!this.lastViewport) return;
    await this.backgroundLoader.loadRegionsInBackground(this.lastViewport, undefined);
  }
}

// AssetManager.ts
// Hex-based asset loading, caching, and retrieval system

import AssetIndexLoader from './AssetIndexLoader';

export type AssetCategory = 'terrain' | 'feature' | 'overlay' | 'variation';

// LOD level type
export type LODLevel = 'high' | 'medium' | 'low';

// LOD metadata for an asset
export interface AssetLODMetadata {
  high: string;   // Path to high LOD asset
  medium: string; // Path to medium LOD asset
  low: string;    // Path to low LOD asset
}

interface AssetLoadOptions {
  category?: AssetCategory;
  fallbackPath?: string;
}

// LOD selection options
interface LODLoadOptions extends AssetLoadOptions {
  lod?: LODLevel;
  lodMetadata?: AssetLODMetadata;
  distance?: number; // Used for auto LOD selection
  lodDistances?: { high: number; medium: number; low: number };
}

interface AssetUsage {
  lastAccess: number;
}

const DEFAULT_CACHE_SIZE = 200;
const FALLBACK_IMAGE_SRC = '/assets/fallback.png';

export class AssetManager {
  private loadedAssets: Map<string, HTMLImageElement> = new Map();
  private loadingPromises: Map<string, Promise<HTMLImageElement>> = new Map();
  private usage: Map<string, AssetUsage> = new Map();
  private cacheSize: number;
  private fallbackImage: HTMLImageElement | null = null;

  constructor(cacheSize: number = DEFAULT_CACHE_SIZE) {
    this.cacheSize = cacheSize;
    this.loadFallbackImage();
  }

  private loadFallbackImage() {
    const img = new Image();
    img.src = FALLBACK_IMAGE_SRC;
    img.onload = () => {
      this.fallbackImage = img;
    };
    img.onerror = () => {
      this.fallbackImage = null;
    };
  }

  /**
   * Load a single asset, with deduplication and caching.
   */
  public async loadAsset(path: string, opts?: AssetLoadOptions): Promise<HTMLImageElement> {
    this.maintainCache();
    if (this.loadedAssets.has(path)) {
      this.usage.set(path, { lastAccess: Date.now() });
      return this.loadedAssets.get(path)!;
    }
    if (this.loadingPromises.has(path)) {
      return this.loadingPromises.get(path)!;
    }
    const promise = new Promise<HTMLImageElement>((resolve, reject) => {
      const img = new Image();
      img.onload = () => {
        this.loadedAssets.set(path, img);
        this.usage.set(path, { lastAccess: Date.now() });
        this.loadingPromises.delete(path);
        resolve(img);
      };
      img.onerror = () => {
        this.loadingPromises.delete(path);
        if (opts?.fallbackPath) {
          this.loadAsset(opts.fallbackPath).then(resolve).catch(reject);
        } else if (this.fallbackImage) {
          resolve(this.fallbackImage);
        } else {
          reject(new Error(`Failed to load asset: ${path}`));
        }
      };
      img.src = path;
    });
    this.loadingPromises.set(path, promise);
    return promise;
  }

  /**
   * Load a batch of assets in parallel.
   */
  public async loadBatch(paths: string[], opts?: AssetLoadOptions): Promise<HTMLImageElement[]> {
    return Promise.all(paths.map((p) => this.loadAsset(p, opts)));
  }

  /**
   * Preload assets (non-blocking).
   */
  public preloadAssets(paths: string[], opts?: AssetLoadOptions): void {
    paths.forEach((p) => {
      this.loadAsset(p, opts).catch(() => { });
    });
  }

  /**
   * Unload a specific asset from cache.
   */
  public unloadAsset(path: string): void {
    this.loadedAssets.delete(path);
    this.usage.delete(path);
  }

  /**
   * Clear the entire asset cache.
   */
  public clearCache(): void {
    this.loadedAssets.clear();
    this.usage.clear();
  }

  /**
   * Get a loaded asset synchronously (if present in cache).
   */
  public getAsset(path: string): HTMLImageElement | undefined {
    if (this.loadedAssets.has(path)) {
      this.usage.set(path, { lastAccess: Date.now() });
      return this.loadedAssets.get(path);
    }
    return undefined;
  }

  /**
   * Maintain cache size using LRU eviction.
   */
  private maintainCache() {
    if (this.loadedAssets.size <= this.cacheSize) return;
    // Sort by lastAccess ascending (oldest first)
    const sorted = Array.from(this.usage.entries()).sort((a, b) => a[1].lastAccess - b[1].lastAccess);
    const toEvict = sorted.slice(0, this.loadedAssets.size - this.cacheSize);
    for (const [path] of toEvict) {
      this.loadedAssets.delete(path);
      this.usage.delete(path);
    }
  }

  /**
   * Load all assets in a directory (pattern-based, requires asset manifest or server endpoint).
   * This is a stub; actual implementation depends on environment.
   */
  public async loadDirectory(_dir: string, _pattern = '*.png'): Promise<HTMLImageElement[]> {
    // In browser, this requires a manifest or server API.
    // In Node, use fs.readdir. Here, return empty for now.
    return [];
  }

  // --- Hex-specific helpers ---

  /**
   * Load all variations for a terrain type.
   */
  public async loadTerrainSet(terrainType: string): Promise<HTMLImageElement[]> {
    const paths = Array.from({ length: 6 }, (_, i) => `/assets/terrain/base/${terrainType}_${(i + 1).toString().padStart(2, '0')}.png`);
    return this.loadBatch(paths);
  }

  /**
   * Load all feature variations for a feature type.
   */
  public async loadFeatureVariations(featureType: string): Promise<HTMLImageElement[]> {
    const paths = Array.from({ length: 5 }, (_, i) => `/assets/terrain/features/${featureType}_${(i + 1).toString().padStart(2, '0')}.png`);
    return this.loadBatch(paths);
  }

  /**
   * Load all seasonal/weather variations for a base asset.
   */
  public async loadSeasonalVariations(assetName: string): Promise<HTMLImageElement[]> {
    const variations = [
      ...['summer', 'autumn', 'winter', 'spring'].map(v => `/assets/terrain/variations/${v}_${assetName}`),
      ...['rain', 'snow', 'fog'].map(v => `/assets/terrain/variations/${v}_${assetName}`),
    ];
    return this.loadBatch(variations);
  }

  /**
   * Load an asset at a specific LOD, or auto-select based on distance.
   */
  public async loadLODAsset(
    opts: LODLoadOptions
  ): Promise<HTMLImageElement> {
    const { lod, lodMetadata, distance, lodDistances } = opts;
    if (!lodMetadata) throw new Error('LOD metadata required');
    let selectedLOD: LODLevel = 'high';
    if (lod) {
      selectedLOD = lod;
    } else if (distance !== undefined && lodDistances) {
      if (distance <= lodDistances.high) selectedLOD = 'high';
      else if (distance <= lodDistances.medium) selectedLOD = 'medium';
      else selectedLOD = 'low';
    }
    const path = lodMetadata[selectedLOD];
    return this.loadAsset(path, opts);
  }

  /**
   * Smoothly transition between LODs (stub for integration with renderer).
   */
  public async transitionLOD(
    from: HTMLImageElement,
    to: HTMLImageElement,
    duration: number = 200
  ): Promise<void> {
    // Implement crossfade or morphing logic in renderer
    // This is a stub for now
    return new Promise((resolve) => setTimeout(resolve, duration));
  }

  /**
   * Load and return the asset manifest (from AssetIndexLoader).
   */
  public async loadManifest(): Promise<any> {
    await AssetIndexLoader.load();
    return AssetIndexLoader.getIndex();
  }

  /**
   * Preload all assets listed in the manifest (optionally filtered by category/type).
   */
  public async preloadManifestAssets(filter?: { category?: string; type?: string }) {
    const manifest = await this.loadManifest();
    let assetPaths: string[] = [];
    if (manifest.categories) {
      for (const category of manifest.categories) {
        if (filter?.category && category.name !== filter.category) continue;
        for (const feature of category.features) {
          if (filter?.type && feature.type !== filter.type) continue;
          for (const asset of feature.assets) {
            assetPaths.push(asset.filePath);
          }
        }
      }
    }
    this.preloadAssets(assetPaths);
  }

  /**
   * Get all asset paths from the manifest (optionally filtered).
   */
  public async getManifestAssets(filter?: { category?: string; type?: string }): Promise<string[]> {
    const manifest = await this.loadManifest();
    let assetPaths: string[] = [];
    if (manifest.categories) {
      for (const category of manifest.categories) {
        if (filter?.category && category.name !== filter.category) continue;
        for (const feature of category.features) {
          if (filter?.type && feature.type !== filter.type) continue;
          for (const asset of feature.assets) {
            assetPaths.push(asset.filePath);
          }
        }
      }
    }
    return assetPaths;
  }
} 
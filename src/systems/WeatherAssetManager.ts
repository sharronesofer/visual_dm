import { AssetManager, LODLevel, AssetLODMetadata } from '../assets/AssetManager';
import { AssetReferenceManager } from '../assets/AssetReferenceManager';

/**
 * WeatherAssetManager: Specialized asset manager for weather effects.
 * - Wraps AssetManager for weather-specific asset loading, preloading, and unloading
 * - Supports LOD, forecast-based preloading, and unified reference counting
 */
export class WeatherAssetManager {
    private static instance: WeatherAssetManager;
    private assetManager: AssetManager;
    private assetRefManager: AssetReferenceManager;

    private constructor() {
        this.assetManager = new AssetManager(200);
        this.assetRefManager = new AssetReferenceManager();
    }

    public static getInstance(): WeatherAssetManager {
        if (!WeatherAssetManager.instance) {
            WeatherAssetManager.instance = new WeatherAssetManager();
        }
        return WeatherAssetManager.instance;
    }

    /**
     * Load a weather asset at a specific LOD.
     * Increments reference count in AssetReferenceManager.
     */
    public async loadWeatherAsset(path: string, lod?: LODLevel, lodMetadata?: AssetLODMetadata, estimatedBytes: number = 1024 * 64): Promise<HTMLImageElement> {
        let asset: HTMLImageElement;
        if (lod && lodMetadata) {
            asset = await this.assetManager.loadLODAsset({ lod, lodMetadata });
        } else {
            asset = await this.assetManager.loadAsset(path);
        }
        this.assetRefManager.addReference(path, estimatedBytes);
        return asset;
    }

    /**
     * Preload weather assets for upcoming forecast (non-blocking).
     */
    public preloadWeatherAssets(paths: string[], lod?: LODLevel, lodMetadata?: AssetLODMetadata, estimatedBytes: number = 1024 * 64) {
        if (lod && lodMetadata) {
            paths.forEach((p) => {
                this.assetManager.loadLODAsset({ lod, lodMetadata }).then(() => {
                    this.assetRefManager.addReference(p, estimatedBytes);
                }).catch(() => { });
            });
        } else {
            paths.forEach((p) => {
                this.assetManager.preloadAssets([p]);
                this.assetRefManager.addReference(p, estimatedBytes);
            });
        }
    }

    /**
     * Unload a weather asset (decrements reference count, unloads if zero).
     */
    public unloadWeatherAsset(path: string) {
        this.assetRefManager.removeReference(path);
        if (this.assetRefManager.getReferenceCount(path) <= 0) {
            this.assetManager.unloadAsset(path);
        }
    }

    /**
     * Get a loaded weather asset synchronously (if present in cache).
     */
    public getWeatherAsset(path: string): HTMLImageElement | undefined {
        return this.assetManager.getAsset(path);
    }

    /**
     * Clear all cached weather assets and references.
     */
    public clearWeatherAssets() {
        this.assetManager.clearCache();
        // Remove all references
        for (const ref of this.assetRefManager.getAllReferences()) {
            this.assetRefManager.removeReference(ref.id);
        }
    }
} 
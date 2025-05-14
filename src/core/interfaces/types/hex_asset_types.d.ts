// Type definitions for hex asset management system

export interface HexAssetManager {
    load_hex_image: (
        path: string,
        category: string,
        metadata?: Record<string, any>,
        lazy?: boolean
    ) => any;
    get_hex_metadata: (path: string) => Record<string, any> | null;
    clear_hex_cache: (category?: string) => void;
    process_hex_loading_queue: () => void;
}

/**
 * Memory-efficient caching system for hex-based assets.
 */
export interface HexAssetCache {
    /**
     * Get an asset from the cache.
     * @param assetId ID of the asset to retrieve
     * @returns The cached surface if found, null otherwise
     */
    get: (assetId: string) => any;

    /**
     * Add an asset to the cache.
     * @param assetId ID of the asset
     * @param surface The surface to cache
     * @param memorySize Size in bytes, calculated if not provided
     * @returns True if successfully cached
     */
    put: (assetId: string, surface: any, memorySize?: number) => boolean;

    /**
     * Remove an asset from the cache.
     * @param assetId ID of the asset to remove
     * @returns True if successfully removed
     */
    remove: (assetId: string) => boolean;

    /**
     * Clear all assets from the cache.
     */
    clear: () => void;

    /**
     * Preload a set of assets into the cache.
     * @param assetIds List of asset IDs to preload
     * @param loaderFunc Function to load an asset if not cached
     * @returns Number of assets successfully preloaded
     */
    preload: (assetIds: string[], loaderFunc: (assetId: string) => any) => number;

    /**
     * Get current memory usage.
     * @returns Tuple of [bytes_used, percentage_used]
     */
    get_memory_usage: () => [number, number];

    /**
     * Configure cache cleanup behavior.
     * @param threshold Memory usage percentage that triggers cleanup
     * @param target Target memory usage percentage after cleanup
     */
    configure_cleanup: (threshold: number, target: number) => void;

    /**
     * Get cache statistics for monitoring.
     * @returns Object containing cache statistics
     */
    get_stats: () => {
        totalAssets: number;
        memoryUsed: number;
        memoryLimit: number;
        hitRate: number;
        missRate: number;
        cleanupCount: number;
    };

    /**
     * Validate cache integrity and repair if needed.
     * @returns True if cache is valid or was successfully repaired
     */
    validate: () => boolean;

    /**
     * Warm up the cache with frequently used assets.
     * @param assetIds List of asset IDs to warm up
     * @param priority Priority level for cache retention
     */
    warmup: (assetIds: string[], priority?: 'high' | 'medium' | 'low') => void;
}

export interface HexAssetRenderer {
    render_hex_tile: (
        surface: any,
        position: [number, number],
        baseAssetId: string,
        features?: string[],
        overlays?: string[],
        effects?: string[],
        scale?: number
    ) => void;
    calculate_hex_position: (hexCoord: [number, number], scale?: number) => [number, number];
} 
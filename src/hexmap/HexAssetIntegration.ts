import { HexGrid } from './HexGrid';
import { TacticalHexGrid } from './TacticalHexGrid';
import { TerrainType, WeatherType } from './HexCell';
import { HexAssetManager, HexAssetCache, HexAssetRenderer } from '../types/hex_asset_types';

interface TerrainAssetConfig {
    base: string;
    features: string[];
    overlays: string[];
    variations: {
        [key: string]: string; // season/weather -> asset id
    };
}

interface RenderLayerConfig {
    layer: string;
    zIndex: number;
    opacity: number;
    blendMode?: string;
}

export class HexAssetIntegration {
    private assetManager: HexAssetManager;
    private assetCache: HexAssetCache;
    private renderer: HexAssetRenderer;
    private currentSeason: string = 'summer';
    private transitionProgress: number = 0;
    private targetSeason: string | null = null;
    private terrainConfigs: { [key: string]: TerrainAssetConfig } = {
        plains: {
            base: 'terrain_plains_base',
            features: ['grass_patch_1', 'grass_patch_2'],
            overlays: ['elevation_overlay'],
            variations: {
                summer: 'terrain_plains_summer',
                winter: 'terrain_plains_winter',
                autumn: 'terrain_plains_autumn',
                spring: 'terrain_plains_spring'
            }
        },
        forest: {
            base: 'terrain_forest_base',
            features: ['tree_cluster_1', 'tree_cluster_2'],
            overlays: ['elevation_overlay', 'forest_density_overlay'],
            variations: {
                summer: 'terrain_forest_summer',
                winter: 'terrain_forest_winter',
                autumn: 'terrain_forest_autumn',
                spring: 'terrain_forest_spring'
            }
        },
        mountain: {
            base: 'terrain_mountain_base',
            features: ['rock_formation_1', 'rock_formation_2'],
            overlays: ['elevation_overlay', 'snow_cap_overlay'],
            variations: {
                summer: 'terrain_mountain_summer',
                winter: 'terrain_mountain_winter',
                autumn: 'terrain_mountain_autumn',
                spring: 'terrain_mountain_spring'
            }
        }
    };

    constructor(
        assetManager: HexAssetManager,
        assetCache: HexAssetCache,
        renderer: HexAssetRenderer
    ) {
        this.assetManager = assetManager;
        this.assetCache = assetCache;
        this.renderer = renderer;
    }

    public renderRegionGrid(grid: HexGrid): void {
        for (let x = 0; x < grid.width; x++) {
            for (let y = 0; y < grid.height; y++) {
                const cell = grid.get(x, y);
                if (!cell) continue;

                const terrain = cell.terrain;
                const config = this.terrainConfigs[terrain];
                if (!config) continue;

                // Calculate base asset ID based on current season and transition
                let baseAssetId = config.variations[this.currentSeason];
                let overlayAssets = [...config.overlays];
                let featureAssets = [...config.features];

                // Handle season transition
                if (this.targetSeason && this.transitionProgress > 0) {
                    const targetAssetId = config.variations[this.targetSeason];
                    this.renderer.render_hex_tile(
                        null,
                        [x, y],
                        baseAssetId,
                        featureAssets,
                        overlayAssets,
                        [targetAssetId],
                        1.0 - this.transitionProgress
                    );

                    // Render target season on top
                    this.renderer.render_hex_tile(
                        null,
                        [x, y],
                        targetAssetId,
                        featureAssets,
                        overlayAssets,
                        [],
                        this.transitionProgress
                    );
                } else {
                    // Normal render without transition
                    this.renderer.render_hex_tile(
                        null,
                        [x, y],
                        baseAssetId,
                        featureAssets,
                        overlayAssets,
                        [],
                        1.0
                    );
                }
            }
        }
    }

    public renderTacticalGrid(grid: TacticalHexGrid): void {
        for (let x = 0; x < grid.width; x++) {
            for (let y = 0; y < grid.height; y++) {
                const cell = grid.get(x, y);
                if (!cell) continue;

                const terrain = cell.terrain;
                const config = this.terrainConfigs[terrain];
                if (!config) continue;

                let baseAssetId = config.variations[this.currentSeason];
                let overlayAssets = [...config.overlays];
                let featureAssets = [...config.features];

                // Add tactical-specific overlays
                if (cell.cover > 0) {
                    overlayAssets.push(`cover_overlay_${Math.floor(cell.cover * 10)}`);
                }
                if (cell.movementCost > 1) {
                    overlayAssets.push(`movement_cost_${cell.movementCost}`);
                }
                if (cell.terrainEffect) {
                    overlayAssets.push(`effect_${cell.terrainEffect}`);
                }

                this.renderer.render_hex_tile(
                    null,
                    [x, y],
                    baseAssetId,
                    featureAssets,
                    overlayAssets,
                    [],
                    1.0
                );
            }
        }
    }

    public preloadAssets(grid: HexGrid): void {
        const assetsToLoad: string[] = [];

        // Collect all potentially needed assets
        for (const terrain of Object.keys(this.terrainConfigs)) {
            const config = this.terrainConfigs[terrain];
            assetsToLoad.push(config.base);
            assetsToLoad.push(...config.features);
            assetsToLoad.push(...config.overlays);
            assetsToLoad.push(...Object.values(config.variations));
        }

        // Preload unique assets
        this.assetCache.preload(
            Array.from(new Set(assetsToLoad)),
            (assetId: string) => this.assetManager.load_hex_image(assetId, 'terrain')
        );
    }

    public startSeasonTransition(targetSeason: string): void {
        if (this.terrainConfigs[Object.keys(this.terrainConfigs)[0]].variations[targetSeason]) {
            this.targetSeason = targetSeason;
            this.transitionProgress = 0;
        }
    }

    public updateTransition(deltaProgress: number): void {
        if (!this.targetSeason) return;

        this.transitionProgress = Math.min(1.0, this.transitionProgress + deltaProgress);
        
        if (this.transitionProgress >= 1.0) {
            this.currentSeason = this.targetSeason;
            this.targetSeason = null;
            this.transitionProgress = 0;
        }
    }
} 
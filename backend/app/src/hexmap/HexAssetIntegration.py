from typing import Any, Dict, List


class TerrainAssetConfig:
    base: str
    features: List[str]
    overlays: List[str]
    variations: Dict[str, Any]
class RenderLayerConfig:
    layer: str
    zIndex: float
    opacity: float
    blendMode?: str
class HexAssetIntegration {
    private assetManager: HexAssetManager
    private assetCache: HexAssetCache
    private renderer: HexAssetRenderer
    private currentSeason: str = 'summer'
    private transitionProgress: float = 0
    private targetSeason: str | null = null
    private terrainConfigs: Dict[str, Any] = {
        plains: Dict[str, Any]
        },
        forest: Dict[str, Any]
        },
        mountain: Dict[str, Any]
        }
    }
    constructor(
        assetManager: HexAssetManager,
        assetCache: HexAssetCache,
        renderer: HexAssetRenderer
    ) {
        this.assetManager = assetManager
        this.assetCache = assetCache
        this.renderer = renderer
    }
    public renderRegionGrid(grid: HexGrid): void {
        for (let x = 0; x < grid.width; x++) {
            for (let y = 0; y < grid.height; y++) {
                const cell = grid.get(x, y)
                if (!cell) continue
                const terrain = cell.terrain
                const config = this.terrainConfigs[terrain]
                if (!config) continue
                let baseAssetId = config.variations[this.currentSeason]
                let overlayAssets = [...config.overlays]
                let featureAssets = [...config.features]
                if (this.targetSeason && this.transitionProgress > 0) {
                    const targetAssetId = config.variations[this.targetSeason]
                    this.renderer.render_hex_tile(
                        null,
                        [x, y],
                        baseAssetId,
                        featureAssets,
                        overlayAssets,
                        [targetAssetId],
                        1.0 - this.transitionProgress
                    )
                    this.renderer.render_hex_tile(
                        null,
                        [x, y],
                        targetAssetId,
                        featureAssets,
                        overlayAssets,
                        [],
                        this.transitionProgress
                    )
                } else {
                    this.renderer.render_hex_tile(
                        null,
                        [x, y],
                        baseAssetId,
                        featureAssets,
                        overlayAssets,
                        [],
                        1.0
                    )
                }
            }
        }
    }
    public renderTacticalGrid(grid: TacticalHexGrid): void {
        for (let x = 0; x < grid.width; x++) {
            for (let y = 0; y < grid.height; y++) {
                const cell = grid.get(x, y)
                if (!cell) continue
                const terrain = cell.terrain
                const config = this.terrainConfigs[terrain]
                if (!config) continue
                let baseAssetId = config.variations[this.currentSeason]
                let overlayAssets = [...config.overlays]
                let featureAssets = [...config.features]
                if (cell.cover > 0) {
                    overlayAssets.push(`cover_overlay_${Math.floor(cell.cover * 10)}`)
                }
                if (cell.movementCost > 1) {
                    overlayAssets.push(`movement_cost_${cell.movementCost}`)
                }
                if (cell.terrainEffect) {
                    overlayAssets.push(`effect_${cell.terrainEffect}`)
                }
                this.renderer.render_hex_tile(
                    null,
                    [x, y],
                    baseAssetId,
                    featureAssets,
                    overlayAssets,
                    [],
                    1.0
                )
            }
        }
    }
    public preloadAssets(grid: HexGrid): void {
        const assetsToLoad: List[string] = []
        for (const terrain of Object.keys(this.terrainConfigs)) {
            const config = this.terrainConfigs[terrain]
            assetsToLoad.push(config.base)
            assetsToLoad.push(...config.features)
            assetsToLoad.push(...config.overlays)
            assetsToLoad.push(...Object.values(config.variations))
        }
        this.assetCache.preload(
            Array.from(new Set(assetsToLoad)),
            (assetId: str) => this.assetManager.load_hex_image(assetId, 'terrain')
        )
    }
    public startSeasonTransition(targetSeason: str): void {
        if (this.terrainConfigs[Object.keys(this.terrainConfigs)[0]].variations[targetSeason]) {
            this.targetSeason = targetSeason
            this.transitionProgress = 0
        }
    }
    public updateTransition(deltaProgress: float): void {
        if (!this.targetSeason) return
        this.transitionProgress = Math.min(1.0, this.transitionProgress + deltaProgress)
        if (this.transitionProgress >= 1.0) {
            this.currentSeason = this.targetSeason
            this.targetSeason = null
            this.transitionProgress = 0
        }
    }
} 
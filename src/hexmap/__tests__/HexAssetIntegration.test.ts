import { HexGrid } from '../HexGrid';
import { TacticalHexGrid } from '../TacticalHexGrid';
import { HexAssetIntegration } from '../HexAssetIntegration';
import { HexAssetManager, HexAssetCache, HexAssetRenderer } from '../../types/hex_asset_types';

describe('HexAssetIntegration', () => {
    let mockAssetManager: jest.Mocked<HexAssetManager>;
    let mockAssetCache: jest.Mocked<HexAssetCache>;
    let mockRenderer: jest.Mocked<HexAssetRenderer>;
    let integration: HexAssetIntegration;
    let grid: HexGrid;
    let tacticalGrid: TacticalHexGrid;

    beforeEach(() => {
        // Create mock implementations
        mockAssetManager = {
            load_hex_image: jest.fn(),
            get_hex_metadata: jest.fn(),
            clear_hex_cache: jest.fn(),
            process_hex_loading_queue: jest.fn()
        };

        mockAssetCache = {
            get: jest.fn(),
            put: jest.fn(),
            remove: jest.fn(),
            clear: jest.fn(),
            preload: jest.fn(),
            get_memory_usage: jest.fn()
        };

        mockRenderer = {
            render_hex_tile: jest.fn(),
            calculate_hex_position: jest.fn()
        };

        integration = new HexAssetIntegration(mockAssetManager, mockAssetCache, mockRenderer);

        // Create test grids
        grid = new HexGrid(3, 3);
        tacticalGrid = new TacticalHexGrid(3, 3);

        // Set up test cells
        for (let x = 0; x < 3; x++) {
            for (let y = 0; y < 3; y++) {
                grid.setTerrain(x, y, 'plains');
                tacticalGrid.setTerrain(x, y, 'plains');
                const cell = tacticalGrid.get(x, y);
                if (cell) {
                    cell.cover = 0.5;
                    cell.movementCost = 2;
                    cell.terrainEffect = 'muddy';
                }
            }
        }
    });

    describe('renderRegionGrid', () => {
        it('should render all cells in the grid', () => {
            integration.renderRegionGrid(grid);

            // Should call render_hex_tile for each cell (3x3 grid)
            expect(mockRenderer.render_hex_tile).toHaveBeenCalledTimes(9);

            // Verify first cell render
            expect(mockRenderer.render_hex_tile).toHaveBeenCalledWith(
                null,
                [0, 0],
                'terrain_plains_summer',
                ['grass_patch_1', 'grass_patch_2'],
                ['elevation_overlay'],
                [],
                1.0
            );
        });

        it('should handle season transitions correctly', () => {
            integration.startSeasonTransition('winter');
            integration.updateTransition(0.5);
            integration.renderRegionGrid(grid);

            // Should render each cell twice during transition (3x3 grid * 2)
            expect(mockRenderer.render_hex_tile).toHaveBeenCalledTimes(18);

            // Verify transition renders for first cell
            expect(mockRenderer.render_hex_tile).toHaveBeenCalledWith(
                null,
                [0, 0],
                'terrain_plains_summer',
                ['grass_patch_1', 'grass_patch_2'],
                ['elevation_overlay'],
                ['terrain_plains_winter'],
                0.5
            );

            expect(mockRenderer.render_hex_tile).toHaveBeenCalledWith(
                null,
                [0, 0],
                'terrain_plains_winter',
                ['grass_patch_1', 'grass_patch_2'],
                ['elevation_overlay'],
                [],
                0.5
            );
        });
    });

    describe('renderTacticalGrid', () => {
        it('should render tactical cells with appropriate overlays', () => {
            integration.renderTacticalGrid(tacticalGrid);

            // Should call render_hex_tile for each cell (3x3 grid)
            expect(mockRenderer.render_hex_tile).toHaveBeenCalledTimes(9);

            // Verify first cell render with tactical overlays
            expect(mockRenderer.render_hex_tile).toHaveBeenCalledWith(
                null,
                [0, 0],
                'terrain_plains_summer',
                ['grass_patch_1', 'grass_patch_2'],
                [
                    'elevation_overlay',
                    'cover_overlay_5',
                    'movement_cost_2',
                    'effect_muddy'
                ],
                [],
                1.0
            );
        });
    });

    describe('preloadAssets', () => {
        it('should preload all required assets', () => {
            integration.preloadAssets(grid);

            // Verify preload was called with all unique assets
            expect(mockAssetCache.preload).toHaveBeenCalledTimes(1);
            
            const preloadCall = mockAssetCache.preload.mock.calls[0];
            const [assetList, loaderFn] = preloadCall;

            // Verify asset list contains all required assets
            expect(assetList).toContain('terrain_plains_base');
            expect(assetList).toContain('grass_patch_1');
            expect(assetList).toContain('grass_patch_2');
            expect(assetList).toContain('elevation_overlay');
            expect(assetList).toContain('terrain_plains_summer');
            expect(assetList).toContain('terrain_plains_winter');
            expect(assetList).toContain('terrain_plains_autumn');
            expect(assetList).toContain('terrain_plains_spring');

            // Verify loader function
            loaderFn('test_asset');
            expect(mockAssetManager.load_hex_image).toHaveBeenCalledWith(
                'test_asset',
                'terrain'
            );
        });
    });

    describe('season transitions', () => {
        it('should handle complete season transition cycle', () => {
            // Start winter transition
            integration.startSeasonTransition('winter');
            expect(integration['transitionProgress']).toBe(0);
            expect(integration['targetSeason']).toBe('winter');

            // Update halfway
            integration.updateTransition(0.5);
            expect(integration['transitionProgress']).toBe(0.5);
            expect(integration['targetSeason']).toBe('winter');

            // Complete transition
            integration.updateTransition(0.5);
            expect(integration['currentSeason']).toBe('winter');
            expect(integration['targetSeason']).toBeNull();
            expect(integration['transitionProgress']).toBe(0);
        });

        it('should ignore invalid season transitions', () => {
            integration.startSeasonTransition('invalid_season');
            expect(integration['targetSeason']).toBeNull();
            expect(integration['transitionProgress']).toBe(0);
        });
    });
}); 
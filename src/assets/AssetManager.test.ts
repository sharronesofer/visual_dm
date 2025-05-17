import { AssetManager, AssetLODMetadata, LODLevel } from './AssetManager';

describe('AssetManager LOD Support', () => {
    let manager: AssetManager;
    let lodMeta: AssetLODMetadata;

    beforeAll(() => {
        // Mock global Image for Node environment
        (global as any).Image = class {
            src: string = '';
            onload: () => void = () => { };
            onerror: () => void = () => { };
        };
    });

    beforeEach(() => {
        manager = new AssetManager(10);
        lodMeta = {
            high: 'high.png',
            medium: 'medium.png',
            low: 'low.png',
        };
        // Mock loadAsset to resolve with a dummy object
        jest.spyOn(manager, 'loadAsset').mockImplementation(async (path: string) => ({ src: path } as any));
    });

    it('loads the correct LOD by explicit level', async () => {
        for (const level of ['high', 'medium', 'low'] as LODLevel[]) {
            const img = await manager.loadLODAsset({ lod: level, lodMetadata: lodMeta });
            expect(img.src).toBe(lodMeta[level]);
        }
    });

    it('selects LOD based on distance', async () => {
        const lodDistances = { high: 10, medium: 30, low: 100 };
        // Should select high
        let img = await manager.loadLODAsset({ distance: 5, lodDistances, lodMetadata: lodMeta });
        expect(img.src).toBe('high.png');
        // Should select medium
        img = await manager.loadLODAsset({ distance: 20, lodDistances, lodMetadata: lodMeta });
        expect(img.src).toBe('medium.png');
        // Should select low
        img = await manager.loadLODAsset({ distance: 50, lodDistances, lodMetadata: lodMeta });
        expect(img.src).toBe('low.png');
    });

    it('throws if LOD metadata is missing', async () => {
        await expect(manager.loadLODAsset({ lod: 'high' as LODLevel } as any)).rejects.toThrow('LOD metadata required');
    });

    it('transitionLOD resolves after duration', async () => {
        const start = Date.now();
        await manager.transitionLOD({} as any, {} as any, 50);
        const elapsed = Date.now() - start;
        expect(elapsed).toBeGreaterThanOrEqual(50);
    });
}); 
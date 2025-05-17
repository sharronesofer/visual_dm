import { AssetReferenceManager } from './AssetReferenceManager';

describe('AssetReferenceManager', () => {
    let manager: AssetReferenceManager;

    beforeEach(() => {
        manager = new AssetReferenceManager(100); // 100 bytes budget for testing
        // Mock unloadAsset to track calls
        (manager as any).unloadAsset = jest.fn();
    });

    it('adds and removes references correctly', () => {
        manager.addReference('asset1', 10);
        expect(manager.getReferenceCount('asset1')).toBe(1);
        manager.addReference('asset1', 10);
        expect(manager.getReferenceCount('asset1')).toBe(2);
        manager.removeReference('asset1');
        expect(manager.getReferenceCount('asset1')).toBe(1);
        manager.removeReference('asset1');
        expect(manager.getReferenceCount('asset1')).toBe(0);
    });

    it('tracks memory usage and enforces budget', () => {
        manager.addReference('asset1', 60);
        manager.addReference('asset2', 50);
        // asset2 should push us over budget, but not be unloaded since it has a ref
        expect(manager.getCurrentMemory()).toBe(110);
        // Remove both references
        manager.removeReference('asset1');
        manager.removeReference('asset2');
        // Now enforceBudget should unload both
        manager.addReference('asset3', 10); // triggers enforceBudget
        expect((manager as any).unloadAsset).toHaveBeenCalledWith('asset1');
        expect((manager as any).unloadAsset).toHaveBeenCalledWith('asset2');
    });

    it('does not unload assets with active references', () => {
        manager.addReference('asset1', 60);
        manager.addReference('asset2', 50);
        // Remove only one reference
        manager.removeReference('asset1');
        // asset2 still has a reference
        manager.addReference('asset3', 10); // triggers enforceBudget
        expect((manager as any).unloadAsset).toHaveBeenCalledWith('asset1');
        expect((manager as any).unloadAsset).not.toHaveBeenCalledWith('asset2');
    });

    it('getAllReferences returns all tracked assets', () => {
        manager.addReference('asset1', 10);
        manager.addReference('asset2', 20);
        const refs = manager.getAllReferences();
        expect(refs.length).toBe(2);
        expect(refs.some(r => r.id === 'asset1')).toBe(true);
        expect(refs.some(r => r.id === 'asset2')).toBe(true);
    });
}); 
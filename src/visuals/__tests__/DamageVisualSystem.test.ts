import { expect } from 'chai';
import { DamageVisualSystem, DamageState, DamageVisualMapping } from '../DamageVisualSystem.ts';
import { OverlayType } from '../OverlayManager.ts';

describe('DamageVisualSystem', () => {
    let dvs: DamageVisualSystem;
    let overlayManagerMock: any;
    let spriteRegistryMock: any;

    beforeEach(() => {
        dvs = DamageVisualSystem.getInstance();
        // Reset mappings for each test
        (dvs as any).mappings.clear();
        (dvs as any).registerDefaultMappings();
        // Mock OverlayManager
        overlayManagerMock = {
            removeOverlay: function () { overlayManagerMock._calls.push(['removeOverlay', ...arguments]); },
            applyOverlay: function () { overlayManagerMock._calls.push(['applyOverlay', ...arguments]); },
            _calls: [] as any[],
        };
        // Mock SpriteRegistry
        spriteRegistryMock = { _calls: [] };
        dvs.setOverlayManager(overlayManagerMock);
        dvs.setSpriteRegistry(spriteRegistryMock);
    });

    it('returns the singleton instance', () => {
        const dvs2 = DamageVisualSystem.getInstance();
        expect(dvs).to.equal(dvs2);
    });

    it('registers and retrieves a mapping', () => {
        const mapping: DamageVisualMapping = {
            state: DamageState.DIRTY,
            overlayTypes: [OverlayType.DIRTY],
            spriteKey: 'dirty',
            transition: 'fade',
        };
        dvs.registerMapping(mapping);
        expect(dvs.getVisualMapping(DamageState.DIRTY)).to.deep.equal(mapping);
    });

    it('returns default mappings for all states', () => {
        Object.values(DamageState).forEach(state => {
            expect(dvs.getVisualMapping(state)).to.exist;
        });
    });

    it('calls OverlayManager to update overlays for a building', () => {
        dvs.updateVisualsForBuilding('b1', DamageState.CRACKED, { position: { x: 1, y: 2 }, size: { width: 10, height: 20 } });
        // Should remove all overlays, then apply CRACKED overlay
        const removeCalls = overlayManagerMock._calls.filter(([fn]) => fn === 'removeOverlay');
        const applyCalls = overlayManagerMock._calls.filter(([fn]) => fn === 'applyOverlay');
        expect(removeCalls.length).to.equal(Object.keys(OverlayType).length);
        expect(applyCalls.length).to.equal(1);
        expect(applyCalls[0][1]).to.equal('b1');
        expect(applyCalls[0][2]).to.equal(OverlayType.CRACKED);
        expect(applyCalls[0][3]).to.include({ position: { x: 1, y: 2 }, size: { width: 10, height: 20 }, zIndex: 100 });
    });

    it('does nothing if OverlayManager is not set', () => {
        dvs.setOverlayManager(null as any);
        expect(() => dvs.updateVisualsForBuilding('b2', DamageState.DIRTY)).to.not.throw();
    });

    it('can set OverlayManager and SpriteRegistry', () => {
        const om = {};
        const sr = {};
        expect(() => dvs.setOverlayManager(om as any)).to.not.throw();
        expect(() => dvs.setSpriteRegistry(sr as any)).to.not.throw();
    });

    it('getVisualState returns PRISTINE by default (stub)', () => {
        expect(dvs.getVisualState('any')).to.equal(DamageState.PRISTINE);
    });

    it('transition logic is stubbed (TODO)', () => {
        // This is a placeholder for future animation/transition tests
        // For now, just ensure updateVisualsForBuilding does not throw
        expect(() => dvs.updateVisualsForBuilding('b3', DamageState.CHIPPED)).to.not.throw();
    });
});

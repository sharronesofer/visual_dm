import { OverlayManager, OverlayType, OverlayInstance } from './OverlayManager';
import { expect } from 'chai';
import { Point, Size, BuildingVisualInfo } from './types';

describe('OverlayManager', () => {
    let overlayManager: OverlayManager;
    let mockImage: HTMLImageElement;

    beforeAll(() => {
        // Mock window.Image or globalThis.Image
        (globalThis as any).Image = class {
            src = '';
        };
    });

    beforeEach(() => {
        overlayManager = OverlayManager.getInstance();
        // Clear overlays between tests
        (overlayManager as any).overlays.clear();
        (overlayManager as any).overlayAssets.clear();
        // Preload mock assets
        Object.values(OverlayType).forEach(type => {
            mockImage = { src: `/assets/overlays/${type}.png` } as HTMLImageElement;
            (overlayManager as any).overlayAssets.set(type, mockImage);
        });
    });

    it('applies and retrieves overlays correctly', () => {
        overlayManager.applyOverlay('b1', OverlayType.DIRTY);
        overlayManager.applyOverlay('b1', OverlayType.CRACKED, { zIndex: 50 });
        const overlays = overlayManager.getActiveOverlays('b1');
        expect(overlays.length).to.equal(2);
        expect(overlays[0].overlayType).to.equal(OverlayType.DIRTY);
        expect(overlays[1].overlayType).to.equal(OverlayType.CRACKED);
        expect(overlays[1].zIndex).to.equal(50);
    });

    it('removes overlays correctly', () => {
        overlayManager.applyOverlay('b2', OverlayType.DINGY);
        overlayManager.removeOverlay('b2', OverlayType.DINGY);
        expect(overlayManager.getActiveOverlays('b2')).to.deep.equal([]);
    });

    it('sorts overlays by zIndex', () => {
        overlayManager.applyOverlay('b3', OverlayType.DIRTY, { zIndex: 10 });
        overlayManager.applyOverlay('b3', OverlayType.CRACKED, { zIndex: 40 });
        overlayManager.applyOverlay('b3', OverlayType.CHIPPED, { zIndex: 30 });
        const overlays = overlayManager.getActiveOverlays('b3');
        expect(overlays.map(o => o.overlayType)).to.deep.equal([
            OverlayType.DIRTY,
            OverlayType.CHIPPED,
            OverlayType.CRACKED,
        ]);
    });

    it('preloads overlay assets', () => {
        // Should have an asset for each OverlayType
        Object.values(OverlayType).forEach(type => {
            expect((overlayManager as any).overlayAssets.get(type)).to.exist;
        });
    });

    it('renders overlays (mock context)', () => {
        // Mock CanvasRenderingContext2D
        const drawCalls: any[] = [];
        const mockContext = {
            save: () => { },
            restore: () => { },
            drawImage: (img: any, x: number, y: number, w: number, h: number) => drawCalls.push({ img, x, y, w, h }),
            globalAlpha: 1.0,
        } as any;
        overlayManager.applyOverlay('b4', OverlayType.DIRTY, { position: { x: 10, y: 20 }, size: { width: 32, height: 32 } });
        overlayManager.renderOverlays(mockContext, [
            { id: 'b4', position: { x: 10, y: 20 }, size: { width: 32, height: 32 } },
        ]);
        expect(drawCalls.length).to.equal(1);
        expect(drawCalls[0].x).to.equal(10);
        expect(drawCalls[0].y).to.equal(20);
        expect(drawCalls[0].w).to.equal(32);
        expect(drawCalls[0].h).to.equal(32);
    });

    it('integrates with SpriteRegistry (stub)', () => {
        expect(() => overlayManager.setSpriteRegistry({})).to.not.throw();
    });
});

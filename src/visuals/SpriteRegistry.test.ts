import { before, beforeEach, describe, it } from 'mocha';
import { SpriteRegistry, SpriteKey, SpriteInstance } from './SpriteRegistry.ts';
import { expect } from 'chai';
import { Point, Size } from './types.ts';

describe('SpriteRegistry', () => {
    let spriteRegistry: SpriteRegistry;
    let mockImage: HTMLImageElement;

    before(() => {
        // Mock window.Image or globalThis.Image
        (globalThis as any).Image = class {
            src = '';
            width = 64;
            height = 64;
            onload: (() => void) | null = null;
            setSrc(val: string) {
                this.src = val;
                if (this.onload) this.onload();
            }
        };
    });

    beforeEach(() => {
        spriteRegistry = SpriteRegistry.getInstance();
        spriteRegistry.clearCache();
    });

    it('returns the singleton instance', () => {
        const reg2 = SpriteRegistry.getInstance();
        expect(spriteRegistry).to.equal(reg2);
    });

    it('registers and retrieves a sprite', () => {
        spriteRegistry.registerSprite('house', 'house.png');
        const sprite = spriteRegistry.getSprite('house');
        expect(sprite).to.exist;
        expect(sprite!.key).to.equal('house');
        expect(sprite!.assetRef.src).to.include('house.png');
    });

    it('does not overwrite an existing sprite', () => {
        spriteRegistry.registerSprite('house', 'house.png');
        const sprite1 = spriteRegistry.getSprite('house');
        spriteRegistry.registerSprite('house', 'other.png');
        const sprite2 = spriteRegistry.getSprite('house');
        expect(sprite2).to.equal(sprite1);
    });

    it('preloads multiple sprites', () => {
        spriteRegistry.preloadSprites([
            ['house', 'house.png'],
            ['factory:roof', 'roof.png'],
        ]);
        expect(spriteRegistry.getSprite('house')).to.exist;
        expect(spriteRegistry.getSprite('factory:roof')).to.exist;
    });

    it('clears the sprite cache', () => {
        spriteRegistry.registerSprite('house', 'house.png');
        expect(spriteRegistry.getSprite('house')).to.exist;
        spriteRegistry.clearCache();
        expect(spriteRegistry.getSprite('house')).to.be.undefined;
    });

    it('sets placeholder before image loads', () => {
        spriteRegistry.registerSprite('house', 'house.png');
        const sprite = spriteRegistry.getSprite('house');
        expect(sprite).to.exist;
        expect(sprite!.width).to.equal(0); // Placeholder width before load
        // Simulate image load
        (sprite!.assetRef as any).width = 128;
        (sprite!.assetRef as any).height = 128;
        if (sprite!.assetRef.onload) (sprite!.assetRef.onload as () => void)();
        // After load, the registry should update width/height
        const loaded = spriteRegistry.getSprite('house');
        expect(loaded!.width).to.equal(128);
        expect(loaded!.height).to.equal(128);
    });

    it('integrates with OverlayManager (stub)', () => {
        expect(() => spriteRegistry.setOverlayManager({})).to.not.throw();
    });

    it('integrates with DamageVisualSystem (stub)', () => {
        expect(() => spriteRegistry.setDamageVisualSystem({})).to.not.throw();
    });
});
